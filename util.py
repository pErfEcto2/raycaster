from line import Line
from v2 import V2 as v2
import _pickle as pl


def generate_map(grid: list[str], w: int, h: int) -> list[Line]:
    try:
        with open("map.pkl", "rb") as f:
            try:
                res = pl.load(f)
                return res
            except EOFError:
                pass
    except OSError:
        pass

    if not grid:
        raise Exception("grid is empty")

    grid_w = len(grid[0])
    for row in grid:
        if len(row) != grid_w:
            raise Exception("grid is not a rectangle")

    res = []
    grid_h = len(grid)
    wall_len_h = w // grid_w + 1
    wall_len_v = h // grid_h + 1
    for i in range(grid_h):
        for j in range(grid_w):
            texture_name = ""
            match grid[i][j]:
                case " ":
                    continue
                case "b":
                    texture_name = "brick_wall"
                case "w":
                    texture_name = ""

            if i - 1 >= 0 and grid[i - 1][j] == " ":
                res.append(Line(v2(j * wall_len_h, i * wall_len_v),
                                v2((j + 1) * wall_len_h, i * wall_len_v),
                                texture_name=texture_name))
            if i + 1 < grid_h and grid[i + 1][j] == " ":
                res.append(Line(v2(j * wall_len_h, (i + 1) * wall_len_v),
                                v2((j + 1) * wall_len_h, (i + 1) * wall_len_v),
                                texture_name=texture_name))

            if j - 1 >= 0 and grid[i][j - 1] == " ":
                res.append(Line(v2(j * wall_len_h, i * wall_len_v),
                                v2(j * wall_len_h, (i + 1) * wall_len_v),
                                texture_name=texture_name))
            if j + 1 < grid_w and grid[i][j + 1] == " ":
                res.append(Line(v2((j + 1) * wall_len_h, i * wall_len_v),
                                v2((j + 1) * wall_len_h, (i + 1) * wall_len_v),
                                texture_name=texture_name))
    with open("map.pkl", "wb") as f:
        pl.dump(res, f, -1)

    return res
