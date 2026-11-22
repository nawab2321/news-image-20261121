"""Three lead-story illustrations for the Saturday front page."""

from math import cos, radians, sin
from random import Random

from graphics import Canvas, GOLD, INK, RED


def stipple(canvas, box, interval, ink, seed, density=.8):
    """Place repeatable grain inside a printed color field."""
    left, top, right, bottom = box
    rng = Random(seed)
    for y in range(top, bottom, interval):
        for x in range(left, right, interval):
            if rng.random() < density:
                canvas.dot(x + rng.uniform(-.8, .8), y + rng.uniform(-.8, .8),
                           rng.uniform(.28, .72), ink)


def wind_turbine(canvas, center, blade, color):
    x, y = center
    canvas.polygon([(x - .8, y), (x + .8, y), (x + 1.5, y + 1.55 * blade),
                    (x - 1.5, y + 1.55 * blade)], color)
    for degrees in [-98, 22, 142]:
        angle = radians(degrees)
        tip = x + blade * cos(angle), y + blade * sin(angle)
        shoulder = x + .33 * blade * cos(angle + .3), y + .33 * blade * sin(angle + .3)
        canvas.polygon([(x, y), shoulder, tip], color)
    canvas.dot(x, y, 1.7, color)


def rolling_coast(canvas, width, height):
    """Antalya-inspired coastline with terrain layers and a power horizon."""
    canvas.ellipse(381, -58, 562, 124, "#e5ae63")
    for radius in (52, 66, 79):
        canvas.ellipse(471 - radius, 33 - radius, 471 + radius, 33 + radius,
                       outline="#f3d896", width=.7)
    stipple(canvas, (9, 8, 377, 91), 5, "#52736a", 671)
    ridges = [
        ("#285853", [(0, 87), (54, 76), (114, 92), (170, 60), (237, 80),
                     (308, 77), (368, 103), (430, 93), (493, 72), (width, 91)]),
        ("#6c9488", [(0, 112), (81, 95), (164, 121), (231, 108), (310, 134),
                     (360, 114), (433, 122), (495, 101), (width, 107)]),
        ("#31585a", [(0, 135), (70, 122), (140, 147), (232, 131), (340, 150),
                     (436, 132), (505, 140), (width, 125)]),
    ]
    for color, ridge in ridges:
        canvas.polygon(ridge + [(width, height), (0, height)], color)
    for center, blade in [((396, 91), 15), ((454, 79), 23), ((529, 88), 18)]:
        wind_turbine(canvas, center, blade, "#173e43")
    for left, right, y in [(0, 73, 125), (17, 92, 139), (48, 110, 148),
                           (376, 476, 145), (397, 522, 154), (499, 552, 147)]:
        canvas.line([(left, y), (right, y)], "#a8b6a0", .75)


def draft_and_clock(canvas):
    """A marked-up draft and analog clock stand in for the overnight talks."""
    canvas.polygon([(117, 37), (284, 27), (325, 139), (146, 155)], "#112d34")
    canvas.polygon([(107, 30), (277, 21), (311, 137), (136, 148)], "#c79e61")
    canvas.polygon([(99, 23), (269, 15), (303, 128), (128, 141)], "#f5e7c5")
    canvas.polygon([(237, 17), (269, 15), (279, 39), (252, 39)], "#dfc58e")
    canvas.line([(119, 44), (220, 39)], "#23524b", 4.5)
    for slant, length in [(57, 105), (68, 78), (79, 107), (94, 114), (105, 80),
                          (116, 100)]:
        start = 122 + (slant - 44) * .25
        canvas.line([(start, slant), (start + length, slant - 6)], "#819082", 1.55)
    canvas.line([(127, 91), (249, 84)], "#a24b3e", 2.4)
    canvas.line([(242, 79), (249, 84), (244, 91)], "#a24b3e", 1.9)

    x, y = 323, 97
    canvas.dot(x + 6, y + 5, 42, "#112d34")
    canvas.dot(x, y, 40, "#b78343")
    canvas.dot(x, y, 37, GOLD)
    canvas.dot(x, y, 32, "#f8eaca")
    for hour in range(12):
        a = radians(30 * hour)
        small = 23 if hour % 3 == 0 else 25
        canvas.line([(x + small * cos(a), y + small * sin(a)),
                     (x + 28 * cos(a), y + 28 * sin(a))], INK, .9)
    canvas.line([(x - 2, y - 17), (x, y), (x + 17, y + 7)], INK, 2.7)
    canvas.line([(x + 4, y - 4), (x - 15, y + 17)], RED, 1.15)
    canvas.dot(x, y, 2.35, INK)


def climate_scene(width, height):
    scene = Canvas(width, height, "#173d3d")
    rolling_coast(scene, width, height)
    draft_and_clock(scene)
    return scene


def ukraine_scene():
    scene = Canvas(110, 109, "#eee0cf")
    scene.ellipse(26, 9, 99, 82, "#d5a07b")
    stipple(scene, (4, 4, 108, 75), 4, "#bc997e", 202)
    scene.polygon([(2, 77), (15, 63), (34, 69), (53, 56), (74, 60),
                   (97, 43), (110, 54), (110, 109), (0, 109)], "#907985")
    for left, roof, width, floor_count in [(5, 60, 20, 5), (28, 47, 29, 7),
                                           (61, 66, 19, 4), (83, 58, 23, 6)]:
        right = left + width
        scene.rect(left, roof, right, 109, "#293c4c")
        scene.rect(right - 4, roof, right, 109, "#182d3e")
        scene.line([(left, roof), (right, roof)], "#eed7ba", 1)
        for floor in range(floor_count):
            for span in range(2):
                wx, wy = left + 4 + 7 * span, roof + 7 + 7 * floor
                warm = (floor * 3 + span + left) % 5 in (1, 3)
                scene.rect(wx, wy, wx + 3.2, wy + 2.7, "#e5b982" if warm else "#657179")
    scene.line([(0, 101), (33, 101), (42, 97), (59, 101), (110, 101)], "#b96358", 1.8)
    return scene


def hormuz_scene():
    scene = Canvas(110, 109, "#dce8de")
    scene.ellipse(45, 8, 92, 55, "#e8b977")
    scene.polygon([(0, 52), (19, 38), (35, 43), (52, 54), (71, 55),
                   (91, 43), (110, 47), (110, 109), (0, 109)], "#7ca09c")
    scene.polygon([(0, 75), (14, 64), (36, 64), (53, 72), (82, 60),
                   (110, 66), (110, 109), (0, 109)], "#286675")
    stipple(scene, (4, 81, 110, 108), 4, "#82aba2", 918)
    for left, right, y in [(5, 33, 74), (51, 105, 88), (11, 60, 95), (70, 102, 101)]:
        scene.line([(left, y), (right, y)], "#c0d2bd", .65)
    scene.polygon([(10, 64), (97, 64), (86, 81), (23, 81)], "#162f3b")
    scene.polygon([(17, 75), (90, 75), (86, 81), (23, 81)], "#a95a48")
    scene.rect(25, 53, 42, 64, "#f0dfbd")
    scene.rect(29, 48, 40, 54, "#f0dfbd")
    scene.line([(34, 49), (34, 43)], "#253845", .9)
    scene.line([(31, 56), (38, 56)], "#253845", 1.3)
    scene.rect(47, 60, 80, 63, "#d3a26b")
    scene.line([(50, 59), (76, 59), (79, 61)], "#a35443", 1.4)
    scene.line([(89, 84), (105, 83)], "#d6e0cf", 1.2)
    return scene
