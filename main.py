import httpx
from cachetools import TTLCache
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Cache up to 200 sources (tag combos / feed names), each for 20 minutes
_cache: TTLCache = TTLCache(maxsize=200, ttl=1200)

LOBSTERS_BASE = "https://lobste.rs"
MAX_PAGES = 3


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
            response = await client.get(url, params={"page": page})
            if response.status_code != 200:
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
        raise HTTPException(status_code=502, detail=str(e))
    return {"source": source, "count": len(stories), "stories": stories[:3]}
