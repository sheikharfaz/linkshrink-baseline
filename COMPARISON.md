# Comparison: linkshrink-baseline vs. linkshrink-agent-memory-kit

Same spec. Same 4 feature sessions, in the same order. Same final
application code — `diff` between the two repos' `app/` directories
returns nothing. The only thing that differs is the process: one repo,
[linkshrink-baseline](https://github.com/sheikharfaz/linkshrink-baseline),
was built with no memory/planning tooling between sessions; the other,
[linkshrink-agent-memory-kit](https://github.com/sheikharfaz/linkshrink-agent-memory-kit),
with [agent-memory-kit](https://github.com/sheikharfaz/agent-memory-kit)
installed. Every session in both is its own commit — the git history is
part of the evidence, not just this document. (This file is identical in
both repos, on purpose — read it from whichever one you found first.)

## TL;DR

| | linkshrink-baseline | linkshrink-agent-memory-kit |
|---|---|---|
| Context tokens, Sessions 2–4 | **≈1,993** | **≈4,004** |
| How that context was recovered | full-file re-reads each session | map + targeted queries + session recall |
| New dependency (`slowapi`) | pip-installed directly, no record of why | proposed → approved → installed → logged to an audit ledger |
| PRD/TRD per feature | none | 4 (one pair per session, in `.agent/work/`) |
| Closing recap per session | none | 4 (kept local — see agent-memory-kit's privacy stance) |
| Cross-session continuity | re-derived from scratch each time | `session-memory` recall (real output logged per session) |
| Final tests | 9 passing | 9 passing |
| Final application code | 140 lines | 140 lines, byte-for-byte identical |
| Real bugs found in the tooling itself | — | 1 (fixed upstream during Session 2) |

**Read the token row correctly: the kit used *more* tokens here, not
fewer.** That is the honest result at this project's scale (4–5 source
files), explained below — and it is not the result you'd get on a real
codebase; see [Why the token result flips at scale](#why-the-token-result-flips-at-scale).

## Methodology

Both repos implement the identical 4-feature spec (see either repo's
`SESSION_LOG.md` for the PRD-level detail): core shorten+redirect, click
analytics, rate limiting (needs a new dependency), then validation/dedup.
Each feature was built as if it were a **separate session with no memory
of the previous one** — no notes carried forward by the person driving it,
only whatever each repo's own tooling could recover.

- **linkshrink-baseline**: context was recovered by reading the relevant
  existing files in full via a plain file-read tool, the same way an
  agent without any indexing does it today. Every file read is logged
  with its real character count in
  [linkshrink-baseline/SESSION_LOG.md](https://github.com/sheikharfaz/linkshrink-baseline/blob/main/SESSION_LOG.md).
- **linkshrink-agent-memory-kit**: context was recovered via
  `codebase-memory` (`CODEBASE_MAP.md`, read once per session, plus
  targeted `query.py file`/`query.py impact` calls instead of whole-file
  reads) and `session-memory` (`memory.py recall`/`recent`, using the
  actual local log left by the previous sessions' `dev-recap` entries).
  Every command and its real output size is logged in
  [linkshrink-agent-memory-kit/SESSION_LOG.md](https://github.com/sheikharfaz/linkshrink-agent-memory-kit/blob/main/SESSION_LOG.md).

Token counts use the chars/4 heuristic — the same approximation
`agent-memory-kit`'s own benchmark suite uses, and the one its `AGENTS.md`
uses for its own budget checks. Both repos are measured the same way, so
the comparison between them is meaningful regardless of the heuristic's
absolute accuracy.

**What this measures:** the cost of *recovering context at the start of a
session* — reading a map/querying vs. reading whole files fresh, or
recalling a prior session's notes vs. having none. **What this does not
measure:** the tokens spent actually reasoning about or writing the new
code each session, which both repos pay equally, or answer quality —
that's a different, harder question this comparison doesn't attempt.

## Why the token result flips at scale

`CODEBASE_MAP.md` is read once per session and costs ≈1,100–1,200 tokens
here regardless of which 1–3 files that session actually needs — a fixed
cost that has to amortize over the size of the codebase it's summarizing.
At 4–5 source files, summarizing "everything" isn't much cheaper than
reading "the 1–2 files that matter," so the fixed cost can exceed the
direct-read cost. That's exactly what happened in Sessions 2–4 here.

`agent-memory-kit`'s own benchmark suite
([`benchmarks/`](https://github.com/sheikharfaz/agent-memory-kit/tree/main/benchmarks))
runs the identical kind of comparison against two real, much larger
public repositories, using a similar naive-baseline methodology:

| Repo | Naive tokens | Kit-assisted tokens | Ratio |
|---|---|---|---|
| `psf/requests` (37 parsed files) | 85,220 | 1,939 | 44.0x fewer |
| `django/django` (2,979 parsed files) | 167,437 | 4,706 | 35.6x fewer |

Read together: the map's fixed cost stops being a discount and starts
being a tax somewhere between "5 files" and "37 files." Both LinkShrink
repos were deliberately kept small and simple as a POC — which is exactly
what makes them a fair, honest complement to the large-repo benchmark
rather than a redundant one. A demo that only ever showed favorable
numbers would be a worse piece of evidence than this one.

## What doesn't show up in the token count

- **An audit trail for the new dependency.** `slowapi` isn't in
  `agent-memory-kit`'s shipped registry, so Session 3 added a
  project-local entry, ran `toolkit.py plan` (prints the exact
  install/uninstall commands and a risk note, runs nothing), got
  approved, then `toolkit.py install` — logged to
  `linkshrink-agent-memory-kit/.agent/memory/tools/tool-ledger.jsonl` with
  a timestamp and session id. `linkshrink-baseline`'s Session 3 just added
  it to `requirements.txt` and ran pip install — nothing records *why* or
  *that it was approved*, beyond a commit message written after the fact.
- **Written intent, not just written code.**
  `linkshrink-agent-memory-kit/.agent/work/` has a `PRD.md` (problem,
  acceptance criteria, non-goals) and `TRD.md` (approach, alternatives
  considered, testing strategy, blast radius) for every one of the 4
  sessions. `linkshrink-baseline` has none of that — the request and the
  diff are the only record of intent.
- **A real bug in the tooling itself, found and fixed mid-build.**
  `dev-recap`'s `gaps` scanner was checking the wrong JSON field name
  against `codebase-memory`'s index and always reported indexed files as
  unindexed. Building `linkshrink-agent-memory-kit` for real (not a
  scripted demo) surfaced it in Session 2; it's fixed upstream in
  `agent-memory-kit`, with 3 new regression tests, and the fix is already
  reflected in that repo's copy of the script from Session 2 onward. This
  is arguably the most valuable thing this whole exercise produced — a
  real defect in a tool that had already shipped, found by actually using
  it on a real (if small) project instead of only ever running it against
  itself.

## What this comparison does not prove

Not that `agent-memory-kit` makes every project cheaper — Session 2–4's
own numbers say otherwise at this scale. Not that the resulting code is
better — it's identical in both repos by construction, since that wasn't
the variable under test. Not a claim about answer quality, bug rate, or
development speed — none of those were measured. What it does show,
plainly, with real commands and real output committed alongside the
claims: what `linkshrink-agent-memory-kit`'s process produces that
`linkshrink-baseline`'s doesn't (a PRD/TRD trail, a tool-install audit
log, cross-session recall that survived closing the session), and an
honest accounting of what that process costs in tokens, including the
case where it costs more.

## See also

- [linkshrink-baseline](https://github.com/sheikharfaz/linkshrink-baseline) — the baseline half of this comparison, with its own `SESSION_LOG.md`
- [linkshrink-agent-memory-kit](https://github.com/sheikharfaz/linkshrink-agent-memory-kit) — the kit-assisted half, with its own `SESSION_LOG.md`
- [agent-memory-kit](https://github.com/sheikharfaz/agent-memory-kit) — the kit itself
- [agent-memory-kit/benchmarks](https://github.com/sheikharfaz/agent-memory-kit/tree/main/benchmarks) — the large-repo token comparison referenced above
