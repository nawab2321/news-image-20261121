"""Equal Earth atlas with numbered locations and offset labels."""

import gzip
import json
from math import asin, cos, radians, sin, sqrt

from graphics import Canvas, INK, MUTED, PAPER, ROOT

OCEAN = "#e7eee8"
LAND = "#afc4b8"
GRATICULE = "#c9d9d1"
SHORELINE = "#819f93"
MAP_WIDTH = 526
MAP_HEIGHT = 154

# Values hold the printed number and the label offset from the measured dot.
POINTS = {
    "cop31": (1, -15, 13),
    "kryvyi-rih": (2, 0, -12),
    "hormuz": (3, 14, 4),
    "mexico-cartel": (4, -6, -8),
    "peru-quake": (5, -8, 11),
    "khartoum-kitchens": (6, -13, 16),
    "banda-quake": (7, 8, 9),
    "cyclone-xavier": (8, 8, -10),
}


def project(longitude, latitude):
    """Project geographic degrees into the front page's cropped map frame."""
    parallel = asin(sqrt(3) / 2 * sin(radians(latitude)))
    squared = parallel * parallel
    a, b, c, d = 1.340264, -.081106, .000893, .003796
    meridian_scale = a + 3 * b * squared + squared**3 * (7 * c + 9 * d * squared)
    easting = 2 * sqrt(3) * radians(longitude) * cos(parallel) / (3 * meridian_scale)
    northing = parallel * (a + b * squared + squared**3 * (c + d * squared))
    return MAP_WIDTH / 2 + easting * 91.8, 84 - northing * 57


def load_land():
    resource = ROOT / "assets" / "land-110m.geojson.gz"
    with gzip.open(resource, mode="rt", encoding="utf-8") as stream:
        for feature in json.load(stream)["features"]:
            geometry = feature["geometry"]
            if geometry["type"] == "Polygon":
                yield geometry["coordinates"]
            else:
                yield from geometry["coordinates"]


def draw_graticule(canvas):
    for latitude in (-45, -15, 15, 45, 75):
        parallel = [project(lon, latitude) for lon in range(-180, 181, 4)]
        canvas.line(parallel, GRATICULE, .68)
    for longitude in range(-180, 181, 30):
        meridian = [project(longitude, lat) for lat in range(-60, 85, 3)]
        canvas.line(meridian, GRATICULE, .68)


def draw_land(canvas):
    for coast, *lakes in load_land():
        if max(point[1] for point in coast) < -60:
            continue
        edge = [project(*point) for point in coast]
        canvas.polygon(edge, LAND)
        canvas.line(edge, SHORELINE, .45)
        for lake in lakes:
            canvas.polygon([project(*point) for point in lake], OCEAN)


def badge(canvas, x, y, number, color, radius=7.6):
    canvas.dot(x, y, radius + .8, PAPER)
    canvas.dot(x, y, radius, color)
    canvas.text(x, y + .3, str(number), "bold", radius * 1.55, "white", "mm")


def atlas(stories, colors):
    field = Canvas(MAP_WIDTH, MAP_HEIGHT, OCEAN)
    draw_graticule(field)
    draw_land(field)
    for label, lon, lat in [
        ("PACIFIC", -150, -25), ("ATLANTIC", -29, -23),
        ("INDIAN", 78, -32), ("PACIFIC", 163, -10),
    ]:
        x, y = project(lon, lat)
        field.text(x, y, label, "bold", 8.4, MUTED, "mm")
    badges = []
    for story_id, (number, offset_x, offset_y) in POINTS.items():
        story = stories[story_id]
        lat, lon = story["coordinates"]
        if not -60 <= lat <= 84 or not -180 <= lon <= 180:
            raise ValueError(f"Map location outside the atlas for {story_id}")
        x, y = project(lon, lat)
        label_x, label_y = x + offset_x, y + offset_y
        field.line([(x, y), (label_x, label_y)], INK, .72)
        field.dot(x, y, 1.9, INK)
        badges.append((label_x, label_y, number, colors[story["region"]]))
    for mark in badges:
        badge(field, *mark)
    return field
