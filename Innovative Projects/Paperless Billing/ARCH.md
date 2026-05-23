# Paperless Billing — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **thin anchor-and-event ledger** sitting beside existing vendor systems:

1. **Edge Layer** — vendor POS / e-commerce checkout / ERP, customer wallet, auditor / tax-authority client.
2. **Gateway / API Layer** — encrypts payloads, pins them to a content-addressed store, builds and submits the on-chain anchor.
3. **Ledger Layer** — a single contract holds `BillIssued` / `BillVoided` / `BillRefunded` events; that's all.
4. **Off-chain Storage** — IPFS pinning service (or S3-compatible content-addressed bucket) for encrypted bill payloads.

The ledger is intentionally minimal: hashes, totals and pointers — never line items, never customer identity.

## 2. Component Diagram (logical)

```
┌─────────────────────────────────────────────────────────────────────┐
│                              EDGE LAYER                              │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────────┐  │
│  │ Vendor POS │ │ E-commerce │ │ Customer   │ │ Auditor / Tax    │  │
│  │ / ERP      │ │ Checkout   │ │ Wallet     │ │ Authority Client │  │
│  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘ └─────────┬────────┘  │
└────────┼──────────────┼──────────────┼──────────────────┼───────────┘
         │              │              │                  │
         ▼              ▼              ▼                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          GATEWAY / API LAYER                         │
│  ┌────────────┐ ┌──────────────┐ ┌────────────┐ ┌────────────────┐  │
│  │ REST API   │ │ Peppol BIS / │ │ Encrypt &  │ │ Verify Cache   │  │
│  │ (W/R)      │ │ EN 16931     │ │ Pin Worker │ │ + Materialised │  │
│  │            │ │ Validator    │ │            │ │ Views          │  │
│  └─────┬──────┘ └──────┬───────┘ └─────┬──────┘ └────────┬───────┘  │
└────────┼───────────────┼───────────────┼─────────────────┼──────────┘
         │               │               │                 │
         ▼               ▼               ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                            LEDGER LAYER                              │
│        ┌──────────────────────────────────────────────────┐          │
│        │   BillAnchor contract  (NEAR Rust  or  EVM Sol)  │          │
│        │   events: BillIssued | BillVoided | BillRefunded │          │
│        └──────────────────────────────────────────────────┘          │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          OFF-CHAIN STORAGE                           │
│         ┌─────────────────────────────────────────────┐              │
│         │ IPFS / S3-compatible content-addressed store │              │
│         │ Encrypted bill payloads, audit reports       │              │
│         └─────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

## 3. Components (responsibilities)

| # | Component | Layer | Responsibility |
|---|---|---|---|
| C1 | Vendor POS / ERP | Edge | Builds the bill payload (compact JSON or UBL); signs the submission. |
| C2 | E-commerce checkout | Edge | Same as C1 but server-side. |
| C3 | Customer wallet | Edge | Holds DID; claims bills; decrypts using wrapped CEKs. |
| C4 | Auditor client | Edge | Presents grant VC; pulls vendor-period bundle. |
| C5 | REST API | Gateway | JWS validation; rate-limiting; routing. |
| C6 | EN 16931 / Peppol BIS validator | Gateway | Static validation of B2B payloads before anchor. |
| C7 | Encrypt & Pin worker | Gateway | Generates CEK; wraps for vendor + customer + grantees; pins to IPFS. |
| C8 | Verify cache | Gateway | Materialised views over the contract's events. |
| C9 | BillAnchor contract | Ledger | Holds anchor events; enforces uniqueness, void / refund invariants. |
| C10 | Off-chain store | Storage | IPFS pinning service or S3-compatible bucket (content-addressed). |
| C11 | Adapter (national e-invoicing) | Gateway | Translates UBL into national clearance formats where required. |

## 4. Key Sequences

### 4.1 Issue a B2C receipt

```
POS ──build JSON──▶ API ──validate──▶ Encrypt+Pin worker
                                           │
                                           ├─▶ encrypt(JSON, CEK)
                                           ├─▶ pin to IPFS  → CID
                                           ├─▶ wrap(CEK, vendorPub)
                                           │
                                           └─▶ BillAnchor.issue(billHash, cid, …, totals)
                                                   │
                                                   └─▶ event BillIssued
```

### 4.2 Customer claims a receipt

```
POS shows QR pbil://claim/<billId>?one_time=token

Wallet ──POST /v1/bills/{id}/claim──▶ API
                                       │
                                       ├─▶ verify one_time token
                                       ├─▶ wrap(CEK, customerPub)
                                       └─▶ off-chain BillClaimed (no on-chain leakage of customer DID)
```

### 4.3 Tax authority audit

```
Authority ──present grant VC──▶ API
                                  │
                                  ├─▶ verify VC against Registry
                                  ├─▶ stream {anchor events, encrypted payloads, wrapped CEKs}
                                  └─▶ signed bundle (PDF + JSON) for the period
```

### 4.4 Refund

```
POS ──sign──▶ API ──▶ BillAnchor.refund(originalHash, amount, refundBillHash)
                              │
                              ├─▶ event BillRefunded
                              └─▶ event BillIssued(refundBillHash, …, gross = -refundAmount)
```

## 5. Trust Boundaries

| Boundary | Trust assumption | Mitigation |
|---|---|---|
| Vendor ↔ Gateway | Vendor key may be lost / compromised. | Strong key custody; Registry-level revocation; per-store sub-keys. |
| Customer wallet ↔ Gateway | Customer may use a managed wallet. | Wallet keys per user; recovery flow; magic-link claim option for non-crypto users. |
| Gateway ↔ Ledger | Gateway is a thin verifier — it cannot forge events. | All authority is signature-based. |
| Ledger ↔ Off-chain store | Store could lose or refuse to serve a payload. | Mirror to ≥ 2 pinning services; verifier reports `payload-unavailable` rather than fabricating data. |
| Vendor ↔ Auditor | Vendor must release CEKs in scope. | Grant VCs; auditor cannot decrypt anything outside scope. |

## 6. Data Storage

| Data | Where | Notes |
|---|---|---|
| Anchor events (hashes, totals, CIDs) | On-chain | Authoritative. |
| Encrypted bill payloads | IPFS / S3 (content-addressed) | Referenced by CID. |
| Wrapped CEKs | Off-chain (per-grantee) | Vendor keeps the master wrap; per-grantee wraps emitted on demand. |
| Materialised views (verify cache, vendor periods) | Gateway RDBMS | Rebuilt from chain on demand. |
| Customer DID ↔ billId links | Customer wallet (local) + optional gateway index | Not on-chain. |

## 7. Deployment View

* **Chain:** NEAR mainnet (reference) or an EVM L2 (Polygon PoS / Arbitrum). Carbon-neutral certification preferred.
* **Gateway:** stateless containers behind a regional LB; horizontal autoscale.
* **IPFS:** at least two pinning services in different regions, or a self-hosted cluster + a public-pinning failover.
* **Observability:** OpenTelemetry traces, Prometheus metrics, signed audit logs to a regulator-accessible bucket.

## 8. Scalability and Performance

* **Batching:** N receipts → one anchor tx where chain fees dominate (configurable cadence; default 1 s window or 100 receipts).
* **Read path:** Verify hits the gateway cache; cold reads walk the chain index.
* **Latency:** Issuance < 5 s p95 includes encrypt + pin + finality on the chosen chain.

## 9. Security and Privacy

* TLS 1.3 ingress.
* No PII on-chain. Customer DID is never on-chain unless the customer chose a public address.
* Per-bill CEK; rotating wraps; CEK is destroyed once all grantees have their wrapped copy and the bill is final.
* Right-to-be-forgotten: customer can request the off-chain payload be purged from all pinning services they control. On-chain anchor remains but no longer resolves to data.

## 10. Failure Modes

| Failure | Effect | Recovery |
|---|---|---|
| IPFS pinning service down | New receipts cannot pin to that service. | Round-robin across configured pinning providers. |
| Chain congestion / fee spike | Anchor latency above NFR. | Wider batch window; fallback chain for non-time-critical anchors. |
| Vendor key compromise | Forged receipts until rotation. | Registry revocation; verify endpoint marks bills issued in the window as `key-revoked`. |
| Customer wallet loss | Customer loses access to their copies. | Magic-link recovery if vendor + customer both opted into a recovery custodian. |

## 11. Build / Tech Choices (indicative)

* **Chain:** NEAR (Rust contracts) or Polygon PoS / Arbitrum (Solidity 0.8.x).
* **Gateway:** Go (Echo) or Node.js (Fastify); JOSE for JWS; UBL libraries for B2B.
* **Storage:** Web3.Storage / Pinata for IPFS; or self-hosted Kubo cluster.
* **EN 16931 validator:** Mustang Project (open source) or KoSIT validator.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; cosign-signed images.

## 12. Open Architecture Questions

* Single anchor contract vs. per-vendor subcontract.
* Storage governance: vendor-side pinning vs. shared consortium-pinning service.
* National e-invoicing integration: per-country adapter set vs. a single Peppol Access Point.
* Whether customer claim should be on-chain (more decentralised, leaks DID) or off-chain (current default).

## 13. SFC Compliance Profile

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Project pin: `sustainability-profile: SFC-PROFILE v1.1`.

| Criterion | How this project meets it |
|---|---|
| **1. Energy < 1 GWh / yr** | Hot path: NEAR Protocol — sharded PoS, Climate-Neutral certified, measured network energy well below the SFC cap. Gateway tier (encrypt + pin + submit) sized to a handful of general-purpose VMs per region. |
| **2. Hardware lifecycle** | NEAR validators run general-purpose servers. Our own gateway VMs are general-purpose; if self-hosted, declared in `nodeProfile` with WEEE-certified retirement. No ASICs anywhere. |
| **3. Carbon accountability** | Gateway operators publish monthly `EnergyAttested` and `CarbonAttested` events. Chain-tier energy disclosed via NEAR Foundation's published certification (pulled into `/v1/sustainability/network` as a separately attributed line). Scope 2 = VM electricity × regional intensity (Electricity Maps); Scope 3 = amortised embodied carbon of self-hosted gateway hardware. Offsets retired per period. |
| **4. Regulatory readiness** | `/v1/sustainability/csrd` returns signed ESRS E1 JSON. Customer retailers can pull the project's per-vendor footprint as a Scope-3 input for their own CSRD disclosure. |

**Measurement sources.** NEAR Foundation public certification (chain tier); CCRI Sustainability API for cross-comparison; Electricity Maps API for per-region grid intensity; IEA emission factors (fallback). GHG Protocol Scopes 2 & 3 for boundary definition.

**Migration clause.** If NEAR's measured energy ever rises above the SFC 1 GWh / yr cap, the project migrates to another platform from [SFC_COMPLIANCE.md §2](../SFC_COMPLIANCE.md) (e.g., Algorand or Hedera) within one reporting period. The receipt anchor format is platform-agnostic by design (cf. SPEC §3).
