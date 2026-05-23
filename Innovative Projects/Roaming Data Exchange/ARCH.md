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

* **Throughput:** Fabric / Hedera-class. Roaming volumes (tens of thousands of sessions per minute at peak across a whole consortium) sit well within published benchmarks.
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

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Project pin: `sustainability-profile: SFC-PROFILE v1.1`.

| Criterion | How this project meets it |
|---|---|
| **1. Energy < 1 GWh / yr** | Hot path: Hyperledger Fabric (consortium BFT, aligned with the GSMA eBusiness Network) or Hedera (carbon-negative aBFT, public). Anchor: Polygon zkEVM. Combined measured budget well under the cap. |
| **2. Hardware lifecycle** | All peers, gateways and adapter nodes run on general-purpose x86 / arm64 servers. ASICs forbidden. Each Operator declares `nodeProfile` (purchasedAt, expectedRetireAt, reusePolicy); WEEE-certified recycling at retirement. |
| **3. Carbon accountability** | Each Operator publishes monthly `EnergyAttested` and `CarbonAttested` events. Scope 2 from peer + gateway electricity weighted by Electricity Maps regional intensity; Scope 3 from amortised embodied carbon. EV session ESG tags reference Guarantees-of-Origin (verifiable via the issuing certificate). Offsets retired per period; Net Zero invariant enforced. |
| **4. Regulatory readiness** | `/v1/sustainability/csrd` returns signed ESRS E1 JSON. Telecom and CPO groups are typically CSRD-in-scope undertakings; AFIR (Alternative Fuels Infrastructure Regulation) reporting for EV charging is supported via the same disclosure block. |

**Measurement sources.** CCRI Sustainability API + Electricity Maps API + IEA emission factors (fallback). GHG Protocol Scopes 2 & 3 for boundary definition.

**Migration clause.** If the chosen platform's measured energy exceeds 1 GWh / yr in any 12-month window, the project migrates to another platform from [SFC_COMPLIANCE.md §2](../SFC_COMPLIANCE.md) within one reporting period.
