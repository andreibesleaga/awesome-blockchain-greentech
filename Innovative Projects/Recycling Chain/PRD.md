# RecyclingChain — Product Requirements Document (PRD)

> Minimal PRD. Companion to [README.md](README.md), [SPEC.md](SPEC.md), [ARCH.md](ARCH.md).

## 1. Problem

Today's recycling pipeline is opaque. A product placed in a bin disappears into a chain of handlers — collectors, sorters, MRFs, recyclers — with no verifiable record of what was actually recovered. The result is double-counting of recycled volumes, fraudulent green claims, missing EPR (Extended Producer Responsibility) data, and consumer mistrust.

## 2. Vision

A ledger-backed traceability system that captures every product's lifecycle from manufacture to material recovery as a chain of signed, append-only events — so regulators, brands, and consumers can verify "what was recycled, by whom, into what" without trusting any single party.

## 3. Users and Jobs-to-be-Done

| Persona | Job |
|---|---|
| Manufacturer (OEM) | Register items at birth and publish EPR-compliant composition data. |
| Distributor / Retailer | Record custody transfers; trigger deposit-return at point of sale. |
| Consumer | Scan a label to learn what to do with an item; return it for a deposit. |
| Collector / Logistics | Log pickups, weights, and photo-proof; claim collection bounties. |
| MRF Operator | Sort, weigh, split/merge batches; report contamination. |
| Recycler / Refiner | Lock items for decommission; publish yields and residues. |
| Auditor / Regulator | Verify attestations end-to-end and export compliance reports. |
| Brand (recycled-content buyer) | Buy and retire MaterialTokens to substantiate green claims. |

## 4. Goals (12-month horizon)

1. **G1 — Provable provenance.** Every registered item can be traced from `ManufactureRegistered` to a terminal event with a chain of signed receipts.
2. **G2 — Anti-double-counting.** A given item cannot be decommissioned more than once; recovered-material mass must reconcile within tolerance against accepted mass.
3. **G3 — Regulator-ready exports.** One-click export of EPR / EU Digital Product Passport (DPP) reports for any time window or batch.
4. **G4 — Consumer transparency.** Public verification portal returns an item's status and recycling outcome in < 2 s from a QR scan, anywhere.
5. **G5 — Pilot adoption.** Run a production pilot covering at least one item-level category (e.g., consumer electronics) and one batch-level commodity (e.g., PET bottles).

## 5. Non-Goals

* Building a generic supply-chain ledger for arbitrary goods.
* Replacing existing ERP or WMS systems used by participants.
* Operating the physical collection or recycling infrastructure.
* On-chain storage of PII or commercially sensitive bill-of-materials data.

## 6. Functional Requirements

* **FR-1 Registry.** Onboard participants with DIDs and Verifiable Credentials; assign roles (RBAC).
* **FR-2 Item Birth.** Mint `ItemToken` (NFT) or `BatchToken` (semi-fungible) with composition metadata; bind a signed QR/NFC label.
* **FR-3 Custody Transfer.** Append a signed `CustodyTransferred` event between two registered actors.
* **FR-4 Condition Report.** Append `ConditionReported` with weight, contamination, optional photo CID.
* **FR-5 Decommission Lock.** `DecommissionRequested` acquires an exclusive lock on an item via the `Lockbox`.
* **FR-6 Recycle Completion.** `RecycleCompleted` releases the lock and mints `MaterialToken` outputs proportional to declared yields.
* **FR-7 Retire Materials.** Brands burn `MaterialToken` units to back recycled-content claims.
* **FR-8 Public Verify.** A read API + portal that resolves an `itemId` to its full event chain, with cryptographic verification.
* **FR-9 Compliance Export.** Generate EPR / DPP reports as signed PDF + JSON for a given producer, period, or batch.
* **FR-10 Oracle Ingest.** Adapters for IoT scales and spectrometers that submit signed measurements as oracle attestations.

## 7. Non-Functional Requirements

* **NFR-1 Throughput.** Permissioned core sustains ≥ 500 events/sec, peak 2 000/sec.
* **NFR-2 Latency.** Public verify endpoint < 2 s end-to-end at p95.
* **NFR-3 Privacy.** No PII on-chain; consumer accounts are pseudonymous; off-chain stores are GDPR-compliant.
* **NFR-4 Availability.** 99.9 % monthly for the core ledger and verify API.
* **NFR-5 Integrity.** Every event is signed by the originating actor and verifiable against the Registry; daily Merkle anchor to a public L2.
* **NFR-6 Interoperability.** Event payloads map to GS1 EPCIS 2.0; identifiers expressible as URNs/DIDs.
* **NFR-7 Cost.** Per-event amortised cost ≤ $0.001 (batched + anchored).
* **NFR-8 Sustainability (SFC).** Network compliant with [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md): total measured energy < **1 GWh / yr**; no ASICs; monthly `EnergyAttested` + `CarbonAttested` events per operator; Net Zero per period via verified offsets; CSRD / ESRS E1 export on demand.

## 8. Success Metrics (KPIs)

| KPI | Target |
|---|---|
| Traceability coverage (registered → terminal) | ≥ 80 % within pilot scope |
| True recycling rate (valid `RecycleCompleted` / sold) | ≥ 60 % for pilot category |
| Median time-to-decommission | ≤ 90 days |
| Counterfeit / anomaly rate | ≤ 5 per 10 000 scans |
| Mass-balance reconciliation error | ≤ 2 % per MRF per month |
| Consumer verify-portal p95 latency | < 2 s |

## 9. Constraints and Assumptions

* Regulatory landscape: EU CSRD, EU Green Claims Directive, EU Digital Product Passport, regional EPR schemes — all moving targets, schema must be versioned.
* Pilot participants will run their existing ERP/WMS; integration is via REST/event adapters, not a rip-and-replace.
* Hardware (smart scales, NFC SE labels) is available off-the-shelf at acceptable BOM cost.
* Public-chain anchoring uses an EVM L2 with predictable fees.

## 10. Out-of-Scope (Phase 1)

* Tokenised carbon credits or offset markets.
* Reverse-logistics routing optimisation.
* In-store kiosk hardware design.
* Cross-jurisdiction legal harmonisation (we surface data; we don't arbitrate).

## 11. Milestones

| # | Milestone | Exit criteria |
|---|---|---|
| M1 | Spec & data model frozen | [SPEC.md](SPEC.md) v1.0 published and reviewed. |
| M2 | Core ledger + Registry live | FR-1…FR-3 on testnet; conformance tests green. |
| M3 | Lockbox + Material tokens | FR-4…FR-7 live; mass-balance checks enforced. |
| M4 | Public verify portal | FR-8 live; meets NFR-2. |
| M5 | Pilot launch | One OEM, one MRF, one recycler in production; KPIs reported weekly. |
| M6 | Compliance export GA | FR-9 produces signed EPR + DPP reports accepted by at least one regulator. |

## 12. Open Decisions

Tracked in [README.md § Open Decisions](README.md). Key items: network model (consortium vs. hybrid), unclaimed-deposit beneficiary, exact DPP schema version.
