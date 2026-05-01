# 🔴 #18 — Event-Driven Architecture & Saga Pattern (5-min read)

## 🎯 TL;DR
**Event-driven architecture (EDA) means services react to events instead of calling each other directly. The Saga pattern is how you do "distributed transactions" without 2PC: a chain of local transactions, each compensated if a later one fails.**

---

## 📖 Plain English

### Traditional Request-Response (synchronous)
```
[Order Service] ──calls──→ [Payment Service] ──calls──→ [Inventory] ──calls──→ [Shipping]
                  │                              │                    │
              waits, fails if         tightly coupled,     fan-out cascade,
              any service is down     blocking, slow       hard to evolve
```

If any service is slow or down, the whole chain fails.

### Event-Driven Architecture
```
[Order Service] → emits event "OrderCreated" → [Event Bus / Kafka]
                                                    │
                                ┌───────────────────┼──────────────────┐
                                ▼                   ▼                  ▼
                          [Payment Svc]      [Inventory Svc]    [Shipping Svc]
                          (reacts)            (reacts)           (reacts)
```

Each service:
- ✅ Doesn't know who else is listening
- ✅ Reacts in its own time
- ✅ Can be deployed independently
- ✅ Survives if other services are temporarily down

---

## 🎯 Core EDA Concepts

| Term | Meaning |
|---|---|
| **Event** | An immutable fact: "OrderCreated", "UserSignedUp" |
| **Producer** | Service that emits events |
| **Consumer** | Service that reacts to events |
| **Event bus** | Where events flow (Kafka, RabbitMQ, Pub/Sub) |
| **Choreography** | Each service knows what events to react to (decentralized) |
| **Orchestration** | A central coordinator tells services what to do (centralized) |

---

## 🌀 The Saga Pattern — Distributed Transactions Without 2PC

The classic problem:

> "Place an order: charge the credit card AND reserve inventory AND ship. If any step fails, undo the others."

In a single database, this is a `BEGIN TRANSACTION ... COMMIT`. Across microservices, no such luxury.

**Saga** = a sequence of local transactions, each with a compensating action.

### Example: E-commerce Saga

```
1. Order Service     → INSERT order (pending)        [compensate: cancel order]
2. Payment Service   → charge card                   [compensate: refund]
3. Inventory Service → reserve items                 [compensate: release reservation]
4. Shipping Service  → create shipment               [compensate: cancel shipment]
5. Order Service     → UPDATE order to confirmed
```

If **step 3** fails:
- Run compensation for **step 2** (refund the card)
- Run compensation for **step 1** (cancel the order)
- Tell the user: "Couldn't fulfill the order"

This avoids 2PC (two-phase commit) which requires all systems to lock and is fragile across the network.

---

## 🎭 Choreography vs Orchestration

### Choreography (decentralized)
```
Order Svc emits "OrderCreated"
   ↓
Payment Svc listens, charges, emits "PaymentSucceeded"
   ↓
Inventory Svc listens, reserves, emits "InventoryReserved"
   ↓
Shipping Svc listens, ships, emits "ShipmentCreated"
   ↓
Order Svc listens, marks order as confirmed
```

- ✅ Loose coupling
- ❌ Hard to understand the flow (no central place that defines it)
- ❌ Compensation logic scattered

### Orchestration (centralized)
```
[Order Saga Orchestrator]
        │
        ├─→ Payment.charge → success
        ├─→ Inventory.reserve → success
        ├─→ Shipping.ship → FAILED
        ├─→ Inventory.release (compensation)
        └─→ Payment.refund (compensation)
```

- ✅ Clear, central definition
- ✅ Easy to monitor & test
- ❌ Orchestrator becomes a focal point (could be a bottleneck/SPOF)

**Both are valid.** Use orchestration for complex business flows; choreography for simpler, evolving systems. Tools: Temporal, Camunda Zeebe, AWS Step Functions for orchestration.

---

## 📦 Event Sourcing (related, but different)

- **Event-driven architecture** = services communicate via events
- **Event sourcing** = the *state* of your data is the log of events; current state is computed by replaying

```
Traditional:   [Account: balance = $100]   ← stored
Event sourced: [Account events: +$50, +$50, -$10, +$10]   ← stored
                Current balance: replay = $100
```

Used when:
- You need a complete audit trail
- You want to "rewind" state for debugging
- You want to compute multiple "views" of the same data
- Examples: financial systems (Stripe), git (literally event-sourced), CQRS apps

Pairs naturally with EDA: emit each event when state changes.

---

## 🏗️ Real-World EDA at Scale

### Uber
Each trip emits 50+ events; downstream systems consume them in parallel (pricing, ETA prediction, driver state, billing, fraud).

### LinkedIn
Invented Kafka. Every user action is an event. ML models, analytics, notifications all consume the same event stream.

### Netflix
Backend microservices use events extensively. Migrated from hard-coded service calls to event-driven for resilience.

### Stripe
Webhooks are an EDA pattern: when something happens in Stripe, an event is sent to your endpoint. You react.

---

## ⚠️ Common Pitfalls

1. **Events as commands** — Events should be facts ("OrderCreated"), not commands ("ChargeCard"). Mixing them recreates tight coupling.
2. **No schema evolution plan** — Events live forever. Use Avro/Protobuf with versioning, not JSON freestyle.
3. **Forgetting idempotency** — At-least-once delivery means duplicates. Each consumer must handle them.
4. **Saga not actually idempotent** — A saga step that runs twice must produce the same result.
5. **Hidden dependencies** — Choreography hides the flow. Use distributed tracing (OpenTelemetry) to recover visibility.
6. **No DLQ / retry strategy** — Events that can't be processed fester. Always plan for poison messages.

---

## 🔗 Dig Deeper

- 📘 *Designing Data-Intensive Applications* — Chapter 11: Stream Processing
- 📘 [Microsoft: Saga Pattern](https://learn.microsoft.com/en-us/azure/architecture/reference-architectures/saga/saga)
- 📘 [Chris Richardson: Microservices Patterns — Saga chapter](https://microservices.io/patterns/data/saga.html)
- 📘 [Martin Fowler: Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
- 📺 [Temporal: Workflow Orchestration tutorials](https://temporal.io/)

---

← [Back to 5-min reads index](./README.md)
