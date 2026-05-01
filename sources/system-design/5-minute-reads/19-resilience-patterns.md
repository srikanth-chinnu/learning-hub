# 🔴 #19 — Resilience Patterns: Circuit Breaker & Bulkhead (5-min read)

## 🎯 TL;DR
**Distributed systems fail in cascading ways: one slow service can drag down 10 others. Resilience patterns — circuit breakers, bulkheads, timeouts, retries, fallbacks — contain failures so a small fire doesn't burn down the building.**

---

## 📖 Plain English

You have 10 microservices. Service B starts responding slowly. Service A calls B, A's threads pile up waiting. Service C calls A, C's threads pile up waiting. The whole system grinds to a halt.

**This is a cascading failure.** Resilience patterns prevent it.

```
Without patterns:        With circuit breaker + bulkhead:

[A] → [B is slow]       [A] → [B circuit OPEN; instant fail]
 ↓                        ↓
[C] hangs                [C] keeps working with cached result
 ↓
[D] hangs
 ↓
   💥 system dead
```

---

## 🔌 Pattern #1: Circuit Breaker

Inspired by electrical circuit breakers. **Stops calling a failing service** to give it time to recover.

### Three States
```
   [CLOSED]  ──N failures──►  [OPEN]
       ▲                        │
       │                  wait timeout
   success                      │
       │                        ▼
       └─────one success──── [HALF-OPEN]
                             (try one call)
                             on fail → OPEN
                             on success → CLOSED
```

- **CLOSED**: Calls flow normally; track failures
- **OPEN**: Failures crossed threshold; *immediately* fail without calling (fast fail)
- **HALF-OPEN**: After a cool-off, allow one test call; if it succeeds, close the breaker

### Code-Level Example (Hystrix-style)

```python
@circuit_breaker(failure_threshold=5, recovery_timeout=30)
def get_user_profile(user_id):
    return user_service.get(user_id)
```

After 5 failures within a window:
- Breaker opens for 30 seconds
- All calls return `CircuitBreakerOpenError` instantly (no network call)
- After 30s, one call is allowed; rest follows

### Where Used
- **Netflix Hystrix** (the famous library; now in maintenance)
- **Resilience4j** (Java)
- **Polly** (.NET)
- Built into Envoy, Istio, AWS App Mesh

---

## 🚣 Pattern #2: Bulkhead

Named after **ship compartments**: if one floods, others stay watertight.

**Idea:** Isolate resources (threads, connections, memory) per dependency. A failure in one can't drain everything.

### Without Bulkhead
```
[App: 200 threads pool]
   ├─→ Service A (slow → 150 threads stuck)
   ├─→ Service B (only 50 left)
   └─→ Service C (starves)
```

### With Bulkhead
```
[App]
   ├─→ Service A pool: max 50 threads (slow → 50 stuck, 150 left for others)
   ├─→ Service B pool: max 50 threads
   └─→ Service C pool: max 50 threads
```

A's slowness is **contained**. Other services keep working.

This is also why microservices are deployed in **separate processes** — natural bulkheads at the OS level.

---

## ⏱️ Pattern #3: Timeouts

**Always set a timeout on every network call.** Most languages default to "wait forever," which is catastrophic.

```python
# DANGEROUS
response = requests.get(url)  # waits forever if server hangs

# CORRECT
response = requests.get(url, timeout=5)  # fail after 5 seconds
```

### Setting Timeouts
- Use **percentile-based** timeouts: timeout = p99 latency × 2
- Make them **shorter** at higher levels of the stack:
  - DB query: 1s
  - Service call: 3s
  - Total request: 5s
- Otherwise inner timeouts never fire

---

## 🔁 Pattern #4: Retries (with backoff!)

Network is unreliable. Some failures are transient. Retrying often helps.

**But naive retries make things worse:**
- 1 server fails → 100 clients retry → 100x load
- Recovering server gets DDoS'd back into failure

### Exponential Backoff
```
attempt 1: wait 100ms
attempt 2: wait 200ms
attempt 3: wait 400ms
attempt 4: wait 800ms
...
```

### Jitter (critical!)
```python
delay = base * 2^attempt + random(0, base)  # add randomness
```

Without jitter, clients all retry simultaneously → "retry storms." With jitter, retries spread out.[^1]

### Idempotency Required
Retries assume operations are safe to repeat. Use idempotency keys for non-idempotent ops (payments).

---

## 🪂 Pattern #5: Fallbacks (Graceful Degradation)

When the primary path fails, return *something useful*, not an error:

| Primary failed | Fallback |
|---|---|
| Recommendation engine | Return generic top-10 list |
| Personalized homepage | Return cached version from yesterday |
| Search service | Return autocomplete suggestions only |
| User profile | Return default avatar + basic info |

Netflix is famous for this:[^2] when the recommendation engine fails, you still see *some* movies, not a 500 error.

---

## ⚡ Pattern #6: Backpressure

When a downstream service can't keep up, **slow down or drop requests** rather than overwhelming it.

- Reactive systems (Akka, RxJava) have first-class backpressure
- HTTP/2 has flow control
- Kafka consumers control their own rate (pull model)

The opposite is **load shedding**: at the edge, when the system is over capacity, reject some requests immediately to protect the rest.

---

## 🌐 Service Mesh: All of This, For Free

A **service mesh** (Istio, Linkerd, Consul Connect) injects a sidecar proxy beside every service. The proxy handles:
- ✅ Circuit breakers
- ✅ Retries with backoff
- ✅ Timeouts
- ✅ mTLS encryption
- ✅ Distributed tracing
- ✅ Load balancing

**No application code changes.** Just configure and deploy.

This is how modern distributed systems get resilience patterns "for free."

---

## 🚦 The Resilience Checklist

For every external service call:

- [ ] Has a **timeout** (not "wait forever")
- [ ] Has **retry with jitter + exponential backoff**
- [ ] Is wrapped in a **circuit breaker**
- [ ] Has a **fallback** (cached, default, or graceful error)
- [ ] Uses a **bounded thread pool / connection pool**
- [ ] Is **observable** (metrics: success rate, latency, p99)
- [ ] Is **idempotent** if retried

Even half this checklist makes you better than 90% of production systems.

---

## 🔗 Dig Deeper

- 📘 *Release It!* by Michael Nygard ★ — the bible of resilience patterns
- 📘 [Hystrix wiki — patterns & rationale](https://github.com/Netflix/Hystrix/wiki)
- 📘 [AWS Builders' Library: Avoiding Cascading Failures](https://aws.amazon.com/builders-library/avoiding-fallback-in-distributed-systems/)
- 📘 [Resilience4j docs](https://resilience4j.readme.io/)
- 📘 [Marc Brooker: Exponential Backoff and Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)

---

## 📖 Citations

[^1]: [Marc Brooker: Exponential Backoff and Jitter (AWS)](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/)
[^2]: [Netflix Tech Blog — Hystrix and Fallbacks](https://netflixtechblog.com/) — graceful degradation philosophy.

---

← [Back to 5-min reads index](./README.md)
