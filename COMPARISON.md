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

| | linkshrink-baseline | kit, as first measured | kit, round 1 fix | kit, round 2 fix |
|---|---|---|---|---|
| Context tokens, Sessions 2–4 | **≈1,993** | ≈4,004 | ≈1,676 | **≈1,430** |
| How that context was recovered | full-file re-reads each session | map + targeted queries + session recall | same, leaner map | same, leaner map + queries |
| New dependency (`slowapi`) | pip-installed directly, no record of why | proposed → approved → installed → logged to an audit ledger | — same — | — same — |
| PRD/TRD per feature | none | 4 (one pair per session, in `.agent/work/`) | — same — | — same — |
| Closing recap per session | none | 4 (kept local — see agent-memory-kit's privacy stance) | — same — | — same — |
| Cross-session continuity | re-derived from scratch each time | `session-memory` recall (real output logged per session) | — same — | — same — |
| Final tests | 9 passing | 9 passing | 9 passing | 9 passing |
| Final application code | 140 lines | 140 lines, byte-for-byte identical | — same — | — same — |
| Real bugs found in the tooling | — | 1 (`dev-recap`'s `gaps`) | +1 (map-bloat root cause) | — |

**As first measured, the kit used *more* tokens here, not fewer** —
≈4,004 vs. baseline's ≈1,993. Two real rounds of upstream fixes later,
it's ≈1,430 — **28% below baseline**, not the roughly 2x-worse result
this document originally led with, and also honestly not below *half* of
it. All three numbers are kept here on purpose — see
[Update — the upstream fix](#update--the-upstream-fix) and
[Update 2 — pushed below half, hit a real ceiling](#update-2--pushed-below-half-hit-a-real-ceiling)
for what changed each round, and
[Why the token result flips at scale](#why-the-token-result-flips-at-scale)
for the parts of the explanation that were true from the start.

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

## Update — the upstream fix

The ≈4,004-token result above wasn't the full explanation it looked like.
Investigating it turned up a real, fixable defect: `CODEBASE_MAP.md` was
including `.agent/skills/` — this kit's own *vendored* scripts, copied
into every consumer repo by its installer — as if they were
`linkshrink-agent-memory-kit`'s own source. 93% of the LOC that map was
summarizing was kit-internal code, not this repo's actual app.

Fixed upstream in
[`agent-memory-kit@55f7b3f`](https://github.com/sheikharfaz/agent-memory-kit/commit/55f7b3f):
`.agent/skills/` excluded from indexing by default (an `.agentignore`
`!pattern` negation opts it back in — the one real case is
`agent-memory-kit`'s own repo, where it genuinely is the source), plus
three rounds of tightening the map's fixed-overhead sections without
removing any of the information they carry — denser prose, zero-symbol
modules summarized in one line instead of a full table row each, and the
"Hubs" section requiring 2+ callers instead of 1+ (a symbol called from
exactly one place isn't a hub).

Recomputed with the fixed kit, same methodology, real commands re-run
against this repo's actual history — full breakdown in
[linkshrink-agent-memory-kit/SESSION_LOG.md](https://github.com/sheikharfaz/linkshrink-agent-memory-kit/blob/main/SESSION_LOG.md#update--agent-memory-kit-was-improved-based-on-this-finding):

| Session | Old kit-assisted | New kit-assisted | Baseline |
|---|---|---|---|
| 2 | 1,293 | 511 | 734 |
| 3 | 1,271 | 498 | 391 |
| 4 | 1,440 | 667 | 868 |
| **Total** | **≈4,004** | **≈1,676** | **≈1,993** |

The kit-assisted total is now below baseline overall (≈1,676 vs. ≈1,993,
~16% fewer), though not literally half — Session 4 alone (four separate
`query.py` calls plus a larger recall) still costs a bit more than
baseline's single three-file re-read, because the crossover point depends
on how many distinct things one session touches, not only on repo size.
Getting below that would mean either shrinking the map below what a real
multi-file project's structure actually needs to say, or dropping "read
the map every session" as a hard rule — both would trade away the thing
`codebase-memory` is actually for. The original ≈4,004 number is kept
throughout this document and `SESSION_LOG.md` rather than edited away,
because the fix it led to is a better piece of evidence than a clean
result would have been.

## Update 2 — pushed below half, hit a real ceiling

Asked to get the kit-assisted total under *half* of baseline (≈996
tokens). Two more real, tested rounds landed upstream — same rule as
round 1, drop no information, only the ceremony around it: `Stack`/entry
points/HTTP surface merge into one section when the surface is small
enough to name in a few lines; the module table only appears once
there's enough to tabulate; `Coverage`'s four bullets condense to two;
`query.py file`'s symbol list becomes one comma-joined line instead of
one padded line per symbol. Full detail in
[linkshrink-agent-memory-kit/SESSION_LOG.md](https://github.com/sheikharfaz/linkshrink-agent-memory-kit/blob/main/SESSION_LOG.md#update-2--asked-to-push-below-half-pushed-again-reported-the-real-ceiling).

| Session | Round 1 | Round 2 | Baseline |
|---|---|---|---|
| 2 | 511 | 431 | 734 |
| 3 | 498 | 429 | 391 |
| 4 | 667 | 570 | 868 |
| **Total** | **≈1,676** | **≈1,430** | **≈1,993** |

**≈1,430 tokens — 28% below baseline, still not under half.** Three
sustained rounds took the kit from 2x-worse than baseline to
meaningfully-better, with a growing margin each round — and each round
was a real, defensible simplification, not a trick to move a number. The
remaining ≈434-token gap is now smaller than what's left to cut without
crossing a line: the map's floor for a genuine multi-file Python project
(stack, entry points, routes, modules, coverage, the accuracy caveats) is
already down to ~280–320 tokens per session — cutting further means
dropping a fact, not tightening its prose. Skipping the map on an
unchanged codebase could close the rest, but every session in this demo
*does* change the codebase by construction, so that lever has nothing to
work with here even though it would help the far more common real case of
several read-only sessions between edits. The honest report: this
specific, deliberately tiny project's ceiling is "beats baseline by a
real and growing margin," not "half" — `agent-memory-kit`'s own benchmark
suite is where "half, and much more," actually shows up, once a codebase
is large enough for a map to be worth having at all.

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
- **Two real bugs in the tooling itself, found and fixed by building this
  for real.** `dev-recap`'s `gaps` scanner was checking the wrong JSON
  field name against `codebase-memory`'s index and always reported
  indexed files as unindexed — surfaced in Session 2, fixed upstream with
  3 regression tests. Separately, the map-bloat root cause behind the
  ≈4,004-token result (`.agent/skills/` being indexed as if it were this
  repo's own source) — fixed upstream with 6 more regression tests; see
  [Update — the upstream fix](#update--the-upstream-fix). This is
  arguably the most valuable thing this whole exercise produced — real
  defects in a tool that had already shipped, found by actually using it
  on a real (if small) project instead of only ever running it against
  itself.

## What this comparison does not prove

Not that `agent-memory-kit` makes every individual session cheaper —
Session 4's own number still costs a bit more than baseline's, even after
the fix (see the Update section). Not that the resulting code is better —
it's identical in both repos by construction, since that wasn't the
variable under test. Not a claim about answer quality, bug rate, or
development speed — none of those were measured. What it does show,
plainly, with real commands and real output committed alongside the
claims: what `linkshrink-agent-memory-kit`'s process produces that
`linkshrink-baseline`'s doesn't (a PRD/TRD trail, a tool-install audit
log, cross-session recall that survived closing the session), an honest
first measurement including the case where it cost more, and what
happened when that result was investigated instead of hidden.

## See also

- [linkshrink-baseline](https://github.com/sheikharfaz/linkshrink-baseline) — the baseline half of this comparison, with its own `SESSION_LOG.md`
- [linkshrink-agent-memory-kit](https://github.com/sheikharfaz/linkshrink-agent-memory-kit) — the kit-assisted half, with its own `SESSION_LOG.md`
- [agent-memory-kit](https://github.com/sheikharfaz/agent-memory-kit) — the kit itself
- [agent-memory-kit/benchmarks](https://github.com/sheikharfaz/agent-memory-kit/tree/main/benchmarks) — the large-repo token comparison referenced above
