import pygame as pg
from v2 import V2 as v2
from player import Player
from rect import Rect
import constants
import draw
import lib
import math
import util


pg.init()

# window = pg.display.set_mode((500, 500)) # for debugging 
window = pg.display.set_mode((0, 0), pg.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = window.get_size()
LONGEST_LINE_LEN = v2(SCREEN_WIDTH, SCREEN_HEIGHT).mag()

MINIMAP_OFFSET = v2(SCREEN_WIDTH * (1 - constants.MINIMAP_SCALE), 1)
FPS_OFFSET = (int(SCREEN_WIDTH * constants.FPS_OFFSET_FACTOR[0]),
              int(SCREEN_HEIGHT * constants.FPS_OFFSET_FACTOR[1]))

pg.display.set_caption("fps")
pg.mouse.set_visible(False)
pg.event.set_grab(True) # keep mouse confined to window

clock = pg.time.Clock()

pg.font.init()
if not pg.font.get_init():
    raise Exception("something went wrong with the font")
font = pg.font.SysFont("FiraCode", 30)

keys_pressed = {}

p = Player(v2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2),
           fov=constants.FOV,
           rays_number=SCREEN_WIDTH / 10 + 1,
           r=50)

# dont forget to remove "map.pkl" file!
grid = [
    "bbbbbbbbbbbbb",
    "b           b",
    "b      ww w b",
    "b ww w      b",
    "b           b",
    "b    b      b",
    "bbbbbbb  bbbb",
    "b           b",
    "bbbbbbbbbbbbb",
]

walls = util.generate_map(grid, SCREEN_WIDTH, SCREEN_HEIGHT)


running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

        if event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                keys_pressed[constants.LEFT_MOUSE] = True

        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                keys_pressed[constants.LEFT_MOUSE] = False

        if event.type == pg.KEYDOWN:
            keys_pressed[event.key] = True

        if event.type == pg.KEYUP:
            keys_pressed[event.key] = False

    dt = clock.tick(60) / 1000

    text = font.render(str(int(1 / dt)), True, constants.GREEN)
    text_rect = text.get_rect()
    text_rect.topleft = FPS_OFFSET

    if keys_pressed.get(pg.K_UP) or keys_pressed.get(constants.K_W):
        p.move_forward(dt)
    if keys_pressed.get(pg.K_DOWN) or keys_pressed.get(constants.K_S):
        p.move_backwards(dt)

    if keys_pressed.get(pg.K_RIGHT) or keys_pressed.get(constants.K_D):
        p.move_right(dt)
    if keys_pressed.get(pg.K_LEFT) or keys_pressed.get(constants.K_A):
        p.move_left(dt)

    mouse_rel_x = pg.mouse.get_rel()[0]
    p.rotate_right(mouse_rel_x * constants.MOUSE_SENSITIVITY, dt)

    p.update(walls)

    # i'm not proud of the naming...
    points = p.get_rays_distances()
    rects: list[None | Rect] = []
    n = len(points)
    rect_width = int(SCREEN_WIDTH / n) + 1

    for i, point in enumerate(points):
        if point is None:
            rects.append(None)
            continue

        # wall
        true_distance = p.get_pos().dist(point["pos"])
        ray_angle_diff = p.get_angle() - point["angle"]
        distance = true_distance * math.cos(lib.degree_to_rad(ray_angle_diff))
        distance = max(0.1, distance)  # Avoid division by zero
        rect_height = SCREEN_HEIGHT * 100 / distance # magic number

        # wall's texture
        h = constants.TEXTURE_RESOLUTION
        x = int(h * (point["line"].start.dist(point["pos"]) / point["line"].len()))
        if  0 <= p.get_angle() <= 180 and point["line"].start.y == point["line"].end.y or\
            90 <= p.get_angle() <= 270 and point["line"].start.x == point["line"].end.x:
            x = h - x - 1

        for y in range(h):
            rect_height_offset = (SCREEN_HEIGHT - rect_height) / 2 + rect_height / h * y 
            rect = Rect(
                v2(i * rect_width, rect_height_offset),
                rect_width,
                rect_height / h
            )

            brightness = lib.map_value(distance, 0, SCREEN_HEIGHT, 1, 0)
            brightness = lib.clamp(brightness, 0, 1)
            color = point["line"].get_texture(x, y)
            color = (
                color[0] * brightness,
                color[1] * brightness,
                color[2] * brightness
            )

            if color != (0, 0, 0):
                rect.color = color
                rects.append(rect)

    window.fill(constants.BLACK)

    # draw walls
    for rect in rects:
        if rect is not None:
            pg.draw.rect(window,
                        rect.color,
                        [*list(rect.top_left), rect.w, rect.h])

    # draw minimap
    pg.draw.rect(window,
                 constants.BLACK,
                 [MINIMAP_OFFSET[0],
                  MINIMAP_OFFSET[1],
                  SCREEN_WIDTH * constants.MINIMAP_SCALE,
                  SCREEN_HEIGHT * constants.MINIMAP_SCALE
                  ]
                 )
    for wall in walls:
        draw.draw_object(window, wall, scale=constants.MINIMAP_SCALE, offset=MINIMAP_OFFSET)

    draw.draw_object(window, p, scale=constants.MINIMAP_SCALE, offset=MINIMAP_OFFSET)

    for ray in p.get_rays():
        draw.draw_object(window, ray, scale=constants.MINIMAP_SCALE, offset=MINIMAP_OFFSET)

    # draw fps counter
    window.blit(text, text_rect)

    pg.display.flip()

pg.quit()
