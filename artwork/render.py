"""Compose the 21 November front page from the audited story ledger."""

import json

from PIL import Image

from atlas import MARKERS, atlas, badge
from graphics import (
    COPPER, FOREST, INK, MUTED, PAPER, RED, ROOT, RULE, TEAL,
    Canvas, climate_scene, hormuz_scene, ukraine_scene,
)

LEFT = 34
RIGHT = 990
COLUMNS = (34, 278, 522, 766)
COLUMN_WIDTH = 224
REGIONS = {
    "Europe": "#315a78",
    "Middle East": RED,
    "Asia": TEAL,
    "International": FOREST,
    "Americas": "#634d70",
    "Africa": COPPER,
    "Oceania": "#3e6757",
}


def section_rule(canvas, y, color=RULE):
    canvas.line([(LEFT, y), (RIGHT, y)], color)


def masthead(canvas):
    section_rule(canvas, 26, INK)
    canvas.rect(LEFT, 26, LEFT + 47, 30, RED)
    canvas.spaced(LEFT, 36, "WORLD NEWS", 13, RED, 2.5)
    canvas.fit(LEFT - 2, 53, "The World at a Glance", "serif", 76, 682, min_size=68)
    canvas.line([(742, 42), (742, 114)], RULE)
    canvas.text(754, 44, "21", "serif", 103, RED)
    canvas.spaced(858, 40, "SATURDAY", 18, INK, 1.8)
    canvas.spaced(858, 64, "NOVEMBER", 18, INK, 1.6)
    canvas.spaced(858, 87, "2026", 23, INK, 2.3)
    section_rule(canvas, 126, INK)
    section_rule(canvas, 130)


def lead_tag(canvas, x, y, story):
    color = REGIONS[story["region"]]
    badge(canvas, x + 8, y + 9, MARKERS[story["id"]][0], color)
    label = f'{story["category"]}  /  {story["location"]}'.upper()
    canvas.spaced(x + 22, y, label, 12.5, color, 1.06)


def lead_stories(canvas, stories):
    story = stories["cop31"]
    lead_tag(canvas, LEFT, 139, story)
    canvas.put(climate_scene(569, 161), LEFT, 163)
    canvas.fit(LEFT, 331, story["headline"], "serif", 57, 569, min_size=49)
    canvas.wrapped(LEFT + 2, 389, story["verified_summary"], "sans", 20, 553, 23, 2)
    canvas.line([(618, 142), (618, 425)], RULE)
    for story_id, top, scene in [("kryvyi-rih", 139, ukraine_scene),
                                  ("hormuz", 284, hormuz_scene)]:
        story = stories[story_id]
        lead_tag(canvas, 635, top, story)
        canvas.put(scene(), 880, top + 21)
        canvas.wrapped(635, top + 22, story["headline"], "serif", 32, 235, 30, 2, INK)
        canvas.wrapped(636, top + 85, story["verified_summary"], "sans", 16, 229, 17, 3)
    canvas.line([(635, 275), (RIGHT, 275)], RULE)


def news_atlas(canvas, stories):
    section_rule(canvas, 438, INK)
    canvas.spaced(LEFT, 447, "THE DAY ON THE MAP", 13, FOREST, 2.0)
    canvas.spaced(819, 447, "THE DAY IN NUMBERS", 13, FOREST, 1.5)
    canvas.put(atlas(stories, REGIONS), LEFT, 473)

    for position, story_id in enumerate(MARKERS):
        story = stories[story_id]
        x = 575 + (position // 4) * 116
        y = 477 + (position % 4) * 38
        badge(canvas, x + 8, y + 10, position + 1, REGIONS[story["region"]])
        canvas.text(x + 21, y + 1, story["atlas_label"], "bold", 16)
        canvas.text(x + 21, y + 18, story["atlas_detail"], "sans", 13, MUTED)

    canvas.line([(802, 446), (802, 629)], RULE)
    for index, story_id in enumerate(("banda-quake", "air-niugini", "geneva-weapons")):
        story = stories[story_id]
        metric = story["number"]
        y = 474 + index * 52
        canvas.text(818, y, metric["value"], "serif", 38, REGIONS[story["region"]])
        canvas.wrapped(905, y + 5, metric["label"], "bold", 14.5, 84, 15, 3)
        if index < 2:
            canvas.line([(819, y + 45), (RIGHT, y + 45)], RULE)
    section_rule(canvas, 638, INK)


def emblem(canvas, name, x, y, color):
    def stroke(points):
        canvas.line([(x + a, y + b) for a, b in points], color, 1.3)

    if name == "Europe":
        stroke([(1, 1), (16, 1), (15, 11), (8.5, 17), (2, 11), (1, 1)])
        stroke([(5, 8), (8, 11), (13, 5)])
    elif name == "Middle East":
        stroke([(1, 15), (1, 9), (4, 5), (8.5, 2), (13, 5), (16, 9), (16, 15)])
        stroke([(0, 15), (17, 15)])
        stroke([(6, 15), (6, 10), (8.5, 8), (11, 10), (11, 15)])
    elif name == "Asia":
        stroke([(0, 15), (6, 5), (9, 10), (12, 3), (18, 15), (0, 15)])
        canvas.dot(x + 2, y + 4, 1.4, color)
    elif name == "International":
        canvas.ellipse(x, y, x + 17, y + 17, outline=color, width=1.2)
        canvas.ellipse(x + 4.5, y, x + 12.5, y + 17, outline=color, width=1.1)
        stroke([(1, 8.5), (16, 8.5)])
    elif name == "Americas":
        stroke([(0, 12), (7, 5), (17, 12), (0, 12)])
        stroke([(2, 15), (15, 15)])
        stroke([(4, 12), (4, 17)])
        stroke([(12, 12), (12, 17)])
    elif name == "Africa":
        canvas.dot(x + 8.5, y + 8.5, 4, color)
        for start, end in [
            ((8.5, 0), (8.5, 2)), ((8.5, 15), (8.5, 17)),
            ((0, 8.5), (2, 8.5)), ((15, 8.5), (17, 8.5)),
            ((2, 2), (4, 4)), ((13, 13), (15, 15)),
            ((15, 2), (13, 4)), ((4, 13), (2, 15)),
        ]:
            stroke([start, end])
    elif name == "Oceania":
        stroke([(0, 7), (4, 4), (8, 7), (12, 4), (17, 7)])
        stroke([(0, 12), (4, 9), (8, 12), (12, 9), (17, 12)])
        stroke([(0, 17), (4, 14), (8, 17), (12, 14), (17, 17)])


def region_heading(canvas, name, x, y, width):
    color = REGIONS[name]
    canvas.line([(x, y), (x + width, y)], color, 1.15)
    canvas.rect(x, y, x + 24, y + 3, color)
    emblem(canvas, name, x + width - 20, y + 9, color)
    canvas.text(x, y + 8, name, "serif", 27, color)


def brief(canvas, story, x, y, width, show_deck=False):
    color = REGIONS[story["region"]]
    label = story["dateline"].upper()
    if story["id"] in MARKERS:
        badge(canvas, x + 7, y + 6, MARKERS[story["id"]][0], color, 6.2)
        canvas.spaced(x + 18, y - 1, label, 10.25, color, .85)
    else:
        canvas.spaced(x, y - 1, label, 10.25, color, .85)
    lines = canvas.wrapped(x, y + 11, story["headline"], "bold", 18, width, 17, 2, INK)
    if show_deck:
        canvas.wrapped(x, y + 14 + lines * 17, story["verified_summary"],
                       "sans", 14.5, width, 15, 2, MUTED)


def brief_section(canvas, stories):
    canvas.spaced(LEFT, 646, "AROUND THE WORLD", 13, RED, 2.25)
    grouped = {name: [story for story in stories.values()
                      if story["region"] == name and story["importance"] != "lead"]
               for name in REGIONS}
    for i, name in enumerate(("Europe", "Middle East", "Asia", "International")):
        x = COLUMNS[i]
        region_heading(canvas, name, x, 670, COLUMN_WIDTH)
        for row, story in enumerate(grouped[name]):
            brief(canvas, story, x, 701 + row * 44, COLUMN_WIDTH)

    region_heading(canvas, "Americas", LEFT, 837, COLUMN_WIDTH * 2 + 20)
    for index, story in enumerate(grouped["Americas"]):
        x = COLUMNS[index % 2]
        brief(canvas, story, x, 871 + (index // 2) * 57, COLUMN_WIDTH, show_deck=True)

    for x, name in zip(COLUMNS[2:], ("Africa", "Oceania")):
        region_heading(canvas, name, x, 837, COLUMN_WIDTH)
        for row, story in enumerate(grouped[name]):
            brief(canvas, story, x, 868 + row * 43, COLUMN_WIDTH)


def render():
    source = ROOT / "research" / "stories.json"
    ledger = json.loads(source.read_text(encoding="utf-8"))
    stories = {story["id"]: story for story in ledger}
    if len(stories) != len(ledger) or {story["region"] for story in ledger} != set(REGIONS):
        raise ValueError("The ledger must have unique story IDs and cover all seven regions.")
    canvas = Canvas(1024, 1024, PAPER)
    masthead(canvas)
    lead_stories(canvas, stories)
    news_atlas(canvas, stories)
    brief_section(canvas, stories)
    section_rule(canvas, 999, INK)
    canvas.spaced(LEFT, 1004, f"{len(stories)} STORIES  /  {len(REGIONS)} REGIONS", 10, MUTED, 1.45)
    canvas.text(RIGHT, 1004, "SATURDAY EDITION", "bold", 10, MUTED, "rt")
    image = canvas.image.resize((1024, 1024), Image.Resampling.LANCZOS)
    image.save(ROOT / "assets" / "edition.png", optimize=True)


if __name__ == "__main__":
    render()
