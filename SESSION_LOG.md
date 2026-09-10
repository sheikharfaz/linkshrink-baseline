# Session log — linkshrink-baseline

This repo is one half of a controlled comparison. It was built across four
separate feature requests, treated as if each were a **new AI session with
no memory of the previous ones** — no notes carried forward, no index of
the existing code, nothing but the files on disk. At the start of each
session after the first, context was rebuilt by actually reading the
existing files fresh (via the `Read` tool), the same way an unaided agent
would, and every file read that way is logged below with its real size.

The companion repo, [linkshrink-agent-memory-kit](https://github.com/sheikharfaz/linkshrink-agent-memory-kit),
implements the identical spec using [agent-memory-kit](https://github.com/sheikharfaz/agent-memory-kit).
See [COMPARISON.md](COMPARISON.md) (once both are done) for the full
numbers. Token counts here use the chars/4 heuristic — the same one
`agent-memory-kit`'s own benchmark suite uses, for comparability.

---

## Session 1 — Core: shorten + redirect

**Simulated as:** the first session, repo is empty — there is nothing to
re-read yet, so this session has no "lost context" cost either way. The
comparison's real signal starts in Session 2, once there's existing code
to understand.

**Built:** `app/storage.py` (SQLite layer), `app/shortcode.py` (random code
generator), `app/main.py` (FastAPI app: `POST /links`, `GET /{code}`),
`tests/test_core.py`.

**Context read this session:** none — nothing existed yet.

**Verification:** `python3 -m pytest tests/ -v` → 2 passed.

| File | Lines |
|---|---|
| app/storage.py | 41 |
| app/shortcode.py | 8 |
| app/main.py | 44 |
| tests/test_core.py | 29 |

---

## Session 2 — Click analytics

**Simulated as:** a new session with no memory of Session 1. To understand
the existing schema and API shape before changing anything, the full
content of every file that mattered was read fresh, the way an agent
without an index has to.

**Context read this session** (full file reads, no map, no query CLI):

| File read in full | Chars | ≈ Tokens (chars/4) |
|---|---|---|
| app/storage.py | 1,027 | 257 |
| app/main.py | 1,104 | 276 |
| tests/test_core.py | 803 | 201 |
| **Total** | **2,934** | **≈ 734** |

**Built:** added `click_count`/`last_clicked_at` columns and
`record_click()` to `app/storage.py`; added `GET /links/{code}/stats` and
wired click recording into the redirect handler in `app/main.py`;
`tests/test_stats.py` (3 new tests).

**Verification:** `python3 -m pytest tests/ -v` → 5 passed.

| File (after this session) | Lines |
|---|---|
| app/storage.py | 52 |
| app/main.py | 61 |
| tests/test_stats.py | 43 |

---

## Session 3 — Rate limiting

**Simulated as:** a new session, no memory of Sessions 1–2. Re-read
`app/main.py` in full to see the current route shape before adding a
limiter to the right endpoint.

**Context read this session:**

| File read in full | Chars | ≈ Tokens |
|---|---|---|
| app/main.py | 1,562 | 391 |

**New dependency decision:** chose `slowapi` and added it straight to
`requirements.txt` + ran `pip install slowapi` — no proposal, no approval
step, no record of why it was chosen or what else was considered. That
decision and its rationale exist only in this commit message and this log
entry, written after the fact.

**Built:** `Limiter` wired into `app/main.py`, `@limiter.limit("5/minute")`
on `POST /links`; `tests/test_rate_limit.py` (2 new tests).

**Verification:** `python3 -m pytest tests/ -v` → 7 passed.

| File (after this session) | Lines |
|---|---|
| app/main.py | 69 |
| tests/test_rate_limit.py | 28 |
