# 🟡 #12 — Microservices vs Monolith (5-min read)

## 🎯 TL;DR
**Monolith = one codebase, one deployment. Microservices = many small services, each independently deployed. Monoliths win at small scale; microservices win at organizational scale (50+ engineers). Most teams should start with a monolith.**

---

## 📖 Plain English

### Monolith
**One big application.** All features (auth, billing, notifications, products, etc.) live in one codebase, one repository, one deployment artifact.

```
┌─────────────────────────────────────┐
│        MyApp (one process)          │
│  ┌────────┐ ┌─────────┐ ┌────────┐  │
│  │  Auth  │ │ Billing │ │Products│  │
│  └────────┘ └─────────┘ └────────┘  │
│       Single shared database        │
└─────────────────────────────────────┘
```

### Microservices
**Many small applications**, each owning a single business capability, each with its own DB, deployed independently, communicating over the network.

```
[Auth Service]    [Billing Service]   [Products Service]
   │ DB-1              │ DB-2              │ DB-3
   └────────── network calls ──────────────┘
```

---

## 🔑 The Core Trade-Off

> **Microservices trade local complexity for network/operational complexity.**

A monolith has nasty in-codebase complexity: tangled modules, shared dependencies, slow build times, fear of changing anything.

Microservices push that complexity *out of the code* and into the network: timeouts, retries, distributed tracing, eventual consistency, deployment orchestration.

**Both have roughly the same total complexity** — just in different places. The question is: which kind of complexity do you handle better?

---

## 📊 Side-by-Side

| | **Monolith** | **Microservices** |
|---|---|---|
| Codebase | 1 | N (one per service) |
| Deployments | 1 | N (independent) |
| Scaling | Whole app together | Per-service |
| Tech stack | Usually one | Polyglot (use right tool) |
| Team coordination | Hard at >50 engineers | Each team owns its service |
| Network overhead | None (in-process) | Significant (RPC, latency) |
| Debugging | Stack trace | Distributed tracing |
| Transactions | ACID via DB | Saga pattern (eventual consistency) |
| Failure mode | Whole app crashes | Partial (other services work) |
| Time to ship feature (early) | Fast | Slow (more setup) |
| Time to ship feature (large org) | Slow (coordination) | Fast (independent teams) |

---

## 🚦 Use Microservices When...

✅ You have **multiple teams** (Conway's Law — your architecture mirrors your org chart)
✅ Different services need **different scaling** (search needs 100 servers; user profile needs 2)
✅ Different services need **different tech** (ML in Python, real-time in Go, web in Node)
✅ You need **independent deployment** (deploy 10x/day without coordinating)
✅ **Different failure tolerances** (payments must be perfect; recommendations can be flaky)

## 🚦 Use a Monolith When...

✅ You're a **small team** (< 30 engineers)
✅ The product is still finding **product-market fit** (boundaries are unclear)
✅ You don't have **strong DevOps capability**
✅ **Latency matters** (avoiding network hops is huge)
✅ **Strong transactional consistency** is core (SQL transactions span everything)

> **Famously monolithic**: Stack Overflow (one .NET app, one SQL Server, beats most microservices stacks on perf), GitHub (Rails monolith for years), Shopify (Rails "majestic monolith")

---

## 🪜 The Modular Monolith — The Pragmatic Middle

A **modular monolith** is one deployment with **strict internal module boundaries**. Each "module" is structured as if it were a service (its own folder, schema, public API), but they all run together.

```
[MyApp Process]
├── auth/        ← could be a service later
├── billing/     ← could be a service later
└── products/    ← could be a service later
```

✅ Easy to refactor into services *later* if needed
✅ All the perf benefits of a monolith
✅ Most companies should start here, not microservices

This is what Shopify, GitHub, Basecamp do.

---

## ⚠️ Microservices Anti-patterns

1. **Distributed monolith** — Services that must always be deployed together. Worst of both worlds.
2. **Shared database** — Multiple services hitting the same DB. Couples them at the worst layer.
3. **Chatty services** — One user request fans out to 50 internal calls. Latency dies.
4. **Premature decomposition** — Splitting domains you don't understand yet. Boundaries shift painfully.
5. **No service ownership** — When everyone owns a service, no one does. Each service should have a clear team.

---

## 🏗️ Real-World Examples

| Company | Architecture | Why |
|---|---|---|
| **Netflix** | 1000+ microservices | Massive scale, polyglot, independent teams |
| **Amazon** | Service-Oriented (since 2002 Bezos memo) | Forced API boundaries internally |
| **Stack Overflow** | Monolith (.NET + SQL Server) | Very small ops team; extreme perf |
| **Shopify** | Modular monolith (Rails) | Maintained codebase boundaries via "components" |
| **Uber** | Migrated monolith → microservices → DOMA (Domain-Oriented Microservice Architecture)[^1] | Pendulum swing |
| **GitHub** | Rails monolith + few satellite services | Pragmatic, ships fast |

---

## 🔗 Dig Deeper

- 📘 *Building Microservices* by Sam Newman ★
- 📺 [Sam Newman: When To Use Microservices (And When Not To)](https://www.youtube.com/watch?v=GBTdnfD6s5Q)
- 📘 [karanpratapsingh/system-design — Monolith vs Microservices](https://github.com/karanpratapsingh/system-design)
- 📘 [Shopify: Deconstructing the Monolith](https://shopify.engineering/deconstructing-monolith-designing-software-maximizes-developer-productivity)

---

## 📖 Citations

[^1]: [Uber Engineering: Microservice Architecture (DOMA)](https://www.uber.com/blog/microservice-architecture/) — Uber's evolution from monolith to many small services to domain-oriented service groups.

---

← [Back to 5-min reads index](./README.md)
