from pathlib import Path

import markdown

_cache: str | None = None

_TEMPLATE = Path("template.html").read_text()


def render() -> str:
    global _cache
    if _cache is None:
        md = Path("docs.md").read_text()
        body = markdown.markdown(md, extensions=["tables", "toc"])
        _cache = _TEMPLATE.replace("<!-- CONTENT -->", body)
    assert _cache is not None
    return _cache
