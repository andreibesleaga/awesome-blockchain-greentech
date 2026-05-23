# Paperless Billing — Product Requirements Document (PRD)

> Minimal PRD. Companion to [README.md](README.md), [SPEC.md](SPEC.md), [ARCH.md](ARCH.md).

## 1. Problem

Paper receipts and small-format invoices are a daily-life waste stream: ~300 billion paper receipts are produced globally each year (Green America, *Skip the Slip*), most thermal-paper is BPA/BPS-coated and not recyclable, and B2B paper invoices add reconciliation cost and fraud surface. Existing e-receipt apps are siloed per merchant or per payment processor — there is no shared verifiable receipt that a customer, a tax authority and an accounting system can all trust.

## 2. Vision

A **vendor-agnostic, ledger-anchored receipt**: the vendor's POS pins an encrypted bill payload to a content-addressed store and writes one tamper-evident anchor transaction. The customer reads the receipt through any compatible wallet. The tax authority audits through the on-chain event log. No new walled garden.

## 3. Users and Jobs-to-be-Done

| Persona | Job |
|---|---|
| Vendor (retailer, e-commerce, B2B seller) | Issue a receipt / invoice once, in a standard format, that the customer and the tax authority both accept. |
| Customer | Receive and keep receipts without paper, scoped to a single wallet they control. |
| Accountant / Bookkeeper | Pull verifiable invoices for the period, mapped to ledger accounts. |
| Tax / VAT Authority | Audit a vendor's issued receipts and totals over a period; check uniqueness; verify no after-the-fact rewriting. |
| Expense Auditor (employer) | Detect duplicate-claim attempts — the same receipt submitted by two employees. |

## 4. Goals (12-month horizon)

1. **G1 — Universal verify.** Any party with the bill CID and the on-chain anchor can verify integrity offline in < 100 ms.
2. **G2 — No paper.** Pilot deployments demonstrably replace ≥ 95 % of paper receipt issuance for participating SKUs.
3. **G3 — Tax-ready.** Generated invoices conform to **Peppol BIS 3.0 / EN 16931** for B2B; B2C receipts follow a published compact schema.
4. **G4 — Privacy.** Line-item data is never on-chain; default disclosure to the regulator is event-level (totals + tax), not item-level.
5. **G5 — Pilot adoption.** At least one mid-size retailer (multi-store POS) and one e-commerce platform in production.

## 5. Non-Goals

* Building a payment processor.
* Storing personally identifiable customer profiles on-chain.
* Replacing existing ERP / accounting software (we anchor; they reconcile).
* Becoming a global tax-clearance gateway (we generate compliant data; jurisdictions still gate clearance).

## 6. Functional Requirements

* **FR-1 Vendor onboarding.** Registry of vendors with a DID and a tax-id binding; per-vendor key rotation.
* **FR-2 Receipt issuance (B2C).** Vendor encrypts a JSON receipt, pins to IPFS, and writes one anchor tx `(billHash, cid, totals, vatBreakdown, customerDidOptional)`.
* **FR-3 Invoice issuance (B2B).** Same, but payload follows Peppol BIS 3.0 / EN 16931; counterparty DID is required.
* **FR-4 Customer linking.** A customer can attach a receipt to their wallet either at issuance (scan a code) or post-hoc (claim via a one-time link).
* **FR-5 Verify.** Public verify endpoint: given a CID and anchor tx, returns "valid / tampered / unknown".
* **FR-6 Vendor audit export.** Signed bundle for a vendor + period: list of `(billHash, totals, vatBreakdown, issuedAt)` — without line items unless line items were already public.
* **FR-7 Selective disclosure.** Customer or vendor can grant a regulator decryption access to one or more receipts via a Verifiable Credential.
* **FR-8 Duplicate detection.** Same `billHash` cannot be anchored twice; expense systems can detect the same `billHash` submitted by two employees.
* **FR-9 Revocation / void.** Vendor can publish a `BillVoided` event referring to a prior `BillIssued`; verify returns "voided" with a reason.
* **FR-10 Refunds.** A `BillRefunded` event links back to a `BillIssued` with the refund amount; mass-balance check totals refunds ≤ original.

## 7. Non-Functional Requirements

* **NFR-1 Anchor cost.** Per-receipt amortised on-chain cost < $0.001 (batched / on a low-fee chain).
* **NFR-2 Anchor latency.** Submit-to-finality < 5 s p95.
* **NFR-3 Verify latency.** < 100 ms p95 from cache, < 1 s p95 cold.
* **NFR-4 Privacy.** No PII on-chain; off-chain payloads encrypted with per-receipt CEKs.
* **NFR-5 Carbon.** Run on a published carbon-neutral chain (e.g., NEAR) or commit a measured / offset footprint elsewhere.
* **NFR-6 Standards.** B2B payloads conform to EN 16931 (UBL or CII syntax).
* **NFR-7 Availability.** 99.9 % monthly for the issuance and verify APIs.
* **NFR-8 Sustainability (SFC).** Network compliant with [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md): total measured energy (chain + gateways) < **1 GWh / yr**; no ASICs; monthly `EnergyAttested` + `CarbonAttested` per gateway operator; Net Zero per period via verified offsets; CSRD / ESRS E1 export on demand.

## 8. Success Metrics (KPIs)

| KPI | Target |
|---|---|
| % of receipts issued digitally in pilot scope | ≥ 95 % |
| % of B2B invoices passing Peppol BIS validation | 100 % |
| Detected duplicate-receipt fraud attempts blocked | 100 % |
| Verify p95 latency | < 100 ms (cached) |
| Customer wallet attach rate (B2C) | ≥ 60 % |

## 9. Constraints and Assumptions

* Vendors run existing POS / ERP and integrate via an adapter, not a rip-and-replace.
* Customers either hold a wallet (managed or self-custody) or accept a magic-link claim flow.
* The chosen chain offers predictable, low fees and either native account abstraction or wallet-friendly sponsorship.
* Tax authorities accept signed exports as compliant evidence (jurisdiction-specific validation expected).

## 10. Out-of-Scope (Phase 1)

* Coupons / loyalty programs (can be layered later on the same wallet).
* Cross-border tax determination engine.
* Real-time clearance with national e-invoicing systems (Italy SdI, Spain Veri*factu, etc.) — Phase 2 integration.

## 11. Milestones

| # | Milestone | Exit criteria |
|---|---|---|
| M1 | Spec frozen | [SPEC.md](SPEC.md) v1.0 reviewed. |
| M2 | Issuance + verify | FR-1, FR-2, FR-5 live on testnet. |
| M3 | B2B EN 16931 conformance | FR-3 live; sample bundle validates against Peppol BIS 3.0. |
| M4 | Customer wallet UX | FR-4 + magic-link claim flow live. |
| M5 | Pilot live | One retailer + one e-commerce vendor in production for ≥ 60 days. |
| M6 | Tax export & regulator pilot | FR-6 + FR-7 accepted by at least one tax authority sandbox. |

## 12. Open Decisions

* Chain choice (NEAR vs. an EVM L2) — driven by ecosystem reach and wallet UX.
* Default storage: IPFS pinning service vs. S3-compatible bucket with content addressing.
* Whether to anchor each receipt individually or batch N receipts per tx (cost vs. latency).
* National e-invoicing clearance: integrate per-country (Italy SdI, France Chorus Pro, Spain Veri*factu) vs. adapter-on-demand.
