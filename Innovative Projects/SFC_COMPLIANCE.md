# Sustainability-First Consensus (SFC) profile, version 2.0

**Short name:** SFC 2. **Version:** 2.0 (semantic versioning, 12.2). **Status:** normative profile; the adoption date is set at release. Section 2 and Appendix E are informative; everything else is normative.

## 1. Status and citation

- **Applies to** the six designs of the greentech catalogue (Appendix E.1) and to any other deployment that claims SFC.
- **Replaces** ledger profile 1.1 and 1.2 and disclosure profile 1.0, 1.1 and 1.1.1. Appendix C maps every 1.x item; Appendix E gives where each stays reachable.
- **Written against** [draft-besleaga-sustainability-wellknown-10](https://datatracker.ietf.org/doc/draft-besleaga-sustainability-wellknown/10/) (the *draft*; Internet-Draft, work in progress). Appendix D lists the draft members this profile relies on.
- **Cite the framework** in any deployment that claims SFC. The framework is the column:

  > Besleaga, A. N. "'Sustainability-First Consensus' Ledgers for a Green Digital Future." *Communications of the ACM*, Opinion, in press, doi:10.1145/3809296 (the DOI resolves on publication). ORCID 0009-0001-3464-5283.

- **Cite this profile** by the Zenodo concept DOI 10.5281/zenodo.22681204 (resolves to the latest version); the version DOI of 2.0 is assigned at deposit. A later paper cites the version it uses ("SFC profile 2.x") with that version's DOI, and the concept DOI only as "latest".
- **Files.** Schemas, test vectors, examples and the reference checker live in [`sfc-compliance/`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/tree/main/sfc-compliance/) of the rfc-sustainability-wellknown repository (Appendices A and B).

The profile states what a ledger records, how the records are summed, how the sums are published at `/.well-known/sustainability-data`, and which checks a reader can run. It does not repeat the column's argument. It changes nothing in the draft and adds no top-level member to it; what the draft lacks is carried under extension names (section 8). A published figure is a claim of the origin that served it; nothing here makes a figure true.

## 2. Quick start (informative)

Where this section and the rules differ, the rules win. You need Node 22.13 or later (checker, vector generator) and Python 3 (cross-check), or any language with RFC 8785, Ed25519, SHA-256, exact decimal arithmetic, RFC 3339 parsing, JSON Schema 2020-12 and JWS (Ed25519, ES256). Links: [schemas](https://github.com/andreibesleaga/rfc-sustainability-wellknown/tree/main/sfc-compliance/schemas/), [vectors](https://github.com/andreibesleaga/rfc-sustainability-wellknown/tree/main/sfc-compliance/vectors/), [examples](https://github.com/andreibesleaga/rfc-sustainability-wellknown/tree/main/sfc-compliance/examples/), [checker](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/sfc-check.mjs). The vectors use the RFC 8032 section 7.1 test 1 key; it proves nothing about who signed, so never use it for real data.

### 2.1 Emit attestations (operator)

Once a month ends, emit one `EnergyAttested` and one `CarbonAttested` for it.

| Step | Do | Rule | Schema | Vector |
|---|---|---|---|---|
| 1 | Fill the payload: one whole month; kWh and kg as plain decimals (at most 15 digits, 6 decimals, not negative); a `measurementMethod`; an absolute `evidence` URI; `retirements`; `offsetsKgCO2e` = sum of `kg`; `netZero` true when S1 + S2 + S3 <= offsets, else false; `network` = the network's target. | 5.3, 5.4, 6 | [energy](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/event-energy.json), [carbon](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/event-carbon.json) | v12, v14, v23 |
| 2 | Canonicalise the event without `sig` (RFC 8785); sign with pure Ed25519; write `sig` as `{"alg":"Ed25519","value":<86-character base64url>}`. | 3.6 | | v01, v02, v16 |
| 3 | Hash the whole event, `sig` included. Store and resend events exactly as signed, unknown members included. | 3.6 | | v02 |
| 4 | Set `prev` to the chain's tip (null for the first event; after a takeover, the old ledger's tip). Set `supersedes` to the hash of the effective attestation for that subject, type and month, or omit it. | L4, L6 | | v03 |
| 5 | Retire credits at the registry first. `retiredAt` must be at or before the due instant (month end plus 5 days: January 2026 gives 2026-02-06T00:00:00Z) and the commit instant. Citations of one retirement repeat `tonnesRetired` and `retiredAt`; their `kg` sum to at most `tonnesRetired` x 1 000. Use the registry and reference forms the methodology document names. | 5.4, L8b to L10 | | v10, v11 |
| 6 | Read the tip before signing. On an L4 or L6 rejection, read again, rebuild, re-sign, resubmit. | 5.5 | | v03 |

Use your own Registry key, never the test key, and never one key in two networks. The ledger judges the key at the commit instant. On rotation, wait until the registrar has published the new key and closed the old key's `validToCommit`, then re-sign queued events with the new key and recompute each later `prev`.

### 2.2 Publish a declaration (publisher)

| Step | Do | Rule | Schema | Vector |
|---|---|---|---|---|
| 1 | Take a ledger read. Set `updated` to its `read-at` or earlier, never later than publication. Pick the effective attestation per operator, type and month committed at or before `updated`. | 5.6, 5.7, 7.1 | | v03 |
| 2 | Sum per operator in exact decimal, round half to even to 6 decimals. A silent operator-month, or a month with no active operator, makes the object incomplete: omit the listed members. | 3.3, 7.4, 7.5 | [evidence](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-ledger-evidence-2.json) | v04, v05, v07 |
| 3 | Write the seven draft members, units, the 7.4 members and `disclosure-uri` (network); do not perturb. Optionally write the location-based object. | 7.1 to 7.4 | | v06, v14 |
| 4 | Add the extensions, sign each object (`signed`: Ed25519 for an operator declaration, Ed25519 or ES256 for a network declaration) and serve at `/.well-known/sustainability-data` as `application/sustainability-data+json`. Say "offset coverage", never "net zero". | 7.2, 8, 11 | [extensions](https://github.com/andreibesleaga/rfc-sustainability-wellknown/tree/main/sfc-compliance/schemas/) | v21, v29 |

### 2.3 Verify

Run the shallow check (9.3) on any declaration, and the deep check (9.4) when you can read the ledger. Pin the registrar key out of band for D2. An implementation matches when it reproduces every row of `vectors/expected/`.

### 2.4 Move from 1.x, and run the Registry

- Do not rewrite old events. The first 2.0 event's `prev` is the hash of the last 1.x event; after it emit only 2.0 forms (12.1 rule 4). A 1.x `CarbonAttested` without `scope2Method` needs `scope2-basis-1x` (7.6). Write `ledger-evidence-2`, not `ledger-evidence`; a -07 wire declaration fails S2, so convert it first.
- Registrar: one entry per operator (`operator`, `origin`, `network`, month-bound `active`, `keys`, `nodeProfile`, `version` (optional; 1 at first signing when used, 5.1)); refuse small-order keys; sign the entry without `sig`; re-sign on every change. List the registrar key as `current` in the parameters and publish the methodology document so verifiers can pin it.

## 3. Conventions

### 3.1 Key words

MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, RECOMMENDED, MAY and OPTIONAL are read as in BCP 14 (RFC 2119, RFC 8174) only in capitals. They bind a ledger, registrar, operator, publisher, emitter, checker (also called verifier), and a consumer or aggregator that displays a declaration, each when it claims this profile; never the draft. Each rule is stated once and other sections point to it by number. The schemas restate the member tables and are tested against the checker's shape tables; if they differ, the text wins (Appendix A).

### 3.2 Terms

| Term | Meaning |
|---|---|
| operator | A party that runs ledger nodes and has a Registry entry (5.1). Identified by a DID string, compared as a string; any DID method. Its declaration is an *operator declaration*. |
| Registry, registrar | The ledger's set of entries, and the party that signs them. |
| network, hot path | The system whose energy criterion C1 is judged (its declaration is the *network declaration*), and the ledger carrying its operational events. |
| month | A calendar month in UTC. Its *bounds* are the first instants of the month and of the next, written `YYYY-MM-01T00:00:00Z`. |
| calendar year | Twelve consecutive months from 1 January. With no ledger evidence the bounds may carry one numeric offset, and the year is the year in that offset; only C-SFC-2 disclosure form uses it. |
| instant | An RFC 3339 `date-time`: upper-case `T`, `Z` when no offset is written; numeric offsets and fractions allowed; second 60 not allowed. Instants compare as the moments they denote. |
| commit instant | Assigned by the ledger on acceptance; strictly increasing. *Ledger order* is commit order. |
| check instant T | Given by the caller, else the checker's clock when the check runs (when the read is received, if one is used). The checker prints T and its source. With a read and no explicit T, window and cut-off are anchored at `read-at` and T only bounds the read's age (5.7). An explicit T later than `read-at` makes C-SFC-1, C-SFC-2 ledger form, C-SFC-4 on its own and the permissioned case of C-SFC-6 NOT-EVALUABLE ("read older than T"). C-SFC-7 and the C-SFC-4 inside D5 use `updated` as cut-off; T bounds only the read's age (5.7). |
| at most 18 months before T | A period whose end plus 18 calendar months (UTC, same day, clamped to the month's last day) is at or after T. "More than 18 months before T" is the opposite. Used by 4.4 rule 2, C-SFC-6 and S4. |
| grace period G, due instant, evaluation window | G is 5 days of 24 hours. The due instant of a month is its end bound plus G. The window is the 12 months that ended at least G before T (the last is the latest month due at or before T). |
| active, operator-month | An operator is active in a month when an `active` interval has `from` before the month's end and `to` null or after its start. An operator-month is a pair (operator, month) with the operator active. |
| counted operators | Operators active in at least one month of a declaration's `period`, or of the window for a check on a read alone. |
| attestation, chain | One signed `EnergyAttested` or `CarbonAttested` event; and one operator's attestations of one type linked by `prev`, in ledger order. Skipped events (5.5) stay in the chain. |
| tip | Hash of the last event of a chain, effective or not, when the ledger judges a new event; null if the chain is empty. Not the *head*. |
| cut-off | The instant after which events and void acts are ignored: `updated` for a declaration check, T otherwise. |
| effective attestation | For one operator, type and month, the latest attestation in chain order that 5.6 selects: committed at or before the cut-off and breaking no rule of 5.5 at its own commit instant. Every sum and check uses effective attestations only. For a 1.x event: the latest no later event supersedes (12.1 rule 2). |
| head | Hash of the last attestation in chain order committed at or before the cut-off whose period ends at or before the declared period's end; skipped events count; null if none. Event counts (8.5) need the period inside the declared period, so a chain with only last-year events has a head and a count of 0. |
| silent | An operator-month with no effective attestation of a type is silent for it. A 1.x event on the location basis, or of unknown basis, is silent for `CarbonAttested` in 7.4, 7.5 and 8.5 but effective for C-SFC-4 (12.1 rule 1). |
| retirement | Cancellation of whole carbon credits (one tonne of CO2e each) in a registry. |
| claims SFC | An object claims SFC when its `extensions` carries a name of 8.1 other than the superseded `ledger-evidence`. A body that is not I-JSON claims SFC when `ledger-evidence-2` appears as a member name in its text, in any duplicate. |
| Scope 1, 2, 3; market-based, location-based | As the GHG Protocol defines them. |

### 3.3 Arithmetic

1. **Exact.** Read every number as the exact decimal of its RFC 8785 text (after the 32-character literal limit of section 10). Sum in decimal, divide as rationals, never use binary floating point. A 1.x figure over rule 2's digit limit is read as the RFC 8785 text of its binary64 value.
2. **Event figures** are in kWh or kg, finite, not negative, plain decimal (no exponent), at most 15 digits in all and at most 6 after the point. `tonnesRetired` is an integer of at most 15 digits. A breach fails L8. Round only on unit conversion and for the intensity, never per event.
3. **Published figures** are the exact value in the published unit, rounded half to even to 6 decimals: the members of an `operators` entry, and `energy-consumption`, `scope-1`, `scope-2`, `scope-3`, `carbon-footprint`, `offsets-retired-tCO2e` and `carbon-intensity-gCO2e-per-kWh` of an object with `ledger-evidence-2` and of its paired object (7.3). They are compared with the ledger by equality. `net-zero-status` and `validated-node-count` are not rounded. Rule 2's digit limit holds for published values: at most 15 digits in all and 6 after the point, so a figure of 10^9 or more cannot carry six decimals and 10^15 or more cannot be published at all; pick a coarser unit (`tCO2e`, `GWh`); an object that cannot be published within the limit FAILs C-SFC-5. "Energy is 0" means the exact sum is 0; a positive sum that rounds to 0 still gets an intensity (S6 d cannot test it; C-SFC-7 checks it by equality).
4. **Tolerance rule.** It applies when comparing published values (S6 b to d, i) and to any comparison on an object without `ledger-evidence-2`. Convert every value and tolerance to the unit of P, the figure tested. Let k of a figure be the number of digits after the point in its RFC 8785 text (0 for an integer, which tolerates +/-0.5 of its unit). Use k = 6 for every figure rule 3 rounds. An absent term (an absent `scope-1`) is exact 0 and adds no tolerance term. Against a sum of published terms T1 to Tn, P passes when |P - sum Ti| <= 1/2 x 10^-k(P) + sum 1/2 x 10^-k(Ti). S6 d gives the quotient form.
5. **Two published values** compared as "at least" or "equal" are compared exactly.

### 3.4 Units

`tCO2e` = 1 000 `kgCO2e` = 1 000 000 `gCO2e`; `GWh` = 1 000 000 kWh; `MWh` = 1 000 kWh; `kWh` = 1 000 Wh. **CAP = 1 000 000 kWh** (the column's 0.001 TWh) is a parameter with its source (12.2). The draft's `energy-unit` has no TWh, so no declaration states TWh.

### 3.5 Value forms

| Form | Definition |
|---|---|
| `month-bound` | An `instant` that is the first instant of a month: `YYYY-MM-01T00:00:00Z`, no fraction, `Z` only. |
| `full-date` | RFC 3339 `YYYY-MM-DD`. |
| `hex64` | 64 lower-case hexadecimal characters. |
| `b64url` | base64url without padding (Ed25519 signature: 86 characters; public key `x`: 43). Only the canonical encoding is valid: re-encoding the decoded bytes reproduces the string. |
| `did` | DID Core section 3.1 syntax. A 1.x value that fails it is INFO, not FAIL. |
| `host` | A-label host name, lower case, no scheme, port or path. Compared after ASCII lower-casing both sides; upper case is accepted as input. |
| `https-uri` | Absolute URI, scheme `https`; compared without normalisation. |
| `uri`, `uri-abs` | `uri`: a URI reference as the draft defines it. `uri-abs`: a URI with a scheme (RFC 3986 section 3); a relative reference is invalid, a fragment is allowed. Used where no retrieval URI exists, as for event `evidence`. |
| `sha256` | SHA-256 over the RFC 8785 text of a JSON value, as `hex64`. |

### 3.6 Hashing and signing

1. The **hash** of an event is `sha256` over the RFC 8785 text of the whole event, `sig` included.
2. The **signing input** of an event, Registry entry, void act or checkpoint is the RFC 8785 text without `sig`. `sig` is `{"alg":"Ed25519","value":<b64url>}`. Ed25519 is the only algorithm for them; another `sig.alg` fails L5 (a 1.x event: 12.1 rule 2) or, in a Registry entry, D2.
3. **Unknown members.** A reader ignores unknown members in events, payloads, Registry entries and extension values; they still enter every hash and signature. Two signed objects are closed: a void act has exactly `commit`, `target` and `sig`; a checkpoint has only the members of 5.8. An extra member fails D2 (void act) or D4 (checkpoint). The exceptions to this rule and to 12.2 rule 2 are the closed void act and checkpoint, the four names forbidden on a Registry entry (next sentence), and the other level's members in `network-topology` (8.4). A Registry entry MUST NOT carry the top-level members `commit`, `target`, `read-at` or `chains`. A verifier reads an object only as the kind of the member where it was found (`registry[]`, `voids[]`, `checkpoint`).
4. **`signed`** of a declaration is the draft's own (JWS Compact, `cty` `sustainability-data+json`). Its `alg` is an asymmetric signature algorithm (`Ed25519` and `ES256` recommended); `none` and MAC algorithms are forbidden. This profile adds only the restriction of 7.2 rule 2.

## 4. The four criteria, applied

### 4.1 Criteria table

Column 1 is the printed text of the column, verbatim. Column 3 names each narrowing; 4.2 and 4.3 give the reasons.

| Printed criterion | As SFC 2 applies it | Narrowing |
|---|---|---|
| **C1 Energy Consumption.** "Total annualized network energy consumption to be < 0.001 TWh (1 GWh) systemwide." | The energy attested by registered operators is below CAP, over one calendar year (disclosure form) or the evaluation window (ledger form). Checked by C-SFC-2. | Boundary, annualised, measurement (4.2). |
| **C2 Hardware Lifecycle.** "Mandatory extended hardware utility to prevent e-waste (for example, using general-purpose hardware rather than single-use ASICs)." | Every active operator declares its node hardware in its Registry entry (5.1). Reported as declared, never as passed (C-SFC-3). | No document shows what hardware exists, so the check tests a complete declaration: class in a closed list, `asicForbidden` true. "Extended utility" is carried by the purchase date, planned retirement date and reuse policy. `cloud-instance` and `accelerator-server` count as general-purpose (8.2); the accelerator class is not an ASIC test. |
| **C3 Carbon Accountability.** "Native on-chain carbon transparency and regulatory-aligned thresholds requiring annual Net Zero status via direct renewables or verified offsets." | Every operator attests Scope 2 and Scope 3 monthly, Scope 1 when it has any (omitted is 0), and its retired credits, on the ledger. Section 6 is tested per operator and month (C-SFC-4). | Seven readings (4.3). |
| **C4 Regulatory Readiness.** "Architecture must support auditability standards compatible with CSRD and ESG reporting (for example, accessible via APIs)." | The declaration at the well-known URI is the machine-readable access (C-SFC-5); a ledger read (5.7) gives audit access. | Only machine-readability is applied. The declaration maps onto ESRS E1 quantities and MiCA sustainability indicators; it is not a regulatory filing. The GHG Protocol Scope 2 Guidance asks for both bases where contractual instruments are available in the operator's markets: SFC 2 requires market-based, and a publisher in such a market SHOULD also publish the location-based object (7.3). |

The criteria and CAP are design constraints a conforming system commits to meet, not a statement that any system meets them. The column calls the thresholds "an adaptable baseline"; 12.2 says how CAP changes.

### 4.2 C1: boundary, annualised, measurement

- **Boundary.** "Systemwide" is undefined in the column. SFC 2 uses Commission Delegated Regulation (EU) 2025/422, Table 2, field S.8 (Art. 6(5), second subparagraph: calculated under the guidance in point AR 32 of Appendix A to ESRS E1): energy for validating transactions and maintaining ledger integrity, per calendar year, over all nodes. This profile additionally places data-centre overhead inside the boundary and client devices outside. Whatever is inside is attested by an operator or named as excluded in the methodology document (gateways, storage, backups, an anchor chain's share). A consortium running shared parts registers itself as an operator. Figures are gross: offsets are excluded (Art. 6(6)).
- **Annualised** is one calendar year for the disclosure form and the 12-month window (a rolling year) for the ledger form; each report row names its period.
- **Measurement.** The column asks for CBECI or CCRI alignment; SFC 2 requires less. The figure carries one of the draft's four method values and the methodology document defines the method. `nodeCount` is the operator's own declaration and `validated-node-count` is reported DECLARED. The network total is the sum over registered operators that attest. Published figures for one ledger differ by a factor of two or more with boundary and provider: on 27 October 2026 the CCAF Ethereum methodology page (https://ccaf.io/cbnsi/ethereum/methodology, comparison table) listed its own live estimate at 8.61 GWh a year beside CCRI's live index at 4.29 GWh and CCRI's September 2022 report at 2.6 GWh. Compare figures only on one boundary.

### 4.3 C3: readings

- **Stricter than annual.** Every month of the window is tested; an annual network result follows only when every operator-month holds.
- **"Verified offsets"** means credits retired in a registry, with a registry reference. Credit quality is not judged; the methodology document names the standard or label.
- **"Direct renewables"** is admitted as any market-based contractual instrument, unbundled certificates included, through market-based Scope 2.
- **"Regulatory-aligned thresholds"** is not implemented. The only carbon test is the offset-coverage rule of section 6, this profile's own.
- **Real-time monitoring** is not checked. The monthly attestation names its intensity source (`gridIntensityRef`) and method (`measurementMethod`).
- **"On-chain audit trails"** are the attestation chains; **"native on-chain"** is any ledger with a Registry and attestations, not necessarily the hot path. A network declaration without `ledger-evidence-2` has no ledger evidence, so C-SFC-4 is NOT-EVALUABLE on it.
- **Offset coverage is not net zero.** The GHG Protocol keeps credits outside the inventory, and the SBTi Corporate Net-Zero Standard v1.3.1 never counts credits as emission reductions toward a target (C12); it admits them only to neutralise, by permanent removal, the unabated emissions that remain once the long-term target is met (C28), or to finance mitigation beyond the value chain in addition to the targets (R12). Offset coverage under this profile is a monthly ledger test (section 6). It is not removal after a met target, and it is not financing beyond targets.

### 4.4 Platform rule and migration

This rule is the profile's own, not a printed criterion. C-SFC-6 is the worst of the not-proof-of-work test and the one case that applies (FAIL, then NOT-EVALUABLE, then PASS); the platform statement (7.6) names the case.

1. A **proof-of-work** ledger MUST NOT carry any event SFC 2 relies on, nor serve as the hot path.
2. **Public case.** A hot path whose nodes are not all registered operators MUST have a public assessment, on the C1 boundary, of a 12-month period that ended at most 18 months before T (3.2), with a figure below CAP.
3. **Permissioned case.** A hot path run only by registered operators is assessed by the deployment's own C-SFC-2. If every window month has an active operator, the case takes the C-SFC-2 ledger result. Otherwise it passes when the node bound is below CAP: N x P (W) x O x 8 784 h / 1 000, in kWh. N is the greatest number of nodes the registered operators may run. P is the rated watts of the worst hardware class in use. O is the data-centre overhead factor (at least 1, stated in the methodology document, no default). 8 784 h is a leap year. Example: 100 x 500 W x 1.5 x 8 784 / 1 000 = 658 800 kWh, below CAP. The case fails at or above CAP and is NOT-EVALUABLE when N, P or O is missing.
4. A public non-proof-of-work chain MAY serve as an anchor (Appendix E). No rule or check depends on it; no platform is named normatively.
5. **Migration.** When C-SFC-6, or C-SFC-2 on a fully covered window, places the hot path at or above CAP, the deployment moves to a qualifying ledger within 12 months and carries its chain tips. The first event of a chain on the new ledger links by `prev` to the old tip. The methodology document lists that tip per subject and type (7.6), and the new ledger accepts it (L4). After takeover the operator writes no further event of that subject and type to the old ledger. An event there after the listed tip is a cross-ledger fork (D4).

## 5. Ledger records

### 5.1 Registry entry

One entry per operator, at most 1 000 per Registry, signed by the registrar over the entry without `sig`. Schema: [registry-entry.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/registry-entry.json).

| Member | Type | Required | Meaning |
|---|---|---|---|
| `operator` | `did` | yes | The operator's DID. Unique in the Registry. |
| `origin` | `host` | yes | Host of the operator declaration; its `target`. Unique in the Registry. |
| `network` | `host` | yes (2.0 form) | The network's `target`. Signed, so an entry cannot move to another network; D2 FAILs a mismatch. A 1.x entry has none. |
| `active` | array of `active`, at least 1 | yes | Intervals of activity, sorted, not overlapping: `from` (`month-bound`, included) and `to` (`month-bound` or null, excluded, later than `from`; null while active). |
| `keys` | array of `key`, at least 1 | yes | Signing keys. They sign events and the `signed` of an operator declaration. |
| `nodeProfile` | object | yes | The hardware declaration (C2); below. A 1.x entry that was never re-signed may have none or an incomplete one (12.1 rule 6). |
| `version` | integer, at least 1 | no | A registrar that writes `version` MUST start at 1 and raise it by 1 at each change. An entry without `version` gets no rollback check (D2). |
| `profile2From` | `month-bound` | no | First month whose events are 2.0 form (L11b). Written once, at the first re-signing of a 1.x entry, as a month no later than the operator's first 2.0-form event; absent when the entry was 2.0 from the start (L11b then reads the first active month). D2 FAILs the entry when the read holds a 2.0-form event for an earlier month. |
| `sig` | `{alg, value}` | yes | The registrar's signature (3.6). |

`key` object: `jwk` (`{kty, crv, x}` with `kty` `"OKP"`, `crv` `"Ed25519"`, `x` a 43-character `b64url`), `validFromCommit` (`instant`) and `validToCommit` (`instant` or null while valid); all required. A key is *valid for an event* when `validFromCommit` <= its commit instant < `validToCommit` (null is unbounded).

`nodeProfile` object:

| Member | Type | Required | Meaning |
|---|---|---|---|
| `hardwareClass` | one of `general-purpose-x86`, `arm64-server`, `rpi-cluster`, `cloud-instance`, `accelerator-server` | yes | Closed for all 2.x. `cloud-instance` is a rented virtual machine; `accelerator-server` is a general-purpose server with accelerators. |
| `asicForbidden` | boolean `true` | yes | No single-use ASIC hardware. Key-custody HSMs are accepted. |
| `purchasedAt`, `expectedRetireAt` | `full-date` | yes | Purchase date (instance start for `cloud-instance`); planned end of use, not before `purchasedAt`. |
| `reusePolicy` | `donate-to-education`, `resell-refurbished` or `recycle-WEEE-certified` | yes | What happens to the hardware afterwards. |
| `serviceLifeMonths` | integer, at least 1 | no | Planned service life. |

**Registrar rules.**

- The methodology document names the registrar's keys: the current one and each former one, marked former with its retirement date. Only that document adds a replacement.
- On every registrar key rotation the registrar MUST re-sign all entries under the new key in the same revision of that document; the former key is listed only until then, and the next revision delists it. An entry verifying only under a former key is accepted with INFO "signed under a former key"; a checkpoint is verified only under a current key.
- A registrar key MUST NOT sign for more than one network; a verifier holds one pin per network. The registrar checks every operator key before signing; a small-order key is a fault. An operator SHOULD NOT use one key in more than one network.
- The registrar re-signs the entry on every change. `version` follows the 5.1 table.
- A change MAY append an `active` interval or a `keys` element, close an open end (`to`, `validToCommit`), or replace `nodeProfile` as a whole. A past interval is never altered (closing an open end, and the form change of 12.1 rule 6, are not alterations). `operator`, `origin` and `profile2From` never change; a different DID or host is a new entry. Key rotation is a new `keys` element and the old one closed.
- Closing `to` or `validToCommit` earlier than the time of the change is a registrar act. A verifier takes the entry as signed and applies it to the whole window: a retroactive `validToCommit` closure can make a committed event fail L5 (skipped; events that supersede it fail L6); a retroactive `to` closure makes later attested months inactive (L1 skips them, sums leave them out, D2 reports). The registrar SHOULD publish the reason and date in the methodology document.

### 5.2 Event envelope

| Member | Type | Required | Meaning |
|---|---|---|---|
| `type` | `"EnergyAttested"` or `"CarbonAttested"` | yes | The event type. |
| `network` | `host` | yes | The network's `target`. The ledger rejects another value (L1), so an event cannot be replayed in another network. |
| `subject`, `actor` | `did` | yes | The operator the event is about, and the signer; equal. |
| `prev` | `hex64` or null | yes | Hash of the previous event of the same type and subject (the tip); null only for the first, except as L4 says. |
| `ts` | `instant` | yes | The operator's emission time. Beyond L3 it is informative: never compared with the commit instant, never used for keys or ordering. |
| `payload` | object | yes | 5.3 or 5.4. |
| `sig` | `{alg, value}` | yes | 3.6. |

### 5.3 `EnergyAttested` payload (C1)

Schema: [event-energy.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/event-energy.json).

| Member | Type | Required | Meaning |
|---|---|---|---|
| `period` | `{start, end}` of `month-bound` | yes | One whole month; `end` is the next month's first instant. |
| `nodeCount` | integer, at least 0 | yes | Greatest number of nodes running at any instant of the month. The methodology document says how they are counted. |
| `kWhConsumed` | number, kWh | yes | Energy consumed in the month on the 4.2 boundary: everything the operator attests for it. |
| `measurementMethod` | `hardware-metered`, `hardware-estimated`, `cloud-billing` or `third-party-modeled` | yes | Most to least direct. Closed for all 2.x. The methodology document defines each. |
| `evidence` | `uri-abs` | yes | Where the evidence is kept. `ipfs:` names content by identifier; `https:` names a location. |
| `supersedes` | `hex64` | no | Present exactly as L6 says. |

### 5.4 `CarbonAttested` payload (C3)

Schema: [event-carbon.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/event-carbon.json).

| Member | Type | Required | Meaning |
|---|---|---|---|
| `period` | `{start, end}` of `month-bound` | yes | The month of the matching `EnergyAttested`. |
| `scope1KgCO2e` | number, kg | no | Direct emissions (a backup generator). Absent is 0. |
| `scope2KgCO2e` | number, kg | yes | Purchased-electricity emissions, **market-based**: contractual instruments where held, else supplier-specific or residual-mix factors, else grid average where no residual mix exists. |
| `scope2LocationKgCO2e` | number, kg | no | Location-based figure for the same month; feeds the paired object (7.3). |
| `scope3KgCO2e` | number, kg | yes | Value-chain emissions in the categories the methodology document lists; not negative (removals are not counted). Capital goods count in the month of acquisition; amortising is a stated deviation in the methodology document. |
| `gridIntensityRef` | string | yes | Source, zone and period of the grid-intensity data used. |
| `retirements` | array of `retirement`, may be empty | yes | Credits counted for this month. |
| `offsetsKgCO2e` | number, kg | yes | Sum of `kg` over `retirements`. |
| `netZero` | boolean | yes | The offset-coverage flag, equal to the section 6 comparison. The name is kept from 1.x; it is not a net-zero finding. |
| `evidence` | `uri-abs` | yes | Where the retirement records and emission calculation are kept. |
| `supersedes` | `hex64` | no | Present exactly as L6 says. |

`retirement` object:

| Member | Type | Required | Meaning |
|---|---|---|---|
| `registry` | `https-uri` | yes | The registry's base URI in the one form the methodology document names (L8b): lower-case scheme and host, no userinfo, default port, query, fragment or trailing slash. |
| `reference` | non-empty string | yes | Identifier of one retirement record exactly as the registry shows it (no trimming or case change), in the canonical form the methodology document names, if any (L8b). Where a registry identifies a record only by a serial range, the whole range. |
| `tonnesRetired` | integer, at least 1 | yes | Whole tonnes of CO2e in that record. |
| `retiredAt` | `instant` | yes | When the registry recorded it. |
| `kg` | number, at least 0 | yes | The part of that retirement counted here. |
| `beneficiary` | string | no | The registry's named owner, as the operator's claim; not in the equality set of L9. |

The *retirement key* is the pair (`registry`, `reference`), compared as two exact strings. The operator MUST use one spelling in every attestation. Differently spelled citations are different keys, so L9 cannot see that they cite one tonne; where the methodology document names a canonical form, L8b rejects other spellings, and where it names none, only D8 can find a double citation.

The operator MUST publish at the registry the beneficiary and period of each retirement it counts. Checks cannot read that (D8 is optional), so an operator may cite a retirement it does not own, and L9 gives the tonne to the first citation. Two measures limit this.

- Before accepting the first citation of a key, the ledger SHOULD confirm at the registry that the beneficiary matches the citing operator, using `beneficiaries` (7.6). The ledger operator states in the methodology document whether it confirms ownership. A verifier cannot confirm it at the registry and reports nothing for it.
- **Void act.** A registrar MAY void a citation with a record `{commit, target, sig}` (5.8). `target` is the hash of a `CarbonAttested` committed before `commit`; `sig` is the registrar's signature over the record without `sig` (3.6 rule 2); the void is bound to its network through the event it targets; `commit` differs from every ledger commit instant and every other act's. Who may ask a registrar for a void is a ledger-side policy, which the methodology document MAY state in `void-requesters` (7.6); a verifier does not read it and checks a void act by the registrar's signature alone (D2). From its commit, if the target is E's entry (5.6) for its subject, type and month, that entry is deleted: the event it superseded is not restored, the month is silent for that type, later citations are judged without it (L9), and the next attestation for the month has no `supersedes` (L6). If a later event already superseded the target, E does not change. Other events are never re-judged. A void is not a skip and does not restore an earlier-skipped event; the operator files a superseding attestation, which L6 permits because none stands. An act that breaks these conditions is ignored with INFO on D2.

### 5.5 Acceptance rules

The ledger MUST reject an attestation unless all of these hold, and a verifier applies the same rules. Each rule is judged once, at the event's own commit instant, using only earlier events (5.6), and never re-judged. An event that breaks a rule stays in the chain (events are never edited or deleted) but is *skipped*: the previous valid event stays effective. A ledger holding such an event is faulty; D3 or D5 reports it on its own row.

| # | Rule |
|---|---|
| L1 | `type` is one of the two types, `network` is the ledger's network, and `subject` = `actor` = the DID of a Registry operator active in the attested month. |
| L2 | `payload.period` is one whole month. |
| L3 | `ts` and the commit instant are both at or after `period.end`. |
| L4 | `prev` equals the tip of that subject's chain of that type; null only when the chain is empty. The first event on a ledger that took over (4.4 rule 5) has `prev` equal to the old ledger's tip for that subject and type, as the methodology document records it. |
| L5 | `sig` verifies (section 10) under a Registry key of the operator valid for the event at the commit instant the ledger assigns. `ts` is never used for keys. |
| L6 | `supersedes` is absent when the chain holds no earlier effective attestation, as of this event's commit instant, for the same subject, type and month; otherwise present and equal to the hash of that attestation. |
| L7 | For `CarbonAttested`, `netZero` equals the section 6 comparison on the event's figures. |
| L8 | Every figure meets 3.3 rule 2 and the member tables; `offsetsKgCO2e` equals the exact sum of `kg`; each `kg` is at most `tonnesRetired` x 1 000; the event meets the limits of section 10 (at most 100 `retirements`, 4 096 bytes per string, nesting 32, 65 536 bytes in all). |
| L8b | Each `registry` is in the one form the methodology document names for it, and each `reference` is in the canonical form it names, if any. Any other is rejected. |
| L9 | **Single use of each tonne.** Take the effective set built from events committed before this one, over every operator, with this event in place of the one it supersedes. For each retirement key, every citation states the same `tonnesRetired` and `retiredAt` (equal as moments, fractions of a second included, 3.2), and the sum of `kg` over all citations is at most `tonnesRetired` x 1 000. For a registry whose `reference-forms` has `range-first-last`, a range that overlaps without equalling another citation's is also rejected. |
| L10 | **No late credits.** Each `retiredAt` is at or before the due instant of the attested month and at or before the event's commit instant. No lower bound is checked: a credit retired before the month may count if L9 holds. D8 is the only link between a retirement and a month. |
| L11 | An event with a 1.x-form `period` (`from`, `to`) is accepted only if no 2.0-form event of the same subject, of either type, precedes it. |
| L11b | For an operator whose Registry entry is 2.0 form, an event for a month at or after `profile2From` (absent: the first active month) is 2.0 form. A 1.x-form entry has no switch month; L11 alone applies. |
| L12 | At most twenty 2.0-form attestations per operator, type and month (corrections included) and 10 000 events in one chain of one type. The ledger rejects the next; a verifier counts rejected events toward the limits. 1.x events do not count. |

An attestation is *late-filed* when its commit instant is after the due instant of its month; L10 for it rests only on the operator's `retiredAt` assertion (D5 reports it, D8 confirms it). A **correction** is a new attestation chained normally with `supersedes` set by L6; the effective attestation of a month is the latest valid one.

### 5.6 Selecting the effective attestations

The ledger applies this when it accepts an event. A verifier replays the whole read in ledger order up to the cut-off, for every operator the read yields (counted operators, and others for L9); two verifiers with the same read get the same effective set. E holds, per (subject, type, month), the effective attestation, and starts empty. An event or void act committed after the cut-off is never processed. For each, in ledger order:

1. Append the event to its chain, effective or not. Tips, heads and counts (`energy-events`, `carbon-events`, `chains[].count`) include skipped events.
2. Judge L1 to L12 using E as it stood before this event. L6 reads E's entry for the event's subject, type and month; L9 reads E over all operators with this event in place of that entry.
3. If no rule is broken, the event replaces that entry of E; otherwise E is unchanged and the event is skipped.
4. A void act deletes the entry of its target when that is E's entry for the target's subject, type and month, and changes nothing otherwise.

The verdict is final: a later correction that removes a retirement from E does not change the verdict on an event committed between. A correction committed after `updated` does not make a declaration wrong; the deep check reports it as INFO "superseded since publication" (D7), never FAIL.

### 5.7 What a ledger read yields

For each counted operator a read MUST yield: (1) every attestation of both types with commit instant and hash, in ledger order, from the first event (`prev` null) to the last committed at or before the read; (2) the signed Registry entry and any void act (5.8); (3) `read-at`, the instant of the read.

- A read supports only cut-offs at or before `read-at`; a later cut-off is NOT-EVALUABLE. Every event in the read is committed at or before `read-at` (D4 fails one that is not).
- When T is the checker's clock, the read is NOT-EVALUABLE ("stale read") if T minus `read-at` exceeds MAX_READ_AGE or `read-at` is later than T plus the clock skew of section 10. The checker prints `read-at`, T and MAX_READ_AGE. With an explicit T there is no age limit, so archival and test runs stay reproducible; with an explicit T later than `read-at`, 3.2 applies.
- For every other Registry operator with an event citing a retirement key, the read MUST yield that operator's whole chain, so supersession and L9 can run.

How a ledger exports a read is its own matter; the registrar key is not part of it (D2 says where it comes from).

### 5.8 Ledger excerpt (optional interchange format)

A JSON document (`application/json`) holding one read; any other form that yields 5.7 is as good. Schema: [ledger-excerpt.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ledger-excerpt.json).

| Member | Type | Required | Meaning |
|---|---|---|---|
| `excerpt-version` | integer `2` | yes | Format version. |
| `profile-version` | string `2.<digits>` | yes | `"2.0"` here; same major as the `profile-version` of the declaration's `ledger-evidence-2` (D1). |
| `network`, `read-at` | `host`, `instant` | yes | The network's `target`; 5.7. |
| `registrar` | `{jwk}` (form of `key.jwk`) | yes | The registrar key the excerpt claims. Not a trust anchor; used only when equal to the independently obtained key (D2). |
| `registry` | array of Registry entries | yes | 5.1. |
| `ledger` | array of `entry` | yes | Events in ledger order. `entry` is `{commit, hash, event}`: `commit` an `instant`, `hash` the `hex64` hash of `event`, `event` a 2.0 or 1.x event; all required. Commit instants should increase strictly; a violation is D3 "ledger order" FAIL, never a reason to refuse an excerpt. |
| `voids` | array of `{commit, target, sig}` | no | Void acts (5.4); each `commit` distinct from every ledger commit and every other act's. |
| `checkpoint` | object | no | Registrar-signed claim about every chain at `read-at`; members below. |
| `notice` | string | no | Free text. |

`checkpoint` has these members and no others:
- `network` and `read-at`, equal to the excerpt's.
- `chains`: one `{operator, type, tip, count}` per Registry operator and type, empty chains included (`tip` null, `count` 0). `count` is all events up to and including the tip, over the whole chain.
- Optional digests (a publisher SHOULD include `ledger-digest`; without it a verified checkpoint does not authenticate commit instants, D4): `registry-digest` (`sha256` of the RFC 8785 text of all entries sorted by `operator`), `ledger-digest` (of the `ledger` array) and `voids-digest` (of the `voids` array in order; absent `voids` is `[]`).
- `sig`: the registrar's, under a current key, over the object without `sig`.

## 6. The offset-coverage rule

For operator o and month m, take the effective `CarbonAttested` and write S1 (`scope1KgCO2e`, 0 if absent), S2, S3, R (`offsetsKgCO2e`) and z (`netZero`).

- **Consistency (L7).** z is true when S1 + S2 + S3 <= R, else false, compared exactly. A mismatch fails the attestation whatever the flag says.
- **Coverage.** z is true for every operator-month of the evaluated period or window, on effective attestations. A month with no effective `CarbonAttested` is silent and fails coverage.
- **Network consequence.** If the rule holds for every operator-month of a year, sum(S1 + S2 + S3) <= sum R <= the kilograms in the distinct retirement keys (L9). The converse fails: a network can meet the annual sum while one operator misses a month. D8 establishes that the tonnes were retired.

The rule asks for no reductions and does not judge credits. An emitter, publisher, consumer or aggregator that claims this profile MUST NOT present its result as a consumer-facing claim of climate neutrality: point 4c of Annex I to Directive 2005/29/EC, inserted by Directive (EU) 2024/825 (Article 1(4) and Annex), bars offset-based neutrality claims in business-to-consumer practice, with national measures applying from 27 September 2026. The ban covers claims about a product. The Commission services' Questions & Answers on the directive (September 2026) say it does not apply to claims based on offsetting at company level; such claims stay subject to the other provisions of Directive 2005/29/EC. The Q&A states preliminary views of the Commission services, not an official position. That is no permission to call a network or operator result net zero or neutral. The labelling rule in 8.3 (offset-coverage meaning, shown beside the gross `carbon-footprint`) applies to a network or operator figure however it is presented.

## 7. Publication under draft -10

### 7.1 Levels

| | Network declaration | Operator declaration |
|---|---|---|
| About; publisher | The whole network; the body that speaks for it. | One operator; the operator. |
| `target-type`; `target` | `service`; the network's host. | `origin`; the operator's Registry `origin`. |
| `period` | One calendar year. | One month or one calendar year when it carries `ledger-evidence-2`; otherwise any period the draft allows, and C-SFC-7 does not apply. |
| `updated` | For a ledger-backed object, the cut-off: events committed at or before it count. The publisher sets it to its read's instant or earlier, and MUST NOT set it later than publication. A checker sees only that `read-at` is not before `updated` (D1) and `updated` is not after T plus the skew (C-SFC-5). | Likewise. |
| `capabilities`; `provider` | As the draft defines them (`basic` when no query parameter is supported, else `extended`; a human-readable publisher identification, a role contact preferred). | Likewise. |
| `measurement-method`; `methodology-uri` | The least direct `measurementMethod` among counted operators for the period; a URI reference to the methodology document, which cites this profile (one per object). | Likewise for the operator. |

Every object carries the draft's seven mandatory members: `updated`, `capabilities`, `provider`, `measurement-method`, `methodology-uri`, `period`, `target`. C1 is evaluated only on a network declaration. An object whose `network-topology` carries `member-of-network` is an operator declaration whatever its `target-type` says. Any object that is not an operator declaration by the two rules above (`target-type` `origin`, or `network-topology` with `member-of-network`) is a network declaration, and 7.2 rule 4 applies to it, so an object without `target-type` fails C-SFC-5.

**Withholding.** A publisher withholds an object when D2 to D6 or C-SFC-7 FAIL for it. The criterion rows C-SFC-1, 2, 3, 4 and 6, including those D5 prints, judge the network and not the read: they are findings, not grounds to withhold.

### 7.2 Claims, signing, units, noise

1. An object that claims SFC MUST carry `energy-unit` with `energy-consumption` and `carbon-unit` with any carbon figure. The draft's defaults are never relied on.
2. It MUST carry `signed` when it carries `ledger-evidence-2`, and SHOULD otherwise. For an object that claims SFC, `signed` MUST decode to a payload equal (JSON value equality, I-JSON-strict read) to the served object without `signed`; a duplicate member name in either makes the comparison FAIL, and any difference FAILs C-SFC-5. The `signed` strings of two correct signers can differ (header, member order), so strings are never compared, only decoded payloads; a signer SHOULD sign the RFC 8785 text of the object without `signed`. The key is chosen so:
   - *Operator declaration:* if it claims SFC it MUST be signed with `Ed25519` (Registry keys are Ed25519 only); another `alg` has no candidate key and S3 FAILs. If it does not claim SFC, another `alg` is verified only under a caller-pinned key; with no key pinned for the level, INFO "signed, not verified against a pinned key"; with one pinned that cannot serve it, "signature rejected". Candidates are the operator's Registry keys; use the key whose validity window contains T, not `updated` (self-asserted). A header `kid` only narrows candidates by RFC 7638 thumbprint; a verifier that cannot narrow to one key tries every candidate. A historical check needs a caller-supplied instant. In a shallow check the candidates are only caller-pinned keys: Registry keys count only after D2 authenticated the entry under a pinned registrar key, and a Registry or key set fetched from the declaration's own host is not pinned.
   - *Network declaration:* the key is the one the verifier pinned out of band for the publisher; no other location is defined (a known limit). ES256 and other asymmetric algorithms are allowed only here, under a pinned key. With a key pinned for the publisher that cannot serve the object's `alg`, the signature is rejected (S3).
   - A header `jwk` or `x5c` is not a key source, except an `x5c` chain to a trusted anchor (S3).
3. A network-level object that claims SFC, and any object with `ledger-evidence-2`, MUST NOT apply the draft's perturbation: figures equal the ledger sums rounded by 3.3 rule 3, and coarser rounding is perturbation.
4. A network declaration MUST carry `target-type` `service` and `disclosure-uri`, naming a machine-readable index of filed reports (not one report); C-SFC-5 FAILs without them.
5. A network declaration MUST NOT present figures for part of a year as that year's figures.
6. An object with `ledger-evidence-2` MUST write both `period` bounds as `month-bound` values. A network declaration with a local-offset calendar year MAY claim SFC through the disclosure form (C-SFC-2) only; it carries no `ledger-evidence-2`, and the ledger-dependent checks are NOT-EVALUABLE on it.
7. A network declaration's methodology document MUST state which parts of the network are measured and which modelled.
8. An object with `target-type` `origin` and `ledger-evidence-2` MUST carry `network-topology` with `member-of-network`; C-SFC-5 FAILs without it (C-SFC-7 needs the network to compare).

### 7.3 Two objects for Scope 2

The draft publishes market-based and location-based Scope 2 as two objects with the same `target` and `period`.

- The **primary** object has `carbon-accounting` `market-based` (omitted when it is incomplete for carbon, 7.5) and carries the section 8 extensions.
- The optional **paired location object** has `carbon-accounting` `location-based`. It has the seven mandatory members and the same `target`, `target-type`, `period`, `energy-consumption` (equal after conversion), `energy-unit`, `carbon-unit` and `disclosure-uri` as the primary. Its other members are `scope-2` (the sum of `scope2LocationKgCO2e`), `carbon-footprint` (the primary's Scope 1 sum plus its `scope-2` plus the primary's Scope 3 sum) and its own `carbon-intensity-gCO2e-per-kWh` (7.4). It carries no `scope-1`, `scope-3` or extensions, and SHOULD carry its own `signed` (the draft signs `carbon-accounting`). 7.2 rules 1, 3 and 4 apply to it, and its figures have k = 6. It gets no verdict of its own: its S6 i rows count toward the primary's verdict.
- Publish it only when every counted effective `CarbonAttested` of the period carries `scope2LocationKgCO2e` (superseded events do not count) and the primary is not incomplete for carbon. When the primary is incomplete for carbon, a paired object MUST NOT be published.
- A checker pairs each location object with the primary of its `target` and `period`, chosen as S4 chooses: the object with `carbon-accounting` `market-based`, else the one with `ledger-evidence-2`. Its location object is the one with `carbon-accounting` `location-based` and the same `target` and `period`; it is found also when the primary omits its carbon members. A location object with no such primary is INFO "unpaired object" and gets S2 only; one whose primary is incomplete for carbon is INFO "location object not applicable (incomplete)", S2 only. S6 i and D6 check a paired object. Two annual network objects differing only in `carbon-accounting` give one C1 result.

### 7.4 Mapping ledger sums to the primary object

All sums run over effective attestations of counted operators for the months of `period`. A network declaration that carries `ledger-evidence-2` MUST carry every member below, `ledger-evidence-2` and `offsets-retired-tCO2e` included, except:

- `scope-1`: SHOULD; MUST when the `operators` entries' `scope1-kgco2e` sum to more than 0, which S6 a tests.
- `carbon-intensity-gCO2e-per-kWh`: MUST be absent when energy is 0.
- the members 7.5 omits from an incomplete object: absent; the object is reported INCOMPLETE, not failed.

`renewable-energy` and `verifiable-attestation-uri` SHOULD be present where the declaration publishes `carbon-neutrality`. Where 8.2 says to omit `hardware-lifecycle`, or 7.5 omits a member, the object conforms. A disclosure-form network declaration (7.2 rule 6) carries the members it publishes.

| Ledger | Declaration member (primary object) |
|---|---|
| sum of `kWhConsumed` | `energy-consumption` with `energy-unit`, in the publisher's chosen unit. |
| sum of `scope1KgCO2e` | `scope-1`; MUST when the entries' `scope1-kgco2e` sum to more than 0, SHOULD otherwise (an absent `scope-1` reads as exact 0). |
| sums of `scope2KgCO2e`, `scope3KgCO2e` | `scope-2` (with `carbon-accounting` `market-based`), `scope-3`. |
| S1 + S2 + S3 summed | `carbon-footprint`: gross, never reduced by credits; with `carbon-unit`. |
| sums of Scope 2 and kWh | `carbon-intensity-gCO2e-per-kWh` = (sum of `scope2KgCO2e` x 1 000) / sum of `kWhConsumed`, from exact ledger sums, rounded by 3.3 rule 3. It is the object's own average, not a grid intensity. The identity energy x intensity = scope-2 holds for exact sums and within rounding for published ones. |
| `measurementMethod`; `nodeProfile` | `measurement-method`, the least direct value among counted events, or `third-party-modeled` when no counted effective `EnergyAttested` exists; `hardware-lifecycle` (8.2). |
| sum of `offsetsKgCO2e` / 1 000 | `offsets-retired-tCO2e` in `carbon-neutrality`. |
| the rule's results | `net-zero-status` in `carbon-neutrality`; first match: `achieved` when every counted operator met the rule in every active month, no month is silent for `CarbonAttested` and every month has an active operator (zero emissions with zero offsets counts, INFO "no emissions to cover"); `not-achieved` when the sum of `offsetsKgCO2e` is 0; else `partial`. |
| sum of `nodeCount` | `validated-node-count` in `network-topology`: the maximum over the period's months of the monthly sum, with `node-count-validation-method` saying so; an upper bound on simultaneous nodes. A 1.x `nodeCount` is read as given. |
| the above, per operator | `ledger-evidence-2` (8.5). |

An operator declaration with `ledger-evidence-2` MAY carry these members for its one operator, computed from its single `operators` entry, with no `validated-node-count` and no `network-offset-coverage`; `disclosure-uri` is OPTIONAL while a numeric top-level member is present, and one with no numeric member (all months silent) MUST carry `disclosure-uri` or `verifiable-attestation-uri`. 7.5 applies per operator. A negative `scope-1`, `scope-2` or `scope-3` on an object with `ledger-evidence-2` fails S6 b, unless the sums include a negative 1.x figure. `renewable-energy` is the publisher's market-based share and is not recomputed. The paired object takes the same energy sum and its own `scope-2`, footprint and intensity (7.3).

### 7.5 Silent months and incomplete objects

When an active operator-month is silent for a type, or a month of the period has no active operator (silent for both types), the object is **incomplete** (for an operator declaration, `network-offset-coverage` stays absent).

1. Omit the members derived from the silent type. Energy: `energy-consumption`, `energy-unit`, `validated-node-count` with `node-count-validation-method`. Carbon: `scope-1`, `scope-2`, `scope-3`, `carbon-footprint`, `carbon-accounting`, `offsets-retired-tCO2e`. Either type: `carbon-intensity-gCO2e-per-kWh`.
2. Still carry the extensions with the sums that exist. A carbon-silent month makes the operator's `offset-coverage-every-period` (where one exists) and `network-offset-coverage` false; a month with no active operator makes `network-offset-coverage` false; an energy-silent month leaves the flags to the carbon attestations.
3. A checker reports `INCOMPLETE (silent: operator, month, type)` or `INCOMPLETE (no operator: month)`; C-SFC-2 disclosure form is NOT-EVALUABLE. INCOMPLETE is an object verdict, not FAIL. An operator declaration with all figures omitted still carries `disclosure-uri` or `verifiable-attestation-uri`.
4. The paired location object follows the primary: absent when the primary is incomplete for carbon; when incomplete only for energy, it omits the same energy members and `carbon-intensity-gCO2e-per-kWh`.
5. When no operator-month has any effective attestation, the checker reports INCOMPLETE by rules 1 to 3.

### 7.6 Methodology parameters

The checks read these items from the methodology document. One JSON object holds them, validated by [sfc-parameters.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/sfc-parameters.json) (example: [sfc-parameters.example.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/examples/sfc-parameters.example.json)). The document links it as a file or, when Markdown or plain text, embeds it as a fenced `json` block under the heading `## SFC parameters`. A key the caller pins out of band takes precedence. A checker that cannot find an item a check needs reports NOT-EVALUABLE on that row, naming the item. An item is required only when a check that reads it applies.

| Item | Needed by | Form | Required when |
|---|---|---|---|
| `registrar-keys` | 5.1, D2 | Array of `{jwk, status, retired}`: `status` `current` or `former`; `retired` optional, a `full-date`, information only. At least one `current`. A former key verifies an entry only with INFO and never a checkpoint. Pinned for one network. | A Registry entry is verified |
| `retirement-registries` | L8b | Array of `https-uri`: the one form per registry. | An event cites a retirement |
| `reference-forms` | L8b, L9 | Array of `{registry, rules}`; `rules` a non-empty subset of `upper-case`, `lower-case`, `no-leading-zeros`, `no-surrounding-space`, `range-first-last` (`first-last` of two non-negative integers, first below last; a single serial is written alone, so `5-5` is not canonical). | The registry has a canonical form (optional) |
| `takeovers` | 4.4, L4 | Array of `{operator (did), type (EnergyAttested or CarbonAttested), ledger (non-empty string naming the old ledger), tip (hex64)}`. | After a takeover |
| `platform` | 4.4, C-SFC-6 | `hot-path` (name); `access` (`public` or `permissioned`); `mechanism` (`proof-of-work`, `proof-of-stake`, `proof-of-authority`, `dag`, `hybrid`, `bft`, `crash-fault-tolerant`; compared after ASCII lower-casing, trimming, and mapping each run of spaces, underscores and hyphens to one hyphen; `pow` is `proof-of-work`; `crash-fault-tolerant` covers Raft and notary clusters and is not proof-of-work). Public: `assessment` `{publisher, uri, period, figure, unit, method}` with `period` = `{start, end}` of `Z` instants, `end` exactly 12 calendar months after `start` (the 12-month equality is judged as moments (3.2), fractions included), `figure` a finite number >= 0, `unit` one of `Wh`, `kWh`, `MWh`, `GWh`. Permissioned: `n` (integer >= 1), `p-watts` (number > 0), `o` (number >= 1). | C-SFC-6 (the case's items only) |
| `registry-1x-digests` | D2 | Array of `{operator, sha256}` of a 1.x entry's RFC 8785 text. | A 1.x entry is authenticated |
| `beneficiaries`; `void-requesters` | 5.4 (ledger-side; not read by a verifier) | Array of `{beneficiary, operator}`; array of `did`. | Never (optional, ledger-side: no check reads them) |
| `scope2-basis-1x` | 12.1 | `market-based` or `location-based`. | A counted 1.x `CarbonAttested` has no `scope2Method` |

Prose disclosures no checker judges: measurement method (5.3), reasons for a registrar change (5.1), measured and modelled parts (7.2 rule 7), boundary exclusions (4.2), Scope 3 categories (5.4), and the standard or label of credits retired (4.3). No check reads them, and no row reports them; a reader checks them in the methodology document.

## 8. Extensions

### 8.1 Names

Names live under `https://andreibesleaga.com/sfc/extensions/`, are compared as strings and never fetched. Each value is an object. A consumer ignores unknown names. A minted name is never redefined: a change of meaning is 3.0 and mints a new name; a new optional member does not. "Required" below means within the extension value; a wrong JSON type is read as absent (the schemas are stricter and reject a wrong-typed optional member too), and a required member read as absent is reported by S6 a and the extension is not conforming.

| Name suffix | Level | Meaning | Section |
|---|---|---|---|
| `hardware-lifecycle` | both | What the hardware is and becomes. | 8.2 |
| `carbon-neutrality` | network, and an operator making its own claim | The offset-coverage position; `net-zero-status` is narrowed to offset coverage. | 8.3 |
| `network-topology` | both, different members | The network's shape; at operator level, membership. | 8.4 |
| `ledger-evidence-2` | network, and an operator publishing its own trail | Pointer to the ledger evidence. New in 2.0. | 8.5 |
| `ledger-evidence` | n/a | **Superseded.** A 2.0 emitter does not use it; a 2.0 checker reads it as "profile 1.1 evidence". | 12.1 rule 3 |

### 8.2 `hardware-lifecycle`

Schema: [ext-hardware-lifecycle.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-hardware-lifecycle.json).

| Member | Type | Required | Meaning |
|---|---|---|---|
| `general-purpose-hardware` | boolean | yes | True when the work runs on commodity hardware with other uses afterwards. |
| `single-use-asic-required` | boolean | yes | True when taking part needs purpose-built devices with no other use. |
| `expected-service-life-years` | number >= 0 | no | Stated by the publisher; not recomputed. |
| `embodied-carbon-in-scope-3` | boolean | no | True when manufacturing emissions are inside `scope-3` of this object. |
| `reuse-and-recycling-policy-uri` | `https-uri` | no | The published reuse and recycling policy. |

From the ledger, apply the C-SFC-3 test to every operator counted in the object (3.2, 7.4), not to the window's operators. When all pass, `general-purpose-hardware` is true and `single-use-asic-required` false; all five `hardwareClass` values count as general-purpose. When any counted operator would give NOT-DECLARED, or there is no Registry, omit the extension (the object still conforms) and never publish `general-purpose-hardware` false on this basis. The extension cannot travel alone: the object also carries a numeric metric, `disclosure-uri` or `verifiable-attestation-uri`.

### 8.3 `carbon-neutrality`

Schema: [ext-carbon-neutrality.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-carbon-neutrality.json).

| Member | Type | Required | Meaning |
|---|---|---|---|
| `net-zero-status` | `achieved`, `partial` or `not-achieved` | yes | The offset-coverage position. Ledger-backed: derived by 7.4. With no ledger, first match: `achieved` when `offsets-retired-tCO2e` x 1 000 is at least the gross `carbon-footprint` in kg (exact; zero with zero counts, INFO "no emissions to cover"); `not-achieved` when `offsets-retired-tCO2e` is absent or 0; else `partial`. Absent offsets count as 0; an absent `carbon-footprint` makes the status not derivable (S6 f INFO). |
| `renewable-procurement` | `on-site-generation`, `power-purchase-agreements`, `unbundled-certificates`, `supplier-tariff`, `grid-average` or `mixed` | no | How renewable energy was obtained. |
| `residual-emissions-tCO2e` | number >= 0 | no | Publisher's statement, not recomputed; a ledger-backed object SHOULD omit it. |
| `offsets-retired-tCO2e` | number >= 0 | no | Ledger-backed: sum of `offsetsKgCO2e` / 1 000; omitted when incomplete for carbon. |
| `offset-registry-uri`; `offsets-attested-by` | `https-uri`; string | no | Registry record of the retirements; issuer of the statement at `verifiable-attestation-uri`. |

A consumer or aggregator that displays `net-zero-status` or `netZero` MUST label it "offset coverage", MUST NOT display it as net zero, carbon neutral or climate neutral, MUST NOT display it without the words "offset coverage", and MUST show it beside the gross `carbon-footprint`. The no-ledger derivation is the 2.0 emitter rule; a 1.1.1 object meets it only through 12.1 rule 3d.

### 8.4 `network-topology`

An object carries the network-level or the operator-level members, not both (S6 a checks this). Schema: [ext-network-topology.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-network-topology.json).

| Level | Member | Type | Required | Meaning |
|---|---|---|---|---|
| network | `consensus-mechanism` | string | yes | Compared as 7.6 compares `mechanism`; used only to cross-check the platform statement (C-SFC-6). |
| network | `validated-node-count` | integer >= 0 | yes; omitted when incomplete for energy | Nodes counted over the period (7.4 when ledger-backed). |
| network | `node-count-validation-method` | string | with the count | One sentence on how it was reached. |
| network | `per-transaction-energy-Wh`, `nakamoto-coefficient`, `geographic-regions` | number >= 0; integer >= 0; integer >= 0 | no | Descriptors. |
| operator | `member-of-network` | `host` | yes with `ledger-evidence-2` (7.2 rule 8) | The `target` of the network the operator belongs to. |
| operator | `network-declaration` | `https-uri` | no | Where the network's declaration is published. |

`upstream` names suppliers and is not membership.

### 8.5 `ledger-evidence-2`

A pointer from the declaration to the signed trail, with figures recomputable from it. It sits inside the object, so `signed` covers it; `verifiable-attestation-uri` is for a third party's statement and never carries this pointer. Schema: [ext-ledger-evidence-2.json](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-ledger-evidence-2.json).

| Member | Type | Required | Meaning |
|---|---|---|---|
| `profile-version` | string `2.<digits>` | yes | `"2.0"` here. |
| `ledger-access-uri` | `https-uri` | yes | Where a verifier obtains a read (5.7). Access MAY be limited to consortium members and auditors. |
| `operators` | array of entries, at least 1 | yes | One per counted operator (exactly one in an operator declaration), any order. |
| `network-offset-coverage` | boolean | yes at network level; absent at operator level | True when every counted operator's `offset-coverage-every-period` is true and every month of the period has an active operator; false when any operator-month is silent for `CarbonAttested` or a month has no active operator. A value at operator level FAILs (S6 e). |

`operators` entry; all members required. Each figure is the sum over the operator's effective attestations for the months of `period` committed at or before `updated`, rounded by 3.3 rule 3.

| Member | Type | Meaning |
|---|---|---|
| `operator`; `origin` | `did`; `host` | The operator's DID and Registry `origin`. |
| `energy-head`, `carbon-head` | `hex64` or null | Head of that chain (3.2); null when none. |
| `energy-events`, `carbon-events` | integer >= 0 | Events of that type whose period lies in `period`, committed at or before `updated`; corrections and skipped events included. |
| `kwh`; `scope1-kgco2e` | number >= 0 | Sums of `kWhConsumed` and `scope1KgCO2e` (absent counts as 0). |
| `scope2-kgco2e`, `scope3-kgco2e` | number | Sums; at least 0 unless a counted 1.x event carries a negative figure. |
| `offsets-kgco2e` | number >= 0 | Sum of `offsetsKgCO2e`. |
| `offset-coverage-every-period` | boolean | True when every month of the period in which the operator is active has an effective `CarbonAttested` whose flag equals the section 6 comparison and is true. Energy-only silence does not change it. |

The object's `period` is the evidence period; there are no separate period members.

## 9. Checks

### 9.1 Result words

| Word | Meaning |
|---|---|
| PASS, FAIL | The pass condition of 9.2 holds, or does not. |
| NOT-EVALUABLE | A named input is missing, incomplete or out of reach; the row names it and says why. Never a pass. Causes: a silent month (C-SFC-2 only; C-SFC-1 and C-SFC-4 FAIL for it), a window with no active operator-month, a refused, stale or too-old read, a missing unit, an object not annual or not network-level, a missing platform statement, a period not in UTC months, a limit of section 10. |
| DECLARED, NOT-DECLARED | For C-SFC-3 and S6 g: the declaration is complete and in the list, or not. Never "C2 passed". An absent optional extension is NOT-DECLARED for C-SFC-3 and INFO "not declared" elsewhere. |
| INFO | A note on a row, not a result. |

Object verdicts: COMPLETE, INCOMPLETE (7.5), NOT-APPLICABLE (not an SFC object). A paired location object (7.3) gets no verdict of its own; its S6 i rows count toward the primary's.

- A refused read (HTTP 401 or 403) means the deep check was not run: NOT-EVALUABLE, never FAIL. Any fetch with no document (other non-2xx, timeout, TLS failure, size limit) is NOT-EVALUABLE with the cause. A 2xx with an invalid body is FAIL; with a wrong media type it stays FAIL under S1.
- A row skipped because a profile is not read (12.2 rule 3) is NOT-EVALUABLE. A repeated NOT-EVALUABLE is not escalated to FAIL.
- Each row names the period or window it covers. A report ends with one line counting rows by word (a `summary` object in the Appendix B expected files). That line and any summary MUST NOT read as a pass or "conforms" while any applicable row of C-SFC-1, 2, 4, 5, 6 or 7 is FAIL or NOT-EVALUABLE. NOT-DECLARED in C-SFC-3 is counted in the line and named in any summary.
- **Applicable rows.** C-SFC-5 for every object that claims SFC (S2 also runs on a body that claims none). C-SFC-2 disclosure form when S4 selects a year. D1 and C-SFC-7 for every object with `ledger-evidence-2`: without a read they are NOT-EVALUABLE ("no ledger read given"). C-SFC-1, 2 ledger form, 3, 4 and 6 only when the deep check runs with a read; C-SFC-6 is produced only by D5d.

### 9.2 The checks

Window and cut-off are as in 3.2. Active operator-months come from the Registry of the read; months of the window with no active operator are not counted. With no active operator-month in the window, C-SFC-1, C-SFC-2 ledger form and C-SFC-4 are NOT-EVALUABLE ("no operator active in the window"). When some, but not all, window months have no active operator, a PASS of C-SFC-1 or C-SFC-4 carries INFO "window not fully covered" and C-SFC-2 ledger form is FAIL when its step (2) applies, else NOT-EVALUABLE (see the row for the order). C-SFC-4 takes a set of months and a cut-off: alone, the window and T; in D5, the declaration's `period` and `updated`; in D7, `period` at cut-offs `updated` and `read-at`.

| ID | Input; window, cut-off | Pass condition | Result words |
|---|---|---|---|
| C-SFC-1 coverage | Read; window, T | Every active operator-month has an effective `EnergyAttested`. | PASS, FAIL (a silent month), NOT-EVALUABLE (no read; explicit T later than `read-at` (3.2); no operator in the window) |
| C-SFC-2 ledger form | Read; window, T | The sum of `kWhConsumed` over effective `EnergyAttested` of all active operator-months is below CAP. Order: (1) NOT-EVALUABLE if no read or an explicit T is later than `read-at` (3.2); (2) FAIL if the sum over existing window months is already at or above CAP, even with silent months (kWh is not negative, so a partial sum is a lower bound); (3) NOT-EVALUABLE if an operator-month is silent for energy or the window is not fully covered; (4) PASS. | PASS, FAIL, NOT-EVALUABLE |
| C-SFC-2 disclosure form | Network declaration; its `period`, no ledger | A calendar-year network object (both bounds on 1 January 00:00, `Z`, or one offset when it has no `ledger-evidence-2`) with `energy-consumption` and `energy-unit`, whose figure in kWh is below CAP. A local-offset year is judged as the draft defines; a gateway MUST NOT mix it with UTC months of a read. Annual objects of one `target` and `period` differing only in `carbon-accounting` have equal `energy-consumption` and give one result. When \|figure - CAP\| <= 0.01 x CAP, INFO beside the result, "within 1% of CAP: the methodology document must say no perturbation was applied" (7.2 rule 3 forbids perturbation; the statement is prose a reader checks, and no checker judges it, as 7.6). | PASS, FAIL, NOT-EVALUABLE (not annual or not network-level; figure or unit missing; annual objects with different targets, or of one target and period disagreeing; incomplete object) |
| C-SFC-3 hardware declared | Registry; operators active in any window month | Every such operator's `nodeProfile` is complete: class in the list, `asicForbidden` true, both dates full dates in order, `reusePolicy` in the list. It reads the entry as read, so a replacement applies to the whole window. An entry with no complete `nodeProfile` (a 1.x entry never re-signed, or one whose declaration is incomplete) is NOT-DECLARED, entry named. | DECLARED, NOT-DECLARED, NOT-EVALUABLE (no Registry) |
| C-SFC-4 coverage rule | Read; window, T | Every active operator-month has an effective `CarbonAttested` whose `netZero` equals the section 6 comparison, and the comparison holds. A non-compliant month fails the check while in the window. The row lists each late-filed effective attestation with its commit instant, and INFO "retirement rules L8b to L10 not applied: <event>" for each 1.x event counted. | PASS, FAIL, NOT-EVALUABLE (no read; explicit T later than `read-at` (3.2); no operator in the window) |
| C-SFC-5 declaration | A declaration | All hold: conforms to the draft (S2, strict); a network declaration with `ledger-evidence-2` carries every 7.4 member (or is INCOMPLETE), `target-type` `service` and `disclosure-uri`; an operator declaration without a numeric member carries `disclosure-uri` or `verifiable-attestation-uri`; an `origin` object with `ledger-evidence-2` carries `member-of-network`; units explicit; `signed` present with `ledger-evidence-2`, decodes to the served object, header and signature not rejected (S3); with `ledger-evidence-2`, both period bounds `month-bound` and the period one calendar year (network) or one month or one calendar year (operator), as 3.2 defines them; every figure meets 3.3 rule 3; `ledger-evidence-2.profile-version` matches `2.<digits>`; `updated` not after T plus the skew; a paired object carries the 7.3 members (its `signed` is a SHOULD, 7.2 rule 2, reported by S3). | PASS, FAIL |
| C-SFC-6 platform | Platform statement (7.6) and `consensus-mechanism`; T (permissioned: the window and T of its C-SFC-2) | Worst of two tests (FAIL, NOT-EVALUABLE, PASS). **Test 1, not proof-of-work:** FAIL when either `platform.mechanism` or `consensus-mechanism` is `proof-of-work` after the 7.6 comparison, even if the other disagrees; NOT-EVALUABLE when no statement names the mechanism or the value is outside the 7.6 list (a misspelling cannot pass a MUST NOT); else PASS. Other `consensus-mechanism` text is INFO. **Test 2, the named case.** *Public:* an assessment of a 12-month period that ended at most 18 months before T (3.2) puts the platform below CAP (figure in kWh). A period not exactly 12 calendar months FAILs; a missing or malformed `period`, `figure` or `unit` is NOT-EVALUABLE naming it. Its result needs no read, but the row is produced only by D5d. *Permissioned:* if every window month has an active operator, the C-SFC-2 ledger result (FAIL and NOT-EVALUABLE stay); else the 4.4 node bound decides, and a C-SFC-2 that is NOT-EVALUABLE only for partial coverage does not make C-SFC-6 NOT-EVALUABLE. | PASS, FAIL, NOT-EVALUABLE (no statement names mechanism or case; an item missing or malformed; permissioned: no read, explicit T later than `read-at` (3.2), an operator-month silent for energy) |
| C-SFC-7 bridge consistency | Declaration and read; its `period`, cut-off `updated` | D2 passes; per counted operator the heads, counts and sums recompute from events committed at or before `updated`, each `operators` member equal to the exact value rounded half to even to 6 decimals; the flags and `network-offset-coverage` recompute by 8.5, including a month with no active operator (operator level: only `offset-coverage-every-period`; a present `network-offset-coverage` FAILs); the top-level figures 7.4 derives equal the rounded exact value in the published unit; `net-zero-status` and `validated-node-count` equal the recomputed values; a paired object agrees likewise. | PASS, FAIL, NOT-EVALUABLE (no read; `read-at` before `updated`; stale read; no `ledger-evidence-2`; period not one calendar year (network) or not one month or one calendar year (operator); `member-of-network` missing; `profile-version` not read or of another major than the excerpt's; a limit of section 10; L9 not evaluable (D5); a 1.x-form event in counted months (D6)) |

### 9.3 Shallow check (HTTPS only)

Input: an origin or a document. A body is read under SFC 2 when any object in it claims SFC (3.2); otherwise only S1, S2 and S7 run and the verdict is NOT-APPLICABLE. A lone location object does not claim SFC: it gets S2 and INFO "unpaired object" (7.3). Each step has a report row.

1. **S1 fetch.** Fetch `https://<origin>/.well-known/sustainability-data`. `application/sustainability-data+json` is PASS; `application/json` is INFO "generic media type"; any other type FAILs. Record URL and type. Plain `http` is not fetched: NOT-EVALUABLE "plain http refused" (a run the caller allows for a local instance says so on the row). No document: NOT-EVALUABLE with the cause.
2. **S2 conformance.** Validate against the draft with `sustainability-wellknown-consumer` (npm, 0.8.2 or a later 0.8) in strict mode (`legacyCompat: false`). A document valid only under the default compatibility reading (-08 or -09 forms) FAILs (12.1 rule 3a); any violation FAILs. In another language, implement the draft's CDDL and MUST rules strictly, duplicate-member detection included; the library is the reference for what a violation is. A verdict that changes between library releases on unchanged input is a library defect to report, and the Appendix B vectors pass unchanged on the version used.
3. **S3 signature.** Verify each `signed` under an out-of-band or pinned key chosen by 7.2 rule 2. An `x5c` chain to an already trusted anchor, with an end-entity certificate identifying the publisher, counts as pinned.
   - The payload comparison needs no key and always runs on a decodable payload. A differing payload FAILs an object that claims SFC (S4 to S6 stop for it; S7 still records) and is otherwise INFO "signed payload differs" (S4 to S6 run on the served members).
   - A header or signature rejected under the draft's rules (`alg` `none` or MAC; `cty` absent or not `sustainability-data+json`; a `crit` parameter (this profile understands none, so any `crit` is un-understood, as the draft says); a signature that fails under a pinned key) leaves the member unverified: FAIL for an object that claims SFC, else INFO "signature rejected".
   - A JOSE header or payload that is not UTF-8 JSON (a byte-order mark included) is not decodable: detail "malformed header" or "malformed payload"; FAIL for an object that claims SFC, else INFO. No payload comparison runs on an undecodable payload.
   - No pinned key: INFO "signed, not verified against a pinned key" once the payload comparison passed; a key from the object's own header is trusted no further than the object. An `alg` other than Ed25519 and ES256 is verified if supported, else INFO "algorithm not supported". With a key pinned for the level, an `alg` that no pinned key can serve is rejected: FAIL for an object that claims SFC, else INFO "signature rejected". Exception: an operator declaration that claims SFC with an `alg` other than Ed25519 FAILs.
   - *Attestation (optional).* If `verifiable-attestation-uri` is present, fetching it under the fetch rules of section 10 and verifying under an out-of-band key is OPTIONAL: INFO "attested by <signer>" or "attestation not verified". Never PASS or FAIL.
4. **S4 selection and C-SFC-2.** The network target is the host of the origin given, or the `target` of the document's network declaration; record it. Take objects with that `target` (compared as the draft says) and `target-type` `service`, excluding any with `member-of-network`. If the check fetched the document, an object whose `target` differs from the retrieval host is INFO "target differs from retrieval host". No match, or no year selected (a -08 declaration has no `period`; a -09 `period` has full-date bounds, which never form a whole calendar year): S4 is NOT-EVALUABLE naming the target and C-SFC-2 has no row. Group by `period`; periods that are not a whole calendar year are excluded (INFO). Select the whole year with the latest `end` at or before T, reporting INFO "latest year selected: <start> to <end>" on the C-SFC-2 row (adding "ended more than 18 months before T" (3.2) when so); a year ending after T is INFO "period not yet ended at T"; other years INFO. The primary is the object with `carbon-accounting` `market-based`, else the one with `ledger-evidence-2`, else C-SFC-2 is NOT-EVALUABLE naming the missing input. Run C-SFC-2 disclosure form on the selected period. S6 and C-SFC-7 run on the primary and its paired object (the primary alone when incomplete for carbon).
5. **S5.** Run the remaining parts of C-SFC-5.
6. **S6 coherence**, on an object with `ledger-evidence-2` or any other SFC extension. Steps b to e are PASS or FAIL only with `ledger-evidence-2`; otherwise a disagreement is INFO "not derivable" and f is INFO. Steps a, g and h apply to every such object.
   - a. Every required member is present, of the right type and form: the required members of the extension tables (any object with an SFC extension) and, for a network declaration with `ledger-evidence-2` only, the 7.4 members (`scope-1` is required only when the entries' `scope1-kgco2e` sum to more than 0); except members 7.5 omits; heads are `hex64`. A wrong-typed optional extension member of the 8.2 to 8.4 tables is read as absent, with INFO naming the member; S6 a FAILs on it only when 7.4 requires it of that object. A `network-topology` value that carries both network-level and operator-level members (8.4) FAILs S6 a at either level, with or without `ledger-evidence-2`.
   - b. `energy-consumption`, `scope-1`, `scope-2`, `scope-3` and `offsets-retired-tCO2e` agree with the sum of the `operators` entries by the tolerance rule (3.3 rule 4); an absent `scope-1` with a positive entries' sum FAILs here too.
   - c. A present `carbon-footprint` equals `scope-1` + `scope-2` + `scope-3` by the tolerance rule (absent `scope-1` is exact 0, no tolerance term). An absent `scope-2` or `scope-3` makes it NOT-EVALUABLE, naming the member.
   - d. `carbon-intensity-gCO2e-per-kWh` P against q = (published `scope-2` in kg x 1 000) / (published `energy-consumption` in kWh): passes when |q - P| <= 1/2 x 10^-k(P) + (1 000 x (S + dS) / (E - dE) - q), with S and E the published scope-2 (kg) and energy (kWh) and dS, dE their half-units 1/2 x 10^-k converted to kg and kWh. If published energy is 0: when the entries' `kwh` also sum to 0 the member must be absent (present FAILs); when that sum is positive, d is NOT-EVALUABLE and C-SFC-7 checks by equality.
   - e. `network-offset-coverage` equals the conjunction of the entries' `offset-coverage-every-period` (a month with no active operator is seen only by C-SFC-7). At operator level it is absent and a present one FAILs.
   - f. `net-zero-status` is consistent with 7.4 (PASS or FAIL when ledger-backed, else INFO by 8.3). With F = `network-offset-coverage` (network) or the single entry's flag (operator): `achieved` when F is true; `not-achieved` when F is false and the sum of `offsets-kgco2e` is 0; else `partial`.
   - g. `hardware-lifecycle`, `net-zero-status`, `validated-node-count` and `renewable-energy` are reported DECLARED, never PASS. `net-zero-status` also has rows in f and C-SFC-7; `validated-node-count` in C-SFC-7 only.
   - h. An object with the old name `ledger-evidence` is handled by 12.1 rule 3.
   - i. On a paired object: `energy-consumption` equals the primary's after conversion; `carbon-footprint` equals the primary's `scope-1` + its own `scope-2` + the primary's `scope-3` by the tolerance rule; its intensity passes d on its own `scope-2`. Any failure FAILs.
7. **S7 record.** State: attributed to the origin and the `target` evaluated; integrity verified or not (never "verified" without a pinned key); figures self-asserted; accuracy unknown. Print T, `read-at` if a read was used, the period selected in S4, the age of `updated` at T, the profile version, and the consumer library's name and exact version.

### 9.4 Deep check (needs a ledger read)

Input: a declaration with `ledger-evidence-2` and a read (5.7).

1. **D1 access.** Obtain the read via `ledger-access-uri` or a given excerpt. Refused or no document: NOT-EVALUABLE. Apply the limits of section 10. The cut-off is `updated`; `read-at` must not be earlier. A stale read (5.7) is NOT-EVALUABLE. `ledger-evidence-2` needs `excerpt-version` 2 (version 1 is NOT-EVALUABLE). A read that does not meet the structure of `ledger-excerpt.json` (container types, instants, `network` a host) is NOT-EVALUABLE "read is not a well-formed excerpt" with the first violation. The two `profile-version` values must share a major, else C-SFC-7 is NOT-EVALUABLE naming both.
2. **D2 operator set and Registry.**
   - Network level: `operators` equals the set of operators active in any month of `period`, and each `origin` equals that DID's Registry `origin`; else FAIL. Operator level: one entry, and the DID's Registry entry has `origin` equal to `target` and is active in the period. The excerpt's `network` equals `target` (network) or `member-of-network` (operator), as hosts; else FAIL. A missing `member-of-network` is NOT-EVALUABLE.
   - FAIL when two entries share an `operator` or `origin`, or an entry's `active` intervals are unsorted or overlap (INFO for a 1.x entry). The DID-to-origin binding is the registrar's assertion (INFO).
   - Verify every 2.0 entry's `sig` under a registrar key from the methodology document the checker pinned (`registrar-keys`) or a caller-pinned key. Pins are per network host: the excerpt's `network`, or for an operator declaration its `member-of-network`, never the operator's own methodology document. A pin is the registrar public key `x` obtained out of band (the SHA-256, as `hex64`, of the methodology document's bytes as retrieved, taken out of band, also works); a URI alone is not a pin. With no pin: NOT-EVALUABLE, membership "claimed, not authenticated", INFO "registrar key not pinned".
   - The excerpt's `registrar.jwk` is a convenience copy: FAIL only when it matches none of the pinned or listed keys; if it is the only source, NOT-EVALUABLE and no authenticated PASS is printed (hash, link, fork and sum rows still run, reported "consistent but not authenticated").
   - With a pinned key, FAIL a 2.0 entry whose `sig` is absent, non-canonical, not `Ed25519` or does not verify; whose `network` differs from the excerpt's; that holds a small-order key ("weak key"); or whose operator has a 2.0-form event for a month before `profile2From`.
   - An event skipped under L1 only because its month is inactive: INFO naming operator and month. An entry whose `to` lies before a month with an attested event: FAIL "interval closed over attested months".
   - Each void act: `sig` verifies under the registrar key, `target` is a `CarbonAttested` committed before it, `commit` is distinct. A failing act is ignored with INFO "void ignored", except an extra member, which FAILs.
   - A 1.x entry has no `sig`. It is authenticated only if the `sha256` of its RFC 8785 text is in `registry-1x-digests` of the pinned methodology document, or the caller pins the entry. Otherwise D2 is NOT-EVALUABLE with INFO "unsigned Registry entry not authenticated", L5 for that operator is NOT-EVALUABLE, and dependent sums are "consistent but not authenticated".
   - A verifier holding an earlier verified checkpoint or entry for the operator SHOULD FAIL a lower `version` ("rollback"). An entry without `version` gets no rollback check; the caller supplies earlier verified `{operator, version}` pairs (vectors: `prior.versions`).
3. **D3 events.** Per counted operator and type, take the whole chain from `prev` null to the last event committed at or before `updated`. Each event: the hash recomputes and equals the ledger's (as received, unknown members included); row "encoding" holds (section 10); L1 to L3 and L5 hold. A failure FAILs that event's row. For a 1.x event, L1 reads `network` as the ledger's own and still checks `type` and `subject` = `actor`; L2 and L3 use the month mapped by 12.1 rule 1; an unmappable period is INFO. For every other operator with an event citing a retirement key, also take the whole chain and check hash, encoding, L1 to L3, L5, L6 supersession and the fork walk, skipping the in-period count and head comparisons. Row "ledger order": commit instants strictly increase along `ledger`, no `hash` repeats, no void `commit` equals a ledger or another void's; a violation FAILs "ledger order", reported first. Replay in array order only; never re-sort.
4. **D4 chains.** Every event of a counted operator links to the one before, ending at `prev` null or at a takeover link whose `prev` equals the tip listed in the methodology document. Two events of one chain sharing a non-null `prev`, or more than one chain start (null or takeover), is a fork. Takeover: if the old ledger is reachable, the verifier follows its chain back to `prev` null, and its read for that subject and type must end at the listed tip, and an event after it FAILs "cross-ledger fork". If it is unreachable, the part before takeover is NOT-EVALUABLE. If the methodology document is not pinned, report INFO "takeover not verified (methodology document not pinned)"; the part before is NOT-EVALUABLE, and the new chain's start is not a second start. Every in-period event committed at or before `updated` is on the walk; the declared head equals the head (3.2); the declared count equals the in-period events, skipped included. An event committed after `read-at` FAILs "commit after read-at" (every event of the excerpt).
   - *Checkpoint.* Verify its `sig` under a current registrar key of D2 (a former key gives "mismatch") and that its `network` and `read-at` equal the excerpt's. For each chain present, compare `tip` and `count` with the tip and total event count of the walk to `read-at` (not the period head and count). A chain listed with `count` above 0 but absent from the excerpt: INFO "chain of <operator> not in read", and the rows that depend on L9 (L9, D5, C-SFC-7) are NOT-EVALUABLE. Compare any digest present with the `sha256` of the RFC 8785 text of the entries sorted by `operator`, the `ledger` array, or the `voids` array. Row: "checkpoint: verified", "absent" or "mismatch"; any mismatch FAILs; absent is INFO "ledger read not authenticated: commit instants and completeness are the source's claim" (L9 holds only over the events supplied). A verified checkpoint without `ledger-digest` adds INFO "commit instants not authenticated: no ledger-digest": its chains carry `tip` and `count`, which cover event hashes but not commit instants, and L5, the cut-off, L3 and L10 depend on commit instants. A verified checkpoint with no `voids-digest` on a read with voids adds INFO "void acts not authenticated".
5. **D5 effective attestations, rule and retirements.** Replay the read by 5.6 up to `updated` for every operator the read yields. Run C-SFC-4 on the months of `period` with cut-off `updated`. Check L4 and L6 to L12 over the counted chains by that replay (L12 counts 2.0-form events only). L9 is judged at each event's own commit instant, never over the effective set at the cut-off. The effective set of a non-counted operator is the result of its verified chain; a failed or incomplete chain, or a read known to omit a citing operator's events, makes the L9 row NOT-EVALUABLE, never PASS. A FAIL in D3 or D5 FAILs the deep check (C-SFC-7). Report each late-filed effective attestation as INFO "late-filed, retirement dates asserted only".
   - **D5b.** Run C-SFC-1 and C-SFC-2 ledger form, one row each, over the evaluation window with T (anchored at `read-at` unless T is given), not `updated`. With an explicit T later than `read-at`, 3.2 applies to both.
   - **D5c.** Run C-SFC-3 on the Registry, one row. **D5d.** Run C-SFC-6, one row: the public case needs no read, and with no statement the row is NOT-EVALUABLE; the permissioned case uses the D5b C-SFC-2 result with the same T.
6. **D6 sums and declaration.** Recompute every `operators` member and the 7.4 top-level figures and compare by equality with the exact value rounded half to even to 6 decimals in the published unit. Recompute the coverage flags (8.5; operator level: only `offset-coverage-every-period`), `net-zero-status` and `validated-node-count`. For a paired object, recompute `scope-2` = sum of `scope2LocationKgCO2e`, its footprint, intensity and energy; any counted effective `CarbonAttested` lacking `scope2LocationKgCO2e` FAILs. A 1.x-form event in the counted months makes that operator's `offset-coverage-every-period`, `network-offset-coverage` and `net-zero-status` NOT-EVALUABLE, naming the event, unless a FAIL is already found; never PASS. This is C-SFC-7.
7. **D7 later corrections.** Events committed after `updated` and at or before `read-at` that supersede an in-period event or fill a silent in-period operator-month, and void acts in that span targeting an in-period event: INFO "superseded since publication". Run C-SFC-4 over `period` and C-SFC-2 ledger form over the D5b window at both cut-offs, `updated` and `read-at`, and state each, for example "as of updated: PASS; as of read-at: FAIL". A differing or NOT-EVALUABLE result is still INFO.
8. **D8 registry records (optional).** Follow `evidence` and each retirement reference to the registry. Confirm the credits are retired, in the operator's name, with beneficiary and period published; late-filed months first; and, where a registry publishes serial ranges, that no two references overlap. Fetch an `ipfs:` URI only through a configured `https` gateway, else NOT-EVALUABLE. NOT-EVALUABLE unless performed.
9. **D9 record.** State: `updated` and `read-at`; whether the declaration agrees with the ledger as committed at `updated` (and the as-of-read result when D7 differs); with no verified checkpoint, or one without `ledger-digest`, that it agrees with "the read obtained from <uri>" and that commit instants are the source's claim; whether D8 ran; whether the registrar key was pinned; the parsed host and connected address per fetch; who ran the check and when; any raised limit and MAX_READ_AGE. State also that the operator set is the Registry's, that completeness against the real network is not established, and that the readings are not established.

### 9.5 Exit status

A checker command exits 1 when any row is FAIL. Otherwise it exits 2 when a stage did not complete (the run is incomplete, so 0 would read as clean), on a usage error, or on an unexpected error that stops the run. Otherwise it exits 0: any other NOT-EVALUABLE row leaves the status at 0, so the status is not a conformance statement; read the overall result. The overall result is FAIL if any row is FAIL; else NOT-EVALUABLE if any row of C-SFC-1, 2, 4, 5, 6 or 7 is NOT-EVALUABLE or a stage did not complete; else PASS if any of those rows is present or an object verdict is COMPLETE or INCOMPLETE; else NOT-APPLICABLE.

## 10. Verifier requirements

A verifier that claims SFC 2 does all of the following. Each bullet cites the standard that defines the detail.

**Signatures**

- Verify Ed25519 as RFC 8032 section 5.1.7 says: reject S not below the group order L, decode R and A as canonical points, and use the cofactorless check [S]B = R + [k]A. Reject a `sig.value` that is not canonical `b64url`. Any of these fails row "encoding" of D3 (events) or D2 (Registry entries).
- Reject a public key A of small order (order divides 8, every non-canonical encoding included) and a signature whose R is of small order. A small-order Registry key is FAIL "weak key" in D2; the same check covers event keys in D3. A failed "encoding" or "weak key" is reported on that row only: the event is skipped and gets no second L5 row.
- Verify `signed` as JWS (RFC 7515), ES256 as RFC 7518 section 3.4, `Ed25519` as named in RFC 9864, key thumbprints as RFC 7638.

**Parsing**

- Read events, Registry entries, excerpts, each served object and the decoded `signed` payload as I-JSON (RFC 7493): no duplicate member names, no unpaired surrogates. A violation fails "encoding" (D3, D2) or, for a declaration, the 7.2 rule 2 comparison of the object that holds it (FAIL if it claims SFC, else INFO). A parser that cannot detect duplicates reports those rows NOT-EVALUABLE.
- A JOSE header or payload that is not UTF-8 JSON is rejected under S3.
- Canonicalise as RFC 8785 says and hash and verify every event as received. Check number-literal length before parsing.

**Fetching** (the draft's Security Considerations, with SHOULD read as MUST)

- Fetch only `https`. Bound the time, size and redirects of every fetch. Refuse at every connection, redirects included, any address inside a block that the IANA IPv4 or IPv6 Special-Purpose Address Registry lists with a Globally Reachable value other than True (loopback, private-use, link-local, 100.64.0.0/10, fc00::/7, IPv4-mapped IPv6, 0.0.0.0/8, 240.0.0.0/4, the documentation and benchmarking blocks, Teredo and 6to4), and the multicast ranges 224.0.0.0/4 and ff00::/8, which those registries do not list. Judge an address that embeds an IPv4 address (::ffff:0:0/96, 64:ff9b::/96, 64:ff9b:1::/48, 2002::/16) by the IPv4 address it carries as well. An address in no listed block is accepted by this rule. A verifier states which address rule it applies (a library's approximation is said to be one); where the connected address cannot be reported, D9 says so.
- URIs taken from untrusted data: `ledger-access-uri`, `evidence`, a retirement `registry`, `disclosure-uri`, `methodology-uri` and its parameters object, `verifiable-attestation-uri`, `network-declaration`, `offset-registry-uri`, `reuse-and-recycling-policy-uri`. Resolve a relative `disclosure-uri`, `methodology-uri` or `verifiable-attestation-uri` against the retrieval URI (RFC 3986 section 5) before applying these rules. A declaration read from a file or excerpt has no base: a relative reference, or an `evidence` that is not `uri-abs`, makes the check NOT-EVALUABLE, naming the member.
- Follow at most 3 redirects, `https` only; to another origin only if the target passes the address rule. A URI with userinfo (an `@` in the authority), a redirect target included, is NOT-EVALUABLE ("userinfo in URI").
- Escape every string printed from untrusted data (`reference`, `notice`, `gridIntensityRef`, `provider`) for the output format.
- A checker MAY use an allowlist of hosts or networks (such as a consortium ledger). It prints the allowlist in D9 and matches the parsed host, never the raw string.

**Limits.** These defaults belong to this profile, not the draft.

| Limit | Default | Limit | Default |
|---|---|---|---|
| Seconds per fetch / per check | 30 / 600 | Bytes per event | 65 536 |
| Fetches per check | 100 | Items in one array (except the arrays below) | 100 |
| Bytes per declaration / per read | 1 048 576 / 67 108 864 | Entries in `checkpoint.chains` | 2 000 |
| JSON nesting depth | 32 | Entries in `voids` | 10 000 |
| Operators in a read, entries in the Registry | 1 000 | Entries in each parameters array | 1 000 |
| Events per chain | 10 000 | Objects in a declaration array | 16 |
| Retirements per event | 100 | MAX_READ_AGE (T minus `read-at`) | 24 hours |
| Characters in a number literal | 32 | Clock skew (`read-at` or `updated` after T) | 5 minutes |
| Bytes in a string value (not `signed`) | 4 096 | `ledger`, `registry`, `operators` | own limits above |

- Byte limits count decoded bytes after Content-Encoding. Fetch and time limits are per check.
- Exceeding a limit is never FAIL and never PASS: it is NOT-EVALUABLE with the limit named, for the result that needs the unread data. A limit never suppresses a FAIL already established on data read in full. A literal over 32 characters is not expanded. A checker that raises a limit prints the value in D9.
- The ledger-side rules L8 and L12 apply the limits that bind an event, a chain and the Registry, so a ledger does not commit what a verifier must refuse.

## 11. Claims

A publisher, aggregator or checker writing about a declaration:

**MAY say**

- it conforms to the draft, having validated it;
- the annual network figure is below, at or above CAP, with figure, unit, boundary and the year's `start` and `end`, only when C-SFC-2 is PASS or FAIL;
- it **declares** general-purpose hardware, an offset-coverage position or a node count, naming the extension read;
- it agrees with the ledger read as of `updated`, after a deep check with C-SFC-7 PASS, naming who ran it, when, and the `updated` and `read-at` instants, plus the as-of-read result when D7 differs; with no verified checkpoint, "agrees with the read obtained from <uri>", not "agrees with the ledger";
- retired credits covered emissions under the offset-coverage rule, naming the rule, only when C-SFC-4 is PASS and no counted month holds a 1.x event;
- a named party attested, once the statement is fetched and verified under an out-of-band key (S3); a figure is a claim of the publisher, not verified.

**MUST NOT say**

- a figure is verified, true or accurate; the system is compliant, sustainable, green, carbon neutral or net zero as a finding of its own; the rule supports a consumer-facing climate-neutrality claim; `net-zero-status` or `netZero` means more than offset coverage;
- C2 passed; C1 passed on an operator or sub-annual declaration;
- the network's energy, carbon or node count covers all nodes or operators (it covers registered operator-months);
- a coverage result confirms retirement dates, unless D8 was performed for late-filed months;
- agreement as of `updated` is the current state, when D7 differs;
- figures from two publishers are comparable without equal `carbon-accounting`, `measurement-method`, period and a common boundary in both methodology documents;
- a valid `signed` or a `verifiable-attestation-uri` is evidence about a figure.

**What the checks do not show.** The shallow check shows the origin published these figures and, with a pinned key, that a signed object was not altered (the pin protects a signed object only; an unsigned object under a pin is still self-asserted, S3 INFO "not signed"); a signed object shows integrity, not freshness (a relay can serve an older year; S4 reports the year and its age as INFO). The deep check shows the declaration agrees with the read it was given. Without a verified checkpoint, the read's source is trusted for order, commit instants, completeness and Registry content, and L9 holds only over the events supplied. Operator set and `active` intervals come from the Registry as signed; the checks do not show that no other operator or node ran, that earlier Registry versions were identical, who owns a retirement (without D8 and a void act), or that readings were true. Independent assurance comes only from a third party's signed statement.

Shape of a conformance statement: *this declaration conforms to the draft, and under SFC profile 2.0 it declares X, Y and Z, of which the annual energy figure was checked against the 1 GWh cap on the date shown.*

## 12. Compatibility

### 12.1 Backward: reading 1.x

1. **1.x events.** A 2.0 verifier MUST read 1.x events inside an excerpt version 2 or an equivalent read. An excerpt version 1 is NOT-EVALUABLE in D1: the operator publishes a version 2 excerpt with `read-at` and `registrar` (Appendix C), and its registrar key is the independently obtained one of D2. A 1.x event is recognised by `payload.period` with `from` and `to` (full dates). When they are the first and last day of one UTC calendar month, they map to that month. Absent `scope1KgCO2e` is 0.
   - *Scope 2 basis:* the event's `scope2Method`, else `scope2-basis-1x` of the pinned parameters (a caller pin wins), else undeterminable. A market-basis figure enters 2.0 sums as it is. A location-basis or undeterminable figure makes the month silent for `CarbonAttested` in 7.4, 7.5 and 8.5 (no `scope-2`; coverage flags false; `net-zero-status` not `achieved`) and feeds `scope2LocationKgCO2e` of the paired object. C-SFC-4 still counts it as effective and judges it by L7 with INFO "retirement rules L8b to L10 not applied: <event>"; a standalone C-SFC-4 PASS on such months does not support "retired credits covered emissions", so the flag and the C-SFC-4 result may differ. Repair by a 2.0 correction (L6) that passes L8b, L9 and L10; a retirement dated after the due instant cannot be cited, so the month may stay uncovered. Each case is INFO naming the event.
   - *Energy method:* a missing or out-of-set `measurementMethod` counts as `third-party-modeled`, INFO naming the event and value; the event is not rewritten.
   - *Evidence:* `evidenceCid` is read as `evidence` for display only. A 1.x `evidence` is read as given (INFO if not `uri-abs`, never FAIL).
   - *Period not one month:* INFO "profile 1.x event, period not a month". It is used for no month's effective attestation; the report says sums and coverage are incomplete; a touched month with no other effective attestation is silent. For heads and counts it is placed by its days (`from` 00:00Z to 00:00Z after `to`): it counts in `energy-events` or `carbon-events` when that span lies in the declared `period`, is a head candidate when it ends at or before the period's end, and adds to no sum or flag. If `to` is before `from`, or a date is invalid, it counts nowhere (INFO).
2. **Judging.** The checker reports such a chain as "profile 1.x events". A 1.x event is judged only by the ledger profile 1.2 rules in Appendix C plus L11 and L11b; a chain valid under 1.2 is never failed retroactively. A 1.x event that breaks a rule as the table applies it (the whole rule for Yes, the named checks for L1 and L8) is skipped and reported on its own row; the table names the cases that are INFO or NOT-EVALUABLE instead. A 2.0 correction of a 1.x month has `supersedes` equal to the hash of the latest 1.x event of that month that no later event supersedes.

   | Rule | Applies to a 1.x event |
   |---|---|
   | L1 | Partly: `network` is the ledger's own; `type` is checked; `subject` = `actor` is an operator active in the mapped month. |
   | L2, L3, L4, L7 | Yes, with the mapped month (L2, L3). An unmappable period is INFO. |
   | L5 | Yes, under the key valid at commit. A `sig.alg` other than Ed25519 is NOT-EVALUABLE for that event, naming the `alg`; it still counts in sums, and any C-SFC-1, C-SFC-2 or C-SFC-4 result resting on it is NOT-EVALUABLE unless FAIL without it. |
   | L6 | Yes, 1.x form: a second 1.x event for a (subject, type, month) needs `supersedes` equal to the hash of an earlier event of that subject, type and mapped month, else it is skipped. Effective is the latest not superseded. |
   | L8 | The 1.2 payload members that ledger profile 1.2 does not mark OPTIONAL are present and of the stated type (`nodeCount`, `kWhConsumed`; `scope2KgCO2e`, `scope3KgCO2e`, `offsetsKgCO2e`, `netZero`), and `kWhConsumed`, `nodeCount` and `offsetsKgCO2e` are not negative; an event missing one is skipped under L8. The digit limits of 3.3 do not apply (the literal limit does); a figure over 15 digits is read as its binary64 text. A negative `scope2KgCO2e` or `scope3KgCO2e` is read as is, with INFO. |
   | L8b, L9, L10 | No: a 1.x event has no `retirements`; D8 stays NOT-EVALUABLE for it. |
   | L11, L11b | Yes: a 1.x-form event after a 2.0 event of its operator, or for a month at or after `profile2From`, FAILs. |
   | L12 | No. A month with more than 20 1.x events is INFO; none is skipped. |
   | Encoding (3.6, 10) | INFO, not FAIL, for a 1.x event. The signature is still verified as the 1.2 reference code reads it (decoded 64 bytes against the key). |

3. **Declarations.** 3a and 3b are exclusive: 3a for an object that fails S2 on a pre-10 wire, 3b for one that passes.
   - 3a. Only -10 wire declarations are checked as conforming. One written for an earlier draft (`reporting-period`, `mtCO2e`, free-text `measurement-method`; every 1.0 declaration as published; 1.1 text at rfc commit `2d4822a`, the -07 wire) FAILs S2, and S4 is NOT-EVALUABLE because no whole calendar year is selected, with no C-SFC-2 row. Convert it first. Whenever it carries `ledger-evidence`, the report has only the S2 row, an INFO row "LEGACY" ("profile 1.1 evidence, pre-10 wire") and the NOT-APPLICABLE verdict; S4 to S6 do not run, and its sums are INFO only. A 1.1.1 declaration is on the -10 wire and goes through S2 normally.
   - 3b. An object with `ledger-evidence` and not `ledger-evidence-2` that passes S2 is reported "profile 1.1 evidence, not an SFC 2.0 declaration"; no 2.0 check can PASS on it. Its members are read as disclosure profile 1.1 defines them. Comparing sums with top-level figures is a reading aid (tolerance rule; `network-offset-coverage` read as 1.1: sum(S2 + S3) <= sum R); a mismatch is INFO "profile 1.1 evidence coherence", never FAIL. Units and `signed` are INFO. C-SFC-7 and 9.4 do not run; S6 b to f are INFO "not derivable". It is never failed by a rule absent from 1.1.
   - 3c. An object with both names is a 2.0 object; the old name is INFO "superseded name present".
   - 3d. An object with only the three 1.0 extension names is judged as a 2.0 object without a ledger (8.3) by every rule for an object that claims SFC. 7.2 rules 2 and 3 can FAIL it (a deliberate tightening). One omitting `energy-unit` or `carbon-unit` FAILs 7.2 rule 1.
   - 3e. An operator object without `ledger-evidence-2` keeps the draft's rules for `period`; C-SFC-7 does not apply.
4. **Emitting.** An emitter MUST NOT emit 1.x forms after adopting 2.0. The adoption commit is the operator's first 2.0 event of either type. A chain MAY hold 1.x events before it and 2.0 events after (L11, L11b); the shape of `period` tells them apart. A 1.x event has no `network` and is read under the ledger's. An operator that stays on 1.x is not failed; under `ledger-evidence-2` its months are NOT-EVALUABLE for offset coverage (D6), never PASS.
5. The pinned 1.x locations stay reachable and unchanged (Appendix E).
6. **1.x Registry.** A 1.x entry is recognised by `keys[].public-jwk`, `valid-from-commit` and no `sig`; its members read as `jwk`, `validFromCommit`, `validToCommit`. Its `active` intervals are full dates with inclusive `to`: active in a month when `from` <= the month's last day and (`to` null or `to` >= its first day). Shape selects the reading rules and never replaces authentication (D2). When the registrar first re-signs a 1.x entry it writes the whole entry in 2.0 form. Keys are renamed. Each interval becomes month bounds: `from` is the first instant of the month holding the 1.x `from`; `to` is the first instant of the month after the one holding the inclusive 1.x `to`, or null. Overlapping or meeting intervals merge (1 to 10 January and 20 to 31 January become one January interval). The registrar also writes `network` and, once, `profile2From`. It also writes `nodeProfile` (the 1.x record's declaration where the entry has one, else a new declaration from the operator) and `version` 1. A carried-over declaration must meet 5.1 (`asicForbidden` true, a 2.0 `hardwareClass`); if it does not, the operator supplies a new one. A 1.x entry that was never re-signed has no complete `nodeProfile`, so C-SFC-3 still reports NOT-DECLARED for it. The active months stay the same, so this is a change of form, not an alteration of a past interval.

### 12.2 Forward

1. **Draft.** SFC 2 relies only on the members and values of Appendix D. A later draft revision that keeps every item and adds no value to `energy-unit`, `carbon-unit`, `measurement-method` or `target-type` needs no change; the checker takes the revision from its consumer library. Appendix D is the diff target.
2. **Versions.** 2.x adds and never changes meaning; a change of meaning is 3.0. Additions are new optional members in events, the Registry entry or extensions. A reader ignores unknown members (except the cases listed in 3.6 rule 3, and 8.4). Closed lists (`hardwareClass`, `reusePolicy`, `measurementMethod`, `net-zero-status`, `renewable-procurement`) do not grow in 2.x. A value outside a draft closed set (units, `measurement-method`, `target-type`) that the library rejects is an S2 FAIL (a checker without the library uses the draft's CDDL enum). A value the library accepts but this profile has no rule for is NOT-EVALUABLE for each check needing it, naming member and value. A value outside a closed list of this profile is INFO naming member and value, and for a required member also makes S6 FAIL.
3. **`profile-version`.** `"2.1"` and so on mark additive changes. A `profile-version` of `ledger-evidence-2` or an excerpt not matching `2.<digits>` is a profile this checker does not read: INFO "profile X not read", the C-SFC-7 row NOT-EVALUABLE ("profile X not read"), no S6 coherence or deep check. The row counts as applying under 9.1. C-SFC-5 keeps its 9.2 pass condition, which requires a `2.<digits>` value: a declaration whose `ledger-evidence-2.profile-version` is not read FAILs C-SFC-5 (Appendix B, v17-limits). An excerpt whose `profile-version` is not read leaves C-SFC-5 untouched and makes only C-SFC-7 NOT-EVALUABLE (D1). The superseded `ledger-evidence` value `"1.2"` is never judged by this rule (12.1 rule 3b).
4. **Platforms and CAP.** No platform is named normatively. If a later column revises CAP, 2.x carries the new figure as a parameter with its source and nothing else changes.

## 13. References

**Normative.** [RFC 2119](https://www.rfc-editor.org/info/rfc2119) and [RFC 8174](https://www.rfc-editor.org/info/rfc8174) (BCP 14); [RFC 3339](https://www.rfc-editor.org/info/rfc3339) (timestamps); [RFC 3986](https://www.rfc-editor.org/info/rfc3986) (URIs); [RFC 5890](https://www.rfc-editor.org/info/rfc5890) (IDNA A-labels); [RFC 7493](https://www.rfc-editor.org/info/rfc7493) (I-JSON); [RFC 7515](https://www.rfc-editor.org/info/rfc7515) (JWS); [RFC 7518](https://www.rfc-editor.org/info/rfc7518) (JWA, ES256); [RFC 7638](https://www.rfc-editor.org/info/rfc7638) (JWK thumbprint); [RFC 8032](https://www.rfc-editor.org/info/rfc8032) (EdDSA); [RFC 8037](https://www.rfc-editor.org/info/rfc8037) (OKP keys); [RFC 8259](https://www.rfc-editor.org/info/rfc8259) (JSON); [RFC 8610](https://www.rfc-editor.org/info/rfc8610) (CDDL); [RFC 8785](https://www.rfc-editor.org/info/rfc8785) (JCS); [RFC 9864](https://www.rfc-editor.org/info/rfc9864) (fully-specified `Ed25519`); [IANA IPv4](https://www.iana.org/assignments/iana-ipv4-special-registry/) and [IANA IPv6](https://www.iana.org/assignments/iana-ipv6-special-registry/) special-purpose registries; [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core); [DID Core](https://www.w3.org/TR/did-core/); the [draft](https://datatracker.ietf.org/doc/draft-besleaga-sustainability-wellknown/10/) (-10); the column ([doi:10.1145/3809296](https://doi.org/10.1145/3809296)).

**Informative.** GHG Protocol: [Corporate Standard](https://ghgprotocol.org/corporate-standard), [Scope 2 Guidance](https://ghgprotocol.org/scope-2-guidance), [Scope 3 Standard](https://ghgprotocol.org/corporate-value-chain-scope-3-standard); [SBTi Corporate Net-Zero Standard v1.3.1](https://files.sciencebasedtargets.org/production/files/Net-Zero-Standard.pdf) (criteria C12, C28, recommendation R12; v2.0 is also published, validation under it starts in the first quarter of 2027); [Directive (EU) 2024/825](http://data.europa.eu/eli/dir/2024/825/oj) (inserts point 4c into Annex I of Directive 2005/29/EC); [Commission services, Questions & Answers on Directive (EU) 2024/825](https://commission.europa.eu/document/download/3c257883-bb2a-4dd9-a6dc-501d587bb34f_en?filename=faq-empowerting-consumers-gtd.pdf) (Brussels, September 2026; preliminary views, not an official position; Q10 on Annex I point 4c); [Delegated Regulation (EU) 2025/422](http://data.europa.eu/eli/reg_del/2025/422/oj) (Annex, Table 2, field S.8, recital 8); [CSRD](http://data.europa.eu/eli/dir/2022/2464/oj); [MiCA](http://data.europa.eu/eli/reg/2023/1114/oj); [WEEE](http://data.europa.eu/eli/dir/2012/19/oj); [CBECI](https://ccaf.io/cbnsi/cbeci), [CCAF](https://ccaf.io/cbnsi), [CCRI](https://carbon-ratings.com).

## Appendix A. JSON Schemas (normative)

JSON Schema 2020-12, restating the member tables and tested against the checker's shape tables, in [`schemas/`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/tree/main/sfc-compliance/schemas/). A document is valid when it validates and meets every rule a schema cannot state (L4 to L12, Registry uniqueness, ledger order, and requirements that depend on level or on an incomplete object, such as `validated-node-count` and `network-offset-coverage`, which S6 a states). If schema and text differ, the text wins and the schema is defective. Unknown members are allowed, except in a void act and a checkpoint (3.6 rule 3), for the four names 3.6 rule 3 forbids at the top level of a Registry entry, and for the other level's members in `network-topology` (8.4). The schemas carry the limits of section 10 as `maxLength` and `maxItems`; for figures they carry a minimum and a maximum below 10^15, because a schema cannot constrain digits (L8 does). `ledger-excerpt.json` accepts, per `ledger[].event`, a 2.0 event or a 1.x event (no `network`, `measurementMethod`, `retirements` or `evidence` required), and per `registry[]` a 2.0 or 1.x entry (12.1 rules 1 and 6); the event schemas validate 2.0 form only. The declaration itself is validated by the draft's CDDL through the consumer library.

| File | Validates | Section |
|---|---|---|
| [`registry-entry.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/registry-entry.json) | A Registry entry. | 5.1 |
| [`event-energy.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/event-energy.json), [`event-carbon.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/event-carbon.json) | The two event types. | 5.2 to 5.4 |
| [`ledger-excerpt.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ledger-excerpt.json) | An excerpt with `voids` and `checkpoint`; `profile-version` matches `^2\.[0-9]+$`. | 5.8 |
| [`ext-hardware-lifecycle.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-hardware-lifecycle.json), [`ext-carbon-neutrality.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-carbon-neutrality.json) | Extension values. | 8.2, 8.3 |
| [`ext-network-topology.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-network-topology.json) | Both levels; `validated-node-count` optional, required unless incomplete for energy. | 8.4 |
| [`ext-ledger-evidence-2.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/ext-ledger-evidence-2.json) | The value of `ledger-evidence-2`. | 8.5 |
| [`sfc-parameters.json`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/blob/main/sfc-compliance/schemas/sfc-parameters.json) | The methodology parameters object. | 7.6 |

## Appendix B. Test vectors (normative for implementers)

[`vectors/`](https://github.com/andreibesleaga/rfc-sustainability-wellknown/tree/main/sfc-compliance/vectors/) holds:
- `make-vectors.mjs`: generates every input and expected output from fixed values, using the reference verifier of `sfc-compliance/lib/` (the checker's own code, not a copy); its scenarios are in `cases/`. The clock is T = 2026-05-02T00:10:00Z, given as an explicit T, so the window is April 2025 to March 2026. Every excerpt's `read-at` equals T, so the explicit T does not trigger "read older than T", except one excerpt in v19-window (scenario `explicit-T-after-read-at`) whose `read-at` is 2026-03-20T00:00:00Z; it proves the "read older than T" rule of 3.2. The key is the RFC 8032 section 7.1 test 1 key.
- `crosscheck.py` and its modules in `sfcx/`: Python standard library only, independent of `lib/`. It recomputes hashes, sums and rule results and compares them with the expected outputs.
- `inputs/<id>.json` and `expected/<id>.json`: one input and its expected rows per case, in the result words of 9.1, with the `summary` object of 9.1. An input may carry `prior.versions` (D2 rollback). The expected results are binding. With `worked/` there are 35 files and 184 scenarios.
- `worked/` (`input.json`, `expected.json`): one generated case with three operators, twelve months, one correction, one silent month, 1 500 kg of a 2 t retirement in January and 500 kg in February, and one rounding case.

Every figure is invented. Where the description of `worked/` above and the files in `worked/` differ, the files win.

| Case | What it proves | Sections |
|---|---|---|
| v01-canonical, v02-hash | RFC 8785 bytes, event hash and signature of one event. | 3.6 |
| v03-effective | One correction; a rule-breaking event is skipped. | 3.2, 5.5, 5.6 |
| v04-sums-month, v05-sums-year | Sums, heads, counts; an operator with only last-year events (head set, count 0). | 7.4, 8.5 |
| v06-two-objects | Market and location objects; a location `scope-2` of 12.5 against exact 12.51 FAILs C-SFC-7 by equality (k = 6) and S6 i through the footprint. | 3.3, 7.3, S6 i |
| v07-silent | Silent months, incomplete objects, month with no operator, unpaired location object, operator declaration with all months silent. | 7.3 to 7.5, 8.5 |
| v08-fork | Shared non-null `prev`, two chain starts, cross-ledger fork; first events of different chains sharing null are no fork. | 4.4, D4 |
| v09-bad-signature, v16-noncanonical-signature | A failing signature; non-zero trailing bits or S not below L fail "encoding". | L5, 10 |
| v10-duplicate-retirement | One tonne twice; trailing-slash registry (L8b); two operators on one key, order decides; citations whose `retiredAt` differ only in a fraction of a second (L9); non-canonical `reference` (L8b); overlapping ranges (L9). | 5.4, L8b, L9, 7.6 |
| v11-late-retirement | `retiredAt` after the due instant, and after the commit instant. | L10 |
| v12-wrong-flag | `netZero` contradicting its figures. | L7 |
| v13-late-correction | Correction after `updated` is INFO; as-of-read FAIL; C-SFC-2 and C-SFC-4 at both cut-offs; late void act. | 5.4, 5.6, D7 |
| v14-tolerance | Tolerance edges; half-even tie 1.2345675 gives 1.234568; wrong rounding direction FAILs by equality; digit limit (999999999.999999 accepted, 1000000000.000001 and a 16-digit integer rejected); footprint 10.4 vs scope-2 4.5 + scope-3 5.5, no scope-1, difference 0.4: without `ledger-evidence-2` (k = 1, tolerance 0.15) S6 c is INFO "not derivable"; with it (k = 6, tolerance 0.0000015) FAIL; small-energy intensity bound; a 17-digit 1.x figure; a published figure over the 15-digit limit (C-SFC-5); a wrong-typed optional extension member (INFO); a `network-topology` value of both levels with and without `ledger-evidence-2`. | 3.3, S6, 12.1 |
| v15-profile-1x | 1.x events (location basis, non-month period, out-of-set method, negative scope-3, other `alg`); a 1.1 declaration; mixed chain; `scope2-basis-1x` present and absent; multi-month span; duplicate 1.x month; more than 20 events; excerpt version 1; a 1.2 figure member absent (L8); an operator declaration over a 1.x month (C-SFC-7 names that operator's event). | 12.1 |
| v17-limits | One case per limit, each NOT-EVALUABLE naming it; relative URI with and without a base; unread `profile-version`; userinfo URI; a limit hit after a FAIL keeps the FAIL. | 10, 12.2 |
| v18-registry-1x | 1.x entry with and without digest; conversion to 2.0 form with merged intervals; `network` mismatch FAILs. | 12.1 rule 6, D2 |
| v19-window | Empty Registry; late `active.from`; explicit T after `read-at`; stale read; C-SFC-4 over window and period; C-SFC-6 combinations; public case at exactly 18 months. | 3.2, 5.7, 9.2 |
| v20-selection | Years 2024 and 2025; a year ending after T; two 2025 objects, none market-based; an upper-case host target; a target that differs from the retrieval host. | S4 |
| v21-net-zero-order | All-zero emissions; silent month with and without offsets; no-ledger derivation incl. absent footprint. | 7.4, 8.3 |
| v22-period-offset | A year with `+02:00` bounds: disclosure-only passes or fails C-SFC-2; with `ledger-evidence-2` C-SFC-5 FAILs. | 3.2, 7.2 |
| v23-wrong-network | An event replayed from another network. | L1 |
| v24-1x-after-2x | 1.x-form event after a 2.0 event, in the other chain, at or after `profile2From`. | 5.1, L11, L11b |
| v25-replay-order | Correction after a dependent event; retroactive key closure; shortened `to` over attested months. | 5.1, 5.6, D2 |
| v26-operator-no-membership | No `member-of-network`: C-SFC-5 FAIL, D2 NOT-EVALUABLE; no pin for the claimed network. | 7.2, D2 |
| v27-rollback | Lower `version`; digest mismatches; checkpoint omitting a chain; checkpoint under a former key. | 5.8, D2, D4 |
| v28-citation-void | Void of a first citation, of a correction, of a superseded event; invalid voids ignored. | 5.4, 5.6, D2 |
| v29-signed-rejected, v29b-duplicate-members | Rejected headers and signatures, any `crit` included, and a signature under a key, or an algorithm, the pin cannot serve; differing payload; duplicate members and lone surrogates, with and without a pin; a duplicate charged to the object that holds it; a served body that is valid JSON but not a declaration object or an array of them. | 7.2, S3, 10 |
| v30-registry-binding | Shared `operator` or `origin`; overlapping intervals; wrong `operators[].origin`. | D2 |
| v31-parameters | Parameters with every item; one missing an item; `mechanism` spellings; assessment of 11 and 12 months; MWh figure; `crash-fault-tolerant` as platform `mechanism`, with a `consensus-mechanism` text in and outside the list (INFO); assessment bounds with a fraction, compared as moments. | 7.6, 9.2 |
| v32-ledger-order, v33-registrar-objects | Order violations; registry entry in `voids[]`; small-order keys as A and as R; registrar key pinned for another host. | 5.8, 10, D3, D4 |

## Appendix C. Mapping from 1.x

The 1.x rules a 1.x event is judged by (12.1) are those of ledger profile 1.2 section 3.1 rules 1 to 8 and the section 4 comparison. Items the draft governs (`sci-score`, `functional-unit`, `upstream` by level) have no 2.0 row.

| 1.x item | 2.0 form |
|---|---|
| Envelope members; `sig` "unless the Registry records another algorithm" | Unchanged plus `network` (1.x events have none); `Ed25519` only (5.2, 3.6). |
| Rules one attestation per period, `subject` = `actor`, `prev`, head, key at commit, `ts` | L6, L1, L4 (the tip), L5, L3. |
| `period {from, to}` full dates | `{start, end}` month bounds; 1.x read by 12.1. |
| `nodeCount` (nodes that ran in the period) | Monthly peak; a 1.x value is read as given, so the 7.4 sum stays an upper bound. |
| `measurementMethod` (SHOULD) | Required, closed four values; a missing 1.x value counts as `third-party-modeled`. |
| `evidenceCid` | `evidence` (`uri-abs`); a 1.x value is read as `evidence` for display only (12.1). |
| `scope2KgCO2e`, `scope2Method` | Market-based only; location basis moves to `scope2LocationKgCO2e`; 1.x basis by `scope2-basis-1x`. |
| (none) | `scope1KgCO2e` (optional), `retirements`, `network`, `scope2LocationKgCO2e`. |
| `scope3KgCO2e` | Unchanged name; not negative in 2.0; a negative 1.x figure is read as is, INFO. |
| Signed allocation document | Dropped; `retirements` under the normal key rule replace it (`registry-uri` to `registry`, `tonnes-retired` to `tonnesRetired`, `parts[].kg` to `kg`, `retired-in` to `retiredAt`). |
| "Known gap: double allocation" | Closed for identical keys by L9; not for 1.x months, whose credits L9 cannot see. |
| Anchor-chain statement, per-project platform pins, standard-or-label SHOULD | Dropped as rules; anchor informative (Appendix E); label is a prose disclosure (7.6). |
| Registry `active` full dates, `keys[public-jwk, valid-from-commit, valid-to-commit]` | Month bounds, `jwk`, `validFromCommit`, `validToCommit`; plus `network`, `sig`, `version`, `profile2From`; 1.x read by 12.1 rule 6. |
| `hardwareClass` four values | Five (adds `accelerator-server`, a Registry value only). `asicForbidden` now `true`. A 1.x entry's declaration is carried over only if it meets 5.1; otherwise the operator writes a new one (12.1 rule 6). |
| Excerpt v1 (`fixture`, `hash-algorithm`, `event-encoding`, `retirements`, `publication`) | Excerpt 2 (5.8). Dropped fields are fixed by 3.6 or live in events. A version 1 excerpt is NOT-EVALUABLE in D1. |
| v1.1 endpoints and `application/jose+json` | Dropped; the declaration, `disclosure-uri`, `methodology-uri` and `signed` replace them. |
| C-SFC-1 (35-day test) | Window coverage. The 35-day test is dropped. |
| C-SFC-2, C-SFC-3, C-SFC-5 | Window-anchored with a read-older-than-T rule; narrowed to operators active in the window; conforms to -10. |
| C-SFC-4 ("flag until next compliant") | A non-compliant month fails the check while in the window. |
| C-SFC-6 "current" | Two cases plus the not-proof-of-work test; "current" is 18 months; migration 12 months, hot path only. |
| Shallow 1.2 steps 1 to 6; deep steps 1 to 8; checker 1.1.1 and gateway rows and refusal codes | S1 to S7; D1 to D9 (anchor step dropped, step 8 is D8); rows and codes map to S, D and L rules; `E-METHOD`, `E-DISCLOSURE`, `E-CONFIG`, `S0` and `D0` dropped. |
| Verdict words PASS, FAIL, DECLARED, ABSENT, REFUSED, WARN, INFO | PASS, FAIL, NOT-EVALUABLE (was REFUSED, ABSENT), DECLARED, NOT-DECLARED, INFO; WARN dropped. |
| `ledger-evidence` (`hash-algorithm`, `event-encoding`, `period-start`, `period-end`, `anchor`) | `ledger-evidence-2` (8.5); those members dropped; `network-offset-coverage` is now a conjunction needing an active operator in every month; entries add `origin`, `scope1-kgco2e`. |
| Operator `period` "any" | A month or a calendar year when it carries `ledger-evidence-2`. |
| `net-zero-status` | Offset coverage of gross `carbon-footprint`; `partial` means offsets above 0 and below the footprint; only retired credits count (1.1 also counted renewable instruments). A 1.x value is compared as INFO only. |
| `carbon-intensity-gCO2e-per-kWh` (grid intensity) | The object's own market-based Scope 2 per kWh (7.4). A grid-weighted figure on a ledger-backed object FAILs S6 d. |
| `renewable-energy` SHOULD for every network declaration; integer-MWh advice | SHOULD only with `carbon-neutrality`; a coarser unit (3.3). |
| Perturbation (ledger profile only); `signed` MUST or SHOULD | 7.2 rule 3 for every network-level SFC object; 7.2 rule 2. |
| Files: `PROFILE.md`, `PROFILE-1.0.md`, `SFC.md`, ledger `SFC_COMPLIANCE.md`, `sfc-check.mjs` 1.1.1, `README.md`, examples, fixtures | One profile text here; the folder keeps a pointer; the checker is 2.0.0; examples regenerated; the four 1.1.1 fixtures the tests use kept under `test/fixtures/profile-1.1/`: the two 1.1.1 examples (`sfc-network.example.json`, `sfc-operator.example.json`, judged by 12.1 rule 3d as 2.0 objects without a ledger), `legacy-08` (expects S2 FAIL and S4 NOT-EVALUABLE with no C-SFC-2 row) and `ledger-evidence` (expects 12.1 rule 3b). Earlier texts stay at the commits in E.3. |

## Appendix D. Draft members relied on

All from the draft -10. SFC 2 states its own rules for string comparison, `period` bounds, upper-case `T` and `Z`, and whole months (3.2, 3.5, 5.3, 7.1).

| Item | Used in |
|---|---|
| Path `/.well-known/sustainability-data`; `application/sustainability-data+json`; `application/json` readable; HTTPS only | S1 |
| One object or an array; same `target` and `period` may repeat when `carbon-accounting` differs; totals only over non-overlapping periods of one `target` and `carbon-accounting`, after unit conversion | 7.3, 9.2 |
| Mandatory members, and `capabilities` values `basic` and `extended` | 7.1 |
| `methodology-uri`, `disclosure-uri`, `verifiable-attestation-uri` are URI references resolved against the retrieval URI | 3.5, 10 |
| `updated`, `period.start`, `period.end` are `date-time` (upper-case `T`; `Z` or numeric offset; optional fraction); `period` is half-open, `start` before `end`; periods SHOULD be a day or longer | 3.2, 3.5, 7.1 |
| `measurement-method`: `hardware-metered`, `hardware-estimated`, `cloud-billing`, `third-party-modeled`; combined figures carry the least direct | 5.3, 7.1 |
| `target-type` `service` and `origin` (optional in the draft; 7.2 rule 4 requires it on a network declaration); a consumer compares each `target` with what it requested | 7.1, S4, S7 |
| `energy-unit` `Wh`, `kWh`, `MWh`, `GWh` (default `kWh` not relied on); `carbon-unit` `gCO2e`, `kgCO2e`, `tCO2e` (default `gCO2e` not relied on); `carbon-accounting` `location-based`, `market-based`; `energy-consumption`, `carbon-footprint` (gross), `scope-1`, `scope-2`, `scope-3`, `carbon-intensity-gCO2e-per-kWh`, `renewable-energy` | 7.3, 7.4 |
| `disclosure-uri`, `verifiable-attestation-uri` (at most one, signed by another party), `upstream`; at least one numeric metric or evidence URI per object | 7.2, 7.4, 8.4 |
| `extensions`: URI names compared as strings, never fetched; object values; unknown names ignored | 8.1 |
| `signed`: JWS Compact over the declaration without `signed`; `alg` asymmetric, `Ed25519` and `ES256` recommended, `none` and MAC forbidden; `cty` `sustainability-data+json`; the verifier compares payload `target`, `period.start`, `period.end`, `carbon-accounting`, `functional-unit` as strings; a consumer rejects `none`, MAC, absent or foreign `cty`, and an un-understood `crit`, and treats the object as unverified; key trust is out-of-band, pinned from an earlier retrieval, or an `x5c` chain to a trusted anchor with an end-entity certificate identifying the publisher; any other key is trusted no further than the declaration | 3.6, 7.2, S3 |
| Security Considerations: bound time, size and redirects; `https` only; refuse loopback, private and link-local addresses at every connection; limit bytes and objects (MUST) | 10 |
| No top-level members beyond the draft's; no version member | 1 |
| Strings equal after JSON escapes decode, no case folding; host `target` in A-label form, compared case-insensitively | 3.5, D2 |
| Numeric members not negative unless stated (`scope-1`, `scope-2`, `scope-3` MAY be negative); no number beyond binary64 range or precision (RFC 7493 section 2.2). 2.0 events and `operators` entries are not negative, except a figure read as is from a 1.x event | 3.3, 7.4 |
| Partial answers: figures for part of a period are not presented as the whole | 7.2, 7.5 |
| Optional perturbation within 1% (forbidden here by 7.2 rule 3) | 7.2 |

## Appendix E. Informative notes and history

### E.1 Platform notes

Naming a platform is not a qualification, and no note here is an energy assessment. Each deployment cites the assessment it relies on (C-SFC-6). Annual energy figures are not quoted; read the current estimate at the source. The platform names below are informative examples, never normative.

The six designs of the greentech catalogue, as currently planned:

| Design | Hot path | Attesting operators | Anchor |
|---|---|---|---|
| Certification Supply-Chain | Permissioned (Hyperledger Fabric) | Producers, certifier, neutral foundation | To be chosen |
| Healthcare Pharma | Permissioned (Hyperledger Fabric or Corda) | Hospitals, pharmacy chain, manufacturer, neutral foundation | To be chosen |
| Paperless Billing | Public (NEAR Protocol) | The gateway operators | Not needed (public hot path) |
| Recycling Chain | Permissioned (Hyperledger Fabric; Corda open alternative) | OEM consortium, neutral foundation, two recyclers | To be chosen |
| Roaming Data Exchange | Permissioned (Hyperledger Fabric) | Home and foreign operators, neutral foundation | To be chosen |
| Sustainability Climate Change | Permissioned (Hyperledger Fabric) | Registry operator, verifier, neutral foundation, buyer or auditor | To be chosen |

- Hyperledger Fabric and Corda: permissioned; energy bounded by node count times node power (the 4.4 bound). Fabric (Raft ordering) and Corda (Raft notary) name `mechanism` `crash-fault-tolerant`; a BFT-SMaRt notary names `bft`.
- NEAR Protocol: sharded proof of stake. Its climate-neutral label (2021) rests on purchased offsets and is not an energy measurement. MiCA sustainability-indicator disclosures of crypto-asset service providers carry annual figures; use the current disclosure and its boundary.
- Hedera: aBFT; its carbon-negative statement rests on purchased offsets. VeChainThor: proof of authority; footprint to be confirmed independently. Ethereum L1: proof of stake; compare the [CCRI](https://carbon-ratings.com) and [CCAF](https://ccaf.io/cbnsi) estimates with CAP on one boundary. Any proof-of-work chain is barred from the hot path (4.4); see CBECI.

### E.2 The anchor option

A deployment MAY publish periodic fingerprints (Merkle roots) of hot-path events on a public chain that is not proof-of-work. The methodology document then defines the construction (leaf encoding and hash, order, odd-node rule, UTC day boundary), the chain's finality and availability, and what happens if the chain stops. SFC 2 has no check or rule for it. Polygon zkEVM, used as an example anchor in 1.1, stopped producing blocks on 3 July 2026.

### E.3 History and pinned locations

Ledger profile 1.1: text dated 2026-05-23, deposited 2026-09-09, Zenodo 10.5281/zenodo.22681205. Ledger profile 1.2: 2026-10-03, Zenodo 10.5281/zenodo.23122082, greentech repository commit `edb7e71`. Disclosure profile 1.0 (2026-09-16): rfc-sustainability-wellknown commit `c787378`. Disclosure profile 1.1 (2026-10-03): commit `2d4822a`. Disclosure profile 1.1.1 (checker and examples on the -10 wire, 2026-10-25): `sfc-compliance/` at tag `v0.8.0-draft-10-schema-2.0`, first -10 text of `PROFILE.md` at commit `2e341e6`; "1.1.1" is this document's label, since the header of `PROFILE.md` reads "version 1.1" at both `2d4822a` (-07 wire) and `2e341e6` (-10 wire). `SFC.md`: commit `b6d1df0`. 1.x `README.md`: commit `4eb26cf`. Gateway ledger bridge (excerpt format 1): commit `50a8d4b`. SFC 2.0: Zenodo concept DOI 10.5281/zenodo.22681204; version DOI assigned at deposit. The 1.2 text called the column a Viewpoint; it is filed as an Opinion. The IET paper under review pins ledger profile 1.2 (`edb7e71`, Zenodo 10.5281/zenodo.23122082), disclosure profile 1.1 (`2d4822a`), gateway commit `50a8d4b` and draft -07; those pins stay valid and unchanged.

### E.4 What changed in 2.0

- One document and one version number replace two version lines. The wire is the draft -10 wire: `period` as a date-time pair, Ed25519 only, `tCO2e`.
- A defined Registry entry, one acceptance-rule list, one evaluation window, one grace period, one replay procedure (5.6).
- Retirements inside the signed attestation, single use of each tonne, no late credits; optional Scope 1; market-based Scope 2 in-band with an optional location-based object.
- A cut-off at `updated`; null heads for empty chains; a conjunction rule for the network flag; incomplete objects defined.
- Platform rule split into public and permissioned cases; anchor informative only.
- `carbon-intensity-gCO2e-per-kWh` now means the object's own market-based Scope 2 per kWh.
- A consumer that displays `net-zero-status` MUST show it beside the gross `carbon-footprint` (8.3); earlier texts said so without the keyword.
- A methodology parameters object (7.6); the checker's clock bounds a read's age (5.7); test vectors, schemas and a quick start.

