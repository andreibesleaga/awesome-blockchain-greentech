## Innovative Projects

Work-in-progress system proposals addressing ecological challenges with Distributed Ledger Technology. Each project is described in terms of motivation, architecture, data flow, sustainability impact, and technically and ecologically suitable choices.

### Projects

* [**Certification Supply-Chain**](./Certification%20Supply-Chain/README.md) — Blockchain-based supply-chain certification using laser marking and tokenisation.
* [**Healthcare Pharma**](./Healthcare%20Pharma/README.md) — Prescriptions, patient records and pharmacy interchange on a fingerprint-and-policy ledger.
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

* [**SFC_COMPLIANCE.md**](./SFC_COMPLIANCE.md) — shared engineering profile (platforms, events, API, conformance checks).

The underlying framework is:

> Besleaga, A. N. (2026). *"Sustainability-First Consensus" Ledgers for a Green Digital Future.* Association for Computing Machinery. https://doi.org/10.1145/3809296
> ORCID: [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283)

Any deployment that uses or builds on these projects MUST cite the paper above.

### Status

*All proposals are work in progress and described at a design level only — no production deployments are claimed.*

### License

The work in this directory is licensed under a [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/), Andrei Nicolae Besleaga. See [LICENSE](./LICENSE) in this folder for the full text.

This differs from the [parent repository's license](../LICENSE), which covers the curated list itself.
