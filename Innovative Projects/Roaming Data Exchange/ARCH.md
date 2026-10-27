# Roaming Data Exchange — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **consortium identity + settlement layer** that sits between Home Operators, Foreign Operators, and the existing standards (OCPI / OCPP / GSMA). The ledger holds:

* the **Registry** of Operators,
* **pair agreements** (tariffs, fair-use, dispute window, bond),
* **bonds** posted by Operators,
* **session events** and **settlements**.

Identity is W3C SSI (DIDs + VCs); the user wallet talks to Foreign Operators via short-lived, selective-disclosure proofs.

## 2. Component Diagram (logical)

```
┌─────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                              │
│  ┌────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ User       │ │ Foreign      │ │ Home         │ │ Regulator /  │  │
│  │ Wallet     │ │ Operator     │ │ Operator     │ │ Auditor      │  │
│  │ (DID + VC) │ │ (CPO / VPMN) │ │ (eMSP / MNO) │ │ Client       │  │
│  └─────┬──────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘  │
└────────┼───────────────┼────────────────┼────────────────┼──────────┘
         │               │                │                │
         ▼               ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       GATEWAY / API LAYER                            │
│  ┌────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │ REST API   │ │ OCPI Access  │ │ GSMA / IPX   │ │ ZK / SD-JWT  │  │
│  │ (W/R)      │ │ Point        │ │ Adapter      │ │ Verifier     │  │
│  └─────┬──────┘ └──────┬───────┘ └──────┬───────┘ └──────┬───────┘  │
└────────┼───────────────┼────────────────┼────────────────┼──────────┘
         │               │                │                │
         ▼               ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PERMISSIONED CONSORTIUM LEDGER                      │
│  ┌──────────┐ ┌─────────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐  │
│  │ Registry │ │ PairAgreement│ │ BondVault│ │ Session │ │ Settle  │  │
│  └──────────┘ └─────────────┘ └──────────┘ └─────────┘ └─────────┘  │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │ optional: daily anchor
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PUBLIC ANCHOR (OPTIONAL, EVM L2)                        │
│        ┌───────────────┐               ┌────────────────────┐       │
│        │ PublicAnchor  │               │ Verifier libraries │       │
│        └───────────────┘               └────────────────────┘       │
└─────────────────────────────────────────────────────────────────────┘
```

## 3. Components (responsibilities)

| # | Component | Layer | Responsibility |
|---|---|---|---|
| C1 | User Wallet | Edge | Holds DID and Home Operator VC; generates ZK / SD-JWT presentations. |
| C2 | Foreign Operator | Edge | Asks the gateway to authorise; runs the physical service; submits session records. |
| C3 | Home Operator | Edge | Issues / rotates / revokes user VCs; posts bonds; receives settlement records. |
| C4 | Regulator / Auditor Client | Edge | Pulls signed bundles; runs ZK-proof audits where applicable. |
| C5 | REST API | Gateway | JWS auth, rate-limit, canonicalisation. |
| C6 | OCPI Access Point | Gateway | Speaks OCPI 2.2+ both ways; maps OCPI `Session` / `CDR` ↔ ledger events. |
| C7 | GSMA / IPX Adapter | Gateway | Maps telecom session records / settlement files to / from the ledger. |
| C8 | ZK / SD-JWT Verifier | Gateway | Verifies presentation proofs; tracks nonces. |
| C9 | Registry | Core | Operators, roles, key rotation, revocation. |
| C10 | PairAgreement | Core | Bilateral tariffs / fair-use / dispute windows / bond requirements. |
| C11 | BondVault | Core | Holds Operator bonds; per-session reserve / release. |
| C12 | Session | Core | Lifecycle events; single-active-session invariant. |
| C13 | Settlement | Core | Post-dispute-window finalisation; emits `Settled`. |
| C14 | Anchor Job | Core → Public (opt) | Daily Merkle root for external integrity verification. |

## 4. Key Sequences

### 4.1 EV roaming session

```
Driver Wallet ──present SD-JWT VC──▶ Foreign CPO
                                       │
                                       └──▶ Gateway /v1/access
                                              │
                                              ├─▶ ZK Verifier validates proof
                                              ├─▶ Registry checks issuer DID
                                              ├─▶ BondVault.reserve(homeOp, maxCost)
                                              └─▶ event AccessGranted (≤ 2 s p95)

CPO ──OCPP RemoteStartTransaction──▶ Charge Point
Charge Point ──OCPP MeterValues──▶ CPO

CPO ──/v1/sessions/{id}/end──▶ Session.close()
                                       │
                                       └─▶ event SessionEnded (with OCPI CDR pointer)
                                              │
                                              └─▶ after dispute window
                                                    └─▶ Settlement.finalise()
                                                          └─▶ event Settled
                                                                └─▶ BondVault.release()
```

### 4.2 Telecom roaming session

```
Subscriber UE attaches to VPMN
VPMN ──present user VC proof (held by HPMN-issued eSIM credential)──▶ Gateway /v1/access
   ... same authorisation + bond flow ...
VPMN ──periodic /v1/sessions/{id}/meter──▶ Session
VPMN ──/v1/sessions/{id}/end──▶ Session.close()
   ... settlement same as 4.1 ...
GSMA Adapter exports the session aggregate to the GSMA eBusiness Network for ecosystem-wide reconciliation.
```

### 4.3 Revocation propagation

```
Home Operator ──/v1/vcs/{id}/revoke──▶ Registry.revoke(vcId)
                                        │
                                        └─▶ event Revoked
                                              │
                                              └─▶ Foreign Operator wallets poll / subscribe; cache flush ≤ 5 s
```

## 5. Trust Boundaries

| Boundary | Trust assumption | Mitigation |
|---|---|---|
| User wallet ↔ Foreign Operator | Wallet may use a managed key. | DID-based auth; per-presentation nonce; revocation via Registry. |
| Foreign Operator ↔ Gateway | Operator signs requests; cannot forge user identity. | All authority is signature-based; pre-shared role VC. |
| Gateway ↔ Ledger | Gateway is a thin verifier. | All events signed; ledger checks against Registry. |
| Ledger ↔ Public Anchor | Consortium nodes could collude. | Optional daily anchor + open conformance tests. |
| Adapters ↔ External standards | OCPI / GSMA participants are trusted at the protocol level. | The adapter translates only; it does not endorse arbitrary claims. |

## 6. Data Storage

| Data | Where | Notes |
|---|---|---|
| Operators, roles, revocation | Permissioned core (Registry) | Authoritative. |
| Pair agreements, bonds | Permissioned core | Versioned per pair. |
| Session lifecycle, settlements | Permissioned core | Append-only, signed. |
| OCPI `CDR` / GSMA files | Off-chain object store | Referenced by CID. |
| User VCs and evidence blobs | Off-chain (operator-side) | Hash-anchored only. |
| Daily Merkle roots | Public L2 (optional) | External integrity verification. |

## 7. Deployment View

* **Core nodes:** ≥ 4 operators (mix of Home and Foreign Operators + neutral foundation). BFT / Raft consensus.
* **Gateway:** stateless containers behind a regional LB; horizontal autoscale.
* **OCPI Access Point:** at least one per region; uses standard OCPI endpoints alongside the DLT view.
* **GSMA Adapter:** runs as a peer in the GSMA eBusiness Network (Fabric) plus a worker that mirrors settlement state into the consortium ledger.
* **Anchor Job:** singleton cron with leader election (if hybrid mode used).
* **Observability:** OpenTelemetry traces, Prometheus metrics, signed audit logs to a regulator-accessible bucket.

## 8. Scalability and Performance

* **Throughput:** Fabric / Hedera-class. Roaming volumes (tens of thousands of sessions per minute at peak across a whole consortium) sit well within published benchmarks (e.g., Androulaki et al., EuroSys 2018, [doi:10.1145/3190508.3190538](https://doi.org/10.1145/3190508.3190538), which reports more than 3 500 tx/s for Fabric in certain configurations).
* **Critical-path latency:** dominated by physical media attach (OCPP `RemoteStartTransaction`, RAN attach). Authorisation contract budget: ≤ 500 ms.
* **Reads:** materialised views in the gateway; chain replay used only for audit.

## 9. Security and Privacy

* TLS 1.3 ingress; mTLS gateway ↔ core.
* No PII on-chain.
* Replay protection: every presentation carries a nonce bound to `(foreignOp, sessionId, timestamp)`.
* Right-to-be-forgotten: stop issuing VCs, purge off-chain user records; on-chain pseudonymous events remain.

## 10. Failure Modes

| Failure | Effect | Recovery |
|---|---|---|
| Gateway down | Foreign Operator cannot authorise new sessions. | Multi-region active-active; fallback OCPI hub flow with deferred reconciliation. |
| Anchor missed | No public root for a day. | Catch-up commit. |
| Operator key compromise | Forged session records until detected. | Registry revocation; sessions in window marked `key-revoked`. |
| Bond exhausted | New sessions for that Operator denied. | Operator tops up `BondVault`; alerts at < 25 % threshold. |
| Public L2 outage (if hybrid) | External integrity verification degraded. | Cache last good root; show staleness banner. |

## 11. Build / Tech Choices (indicative)

* **Permissioned core:** Hyperledger Fabric 2.x (Go chaincode) or Hedera (HCS + smart contracts).
* **Identity:** Hyperledger Indy / Aries; SD-JWT VC libraries.
* **API gateway:** Go (Echo) or Node.js (Fastify); JOSE for JWS.
* **OCPI implementation:** TNM (Tomorrow Network Management) or BigchainDB-style OCPI library.
* **GSMA adapter:** Hyperledger Fabric peer + middleware to consortium ledger.
* **Storage:** PostgreSQL materialised views; S3-compatible object store.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; cosign-signed images.

## 12. Open Architecture Questions

* JWT-VC vs JSON-LD VC for user credentials (tooling trade-off).
* Whether to integrate as a peer of the GSMA eBusiness Network or operate parallel to it.
* Bond-vs-credit-line economics across operator tiers.
* Whether to support self-custody wallets at launch or defer to phase 2.

## 13. SFC Compliance Profile

SFC: this design follows [SFC profile 2.0](../SFC_COMPLIANCE.md). Framework: Besleaga, A. N. "'Sustainability-First Consensus' Ledgers for a Green Digital Future", *Communications of the ACM*, Opinion, in press, [doi:10.1145/3809296](https://doi.org/10.1145/3809296). The profile holds the rules and checks; this section holds the project facts only.

| Project fact | This design |
|---|---|
| **Hot path and platform case** | Permissioned: Hyperledger Fabric (Raft ordering, mechanism crash-fault-tolerant; a BFT ordering service would name bft; aligned with the GSMA eBusiness Network), run only by the registered operators. Platform case: the network's own ledger figure. The alternative, Hedera (aBFT), would be a public hot path and would need a public assessment below 1 GWh on the profile's boundary; the vendor [states it is carbon-negative](https://hedera.com/blog/going-carbon-negative-at-hedera-hashgraph) through purchased offsets, which is not an energy measurement. |
| **Attesting operators** | Home and foreign operators and the neutral foundation, each attesting its own energy and carbon. |
| **Node count and registered-node bound** | At least 4 operators (BFT / Raft). The maximum node count is fixed in the methodology document. Example: 4 nodes → 4 × 1 976.4 = 7 905.6 kWh. Registered-node bound, to be met before the first full year: N × P × O × 8 784 h / 1 000 < 1 000 000 kWh, where P = rated power in watts of the worst hardware class in use, N = greatest number of nodes the registered operators may run (gateways and adapter nodes inside the C1 boundary included) and O = data-centre overhead factor, which has no default. With an assumed 150 W per node and an assumed overhead factor of 1.5 (both assumptions, to be fixed in the methodology document), each node adds 1 976.4 kWh, so the bound stays below the cap up to 505 nodes. |
| **Hardware** | Peers, gateways and adapter nodes run on general-purpose x86 / arm64 servers; no ASICs. Each operator declares its hardware in its Registry entry (purchase date, planned retirement date, reuse policy), with WEEE-certified recycling at retirement. |
| **Scope 1** | None, stated in the methodology document. |
| **Scope 2** | Market-based (the declared figure), covering the electricity of peers, gateways and adapter nodes and backed by each operator's own contractual instruments where held; location-based optional, using Electricity Maps regional intensity with IEA emission factors as fallback. Guarantees of Origin attached to EV sessions describe the charging energy sold to drivers, which is outside the C1 boundary, and do not enter the operators' Scope 2. |
| **Scope 3** | Categories named in the methodology document, including the embodied carbon of the hardware. |
| **Offset coverage** | Offset coverage, checked: every month each operator's retired credits are compared with its gross emissions. This is not a net-zero or neutrality claim. |
| **Anchor** | Optional and informative only; to be chosen per deployment (a public chain that is not proof-of-work). |
