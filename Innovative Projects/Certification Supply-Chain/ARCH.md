# Certification Supply-Chain — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **three-layer event-sourced architecture**:

1. **Edge Layer** — laser-marking stations, mobile/PWA scanners, IoT condition sensors, ERP/WMS adapters.
2. **Gateway / API Layer** — stateless services that authenticate, canonicalise, and forward signed events to the ledger.
3. **Ledger Layer** — a permissioned core (Hyperledger Fabric or similar) that holds the authoritative event log and token state, with optional daily anchoring (SFC profile 2.0, Appendix E.2) to a public chain that is not proof-of-work, for open consumer verification.

Trust is **signature-based end-to-end**: an event is only valid if signed by a key the Registry recognises for that action on that subject.

## 2. Component Diagram (logical)

```
┌─────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                              │
│  ┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐  │
│  │ Laser Mark │ │ Mobile   │ │ IoT      │ │ Trusted  │ │ ERP /   │  │
│  │ Station    │ │ Scanner  │ │ Sensors  │ │ Gateway  │ │ WMS     │  │
│  └─────┬──────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬────┘  │
└────────┼─────────────┼────────────┼────────────┼────────────┼───────┘
         │             │            │            │            │
         ▼             ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          GATEWAY / API LAYER                         │
│  ┌────────────┐ ┌───────────┐ ┌──────────┐ ┌───────────────────┐    │
│  │ REST API   │ │ DID Auth  │ │ Oracle   │ │ Verify Portal API │    │
│  │ (W/R)      │ │ / JWS     │ │ Adapter  │ │ (cached reads)    │    │
│  └─────┬──────┘ └─────┬─────┘ └────┬─────┘ └────────┬──────────┘    │
└────────┼──────────────┼────────────┼────────────────┼───────────────┘
         │              │            │                │
         ▼              ▼            ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PERMISSIONED CORE LEDGER                       │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌─────────┐  │
│  │ Registry │ │ ItemNFT  │ │ Batch1155  │ │ CertReg  │ │ EventLog│  │
│  └──────────┘ └──────────┘ └────────────┘ └──────────┘ └─────────┘  │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │  daily Merkle root
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PUBLIC PROOF LAYER  (EVM L2)                     │
│        ┌───────────────┐               ┌────────────────────┐       │
│        │ PublicAnchor  │               │ Verifier libraries │       │
│        └───────────────┘               └────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘

                          OFF-CHAIN STORAGE
        ┌───────────────────────────────────────────────────────┐
        │ IPFS / S3 — VCs, photos, sensor blobs, audit reports  │
        └───────────────────────────────────────────────────────┘
```

## 3. Components (responsibilities)

| # | Component | Layer | Responsibility |
|---|---|---|---|
| C1 | Laser Mark Station | Edge | Engraves UID and Data Matrix on product/packaging; reports back the engraved hash. |
| C2 | Mobile Scanner | Edge | Reads UID, builds and signs scan events; works offline (queue + replay). |
| C3 | IoT Sensors | Edge | Capture temperature, humidity, geolocation; sign if a secure element is present. |
| C4 | Trusted Gateway | Edge | Signs on behalf of sensors without secure elements; records the delegation explicitly. |
| C5 | ERP/WMS Adapter | Edge | Bridges existing business events (PO, ASN, GR) into the event vocabulary. |
| C6 | API Gateway | Gateway | Validates JWS, rate-limits, canonicalises payloads (RFC 8785). |
| C7 | DID Auth | Gateway | Resolves participant DIDs against the Registry; checks roles. |
| C8 | Oracle Adapter | Gateway | Verifies sensor / gateway signatures and tags the event with provenance metadata. |
| C9 | Verify Portal API | Gateway | Cached read-through; returns verdict + chain in < 1 s p95. |
| C10 | Registry | Core | Participants, roles, key rotation, revocation. |
| C11 | Token contracts | Core | ItemNFT and Batch1155 with mint / transfer / split / merge logic. |
| C12 | CertRegistry | Core | Anchors VC hashes; tracks active vs. revoked certifications. |
| C13 | EventLog | Core | Append-only per-subject chain; signature checks on every append. |
| C14 | Anchor Job | Core → Public | Builds and commits a daily Merkle root. |
| C15 | PublicAnchor | Public | Stores `(day, root)` tuples readable by anyone. |

## 4. Key Sequences

### 4.1 Mint and attach certification

```
Producer ERP ──sign──▶ API ──▶ ItemNFT.mint(uid) ──▶ EventLog (Minted)
Certifier   ──sign──▶ API ──▶ CertRegistry.anchor(vcHash) ──▶ EventLog (CertificationAttached)
```

### 4.2 Transport scan with condition data

```
IoT sensor (signed) ──▶ Trusted Gateway (if needed) ──▶ OracleAdapter
                                              │
                                              └─▶ EventLog (ConditionReported)
                                                   │
                                                   └─▶ Off-chain Worker
                                                         │
                                                         ├─ if tempC > threshold → Alert (email/SMS)
                                                         └─ if rule(period, perf) → Reward payout
```

### 4.3 Consumer verify

```
Scan UID ──▶ Verify Portal ──▶ resolve tokenId
                                │
                                ├─ fetch state from Core
                                ├─ walk EventLog, verify every signature
                                ├─ check all certifications still active
                                └─ return verdict + summary (< 1 s p95)
```

### 4.4 Daily public anchoring (optional)

Optional and informative only (SFC profile 2.0, Appendix E.2); chosen per deployment.

```
00:10 UTC cron:
  events_prev_day = EventLog.range(00:00..23:59 previous day)
  root            = merkle(events_prev_day)
  PublicAnchor.commit(root, day) on the chosen public chain, if anchoring is enabled
```

## 5. Trust Boundaries

| Boundary | Trust assumption | Mitigation |
|---|---|---|
| Sensor ↔ Gateway | Sensor key may not be in a secure element. | Either hold key in TPM / SE, or delegate to a trusted gateway and record the delegation. |
| Edge ↔ Gateway | Edge devices may be lost or compromised. | DID-based auth; per-actor revocation; rate limiting. |
| Gateway ↔ Core | Gateway is a thin verifier. | All authority is signature-based; gateway cannot forge events. |
| Core ↔ Public | Consortium nodes could collude. | Daily Merkle anchor + open conformance tests make tampering detectable. |
| Certifier ↔ Core | Certifier could issue an unjustified VC. | VC content is open to audit; revocation is on-chain; reputation tracked off-chain. |

## 6. Data Storage

| Data | Where | Notes |
|---|---|---|
| Event chain, token state | Permissioned core | Authoritative. |
| Daily Merkle roots | Public L2 | Externally verifiable. |
| Verifiable Credentials, photos, audit reports | IPFS / S3 | Referenced on-chain by CID. |
| Participant directory | Permissioned core (Registry) | DIDs, roles, revocation lists. |

## 7. Deployment View

* **Core nodes:** ≥ 4 operators across the consortium (producers + certifier + neutral foundation). Raft / BFT consensus.
* **Gateway:** stateless containers behind a regional load balancer; horizontal autoscale.
* **Anchor Job:** singleton cron with leader election; idempotent.
* **Verify portal:** static front-end + cached read API behind a CDN to hit NFR-2.
* **Observability:** OpenTelemetry traces, Prometheus metrics, signed audit logs to a regulator-accessible bucket.

## 8. Scalability and Performance

* Throughput targeted via batching of low-value commodity events under `BatchToken`.
* Reads served from materialised views in the gateway, not by replaying the chain.
* Optional ZK-Rollup of anchored proofs in a later phase, if anchoring is enabled, to compress L2 gas costs.

## 9. Security and Privacy

* TLS 1.3 ingress; mTLS gateway ↔ core.
* No PII on-chain; consumer scans are pseudonymous.
* Off-chain blobs encrypted at rest; access governed by VC presentation.
* Right-to-be-forgotten implemented by purging the off-chain record; on-chain references degrade to opaque hashes.

## 10. Failure Modes

| Failure | Effect | Recovery |
|---|---|---|
| Anchor job missed | No public root for a day. | Catch-up commit; verifiers tolerate gaps with `MissingDay` markers. |
| Sensor compromised | Forged readings until detected. | Registry revocation; anomaly detector flags spikes. |
| Core node loss | Reduced fault tolerance window. | Add replacement node; resync from peers. |
| Public L2 outage | Verifier UX degraded. | Cache last good root; show staleness banner. |
| Producer loses key | Cannot sign mints. | Pre-published `KeyRotated` VC pre-authorises a backup key. |

## 11. Build / Tech Choices (indicative)

* **Permissioned core:** Hyperledger Fabric 2.x (Go chaincode).
* **Public layer:** Arbitrum, another public chain that is not proof-of-work, or VeChainThor (Solidity 0.8.x).
* **API gateway:** Go (Echo) or Node.js (Fastify); JOSE for JWS; DID-core libs.
* **Storage:** PostgreSQL materialised views; S3-compatible object store for blobs.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; cosign-signed container images.

## 12. Open Architecture Questions

* Public chain selection (Polygon PoS vs. VeChainThor vs. Arbitrum) — driven by ecosystem reach vs. domain fit, subject to the platform case of SFC profile 2.0.
* Whether to expose the daily Merkle root as an OpenTimestamps proof in addition to the on-chain commit. *(Note: OpenTimestamps commits to Bitcoin, a proof-of-work chain, so it falls outside the profile's anchor option (Appendix E.2: a public chain that is not proof-of-work); the daily fingerprint goes to an anchor chosen per deployment on such a chain.)*
* Whether ERP adapters should write directly or via an outbox pattern in the participant's own systems.

## 13. SFC Compliance Profile

SFC: this design follows [SFC profile 2.0](../SFC_COMPLIANCE.md). Framework: Besleaga, A. N. "'Sustainability-First Consensus' Ledgers for a Green Digital Future", *Communications of the ACM*, Opinion, in press, [doi:10.1145/3809296](https://doi.org/10.1145/3809296). The profile holds the rules and checks; this section holds the project facts only.

| Project fact | This design |
|---|---|
| **Hot path and platform case** | Permissioned: Hyperledger Fabric on general-purpose servers, run only by the registered consortium operators. Platform case: the network's own ledger figure (the operators' attested energy sums to less than 1 GWh). The alternative, VeChainThor (Authority masternodes), would be a public hot path and would need a public assessment below 1 GWh on the profile's boundary; its footprint is still to be confirmed from an independent source. |
| **Attesting operators** | Consortium members: producers, certifier and neutral foundation, each running core nodes and attesting its own energy and carbon. |
| **Node count and registered-node bound** | At least 4 operators in the consortium (Raft / BFT). The maximum node count is fixed in the methodology document. Example: 4 nodes → 4 × 1 976.4 = 7 905.6 kWh. Registered-node bound, to be met before the first full year: N × P × O × 8 784 h / 1 000 < 1 000 000 kWh, where P = rated power in watts of the worst hardware class in use, N = greatest number of nodes the registered operators may run (gateways and adapter nodes inside the C1 boundary included) and O = data-centre overhead factor, which has no default. With an assumed 150 W per node and an assumed overhead factor of 1.5 (both assumptions, to be fixed in the methodology document), each node adds 1 976.4 kWh, so the bound stays below the cap up to 505 nodes. |
| **Hardware** | General-purpose x86 / arm64 only; no ASICs. Every operator declares its hardware in its Registry entry (purchase date, planned retirement date, reuse policy). |
| **Scope 1** | None, stated in the methodology document. |
| **Scope 2** | Market-based (the declared figure); location-based optional, using Electricity Maps regional intensity with IEA emission factors as fallback. Electricity of peers and gateways. |
| **Scope 3** | Categories named in the methodology document, including the embodied carbon of the hardware. |
| **Offset coverage** | Offset coverage, checked: every month each operator's retired credits are compared with its gross emissions. This is not a net-zero or neutrality claim. |
| **Anchor** | Optional and informative only; to be chosen per deployment (a public chain that is not proof-of-work). |
