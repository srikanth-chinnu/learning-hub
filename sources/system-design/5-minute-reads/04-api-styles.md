# 🟢 #4 — REST vs GraphQL vs gRPC (5-min read)

## 🎯 TL;DR
**REST is the default web API style (simple, cacheable, ubiquitous). GraphQL solves over-fetching for client-driven UIs. gRPC is the fastest and best for microservice-to-microservice. Pick the right tool, not the trendy one.**

---

## 📖 Plain English

When two computers talk to each other over the network, they need a *protocol*. Three popular choices for application APIs:

### 🌐 REST (Representational State Transfer)
- Uses **HTTP verbs**: GET, POST, PUT, DELETE, PATCH
- Resources have URLs: `GET /users/42`, `POST /users`
- Returns **JSON** (usually)
- **Stateless** — each request stands alone
- Standard since 2000

### 🟪 GraphQL
- A **query language** for APIs (Facebook, 2015)
- Client sends a query saying *exactly* what fields it wants
- Single endpoint (`/graphql`); server resolves the query
- Eliminates over-fetching (don't get 50 fields when you need 3)

### 🟦 gRPC
- Google's **RPC framework** (2015) using HTTP/2
- Uses **Protocol Buffers** (binary, not JSON) — much faster + smaller
- Strongly typed schemas (`.proto` files)
- Built-in streaming support

---

## 📊 Side-by-Side

| | **REST** | **GraphQL** | **gRPC** |
|---|---|---|---|
| **Protocol** | HTTP/1.1 or 2 | HTTP/1.1 or 2 | HTTP/2 (required) |
| **Format** | JSON (text) | JSON (text) | Protobuf (binary) |
| **Performance** | Good | Good | Excellent (5-10x smaller payloads) |
| **Schema** | Optional (OpenAPI) | Required (built-in) | Required (.proto) |
| **Caching** | Easy (HTTP cache) | Hard (POST-based) | Hard |
| **Browser support** | ✅ Native | ✅ Native | ❌ Needs gRPC-Web proxy |
| **Streaming** | Limited (SSE/WebSockets) | Subscriptions | Native bidirectional |
| **Tooling** | Excellent | Excellent | Excellent (codegen) |
| **Learning curve** | Low | Medium | Medium-high |
| **Best for** | Public APIs | Mobile/SPA frontends | Microservices |

---

## 🏗️ When to Use Each

### Use REST when...
- You're building a **public API** (third parties consume it)
- You need **HTTP caching** (CDN, reverse proxies)
- Most clients only need a few endpoints
- Simplicity matters more than absolute performance

**Examples:** Stripe API, GitHub API, Twitter API

### Use GraphQL when...
- A **mobile app or SPA** drives the API design
- Clients need different shapes of data per screen
- You're tired of `?fields=...` query strings and `v2/users-with-posts` endpoints
- You can invest in tooling (cache, batching, security)

**Examples:** Facebook, Shopify, Airbnb internal APIs

### Use gRPC when...
- It's **service-to-service** inside your datacenter
- You need maximum throughput / minimum latency
- You want strict typed contracts (great for polyglot teams)
- Bidirectional streaming matters (chat, telemetry, ML serving)

**Examples:** Google internal RPC, Kubernetes control plane, Netflix internal services

---

## 🔑 Key Trade-offs

| Concern | Winner |
|---|---|
| **Smallest payload** | gRPC (binary protobuf) |
| **Easiest to debug** | REST (curl works, JSON is readable) |
| **Best frontend developer experience** | GraphQL (query exactly what you need) |
| **Most cacheable** | REST (HTTP cache headers) |
| **Best for browsers** | REST or GraphQL (gRPC needs proxy) |
| **Best schema enforcement** | gRPC (compile-time codegen) |

---

## 🚦 The "Mixed Stack" Pattern (Most Companies)

In practice, modern systems use **all three**:

```
[Browser/Mobile] → [REST or GraphQL Gateway] → [gRPC] → [microservices]
                          ↑                       ↑
                  External-facing,         Internal, fastest
                  cacheable, simple        possible RPC
```

- Mobile/web hits **GraphQL** (great DX, custom queries per screen)
- Internal services talk via **gRPC** (fast, typed)
- Public/partner APIs use **REST** (simple, broadly compatible)

---

## 🔗 Dig Deeper

- 📺 [ByteByteGo: SOAP vs REST vs GraphQL vs gRPC](https://www.youtube.com/@ByteByteGo)
- 📘 [karanpratapsingh/system-design — Chapter III: REST/GraphQL/gRPC](https://github.com/karanpratapsingh/system-design)
- 📘 [donnemartin/system-design-primer — Communication section](https://github.com/donnemartin/system-design-primer)

---

← [Back to 5-min reads index](./README.md)
