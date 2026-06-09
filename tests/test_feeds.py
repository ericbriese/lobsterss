import xml.etree.ElementTree as ET

import pytest

from feeds import build_feed

ATOM_NS = {"a": "http://www.w3.org/2005/Atom"}


def make_story(**kwargs):
    defaults = {
        "short_id_url": "https://lobste.rs/s/abc123",
        "title": "Test Story",
        "url": "https://example.com/article",
        "score": 10,
        "comment_count": 5,
        "created_at": "2026-06-08T12:00:00.000-05:00",
        "submitter_user": "testuser",
        "user_is_author": False,
        "comments_url": "https://lobste.rs/s/abc123/test_story",
        "tags": ["python"],
    }
    return {**defaults, **kwargs}


OLDER = make_story(title="Older Story", created_at="2026-06-01T10:00:00.000-05:00", score=5)
NEWER = make_story(title="Newer Story", created_at="2026-06-08T10:00:00.000-05:00", score=15)
HIGH_SCORE = make_story(title="High Score", score=50, created_at="2026-05-30T10:00:00.000-05:00")
LOW_SCORE = make_story(title="Low Score", score=2, created_at="2026-05-29T10:00:00.000-05:00")


def items(tree, fmt):
    if fmt == "rss":
        return tree.findall(".//item")
    return tree.findall("a:entry", ATOM_NS)


def item_titles(tree, fmt):
    if fmt == "rss":
        return [i.find("title").text for i in tree.findall(".//item")]
    return [e.find("a:title", ATOM_NS).text for e in tree.findall("a:entry", ATOM_NS)]


@pytest.mark.parametrize("fmt", ["rss", "atom"])
def test_returns_valid_xml(fmt):
    result = build_feed([NEWER, OLDER], "Test Feed", "https://example.com", fmt, None)
    ET.fromstring(result)  # raises on invalid XML


@pytest.mark.parametrize("fmt", ["rss", "atom"])
def test_newest_first(fmt):
    tree = ET.fromstring(build_feed([OLDER, NEWER], "Test Feed", "https://example.com", fmt, None))
    assert item_titles(tree, fmt) == ["Newer Story", "Older Story"]


@pytest.mark.parametrize("fmt", ["rss", "atom"])
def test_min_score_excludes_low_scores(fmt):
    tree = ET.fromstring(build_feed([HIGH_SCORE, LOW_SCORE], "Test Feed", "https://example.com", fmt, 10))
    assert len(items(tree, fmt)) == 1


@pytest.mark.parametrize("fmt", ["rss", "atom"])
def test_no_min_score_includes_all(fmt):
    tree = ET.fromstring(build_feed([HIGH_SCORE, LOW_SCORE, NEWER, OLDER], "Test Feed", "https://example.com", fmt, None))
    assert len(items(tree, fmt)) == 4


@pytest.mark.parametrize("fmt", ["rss", "atom"])
def test_empty_stories_returns_valid_xml(fmt):
    result = build_feed([], "Test Feed", "https://example.com", fmt, None)
    ET.fromstring(result)


def test_rss_has_comments_element():
    tree = ET.fromstring(build_feed([NEWER], "Test Feed", "https://example.com", "rss", None))
    assert tree.find(".//item/comments") is not None


def test_rss_pubdate_preserves_timezone():
    tree = ET.fromstring(build_feed([NEWER], "Test Feed", "https://example.com", "rss", None))
    pubdate = tree.find(".//item/pubDate").text
    assert "10:00:00" in pubdate
    assert "-0500" in pubdate


def test_rss_channel_has_generator():
    tree = ET.fromstring(build_feed([NEWER], "Test Feed", "https://example.com", "rss", None))
    assert tree.find("channel/generator").text == "lobsterss"


def test_rss_channel_has_ttl():
    tree = ET.fromstring(build_feed([NEWER], "Test Feed", "https://example.com", "rss", None))
    assert tree.find("channel/ttl") is not None


def test_rss_channel_pubdate_is_newest_story():
    tree = ET.fromstring(build_feed([OLDER, NEWER], "Test Feed", "https://example.com", "rss", None))
    channel_pubdate = tree.find("channel/pubDate").text
    assert "08 Jun 2026" in channel_pubdate


@pytest.mark.parametrize("url,user_is_author,expected_author", [
    ("https://example.com/article", True,  "example.com by testuser"),
    ("https://example.com/article", False, "testuser"),
    ("",                            True,  " by testuser"),
    ("",                            False, "testuser"),
])
def test_rss_author(url, user_is_author, expected_author):
    story = make_story(url=url, user_is_author=user_is_author)
    tree = ET.fromstring(build_feed([story], "Test Feed", "https://example.com", "rss", None))
    assert tree.find(".//item/author").text == expected_author


@pytest.mark.parametrize("url,expected_link", [
    ("https://example.com/article", "https://example.com/article"),
    ("",                            "https://lobste.rs/s/abc123/test_story"),  # falls back to comments_url
])
def test_rss_item_link(url, expected_link):
    story = make_story(url=url)
    tree = ET.fromstring(build_feed([story], "Test Feed", "https://example.com", "rss", None))
    assert tree.find(".//item/link").text == expected_link


@pytest.mark.parametrize("url,description_text,expect_in_output", [
    ("",                            "<p>Text post content.</p>",   True),   # text post with description
    ("https://example.com/article", "<p>Link post discussion.</p>", True),  # link post with description
    ("https://example.com/article", "",                             False),  # link post, no description
])
def test_rss_description_story_text(url, description_text, expect_in_output):
    story = make_story(url=url, description=description_text)
    tree = ET.fromstring(build_feed([story], "Test Feed", "https://example.com", "rss", None))
    desc = tree.find(".//item/description").text
    if expect_in_output:
        assert description_text in desc
    else:
        assert "<p>" not in desc


def test_atom_has_generator():
    tree = ET.fromstring(build_feed([NEWER], "Test Feed", "https://example.com", "atom", None))
    assert tree.find("a:generator", ATOM_NS).text == "lobsterss"
