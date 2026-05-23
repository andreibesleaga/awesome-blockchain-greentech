# Certification Supply-Chain — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **three-layer event-sourced architecture**:

1. **Edge Layer** — laser-marking stations, mobile/PWA scanners, IoT condition sensors, ERP/WMS adapters.
2. **Gateway / API Layer** — stateless services that authenticate, canonicalise, and forward signed events to the ledger.
3. **Ledger Layer** — a permissioned core (Hyperledger Fabric or similar) that holds the authoritative event log and token state, anchored daily to a public EVM L2 for open consumer verification.

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

### 4.4 Daily public anchoring

```
00:10 UTC cron:
  events_prev_day = EventLog.range(00:00..23:59 previous day)
  root            = merkle(events_prev_day)
  PublicAnchor.commit(root, day) on EVM L2
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
* Optional ZK-Rollup of anchored proofs in a later phase to compress L2 gas costs.

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
* **Public layer:** Polygon zkEVM, Arbitrum, or VeChainThor (Solidity 0.8.x).
* **API gateway:** Go (Echo) or Node.js (Fastify); JOSE for JWS; DID-core libs.
* **Storage:** PostgreSQL materialised views; S3-compatible object store for blobs.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; cosign-signed container images.

## 12. Open Architecture Questions

* Public chain selection (Polygon vs. VeChainThor vs. Arbitrum) — driven by ecosystem reach vs. domain fit, subject to the SFC §2 platform matrix.
* Whether to expose the daily Merkle root as an OpenTimestamps proof in addition to the on-chain commit.
* Whether ERP adapters should write directly or via an outbox pattern in the participant's own systems.

## 13. SFC Compliance Profile

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Project pin: `sustainability-profile: SFC-PROFILE v1.1`.

| Criterion | How this project meets it |
|---|---|
| **1. Energy < 1 GWh / yr** | Hot path: Hyperledger Fabric on general-purpose servers, or VeChainThor (Authority masternodes — published low-energy footprint). Anchor: Polygon zkEVM. Combined budget well under the cap. |
| **2. Hardware lifecycle** | General-purpose x86 / arm64 only; ASICs forbidden. Every operator declares `nodeProfile` (purchasedAt, expectedRetireAt, reusePolicy). |
| **3. Carbon accountability** | Monthly `EnergyAttested` and `CarbonAttested` events per operator. Scope 2 from peer + gateway electricity weighted by Electricity Maps regional intensity; Scope 3 from amortised embodied hardware carbon. Offsets retired against the period; verifier enforces Net Zero. |
| **4. Regulatory readiness** | `/v1/sustainability/csrd` returns signed ESRS E1 JSON. CSRD reporting integrates with corporate ESG tools without PDF round-trips. |

**Measurement sources.** CCRI Sustainability API + Electricity Maps API + IEA emission factors (fallback). GHG Protocol Scopes 2 & 3 for boundary definition.

**Migration clause.** If the chosen platform's measured energy exceeds 1 GWh / yr in any 12-month window, the project migrates to another platform from [SFC_COMPLIANCE.md §2](../SFC_COMPLIANCE.md) within one reporting period.
