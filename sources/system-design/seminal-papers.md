# 📄 Seminal Papers in Distributed Systems

> The reading list of foundational research papers that shaped modern distributed systems. Most are surprisingly readable. **Read at least 5 in your career.**

> 💡 Bookmark **[papers-we-love/papers-we-love](https://github.com/papers-we-love/papers-we-love)** (~92K stars) — comprehensive curation with PDFs and discussion notes.

---

## ⭐ How to Read a Distributed Systems Paper

1. **First pass (15 min):** Abstract → Introduction → Conclusion. What's the problem? What's the contribution?
2. **Second pass (1-2 hours):** Read figures, key sections. Skip proofs first time.
3. **Third pass (multi-day):** Re-derive the proofs/protocols yourself.
4. **Discuss:** A paper-reading group (or LLM partner!) doubles retention.

📘 Reference: [How to Read a Paper — Keshav](https://web.stanford.edu/class/ee384m/Handouts/HowtoReadPaper.pdf)

---

## 🏛️ Tier S: The Foundational Papers (READ THESE)

### 1. Time, Clocks, and the Ordering of Events in a Distributed System
- **Author:** Leslie Lamport, 1978
- **URL:** https://amturing.acm.org/p558-lamport.pdf
- **Why ★★★★★:** Defined "happened-before" relation; introduced logical clocks; the foundation of all distributed reasoning
- **Read it:** Phase 3 — start of distributed systems study

### 2. Impossibility of Distributed Consensus with One Faulty Process (FLP)
- **Authors:** Fischer, Lynch, Paterson, 1985
- **URL:** https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf
- **Why ★★★★★:** Proved that no deterministic algorithm can guarantee consensus in async systems with one faulty node
- **Implication:** All real systems make trade-offs around this — Raft/Paxos use timeouts (introducing partial synchrony)

### 3. End-to-End Arguments in System Design
- **Authors:** Saltzer, Reed, Clark, 1984
- **URL:** https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf
- **Why ★★★★:** Why correctness checks belong at endpoints, not in the network
- **Influence:** Shapes how we think about TCP, microservices, networking

### 4. CAP Theorem (Brewer 2000 keynote → Gilbert & Lynch 2002 proof)
- **URL (proof):** https://www.glassbeam.com/sites/all/themes/glassbeam/images/blog/10.1.1.67.6951.pdf
- **Why ★★★★★:** Defined the trade-off between consistency, availability, and partition tolerance
- **Note:** Read the PACELC formulation (Abadi 2010) too: when there's NO partition, you still trade Latency vs Consistency — http://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf

---

## 🤝 Tier S: Consensus

### 5. Paxos Made Simple
- **Author:** Leslie Lamport, 2001
- **URL:** https://lamport.azurewebsites.net/pubs/paxos-simple.pdf
- **Why ★★★★★:** The "easier" version of his original "The Part-Time Parliament" paper
- **Note:** Still hard. Worth re-reading multiple times.

### 6. In Search of an Understandable Consensus Algorithm (Raft)
- **Authors:** Ongaro & Ousterhout, 2014
- **URL:** https://raft.github.io/raft.pdf
- **Why ★★★★★:** Designed for understandability; the modern standard. etcd, Consul, CockroachDB, MongoDB all use Raft variants
- **Companion:** [raft.github.io](https://raft.github.io/) — interactive visualization
- **Action:** Implement it (MIT 6.824 Lab 2)

### 7. ZooKeeper: Wait-free Coordination for Internet-scale Systems
- **Authors:** Hunt et al., USENIX 2010
- **URL:** https://www.usenix.org/conference/usenix-atc-10/zookeeper-wait-free-coordination-internet-scale-systems
- **Why ★★★★:** ZAB protocol; ZooKeeper underpins HBase, Kafka (originally), Hadoop ecosystem

### 8. The Chubby Lock Service for Loosely-Coupled Distributed Systems
- **Author:** Mike Burrows (Google), OSDI 2006
- **URL:** https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/
- **Why ★★★★:** Inspired ZooKeeper; teaches you what coordination services actually look like in production

### 9. Practical Byzantine Fault Tolerance (PBFT)
- **Authors:** Castro & Liskov, OSDI 1999
- **URL:** https://pmg.csail.mit.edu/papers/osdi99.pdf
- **Why ★★★★:** Foundation of Byzantine consensus (used in blockchains)

---

## 💾 Tier A: Storage Systems

### 10. The Google File System (GFS)
- **Authors:** Ghemawat, Gobioff, Leung, SOSP 2003
- **URL:** https://research.google/pubs/the-google-file-system/
- **Why ★★★★★:** The paper that started "big data." Inspired HDFS.
- **Key idea:** Master + chunkservers; large append-only files; commodity hardware

### 11. MapReduce: Simplified Data Processing on Large Clusters
- **Authors:** Dean & Ghemawat, OSDI 2004
- **URL:** https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/
- **Why ★★★★★:** Inspired Hadoop. Showed parallel programming model that scales

### 12. Bigtable: A Distributed Storage System for Structured Data
- **Authors:** Chang et al., OSDI 2006
- **URL:** https://research.google/pubs/bigtable-a-distributed-storage-system-for-structured-data-2/
- **Why ★★★★★:** Inspired HBase, Cassandra, Apache Accumulo, AWS DynamoDB
- **Key idea:** SSTable + LSM-tree; key-value with column families

### 13. Dynamo: Amazon's Highly Available Key-value Store
- **Authors:** DeCandia et al., SOSP 2007
- **URL:** https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf
- **Why ★★★★★:** Leaderless replication, consistent hashing, vector clocks, hinted handoff
- **Influence:** Cassandra, Riak, Voldemort all derived from Dynamo concepts

### 14. Spanner: Google's Globally Distributed Database
- **Authors:** Corbett et al., OSDI 2012
- **URL:** https://research.google/pubs/spanner-googles-globally-distributed-database/
- **Why ★★★★★:** External consistency at global scale. Introduced TrueTime.
- **Influence:** CockroachDB, YugabyteDB, FoundationDB

### 15. F1: A Distributed SQL Database That Scales
- **Authors:** Shute et al., VLDB 2013
- **URL:** https://research.google/pubs/f1-a-distributed-sql-database-that-scales/
- **Why ★★★★:** Built on top of Spanner; replaces sharded MySQL for AdWords

### 16. The Log-Structured Merge-Tree (LSM-Tree)
- **Authors:** O'Neil et al., 1996
- **URL:** https://www.cs.umb.edu/~poneil/lsmtree.pdf
- **Why ★★★★★:** The data structure behind RocksDB, Cassandra, HBase, Bigtable

### 17. The Dataflow Model
- **Authors:** Akidau et al., VLDB 2015
- **URL:** https://research.google/pubs/the-dataflow-model-a-practical-approach-to-balancing-correctness-latency-and-cost-in-massive-scale-unbounded-out-of-order-data-processing/
- **Why ★★★★:** Foundation for Apache Beam; how to think about batch + streaming together

---

## 📡 Tier A: Streaming & Logs

### 18. Kafka: a Distributed Messaging System for Log Processing
- **Authors:** Kreps et al., LinkedIn, NetDB 2011
- **URL:** https://notes.stephenholiday.com/Kafka.pdf
- **Why ★★★★★:** The original Kafka paper

### 19. The Log: What every software engineer should know about real-time data's unifying abstraction
- **Author:** Jay Kreps (LinkedIn / Confluent), 2013
- **URL:** https://engineering.linkedin.com/distributed-systems/log-what-every-software-engineer-should-know-about-real-time-datas-unifying
- **Why ★★★★★:** Mind-expanding essay about the role of the log in distributed systems

### 20. Millwheel: Fault-Tolerant Stream Processing at Internet Scale
- **Authors:** Akidau et al., Google, VLDB 2013
- **URL:** https://research.google/pubs/millwheel-fault-tolerant-stream-processing-at-internet-scale/

---

## 🔍 Tier A: Observability & Operations

### 21. Dapper: A Large-Scale Distributed Systems Tracing Infrastructure
- **Authors:** Sigelman et al., Google, 2010
- **URL:** https://research.google/pubs/dapper-a-large-scale-distributed-systems-tracing-infrastructure/
- **Why ★★★★★:** Foundation of Zipkin, Jaeger, OpenTelemetry

### 22. Borg: Large-scale cluster management at Google
- **Authors:** Verma et al., EuroSys 2015
- **URL:** https://research.google/pubs/large-scale-cluster-management-at-google-with-borg/
- **Why ★★★★★:** The system that became Kubernetes (which is "Borg7" rewrite open-sourced)

### 23. Omega: flexible, scalable schedulers for large compute clusters
- **Authors:** Schwarzkopf et al., Google, EuroSys 2013
- **Why ★★★:** Borg's successor concept; influenced k8s scheduler

---

## 🧮 Tier B: Specialized but Influential

### 24. Lamport — The Part-Time Parliament (Paxos)
- **URL:** https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf
- **Why:** The original Paxos. Famously hard. Read "Paxos Made Simple" first

### 25. Raft Refloated: Do We Have Consensus?
- **URL:** https://www.cl.cam.ac.uk/~ms705/pub/papers/2015-osr-raft.pdf
- **Why:** Reproduces Raft, surfaces hidden assumptions

### 26. CRDTs: Conflict-Free Replicated Data Types
- **Authors:** Shapiro et al., 2011
- **URL:** https://hal.inria.fr/inria-00609399v1/document
- **Why ★★★★:** Foundation of collaborative apps (Google Docs, Figma, Yjs, Automerge)

### 27. Calvin: Fast Distributed Transactions for Partitioned Database Systems
- **Authors:** Thomson et al., SIGMOD 2012
- **URL:** https://cs.yale.edu/homes/thomson/publications/calvin-sigmod12.pdf
- **Why:** Foundation of FaunaDB; alternative to 2PC

### 28. Naiad: A Timely Dataflow System
- **Authors:** Murray et al., SOSP 2013
- **URL:** https://www.microsoft.com/en-us/research/publication/naiad-a-timely-dataflow-system/
- **Why:** Cyclic dataflows; iterative + real-time analytics

### 29. Highly Available Transactions: Virtues and Limitations
- **Authors:** Bailis et al., VLDB 2014
- **URL:** http://www.bailis.org/papers/hat-vldb2014.pdf
- **Why ★★★★:** Which transactions can be implemented under high availability?

### 30. Coordination Avoidance in Database Systems
- **Authors:** Bailis et al., VLDB 2015
- **URL:** http://www.bailis.org/papers/ramp-sigmod2014.pdf
- **Why ★★★★:** When coordination is and isn't needed; foundation of CRDTs in databases

### 31. Spark: Cluster Computing with Working Sets
- **Authors:** Zaharia et al., HotCloud 2010
- **URL:** https://www.usenix.org/legacy/event/hotcloud10/tech/full_papers/Zaharia.pdf
- **Why:** RDD abstraction; in-memory MapReduce

### 32. Cassandra — A Decentralized Structured Storage System
- **Authors:** Lakshman & Malik (Facebook), SIGOPS 2010
- **URL:** https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf
- **Why ★★★★:** Hybrid of Dynamo + Bigtable

### 33. The TAO Paper — Facebook's Distributed Data Store for the Social Graph
- **Authors:** Bronson et al., USENIX ATC 2013
- **URL:** https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson
- **Why ★★★★:** How Facebook stores the social graph

### 34. Scaling Memcache at Facebook
- **Authors:** Nishtala et al., NSDI 2013
- **URL:** https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala
- **Why ★★★★★:** Caching at Facebook scale; teaches lease + thundering herd techniques

### 35. Photon: Fault-tolerant and Scalable Joining of Continuous Data Streams
- **Authors:** Ananthanarayanan et al., Google, SIGMOD 2013
- **Why ★★★:** Joining streams; Google's ad system

---

## 🔮 Tier B: Modern (Last Decade) Worth Reading

### 36. The Many Faces of Consistency
- **Author:** Marc Brooker, 2014
- **URL:** http://brooker.co.za/blog/2014/05/15/many-faces.html
- **Why:** Clear modern survey

### 37. Highly Available Consistency, Replication and Distributed Transactions in Cosmos DB
- **Authors:** Microsoft Research
- **Why:** Multiple consistency levels in production

### 38. Magic Pocket: Building a Multi-Exabyte Storage System (Dropbox)
- **URL:** https://dropbox.tech/infrastructure/magic-pocket-infrastructure
- **Why ★★★★:** Real-world exabyte-scale architecture

### 39. ScyllaDB papers
- **URL:** https://www.scylladb.com/resources/research/
- **Why:** Modern engineering; shard-per-core architecture

### 40. Discord: How we scaled to trillions of messages
- **URL:** https://discord.com/blog/how-discord-stores-trillions-of-messages
- **Why:** Iterative scaling story (MongoDB → Cassandra → ScyllaDB)

---

## 📅 Suggested Reading Schedule (1 paper / week for a year)

### Months 1-2: Foundations
1. Lamport — Time, Clocks
2. FLP Impossibility
3. End-to-End Arguments
4. Paxos Made Simple
5. CAP Theorem (Gilbert & Lynch)
6. PACELC (Abadi)
7. Raft
8. ZooKeeper
9. Chubby

### Months 3-4: Storage Systems
10. GFS
11. MapReduce
12. Bigtable
13. Dynamo
14. LSM-Tree (O'Neil)
15. Cassandra
16. Spanner
17. F1

### Months 5-6: Streaming & Operations
18. Kafka
19. The Log essay (Kreps)
20. Millwheel
21. Dataflow
22. Dapper
23. Borg

### Months 7-8: Modern Topics
24. CRDTs (Shapiro)
25. Calvin
26. Highly Available Transactions
27. Coordination Avoidance
28. Scaling Memcache at Facebook
29. TAO

### Months 9-10: Engineering Blogs Deep Dives
30-35. Discord, Stripe, Dropbox, Cloudflare, Slack, Netflix architecture deep-dives

### Months 11-12: Pick Your Specialty
- Streaming → Naiad, Photon, Spark
- Concurrency → Calvin, FaunaDB, FoundationDB
- Networks → BBR (Google), QUIC papers
- Storage → ScyllaDB, TigerBeetle, FoundationDB

---

## 💡 Tips for Paper-Reading Discipline

1. **Pick a fixed time** — e.g., Saturday mornings, 9-11 AM
2. **Read with a partner** — discuss to retain
3. **Take notes** — your future self will thank you
4. **Implement** when you can — Raft is the canonical "implement it to truly understand it"
5. **Revisit annually** — papers you found impenetrable will become accessible after building production systems

---

## 🌐 Where Papers Live

- **[papers-we-love/papers-we-love](https://github.com/papers-we-love/papers-we-love)** — community-curated repo
- **[research.google/pubs/](https://research.google/pubs/)** — Google research
- **[research.facebook.com/publications](https://research.facebook.com/publications/)** — Meta research
- **[microsoft.com/en-us/research/publications/](https://www.microsoft.com/en-us/research/publications/)** — Microsoft research
- **[USENIX](https://www.usenix.org/conferences)** — best systems conference proceedings (free!)
- **[SOSP, OSDI, NSDI](https://www.usenix.org/conferences)** — top systems conferences
- **[VLDB, SIGMOD](https://dblp.org/db/conf/vldb/index.html)** — top database conferences

---

← [Back to System Design home](./README.md)
