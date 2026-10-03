## Innovative Projects

Work-in-progress system proposals addressing ecological challenges with Distributed Ledger Technology. Each project is described in terms of motivation, architecture, data flow, sustainability impact, and technically and ecologically suitable choices.

### Projects

* [**Certification Supply-Chain**](./Certification%20Supply-Chain/README.md) — Blockchain-based supply-chain certification using laser marking and tokenisation.
* [**Healthcare Pharma**](./Healthcare%20Pharma/README.md) — Prescriptions, patient records and pharmacy interchange on a ledger.
* [**Paperless Billing**](./Paperless%20Billing/README.md) — Ledger-anchored digital receipts and B2B invoices.
* [**Recycling Chain**](./Recycling%20Chain/README.md) — End-to-end product traceability from manufacture to material recovery.
* [**Roaming Data Exchange**](./Roaming%20Data%20Exchange/README.md) — Cross-operator roaming for telecom and EV charging on a shared identity + settlement layer.
* [**Sustainability Climate Change**](./Sustainability%20Climate%20Change/README.md) — MRV-anchored carbon-credit registry and adjacent climate innovations.

### Per-project layout

Every project folder follows the same structure so a reader can pick any one and start from the same place:

* **README.md** — motivation, architecture overview, data flow, sustainability and policy alignment.
* **PRD.md** — problem, personas, functional / non-functional requirements, KPIs, milestones.
* **SPEC.md** — identifiers, token schemas, event envelope, REST API, smart contracts, conformance tests.
* **ARCH.md** — components, sequences, trust boundaries, deployment, failure modes.

### Sustainability-First Consensus (SFC) alignment

All six projects share a single sustainability profile applied as a verifiable engineering property — energy budget, hardware lifecycle, on-chain carbon attestation, and CSRD / ESRS-E1 disclosure:

* [**SFC_COMPLIANCE.md**](./SFC_COMPLIANCE.md) — shared engineering profile (platforms, events, disclosure, conformance checks).

The underlying framework is:

> Besleaga, A. N. (in press). *"Sustainability-First Consensus" Ledgers for a Green Digital Future.* Communications of the ACM (Viewpoint). Association for Computing Machinery. https://doi.org/10.1145/3809296 — *accepted; in press. The DOI resolves once ACM publishes.*
> ORCID: [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283)

Any deployment that uses or builds on these projects MUST cite the paper above.

### Status

*All proposals are work in progress and described at a design level only — no production deployments are claimed.*

*No energy or carbon figure of these designs has been measured: every energy budget in these documents is a design target, and every sizing figure is an assumption.*

* **Repository text:** v1.2 (2026-10-03); Zenodo deposit v1.2: <v1.2 DOI — reserved at upload> (v1.1: [10.5281/zenodo.22681205](https://doi.org/10.5281/zenodo.22681205), 2026-09-09, not changed); see [Corrections](#corrections-2026-10-03) below.

### License

The work in this directory is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/), © Andrei Nicolae Besleaga. See [LICENSE](./LICENSE) in this folder for the full text; it is the same licence that covers the rest of the repository.

### Corrections (2026-10-03)

This text (v1.2) differs from the Zenodo deposit v1.1 ([10.5281/zenodo.22681205](https://doi.org/10.5281/zenodo.22681205), 2026-09-09), which is not changed. What was corrected, and why:

* **"Measured" energy.** In several places v1.1 said that network energy was "measured" or "well under the cap". Nothing has been measured; none of the six designs has been built. Those passages now say that the 1 GWh / yr budget is a design target and that sizing figures are assumptions (all six projects, PRD / README / ARCH).
* **Paperless Billing receipt figures.** The global "over 300 billion receipts" and the US "10 billion receipts" figures are not in the cited Green America *Skip the Slip* report (2022). Removed; the report's US figures for trees and water are kept.
* **NEAR.** The NEAR Foundation link was dead (404). It is replaced by South Pole's own announcement (8 June 2021), and the label is described as offset-based. The claim that NEAR was the "first" Layer-1 with the label is removed. The Paperless Billing documents no longer say that chain-tier energy is reported through a NEAR Foundation certification: the only NEAR label found is South Pole's offset-based product label, which is not an energy measurement, so the chain-tier figure is taken from a cited public assessment (C-SFC-6).
* **Hedera.** "Carbon-negative" is a statement by the vendor, reached through purchased offsets. It is now attributed and linked.
* **Proof-of-work and Electricity Maps figures.** The CBECI range (100–170 TWh / yr) and the Electricity Maps zone count (160+) were out of date. Both numbers are removed; the sources are still linked.
* **CSRD.** Directive (EU) 2026/470 (in force 18 March 2026) narrowed who must report. The statements that hospital, pharma, telecom, charge-point and retail groups are typically in scope are replaced by statements that hold after the amendment, with the EUR-Lex source.
* **Unnamed benchmarks.** Fabric throughput statements now cite Androulaki et al., EuroSys 2018.
* **Cross-reference.** The Recycling Chain README pointed to §4 of the profile for the attestation events; they are in §3.
* **SFC profile.** [SFC_COMPLIANCE.md](./SFC_COMPLIANCE.md) is now v1.2 (2026-10-03): the bespoke disclosure API is retired in favour of the `sustainability-data` well-known URI, and the evidence-to-disclosure bridge is defined through the `ledger-evidence` extension of the SFC disclosure profile 1.1. See its change log. The project documents pin profile v1.2; their criterion-4 text names the signed declaration at `/.well-known/sustainability-data`, and their SPEC files point to the profile's mapping table of the retired endpoints (§8).
* **Citation.** The framework paper is cited as accepted, in press, without a year.
* **Polygon zkEVM.** Five designs pin Polygon zkEVM as the anchor for daily fingerprints. Its sequencer was shut down and the network stopped producing blocks on 3 July 2026 ([Polygon](https://polygon.technology/polygon-zkevm)). The anchor is now chosen per deployment: any public chain that is not proof-of-work, with its finality and availability stated (profile v1.2 §2.2). The design documents keep the v1.1 pin and carry a note.
* **"Net Zero".** The project documents say "Net Zero" for the rule `scope2 + scope3 ≤ offsets`. That is the framework's term; in GHG Protocol and Science Based Targets initiative terms the rule is an **offset-coverage** test, not net zero, and no consumer-facing neutrality claim is made (Directive (EU) 2024/825). Profile v1.2 calls it the offset-coverage rule; the field name `netZero` is kept.
* **Scope 2 and Scope 3.** Scope 2 is reported location-based and market-based where contractual instruments exist, and renewables count only through the market-based figure. Where the documents say Scope 3 "amortised embodied carbon", that is the Software Carbon Intensity (ISO/IEC 21031:2024) approach, a stated deviation from the GHG Protocol's guidance to count capital goods in the year of acquisition. Credits are retired in whole tonnes and may be allocated to months.
* **Platform qualification** (added 2026-10-03). The migration clauses said "measured energy"; they now say "assessed energy" on the C1 boundary (MiCA field S.8). Paperless Billing notes that the only published annual figure found for NEAR (0.92 GWh, Crypto Risk Metrics data in a MiCA disclosure for July 2025 – July 2026) is close to the cap, and no longer names Algorand as a migration target, because its current estimate on the MiCA boundary is slightly above 1 GWh. The Recycling Chain SPEC no longer calls the self-reported annual energy "measured". The curated list's "Low-Energy Base Layers" heading no longer says that every entry fits the budget.
* **Cross-references.** The Recycling Chain ARCH pointed to §3 of the profile for the measurement sources (they are in §6); the SPEC files pointed to §4–§5 for the field schemas, which start in §3. In v1.2 the C1 boundary is in §2.1; the migration clauses point there.
* **Recycling Chain sizing.** The ARCH sizing note said "≤ 12 peers → ≤ ~15 MWh / yr" at an assumed ~150 W per peer; 12 × 150 W × 8,760 h = 15.77 MWh, so it now says ≤ ~15.8 MWh / yr (still a sizing assumption, not a measurement).
* **OpenTimestamps.** The Certification Supply-Chain ARCH lists an OpenTimestamps proof of the daily fingerprint as an open question. OpenTimestamps commits to Bitcoin, a proof-of-work chain, so it is not an allowed anchor under profile v1.2 §2.2; a note now says so, and the anchor follows the chain-agnostic rule.
* **Curated list** (top-level [README](../README.md)): the same NEAR, Hedera and Electricity Maps corrections; Algorand's unsourced energy figure and "carbon-negative" label are replaced by what its own sustainability page states (read 2026-10-03); Plastic Bank's "first" is attributed to Plastic Bank. IOTA's unsourced per-transaction energy figure is removed; the Polygon entry notes the zkEVM shutdown.
