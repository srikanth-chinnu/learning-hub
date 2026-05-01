# Roadmap: From Where You Are to Expert (DSA + System Design)

## Reality check, before any phase

You have **~63 KB of DSA curriculum + a system design curriculum + a tradeoffs report**, all sitting in a folder. None of that is progress. Progress = problems solved + designs explained out loud.

**STOP doing these — they masquerade as progress:**
- Asking for more curricula. You already have material for 2 years.
- Reading without coding. Reading-without-coding is entertainment.
- "Learning" multiple new topics in the same week. You'll retain none.
- Bookmarking videos you'll never watch. Delete them.

## The two-track cadence

You want both DSA and System Design. Fine. But they require different muscles, so they get different schedules.

| Track | Cadence | Block size | Why |
|---|---|---|---|
| **DSA** | Daily, 6 days/wk | 45 min | Short feedback loops, gym-style reps |
| **System Design** | Weekly, 1 block | 2 hr (Sat AM) | Deep, paper-writing-style work |

**If you can only sustain one — pick DSA.** It's measurable, has tighter feedback, and unlocks job offers faster.

---

## Phase 1 — Foundation (Weeks 1–4)

**Goal:** fix the leaky basics. You probably skipped these and built advanced thinking on shaky ground.

**DSA daily:**
- Curriculum: Tier 1 topics 1.1 → 1.11, one per ~2 days.
- Each topic: code the example + solve 1 NeetCode-150 easy.
- **Saturday:** re-solve last Monday's problem from scratch, no peeking.
- **Sunday:** rest.

**System design weekly (Sat 2 hr):**
- Pick 4 foundational topics across 4 weeks: consistent hashing, load balancing, caching, sharding/replication.
- For each: 1-page written summary in **your own words**. Hand-drawn diagrams (no Lucid, no Excalidraw — pen and paper forces understanding).

**Milestone — end of Week 4:**
- ✅ 25 LeetCode easies solved in <15 min each.
- ✅ "Design a URL shortener" recorded on your phone, talking out loud, no notes. Watch it back.

**Kill switch:** <15 problems solved by Week 4 → you don't have a knowledge problem, you have a discipline problem. Stop reading curricula. Find an accountability partner or pay for a coach. The roadmap won't fix this — only external pressure will.

---

## Phase 2 — Interview-Ready (Weeks 5–12)

**Goal:** clear FAANG mediums in <30 min and walk through canonical system designs.

**DSA daily:**
- Tier 2 topics 2.1 → 2.14.
- Mix: 1 medium NeetCode + 1 medium from random Top-100 LC.
- **Stress test (M.7) every "optimized" solution.** This is non-negotiable — most submitted bugs would die here.
- Friday: 1 hard.

**System design weekly:**
- Topics: rate limiting, pub/sub, event sourcing, CQRS, eventual consistency, leader election.
- Read 1 chapter/week from *System Design Interview* (Alex Xu) or *Designing Data-Intensive Applications* (Kleppmann — pick this if you want depth over breadth).
- **Sat block:** design one of {Twitter, WhatsApp, Uber, Dropbox, YouTube, TinyURL} in 45 min. **Record yourself.** Watch it back. Self-critique in writing.

**Milestone — end of Week 12:**
- ✅ ≥50% pass rate on LC mediums in 30 min, tracked in spreadsheet.
- ✅ 4 recorded system design walkthroughs, each self-critiqued.

**Kill switch:** medium pass rate <30% → drop back to Phase 1's easies. You're in the wrong tier. No shame; faking ahead is worse.

---

## Phase 3 — Advanced (Months 4–6)

**Goal:** be dangerous in contests + own LLD design end-to-end.

**DSA:**
- Tier 3 (DP, Dijkstra, segment trees, KMP).
- AtCoder EDPC: 2 problems/week.
- 1 Codeforces round/week (start Div 3 → Div 2).

**System design + LLD:**
- HLD case studies, microservices, observability, multi-region active-active, data pipelines (Kafka/Flink).
- **LLD:** pick a small system (parking lot, vending machine, chess, in-memory FS). Design + implement in **Python first, then C++**. Unit tests required. Both languages, because you'll discover the design holes only when the second language exposes them.

**Milestone — end of Month 6:**
- ✅ Codeforces ≥1400 sustained over 5 contests.
- ✅ 5 LLD designs implemented + tested.
- ✅ Pass one mock onsite-style system design interview.

**Kill switch:** Codeforces <1100 after 10 contests → you skipped Tier 1–2. Go back. Don't argue with the rating.

---

## Phase 4 — Expert / Specialization (Months 7–12)

**Don't try to learn all of Tier 4.** Pick 6 topics aligned to your goal:

| Goal | Pick these |
|---|---|
| HFT / quant | segment tree beats, FFT/NTT, persistent segtree, suffix array |
| Staff distributed systems | consensus (Raft/Paxos), Lamport/vector clocks, CRDTs, TLA+ |
| Compiler / DB internals | suffix automaton, Aho–Corasick, advanced graph algos |
| Generalist senior IC | HLD, centroid decomposition, MCMF, LCA, 2-SAT |

**Cadence:** 1 expert topic per 2 weeks. Implement the template + 3 problems. Don't move on until you can re-implement the template from scratch.

**Milestone — end of Month 12:**
- ✅ Codeforces ≥1700 (or LeetCode contest ≥2000).
- ✅ 1 system designed end-to-end **and deployed** as a toy project on AWS/GCP. Diagrammed-only doesn't count.

---

## Tracking — non-optional

Create a Google Sheet **today**, before starting Phase 1:

| date | topic | problem | time-to-solve | first-submit-AC | notes |
|---|---|---|---|---|---|

Review weekly. The graph of "problems-solved-per-week" is the single best leading indicator. If the line is flat, the roadmap is failing — diagnose immediately.

**If you cannot create that sheet by tonight, this roadmap is dead** and you should admit it. Better to admit it than to spend 6 months pretending.

---

## What Counts as Evidence

| Lying to yourself | Real evidence |
|---|---|
| "I read about segment trees" | "I implemented one; it passed 5 problems" |
| "I understand consistent hashing" | "I drew it for a friend who then explained it back correctly" |
| "I bookmarked the video" | "I watched it; my 1-page note is in my own words" |
| "I'll start Monday" | "I solved a problem today" |

---

## Decision points along the way

1. **End of Phase 1:** are you actually doing this, or rationalizing? If discipline is the bottleneck, no amount of curriculum fixes it.
2. **End of Phase 2:** are you interviewing yet? If you're "not ready" after 12 weeks of consistent work, you'll never feel ready. Apply.
3. **End of Phase 3:** which specialization do you actually care about? If you can't answer, you don't have a goal — you have a hobby.
