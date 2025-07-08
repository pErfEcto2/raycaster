import pygame as pg
from v2 import V2 as v2
import constants


class Rect:
    def __init__(self, top_left: v2, w: float | int, h: float | int, color = constants.WHITE) -> None:
        self.top_left = top_left
        self.w = w
        self.h = h
        self.color = color

    def get_bottom_right(self) -> v2:
        return self.top_left + v2(self.w, self.h)

    def intersects(self, o) -> bool:
        """
        returns true if this rect and other one intersects, otherwise false
        """
        o_tl = o.top_left
        o_br = o.get_bottom_right()
        t_tl = self.top_left
        t_br = self.get_bottom_right()
        
        return not (
            o_br.x < t_tl.x or\
            o_br.y < t_tl.y or\
            o_tl.x > t_br.x or\
            o_tl.y > t_br.y
        )

    def contains(self, p: v2) -> bool:
        """
        returns true if the rect contains a point, otherwise false
        """
        t_br = self.get_bottom_right()
        return (p.x >= self.top_left.x and p.y >= self.top_left.y) and\
               (p.x <= t_br.x and p.y <= t_br.y)

    def __str__(self) -> str:
        br = self.get_bottom_right()
        return f"Rect[from ({self.top_left.x}, {self.top_left.y}) to\
({br.x}, {br.y})]"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, o) -> bool:
        return self.top_left == o.top_left and self.w == o.w and self.h == o.h
