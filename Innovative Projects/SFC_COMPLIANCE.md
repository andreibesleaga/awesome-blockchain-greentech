# Sustainability-First Consensus (SFC) — Engineering Profile

> Catalogue-level engineering profile applying to all six projects in this folder. Short name: **the SFC ledger profile** (what a ledger records). Its companion, **the SFC disclosure profile** ([`sfc-compliance/PROFILE.md`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/PROFILE.md), version 1.0), says how the figures are published.

## 0. Citation

This profile applies the framework defined in:

> Besleaga, A. N. (in press). *"Sustainability-First Consensus" Ledgers for a Green Digital Future.* Communications of the ACM (Viewpoint). Association for Computing Machinery. https://doi.org/10.1145/3809296 — *accepted; in press. The DOI resolves once ACM publishes.*
> ORCID: [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283)

For the full framework — rationale, motivation and argumentation — consult the paper. This document covers only the engineering parameters needed to apply the framework here. Any deployment claiming SFC alignment MUST cite the paper above.

## 1. The four criteria (as applied here)

| # | Criterion | Threshold / Requirement |
|---|---|---|
| **C1** | Energy consumption | Total annualised network energy consumption < **0.001 TWh (1 GWh)** system-wide. **Boundary** ("system-wide"): the energy used for the validation of transactions and the maintenance of the integrity of the ledger, per calendar year, as in Commission Delegated Regulation (EU) 2025/422, Annex, Table 2, field S.8, counted over all its nodes as the Regulation's recital 8 says; this profile counts data-centre overhead within it (S.8 itself does not mention it); gateways, off-ledger storage, backups and any anchor-chain share are declared as included or excluded in the methodology document; client devices are excluded. |
| **C2** | Hardware lifecycle | Extended hardware utility; general-purpose hardware; **no single-use ASICs**. |
| **C3** | Carbon accountability | Native on-chain carbon transparency; **annual Net Zero** via direct renewables or verified offsets (the framework's words); **GHG Protocol Scope 2 & 3**. As applied here: emissions covered by market-based renewable instruments or by **retired** carbon credits (the *offset-coverage rule*, §3.2); Scope 2 reported both location-based and market-based; Scope 3 categories listed in the methodology document. |
| **C4** | Regulatory readiness | CSRD / ESG reporting via APIs (machine-readable, ESRS-E1 aligned). As applied from v1.2: the machine-readability part, provided by the well-known declaration (§4); it maps onto the quantities of ESRS E1 and of the MiCA sustainability indicators, but it is not a regulatory filing. |

**What "Net Zero" means here.** The framework's "Net Zero" is, in the terms of the GHG Protocol and the Science Based Targets initiative, an **offset-coverage** claim: retired credits are set against gross emissions; both standards keep credits outside the emissions inventory, and the Science Based Targets initiative admits them towards net zero only to neutralise residual emissions. This profile therefore calls its test the *offset-coverage rule* and makes no consumer-facing claim of climate neutrality; in the EU, such a claim based on offsetting is prohibited for business-to-consumer commercial practices from 27 September 2026 (Directive (EU) 2024/825). The v1.1 names (`netZero`, "Net-Zero invariant") are kept where they are already published.

**Narrowings.** The profile applies the framework with stated narrowings, not "as given": it counts only retired credits with proof, it tests the carbon rule per operator per month (the framework states it annually), it defines the C1 boundary, and it applies C4 in its machine-readability part. The criteria and the 1 GWh threshold are design commitments; they are not a statement that any system meets them.

## 2. Allowed platforms (hot-path)

Use a platform whose **current public assessment** places its network energy below C1, on the C1 boundary of §1 (MiCA field S.8). Where several current assessments exist, the deployment cites the most recent one on that boundary and names any other current assessment that places the platform above C1; published figures for the same chain differ by a factor of two or more with the boundary and the data vendor. Candidate low-energy options used across this catalogue (each to be confirmed against such an assessment before deployment; none has been measured for these designs; naming a platform here is not a qualification):

| Platform | Why it qualifies |
|---|---|
| Hyperledger Fabric | Permissioned BFT; energy bounded by node count × node power. |
| NEAR Protocol | Sharded PoS. Holds South Pole's [climate neutral product label](https://www.southpole.com/news/auction-of-sustainable-blockchain-powered-art-funds-key-climate-projects) (2021), which rests on purchased offsets and is not an energy measurement. |
| Hedera | aBFT (hashgraph consensus). The vendor [states it is carbon-negative](https://hedera.com/blog/going-carbon-negative-at-hedera-hashgraph) through purchased offsets; this is not an energy measurement. |
| VeChainThor | Authority masternodes (Proof of Authority); footprint to be confirmed from an independent source. |
| **Any PoW chain (Bitcoin, …)** | ❌ **Forbidden** in any hot-path — see [CBECI](https://ccaf.io/cbnsi/cbeci) for current estimates of Bitcoin's electricity use. |

**Anchor.** Any public chain that is not proof-of-work MAY serve as an anchor-only layer for daily fingerprints (Merkle roots) of the hot-path events, provided its finality and its continued availability are stated in the methodology document; an anchor-only chain carries no operational events. The anchor is chosen per deployment. v1.1 named Polygon zkEVM; its sequencer was shut down and the network stopped producing blocks on 3 July 2026 ([Polygon](https://polygon.technology/polygon-zkevm)), so it is no longer an option. Ethereum L1 (about 0.0026 TWh/yr, i.e. 2.6 GWh/yr, after the move to proof of stake, per [CCRI's 2022 report](https://carbon-ratings.com/dl/eth-report-2022); about 7.87 GWh/yr in the Cambridge Centre for Alternative Finance's 2026 estimate) is above C1 and is anchor-only, never hot-path. The framework paper names further low-energy platforms as illustrations; naming is not qualification.

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
* `scope2KgCO2e` — electricity emissions for the period; the market-based figure where contractual instruments (certificates, power purchase agreements, supplier tariffs) are used, otherwise the location-based figure
* `scope2Method` *(proposed for v1.2, optional)* — `location-based` | `market-based`, the basis of `scope2KgCO2e`; absent means the basis stated in the methodology document. The location-based figure is reported beside the market-based one where both exist (GHG Protocol Scope 2 Guidance, dual reporting)
* `scope3KgCO2e` — amortised hardware embodied carbon + upstream. Amortising embodied carbon over service life is the approach of the Software Carbon Intensity specification (ISO/IEC 21031:2024); the GHG Protocol's Scope 3 guidance recommends counting capital goods in the period of acquisition. A deployment states which it follows, and the Scope 3 categories it includes, in its methodology document
* `gridIntensityRef` — e.g. `electricitymaps:DE-LU:2026-04-avg` (regional grid data give the location-based figure)
* `offsetsKgCO2e` — retired carbon credits allocated to the period. Registries retire credits in whole tonnes; one retirement MAY be allocated across months (and operators) by a signed allocation whose parts never exceed the tonnes retired
* `netZero` — boolean; MUST equal `(scope2 + scope3) <= offsets`. The field keeps its v1.1 name; it is the offset-coverage flag, not a net-zero finding
* `evidenceCid` — IPFS pointer to offset-retirement proofs

**Offset-coverage rule** (v1.1: "Net-Zero invariant"): `scope2KgCO2e + scope3KgCO2e <= offsetsKgCO2e`, with Scope 2 on the market-based method where instruments are used. It is what the framework calls Net Zero; see §1. A non-compliant period flags the operator until the next compliant attestation.

## 4. Disclosure (v1.2: the well-known document; the v1.1 API is retired)

From v1.2 the figures are published through the `sustainability-data` well-known URI of [draft-besleaga-sustainability-wellknown-07](https://datatracker.ietf.org/doc/draft-besleaga-sustainability-wellknown/) (17 September 2026; an Internet-Draft, work in progress), as the [SFC disclosure profile 1.0](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/PROFILE.md) describes. In short:

* Each declaration is one JSON document at `/.well-known/sustainability-data`, served over HTTPS with the media type `application/sustainability-data+json`.
* A declaration MAY carry an embedded `signed` member: a JWS (Compact Serialization) whose payload is the same object without `signed`. A valid signature shows integrity and continuity of the key; it does not show that a figure is accurate.
* Data the draft does not define goes under `extensions`, an object keyed by extension name (an absolute URI, compared as a string and never fetched). A reader ignores a name it does not implement.
* The network (consortium) publishes the annual declaration with `target-type: service`; C1 is evaluated only on that declaration. Each operator publishes from its own origin with `target-type: origin`.
* `methodology-uri` points to this profile and to the deployment's method; `disclosure-uri` points to a machine-readable index of filed reports. `verifiable-attestation-uri` is only for a statement signed by a party other than the publisher (for example an assurance provider), at most one per declaration.

| v1.1 endpoint (retired) | v1.2 replacement |
|---|---|
| `GET /v1/sustainability/operator/{did}` | the operator's own declaration at `/.well-known/sustainability-data` (`target-type: origin`) |
| `GET /v1/sustainability/network` | the network declaration (`target-type: service`, annual `reporting-period`) |
| `GET /v1/sustainability/csrd?period=…&operator=…` | `disclosure-uri`, naming an index of filed reports |
| `GET /v1/sustainability/sfc` | `methodology-uri`, plus the extensions of the SFC disclosure profile |

In v1.1 all responses were signed `application/jose+json`; in v1.2 the draft's `signed` member is the only signing scheme. The project documents in this folder still pin `SFC-PROFILE v1.1` and name the v1.1 endpoints; they move to v1.2 when v1.2 is final.

### 4.1 Evidence-to-disclosure bridge (proposal)

*This is a proposal. It is not implemented and it is not part of the SFC disclosure profile 1.0. It will be specified in the paper that describes this profile and in version 1.1 of the SFC disclosure profile ([draft](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/PROFILE-1.1-draft.md)).*

The network's annual declaration would carry, under a fourth extension name `https://andreibesleaga.com/sfc/extensions/ledger-evidence`, the head hash of each operator's attestation chains at the end of the period, the period boundaries, the event counts and the result of the offset-coverage rule (proposed members `network-offset-coverage` and, per operator, `offset-coverage-every-period`). Inside the declaration, the entry is covered by `signed`; a pointer placed only behind `disclosure-uri` would not be. A reader could then check at two depths:

* **Shallow:** one HTTPS GET; validate the document; verify `signed`; compare the annual energy figure with 1 GWh. No ledger access is needed.
* **Deep:** follow the pointer to the ledger; verify each event's signature against the operator's registered key; walk the `prev` chain back from the declared head; recompute the offset-coverage rule per period from the raw figures; sum; compare with the declaration.

The deep check would show whether the declaration agrees with the signed ledger record. It would not show that the operators' readings were true.

## 5. Hardware-lifecycle declaration (supports C2)

Every operator declares, in their Registry record:

```jsonc
{
  "nodeProfile": {
    "hardwareClass":   "general-purpose-x86 | arm64-server | rpi-cluster | cloud-instance",
    "asicForbidden":   true,
    "purchasedAt":     "2024-03-01",
    "expectedRetireAt":"2032-03-01",
    "reusePolicy":     "donate-to-education | resell-refurbished | recycle-WEEE-certified"
  }
}
```

Single-use ASIC-class mining hardware is rejected at onboarding. HSMs for institutional key custody are general-purpose security devices and are acceptable. `cloud-instance` *(proposed for v1.2)* covers rented virtual machines; it MAY carry the provider's signed instance identity document as evidence of the instance type, where the provider signs one. The declaration is a declaration: no check can establish what hardware exists, so C2 is reported as declared, never as passed.

## 6. Measurement sources

* [Crypto Carbon Ratings Institute (CCRI) Sustainability API](https://carbon-ratings.com/) — platform-level baseline.
* [Electricity Maps API](https://www.electricitymaps.com/) — per-node real-time grid intensity by grid zone.
* [GHG Protocol Corporate Standard](https://ghgprotocol.org/corporate-standard) — Scope 2 / Scope 3 boundaries. Scope 2 is reported location-based and market-based where contractual instruments exist; renewable electricity counts towards the offset-coverage rule only through the market-based figure. Scope 3 categories (for a node operator, typically purchased services, capital goods, fuel- and energy-related activities and waste) are listed in the methodology document. "No Scope 1 in the designs" is an assumption that the methodology document confirms (on-site backup generators would be Scope 1).
* [Commission Delegated Regulation (EU) 2025/422](https://eur-lex.europa.eu/eli/reg_del/2025/422/oj), Annex, Table 2, field S.8, and recital 8 (all nodes) — the energy boundary used for C1 (§1).
* Credit quality: the methodology document names the standard or label of the credits retired (for example the ICVCM Core Carbon Principles) and publishes the beneficiary and the period of each retirement at the registry. "Retired" is not the same as "high quality".

## 7. Conformance checks

| ID | Check |
|---|---|
| **C-SFC-1** | Latest `EnergyAttested` per operator within the last 35 days. |
| **C-SFC-2** | Trailing-12-month `kWhConsumed` total < **1 000 000 kWh** (= 1 GWh, C1), on the C1 boundary of §1. |
| **C-SFC-3** | Every operator's `nodeProfile.asicForbidden == true` and `hardwareClass` ∈ allowed list (C2). |
| **C-SFC-4** | Per-operator offset-coverage rule per period (C3; v1.1: Net-Zero invariant). |
| **C-SFC-5** | The network declaration conforms to draft-besleaga-sustainability-wellknown-07 and names its filed reports through `disclosure-uri` (C4). *(v1.1: `/v1/sustainability/csrd` returns a schema-valid ESRS-E1 payload.)* |
| **C-SFC-6** | The hot-path platform has a current public assessment placing its network energy below C1 on the C1 boundary (§2), and is not proof-of-work. *(v1.1: "appears in §2 or has a public assessment proving it fits within C1".)* |

## 8. Per-project platform pins

| Project | Hot-path | Anchor |
|---|---|---|
| Recycling Chain | Hyperledger Fabric | Polygon zkEVM |
| Certification Supply-Chain | Hyperledger Fabric or VeChainThor | Polygon zkEVM |
| Healthcare Pharma | Hyperledger Fabric | Polygon zkEVM |
| Paperless Billing | NEAR Protocol | — |
| Roaming Data Exchange | Hyperledger Fabric or Hedera | Polygon zkEVM |
| Sustainability Climate Change | Hedera (with Guardian) or Hyperledger Fabric | Polygon zkEVM |

*Anchor column:* Polygon zkEVM is the v1.1 pin. It stopped producing blocks on 3 July 2026; each deployment re-chooses its anchor under §2. NEAR's only published annual figure found (0.92 GWh, Crypto Risk Metrics data in a MiCA disclosure, July 2025 – July 2026, combined across three chains) is close to the cap.

## 9. Non-negotiables

* No PoW chain in any hot path.
* Operators publish monthly `EnergyAttested` and `CarbonAttested` — missing attestations make the operator `non-compliant`.
* Carbon credits counted by the offset-coverage rule MUST be retired (in whole tonnes, at the registry, with the beneficiary and the period published) and referenced with an auditable proof (CID of retirement record).
* If the chosen platform's assessed energy ever rises above C1, migrate to another §2 platform within one reporting period.

---

* **Profile version:** `SFC-PROFILE v1.2-draft` (2026-10-03). Previous: `SFC-PROFILE v1.1` (2026-05-23), deposited on Zenodo as [10.5281/zenodo.22681205](https://doi.org/10.5281/zenodo.22681205), unchanged.
* **Framework:** Besleaga (in press), https://doi.org/10.1145/3809296 *(accepted; in press)*. Future revisions of the paper trigger a new profile version.
* **Author identifier:** ORCID [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283).
* **Scope reminder:** this profile applies the framework — it does not reproduce its rationale or argumentation. Read the paper.

## Change log

* **v1.2-draft (2026-10-03).**
  * §4: the four bespoke `/v1/sustainability/…` endpoints are retired in favour of the `sustainability-data` well-known URI (draft-besleaga-sustainability-wellknown-07) and the SFC disclosure profile 1.0. The v1.1 endpoints are listed for reference. New §4.1 describes the evidence-to-disclosure bridge as a proposal.
  * §7: C-SFC-5 now checks the well-known declaration instead of the retired endpoint.
  * §2: the platform list is no longer called "verified". Offset-based labels (NEAR, Hedera) are described as what they are, not as energy evidence; the unsourced VeChainThor footprint is removed; the dead NEAR link is replaced; the out-of-date proof-of-work figure (100–170 TWh/yr) is removed in favour of a link to CBECI; the Ethereum figure is given its source.
  * §6: the out-of-date count of Electricity Maps zones is removed.
  * No energy or carbon figure in this profile or in the six designs has been measured. Energy budgets are design targets; the example values in §3 are invented.
  * The framework paper is cited as accepted, in press, without a year.
  * *Additions after the criteria reality check (canonical SFC decisions, 2026-10-04):*
    * §1: the C1 boundary ("system-wide") is defined as in Commission Delegated Regulation (EU) 2025/422, field S.8 (all nodes, as its recital 8 says; data-centre overhead is this profile's addition — wording corrected 2026-10-03 after an accuracy check of S.8); C3 is applied as an **offset-coverage rule** (the framework's "Net Zero"), with no consumer-facing neutrality claim (Directive (EU) 2024/825); C4 is applied in its machine-readability part; the narrowings are stated.
    * §2: qualification needs a current public assessment on the C1 boundary; "Hedera Hashgraph" → "Hedera"; the anchor is chain-agnostic, because Polygon zkEVM stopped producing blocks on 3 July 2026; Ethereum's post-Merge figures are given with both sources (CCRI 2022, CCAF 2026), both above C1; "qualifying platforms" in the framework paper → illustrations.
    * §3.2: Scope 2 basis (market-based where instruments are used, location-based reported beside it; proposed optional `scope2Method`); Scope 3 amortisation named as the SCI approach, a stated deviation from GHG Protocol guidance; retirements in whole tonnes, allocated to periods; `netZero` keeps its name and is described as the offset-coverage flag.
    * §4.1: proposed `ledger-evidence` members for the rule are named `network-offset-coverage` and `offset-coverage-every-period` (not yet published, so named accurately from the start).
    * §5: `cloud-instance` proposed; C2 is declared, never passed. §6: Scope 2/3 rules, the S.8 boundary and credit quality. §7: C-SFC-2, C-SFC-4 and C-SFC-6 reworded. §8: note on the anchor and on NEAR's margin. §9: retirement rules.
    * Field names and event names of v1.1 are unchanged; every addition is optional, so a v1.1 event stays a valid event.
* **v1.1 (2026-05-23).** Deposited on Zenodo, 10.5281/zenodo.22681205 (v1.1, 2026-09-09).
