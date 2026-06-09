import pytest

from helpers import author_str, iso8601, rfc2822


@pytest.mark.parametrize("date_str,expected_time,expected_offset", [
    ("2026-06-08T11:29:42.000-05:00", "11:29:42", "-0500"),
    ("2026-06-08T09:00:00.000+02:00", "09:00:00", "+0200"),
    ("2026-06-08T11:29:42",           "11:29:42", "+0000"),  # naive defaults to UTC
])
def test_rfc2822(date_str, expected_time, expected_offset):
    result = rfc2822(date_str)
    assert expected_time in result
    assert expected_offset in result


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
