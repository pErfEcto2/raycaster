from v2 import V2 as v2
import pygame as pg
import constants
import sys
import importlib


class Line:
    def __init__(self, start: v2, end: v2, color = (255, 255, 255),
                 texture_name: str | None = None) -> None:
        self.start = start
        self.end = end
        self._color = color
        self._texture: list[int] = []

        if texture_name is None or not texture_name:
            self._texture = [255] * (constants.TEXTURE_RESOLUTION ** 2) * 3
        else:
            try:
                brick_wall = importlib.import_module(f"textures.{texture_name}")
                self._texture = brick_wall.texture
            except ImportError as e:
                print("No such texture")
                print(e)
                sys.exit(1)

    def len(self) -> float:
        """
        returns lenght of the line
        """
        return self.start.dist(self.end)

    def get_texture(self, x: int, y: int) -> tuple[int, int, int]:
        i = (y * constants.TEXTURE_RESOLUTION + x) * 3

        return (self._texture[i], self._texture[i + 1], self._texture[i + 2])
    
    def contains_point(self, p: v2) -> bool:
        """
        retuns true if the line contains a point, false otherwise
        """
        ls = self.start
        le = self.end

        lv = le - ls
        pv = p - ls

        return abs(
            (le.x - ls.x) * (p.y - ls.y) -\
            (le.y - ls.y) * (p.x - ls.x)
        ) < 0.0001 and lv.dot(pv) >= 0 and pv.mag() <= lv.mag()
