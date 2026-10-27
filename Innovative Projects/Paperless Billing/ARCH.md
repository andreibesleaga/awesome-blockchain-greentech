# Paperless Billing — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **thin anchor-and-event ledger** sitting beside existing vendor systems:

1. **Edge Layer** — vendor POS / e-commerce checkout / ERP, customer wallet, auditor / tax-authority client.
2. **Gateway / API Layer** — encrypts payloads, pins them to a content-addressed store, builds and submits the on-chain anchor.
3. **Ledger Layer** — two contracts on the hot path: `BillAnchor` holds `BillIssued` / `BillVoided` / `BillRefunded` events; `SfcRegistry` holds the SFC Registry entries and the operators' `EnergyAttested` / `CarbonAttested` chains (section 13).
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
│        ┌──────────────────────────────────────────────────┐          │
│        │   SfcRegistry contract — Registry entries |      │          │
│        │   EnergyAttested | CarbonAttested                │          │
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
| C8 | Verify cache | Gateway | Materialised views over the contracts' events; serves the profile's ledger read (section 5.7) as a ledger excerpt at the `ledger-access-uri`. |
| C9 | BillAnchor contract | Ledger | Holds anchor events; enforces uniqueness, void / refund invariants. |
| C10 | Off-chain store | Storage | IPFS pinning service or S3-compatible bucket (content-addressed). |
| C11 | Adapter (national e-invoicing) | Gateway | Translates UBL into national clearance formats where required. |
| C12 | SfcRegistry contract | Ledger | Holds registrar-signed Registry entries and the attestation chains; rejects an event that breaks an acceptance rule of the profile (section 5.5); assigns strictly increasing commit instants. |

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
| SFC Registry entries and attestations | On-chain (SfcRegistry) | Authoritative; the gateway exports them as a ledger excerpt for verifiers. |
| Encrypted bill payloads | IPFS / S3 (content-addressed) | Referenced by CID. |
| Wrapped CEKs | Off-chain (per-grantee) | Vendor keeps the master wrap; per-grantee wraps emitted on demand. |
| Materialised views (verify cache, vendor periods) | Gateway RDBMS | Rebuilt from chain on demand. |
| Customer DID ↔ billId links | Customer wallet (local) + optional gateway index | Not on-chain. |

## 7. Deployment View

* **Chain:** NEAR mainnet (reference) or an EVM chain (Polygon PoS or the Arbitrum L2) that qualifies under SFC profile 2.0.
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

SFC: this design follows [SFC profile 2.0](../SFC_COMPLIANCE.md). Framework: Besleaga, A. N. "'Sustainability-First Consensus' Ledgers for a Green Digital Future", *Communications of the ACM*, Opinion, in press, [doi:10.1145/3809296](https://doi.org/10.1145/3809296). The profile holds the rules and checks; this section holds the project facts only.

| Project fact | This design |
|---|---|
| **Hot path and platform case** | Public: NEAR Protocol (sharded proof of stake). A public hot path needs a public assessment below 1 GWh on the profile's boundary, and NEAR's energy is shown through that platform check, not through this network's attestations. NEAR holds an offset-based Climate Neutral Product label (South Pole, 2021), which is not an energy measurement and not a qualification. The only published figure found for NEAR is a token-level MiCA sustainability indicator from a crypto-asset service provider; read the current disclosure and its boundary at the source (spec E.1). It is the energy attributed to the NEAR token, so it is a token-level share and not a bound on the network, and it is not a network-boundary assessment; one must still be found or commissioned before deployment. The methodology document names the NEAR validator energy as excluded from the declaration and points to the public assessment used for C-SFC-6. |
| **Attesting operators** | The gateway operators (encrypt, pin and submit), each attesting its own energy and carbon. |
| **Node count and registered-node bound** | Gateway tier sized to a handful of general-purpose VMs per region. The registered-node bound applies to a permissioned hot path only, so it does not apply to NEAR. |
| **Hardware** | NEAR validators run general-purpose servers; they are outside this network's Registry and are not declared here. The gateway VMs are general-purpose; no ASICs. Every gateway operator declares them in its Registry entry (`nodeProfile`): `cloud-instance` for rented VMs, with the instance start as the purchase date, or `general-purpose-x86` / `arm64-server` when self-hosted. Each entry carries the planned retirement date and a reuse policy from the profile's list (WEEE-certified recycling for owned hardware). |
| **Scope 1** | None, stated in the methodology document. |
| **Scope 2** | Market-based (the declared figure); location-based optional, using Electricity Maps regional intensity with IEA emission factors as fallback. Electricity of the gateway VMs. |
| **Scope 3** | Categories named in the methodology document, including the embodied carbon of the hardware. |
| **Offset coverage** | Offset coverage, checked: every month each operator's retired credits are compared with its gross emissions. This is not a net-zero or neutrality claim. This design is consumer-facing (receipts), so it makes no consumer-facing claim of carbon neutrality (Directive (EU) 2024/825). The same rule applies to every design (spec section 6). |
| **Anchor** | Not needed: the hot path is already a public chain. |
| **Project-specific rules** | The network declaration holds the deployment's own operators, the gateway operators, and carries only their attested kWh. It does not carry NEAR's energy. The Registry entries and the attestation chains are committed to the `SfcRegistry` contract on NEAR, beside the bill anchors. The registrar is the gateway operators' consortium; its keys are listed in the methodology document (`registrar-keys`). The `ledger-access-uri` in `ledger-evidence-2` is the gateway's read endpoint, which exports the contract's records as a ledger excerpt (profile section 5.8). |
