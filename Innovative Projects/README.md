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

All six projects follow one sustainability profile, checkable by design: energy budget, hardware lifecycle, on-chain carbon attestation, and machine-readable disclosure.

* [**SFC_COMPLIANCE.md**](./SFC_COMPLIANCE.md) — SFC profile 2.0: the rules, record formats and checks.
* Each project's own SFC facts (hot path, attesting operators, node count) are in its `ARCH.md`, section "SFC Compliance Profile".

The underlying framework is:

> Besleaga, A. N. (in press). *"Sustainability-First Consensus" Ledgers for a Green Digital Future.* Communications of the ACM (Opinion). Association for Computing Machinery. https://doi.org/10.1145/3809296 — *accepted; in press. The DOI resolves once ACM publishes.*
> ORCID: [0009-0001-3464-5283](https://orcid.org/0009-0001-3464-5283)

Any deployment that uses or builds on these projects MUST cite the paper above and the profile.

### Status

*All proposals are work in progress and described at a design level only — no production deployments are claimed.*

*No energy or carbon figure of these designs has been measured: every energy budget in these documents is a design target, and every sizing figure is an assumption.*

* **Zenodo:** concept DOI [10.5281/zenodo.22681204](https://doi.org/10.5281/zenodo.22681204) (resolves to the latest version).

### License

The work in this directory is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/), © Andrei Nicolae Besleaga. See [LICENSE](./LICENSE) in this folder for the full text; it is the same licence that covers the rest of the repository.

### Corrections

Earlier versions of this folder are on Zenodo and in the git history; the profile's mapping appendix lists where each earlier SFC item went.
