# RecyclingChain — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **hybrid distributed ledger** with three layers:

1. **Edge Layer** — labels, scanners, IoT (smart scales, spectrometers), mobile/PWA portals.
2. **Permissioned Core** — high-throughput consortium ledger (Hyperledger Fabric or Corda) holding the authoritative event log.
3. **Public Proof Layer** — an EVM L2 (e.g., Polygon) holding daily Merkle anchors and the `MaterialToken` smart contracts for open consumer/brand verification.

This separates *operational throughput* (handled by the permissioned core) from *open trust* (handled by the public chain).

## 2. Component Diagram (logical)

```
┌─────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌─────────┐    │
│  │ QR / NFC │ │ Scanner  │ │ Mobile   │ │ IoT      │ │ ERP /   │    │
│  │ Labels   │ │ Apps     │ │ Portal   │ │ Scales   │ │ WMS     │    │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬────┘    │
└───────┼────────────┼────────────┼────────────┼────────────┼─────────┘
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          GATEWAY / API LAYER                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │ REST API    │ │ OAuth /     │ │ Oracle      │ │ Verify      │    │
│  │ (write/read)│ │ DID Auth    │ │ Ingest      │ │ Portal API  │    │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘    │
└─────────┼───────────────┼───────────────┼───────────────┼───────────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       PERMISSIONED CORE LEDGER                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ Registry │ │ ItemNFT  │ │ Batch    │ │ Lockbox  │ │ Rewards  │   │
│  │          │ │          │ │ 1155     │ │          │ │ Vault    │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │       Event Log (append-only, signed, chained per subject)   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │  daily Merkle root
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PUBLIC PROOF LAYER  (EVM L2)                     │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐   │
│  │ PublicAnchor   │ │ MaterialERC20  │ │ Verifier (libs/portal) │   │
│  └────────────────┘ └────────────────┘ └────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

## 3. Components (responsibilities)

| # | Component | Layer | Responsibility |
|---|---|---|---|
| C1 | QR/NFC Label | Edge | Carries `itemId` + signed payload. NFC variant uses a secure element. |
| C2 | Scanner App | Edge | Resolves a scan to a verify call; works offline for label authenticity. |
| C3 | Consumer Portal | Edge | Public read-only UI for take-back info and recycling outcomes. |
| C4 | IoT Oracle Client | Edge | Signs measurements (weight, assay) and submits them via OracleAdapter. |
| C5 | ERP/WMS Adapter | Edge | Maps participant business events into RecyclingChain events. |
| C6 | API Gateway | Gateway | Authenticated REST entry point; rate-limits; canonicalises payloads. |
| C7 | Oracle Adapter | Gateway | Verifies oracle credentials, attaches `oracleSig` to events. |
| C8 | Registry contract | Core | DID registry, role assignments, key rotation. |
| C9 | Token contracts (Item/Batch/Material) | Core | Lifecycle of digital twins. |
| C10 | Lockbox contract | Core | Mutual-exclusion lock during decommission. |
| C11 | RewardsVault contract | Core | Escrows deposits and bounties; pays out on verified events. |
| C12 | Event Log | Core | Append-only, signature-verified, chained per subject. |
| C13 | Anchor Job | Core → Public | Computes daily Merkle root and commits to `PublicAnchor`. |
| C14 | PublicAnchor contract | Public | Records `(day, merkleRoot, signerSet)` for external verification. |
| C15 | MaterialERC20 (public mirror) | Public | Tradable / retirable recycled-content units. |

## 4. Key Sequences

### 4.1 Manufacture → Label

```
OEM ERP ──(sign)──▶ API Gateway ──▶ ItemNFT.mint() ──▶ Event Log (ManufactureRegistered)
                                       │
                                       └─▶ Label Printer (QR/NFC with signed payload)
```

### 4.2 Decommission (no double-spend)

```
Recycler ──(sign)──▶ API ──▶ Lockbox.acquire(itemId)
   │
   ├─ ok ─▶ Event Log (DecommissionRequested)
   │        │
   │        └─▶ recycler processes physically
   │              │
   │              └─▶ Event Log (RecycleCompleted, yields)
   │                    │
   │                    └─▶ MaterialERC20.mint(yields) + Lockbox.release()
   │
   └─ already locked ─▶ 409 Conflict
```

### 4.3 Daily public anchoring

```
Anchor Job (cron, 00:10 UTC):
  events_today = EventLog.range(00:00..23:59 prev day)
  root         = merkle(events_today)
  PublicAnchor.commit(root, day) on EVM L2
```

Any third party can later replay `events_today` from the core, recompute `root`, and verify it matches the on-chain commitment.

## 5. Trust Boundaries

| Boundary | Trust assumption | Mitigation |
|---|---|---|
| Edge ↔ Gateway | Edge devices may be lost/compromised. | Per-actor keys; revocation via Registry; rate limiting. |
| Gateway ↔ Core | Gateway is a thin verifier, not authoritative. | All authority is signature-based — gateway cannot forge events. |
| Core ↔ Public | Consortium operators could collude on the core. | Daily public anchor + open conformance tests make tampering detectable. |
| Oracle ↔ Core | IoT measurements can be spoofed. | Oracle keys bound to specific devices; reputation staking. |
| Off-chain stores ↔ Core | Off-chain PII could leak. | Pseudonymous IDs; content-addressed (CID) references only on-chain. |

## 6. Data Storage

| Data | Where | Notes |
|---|---|---|
| Event chain | Permissioned core | Authoritative. |
| Token state | Permissioned core | Derived from events; cacheable. |
| Daily Merkle roots | Public L2 | Read by external verifiers. |
| `MaterialToken` supply | Public L2 | Mirror of core mint/burn events. |
| Photos, assays, BOM details | Off-chain object store (S3-compatible) | Referenced by CID; encrypted at rest. |
| PII (consumer accounts) | Off-chain RDBMS | GDPR-scoped, deletable. |

## 7. Deployment View

* **Core nodes:** ≥ 4 operators (OEM consortium + neutral foundation + 2 recyclers). Raft / BFT consensus.
* **Gateway:** stateless containers behind a regional load balancer; horizontal autoscaling.
* **Anchor Job:** singleton cron with leader election; idempotent.
* **Verify Portal:** static front-end + cached read API; CDN-fronted for the < 2 s NFR.
* **Observability:** OpenTelemetry traces, Prometheus metrics, signed audit logs shipped to a regulator-accessible bucket.

## 8. Scalability and Performance

* **Throughput.** Core targets ≥ 500 events/sec sustained. Reads served from materialised views, not by replaying the chain.
* **Batching.** Low-value commodity flows MUST use `BatchToken` to avoid per-item overhead.
* **Compression.** Future: ZK-Rollups to compress anchored proofs and reduce L2 gas spend.
* **Sharding.** Per-region core deployments anchored to a single public layer to keep verification global while keeping ops regional.

## 9. Security and Privacy

* All ingress traffic over TLS 1.3; mTLS between gateway and core.
* No PII on-chain; all consumer identifiers are pseudonymous.
* Right-to-be-forgotten implemented by purging the off-chain record; on-chain references degrade to opaque hashes.
* Key rotation supported via `KeyRotated` Verifiable Credential without invalidating prior signatures.

## 10. Failure Modes

| Failure | Effect | Recovery |
|---|---|---|
| Anchor job missed | Public root not committed for a day. | Catch-up commit; verifiers tolerate gaps with explicit `MissingDay` markers. |
| Oracle device compromised | Forged measurements until detected. | Registry revocation; rejected events replayed against the new key set. |
| Core node loss | Reduced fault tolerance window. | Add replacement node; resync from peers. |
| Public L2 outage | Verifier UX degraded. | Cache last good root; show staleness banner. |
| Lock TTL expires mid-process | Item appears unlocked while physically being processed. | Recycler must re-`DecommissionRequested`; idempotent on the same actor. |

## 11. Build / Tech Choices (indicative)

* **Permissioned core:** Hyperledger Fabric 2.x (Go chaincode) **or** R3 Corda 5 (Kotlin).
* **Public layer:** Polygon zkEVM or Arbitrum (Solidity 0.8.x).
* **API gateway:** Node.js (Fastify) or Go (Echo); JOSE for JWS/JWE; DID-core libs.
* **Storage:** PostgreSQL for materialised views, S3-compatible for blobs/photos.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; reproducible container builds; signed images (cosign).

## 12. Open Architecture Questions

* Fabric vs Corda for the permissioned core (governance vs. confidentiality trade-off).
* Whether to expose `MaterialERC20` as a freely tradable asset or as a soul-bound, retire-only credit.
* DPP schema version target (the EU spec is still iterating).

## 13. SFC Compliance Profile

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Project pin: `sustainability-profile: SFC-PROFILE v1.1`.

| Criterion | How this project meets it |
|---|---|
| **1. Energy < 1 GWh / yr** | Hot path: Hyperledger Fabric on general-purpose servers (≤ 12 peers, each ~150 W typical → ≤ ~15 MWh / yr peer power; ≤ ~50 MWh / yr including replication & gateways). Anchor: Polygon zkEVM (well below the cap). Total well under 1 GWh / yr. |
| **2. Hardware lifecycle** | All peers run on general-purpose x86 / arm64 servers; ASICs forbidden. Each operator declares `nodeProfile` (purchasedAt, expectedRetireAt, reusePolicy) in the Registry. Hardware reuse policy (donate / refurbish / WEEE-certified recycle) mandatory. |
| **3. Carbon accountability** | Operators emit `EnergyAttested` and `CarbonAttested` events monthly. Scope 2 = peer + gateway electricity, derived from Electricity Maps `gCO2eq/kWh` per region × measured kWh. Scope 3 = amortised embodied carbon of hardware over expected useful life. Offsets retired against the period; verifier enforces `scope2 + scope3 ≤ offsets` (Net Zero). |
| **4. Regulatory readiness** | Gateway exposes `/v1/sustainability/csrd` returning ESRS E1 climate-disclosure JSON (gross Scopes 1/2/3, removals, intensity), signed `application/jose+json`. Also `/v1/sustainability/network` for the network-wide rollup. |

**Measurement sources.** Per [SFC_COMPLIANCE.md §3](../SFC_COMPLIANCE.md): CCRI Sustainability API for the platform-level baseline (Fabric / Polygon zkEVM), Electricity Maps API for per-node grid intensity, IEA emission factors as fallback, GHG Protocol Scopes 2 & 3 for boundary definition.

**Migration clause.** If the chosen platform's measured energy exceeds 1 GWh / yr in any 12-month window, the project migrates to another platform from [SFC_COMPLIANCE.md §2](../SFC_COMPLIANCE.md) within one reporting period.
