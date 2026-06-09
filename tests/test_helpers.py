import pytest

from helpers import author_str, iso8601, matches_query, rfc2822


@pytest.mark.parametrize("date_str,expected_time,expected_offset", [
    ("2026-06-08T11:29:42.000-05:00", "11:29:42", "-0500"),
    ("2026-06-08T09:00:00.000+02:00", "09:00:00", "+0200"),
    ("2026-06-08T11:29:42",           "11:29:42", "+0000"),  # naive defaults to UTC
])
def test_rfc2822(date_str, expected_time, expected_offset):
    result = rfc2822(date_str)
    assert expected_time in result
    assert expected_offset in result


@pytest.mark.parametrize("title,q,expected", [
    # single term
    ("Git internals explained",   "git",             True),
    ("Git internals explained",   "linux",           False),
    # case insensitive
    ("Git internals explained",   "GIT",             True),
    # OR
    ("Git internals explained",   "git OR linux",    True),
    ("Git internals explained",   "python OR linux", False),
    # AND
    ("Git and Linux together",    "git AND linux",   True),
    ("Git internals explained",   "git AND linux",   False),
    # whole-keyword: must not match substrings
    ("Painting with acrylics",    "AI",              False),
    ("AI safety research",        "AI",              True),
    # symbols
    ("C++ is still relevant",     "C++",             True),
    ("Painting with acrylics",    "C++",             False),
])
def test_matches_query(title, q, expected):
    assert matches_query(title, q) == expected


def test_matches_query_term_limit(monkeypatch):
    import helpers
    monkeypatch.setattr(helpers, "MAX_SEARCH_TERMS", 2)
    # third term "linux" would match but is truncated
    assert not matches_query("Linux kernel news", "python OR rust OR linux")


def test_iso8601_preserves_offset():
    result = iso8601("2026-06-08T11:29:42.000-05:00")
    assert "11:29:42" in result
    assert "-05:00" in result


@pytest.mark.parametrize("url,user_is_author,expected", [
    ("https://example.com/article", True,  "example.com by alice"),
    ("https://example.com/article", False, "alice"),
    ("",                            True,  " by alice"),
    (None,                          False, "alice"),
])
def test_author_str(url, user_is_author, expected):
    story = {"url": url, "submitter_user": "alice", "user_is_author": user_is_author}
    assert author_str(story) == expected
