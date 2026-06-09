from datetime import datetime, timezone
from typing import Literal
import xml.etree.ElementTree as ET

from helpers import author_str, description, iso8601, rfc2822
from settings import CACHE_TTL_SECONDS

ATOM_NS = "http://www.w3.org/2005/Atom"
ET.register_namespace("", ATOM_NS)


def _filter_score(stories: list[dict], min_score: int | None) -> list[dict]:
    if min_score is not None:
        return [s for s in stories if s["score"] >= min_score]
    return stories


def build_rss(stories: list[dict], title: str, feed_url: str) -> bytes:
    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = title
    ET.SubElement(channel, "link").text = feed_url
    ET.SubElement(channel, "description").text = title
    ET.SubElement(channel, "pubDate").text = rfc2822(stories[0]["created_at"]) if stories else ""
    ET.SubElement(channel, "ttl").text = str(CACHE_TTL_SECONDS // 60)
    ET.SubElement(channel, "generator").text = "lobsterss"

    for story in stories:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = story["title"]
        ET.SubElement(item, "link").text = story["url"] or story["comments_url"]
        ET.SubElement(item, "guid").text = story["short_id_url"]
        ET.SubElement(item, "author").text = author_str(story)
        ET.SubElement(item, "pubDate").text = rfc2822(story["created_at"])
        ET.SubElement(item, "comments").text = story["comments_url"]
        ET.SubElement(item, "description").text = description(story)
        for tag in story.get("tags", []):
            ET.SubElement(item, "category").text = tag

    ET.indent(rss)
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(rss, encoding="unicode").encode("utf-8")


def build_atom(stories: list[dict], title: str, feed_url: str) -> bytes:
    def sub(parent, tag, text=None, **attrs):
        el = ET.SubElement(parent, f"{{{ATOM_NS}}}{tag}", attrs)
        if text is not None:
            el.text = text
        return el

    feed_el = ET.Element(f"{{{ATOM_NS}}}feed")
    sub(feed_el, "title", title)
    sub(feed_el, "id", feed_url)
    link_el = sub(feed_el, "link")
    link_el.set("href", feed_url)
    link_el.set("rel", "self")
    updated = stories[0]["created_at"] if stories else datetime.now(timezone.utc).isoformat()
    sub(feed_el, "updated", iso8601(updated))
    sub(feed_el, "generator", "lobsterss")

    for story in stories:
        entry = sub(feed_el, "entry")
        sub(entry, "title", story["title"])
        story_link = sub(entry, "link")
        story_link.set("href", story["url"] or story["comments_url"])
        sub(entry, "id", story["short_id_url"])
        sub(entry, "published", iso8601(story["created_at"]))
        sub(entry, "updated", iso8601(story["created_at"]))
        author_el = sub(entry, "author")
        sub(author_el, "name", story["submitter_user"])
        sub(entry, "summary", description(story))
        for tag in story.get("tags", []):
            sub(entry, "category", term=tag)

    ET.indent(feed_el)
    return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(feed_el, encoding="unicode").encode("utf-8")


def build_feed(
    stories: list[dict],
    title: str,
    feed_url: str,
    fmt: Literal["rss", "atom"],
    min_score: int | None,
) -> bytes:
    stories = _filter_score(stories, min_score)
    stories = sorted(stories, key=lambda s: s["created_at"], reverse=True)

    if fmt == "rss":
        return build_rss(stories, title, feed_url)
    return build_atom(stories, title, feed_url)
