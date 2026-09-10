from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app import storage
from app.shortcode import generate_code


@asynccontextmanager
async def lifespan(app: FastAPI):
    storage.init_db()
    yield


app = FastAPI(title="LinkShrink", lifespan=lifespan)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


class ShortenRequest(BaseModel):
    url: HttpUrl


class ShortenResponse(BaseModel):
    code: str
    short_url: str


class StatsResponse(BaseModel):
    code: str
    url: str
    click_count: int
    created_at: str
    last_clicked_at: str | None = None


@app.post("/links", response_model=ShortenResponse)
@limiter.limit("5/minute")
def shorten(request: Request, req: ShortenRequest):
    url = str(req.url)
    existing = storage.get_link_by_url(url)
    if existing:
        return ShortenResponse(code=existing["code"], short_url=f"/{existing['code']}")

    code = generate_code()
    while storage.get_link(code):
        code = generate_code()
    storage.insert_link(code, url, datetime.now(timezone.utc).isoformat())
    return ShortenResponse(code=code, short_url=f"/{code}")


@app.get("/links/{code}/stats", response_model=StatsResponse)
def stats(code: str):
    link = storage.get_link(code)
    if not link:
        raise HTTPException(status_code=404, detail="short code not found")
    return StatsResponse(**link)


@app.get("/{code}")
def redirect(code: str):
    link = storage.get_link(code)
    if not link:
        raise HTTPException(status_code=404, detail="short code not found")
    storage.record_click(code, datetime.now(timezone.utc).isoformat())
    return RedirectResponse(url=link["url"], status_code=307)
