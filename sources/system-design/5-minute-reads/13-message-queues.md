# 🟡 #13 — Message Queues & Pub/Sub (5-min read)

## 🎯 TL;DR
**A message queue lets services communicate asynchronously by parking messages in a buffer. Producers push, consumers pull at their own pace. Pub/Sub is a queue with broadcast: one publish, many subscribers receive. They're the duct tape of distributed systems.**

---

## 📖 Plain English

A user uploads a video on YouTube. What happens?

**Without a queue (synchronous):**
```
[Upload] → [Transcode 720p] → [Transcode 1080p] → [Generate thumbnail]
   ↓             ↓                ↓                       ↓
30s          120s              180s                    20s
                = 350 seconds. User waits. ❌
```

**With a queue (async):**
```
[Upload] → [Queue] → response: "Uploaded! Processing..." (1 second) ✅
                ↓
       [Transcoder workers] pick up jobs
       [Thumbnail workers] pick up jobs
       (run in parallel, behind the scenes)
```

The user gets an instant response. Heavy work happens in the background. **Decoupling.**

---

## 🔑 Two Main Patterns

### Queue (Point-to-Point) — exactly one consumer wins
```
[Producer A]  ──┐
[Producer B]  ──┼──► [Queue] ──► [Consumer 1]    each msg
[Producer C]  ──┘                [Consumer 2]    goes to
                                 [Consumer 3]    one consumer
```
**Use when:** You have work to do, and any worker can do it. (E.g., process this payment, send this email.)

**Examples:** AWS SQS, RabbitMQ (work queue), Redis lists, Sidekiq

### Pub/Sub (Topic-Based) — every subscriber gets a copy
```
[Publisher] ──► [Topic: order.created] ──┬──► [Email service]
                                         ├──► [Inventory service]
                                         └──► [Analytics service]
```
**Use when:** An event happened, and many parts of the system care about it. (E.g., user signed up → send welcome email AND start onboarding flow AND track analytics.)

**Examples:** Apache Kafka, Google Pub/Sub, AWS SNS, Redis Pub/Sub, NATS

---

## 🚀 Why Queues?

| Benefit | Explanation |
|---|---|
| **Decoupling** | Producer doesn't know who consumes. Add/remove consumers without touching producer. |
| **Buffering** | Spikes absorbed by queue. Black Friday traffic? Queue holds it. |
| **Resilience** | If consumer crashes, message stays in queue. Retry safely. |
| **Async work** | User doesn't wait for slow operations. |
| **Fan-out** | One event → many side effects. |
| **Throttling** | Workers process at sustainable pace. |

---

## ⚙️ Delivery Guarantees — The Hard Part

This is **the** trade-off you'll discuss in interviews.

### At-Most-Once
- Message sent, fire-and-forget
- ✅ Fast, simple
- ❌ Messages can be lost
- Use when: metrics, logs, where loss is acceptable

### At-Least-Once (the default)
- Message will be delivered, possibly multiple times
- ✅ No data loss
- ❌ **Consumers must be idempotent** (same msg twice = same result)
- Use when: most cases — emails, notifications, payment processing

### Exactly-Once
- Message delivered exactly one time, no duplicates
- ✅ The dream
- ❌ Famously hard / expensive (Kafka transactions, dedup keys)
- Use when: financial systems, billing

**Reality:** Most systems use **at-least-once + idempotency** (assign each message a unique ID; consumer skips IDs it has already processed).

---

## 📊 Big Three: Kafka vs RabbitMQ vs SQS

| | **Kafka** | **RabbitMQ** | **SQS** |
|---|---|---|---|
| **Type** | Distributed log | Traditional broker | Managed queue |
| **Best for** | Event streaming, analytics, high throughput | Complex routing, work queues | Simple async at AWS |
| **Throughput** | Millions msg/sec | 50K-1M msg/sec | Tens of thousands |
| **Persistence** | Disk (configurable retention) | Disk or memory | Backed (up to 14 days) |
| **Ordering** | Per partition | Per queue | FIFO queues only |
| **Replay messages** | ✅ Yes (key feature) | ❌ No | ❌ No |
| **Operational burden** | High (Zookeeper/KRaft) | Medium | Zero (managed) |

**Quick guide:**
- **Kafka** = log of events, big data, streaming, analytics, change-data-capture
- **RabbitMQ** = work queues, routing, traditional pub/sub
- **SQS** = "give me a queue" with zero ops on AWS
- **Redis Streams / Pub/Sub** = lightweight, in-memory, simple cases

---

## 🛠️ Queue Patterns

### Dead-Letter Queue (DLQ)
After N failed retries, message goes to a DLQ for manual inspection. Don't drop bad messages silently.

### Priority Queues
Some messages are urgent. RabbitMQ supports priority levels.

### Delay Queues
"Process this in 1 hour." SQS supports delivery delays.

### Outbox Pattern
Atomically write to DB + queue. Solution: write event to local DB table, separate process publishes events. Crucial for consistency.

---

## ⚠️ Common Pitfalls

1. **Non-idempotent consumers** — At-least-once delivery + side effects = double-charged credit cards. Always design for idempotency.
2. **Tight coupling via queue** — If service A breaks when B's queue format changes, you've coupled them. Use schemas (Avro, Protobuf) and versioning.
3. **Unbounded queues** — Queue grows forever, memory dies. Set max size; configure backpressure.
4. **Hot partitions** — In Kafka, all messages with the same key go to the same partition. Watch for skew.
5. **Treating Kafka like a generic queue** — Kafka is a *log*, not a queue. Use the right tool.

---

## 🔗 Dig Deeper

- 📘 *Designing Data-Intensive Applications* — Chapter 11: Stream Processing
- 📘 [karanpratapsingh/system-design — Message Queues](https://github.com/karanpratapsingh/system-design)
- 📺 [ByteByteGo: How Apache Kafka Works](https://www.youtube.com/@ByteByteGo)
- 📘 [Confluent Kafka tutorial](https://developer.confluent.io/learn-kafka/)

---

← [Back to 5-min reads index](./README.md)
