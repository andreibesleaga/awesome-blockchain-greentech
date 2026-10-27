# RecyclingChain — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **hybrid distributed ledger** with three layers:

1. **Edge Layer** — labels, scanners, IoT (smart scales, spectrometers), mobile/PWA portals.
2. **Permissioned Core** — high-throughput consortium ledger (Hyperledger Fabric or Corda) holding the authoritative event log.
3. **Public Proof Layer** — an EVM L2 (for example Arbitrum) holding the `MaterialToken` smart contracts for open consumer/brand verification. Daily Merkle anchors are optional (SFC profile 2.0, Appendix E.2) and, if deployed, go to a public chain that is not proof-of-work.

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
| C13 | Anchor Job (optional) | Core → Public | Computes daily Merkle root and commits to `PublicAnchor`. |
| C14 | PublicAnchor contract (optional) | Public | Records `(day, merkleRoot, signerSet)` for external verification. |
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

### 4.3 Daily public anchoring (optional)

The anchor is optional and informative (SFC profile 2.0, Appendix E.2). When deployed:

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
| Anchor job missed (only if the anchor is deployed) | Public root not committed for a day. | Catch-up commit; verifiers tolerate gaps with explicit `MissingDay` markers. |
| Oracle device compromised | Forged measurements until detected. | Registry revocation; rejected events replayed against the new key set. |
| Core node loss | Reduced fault tolerance window. | Add replacement node; resync from peers. |
| Public L2 outage | Verifier UX degraded. | Cache last good root; show staleness banner. |
| Lock TTL expires mid-process | Item appears unlocked while physically being processed. | Recycler must re-`DecommissionRequested`; idempotent on the same actor. |

## 11. Build / Tech Choices (indicative)

* **Permissioned core:** Hyperledger Fabric 2.x (Go chaincode) **or** R3 Corda 5 (Kotlin).
* **Public layer:** Arbitrum or another public chain that is not proof-of-work (Solidity 0.8.x).
* **API gateway:** Node.js (Fastify) or Go (Echo); JOSE for JWS/JWE; DID-core libs.
* **Storage:** PostgreSQL for materialised views, S3-compatible for blobs/photos.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; reproducible container builds; signed images (cosign).

## 12. Open Architecture Questions

* Fabric vs Corda for the permissioned core (governance vs. confidentiality trade-off).
* Whether to expose `MaterialERC20` as a freely tradable asset or as a soul-bound, retire-only credit.
* DPP schema version target (the EU spec is still iterating).

## 13. SFC Compliance Profile

SFC: this design follows [SFC profile 2.0](../SFC_COMPLIANCE.md). Framework: Besleaga, A. N. "'Sustainability-First Consensus' Ledgers for a Green Digital Future", *Communications of the ACM*, Opinion, in press, [doi:10.1145/3809296](https://doi.org/10.1145/3809296). The profile holds the rules and checks; this section holds the project facts only.

| Project fact | This design |
|---|---|
| **Hot path and platform case** | Permissioned: Hyperledger Fabric (Raft ordering, mechanism crash-fault-tolerant; a BFT ordering service would name bft) on general-purpose servers, run only by the registered operators; Corda is the open alternative. Platform case: the network's own ledger figure. |
| **Attesting operators** | The consortium operators: OEM consortium, neutral foundation and two recyclers, each attesting its own energy and carbon. |
| **Node count and registered-node bound** | At least 4 operators; at most 12 peers. Example, with an assumed 4 gateway nodes added to 12 peers: N = 16 → 16 × 1 976.4 = 31 622.4 kWh. Registered-node bound, to be met before the first full year: N × P × O × 8 784 h / 1 000 < 1 000 000 kWh, where P = rated power in watts of the worst hardware class in use, N = greatest number of nodes the registered operators may run (gateways and adapter nodes inside the C1 boundary included) and O = data-centre overhead factor, which has no default. With an assumed 150 W per node and an assumed overhead factor of 1.5 (both assumptions, to be fixed in the methodology document), each node adds 1 976.4 kWh, so the bound stays below the cap up to 505 nodes. |
| **Hardware** | General-purpose x86 / arm64 only; no ASICs. Each operator declares its hardware in its Registry entry (purchase date, planned retirement date, reuse policy). A hardware reuse policy (donate, refurbish or WEEE-certified recycling) is mandatory. |
| **Scope 1** | None, stated in the methodology document. |
| **Scope 2** | Market-based (the declared figure); location-based optional, using Electricity Maps regional intensity with IEA emission factors as fallback. Electricity of peers and gateways. |
| **Scope 3** | Categories named in the methodology document, including the embodied carbon of the hardware. |
| **Offset coverage** | Offset coverage, checked: every month each operator's retired credits are compared with its gross emissions. This is not a net-zero or neutrality claim. |
| **Anchor** | Optional and informative only; to be chosen per deployment (a public chain that is not proof-of-work). |
| **Public proof layer** | The `MaterialERC20` mirror runs on a public chain that is not proof-of-work (section 11). It is not the hot path and carries no event SFC 2 relies on. Its share of that chain's energy is named as excluded in the methodology document (SFC profile 2.0, 4.2), as the anchor chain's share is when the anchor is deployed. |
