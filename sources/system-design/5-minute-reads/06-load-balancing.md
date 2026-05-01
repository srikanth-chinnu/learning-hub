# 🟡 #6 — Load Balancing (5-min read)

## 🎯 TL;DR
**A load balancer (LB) is a traffic cop sitting between users and your servers. It distributes requests so no one server gets overwhelmed and your system survives if a server dies. The "L4 vs L7" distinction matters more than the algorithm.**

---

## 📖 Plain English

You have 10 backend servers. A user sends a request. Where does it go?

A **load balancer** picks one. That's it. It's a piece of software (NGINX, HAProxy) or a managed service (AWS ALB, Cloudflare) that sits in front, accepts requests, and routes them.

```
                 ┌──────► Server 1
[User] → [LB] ───┼──────► Server 2
                 └──────► Server 3
```

If Server 2 dies, the LB **stops sending traffic** there. From the user's point of view, nothing happened.

---

## 🔀 Load Balancing Algorithms

| Algorithm | How it works | Best for |
|---|---|---|
| **Round Robin** | 1 → 2 → 3 → 1 → 2 → 3 ... | Identical servers, similar request weights |
| **Weighted Round Robin** | Bigger servers get more traffic | Heterogeneous hardware |
| **Least Connections** | Send to whoever has fewest active requests | Long-running connections (streaming, WebSockets) |
| **IP Hash** | `hash(client_ip) % N` always picks same server | Sticky sessions without cookies |
| **Least Response Time** | Send to the fastest-responding server | Latency-sensitive workloads |
| **Random** | Just pick one randomly | Simplest, surprisingly effective |
| **Power of 2 Choices** | Pick 2 random, send to whichever is less loaded | Best in practice — used by Twitter, Netflix |

**Pro tip:** Don't agonize over the algorithm. Round Robin or "Power of 2 Choices" is correct 95% of the time.

---

## 🏗️ Layer 4 vs Layer 7 — THE Critical Distinction

This is what interviewers actually ask about.

### L4 (Transport Layer)
- Routes based on **TCP/UDP info only**: source/destination IP, port
- **Cannot read** the request content
- Extremely fast (handles millions of connections)
- **Use when:** Pure performance matters, raw TCP traffic, gaming servers

### L7 (Application Layer)
- Reads the **full HTTP request**: URL path, headers, cookies, body
- Can route `/api/*` to API servers, `/images/*` to image servers
- Can do SSL termination, compression, retries, header rewriting
- **Use when:** HTTP traffic with content-based routing needs

| | **L4** | **L7** |
|---|---|---|
| Speed | Faster | Slower (parses HTTP) |
| Inspect content? | ❌ No | ✅ Yes |
| SSL termination | ❌ No | ✅ Yes |
| Path routing (`/api/v1`) | ❌ No | ✅ Yes |
| Examples | AWS NLB, HAProxy TCP, Envoy L4 | NGINX, AWS ALB, Cloudflare, Envoy L7 |

**Rule of thumb:** If you're routing HTTP, use L7. Otherwise L4.

---

## 🩺 Health Checks (the unsung hero)

Every LB constantly pings backends:
- **Active health check:** LB sends `GET /health` every 5s. If 3 fail → mark unhealthy.
- **Passive health check:** LB watches for failures during real requests.

**Without health checks, an LB will happily send traffic to a dead server.** Always configure them.

---

## 🪞 Active-Active vs Active-Passive

| | **Active-Active** | **Active-Passive** |
|---|---|---|
| All LBs serve traffic | ✅ | ❌ Only primary serves |
| Failover | Instant (DNS) | Failover script swaps |
| Cost | Higher (use both) | Lower (idle backup) |
| Use case | High traffic, geo-distribution | Compliance, simpler ops |

---

## 🚦 Where to Place Load Balancers

```
[DNS Round-Robin]            ← geographic distribution
        │
   [L4 LB at edge]            ← absorbs DDoS, raw TCP
        │
   [L7 LB cluster]            ← HTTP routing, TLS termination
        │
   [Application servers]      ← stateless, behind LB
        │
   [Database with replicas]   ← primary + read replicas
```

This is roughly the architecture of every large web service.

---

## ⚠️ Common Pitfalls

1. **Sticky sessions everywhere** — Defeats the point of stateless services. If you need them, store sessions in Redis instead.
2. **No health checks** — LB will gleefully send traffic to dead servers.
3. **Ignoring connection draining** — When you remove a server, in-flight requests should finish gracefully. Configure draining timeout.
4. **Load balancer = single point of failure** — Use at least 2 LBs in HA mode (or managed service like AWS ALB which handles this).
5. **Hashing on user_id without virtual nodes** — Adding/removing servers reshuffles everything. Use [Consistent Hashing](./11-consistent-hashing.md) instead.

---

## 🔗 Dig Deeper

- 📘 [karanpratapsingh/system-design — Load Balancing chapter](https://github.com/karanpratapsingh/system-design)
- 📺 [ByteByteGo: Top 6 Load Balancing Algorithms](https://www.youtube.com/@ByteByteGo)
- 📘 [donnemartin/system-design-primer — Load balancer + Reverse proxy sections](https://github.com/donnemartin/system-design-primer)

---

← [Back to 5-min reads index](./README.md)
