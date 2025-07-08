from math import atan2, pi, sin, cos
from line import Line
from v2 import V2 as v2


def clamp(val: float | int, minn: float | int, maxx: float | int) -> float | int:
    """
    clamps a value between a minimum and a maximum
    """
    return min(max(val, minn), maxx)

def map_value(val: float | int,
              val_min: float | int,
              val_max: float | int,
              res_min: float | int,
              res_max: float | int) -> float:
    """
    maps a value from one range to another
    """
    normalized = (val - val_min) / (val_max - val_min)
    return res_min + normalized * (res_max - res_min)

def rad_to_degree(rad: float) -> float:
    """
    converts radians to degrees
    """
    return rad * 180 / pi

def degree_to_rad(degree: float) -> float:
    """
    converts degrees to radians
    """
    return degree * pi / 180

def v2_from_angle(angle: float) -> v2:
    """
    returns normalized vector from the given angle
    """
    return v2(cos(degree_to_rad(angle)), sin(degree_to_rad(angle)))

def angle_between_lines(l1: Line, l2: Line) -> float:
    """
    return an angle between two given lines
    """
    u = l1.end - l1.start
    v = l2.end - l2.start
    dot = u.dot(v)
    cross = u[0] * v[1] - u[1] * v[0]
    angle_rad = atan2(cross, dot)
    return rad_to_degree(angle_rad) % 360

