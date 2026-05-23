# Sustainability-First Consensus (SFC) — Engineering Profile

> Catalogue-level engineering profile applying to all six projects in this folder.

## 0. Citation

This profile applies the framework defined in:

> Besleaga, A. N. (2026). *"Sustainability-First Consensus" Ledgers for a Green Digital Future.* Association for Computing Machinery. https://doi.org/10.1145/3809296
> ORCID: [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283)

For the full framework — rationale, motivation and argumentation — consult the paper. This document covers only the engineering parameters needed to apply the framework here. Any deployment claiming SFC alignment MUST cite the paper above.

## 1. The four criteria (as applied here)

| # | Criterion | Threshold / Requirement |
|---|---|---|
| **C1** | Energy consumption | Total annualised network energy consumption < **0.001 TWh (1 GWh)** system-wide. |
| **C2** | Hardware lifecycle | Extended hardware utility; general-purpose hardware; **no single-use ASICs**. |
| **C3** | Carbon accountability | Native on-chain carbon transparency; **annual Net Zero** via direct renewables or verified offsets; **GHG Protocol Scope 2 & 3**. |
| **C4** | Regulatory readiness | CSRD / ESG reporting via APIs (machine-readable, ESRS-E1 aligned). |

## 2. Allowed platforms (hot-path)

Use a platform whose **independently measured** network energy is below C1. Verified low-energy options used across this catalogue:

| Platform | Why it qualifies |
|---|---|
| Hyperledger Fabric | Permissioned BFT; energy bounded by node count × node power. |
| NEAR Protocol | Sharded PoS; [Climate Neutral Product label](https://near.foundation/blog/near-climate-neutral-product/) (South Pole 2021). |
| Hedera Hashgraph | aBFT; carbon-negative. |
| VeChainThor | Authority masternodes; low published footprint. |
| **Any PoW chain (Bitcoin, …)** | ❌ **Forbidden** in any hot-path — 100–170 TWh/yr per [CBECI](https://ccaf.io/cbeci/index). |

Polygon zkEVM is acceptable as an anchor layer for daily Merkle roots. Ethereum L1 (~0.0026 TWh/yr) is anchor-only, never hot-path. The paper lists additional qualifying platforms.

## 3. On-chain sustainability events

Operators emit two events monthly. Signed by the operator DID like any other event.

### 3.1 `EnergyAttested` (supports C1)

```jsonc
{
  "type":   "EnergyAttested",
  "subject":"<operatorDid>",
  "actor":  "<operatorDid>",
  "prev":   "<previous EnergyAttested hash or null>",
  "ts":     "2026-05-23T00:00:00Z",
  "payload": {
    "period":           { "from": "2026-04-01", "to": "2026-04-30" },
    "nodeCount":        7,
    "kWhConsumed":      412.5,
    "measurementMethod":"ccri-hybrid-allocation",
    "evidenceCid":      "bafy…"
  },
  "sig": { "alg": "Ed25519", "value": "…" }
}
```

### 3.2 `CarbonAttested` (supports C3)

Same envelope as above. Payload fields:

* `period` — `{ from, to }`
* `scope2KgCO2e` — electricity emissions for the period
* `scope3KgCO2e` — amortised hardware embodied carbon + upstream
* `gridIntensityRef` — e.g. `electricitymaps:DE-LU:2026-04-avg`
* `offsetsKgCO2e` — retired offsets for the period
* `netZero` — boolean; MUST equal `(scope2 + scope3) <= offsets`
* `evidenceCid` — IPFS pointer to offset-retirement proofs

**Net-Zero invariant**: `scope2KgCO2e + scope3KgCO2e <= offsetsKgCO2e`. A non-compliant period flags the operator until the next compliant attestation.

## 4. Sustainability API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/v1/sustainability/operator/{did}` | Latest attestations + 12-month rollup. |
| `GET` | `/v1/sustainability/network` | Network total vs. C1 threshold. |
| `GET` | `/v1/sustainability/csrd?period=…&operator=…` | Signed ESRS-E1 climate-disclosure block. |
| `GET` | `/v1/sustainability/sfc` | SFC self-report incl. citation pointer. |

All responses signed `application/jose+json`.

## 5. Hardware-lifecycle declaration (supports C2)

Every operator declares, in their Registry record:

```jsonc
{
  "nodeProfile": {
    "hardwareClass":   "general-purpose-x86 | arm64-server | rpi-cluster",
    "asicForbidden":   true,
    "purchasedAt":     "2024-03-01",
    "expectedRetireAt":"2032-03-01",
    "reusePolicy":     "donate-to-education | resell-refurbished | recycle-WEEE-certified"
  }
}
```

Single-use ASIC-class mining hardware is rejected at onboarding. HSMs for institutional key custody are general-purpose security devices and are acceptable.

## 6. Measurement sources

* [Crypto Carbon Ratings Institute (CCRI) Sustainability API](https://carbon-ratings.com/) — platform-level baseline.
* [Electricity Maps API](https://www.electricitymaps.com/) — per-node real-time grid intensity across 160+ zones.
* [GHG Protocol Corporate Standard](https://ghgprotocol.org/corporate-standard) — Scope 2 / Scope 3 boundaries.

## 7. Conformance checks

| ID | Check |
|---|---|
| **C-SFC-1** | Latest `EnergyAttested` per operator within the last 35 days. |
| **C-SFC-2** | Trailing-12-month `kWhConsumed` total < **1 000 000 kWh** (= 1 GWh, C1). |
| **C-SFC-3** | Every operator's `nodeProfile.asicForbidden == true` and `hardwareClass` ∈ allowed list (C2). |
| **C-SFC-4** | Per-operator Net-Zero invariant per period (C3). |
| **C-SFC-5** | `/v1/sustainability/csrd` returns a schema-valid ESRS-E1 payload (C4). |
| **C-SFC-6** | Chosen platform appears in §2 (or has a public assessment proving it fits within C1). |

## 8. Per-project platform pins

| Project | Hot-path | Anchor |
|---|---|---|
| Recycling Chain | Hyperledger Fabric | Polygon zkEVM |
| Certification Supply-Chain | Hyperledger Fabric or VeChainThor | Polygon zkEVM |
| Healthcare Pharma | Hyperledger Fabric | Polygon zkEVM |
| Paperless Billing | NEAR Protocol | — |
| Roaming Data Exchange | Hyperledger Fabric or Hedera | Polygon zkEVM |
| Sustainability Climate Change | Hedera (with Guardian) or Hyperledger Fabric | Polygon zkEVM |

## 9. Non-negotiables

* No PoW chain in any hot path.
* Operators publish monthly `EnergyAttested` and `CarbonAttested` — missing attestations make the operator `non-compliant`.
* "Carbon offsets" used to claim Net Zero MUST reference retired credits with an auditable proof (CID of retirement record).
* If the chosen platform's measured energy ever rises above C1, migrate to another §2 platform within one reporting period.

---

* **Profile version:** `SFC-PROFILE v1.1` (2026-05-23).
* **Framework:** Besleaga (2026), https://doi.org/10.1145/3809296. Future revisions of the paper trigger a new profile version.
* **Author identifier:** ORCID [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283).
* **Scope reminder:** this profile applies the framework — it does not reproduce its rationale or argumentation. Read the paper.
