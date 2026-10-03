# Sustainability-First Consensus (SFC) — Engineering Profile

> Catalogue-level engineering profile applying to all six projects in this folder. Short name: **the SFC ledger profile** (what a ledger records). Its companion, **the SFC disclosure profile** ([`sfc-compliance/PROFILE.md`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/PROFILE.md), version 1.1), says how the figures are published. "SFC 1.2" means ledger profile 1.2 together with disclosure profile 1.1.

**Status:** `SFC-PROFILE v1.2`, 2026-10-03. It supersedes `SFC-PROFILE v1.1` (2026-05-23), which stays on Zenodo unchanged as [10.5281/zenodo.22681205](https://doi.org/10.5281/zenodo.22681205). The v1.1 endpoints are retired; §8 maps each of them to its replacement.

## Citation

This profile applies the framework defined in:

> Besleaga, A. N. (in press). *"Sustainability-First Consensus" Ledgers for a Green Digital Future.* Communications of the ACM (Viewpoint). Association for Computing Machinery. https://doi.org/10.1145/3809296 — *accepted; in press. The DOI resolves once ACM publishes.*
> ORCID: [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283)

For the full framework — rationale, motivation and argumentation — consult the paper. This document covers only the engineering parameters needed to apply the framework here. Any deployment claiming SFC alignment MUST cite the paper above.

**Companion documents:**
- *The SFC disclosure profile* 1.1 ([`sfc-compliance/PROFILE.md`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/PROFILE.md) in the `rfc-sustainability-wellknown` repository, adopted 2026-10-03; [version 1.0](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/c787378/sfc-compliance/PROFILE.md), 2026-09-16, is kept as `PROFILE-1.0.md`), which says how an SFC declaration is published at `/.well-known/sustainability-data`.
- [`draft-besleaga-sustainability-wellknown-07`](https://datatracker.ietf.org/doc/draft-besleaga-sustainability-wellknown/) (17 September 2026, Internet-Draft, work in progress), the disclosure format this profile publishes into.

---

## 1. Conventions

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL are to be read as in BCP 14
[R1, R2] when, and only when, they appear in capitals.

Terms:
- **Operator**: a party that runs one or more nodes of the ledger and is registered in its Registry with a
  decentralised identifier (DID) and a public signing key.
- **Period**: one calendar month, written as its first and last day (`from`, `to`, inclusive, UTC).
- **Attestation**: one signed `EnergyAttested` or `CarbonAttested` event.
- **Chain**: the sequence of one operator's attestations of one type, linked by `prev`.
- **Head**: the hash of the most recent attestation in a chain at a stated point.
- **Network declaration**: the annual declaration about the whole network, published at the network's origin.
- **Operator declaration**: a declaration about one operator, published at that operator's origin.
- **Verifier**: any party running the checks of §7 or §9.
- **Retirement**: the cancellation of one or more whole carbon credits (one tonne of CO2-equivalent each) in a
  registry, in the operator's name.
- **Allocation**: a statement signed by the operator that assigns parts of one retirement, in kilograms, to
  periods; its parts never exceed the tonnes retired.
- **Offset coverage**: the condition of §4, retired credits at least equal to a period's emissions. The framework
  calls it "Net Zero"; it is not net zero in the sense of the GHG Protocol or the Science Based Targets initiative
  [R3, R4]: both keep credits outside the emissions inventory, and the SBTi admits them towards net zero only to neutralise residual emissions.

Hashing is SHA-256 over the RFC 8785 [R5] (JSON Canonicalization Scheme) serialisation of the whole event,
signature included. Hashes are written as 64 lowercase hexadecimal characters. Signatures are Ed25519 [R6] unless
the Registry records another algorithm for the operator's key.

## 2. Criteria and platform rule

### 2.1 The four criteria (as applied)

| # | Criterion | As this profile applies it |
|---|---|---|
| C1 | Energy consumption | Total annual network energy consumption below 1 GWh (0.001 TWh). Threshold from the framework. The network boundary ("system-wide" in the framework) is the energy used for the validation of transactions and the maintenance of the integrity of the ledger, per calendar year, as in Delegated Regulation (EU) 2025/422, Annex, Table 2, field S.8, counted over all its nodes as its recital 8 says [R7]; this profile counts data-centre overhead within it. Gateways, off-ledger storage, backups and any anchor-chain share are declared in the methodology document as included or excluded; client devices are excluded. |
| C2 | Hardware lifecycle | General-purpose hardware with a use beyond the system; no single-use ASICs. |
| C3 | Carbon accountability | On-ledger carbon records; emissions covered by market-based renewable instruments or by retired carbon credits (the framework calls this net zero); Scope 2 and Scope 3 as the GHG Protocol defines them [R3, R8, R9], Scope 2 reported both location-based and market-based where contractual instruments exist, Scope 3 categories listed in the methodology document. The framework states the rule annually; **this profile checks it per operator per month**, which is stricter (§4). |
| C4 | Regulatory readiness | Figures readable by machine without prior arrangement. Under v1.2 the well-known declaration (§8) provides this part of the framework's criterion, which also asks for auditability compatible with CSRD and ESG reporting; the declaration maps onto quantities of ESRS E1 and of the MiCA sustainability indicators but is not a regulatory filing. |

The profile applies the framework with stated narrowings: it gives C1 a boundary, counts only retired credits with
proof, tests the carbon rule per operator per month, and applies C4 in its machine-readability part.

The criteria and the 1 GWh threshold are design constraints a conforming system commits to meeting. They are not
a statement that any system meets them. Published estimates for low-energy public ledgers range from well below to
above 1 GWh a year, depending on the boundary and the data provider [R10, R11, R12, R13].

### 2.2 Hot path and anchor

- A **hot-path** ledger is one that carries the system's operational events. A hot-path ledger MUST have a current
  public assessment of its network energy consumption on the boundary of C1 placing it below C1. Where several
  current assessments exist, the deployment cites the most recent one on that boundary and names any other current
  assessment that places the platform above C1.
- A ledger that uses proof-of-work consensus MUST NOT be used in any hot path.
- Any public chain that is not proof-of-work MAY be used as an **anchor-only** layer that receives periodic (in the
  designs, daily) fingerprints (Merkle roots) of the hot-path events, provided the methodology document states its
  finality and its continued availability. An anchor-only chain carries no operational events. The anchor is chosen
  per deployment; this profile names none.
- The designs name candidate hot-path platforms (Hyperledger Fabric, NEAR Protocol, Hedera, VeChainThor, R5 Corda).
  Naming a platform here is not a qualification. Each deployment cites the public assessment it relies on
  (C-SFC-6).
- **Migration clause.** If the chosen hot-path platform's assessed energy rises above C1 in any 12-month window, the
  deployment moves to another qualifying platform within one reporting period. If the anchor chain stops producing
  blocks, the deployment moves its anchor to another chain within one reporting period.

*Informative.* What the designs say about the candidate platforms (none of these notes is an energy assessment;
naming a platform here is not a qualification):

| Platform | Note |
|---|---|
| Hyperledger Fabric | Permissioned BFT; energy bounded by node count × node power. |
| NEAR Protocol | Sharded PoS. Holds South Pole's [climate neutral product label](https://www.southpole.com/news/auction-of-sustainable-blockchain-powered-art-funds-key-climate-projects) (2021), which rests on purchased offsets and is not an energy measurement. |
| Hedera | aBFT (hashgraph consensus). The vendor [states it is carbon-negative](https://hedera.com/blog/going-carbon-negative-at-hedera-hashgraph) through purchased offsets; this is not an energy measurement. |
| VeChainThor | Authority masternodes (Proof of Authority); footprint to be confirmed from an independent source. |
| **Any PoW chain (Bitcoin, …)** | ❌ **Forbidden** in any hot-path — see [CBECI](https://ccaf.io/cbnsi/cbeci) for current estimates of Bitcoin's electricity use. |

Ethereum L1 (about 0.0026 TWh/yr, i.e. 2.6 GWh/yr, after the move to proof of stake, per [CCRI's 2022 report](https://carbon-ratings.com/dl/eth-report-2022); about 7.87 GWh/yr in the Cambridge Centre for Alternative Finance's 2026 estimate) is above C1 and is anchor-only, never hot-path.

### 2.3 Per-project platform pins

| Design | Hot path | Anchor |
|---|---|---|
| Recycling Chain | Hyperledger Fabric | a public chain, to be chosen (v1.1: Polygon zkEVM) |
| Certification Supply-Chain | Hyperledger Fabric or VeChainThor | a public chain, to be chosen (v1.1: Polygon zkEVM) |
| Healthcare Pharma | Hyperledger Fabric | a public chain, to be chosen (v1.1: Polygon zkEVM) |
| Paperless Billing | NEAR Protocol | none |
| Roaming Data Exchange | Hyperledger Fabric or Hedera | a public chain, to be chosen (v1.1: Polygon zkEVM) |
| Sustainability Climate Change | Hedera (with Guardian) or Hyperledger Fabric | a public chain, to be chosen (v1.1: Polygon zkEVM) |

The pins are the profile's choices; each design's own architecture document still presents its platform as a
choice. The v1.1 anchor, Polygon zkEVM, stopped producing blocks on 3 July 2026 [R14]; the design documents in this
folder keep the old name, with a note. NEAR's only published annual figure found (0.92 GWh, Crypto Risk Metrics data in
a MiCA disclosure, July 2025 – July 2026, combined across three chains) is close to the cap.

## 3. Attestation events

### 3.1 Envelope

Every attestation uses the envelope shared by five of the six designs:

```jsonc
{
  "type":    "EnergyAttested" | "CarbonAttested",
  "subject": "<operator DID>",
  "actor":   "<operator DID>",
  "prev":    "<hash of the previous event of the same type for the same subject, or null>",
  "ts":      "<RFC 3339 date-time of emission>",
  "payload": { /* type-specific, §3.2 and §3.3 */ },
  "sig":     { "alg": "Ed25519", "value": "<base64url signature over the canonical event without sig>" }
}
```

Rules:
1. An operator emits one `EnergyAttested` and one `CarbonAttested` per period, after the period ends. A second
   attestation of the same type for the same period is allowed only as a correction under rule 5. The
   *effective* attestation of a period is the latest one in chain order that no later attestation supersedes;
   every sum and every check uses effective attestations only, so each period is counted once.
2. `subject` and `actor` are the same operator DID. (Delegated signing, used by three of the six designs for
   sensors, is out of scope for attestations; the operator signs its own.)
3. `prev` is `null` only for the first event of its type for that operator.
4. The ledger MUST reject an attestation whose `prev` is not the current head of that operator's chain of that type.
5. Attestations are never edited or deleted. A correction is a new attestation for the same period, chained in the
   usual way, with `payload.supersedes` set to the hash of the attestation it corrects.
6. The ledger MUST reject an attestation whose `sig` does not verify under the operator's key that is current in the
   Registry when the attestation is submitted. Verifiers judge key validity at the ledger's commit time of the event,
   never at `ts`.
7. `ts` MUST NOT be earlier than 00:00 UTC on the day after `period.to`.
8. A reader ignores any member it does not recognise in an event, a payload, a Registry entry or an allocation;
   such a member still enters every hash and signature computed over the object that carries it.

### 3.2 `EnergyAttested` payload (supports C1)

| Field | Type | Meaning |
|---|---|---|
| `period` | `{ from, to }` full dates | the month covered |
| `nodeCount` | integer ≥ 0 | nodes the operator ran in the period |
| `kWhConsumed` | number ≥ 0 | energy consumed by those nodes in the period, in kWh, on the boundary of C1 as the methodology document applies it to the operator |
| `measurementMethod` | string | how the figure was produced; defined in the operator's methodology document; SHOULD be one of `hardware-metered`, `hardware-estimated`, `cloud-billing`, `third-party-modeled` |
| `evidenceCid` | string | content identifier of the off-ledger evidence (meter exports, model inputs) |
| `supersedes` | string, 64 hex | OPTIONAL (new in v1.2): hash of the attestation this one corrects (§3.1 rule 5) |

### 3.3 `CarbonAttested` payload (supports C3)

| Field | Type | Meaning |
|---|---|---|
| `period` | `{ from, to }` | the same month as the matching `EnergyAttested` |
| `scope2KgCO2e` | number | purchased-electricity emissions for the period: the market-based figure where contractual instruments (certificates, power purchase agreements, supplier tariffs) are used, otherwise the location-based figure |
| `scope2Method` | `"location-based"` \| `"market-based"` | OPTIONAL (new in v1.2): the method of `scope2KgCO2e`; absent means the method stated in the methodology document. Where both figures exist, the location-based one is reported beside the market-based one in the methodology document (GHG Protocol dual reporting [R8]) |
| `scope3KgCO2e` | number | value-chain emissions for the period, in the categories listed in the methodology document. Capital goods are counted in the period of acquisition, as the GHG Protocol's Scope 3 Standard recommends [R9]; a deployment that amortises them over service life (as the Software Carbon Intensity specification, ISO/IEC 21031:2024 [R15], does) states this as a deviation. (v1.1 defined the field as amortised embodied carbon plus upstream emissions; a v1.1 figure is read as using that deviation.) |
| `gridIntensityRef` | string | the grid-intensity source, zone and period used; regional grid data give the location-based figure |
| `offsetsKgCO2e` | number ≥ 0 | retired carbon credits **allocated** to this period, in the operator's name (§4) |
| `netZero` | boolean | the offset-coverage flag; MUST equal `scope2KgCO2e + scope3KgCO2e <= offsetsKgCO2e`. The field keeps its v1.1 name; it is not a net-zero finding |
| `evidenceCid` | string | content identifier of the retirement records (registry, serial numbers) and of the allocation |
| `supersedes` | string, 64 hex | OPTIONAL (new in v1.2): as in §3.2 |

## 4. The offset-coverage rule

(v1.1: "the net-zero invariant".) For operator *o* and period *m*, write S2(o,m), S3(o,m) and R(o,m) for
`scope2KgCO2e`, `scope3KgCO2e` and `offsetsKgCO2e`, and z(o,m) for `netZero`.

- **Consistency:** z(o,m) = [ S2(o,m) + S3(o,m) ≤ R(o,m) ]. A verifier recomputes the right-hand side from the
  signed figures and compares it with the flag. A mismatch is a failure of the attestation, whatever the flag says.
- **Compliance:** z(o,m) = true for every period, evaluated on effective attestations (§3.1 rule 1). A non-compliant
  period flags the operator until its next compliant attestation. A month in which the operator was active in the
  Registry and has no effective `CarbonAttested` makes the operator non-compliant.
- **Network consequence:** if every operator is compliant in every month of year *y*, then
  Σ_o Σ_m (S2 + S3) ≤ Σ_o Σ_m R over that year, because the inequalities add. This holds **only if each retired
  tonne is allocated once, to one period, for one operator**. The converse does not hold: a network can meet the
  annual sum while one operator fails a month.

In words: every month, each operator's emissions, with Scope 2 on the market-based method where contractual
instruments are used, must not exceed the retired credits allocated to that month, and the yes/no flag it signs must
be the true answer to that comparison, so that nobody has to believe the flag.

**Retirements and allocation.** Registries retire credits in whole tonnes [R16]. Offsets counted towards the rule
MUST reference retired credits with an auditable proof (`evidenceCid`). One retirement MAY be allocated across
periods by an allocation signed by the operator, whose parts never exceed the tonnes retired; the part allocated to
a period is that period's `offsetsKgCO2e`, and the unallocated remainder is carried forward. An allocation is not
an attestation: it sits on neither of the operator's chains and has no ledger commit time, so the key rule of
§3.1 rule 6 cannot select a key for it, and a verifier accepts its signature under **any key the Registry has
recorded for the operator**. An allocation cannot by itself raise a period's credits, because the part it gives a
period must equal that period's `offsetsKgCO2e`, which is signed under the key rule. The operator MUST
publish, at the registry, the beneficiary and the period of each retirement, and SHOULD name in its methodology
document the standard or label of the credits retired; "retired" does not mean "high quality".

**What the rule claims.** The rule tests whether retired credits cover gross emissions. It does not ask for
reductions and does not judge the credits. A conforming system MUST NOT present the rule's result as a
consumer-facing claim of climate neutrality; in the EU such a claim, based on offsetting, is prohibited for
business-to-consumer commercial practices from 27 September 2026 [R17].

**Known gap.** No check in this profile stops the same retired tonne from being allocated by two operators. A design
proposal for single allocation of retirements is in the paper that describes this profile (in preparation).

## 5. Hardware declaration (supports C2)

Each operator declares in its Registry record:

```jsonc
{ "nodeProfile": {
    "hardwareClass":   "general-purpose-x86 | arm64-server | rpi-cluster | cloud-instance",
    "asicForbidden":   true,
    "purchasedAt":     "<full date>",
    "expectedRetireAt":"<full date>",
    "reusePolicy":     "donate-to-education | resell-refurbished | recycle-WEEE-certified" } }
```

Single-use ASIC-class mining hardware is rejected at onboarding. Hardware security modules for key custody are
general-purpose security devices and are accepted. `cloud-instance` (new in v1.2) covers rented virtual machines; it
MAY carry the provider's signed instance identity document as evidence of the instance type, where the provider
signs one. The declaration is a declaration: C2 is reported as declared, never as passed (§10).

## 6. Measurement binding

Every energy figure names its method (§3.2), and the operator's methodology document defines that method. The
profile binds these sources and rules:
- the C1 boundary of §2.1 (field S.8 of Delegated Regulation (EU) 2025/422 [R7]), with the declared extensions;
- a platform-level energy assessment for the hot path (the designs name the Crypto Carbon Ratings Institute);
- regional grid-intensity data for the location-based Scope 2 figure (the designs name Electricity Maps);
- GHG Protocol scope boundaries for Scope 2 and Scope 3 [R3]; Scope 2 reported location-based and market-based where
  contractual instruments exist, one method for the in-band figure across the network, stated in the methodology
  document; renewable electricity counts towards the rule only through a market-based Scope 2 figure;
- the Scope 3 categories included (for a node operator, typically purchased services, capital goods, fuel- and
  energy-related activities and waste) and the treatment of capital goods (§3.3);
- "no Scope 1 in the designs" is an assumption that the methodology document confirms (an on-site backup generator
  would be Scope 1).

The profile does not define how energy is measured. It requires that the method be named and published.

## 7. Conformance checks

| ID | Check | Depth | Data needed |
|---|---|---|---|
| C-SFC-1 | Each operator's latest `EnergyAttested` that carries no `supersedes` is no more than 35 days old at the time of the check, judged by the ledger's commit time. | ledger | events |
| C-SFC-2 (ledger form) | Trailing-12-month sum of `kWhConsumed` over all operators < 1 000 000 kWh, on the boundary of C1. | ledger | events |
| C-SFC-2 (disclosure form) | The network declaration for a complete calendar year (`reporting-period` `YYYY`, `target-type` `service`) reports `energy-consumption` below 1 GWh after unit conversion. Evaluated **only** on that declaration; an operator or sub-annual declaration cannot pass or fail it. | disclosure | declaration |
| C-SFC-3 | Every operator's `nodeProfile.asicForbidden` is true and `hardwareClass` is in the allowed list. | ledger | Registry |
| C-SFC-4 | For every operator and every month in which it was active in the Registry, an effective `CarbonAttested` exists, its `netZero` equals the recomputed comparison, and the comparison holds (§4). | ledger | events + Registry |
| C-SFC-5 | The network declaration conforms to draft -07 and carries `disclosure-uri` naming a machine-readable index of the filed reports. | disclosure | declaration |
| C-SFC-6 | The hot-path platform is not proof-of-work and has a current public assessment placing its energy below C1 on the boundary of C1, cited as §2.2 requires. | either | assessment |
| C-SFC-7 | **Bridge consistency.** The `ledger-evidence` entry of the declaration agrees with the ledger: it lists exactly the operators active in the Registry for the period, and its heads, counts and totals recompute from the signed events (§9.4). | ledger | events + Registry + declaration |

## 8. Disclosure (replaces the v1.1 Sustainability API)

Disclosure follows the SFC disclosure profile 1.1 [R18], which this section does not restate. In short:

| Was (v1.1) | Now (v1.2) |
|---|---|
| `GET /v1/sustainability/operator/{did}` | the **operator declaration** at the operator's own origin: `target` = the operator's host, `target-type` = `origin`, monthly or annual `reporting-period` |
| `GET /v1/sustainability/network` | the **network declaration** at the network's origin: `target-type` = `service`, `reporting-period` = `YYYY` |
| `GET /v1/sustainability/csrd?period=…&operator=…` | `disclosure-uri`, naming a machine-readable index of filed reports |
| `GET /v1/sustainability/sfc` | `methodology-uri` (pointing at this profile and the deployment's methodology) plus the `ledger-evidence` extension (§9) |
| `application/jose+json` responses | the draft's `signed` member (JWS Compact, EdDSA or ES256, `cty` = `sustainability-data+json`) |

Mapping of ledger figures to draft members [R19] (members stable since revision -04 unless marked):

| Ledger | Declaration member |
|---|---|
| Σ `kWhConsumed` | `energy-consumption` with `energy-unit` |
| Σ `scope2KgCO2e`, Σ `scope3KgCO2e` | `scope-2`, `scope-3` with `carbon-unit` |
| S2 + S3 (no Scope 1 in the designs) | `carbon-footprint`, gross, never reduced by credits |
| `measurementMethod` | `measurement-method` (when all operators agree; otherwise a description, and the methodology document lists each and says which parts are measured and which modelled, as the disclosure profile, §2, requires) |
| `scope2Method` (or the method stated in the methodology document) | `carbon-accounting` |
| `gridIntensityRef` | `carbon-intensity-gCO2e-per-kWh` (period-weighted), source named in the methodology document |
| `nodeProfile` | `general-purpose-hardware` (true), `single-use-asic-required` (false) and `embodied-carbon-in-scope-3` (true only when the period's `scope3KgCO2e` includes hardware embodied emissions) in the `hardware-lifecycle` extension |
| Σ `offsetsKgCO2e` | `offsets-retired-tCO2e` in the `carbon-neutrality` extension (kg ÷ 1000; may be fractional, because it is an allocation of whole-tonne retirements) |
| the rule's results | `net-zero-status` in `carbon-neutrality` (the published 1.0 name, meaning offset coverage): `achieved` when every counted operator met the rule in every month of the period; otherwise `not-achieved` when no credits were allocated to the period, and `partial` when some were |
| heads, counts, totals, rule results | the `ledger-evidence` extension (-07 `extensions`; defined in disclosure profile 1.1, §5.5) |

A period in which a counted operator has no effective attestation of a type is *silent* for that type. The
top-level members derived from a silent type are omitted, as draft -07 omits a sum when a contributing entry is
silent, since it would understate the period: `energy-consumption` and `energy-unit` for energy; `scope-2`,
`scope-3`, `carbon-footprint` and `carbon-accounting` for carbon; and `carbon-intensity-gCO2e-per-kWh` when either
type is silent. The `ledger-evidence` entry still carries the sums of the attestations that exist, and a silent
carbon month makes `offset-coverage-every-period` false.

A declaration that claims this profile and carries the `ledger-evidence` extension MUST NOT apply the optional
noise of draft -07, Section 7 (Privacy Considerations) [R19]: noised figures could never equal the ledger totals that
the shallow check (§9.3, step 5) and the deep check (§9.4, C-SFC-7) recompute. Monthly or annual periods already meet
that section's advice against reporting finer than 24 hours; a publisher concerned about ratio-based fingerprinting
omits the derived members instead, as the same section allows.

A declaration that claims this profile MUST carry a `signed` member. Retired credits never reduce
`carbon-footprint`; the offset-coverage position lives in the `carbon-neutrality` extension. At network level
`offsets-retired-tCO2e` carries the operators' retirements allocated to the period, made in their own names;
disclosure profile 1.0 defined it as credits retired in the publisher's name, and disclosure profile 1.1 widens the
definition to the counted operators' retirements; the methodology document says which applies.
`verifiable-attestation-uri` is reserved for a statement signed by a party other than the publisher (for example an
auditor who ran C-SFC-7), and never carries the ledger pointer.

## 9. The `ledger-evidence` extension

### 9.1 Name

`https://andreibesleaga.com/sfc/extensions/ledger-evidence`

The name is an identifier compared octet for octet and never dereferenced, as draft -07 requires for extension names.
It is defined by the SFC disclosure profile 1.1 (§5.5, adopted 2026-10-03), whose member table is the one below.

### 9.2 Members

| Member | JSON type | Required | Meaning |
|---|---|---|---|
| `profile-version` | string | yes | `"1.2"` |
| `ledger-access-uri` | string, absolute https URI | yes | where a verifier obtains the attestation events and the Registry keys; access MAY be restricted to consortium members and auditors |
| `hash-algorithm` | string | yes | `"sha-256"` |
| `event-encoding` | string | yes | `"rfc8785"` |
| `period-start`, `period-end` | string, full date | yes | first and last day covered; both inside the declaration's `reporting-period` |
| `operators` | array of objects, at least one | yes | one entry per operator counted (exactly one in an operator declaration) |
| `network-offset-coverage` | boolean | network level only | Σ(S2 + S3) ≤ Σ R over the period, from the totals below |
| `anchor` | object | no | `{ "ledger": <name of the public chain>, "reference": <transaction or root identifier> }` for the last anchor covering `period-end` |

Each `operators` entry:

| Member | JSON type | Meaning |
|---|---|---|
| `operator` | string | the operator's DID, as in `subject` |
| `energy-head`, `carbon-head` | string, 64 hex | hash of the latest attestation of each type, in chain order, whose period ends on or before `period-end` |
| `energy-events`, `carbon-events` | integer | number of attestations of each type whose period lies within the declared period, corrections included |
| `kwh` | number | Σ `kWhConsumed` over the effective attestations among those events (§3.1 rule 1) |
| `scope2-kgco2e`, `scope3-kgco2e`, `offsets-kgco2e` | number | Σ of the matching payload fields of the effective attestations |
| `offset-coverage-every-period` | boolean | true when every month of the period has an effective `CarbonAttested` whose `netZero` is true and correct |

The members for the rule are named for what it tests; they are new, so they do not carry the framework's "net zero"
label. Totals are computed with exact decimal arithmetic over the numbers as they appear in the RFC 8785
serialisation of each event.

### 9.3 Shallow check (needs only HTTPS)

1. Fetch `https://<origin>/.well-known/sustainability-data` over HTTPS; require the media type.
2. Validate against draft -07 (schemas and prose rules).
3. Verify `signed` with a key obtained out of band or pinned from an earlier retrieval.
4. At network level for a complete year, run C-SFC-2 (disclosure form) and C-SFC-5.
5. Check internal coherence: the `operators` sums agree with `energy-consumption`, `scope-2`, `scope-3` and
   `offsets-retired-tCO2e`, where those members are present, within unit conversion and rounding; `network-offset-coverage` agrees with the totals.
6. Record: attributed to the origin; integrity verified (or not); figures self-asserted; accuracy unknown.

### 9.4 Deep check (needs ledger read access)

1. Obtain read access through `ledger-access-uri`.
2. Confirm that the `operators` list names exactly the operators the Registry shows as active during the declared
   period (network level), so that no operator has been left out.
3. For each operator entry, fetch the attestations of each type for that subject within the declared period and
   verify each signature against the key the Registry held for the operator when the ledger committed the event
   (never at `ts`).
4. Walk `prev` back from the declared head: every event must link, the count must match (corrections included), and
   no two events may share a `prev` (a fork).
5. Recompute every `netZero` on the effective attestations, and confirm that no active month lacks one (C-SFC-4).
6. Recompute every sum and compare exactly with the entry; recompute `network-offset-coverage`.
7. Optionally, recompute the anchored Merkle root from all hot-path events of that day (not only attestations) and
   compare it with the public chain.
8. Optionally, follow `evidenceCid` to the retirement records and the allocation, and confirm that the credits are
   retired in the operator's name with the beneficiary and period published, that the allocation's parts do not
   exceed the tonnes retired, and that its signature verifies under a key the Registry has recorded for the
   operator (§4).

### 9.5 What the checks establish

- The shallow check establishes that the origin published these figures and, with a trusted key, that they were not
  altered after signing.
- The deep check establishes that **the declaration agrees with the signed ledger record**. A declaration that
  misstates the record is detectable by anyone with read access to the ledger.
- Neither check establishes that an operator's readings were true. A correctly signed false reading is still false.
  Independent assurance about the readings comes only from a third party's signed statement, linked by
  `verifiable-attestation-uri`.

## 10. What a conformance statement may claim

MAY say: the declaration conforms to draft -07; the declared annual network figure is below, at or above 1 GWh (with
figure and unit, and the boundary); the declaration agrees with the ledger record at the stated heads (after a deep
check, naming who ran it and when); a named party attested to the figures (once its statement has been fetched and
verified); the operators' retired credits covered their emissions under the offset-coverage rule (naming the rule).

MUST NOT say: that a figure is verified, true or accurate; that the system is sustainable, green, carbon neutral or
net zero as a finding; that the rule's result supports a consumer-facing claim of climate neutrality; that C1 passed
on an operator or sub-annual declaration; that C2 passed (no document establishes what hardware exists); that a valid
signature is evidence about a figure.

## 11. Compatibility 1.0 / 1.1 / 1.2

*Informative.* The SFC profiles carry two version lines: the **ledger profile**
(what a ledger records; v1.1 deposited on Zenodo, v1.2 this text) and the **disclosure profile** (how an SFC system
publishes under draft -07; `sfc-compliance/PROFILE.md` 1.1, adopted 2026-10-03; 1.0 kept as `PROFILE-1.0.md`). "SFC 1.2" means ledger profile 1.2
together with disclosure profile 1.1.

| Version | What it adds | What stays compatible | What a consumer must do |
|---|---|---|---|
| Ledger profile 1.1 (2026-05-23, Zenodo 10.5281/zenodo.22681205) | `EnergyAttested` and `CarbonAttested`, the net-zero rule, checks C-SFC-1 to C-SFC-6, four bespoke HTTP endpoints | The events and the rule carry into 1.2 unchanged | Nothing new; the four endpoints are retired by 1.2 (§8 maps each to the declaration) |
| Disclosure profile 1.0 (2026-09-16, public) | Publication under draft -07; network level `target-type` `service`, operator level `origin`; three extension names (`hardware-lifecycle`, `carbon-neutrality`, `network-topology`) | Every 1.0 declaration stays valid under 1.1 | Read the three extensions; reach a ledger trail only through `disclosure-uri` |
| Disclosure profile 1.1 (adopted 2026-10-03) | A fourth extension name, `https://andreibesleaga.com/sfc/extensions/ledger-evidence`; a second route to the trail, inside the signed declaration; the C1 boundary; "net zero" explained as offset coverage; allocated retirements in `offsets-retired-tCO2e` | The three 1.0 names keep their meaning; a consumer that implements only 1.0 ignores the new name, as draft -07 requires for any extension it does not implement | To use the bridge, implement `ledger-evidence` (§9) and the shallow check (§9.3) |
| Ledger profile 1.2 (this text, 2026-10-03) | Fixes the `ledger-evidence` members (§9.2); C-SFC-2 in two forms; C-SFC-7; the correction rule (§3.1 rule 5, optional `supersedes`) with effective attestations; current-key and timestamp acceptance rules (§3.1 rules 6, 7); method strings and the Scope 2 method must be stated (optional `scope2Method`); the offset-coverage rule with whole-tonne allocation; the C1 boundary; a chain-agnostic anchor; `cloud-instance`; §10 | Event names and payload fields of 1.1 are unchanged; 1.2 adds only the optional `payload.supersedes` and `payload.scope2Method`, one `hardwareClass` value and two acceptance rules for new events; a 1.1 event emitted after its period ends is a valid 1.2 event | Use the latest attestation for a corrected period and count the period once (§3.1 rule 1); run C-SFC-7 for a deep check (§9.4) |

## References

- [R1] Bradner S. Key words for use in RFCs to indicate requirement levels. RFC 2119, BCP 14. IETF; 1997 Mar. doi:10.17487/RFC2119
- [R2] Leiba B. Ambiguity of uppercase vs lowercase in RFC 2119 key words. RFC 8174, BCP 14. IETF; 2017 May. doi:10.17487/RFC8174
- [R3] World Resources Institute, World Business Council for Sustainable Development. The Greenhouse Gas Protocol: a corporate accounting and reporting standard. Rev ed. Washington (DC): WRI; Geneva: WBCSD; 2004 Mar. Available from: https://ghgprotocol.org/corporate-standard
- [R4] Science Based Targets initiative. SBTi Corporate Net-Zero Standard, version 1.3.1 [Internet]. London: SBTi; 2026 Apr, criterion C12, p. 36–37 (the applicable version for target validation in 2026; version 2.0 published June 2026). Available from: https://files.sciencebasedtargets.org/production/files/Net-Zero-Standard.pdf
- [R5] Rundgren A, Jordan B, Erdtman S. JSON Canonicalization Scheme (JCS). RFC 8785. RFC Editor (Independent Submission); 2020 Jun. doi:10.17487/RFC8785
- [R6] Josefsson S, Liusvaara I. Edwards-curve digital signature algorithm (EdDSA). RFC 8032. Internet Research Task Force (CFRG); 2017 Jan. doi:10.17487/RFC8032
- [R7] European Commission. Commission Delegated Regulation (EU) 2025/422 of 17 December 2024 supplementing Regulation (EU) 2023/1114 of the European Parliament and of the Council with regard to regulatory technical standards specifying the content, methodologies and presentation of information in respect of sustainability indicators in relation to adverse impacts on the climate and other environment-related adverse impacts. Off J Eur Union. 2025 Mar 31;L 2025/422. Available from: http://data.europa.eu/eli/reg_del/2025/422/oj
- [R8] Sotos M. GHG Protocol Scope 2 Guidance: an amendment to the GHG Protocol Corporate Standard. Washington (DC): World Resources Institute; 2015. Section 1.5.1 (dual reporting). Available from: https://ghgprotocol.org/scope-2-guidance
- [R9] World Resources Institute, World Business Council for Sustainable Development. Corporate Value Chain (Scope 3) Accounting and Reporting Standard. Washington (DC): WRI; Geneva: WBCSD; 2011 Sep. Box 5.4. Available from: https://ghgprotocol.org/corporate-value-chain-scope-3-standard
- [R10] Gallersdörfer U, Klaaßen L, Stoll C. Energy efficiency and carbon footprint of proof of stake blockchain protocols. Dingolfing: Crypto Carbon Ratings Institute; 2022 Jan. Available from: https://carbon-ratings.com/dl/pos-report-2022
- [R11] Crypto Carbon Ratings Institute. PoS benchmark study 2023: energy efficiency and carbon footprint of PoS blockchain networks and platforms. Dingolfing: CCRI; 2023 Oct. Available from: https://carbon-ratings.com/dl/pos-report-2023
- [R12] Change Securities B.V. Mandatory information on principal adverse impacts on the climate and other environment-related adverse impacts of the consensus mechanism: Solana. Change Invest; last review 2026 Apr 23 [cited 2026 Oct 3]. Available from: https://assets.changeinvest.com/esg-reporting/SOL.pdf
- [R13] AMINA (Austria) AG. Sustainability indicators for crypto-assets: disclosures pursuant to Article 66(5) MiCA. Report provided by Crypto Risk Metrics GmbH; 2026 Jul 29 [cited 2026 Oct 3]. Available from: https://eu.aminagroup.com/wp-content/uploads/2026/08/2026-07-30-sustainability-indicators.pdf
- [R14] Polygon Labs. Polygon zkEVM: Mainnet Beta sunset and fund claims [Internet]. [cited 2026 Oct 3]. Available from: https://polygon.technology/polygon-zkevm
- [R15] ISO/IEC. ISO/IEC 21031:2024. Information technology — Software Carbon Intensity (SCI) specification. 1st ed. Geneva: ISO; 2024 Mar. Available from: https://www.iso.org/standard/86612.html
- [R16] Verra. Verra Registry Terms of Use, July 2026, Schedule 1 ("Instrument"). Washington (DC): Verra; 2026. Available from: https://verra.org/documents/verra-registry-terms-of-use/
- [R17] European Parliament and Council. Directive (EU) 2024/825 of 28 February 2024 amending Directives 2005/29/EC and 2011/83/EU as regards empowering consumers for the green transition through better protection against unfair practices and through better information. Off J Eur Union. 2024 Mar 6;L 2024/825. Available from: http://data.europa.eu/eli/dir/2024/825/oj
- [R18] Besleaga AN. The SFC profile of /.well-known/sustainability-data, profile 1.1. 2026 Oct 3. Available from: https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/PROFILE.md (profile 1.0, 2026 Sep 16: https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/c787378/sfc-compliance/PROFILE.md)
- [R19] Besleaga AN. The "sustainability-data" well-known URI. Internet-Draft draft-besleaga-sustainability-wellknown-07, work in progress. 2026 Sep 17. Available from: https://datatracker.ietf.org/doc/draft-besleaga-sustainability-wellknown/

---

* **Profile version:** `SFC-PROFILE v1.2` (2026-10-03); previous v1.1: doi:[10.5281/zenodo.22681205](https://doi.org/10.5281/zenodo.22681205).
* **Framework:** Besleaga (in press), https://doi.org/10.1145/3809296 *(accepted; in press)*. Future revisions of the paper trigger a new profile version.
* **Author identifier:** ORCID [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283).
* **Scope reminder:** this profile applies the framework — it does not reproduce its rationale or argumentation. Read the paper.

## Change log

* **v1.2 (2026-10-03).** Final. The profile text is replaced by the normative text of ledger profile 1.2; event names and payload fields of v1.1 are unchanged.
  * §1 (new): conventions (BCP 14 key words), terms (operator, period, attestation, chain, head, retirement, allocation, offset coverage), and hashing: SHA-256 over the RFC 8785 serialisation of the whole event; Ed25519 signatures unless the Registry records another algorithm.
  * §2: the four criteria as applied, with the C1 boundary and the narrowings; hot-path and anchor rule; migration clause for the hot path and for an anchor that stops producing blocks; per-project pins with the anchor "to be chosen" (v1.1: Polygon zkEVM). The informative platform notes of v1.2-draft are kept.
  * §3: one chain per operator per event type; the *effective* attestation of a period (the latest not superseded) is the only one counted; corrections are new attestations with the optional `payload.supersedes`; the ledger rejects an attestation not signed with the operator's current Registry key; key validity is judged at commit time, never at `ts`; `ts` follows the period.
  * §4: the offset-coverage rule stated as consistency, compliance (every active month) and its network consequence (only if each retired tonne is allocated once); whole-tonne retirements and signed allocations; the known gap of double allocation by two operators.
  * §6: every `measurementMethod` is defined in the methodology document and SHOULD be one of the four method tokens of draft -07; one Scope 2 basis for the in-band figure across the network.
  * §7: C-SFC-1 ignores corrections; C-SFC-2 in two forms (ledger and disclosure); C-SFC-4 covers every active month; C-SFC-7 (bridge consistency) added.
  * §8: the mapping table of the retired v1.1 endpoints to the well-known declaration, and the mapping of ledger figures to declaration members (including `carbon-accounting`, `carbon-intensity-gCO2e-per-kWh`, the `hardware-lifecycle` extension and `net-zero-status`). Disclosure follows the SFC disclosure profile 1.1.
  * §9: the `ledger-evidence` extension, now defined by the SFC disclosure profile 1.1 (§5.5): members, with `offset-coverage-every-period` per operator and `network-offset-coverage` at network level; shallow and deep checks; what each establishes.
  * §10 (new): what a conformance statement may and may not claim. §11 (new): compatibility of ledger profiles 1.1 and 1.2 and disclosure profiles 1.0 and 1.1. References R1–R19 added.
  * Before publication (2026-10-03): §3.1 rule 8, members a reader does not recognise are ignored but still hashed and signed; §4, an allocation has no commit time, so it is verified under any key the Registry has recorded for the operator, and it cannot raise a period's credits by itself; §8, a silent month omits the top-level members derived from the silent type (and the carbon intensity when either type is silent); §9.3 step 5 compares only members present; §9.4 step 8 checks the allocation's signature.
  * §8 (2026-10-03, before publication): a declaration that claims this profile and carries `ledger-evidence` MUST NOT apply the optional noise of draft -07, Section 7, because noised figures could never equal the totals the shallow and deep checks recompute; monthly or annual periods already meet that section's granularity advice.
  * The six project documents now pin `SFC-PROFILE v1.2`; their criterion-4 text names the signed declaration at `/.well-known/sustainability-data`, and their SPEC files point to the §8 mapping table instead of listing the retired endpoints.
* **v1.2-draft (2026-10-03).** *(Section numbers in this entry are those of the draft.)*
  * §4: the four bespoke `/v1/sustainability/…` endpoints are retired in favour of the `sustainability-data` well-known URI (draft-besleaga-sustainability-wellknown-07) and the SFC disclosure profile 1.0. The v1.1 endpoints are listed for reference. New §4.1 describes the evidence-to-disclosure bridge as a proposal.
  * §7: C-SFC-5 now checks the well-known declaration instead of the retired endpoint.
  * §2: the platform list is no longer called "verified". Offset-based labels (NEAR, Hedera) are described as what they are, not as energy evidence; the unsourced VeChainThor footprint is removed; the dead NEAR link is replaced; the out-of-date proof-of-work figure (100–170 TWh/yr) is removed in favour of a link to CBECI; the Ethereum figure is given its source.
  * §6: the out-of-date count of Electricity Maps zones is removed.
  * No energy or carbon figure in this profile or in the six designs has been measured. Energy budgets are design targets; the example values in §3 are invented.
  * The framework paper is cited as accepted, in press, without a year.
  * *Additions after the criteria reality check (canonical SFC decisions, 2026-10-03):*
    * §1: the C1 boundary ("system-wide") is defined as in Commission Delegated Regulation (EU) 2025/422, field S.8 (all nodes, as its recital 8 says; data-centre overhead is this profile's addition — wording corrected 2026-10-03 after an accuracy check of S.8); C3 is applied as an **offset-coverage rule** (the framework's "Net Zero"), with no consumer-facing neutrality claim (Directive (EU) 2024/825); C4 is applied in its machine-readability part; the narrowings are stated.
    * §2: qualification needs a current public assessment on the C1 boundary; "Hedera Hashgraph" → "Hedera"; the anchor is chain-agnostic, because Polygon zkEVM stopped producing blocks on 3 July 2026; Ethereum's post-Merge figures are given with both sources (CCRI 2022, CCAF 2026), both above C1; "qualifying platforms" in the framework paper → illustrations.
    * §3.2: Scope 2 basis (market-based where instruments are used, location-based reported beside it; proposed optional `scope2Method`); Scope 3 amortisation named as the SCI approach, a stated deviation from GHG Protocol guidance; retirements in whole tonnes, allocated to periods; `netZero` keeps its name and is described as the offset-coverage flag.
    * §4.1: proposed `ledger-evidence` members for the rule are named `network-offset-coverage` and `offset-coverage-every-period` (not yet published, so named accurately from the start).
    * §5: `cloud-instance` proposed; C2 is declared, never passed. §6: Scope 2/3 rules, the S.8 boundary and credit quality. §7: C-SFC-2, C-SFC-4 and C-SFC-6 reworded. §8: note on the anchor and on NEAR's margin. §9: retirement rules.
    * Field names and event names of v1.1 are unchanged; every addition is optional, so a v1.1 event stays a valid event.
* **v1.1 (2026-05-23).** Deposited on Zenodo, 10.5281/zenodo.22681205 (v1.1, 2026-09-09).
