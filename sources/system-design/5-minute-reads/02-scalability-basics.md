# 🟢 #2 — Scalability: Vertical vs Horizontal (5-min read)

## 🎯 TL;DR
**Scaling means handling more load. Vertical scaling = "buy a bigger server." Horizontal scaling = "buy more servers." The first is easy but capped; the second is harder but limitless.**

---

## 📖 Plain English

Your app is becoming popular. Two roads to handle the traffic:

### 🪜 Vertical Scaling (Scale Up)
Take your existing server and **make it more powerful**: more CPU, more RAM, faster disks.

- ✅ **Pros:** No code changes. Simple. Predictable.
- ❌ **Cons:** There's a hard ceiling (the biggest server money can buy). Single point of failure. Cost grows non-linearly.

**Analogy:** Trading your bicycle for a motorbike, then for a car, then for a truck. Eventually you can't buy a bigger vehicle.

### ➡️ Horizontal Scaling (Scale Out)
Add **more servers** running copies of your app. Distribute traffic across them with a **load balancer**.

- ✅ **Pros:** Effectively unlimited. Built-in redundancy. Cheaper hardware.
- ❌ **Cons:** Code must be **stateless** (no in-memory user sessions). Database becomes the bottleneck. More moving parts.

**Analogy:** Instead of one bigger truck, you hire 100 motorcyclists. Each one handles less, but together they deliver more.

---

## 🔑 Key Trade-offs

| | **Vertical** | **Horizontal** |
|---|---|---|
| Cost ceiling | High (huge servers cost millions) | Low (commodity hardware) |
| Fault tolerance | Single point of failure | Multiple servers tolerate losses |
| Code changes | None | Must be stateless |
| Operational complexity | Low | High (load balancers, service discovery, distributed state) |
| State management | Easy (one server has it all) | Hard (where does session state live?) |

---

## 🏗️ Real-World Example

**Day 1:** Your blog runs on a single $5/month VPS. ✅ Vertical scaling.

**Day 100:** Your blog goes viral. You upgrade to a $200/month server. Still vertical.

**Day 365:** You hit the limits — even AWS's biggest single instance can't keep up. You:
1. Move sessions out of memory into Redis
2. Put a load balancer in front
3. Run 10 identical app servers behind it
4. Now you can scale to 100 servers, 1000, 10000... 🚀

That last step is **horizontal scaling**.

---

## ⚙️ Stateless vs Stateful — The Critical Concept

Horizontal scaling **requires stateless services**.

- **Stateful service:** Stores user data in memory between requests. (Bad — server X has user A's session, server Y doesn't.)
- **Stateless service:** Stores state externally (DB, Redis, JWT in cookie). Any server can handle any request.

The mantra: **"Servers should be cattle, not pets."** You should be able to kill any server and replace it with a fresh one without anyone noticing.

---

## 📊 Availability Math

Multiple servers also boost **availability**[^1]:

- 1 server with 99.9% uptime = 8h 45m downtime/year
- 2 servers in parallel: `1 - (0.001 × 0.001) = 99.9999%` = 31 seconds/year ⚡
- 4 servers: effectively zero downtime

This is why "scale horizontally" usually means more reliability **and** more capacity, simultaneously.

---

## 🚦 When to Use What

| Use vertical scaling when... | Use horizontal scaling when... |
|---|---|
| Early-stage startup (move fast) | You're hitting the single-server ceiling |
| Strongly consistent transactional databases | Your service is naturally stateless (web, API) |
| You can't afford complexity yet | You need 99.99%+ uptime |
| Quick wins, short timeline | You need geographic distribution |

**Pro tip:** Most systems do both. Vertically scale your database (one strong primary), horizontally scale your app servers.

---

## 🔗 Dig Deeper

- 📘 [donnemartin/system-design-primer — Scaling section](https://github.com/donnemartin/system-design-primer) — "Scalability for Dummies" 4-part series
- 📺 [CS75 Harvard Scalability Lecture (David Malan)](https://www.youtube.com/watch?v=-W9F__D3oY4)
- 📘 [karanpratapsingh/system-design — Chapter I](https://github.com/karanpratapsingh/system-design)

---

## 📖 Citations

[^1]: `donnemartin/system-design-primer:README.md` — Availability formula: `Availability (parallel) = 1 - (1 - A) × (1 - B)`. 99.9% = 8h 45m down/yr; 99.99% = 52m/yr.

---

← [Back to 5-min reads index](./README.md)
