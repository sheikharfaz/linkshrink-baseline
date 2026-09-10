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
