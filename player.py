import pygame as pg
from v2 import V2 as v2
from math import sin, cos
from ray import Ray
from line import Line
import lib
from shapely.geometry import LineString
from shapely.strtree import STRtree


class Player:
    def __init__(self, pos: v2, walls: list[Line], fov: float = 90, rays_number: float = 0.5,
                 rotation_speed: int = 200, speed: int = 500, angle: float = 0,
                 r: float = 20) -> None:
        self._pos = pos
        self._walls = walls
        lines = [
            LineString([(wall.start.x, wall.start.y), (wall.end.x, wall.end.y)])
            for wall in self._walls
        ]
        self._walls_tree = STRtree(lines)
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

    def get_rays(self) -> list[Ray]:
        return self._rays

    def get_angle(self) -> float:
        return self._angle

    def get_pos(self) -> v2:
        return self._pos

    def get_size(self) -> float:
        return self._r

    def _calculate_rays(self) -> list[dict[str, v2 | float | Line] | None]:
        res = []
        for ray in self._rays:
            ray_end = ray.start + lib.v2_from_angle(ray.get_angle()) * 10000
            ray_line = LineString([(ray.start.x, ray.start.y), (ray_end.x, ray_end.y)])

            closest_point: v2 | None = None
            closest_wall: Line | None = None

            for wall_idx in self._walls_tree.query_nearest(ray_line):
                wall = self._walls[wall_idx]
                tmp_point: v2 | None = ray.intersects_with_line(wall)
                if tmp_point is None:
                    continue
                if closest_point is None:
                    closest_point = tmp_point
                    closest_wall = wall
                else:
                    if ray.start.dist(tmp_point) < ray.start.dist(closest_point):
                        closest_point = tmp_point
                        closest_wall = wall

            if closest_point is None:
                res.append(None)
            else:
                res.append({"angle": ray.get_angle(),
                            "pos": closest_point,
                            "line": closest_wall,
                            "dist": self._pos.dist(closest_point)})

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

