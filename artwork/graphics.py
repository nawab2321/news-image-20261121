"""Drawing tools and original vector-style editorial illustrations."""

from functools import lru_cache
from pathlib import Path

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

    def wrap_lines(self, text, face, size, width, max_lines):
        """Wrap to actual glyph advances before making any marks on the canvas."""
        lines, current = [], []
        for word in text.split():
            if current and self.width(" ".join([*current, word]), face, size) > width:
                lines.append(" ".join(current))
                current = []
            current.append(word)
        if current:
            lines.append(" ".join(current))
        if len(lines) > max_lines or any(self.width(line, face, size) > width for line in lines):
            raise ValueError(f"Cannot fit {text!r} in {max_lines} lines at {width}px")
        return lines

    def draw_lines(self, x, y, lines, face, size, leading, color):
        for line in lines:
            self.text(x, y, line, face, size, color)
            y += leading

    def wrapped(self, x, y, text, face, size, width, leading, max_lines, color=BODY):
        lines = self.wrap_lines(text, face, size, width, max_lines)
        self.draw_lines(x, y, lines, face, size, leading, color)
