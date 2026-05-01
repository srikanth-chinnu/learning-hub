# 🟡 #14 — Rate Limiting (5-min read)

## 🎯 TL;DR
**Rate limiting is "how many requests per second is this client allowed?" It protects your service from abuse, accidental overuse, and runaway clients. Token Bucket and Sliding Window are the two algorithms you must know.**

---

## 📖 Plain English

Without rate limiting:
- A buggy client retries forever in a tight loop → DDoS yourself
- A malicious bot scrapes your API → cost explosion
- One customer accidentally floods → harms all other customers

With rate limiting:
> "User X may make at most 100 requests per minute. Beyond that, return `429 Too Many Requests`."

Simple in concept. Subtle in implementation.

---

## 🔑 The Five Algorithms

### 1️⃣ Fixed Window
- "100 requests per minute, reset at the top of each minute"
- ✅ Trivial to implement (just count + reset)
- ❌ **Boundary spike problem**: 100 at 11:59:59 + 100 at 12:00:01 = 200 requests in 2 seconds
- Use only when: simplicity > correctness

### 2️⃣ Sliding Window Log
- Track timestamp of every request in the window
- "Have I had 100 requests in the last 60 seconds?"
- ✅ Most accurate
- ❌ Memory grows with traffic (one entry per request)
- Use when: low traffic, accuracy matters

### 3️⃣ Sliding Window Counter
- Two counters (this minute + last minute), weighted by time elapsed
- ✅ Smooth, no boundary spike
- ✅ Constant memory
- Use when: most production cases ★

### 4️⃣ Token Bucket
- Bucket holds N tokens. Refills at R tokens/sec.
- Each request consumes 1 token. No tokens? Reject.
- ✅ Allows bursts (up to bucket size)
- ✅ Used by AWS, Stripe, GCP
- Use when: most production cases ★ — especially when bursts are OK

### 5️⃣ Leaky Bucket
- Requests enter a queue (the bucket). Server processes at fixed rate.
- ✅ Smooths spikes; guaranteed steady output
- ❌ Adds latency (queueing); bucket can fill
- Use when: smoothing traffic to a downstream system

---

## 🪣 Token Bucket — Worked Example

You allow 10 RPS, burst capacity 20.

```
t=0s:  [.................. 20 tokens]
       Client makes 15 requests rapidly.
t=1s:  [...... 5 tokens]   refill +10 → [............. 15 tokens]
       Client makes 5 more rapidly.
t=2s:  [.... 10 tokens]    refill +10 → [.................. 20 tokens (capped)]
```

Burst supported. Steady-state = 10 RPS. Simple. Used by Stripe's API.

---

## 🌐 Where to Apply Rate Limiting

| Layer | What you protect from | Examples |
|---|---|---|
| **CDN / Edge** | DDoS, scraping | Cloudflare, AWS WAF |
| **API Gateway** | Per-API-key limits | Kong, AWS API Gateway |
| **Application** | Per-user, per-endpoint | App-level middleware |
| **Database / Backend** | Expensive queries | Connection limits, query timeouts |

**You usually want multiple layers.** A CDN caps total RPS; the app caps per-user RPS.

---

## 🔑 Distributed Rate Limiting

You have 10 API servers. The user is allowed 100 RPS *total*. How?

### Option 1: Shared Redis counter (most common)
```
INCR rate_limit:user_42:current_minute  (with EXPIRE)
```
- ✅ Simple, correct
- ❌ Redis is a hot path; failure = no limiting

### Option 2: Local + sync
- Each server has a local count; periodically syncs total
- ✅ No hot Redis; lower latency
- ❌ Approximate (may overshoot during sync interval)

### Option 3: Sticky routing (LB hashes user_id to one server)
- ✅ Counter stays local; no sync needed
- ❌ Server failure resets that user's count

**Production reality:** Most companies use Redis with token bucket scripted in Lua for atomicity.

---

## 📋 What to Limit On

| Granularity | When |
|---|---|
| Per IP | Public unauthenticated endpoints (login page) |
| Per API key / user | Authenticated APIs (Stripe, GitHub) |
| Per endpoint | Expensive endpoints get tighter limits |
| Per IP + endpoint | DDoS protection on hot paths |
| Global | Last-resort circuit breaker |

GitHub combines several: 5,000 RPS per token, but `/search` is 30 RPM, and unauthenticated is 60 RPH.

---

## 🚦 Returning the Limit Info

Always tell clients about their limits:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 12
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1735000000
```

This lets well-behaved clients back off intelligently.

---

## ⚠️ Common Pitfalls

1. **Counting by IP only** — NAT means many users share an IP (offices, mobile carriers); they all hit the limit together
2. **No graceful degradation** — When Redis is down, do you allow all traffic, or block all? Decide upfront.
3. **Hard cliff at the limit** — Better: gradually slow down (queueing) before fully rejecting
4. **Forgetting retries amplify** — A client that retries 5 times when rate-limited makes the problem 5x worse. Use exponential backoff.
5. **Not differentiating endpoints** — `/health` and `/expensive-search` shouldn't share a budget

---

## 🏗️ Real-World Examples

- **Stripe API**: Token bucket per API key; 100 read RPS, 100 write RPS, custom for high-volume customers[^1]
- **Twitter API**: Sliding window per user; varies per endpoint
- **GitHub API**: 5,000/hr authenticated; 60/hr unauthenticated; reset returned in headers
- **Cloudflare**: Edge rate limiting, configurable rules across millions of sites

---

## 🔗 Dig Deeper

- 📘 *System Design Interview Vol 1* (Alex Xu) — Chapter 4: Design a Rate Limiter (THE textbook explanation)
- 📺 [ByteByteGo: Rate Limiting](https://www.youtube.com/@ByteByteGo)
- 📘 [Stripe blog: Scaling our API rate limiter](https://stripe.com/blog/rate-limiters)

---

## 📖 Citations

[^1]: [Stripe — Scaling Our API Rate Limiter](https://stripe.com/blog/rate-limiters) — Token bucket, Lua scripts on Redis.

---

← [Back to 5-min reads index](./README.md)
