# 🔴 #20 — Observability: Logs, Metrics, Traces (5-min read)

## 🎯 TL;DR
**Observability is "can I figure out what's broken?" The Three Pillars are logs, metrics, and traces — each answers a different question. Modern systems use all three. The goal is to be able to ask new questions about your system without re-deploying code.**

---

## 📖 Plain English

A user reports: "The site is slow." You have 100 microservices. Where's the problem?

Without observability: panic. SSH into servers. Greps logs. Maybe find something. Hours pass.

With observability: dashboards show a spike in p99 latency on Service B. A trace shows requests are stuck in B → C calls. A log shows C's database connection pool is exhausted. Fix in minutes.

**Monitoring vs Observability:**
- **Monitoring** = watching pre-defined dashboards for known issues
- **Observability** = ability to investigate *unknown* issues by querying system state

You need both, but observability is the harder, more valuable one.

---

## 🏛️ The Three Pillars

### 1️⃣ Logs — "What happened?"

Time-stamped text records of events.

```
2024-12-15 14:23:01 [ERROR] payment.charge failed: card_declined user_id=42 amount=99.99
```

✅ **Strengths:** Rich context, human-readable, simple to add  
❌ **Weaknesses:** Expensive to store/search at scale, no aggregation

**Tools:** Elasticsearch + Kibana (ELK), Splunk, Datadog Logs, Loki, AWS CloudWatch Logs

**Best practice:** **Structured logging** (JSON). Future-you will thank present-you.
```json
{"timestamp":"2024-12-15T14:23:01Z","level":"ERROR","service":"payment","event":"charge_failed","user_id":42,"amount":99.99,"reason":"card_declined","trace_id":"abc123"}
```

---

### 2️⃣ Metrics — "How's the system performing?"

Numerical values measured over time.

```
http_requests_total{service="api",status="500"}  →  1247 in last 5 min
http_request_duration_seconds{quantile="0.99"}    →  340ms
db_connection_pool_active                          →  85 / 100
```

✅ **Strengths:** Cheap to store, fast to aggregate, alertable  
❌ **Weaknesses:** Lose individual request detail; high cardinality is expensive

**Tools:** Prometheus + Grafana, Datadog, New Relic, CloudWatch Metrics

**The Four Golden Signals (Google SRE)**:[^1]
1. **Latency** — how long requests take
2. **Traffic** — RPS, transactions/sec
3. **Errors** — failure rate
4. **Saturation** — how full the system is (CPU, memory, queue depth)

If you have nothing else, monitor these four for every service.

---

### 3️⃣ Traces — "Where's the time going?"

Records of a request as it flows through *many* services.

```
Trace ID: abc123, total: 850ms

[API Gateway   :  10ms]
  └─[Auth Service       :  20ms]
  └─[Order Service      : 800ms]   ← bottleneck!
       └─[DB query        : 750ms]   ← root cause!
       └─[Payment Service :  30ms]
       └─[Inventory       :  20ms]
```

You instantly see: "the DB query in Order Service is the bottleneck."

✅ **Strengths:** Pinpoints bottlenecks across services; great for debugging  
❌ **Weaknesses:** Volume is enormous (sample!); requires instrumentation everywhere

**Tools:** Jaeger, Zipkin, Datadog APM, AWS X-Ray, Honeycomb

**OpenTelemetry** is the modern open standard for tracing instrumentation; works with any backend.

---

## 🌐 The Observability Stack (Modern)

```
[Your service code]
       │
       ▼
[OpenTelemetry SDK]   ← auto-instruments your code
       │
       ▼
[OpenTelemetry Collector]   ← receives, batches, exports
       │
   ┌───┼────────┐
   ▼   ▼        ▼
 [Prom]  [Jaeger]  [Loki]      ← Metrics, Traces, Logs
   │       │        │
   └───────┴────────┘
           ▼
        [Grafana]              ← Single dashboard pane
```

This is the **CNCF reference stack**: Prometheus + Grafana + Jaeger + Loki + OpenTelemetry. All open source. Used by thousands of companies.

---

## 📊 Service Level Objectives (SLOs)

Pick a metric that captures user happiness, decide a target, measure relentlessly.

```
SLO: 99.9% of /checkout requests complete in < 500ms over 30 days

Error budget: 0.1% × 30 days = 43 minutes of "unhappiness" allowed
```

If you're burning the error budget too fast → freeze new features, focus on reliability.
If you have plenty of budget → ship faster, take more risk.

This is the heart of **Site Reliability Engineering** (SRE) at Google.[^2]

---

## 🎯 What Good Observability Looks Like

You can answer:
1. ✅ "Is everything working right now?" (dashboards)
2. ✅ "Are we meeting SLOs?" (alerts)
3. ✅ "Why did this *one user's* request fail?" (traces + structured logs by trace_id)
4. ✅ "Is this latency spike new?" (long-term metrics)
5. ✅ "Which deploy caused this?" (correlate metrics with deploy events)
6. ✅ "What does this look like by region/user-tier/version?" (high-cardinality queries)

If you can't answer #3 in under 5 minutes, you don't have observability — you have nostalgia.

---

## ⚠️ Common Pitfalls

1. **Logging *everything*** — Logs explode. Be selective. Use sampling for high-volume events.
2. **Cardinality bombs in metrics** — `user_id` as a label = millions of time series = Prometheus melts. Keep cardinality bounded.
3. **No correlation IDs** — Logs without `trace_id` are useless for cross-service investigations.
4. **Alerts that cry wolf** — Page on user-impacting symptoms (high error rate), not internal anomalies (CPU at 80%). Symptoms + causes, not causes alone.
5. **"We have logs"** ≠ "We have observability." If you can't query/aggregate, you're storing data, not learning from it.
6. **Tracing without sampling** — At scale, full tracing is too much. Use head-based or tail-based sampling.

---

## 🚦 Day-One Setup for a New Service

For any new microservice, day one:

```yaml
✅ Structured JSON logs to stdout (always)
✅ Trace ID injected into every log line
✅ Prometheus metrics endpoint at /metrics
✅ Standard labels: service, version, env
✅ The Four Golden Signals exposed
✅ /health endpoint (for k8s, LB)
✅ /ready endpoint (different from /health)
✅ Distributed tracing via OpenTelemetry
```

Don't add this later. Add it on day one. You will save weeks of pain.

---

## 🔗 Dig Deeper

- 📘 [Site Reliability Engineering (Google) — free online](https://sre.google/sre-book/table-of-contents/) ★★★
- 📘 [The SRE Workbook (Google) — practical SLOs](https://sre.google/workbook/table-of-contents/)
- 📘 [observability.engineering — free book by Charity Majors](https://www.honeycomb.io/observability-engineering)
- 📘 [OpenTelemetry docs](https://opentelemetry.io/)
- 📘 [Distributed Systems Observability — Cindy Sridharan (free O'Reilly book)](https://www.oreilly.com/library/view/distributed-systems-observability/9781492033431/)

---

## 📖 Citations

[^1]: [Google SRE Book — Chapter 6: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/) — defines the Four Golden Signals.
[^2]: [Google SRE Book — Chapter 4: Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — the canonical SLO/error-budget treatment.

---

← [Back to 5-min reads index](./README.md)
