# Healthcare Pharma — Product Requirements Document (PRD)

> Minimal PRD. Companion to [README.md](README.md), [SPEC.md](SPEC.md), [ARCH.md](ARCH.md).

## 1. Problem

Healthcare data lives in fragmented silos (hospital EHRs, lab systems, pharmacy networks, regional registries). Patients cannot meaningfully consent to or audit how their records flow. Prescriptions are easy to forge or double-dispense, and the pharmaceutical supply chain still suffers from counterfeit and diversion incidents despite serialisation mandates (DSCSA in the US, EU FMD in the EU).

## 2. Vision

A ledger-anchored **access-control and integrity layer** that sits beside existing EHR / pharmacy / supply-chain systems. The ledger never stores Protected Health Information (PHI) — it stores **hashes of encrypted records, signed access decisions, and serialised drug-unit events**. Patients hold consent through Verifiable Credentials; regulators verify integrity without seeing raw clinical data.

## 3. Users and Jobs-to-be-Done

| Persona | Job |
|---|---|
| Patient | Hold and present consent VCs; see who accessed what and when. |
| Clinician / Hospital | Issue prescriptions, write EHR entries, request access to records held by others. |
| Pharmacist | Validate prescriptions against the ledger; record dispense events to prevent double-dispensing. |
| Pharma Manufacturer | Mint serialised drug units; record cold-chain and custody events. |
| Distributor / 3PL | Record handoff events with custody and temperature data. |
| Regulator (FDA / EMA / national) | Verify integrity and compliance via signed exports and ZK-proofs without seeing PHI. |
| Auditor | Replay the signed access log and reconcile dispenses to prescriptions. |

## 4. Goals (12-month horizon)

1. **G1 — Verifiable consent.** Every access to a PHI record is authorised by a valid, on-ledger consent VC or by an explicit emergency-access event that is later reviewable.
2. **G2 — Zero double-dispensing.** A given prescription can be dispensed at most once (or up to its declared refill count); attempted re-dispense is rejected at the ledger.
3. **G3 — End-to-end drug serialisation.** Every regulated drug unit in scope has a continuous, signed event chain from manufacturer to final dispense, aligned with DSCSA / EU FMD.
4. **G4 — Privacy-preserving compliance.** Regulators can verify selected facts (e.g., "all controlled-substance dispenses in period P were authorised") via ZK-proofs without accessing PHI.
5. **G5 — Pilot adoption.** At least one hospital, one pharmacy chain, and one manufacturer integrated in production for a single therapeutic area.

## 5. Non-Goals

* Becoming a primary EHR system or replacing existing ones.
* Storing PHI on the ledger.
* Acting as the legal trust anchor for any clinical decision.
* Issuing prescriptions or clinical diagnoses.

## 6. Functional Requirements

* **FR-1 Identity & Roles.** Onboard patients, clinicians, pharmacies, manufacturers, distributors and regulators with DIDs and role VCs.
* **FR-2 Consent.** Patient issues a consent VC scoped to (`recipient`, `dataCategory`, `purpose`, `notAfter`). Revocation is on-ledger and immediate.
* **FR-3 Record Anchor.** Hospital encrypts a record (FHIR resource), stores it off-chain, and anchors its SHA-256 hash on the ledger together with policy metadata.
* **FR-4 Access Request & Decision.** A requester presents the consent VC; the access-control contract verifies it and emits a signed `AccessGranted` (or `AccessDenied`) event.
* **FR-5 Prescription.** Clinician mints a `Prescription` token bound to the patient DID and the drug code; the contract enforces refill limits.
* **FR-6 Dispense.** Pharmacy submits a `Dispensed` event referencing the Prescription; the contract rejects exceeded refill counts and double-dispense attempts within atomicity windows.
* **FR-7 Drug-Unit Serialisation.** Manufacturer mints a `DrugUnit` token per serialised pack (GS1 SGTIN); custody transfers and cold-chain events are signed and appended.
* **FR-8 Verify API.** Public read endpoint for participants to verify the validity of a prescription, the genuineness of a drug unit (DSCSA / FMD lookup), and the integrity of a record hash.
* **FR-9 Audit / Regulator Export.** Signed bundles answering specific compliance questions over time windows; ZK-proofs where the underlying data is sensitive.
* **FR-10 Right-to-be-Forgotten.** Patient-initiated purge of off-chain payloads; on-chain references degrade to opaque hashes preserved for integrity but no longer resolvable to data.

## 7. Non-Functional Requirements

* **NFR-1 Latency.** Access decision and prescription-verify endpoints < 500 ms p95.
* **NFR-2 Throughput.** Permissioned core sustains ≥ 1 000 events/sec under benchmark load; production targets revisited per environment.
* **NFR-3 Availability.** 99.95 % monthly for the access-control and verify APIs (critical-care dependency).
* **NFR-4 Privacy.** No PHI on-chain; off-chain payloads encrypted at rest; deletable.
* **NFR-5 Standards.** EHR payloads conform to HL7 FHIR R5; drug identifiers follow GS1 SGTIN / GTIN; DIDs and VCs follow W3C specs.
* **NFR-6 Cryptography.** Signatures Ed25519 or ECDSA-P256 (HSM-backed for institutional keys).
* **NFR-7 Auditability.** 100 % of accesses, dispenses and supply-chain events are signed and replayable.
* **NFR-8 Sustainability (SFC).** Network compliant with [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md): total measured energy < **1 GWh / yr**; no ASICs; monthly `EnergyAttested` + `CarbonAttested` per operator; Net Zero per period via verified offsets; CSRD / ESRS E1 export on demand.

## 8. Success Metrics (KPIs)

| KPI | Target |
|---|---|
| Unauthorised access incidents | 0 (any incident triggers post-mortem) |
| Detected double-dispense attempts blocked / attempted | 100 % blocked |
| Consent-revocation propagation time | < 5 s |
| Serialised drug-unit chain completeness | ≥ 99 % in pilot scope |
| Access-decision p95 latency | < 500 ms |

## 9. Constraints and Assumptions

* Participants run existing EHR / pharmacy systems; integration is via standards-based adapters (FHIR, GS1), not rip-and-replace.
* Institutional keys live in HSMs or equivalent; patient keys live in a managed wallet by default (with self-custody option).
* Regulators will accept signed exports / ZK-proofs as evidence (subject to formal validation per jurisdiction).
* Off-chain stores are GDPR/HIPAA-compliant; ledger remains a fingerprint and policy layer.

## 10. Out-of-Scope (Phase 1)

* Insurance claim adjudication and pricing logic.
* Clinical decision support algorithms.
* Genomic / large-binary record storage (referenced only by CID).
* Cross-border patient identity harmonisation.

## 11. Milestones

| # | Milestone | Exit criteria |
|---|---|---|
| M1 | Spec & data model frozen | [SPEC.md](SPEC.md) v1.0 reviewed and signed off. |
| M2 | Registry + consent | FR-1 / FR-2 / FR-4 live on testnet. |
| M3 | Record anchor + access log | FR-3 live; audit replay reproduces full access history. |
| M4 | Prescription & dispense | FR-5 / FR-6 live; conformance tests for double-dispense pass. |
| M5 | Drug-unit serialisation | FR-7 live; DSCSA / EU FMD integration tested against a sandbox. |
| M6 | Pilot in production | One hospital, one pharmacy chain, one manufacturer live for ≥ 90 days. |
| M7 | Regulator export | FR-9 producing accepted bundles for at least one regulator. |

## 12. Open Decisions

* **Permissioned core choice:** Hyperledger Fabric vs. R3 Corda (governance vs. confidentiality trade-off).
* **Patient key custody model:** managed wallet by default vs. self-custody by default.
* **Emergency access (break-the-glass):** policy boundaries and after-the-fact review process.
* **Regional vs. global deployment:** per-country shards anchored to a single public root vs. fully federated networks.
