from math import sin, cos
import pygame as pg
from v2 import V2 as v2
from line import Line
import lib
from shapely import LineString


class Ray:
    def _get_end(self) -> v2:
        """
        returns a point - end of the normalized vector
        """
        return self.start + v2(cos(lib.degree_to_rad(self._angle)),
                               sin(lib.degree_to_rad(self._angle)))

    def __init__(self, start: v2, angle: float = 0, color = (255, 255, 255)) -> None:
        self.start = start
        self._angle = angle
        self._color = color
        self.end = self._get_end()
        ray_end = self.start + lib.v2_from_angle(self.get_angle()) * 10000
        self._ray_line = LineString([(self.start.x, self.start.y), (ray_end.x, ray_end.y)])

    def get_ray_line(self) -> LineString:
        return self._ray_line

    def get_angle(self) -> float:
        return self._angle

    def rotate(self, angle) -> None:
        self._angle += angle
        self.end = self._get_end()

    def intersects_with_line(self, l: Line) -> v2 | None:
        """
        returns None if the ray and a line doesnt intersect
        otherwise returns an intersection point
        """
        x1 = self.start.x
        y1 = self.start.y
        x2 = self.end.x
        y2 = self.end.y

        x3 = l.start.x
        y3 = l.start.y
        x4 = l.end.x
        y4 = l.end.y

        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if abs(denom) == 0.0001:
            return

        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4))
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3))

        # some optimization
        if  t < 0 and denom > 0 or\
            t > 0 and denom < 0 or\
            u < 0 and denom > 0 or\
            u > 0 and denom < 0 or\
            u > 0 and u > denom or\
            u < 0 and u < denom:
            return


        t /= denom
        u /= denom

        return v2(
            x1 + t * (x2 - x1),
            y1 + t * (y2 - y1)
        )
