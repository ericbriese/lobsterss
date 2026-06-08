import logging

import httpx
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException

from settings import CACHE_MAX_SIZE, CACHE_TTL_SECONDS, LOBSTERS_BASE, MAX_PAGES

logger = logging.getLogger(__name__)

app = FastAPI()

_cache: TTLCache = TTLCache(maxsize=CACHE_MAX_SIZE, ttl=CACHE_TTL_SECONDS)


async def fetch_stories(source: str) -> list[dict]:
    """
    Fetch up to MAX_PAGES pages of stories from lobste.rs for the given source.

    source examples:
      "newest"         → /newest.json
      "hottest"        → /hottest.json
      "t/rust,python"  → /t/rust,python.json  (OR semantics: rust or python)
    """
    if source in _cache:
        return _cache[source]

    stories = []
    async with httpx.AsyncClient() as client:
        for page in range(1, MAX_PAGES + 1):
            url = f"{LOBSTERS_BASE}/{source}.json"
            try:
                response = await client.get(url, params={"page": page})
            except httpx.RequestError as e:
                logger.error("Request to lobste.rs failed (source=%s, page=%d): %s", source, page, e)
                break
            if response.status_code != 200:
                logger.warning(
                    "lobste.rs returned %d for source=%s page=%d",
                    response.status_code, source, page,
                )
                break
            page_stories = response.json()
            if not page_stories:
                break
            stories.extend(page_stories)

    _cache[source] = stories
    return stories


@app.get("/healthz")
async def health():
    return {"status": "ok"}


@app.get("/debug/{source:path}")
async def debug(source: str):
    """Temporary endpoint to inspect raw lobste.rs data."""
    try:
        stories = await fetch_stories(source)
    except Exception as e:
        logger.exception("Unhandled error fetching source=%s", source)
        raise HTTPException(status_code=502, detail=str(e))
    return {"source": source, "count": len(stories), "stories": stories[:3]}