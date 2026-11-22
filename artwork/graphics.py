"""Drawing tools and original vector-style editorial illustrations."""

from functools import lru_cache
from math import cos, radians, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 3
PAPER = "#f6f1e6"
INK = "#122b38"
BODY = "#263c44"
MUTED = "#415963"
RULE = "#b7b5a7"
RED = "#9b3e36"
FOREST = "#275e51"
TEAL = "#236674"
GOLD = "#d4a35a"
COPPER = "#875135"


@lru_cache(maxsize=None)
def font(face, size):
    fonts = ROOT / "assets/fonts"
    filename = {
        "serif": "CormorantGaramond.ttf",
        "sans": "BarlowSemiCondensed-Medium.ttf",
        "bold": "BarlowSemiCondensed-Bold.ttf",
    }[face]
    result = ImageFont.truetype(str(fonts / filename), round(size * SCALE))
    if face == "serif":
        result.set_variation_by_axes([700])
    return result


class Canvas:
    def __init__(self, width, height, color):
        self.image = Image.new("RGB", (round(width * SCALE), round(height * SCALE)), color)
        self.draw = ImageDraw.Draw(self.image)

    @staticmethod
    def point(point):
        return tuple(round(dimension * SCALE) for dimension in point)

    def rect(self, x0, y0, x1, y1, color):
        self.draw.rectangle((*self.point((x0, y0)), *self.point((x1, y1))), fill=color)

    def line(self, points, color, width=1):
        self.draw.line([self.point(point) for point in points], fill=color,
                       width=max(1, round(width * SCALE)), joint="curve")

    def polygon(self, points, color):
        self.draw.polygon([self.point(point) for point in points], fill=color)

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        self.draw.ellipse((*self.point((x0, y0)), *self.point((x1, y1))), fill=fill,
                          outline=outline, width=max(1, round(width * SCALE)))

    def dot(self, x, y, radius, color):
        self.ellipse(x - radius, y - radius, x + radius, y + radius, color)

    def put(self, other, x, y):
        self.image.paste(other.image, self.point((x, y)))

    def width(self, text, face, size):
        return self.draw.textlength(text, font=font(face, size)) / SCALE

    def text(self, x, y, text, face, size, color=INK, anchor="lt"):
        self.draw.text(self.point((x, y)), text, fill=color, font=font(face, size), anchor=anchor)

    def spaced(self, x, y, text, size, color=INK, tracking=1.25):
        for character in text:
            self.text(x, y, character, "bold", size, color, "la")
            x += self.width(character, "bold", size) + tracking

    def fit(self, x, y, text, face, size, width, color=INK, min_size=None):
        minimum = size if min_size is None else min_size
        while self.width(text, face, size) > width and size > minimum:
            size -= 0.25
        if self.width(text, face, size) > width:
            raise ValueError(f"Cannot fit {text!r} in {width}px")
        self.text(x, y, text, face, size, color)

    def wrapped(self, x, y, text, face, size, width, leading, max_lines, color=BODY):
        lines = []
        current = ""
        for word in text.split():
            candidate = f"{current} {word}".lstrip()
            if not current or self.width(candidate, face, size) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
        if len(lines) > max_lines or any(self.width(line, face, size) > width for line in lines):
            raise ValueError(f"Cannot wrap {text!r} in {max_lines} lines at {width}px: {lines}")
        for index, line in enumerate(lines):
            self.text(x, y + leading * index, line, face, size, color)
        return len(lines)


def hatch(canvas, left, top, right, bottom, step, color, seed):
    rng = Random(seed)
    for y in range(top, bottom, step):
        for x in range(left, right, step):
            if rng.random() < 0.77:
                canvas.dot(x + rng.uniform(-0.6, 0.6), y + rng.uniform(-0.6, 0.6),
                           rng.uniform(0.23, 0.68), color)


def turbine(canvas, x, y, radius, color):
    canvas.line([(x, y + radius * 1.5), (x, y)], color, 1.5)
    canvas.dot(x, y, 2, color)
    for angle in (-94, 26, 146):
        a = radians(angle)
        tip = (x + radius * cos(a), y + radius * sin(a))
        back = (x + radius * .29 * cos(a + .34), y + radius * .29 * sin(a + .34))
        canvas.polygon([(x, y), back, tip], color)


def climate_scene(width, height):
    canvas = Canvas(width, height, "#173d3d")
    # The alternating bands evoke an Antalya coast at dusk.
    canvas.ellipse(360, -82, 560, 118, "#e9b76e")
    canvas.ellipse(373, -69, 547, 105, outline="#fae2ab", width=1)
    canvas.ellipse(387, -55, 533, 91, outline="#fae2ab", width=0.6)
    hatch(canvas, 8, 8, 355, 71, 5, "#456358", 21)
    canvas.polygon([(0, 94), (70, 75), (105, 85), (175, 62), (243, 87), (291, 84),
                    (340, 108), (389, 79), (430, 66), (503, 82), (width, 53),
                    (width, height), (0, height)], "#2c645b")
    canvas.polygon([(0, 110), (79, 93), (139, 114), (209, 91), (342, 133),
                    (431, 107), (width, 108), (width, height), (0, height)], "#6f9790")
    canvas.polygon([(0, 129), (75, 121), (171, 143), (262, 133), (349, 152),
                    (448, 121), (width, 124), (width, height), (0, height)], "#2d5556")
    for y, begin, end in [(119, 2, 77), (133, 5, 131), (139, 32, 135),
                          (151, 390, 515), (157, 410, 548), (142, 460, 539)]:
        canvas.line([(begin, y), (end, y)], "#a4b2a2", .8)
    for x, y, radius in [(365, 85, 19), (413, 87, 15), (507, 88, 22), (544, 83, 13)]:
        turbine(canvas, x, y, radius, "#173d3d")

    # Annotated draft sheets and an analog clock are editorial symbols.
    canvas.polygon([(130, 36), (287, 23), (342, 136), (166, 160)], "#0c292f")
    canvas.polygon([(118, 28), (278, 18), (326, 132), (153, 152)], "#cea267")
    canvas.polygon([(109, 21), (269, 14), (313, 123), (145, 146)], "#f5e7c3")
    canvas.polygon([(239, 16), (269, 14), (281, 44)], "#d6b97e")
    canvas.line([(129, 43), (228, 37)], "#264f4d", 4)
    for y, x, length in [(57, 136, 74), (67, 139, 107), (77, 143, 90),
                         (92, 148, 113), (104, 154, 70), (114, 158, 84)]:
        canvas.line([(x, y), (x + length, y - 7)], "#8f9a81", 2)
    canvas.line([(142, 90), (257, 81)], "#ac4f3d", 3)
    cx, cy = 306, 100
    canvas.dot(cx + 5, cy + 5, 37, "#112e35")
    canvas.dot(cx, cy, 36, "#dba75c")
    canvas.dot(cx, cy, 31, "#f7e8c7")
    for degree in range(0, 360, 30):
        a = radians(degree)
        canvas.line([(cx + 23 * cos(a), cy + 23 * sin(a)),
                     (cx + 27 * cos(a), cy + 27 * sin(a))], INK, .9)
    canvas.line([(cx, cy - 17), (cx, cy), (cx + 15, cy + 7)], INK, 2.2)
    canvas.line([(cx, cy), (cx - 7, cy + 19)], RED, 1.2)
    canvas.dot(cx, cy, 2.5, RED)
    return canvas


def ukraine_scene():
    canvas = Canvas(110, 109, "#eadfd0")
    canvas.ellipse(32, 7, 97, 72, "#d5a07a")
    hatch(canvas, 4, 5, 106, 104, 4, "#c8a78f", 19)
    canvas.polygon([(0, 70), (20, 64), (34, 68), (61, 55), (81, 66), (110, 58),
                    (110, 109), (0, 109)], "#9a7781")
    for x, y, w, levels in [(6, 61, 22, 5), (31, 48, 28, 7), (63, 66, 16, 5), (83, 53, 24, 6)]:
        canvas.rect(x, y, x + w, 109, "#27394a")
        canvas.rect(x + w - 4, y + 3, x + w, 109, "#182a3b")
        for row in range(levels):
            for column in range(2):
                if (row + column * 3 + x) % 5 != 0:
                    wx, wy = x + 4 + column * 7, y + 7 + row * 7
                    canvas.rect(wx, wy, wx + 3, wy + 2.5, "#e2b98a")
    canvas.line([(0, 101), (27, 101), (49, 96), (78, 101), (110, 101)], "#b65b52", 2)
    return canvas


def hormuz_scene():
    canvas = Canvas(110, 109, "#dce8df")
    canvas.ellipse(44, 7, 92, 55, "#e9bd79")
    canvas.polygon([(0, 54), (20, 40), (39, 44), (63, 55), (83, 46), (110, 48),
                    (110, 109), (0, 109)], "#6b9a99")
    canvas.polygon([(0, 72), (23, 61), (52, 70), (78, 60), (110, 64),
                    (110, 109), (0, 109)], "#276773")
    hatch(canvas, 3, 81, 110, 106, 4, "#7caaa5", 13)
    for y, x0, x1 in [(74, 4, 36), (86, 54, 106), (93, 6, 53), (99, 59, 102)]:
        canvas.line([(x0, y), (x1, y)], "#b4cdc0", .75)
    canvas.polygon([(11, 65), (99, 65), (87, 80), (22, 80)], "#132c38")
    canvas.polygon([(17, 75), (91, 75), (87, 80), (22, 80)], "#aa5f4b")
    canvas.rect(27, 53, 43, 65, "#f2e4c8")
    canvas.rect(30, 48, 40, 54, "#f2e4c8")
    canvas.line([(34, 48), (34, 43)], INK, 1)
    canvas.line([(31, 56), (39, 56)], INK, 1.4)
    canvas.rect(47, 60, 79, 64, "#d8a466")
    canvas.line([(49, 61), (80, 61)], RED, 1)
    return canvas
