import line
import ray
import rect
import player
import pygame as pg
from v2 import V2 as v2


def draw_object(w, obj, color = (255, 255, 255), scale: float = 1, offset: v2 = v2(0, 0)) -> None:
    """
    draws an object on the given surface
    the drawings can be modified using scale and offset params
    """
    match obj.__class__:
        case line.Line:
            pg.draw.line(w, color, list(obj.start * scale + offset), list(obj.end * scale + offset))
        case ray.Ray:
            end = obj.end
            end -= obj.start
            end = (end * 100) + obj.start
            pg.draw.line(w, color, list(obj.start * scale + offset), list(end * scale + offset))
        case rect.Rect:
            pg.draw.rect(w, color, [*list(obj.top_left * scale + offset), obj.w * scale, obj.h * scale])
        case player.Player:
            pg.draw.circle(w, color, list(obj.get_pos() * scale + offset), obj.get_size() * scale)
        case _:
            raise ValueError("invalid object class")
