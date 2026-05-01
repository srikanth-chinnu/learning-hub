# 🟢 #3 — Latency vs Throughput (5-min read)

## 🎯 TL;DR
**Latency = how long one request takes. Throughput = how many requests per second. They're related but optimizing one often hurts the other.**

---

## 📖 Plain English

Imagine a coffee shop:

- **Latency:** how long YOU wait from "ordering" to "receiving your coffee." (You care about this.)
- **Throughput:** how many coffees the shop serves per hour. (The owner cares about this.)

A barista who makes one perfect espresso in 30 seconds = low latency, low throughput.
A drive-thru with 5 baristas making 100 mediocre coffees per minute = higher throughput but maybe higher latency per customer (queue).

In systems:
- **Latency** is measured per request: `p50 latency = 50ms`, `p99 = 250ms`
- **Throughput** is rate: `1,000 requests/second (RPS)`, `5 GB/sec`

---

## 🔑 The Counterintuitive Truth

**You can have high throughput AND high latency simultaneously.**

Example: A nightly batch job processes 10 million records (high throughput!) but each one takes 2 seconds (high latency). That's fine — nobody is waiting on individual records.

Example: A real-time API serves 10,000 RPS (high throughput!) at 5ms p99 (low latency). That's elite.

**The two are independent dimensions.** A good system optimizes the one that matters for the use case.

---

## 📊 Percentiles Matter More Than Averages

If you only know "average latency = 50ms", you don't know how bad bad days are.

| Percentile | Meaning |
|---|---|
| **p50 (median)** | Half the requests are faster, half are slower |
| **p95** | 95% of requests are this fast or faster |
| **p99** | The slowest 1% of requests — your unhappy customers |
| **p99.9** | 1 in 1000 worst — system pathologies |

**Why p99 matters:** A user who makes 100 requests has a ~63% chance of hitting at least one p99 request.[^1] So p99 latency basically *is* the user-perceived latency.

---

## 🏗️ Latency Numbers Every Engineer Should Know

From Jeff Dean's famous "Latency Numbers Every Programmer Should Know":[^2]

| Operation | Latency |
|---|---|
| L1 cache reference | 0.5 ns |
| Branch mispredict | 5 ns |
| L2 cache reference | 7 ns |
| Mutex lock/unlock | 25 ns |
| Main memory reference | 100 ns |
| Compress 1KB with Snappy | 3 µs |
| Send 1KB over 1Gbps network | 10 µs |
| **Read 4KB from SSD** | **150 µs** |
| Read 1MB sequentially from memory | 250 µs |
| **Round trip in same datacenter** | **500 µs** |
| Read 1MB sequentially from SSD | 1 ms |
| Disk seek (HDD) | 10 ms |
| **Round trip CA → Netherlands** | **150 ms** |

**Internalize these.** Senior engineers reason in these numbers without thinking.

---

## ⚖️ The Trade-Off

To increase **throughput**, you often **batch** or **parallelize**. Both can hurt **latency**:

| Optimization | Throughput effect | Latency effect |
|---|---|---|
| Batching (collect 100 requests, send together) | ⬆️ Up | ⬆️ Up (waiting for batch) |
| Parallelism (spawn more workers) | ⬆️ Up | ➡️ Same per request |
| Pipelining (overlap stages) | ⬆️ Up | ➡️ Same |
| Caching | ⬆️ Up (hits) | ⬇️ Down (hits) |

**Kafka** is throughput-optimized: millions of msg/sec at the cost of ~10ms latency due to batching.
**Redis** is latency-optimized: sub-ms latency at the cost of running mostly in single-threaded memory.

---

## 🚦 What to Optimize

| User-facing? | Optimize for | Example |
|---|---|---|
| **Yes, real-time** (search, chat, gaming) | Latency (p99 < 100ms) | Twitter timeline, Stripe payment |
| **Yes, async** (video upload, email send) | Throughput (jobs/sec) | YouTube transcoding, Mailchimp |
| **No** (analytics, ML training) | Throughput (rows/sec) | Spark batch jobs, Snowflake |

---

## 🔗 Dig Deeper

- 📘 [Latency Numbers Every Programmer Should Know — Norvig](http://norvig.com/21-days.html#answers)
- 📘 [donnemartin/system-design-primer — Performance vs Scalability section](https://github.com/donnemartin/system-design-primer)
- 📺 [Jeff Dean: Achieving Rapid Response Times in Large Online Services](https://www.youtube.com/watch?v=1-3Ahy7Fxsc)

---

## 📖 Citations

[^1]: Tail latency math: `P(at least one slow) = 1 - P(none slow)¹⁰⁰ = 1 - 0.99¹⁰⁰ ≈ 0.63`
[^2]: [Latency numbers — Jeff Dean / Peter Norvig](http://norvig.com/21-days.html#answers) — also in `donnemartin/system-design-primer` appendix.

---

← [Back to 5-min reads index](./README.md)
