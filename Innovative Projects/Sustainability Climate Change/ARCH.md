# Sustainability Climate Change — Architecture (ARCH)

> Minimal architecture overview for the MRV-anchored carbon-credit registry described in [PRD.md](PRD.md). Companion to [README.md](README.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **permissioned consortium ledger** with three layers, optionally anchored to a public chain for external integrity verification:

1. **Edge Layer** — project gateways, MRV sensors, validator / verifier tools, buyer / auditor clients.
2. **Gateway / API Layer** — authenticates DIDs, validates submissions, canonicalises payloads, forwards events to the ledger.
3. **Permissioned Core Ledger** — Registry, Methodology, CreditRegistry, Dispute, Bridge, EventLog. Optional periodic anchor to a public EVM L2 for external integrity verification.

The system **integrates with** Hedera Guardian (open-source MRV / asset toolkit) and existing methodology bodies (Verra, Gold Standard, Puro) rather than replacing them.

## 2. Component Diagram (logical)

```
┌─────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐    │
│  │ Project    │ │ MRV        │ │ Verifier   │ │ Buyer / Auditor│    │
│  │ Gateway    │ │ Sensors    │ │ Client     │ │ Client         │    │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └────────┬───────┘    │
└────────┼──────────────┼──────────────┼─────────────────┼────────────┘
         │              │              │                 │
         ▼              ▼              ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       GATEWAY / API LAYER                            │
│  ┌────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ REST API   │ │ DID Auth +   │ │ Methodology  │ │ Oracle /     │  │
│  │ (W/R)      │ │ VC Verifier  │ │ Validator    │ │ Sensor Adapt │  │
│  └─────┬──────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘  │
└────────┼───────────────┼────────────────┼────────────────┼──────────┘
         │               │                │                │
         ▼               ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PERMISSIONED CONSORTIUM LEDGER                      │
│  ┌──────────┐ ┌────────────┐ ┌────────────────┐ ┌─────────┐ ┌─────┐ │
│  │ Registry │ │ Methodology│ │ CreditRegistry │ │ Dispute │ │Bridge│ │
│  └──────────┘ └────────────┘ └────────────────┘ └─────────┘ └─────┘ │
│  ┌──────────────────────────────────────────────────────┐           │
│  │   EventLog (append-only, signed, per-subject chain)   │           │
│  └──────────────────────────────────────────────────────┘           │
└────────────────────────────────┬────────────────────────────────────┘
                                 │  daily anchor (optional)
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PUBLIC ANCHOR LAYER (OPT)                      │
│        ┌───────────────┐               ┌────────────────────┐       │
│        │ PublicAnchor  │               │ Verifier libraries │       │
│        └───────────────┘               └────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘

                              OFF-CHAIN STORAGE
        ┌────────────────────────────────────────────────────────┐
        │  Methodology PDFs, MRV evidence (raw + processed),     │
        │  audit bundles, photos and remote-sensing imagery.     │
        │  IPFS / S3-compatible; encrypted where commercially    │
        │  sensitive; referenced on-chain by CID.                │
        └────────────────────────────────────────────────────────┘
```

## 3. Components (responsibilities)

| # | Component | Layer | Responsibility |
|---|---|---|---|
| C1 | Project Gateway | Edge | Builds project records and MRV submissions; signs on behalf of the project. |
| C2 | MRV Sensors | Edge | Capture measurements (in-situ or remote-sensed); sign where a secure element exists. |
| C3 | Verifier Client | Edge | Pulls MRV submissions, signs `Validated` / `Rejected` decisions. |
| C4 | Buyer / Auditor Client | Edge | Buys / retires credits; pulls audit bundles. |
| C5 | REST API | Gateway | JWS auth, rate-limit, canonicalisation. |
| C6 | DID Auth + VC Verifier | Gateway | Resolves DIDs against Registry; verifies role VCs. |
| C7 | Methodology Validator | Gateway | Static check that submitted payloads match the methodology parameters before chain submission. |
| C8 | Oracle / Sensor Adapter | Gateway | Verifies sensor signatures or trusted-gateway delegation. |
| C9 | Registry | Core | Participants, roles, key rotation, revocation. |
| C10 | Methodology | Core | Anchors methodology version hashes; immutable per version. |
| C11 | CreditRegistry | Core | Mint / transfer / retire CreditBatches; enforces invariants. |
| C12 | Dispute | Core | Locks credits during dispute; records resolution. |
| C13 | Bridge | Core | Burn / mint with proof-of-burn from source chain. |
| C14 | EventLog | Core | Append-only signed chain per subject. |
| C15 | Anchor Job | Core → Public (opt) | Builds and commits a daily Merkle root. |

## 4. Key Sequences

### 4.1 Methodology registration

```
Registry Operator ──sign──▶ API ──▶ Methodology.register(methodId, docHash, paramsHash)
                                       │
                                       └─▶ event MethodologyRegistered
```

### 4.2 Issue credits after validation

```
Project Gateway ──sign──▶ API ──▶ MRV.submit(evidenceCid, period)
                                       │
                                       └─▶ event MRVSubmitted

Verifier ──sign──▶ API ──▶ Verifier review
                              │
                              └─▶ event Validated (tCO2eClaimed)

Registry Operator ──sign──▶ API ──▶ CreditRegistry.issue(batchId, tCO2e, methodologyHash, mrvRefs)
                                       │
                                       └─▶ event Issued
```

### 4.3 Retire credits

```
Buyer ──sign──▶ API ──▶ CreditRegistry.retire(batchId, qty, beneficiary, scope, reportYear)
                              │
                              ├─▶ enforce: held qty >= qty AND status != disputed
                              └─▶ event Retired (immutable)
```

### 4.4 Cross-chain bridge

```
Holder ──sign──▶ API ──▶ Bridge.burn(batchId, qty, targetChain)
                              │
                              └─▶ event BridgeBurned (with burn proof)

Target-chain bridge contract ──verify burn proof──▶ mint target token

Reverse direction symmetric: BridgeMinted requires verified BridgeBurned on source chain.
```

### 4.5 Daily anchoring (optional)

```
00:10 UTC cron:
  events_prev_day = EventLog.range(00:00..23:59 previous day)
  root            = merkle(events_prev_day)
  PublicAnchor.commit(root, day) on EVM L2
```

## 5. Trust Boundaries

| Boundary | Trust assumption | Mitigation |
|---|---|---|
| Sensor ↔ Gateway | Sensor key may not be in a secure element. | TPM / SE preferred; otherwise trusted gateway signs and records the delegation. |
| Project ↔ Gateway | Project key in custody. | Registry-level revocation; per-period sub-keys. |
| Gateway ↔ Core | Gateway is thin verifier. | All authority signature-based. |
| Verifier ↔ Core | Verifier could mis-validate. | Verifier identity public; reputation tracked; Dispute path available. |
| Core ↔ Public | Consortium nodes could collude. | Optional daily anchor + open conformance tests. |
| Bridge ↔ other chains | Bridges are historical sources of attacks. | Require source-side burn proof; no minting without it; consider deferring bridges. |

## 6. Data Storage

| Data | Where | Notes |
|---|---|---|
| Event chain, contract state | Permissioned core | Authoritative. |
| Methodology PDFs and params | Off-chain (IPFS / S3) | Anchored by hash. |
| MRV raw evidence (sensor logs, imagery) | Off-chain | Anchored by CID; can be encrypted. |
| Daily Merkle roots | Public L2 (optional) | External integrity verification. |
| Buyer audit bundles | Generated on demand, optionally archived | Signed; reproducible from chain. |

## 7. Deployment View

* **Core nodes:** ≥ 4 operators (Registry Operator + recognised Verifier + neutral foundation + at least one buyer / auditor). BFT / Raft consensus.
* **Gateway:** stateless containers behind a regional LB; horizontal autoscale.
* **Anchor Job:** singleton cron with leader election (if hybrid mode used).
* **Observability:** OpenTelemetry traces, Prometheus metrics, signed audit logs to a regulator-accessible bucket.
* **Carbon footprint:** the system's own annual footprint MUST be reported (method named) and published as part of [PRD.md NFR-5](PRD.md).

## 8. Scalability and Performance

* **Throughput:** consortium ledger comfortably handles expected volumes; the bottleneck is MRV processing, not chain throughput.
* **Reads:** materialised views in the gateway; lineage walks served from cache.
* **Methodology updates:** new versions deploy via `MethodologyRegistered`; old credits stay bound to their issuance-time version.

## 9. Security and Privacy

* TLS 1.3 ingress; mTLS gateway ↔ core.
* No PII on-chain.
* Commercially sensitive evidence encrypted off-chain; access governed by VC presentation.
* Right-to-be-forgotten where applicable: purge off-chain personal data; on-chain pseudonymous events remain.

## 10. Failure Modes

| Failure | Effect | Recovery |
|---|---|---|
| MRV sensor compromise | Tampered measurements until detected. | Registry revocation; affected issuances flagged for re-validation. |
| Verifier mistake | Unjustified issuance. | Dispute path; credits locked; possible recall via `Disputed`. |
| Bridge contract bug on target chain | Unauthorised mint on the other side. | Local registry refuses re-import; reconciliation report published. |
| Anchor missed (if hybrid) | No public root for a day. | Catch-up commit. |
| Off-chain store outage | Evidence temporarily unreadable. | Multi-region replication; verify endpoint returns `evidence-unavailable`. |

## 11. Build / Tech Choices (indicative)

* **Permissioned core:** Hyperledger Fabric 2.x (Go chaincode) or Hedera (HCS + smart contracts with Guardian for methodology workflows).
* **Methodology engine:** Hedera Guardian (where ecosystem fit) or custom workflow service on Fabric.
* **API gateway:** Go (Echo) or Node.js (Fastify); JOSE for JWS; DID-core libs.
* **Storage:** PostgreSQL materialised views; S3-compatible blob store; IPFS pinning for public artefacts.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; cosign-signed images.

## 12. Open Architecture Questions

* Fabric vs Hedera Guardian as the primary core (each subject to the platform case of SFC profile 2.0).
* Whether to integrate the Bridge at all in Phase 1, or defer until reliable cross-chain proof patterns are battle-tested for credits.
* Public anchor: always-on vs. opt-in per Operator.
* Whether biodiversity credits get a separate contract from carbon credits (likely yes — different invariants).

## 13. SFC Compliance Profile (self-applied)

SFC: this design follows [SFC profile 2.0](../SFC_COMPLIANCE.md). Framework: Besleaga, A. N. "'Sustainability-First Consensus' Ledgers for a Green Digital Future", *Communications of the ACM*, Opinion, in press, [doi:10.1145/3809296](https://doi.org/10.1145/3809296). The profile holds the rules and checks; this section holds the project facts only. Self-application matters here above all other projects: a registry that issues green claims while burning energy itself would be incoherent.

| Project fact | This design |
|---|---|
| **Hot path and platform case** | Permissioned: Hyperledger Fabric (Raft ordering, mechanism crash-fault-tolerant; a BFT ordering service would name bft), run only by the registered operators. Platform case: the network's own ledger figure. The alternative, Hedera (aBFT) with Guardian for methodology workflows, would be a public hot path and would need a public assessment below 1 GWh on the profile's boundary; the vendor [states it is carbon-negative](https://hedera.com/blog/going-carbon-negative-at-hedera-hashgraph) through purchased offsets, which is not an energy measurement. |
| **Attesting operators** | The registry operator, a recognised verifier, the neutral foundation and at least one buyer or auditor, each attesting its own energy and carbon. |
| **Node count and registered-node bound** | At least 4 operators (BFT / Raft). The maximum node count is fixed in the methodology document. Example: 4 nodes → 4 × 1 976.4 = 7 905.6 kWh. Registered-node bound, to be met before the first full year: N × P × O × 8 784 h / 1 000 < 1 000 000 kWh, where P = rated power in watts of the worst hardware class in use, N = greatest number of nodes the registered operators may run (gateways and adapter nodes inside the C1 boundary included) and O = data-centre overhead factor, which has no default. With an assumed 150 W per node and an assumed overhead factor of 1.5 (both assumptions, to be fixed in the methodology document), each node adds 1 976.4 kWh, so the bound stays below the cap up to 505 nodes. |
| **Hardware** | General-purpose x86 / arm64 only; no ASICs. Each operator declares its hardware in its Registry entry, with a reuse and WEEE-certified retirement policy. |
| **Scope 1** | None, stated in the methodology document. |
| **Scope 2** | Market-based (the declared figure); location-based optional, using Electricity Maps regional intensity with IEA emission factors as fallback. |
| **Scope 3** | Categories named in the methodology document, including the embodied carbon of the hardware. |
| **Offset coverage** | Offset coverage, checked: every month each operator's retired credits are compared with its gross emissions. This is not a net-zero or neutrality claim. |
| **Anchor** | Optional and informative only; to be chosen per deployment (a public chain that is not proof-of-work). |
| **Project-specific rules** | Breach flag: the verifier publicly flags a breach of the energy cap the moment it is detected, not at the end of the period. Offsets are retired preferably through `Retired` events on this registry, so each claimed offset is a `CreditBatch` with a full MRV chain. The system's own annual footprint is published in every audit bundle. |
