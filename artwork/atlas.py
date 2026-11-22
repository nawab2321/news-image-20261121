"""Small world atlas with coastline data and geographically anchored callouts."""

import gzip
import json

from graphics import Canvas, INK, MUTED, PAPER, ROOT

SEA = "#e7eee8"
LAND = "#b5c8bd"
GRID = "#cad9d0"
COAST = "#8da89f"

MARKERS = {
    "cop31": (1, -13, 14),
    "kryvyi-rih": (2, 0, -13),
    "hormuz": (3, 15, 3),
    "mexico-cartel": (4, -6, -9),
    "peru-quake": (5, -8, 10),
    "khartoum-kitchens": (6, -10, 16),
    "banda-quake": (7, 5, 10),
    "cyclone-xavier": (8, 7, -11),
}


def project(lon, lat):
    return 12 + (lon + 180) * 1.39, 7 + (84 - lat) * 0.972


def outline_land(canvas):
    with gzip.open(ROOT / "assets" / "land-110m.geojson.gz", "rt", encoding="utf-8") as source:
        dataset = json.load(source)
    for feature in dataset["features"]:
        geometry = feature["geometry"]
        polygons = geometry["coordinates"]
        if geometry["type"] == "Polygon":
            polygons = [polygons]
        for boundary, *holes in polygons:
            if max(lat for _, lat in boundary) < -60:
                continue
            points = [project(lon, lat) for lon, lat in boundary]
            canvas.polygon(points, LAND)
            canvas.line(points, COAST, .45)
            for hole in holes:
                canvas.polygon([project(lon, lat) for lon, lat in hole], SEA)


def badge(canvas, x, y, index, color, radius=7.6):
    canvas.dot(x, y, radius + .7, PAPER)
    canvas.dot(x, y, radius, color)
    canvas.text(x, y + .1, str(index), "bold", radius * 1.52, "white", "mm")


def atlas(stories, region_colors):
    canvas = Canvas(526, 154, SEA)
    for lat in [-45, -15, 15, 45, 75]:
        canvas.line([project(-180, lat), project(180, lat)], GRID, .6)
    for lon in range(-180, 181, 30):
        canvas.line([project(lon, 84), project(lon, -58)], GRID, .6)
    outline_land(canvas)
    for lat in [0, 60, -30]:
        canvas.line([project(-180, lat), project(180, lat)], GRID, .35)
    canvas.text(28, 113, "PACIFIC", "bold", 8, MUTED, "mm")
    canvas.text(218, 106, "ATLANTIC", "bold", 8, MUTED, "mm")
    canvas.text(375, 121, "INDIAN", "bold", 8, MUTED, "mm")
    canvas.text(492, 101, "PACIFIC", "bold", 8, MUTED, "mm")
    points = []
    for story_id, (number, dx, dy) in MARKERS.items():
        story = stories[story_id]
        latitude, longitude = story["coordinates"]
        x, y = project(longitude, latitude)
        color = region_colors[story["region"]]
        canvas.line([(x, y), (x + dx, y + dy)], INK, .7)
        canvas.dot(x, y, 2, INK)
        points.append((x + dx, y + dy, number, color))
    for x, y, number, color in points:
        badge(canvas, x, y, number, color)
    return canvas
