import pygame as pg
from v2 import V2 as v2
from math import sin, cos
from ray import Ray
from line import Line
import lib
from concurrent.futures import ProcessPoolExecutor
import math
import os


_WORKER_WALLS = None

def _worker_init(walls_tuples):
    """Initializer for worker processes; runs once per worker."""
    global _WORKER_WALLS
    _WORKER_WALLS = walls_tuples

def _intersect_ray_segment(x1, y1, x2, y2, x3, y3, x4, y4):
    # robust parametric intersection (ray from p1->p2 vs segment p3->p4)
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if abs(denom) < 1e-9:
        return None
    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
    if t < 0.0 or t > 1.0 or u < 0.0 or u > 1.0:
        return None
    ix = x1 + t * (x2 - x1)
    iy = y1 + t * (y2 - y1)
    return (ix, iy)

def _cast_rays_chunk(chunk):
    """
    Worker function: chunk = (starts_x_list, starts_y_list, angles_list)
    returns a list of results matching input ray order:
      None or (angle, ix, iy, wall_index, dist)
    Uses module-global _WORKER_WALLS (set by initializer).
    """
    global _WORKER_WALLS
    starts_x, starts_y, angles = chunk
    out = []
    for sx, sy, angle in zip(starts_x, starts_y, angles):
        rad = angle * math.pi / 180.0
        rx2 = sx + math.cos(rad) * 10000.0
        ry2 = sy + math.sin(rad) * 10000.0

        best_pt = None
        best_idx = -1
        best_dist = float("inf")

        # iterate walls that were preloaded into this worker as tuples:
        # each wall tuple is (x1, y1, x2, y2)
        for idx, w in enumerate(_WORKER_WALLS):
            x3, y3, x4, y4 = w
            pt = _intersect_ray_segment(sx, sy, rx2, ry2, x3, y3, x4, y4)
            if pt is None:
                continue
            dx = pt[0] - sx
            dy = pt[1] - sy
            d = math.hypot(dx, dy)
            if d < best_dist:
                best_dist = d
                best_pt = pt
                best_idx = idx

        if best_pt is None:
            out.append(None)
        else:
            out.append((angle, best_pt[0], best_pt[1], best_idx, best_dist))
    return out


class Player:
    def __init__(self, pos: v2, walls: list[Line], fov: float = 90, rays_number: float = 100,
                 rotation_speed: int = 200, speed: int = 500, angle: float = 0,
                 r: float = 20) -> None:
        self._pos = pos
        self._walls = walls
        self._angle = angle
        self._fov = fov
        self._rays_number = rays_number
        self._ray_degree = fov / rays_number
        self._r = r
        self._rotation_speed = rotation_speed
        self._speed = speed
        self._rays: list[Ray] = []
        self._calculated_rays_points: list[dict[str, v2 | float | Line] | None] = []

        angle = -self._fov / 2 + self._angle
        while angle <= self._fov / 2 + self._angle:
            self._rays.append(Ray(self._pos, angle))
            angle += self._ray_degree

        # ---- multiprocessing pool (kept alive) ----
        # convert walls to primitive tuples once (pickled only on pool creation)
        self._walls_tuples = [(w.start.x, w.start.y, w.end.x, w.end.y) for w in self._walls]

        # choose number of workers (None uses default). You can tune max_workers.
        max_workers = os.cpu_count() or 2
        self._pool = ProcessPoolExecutor(
            max_workers=max_workers,
            initializer=_worker_init,
            initargs=(self._walls_tuples,)
        )

    def close(self):
        """Shutdown the persistent process pool (call once at program end)."""
        if getattr(self, "_pool", None) is not None:
            self._pool.shutdown(wait=True)
            self._pool = None


    def get_rays(self) -> list[Ray]:
        return self._rays

    def get_angle(self) -> float:
        return self._angle

    def get_pos(self) -> v2:
        return self._pos

    def get_size(self) -> float:
        return self._r

    def _calculate_rays(self) -> list[dict[str, v2 | float | Line] | None]:
        # Prepare simple arrays of ray data (primitive floats)
        n = len(self._rays)
        if n == 0:
            return []

        starts_x = [r.start.x for r in self._rays]
        starts_y = [r.start.y for r in self._rays]
        angles = [r.get_angle() for r in self._rays]

        # chunking: tune chunk_size (32 is a reasonable starting point)
        chunk_size = 32
        chunks = []
        for i in range(0, n, chunk_size):
            j = i + chunk_size
            chunks.append((starts_x[i:j], starts_y[i:j], angles[i:j]))

        assert self._pool is not None
        # map chunks to worker pool (workers already have walls preloaded)
        chunks_results = list(self._pool.map(_cast_rays_chunk, chunks))

        # flatten and convert results back to the original API (v2 + Line object)
        flat = [item for chunk in chunks_results for item in chunk]
        res = []
        for item in flat:
            if item is None:
                res.append(None)
            else:
                angle, ix, iy, wall_idx, dist = item
                res.append({
                    "angle": angle,
                    "pos": v2(ix, iy),
                    "line": self._walls[wall_idx],
                    "dist": dist
                })
        return res

    def rotate_right(self, amt: float, dt: float) -> None:
        """
        rotates the player clockwise
        """
        self._angle += self._rotation_speed * amt * dt
        for i, _ in enumerate(self._rays):
            self._rays[i].rotate(self._rotation_speed * amt * dt)

    def rotate_left(self, amt: float, dt: float) -> None:
        """
        rotates the player counter clockwise
        """
        self._angle -= self._rotation_speed * amt * dt
        for i, _ in enumerate(self._rays):
            self._rays[i].rotate(-self._rotation_speed * amt * dt)

    def _update_rays_pos(self) -> None:
        for i, _ in enumerate(self._rays):
            self._rays[i].start = self._pos

    def move_forward(self, dt: float) -> None:
        """
        moves the player forward
        """
        offset: v2 = v2(cos(lib.degree_to_rad(self._angle)),
                        sin(lib.degree_to_rad(self._angle))) * self._speed
        self._pos += offset * dt
        self._update_rays_pos()

    def move_backwards(self, dt: float) -> None:
        """
        moves the player backwards
        """
        offset: v2 = v2(cos(lib.degree_to_rad(self._angle)),
                        sin(lib.degree_to_rad(self._angle))) * self._speed
        self._pos -= offset * dt
        self._update_rays_pos()

    def move_left(self, dt: float) -> None:
        """
        moves the player to the left
        """
        offset: v2 = v2(cos(lib.degree_to_rad(self._angle + 90)),
                        sin(lib.degree_to_rad(self._angle + 90))) * self._speed
        self._pos -= offset * dt
        self._update_rays_pos()

    def move_right(self, dt: float) -> None:
        """
        moves the player to the right
        """
        offset: v2 = v2(cos(lib.degree_to_rad(self._angle - 90)),
                        sin(lib.degree_to_rad(self._angle - 90))) * self._speed
        self._pos -= offset * dt
        self._update_rays_pos()

    def _intersects_with_line(self, l: Line) -> None | tuple[v2, v2]:
        """
        returns None if the player doesnt intersects with a line
        otherwise returns two points where the player and the line intersect
        two returned points will be the same if the line is tangent to the player
        """
        # line
        x1 = l.start.x - self._pos.x
        y1 = l.start.y - self._pos.y
        x2 = l.end.x - self._pos.x
        y2 = l.end.y - self._pos.y
        a = y1 - y2
        b = x2 - x1
        c = y1 * (x2 - x1) - x1 * (y2 - y1)

        # circle
        r = self._r

        d = (r ** 2) * (a ** 2 + b ** 2) - c ** 2

        if d < 0:
            return 

        d = d ** 0.5
        denom = a ** 2 + b ** 2
        
        x1 = (a * c + b * d) / denom
        x2 = (a * c - b * d) / denom
        y1 = (b * c - a * d) / denom
        y2 = (b * c + a * d) / denom

        p1 = v2(x1, y1) + self._pos
        p2 = v2(x2, y2) + self._pos

        if not l.contains_point(p1) and not l.contains_point(p2):
            return
        
        if not l.contains_point(p1) or not l.contains_point(p2):
            closest_line_end = l.start
            far_line_end = l.end
            if self._pos.dist(closest_line_end) > self._pos.dist(l.end):
                closest_line_end, far_line_end = far_line_end, closest_line_end

            if (self._pos - closest_line_end).dot(far_line_end - closest_line_end) >= 0:
                return (p1, p2)
            return (closest_line_end, closest_line_end)

        return (p1, p2)

    def get_rays_distances(self) -> list[dict[str, v2 | float | Line] | None]:
        """
        returns list of points, where rays hit closest wall
        if a ray didnt hit any wall, instead of point will be None 
        """
        return self._calculated_rays_points

    def update(self, walls: list[Line]) -> None:
        """
        update the player
        """
        self._calculated_rays_points = self._calculate_rays()
        
        for wall in walls:
            pts = self._intersects_with_line(wall)
            if pts is None:
                continue
            center_point = (pts[0] + pts[1]) / 2
            amt = self._r - self._pos.dist(center_point)
            direction = (self._pos - center_point).norm()
            self._pos += direction * amt

