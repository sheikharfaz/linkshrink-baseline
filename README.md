# linkshrink-baseline

A small URL-shortener API — `POST /links`, `GET /{code}` (redirect),
`GET /links/{code}/stats`, rate limiting on shortening, URL validation and
dedup. FastAPI + SQLite, no ORM.

This is one half of a controlled comparison: the same spec, built the same
number of feature sessions, once **without** any memory/planning tooling
(this repo) and once **with** [agent-memory-kit](https://github.com/sheikharfaz/agent-memory-kit)
(the companion repo, [linkshrink-agent-memory-kit](https://github.com/sheikharfaz/linkshrink-agent-memory-kit)).
Every session in both repos was pushed as its own commit, so the git
history itself is part of the evidence. See
[SESSION_LOG.md](SESSION_LOG.md) for what got read/rebuilt at the start of
each session here, and the comparison repo's `COMPARISON.md` for the full
numbers once both are complete.

## Run it

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```bash
curl -X POST localhost:8000/links -H 'content-type: application/json' \
  -d '{"url": "https://example.com"}'
# {"code": "aB3dE7x", "short_url": "/aB3dE7x"}

curl -i localhost:8000/aB3dE7x            # 307 redirect
curl localhost:8000/links/aB3dE7x/stats   # click_count, last_clicked_at
```

## Test

```bash
python3 -m pytest tests/ -v
```

## Endpoints

| Method | Path | Notes |
|---|---|---|
| POST | `/links` | Rate-limited 5/minute per IP. Shortening the same URL twice returns the same code. |
| GET | `/{code}` | 307 redirect; records a click. |
| GET | `/links/{code}/stats` | click_count, created_at, last_clicked_at. |

## What was deliberately *not* done here

No PRD or design doc per feature — just the request, then code. No index of
the codebase — every session that touched existing code re-read the
relevant files in full first (logged in `SESSION_LOG.md`). No proposal/
approval step before adding the `slowapi` dependency in Session 3 — it was
just added. No closing recap after any session. This is the point: it's
what "just build it" looks like without deliberate process, for comparison
against the companion repo that has all of the above.
