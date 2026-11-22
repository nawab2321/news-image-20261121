"""Compose the 21 November front page from the audited story ledger."""

import json

from PIL import Image

from cartography import POINTS, atlas, badge
from graphics import (
    COPPER, FOREST, INK, MUTED, PAPER, RED, ROOT, RULE, TEAL, Canvas,
)
from illustrations import climate_scene, hormuz_scene, ukraine_scene

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
    badge(canvas, x + 8, y + 9, POINTS[story["id"]][0], color)
    label = f'{story["category"]}  /  {story["location"]}'.upper()
    canvas.spaced(x + 22, y, label, 12.5, color, 1.06)


def lead_stories(canvas, stories):
    lead = stories["cop31"]
    lead_tag(canvas, LEFT, 139, lead)
    canvas.put(climate_scene(568, 161), LEFT, 163)
    canvas.fit(LEFT, 331, lead["headline"], "serif", 57, 569, min_size=49)
    canvas.wrapped(LEFT + 2, 389, lead["verified_summary"], "sans", 20, 556, 23, 2)

    left = 632
    canvas.line([(617, 141), (617, 425)], RULE)
    for story_id, top, illustration in [
        ("kryvyi-rih", 139, ukraine_scene), ("hormuz", 282, hormuz_scene),
    ]:
        item = stories[story_id]
        lead_tag(canvas, left, top, item)
        canvas.put(illustration(), RIGHT - 110, top + 21)
        headline = canvas.wrap_lines(item["headline"], "serif", 32, 235, 2)
        canvas.draw_lines(left, top + 22, headline, "serif", 32, 30, INK)
        deck_y = top + 26 + 30 * len(headline)
        canvas.wrapped(left + 1, deck_y, item["verified_summary"], "sans", 16, 233, 17, 3)
        canvas.text(RIGHT, top + 132, item["source_slug"], "bold", 8.5, MUTED, "rt")
    canvas.line([(left, 279), (RIGHT, 279)], RULE)


def news_atlas(canvas, stories):
    section_rule(canvas, 438, INK)
    canvas.spaced(LEFT, 447, "THE DAY ON THE MAP", 13, FOREST, 2.0)
    canvas.spaced(819, 447, "THE DAY IN NUMBERS", 13, FOREST, 1.5)
    canvas.put(atlas(stories, REGIONS), LEFT, 473)

    for position, story_id in enumerate(POINTS):
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


DESK_ICONS = {
    "Europe": [[(1, 2), (17, 2), (16, 11), (9, 17), (2, 11), (1, 2)],
               [(5, 9), (8, 12), (13, 6)]],
    "Middle East": [[(1, 16), (1, 9), (9, 2), (17, 9), (17, 16), (1, 16)],
                    [(6, 16), (6, 10), (12, 10), (12, 16)]],
    "Asia": [[(1, 15), (7, 5), (10, 9), (13, 3), (18, 15), (1, 15)]],
    "International": [[(1, 9), (17, 9)], [(9, 1), (9, 17)]],
    "Americas": [[(1, 10), (5, 6), (13, 6), (17, 10), (1, 10)],
                 [(4, 10), (4, 17)], [(14, 10), (14, 17)], [(1, 17), (17, 17)]],
    "Africa": [[(1, 9), (4, 9)], [(14, 9), (17, 9)], [(9, 1), (9, 4)], [(9, 14), (9, 17)]],
    "Oceania": [[(1, 6), (5, 3), (9, 6), (13, 3), (17, 6)],
                [(1, 11), (5, 8), (9, 11), (13, 8), (17, 11)],
                [(1, 16), (5, 13), (9, 16), (13, 13), (17, 16)]],
}


def region_heading(canvas, name, left, top, width):
    color = REGIONS[name]
    end = left + width
    canvas.line([(left, top), (end, top)], color, 1.15)
    canvas.rect(left, top, left + 23, top + 3, color)
    canvas.text(left, top + 7, name, "serif", 27, color)
    x, y = end - 20, top + 9
    for component in DESK_ICONS[name]:
        canvas.line([(x + dx, y + dy) for dx, dy in component], color, 1.25)
    if name == "Africa":
        canvas.dot(x + 9, y + 9, 4, color)
    if name == "International":
        canvas.ellipse(x + 1, y + 1, x + 17, y + 17, outline=color, width=1.2)


def story_type(canvas, story, width, with_deck):
    headline = canvas.wrap_lines(story["headline"], "bold", 18, width, 2)
    deck = []
    if with_deck:
        deck = canvas.wrap_lines(story["verified_summary"], "sans", 14, width, 2)
    height = 10 + len(headline) * 16 + len(deck) * 15 + (3 if deck else 0)
    return headline, deck, height


def draw_brief(canvas, story, left, top, headline, deck):
    color = REGIONS[story["region"]]
    indent = 0
    if story["id"] in POINTS:
        badge(canvas, left + 7, top + 5.5, POINTS[story["id"]][0], color, 5.9)
        indent = 17
    canvas.spaced(left + indent, top - 1, story["dateline"].upper(), 10.25, color, .85)
    canvas.draw_lines(left, top + 10, headline, "bold", 18, 16, INK)
    canvas.draw_lines(left, top + 13 + len(headline) * 16, deck, "sans", 14, 15, MUTED)


def column(canvas, stories, left, start, end, width, with_decks=False):
    metrics = [story_type(canvas, story, width, with_decks) for story in stories]
    free_space = end - start - sum(height for _, _, height in metrics)
    gaps = len(stories) - 1
    gap = free_space / gaps if gaps else 0
    if free_space < 0 or (gaps > 0 and gap < 2):
        raise ValueError(f"Stories in the column starting at {left}, {start} exceed their space")
    top = start
    for index, (story, (headline, deck, height)) in enumerate(zip(stories, metrics)):
        draw_brief(canvas, story, left, top, headline, deck)
        if index < gaps and gap >= 6:
            y = top + height + gap / 2 - 1
            canvas.line([(left, y), (left + width, y)], "#d5cfc0", .65)
        top += height + gap


def brief_section(canvas, stories):
    canvas.spaced(LEFT, 645, "AROUND THE WORLD", 13, RED, 2.25)
    editions = {region: [] for region in REGIONS}
    for story in stories.values():
        if story["importance"] != "lead":
            editions[story["region"]].append(story)

    desks = ("Europe", "Middle East", "Asia", "International")
    for region, left in zip(desks, COLUMNS, strict=True):
        region_heading(canvas, region, left, 667, COLUMN_WIDTH)
        column(canvas, editions[region], left, 699, 831, COLUMN_WIDTH)

    region_heading(canvas, "Americas", LEFT, 835, 2 * COLUMN_WIDTH + 20)
    for index, left in enumerate(COLUMNS[:2]):
        column(canvas, editions["Americas"][index::2], left, 869, 994, COLUMN_WIDTH, True)
    for region, left in zip(("Africa", "Oceania"), COLUMNS[2:], strict=True):
        region_heading(canvas, region, left, 835, COLUMN_WIDTH)
        column(canvas, editions[region], left, 867, 997, COLUMN_WIDTH)


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
