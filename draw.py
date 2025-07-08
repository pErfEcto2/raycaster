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
    if isinstance(obj, line.Line):
        pg.draw.line(w, color, list(obj.start * scale + offset), list(obj.end * scale + offset))
        return

    if isinstance(obj, ray.Ray):
        end = obj.end
        end -= obj.start
        end = (end * 100) + obj.start
        pg.draw.line(w, color, list(obj.start * scale + offset), list(end * scale + offset))
        return
    
    if isinstance(obj, rect.Rect):
        pg.draw.rect(w, color, [*list(obj.top_left * scale + offset), obj.w * scale, obj.h * scale])
        return
    
    if isinstance(obj, player.Player):
        pg.draw.circle(w, color, list(obj.get_pos() * scale + offset), obj.get_size() * scale)
        return

    raise ValueError("invalid object class")
