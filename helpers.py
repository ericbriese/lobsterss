import re
from datetime import datetime, timezone
from urllib.parse import urlparse

from settings import MAX_SEARCH_TERMS


def parse_dt(date_str: str) -> datetime:
    dt = datetime.fromisoformat(date_str)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def rfc2822(date_str: str) -> str:
    return parse_dt(date_str).strftime("%a, %d %b %Y %H:%M:%S %z")


def iso8601(date_str: str) -> str:
    return parse_dt(date_str).isoformat()


def author_str(story: dict) -> str:
    if story.get("user_is_author"):
        domain = urlparse(story["url"]).netloc if story.get("url") else ""
        return f"{domain} by {story['submitter_user']}"
    return story["submitter_user"]


def _term_matches(term: str, title: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(term) + r"(?!\w)"
    return bool(re.search(pattern, title, re.IGNORECASE))


def matches_query(title: str, q: str) -> bool:
    """
    Case-insensitive whole-keyword title search. Supports OR and AND operators:
      q=git OR linux   → title contains "git" or "linux" as whole keywords
      q=git AND linux  → title contains both "git" and "linux" as whole keywords
    Terms are capped at MAX_SEARCH_TERMS.
    """
    if " OR " in q:
        terms = q.split(" OR ")[:MAX_SEARCH_TERMS]
        return any(_term_matches(t, title) for t in terms)
    if " AND " in q:
        terms = q.split(" AND ")[:MAX_SEARCH_TERMS]
        return all(_term_matches(t, title) for t in terms)
    return _term_matches(q, title)


def description(story: dict) -> str:
    parts = []
    if story.get("description"):
        parts.append(story["description"])
    parts.append(
        f'Score: {story["score"]} | '
        f'Comments: {story["comment_count"]} | '
        f'<a href="{story["comments_url"]}">Comments</a>'
    )
    return "\n".join(parts)
