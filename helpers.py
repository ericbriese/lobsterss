from datetime import datetime, timezone
from urllib.parse import urlparse


def parse_dt(date_str: str) -> datetime:
    dt = datetime.fromisoformat(date_str)
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def rfc2822(date_str: str) -> str:
    return parse_dt(date_str).strftime("%a, %d %b %Y %H:%M:%S %z")


def iso8601(date_str: str) -> str:
    return parse_dt(date_str).isoformat()


def author_str(story: dict) -> str:
    url = story.get("url") or ""
    if url and story.get("user_is_author"):
        return f"{urlparse(url).netloc} by {story['submitter_user']}"
    return story["submitter_user"]


def description(story: dict) -> str:
    return (
        f'Score: {story["score"]} | '
        f'Comments: {story["comment_count"]} | '
        f'<a href="{story["comments_url"]}">Comments</a>'
    )
