# Sustainability Climate Change — Product Requirements Document (PRD)

> Minimal PRD. Scopes the catalogue in [README.md](README.md) down to **one** implementable subset: an MRV-anchored carbon-credit registry. Companion to [SPEC.md](SPEC.md), [ARCH.md](ARCH.md).

## 1. Problem

Voluntary carbon and biodiversity markets suffer from:

* opaque registries with manual reconciliation,
* "zombie credits" — credits retired in one registry but re-listed elsewhere via bridges,
* slow and expensive third-party audit,
* MRV data trapped in PDFs that are not machine-verifiable.

Buyers (corporates under CSRD / CBAM), regulators, and project developers all need a single tamper-evident view of *what was measured, by whom, with what methodology, and what was issued / retired against it*.

## 2. Vision

A **permissioned registry + MRV anchor** that:

* records every credit's full lineage (project → MRV evidence → issuance → transfers → retirement),
* binds each credit to a published methodology and its parameters,
* makes it impossible to retire a credit twice and detectable to bridge a retired credit,
* lets auditors and regulators read the full lineage on a signed event log.

The system **interoperates with** existing registries (Verra, Gold Standard, Puro, national registries via Hedera Guardian) — it does not replace them.

## 3. Users and Jobs-to-be-Done

| Persona | Job |
|---|---|
| Project Developer | Register a project, attach methodology, submit MRV data, get credits issued. |
| Validator / Verifier | Review MRV evidence and methodology fit; sign or reject issuance requests. |
| Registry Operator | Issue credits against approved validation; monitor lineage. |
| Corporate Buyer | Buy credits with auditable lineage; retire them against CSRD / CBAM reporting. |
| Regulator / Auditor | Audit issuance, transfers, retirements; check methodology compliance. |
| MRV Sensor / Data Provider | Submit signed measurements (weather stations, satellite-derived indices, in-situ sensors). |

## 4. Goals (12-month horizon)

1. **G1 — No double retirement.** A credit cannot be retired twice; bridge events to other chains require burn proof.
2. **G2 — Methodology binding.** Every issued credit carries the SHA-256 of the methodology version it was issued under.
3. **G3 — MRV anchored.** Every issuance references at least one MRV evidence CID with a verifier signature.
4. **G4 — Regulator-ready exports.** Signed CBAM / CSRD bundles for any buyer in < 60 s per period.
5. **G5 — Pilot adoption.** At least one project type (forestry or biochar) live in production with a Registry Operator, ≥ 3 corporate buyers and one auditor.

## 5. Non-Goals

* Inventing new MRV methodologies (we anchor; methodology bodies define).
* Operating physical sensors or remote-sensing platforms.
* Tokenising biodiversity as a tradable currency before integrity rules are settled.
* Replacing existing registries (Verra / Gold Standard / Puro).

## 6. Functional Requirements

* **FR-1 Project Registration.** Onboard a project with DID, geo footprint (geohash polygon), and a chosen methodology version.
* **FR-2 Methodology Anchor.** Register a methodology (PDF + parameters JSON) and pin its hash; methodology versions are immutable.
* **FR-3 MRV Submission.** Project submits signed measurements (sensor or remote-sensed) referencing project + period.
* **FR-4 Verifier Decision.** Accredited Verifier reviews evidence; emits a signed `Validated` or `Rejected` event with rationale.
* **FR-5 Issuance.** Upon `Validated`, registry mints credits with `(projectId, methodologyHash, vintage, quantity, mrvRefs)`.
* **FR-6 Transfer.** Credits transfer between Registry-onboarded holders; transfers are signed and logged.
* **FR-7 Retirement.** Holder burns credits with `(beneficiary, claimScope, reportYear)`; retirement is final.
* **FR-8 Bridge Lock.** Credits bridged to another chain must be burned locally; bridge contract holds the burn proof for two-way auditability.
* **FR-9 Audit Export.** Signed bundle for a project, buyer, or vintage — including methodology, MRV, issuance, lineage and retirement events.
* **FR-10 Recall.** A Verifier can flag an issuance as `Disputed`; under-investigation credits are non-transferable until resolved.

## 7. Non-Functional Requirements

* **NFR-1 Integrity.** No credit is issued without a Validator signature against a registered methodology.
* **NFR-2 Throughput.** ≥ 200 events/sec sustained; pilot volumes will be far below this.
* **NFR-3 Latency.** Public lineage-read endpoint < 1 s p95.
* **NFR-4 Privacy.** No PII on-chain; project documents can be encrypted off-chain.
* **NFR-5 Carbon footprint.** Run on a low-energy DLT (Hedera, Hyperledger Fabric, Polygon zkEVM). The carbon footprint of the system itself is published.
* **NFR-6 Standards.** Identifiers and event payloads align with **VCMI** / **ICVCM** integrity expectations and the **GHG Protocol Product Standard**; methodology hashes reference published Verra / Gold Standard / Puro documents where applicable.
* **NFR-7 Sustainability (SFC, self-applied).** Network compliant with [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md): total measured energy < **1 GWh / yr**; no ASICs; monthly `EnergyAttested` + `CarbonAttested` per Operator; Net Zero per period via offsets *retired through this very registry* where possible. Failure to self-comply breaks the trust premise of the system.

## 8. Success Metrics (KPIs)

| KPI | Target |
|---|---|
| Double-retirement attempts blocked | 100 % |
| % of issued credits with full MRV chain | 100 % |
| Median time from MRV submission → issuance | ≤ 30 days |
| Buyer audit-bundle generation p95 | < 60 s |
| Bridged-credit reconciliation error | 0 |

## 9. Constraints and Assumptions

* Recognised Verifiers exist and will adopt DIDs.
* Methodology bodies (Verra, Gold Standard, Puro) publish stable, versioned methodologies that can be hashed.
* The chosen DLT has carbon-footprint disclosure.
* Buyers' CSRD / CBAM reporting tooling can ingest signed JSON+PDF bundles.

## 10. Out-of-Scope (Phase 1)

* DeFi-style liquidity pools for credits.
* Insurance products against credit reversal.
* Cross-jurisdiction tax treatment of retirement claims.
* Direct trading of biodiversity credits (deferred until integrity rules are codified).

## 11. Milestones

| # | Milestone | Exit criteria |
|---|---|---|
| M1 | Spec frozen | [SPEC.md](SPEC.md) v1.0 reviewed. |
| M2 | Registry + Methodology + Projects | FR-1 / FR-2 live on testnet. |
| M3 | MRV + Validation | FR-3 / FR-4 live. |
| M4 | Issuance + Transfer + Retire | FR-5–FR-7 live; conformance tests pass. |
| M5 | Bridge lock | FR-8 live with at least one external chain. |
| M6 | Pilot live | One project type live with three buyers and one auditor for ≥ 60 days. |
| M7 | Audit / regulator export | FR-9 producing accepted bundles. |

## 12. Open Decisions

* DLT choice (Hedera vs. Hyperledger Fabric) — driven by ecosystem (Hedera Guardian) vs. consortium privacy needs.
* Methodology body partnerships at launch (Verra, Gold Standard, Puro — which to integrate first).
* Whether to anchor periodically to a public chain for external integrity verification.
* Treatment of biodiversity credits (defer vs. include as research-stage track).
