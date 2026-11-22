"""Drawing tools and original vector-style editorial illustrations."""

from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SCALE = 3
FONT_FILES = {
    "serif": "CormorantGaramond.ttf",
    "sans": "BarlowSemiCondensed-Medium.ttf",
    "bold": "BarlowSemiCondensed-Bold.ttf",
}
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


@lru_cache(maxsize=128)
def font(face, pixel_size):
    """Load a font once per raster size, including equivalent editorial sizes."""
    path = ROOT / "assets" / "fonts" / FONT_FILES[face]
    result = ImageFont.truetype(str(path), pixel_size)
    if face == "serif":
        result.set_variation_by_axes([700])
    return result


def scaled(value):
    return round(value * SCALE)


def point(pair):
    return scaled(pair[0]), scaled(pair[1])


def bounds(left, top, right, bottom):
    return scaled(left), scaled(top), scaled(right), scaled(bottom)


class Canvas:
    def __init__(self, columns, rows, color):
        self.size = point((columns, rows))
        self.image = Image.new(mode="RGB", size=self.size, color=color)
        self.draw = ImageDraw.Draw(self.image)

    def rect(self, x0, y0, x1, y1, color):
        self.draw.rectangle(bounds(x0, y0, x1, y1), fill=color)

    def line(self, points, color, width=1):
        pixels = [point(vertex) for vertex in points]
        stroke = max(1, scaled(width))
        self.draw.line(pixels, fill=color, width=stroke, joint="curve")

    def polygon(self, points, color):
        self.draw.polygon(list(map(point, points)), fill=color)

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        pixel_width = max(1, scaled(width))
        self.draw.ellipse(bounds(x0, y0, x1, y1), fill=fill, outline=outline, width=pixel_width)

    def dot(self, x, y, radius, color):
        self.ellipse(x - radius, y - radius, x + radius, y + radius, color)

    def put(self, inset, x, y):
        left, top = point((x, y))
        width, height = inset.size
        if min(left, top) < 0 or left + width > self.size[0] or top + height > self.size[1]:
            raise ValueError(f"Illustration at ({x}, {y}) exceeds the page")
        self.image.paste(inset.image, (left, top))

    def width(self, text, face, size):
        return self.draw.textlength(text, font=font(face, scaled(size))) / SCALE

    def text(self, x, y, text, face, size, color=INK, anchor="lt"):
        position = point((x, y))
        typeface = font(face, scaled(size))
        left, top, right, bottom = self.draw.textbbox(position, text, font=typeface, anchor=anchor)
        if min(left, top) < 0 or right > self.size[0] or bottom > self.size[1]:
            raise ValueError(f"Text {text!r} at ({x}, {y}) exceeds its image")
        self.draw.text(position, text, fill=color, font=typeface, anchor=anchor)

    def spaced(self, x, y, text, size, color=INK, tracking=1.25):
        for character in text:
            self.text(x, y, character, "bold", size, color, "la")
            x += self.width(character, "bold", size) + tracking

    def fit(self, x, y, text, face, size, width, color=INK, min_size=None):
        """Use the largest whole raster size that fits the available measure."""
        smallest = scaled(size if min_size is None else min_size)
        largest = scaled(size)
        for pixel_size in range(largest, smallest - 1, -1):
            typeface = font(face, pixel_size)
            if self.draw.textlength(text, font=typeface) <= scaled(width):
                self.text(x, y, text, face, pixel_size / SCALE, color)
                return
        raise ValueError(f"No allowed size fits {text!r} in {width}px")

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
