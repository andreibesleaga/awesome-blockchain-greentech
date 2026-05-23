# Roaming Data Exchange — Product Requirements Document (PRD)

> Minimal PRD. Companion to [README.md](README.md), [SPEC.md](SPEC.md), [ARCH.md](ARCH.md).

## 1. Problem

Cross-operator service consumption — a mobile subscriber roaming abroad, an EV driver charging on a foreign network, a utility customer drawing from another grid balance — relies on bilateral or hub-based agreements with slow reconciliation (days to months in telecom, batched files in EV charging via OCPI hubs). The result: high disputes, multi-week settlement, fraud surfaces (sim-box, charger-spoofing, station-side abuse), and significant duplicate-onboarding cost.

## 2. Vision

A **shared identity and settlement layer** that operates alongside existing standards — **OCPI / OCPP** in EV, **GSMA wholesale roaming** in telecom — and provides:

* one cryptographic identity per user (DID + Verifiable Credentials),
* near-real-time inter-operator settlement against pre-posted bonds,
* a single tamper-evident event log auditable by both operators and regulators.

We do not replace OCPI or GSMA processes. We augment them so existing operators get faster settlement and lower fraud without re-platforming.

## 3. Users and Jobs-to-be-Done

| Persona | Job |
|---|---|
| End user (driver / subscriber) | Use a service abroad without paperwork, get a single bill from their Home Operator. |
| Home Operator | Vouch for the user with minimum data exposure, settle quickly with Foreign Operators. |
| Foreign Operator (CPO / VPMN) | Authorise the user in ≤ 2 s, get paid in minutes-to-hours, not weeks. |
| Roaming Hub (OCPI / GSMA) | Consume signed session records and shorten reconciliation. |
| Regulator | Audit pricing, fair-use compliance, and (in EV) renewable-energy provenance. |
| Auditor | Replay settlement to reconcile per-operator dues. |

## 4. Goals (12-month horizon)

1. **G1 — Sub-2 s authorisation.** End-to-end "show credential → access granted" in ≤ 2 s p95.
2. **G2 — Settlement within hours.** Inter-operator micro-settlements (after dispute window) within ≤ 6 h p95, vs. industry's days-to-months baseline.
3. **G3 — Zero new identity stores at the Foreign Operator.** Foreign Operators authorise off a DID + VC presentation, with no new account creation.
4. **G4 — OCPI / GSMA conformance.** Sessions flowing through the system also produce a valid OCPI `CDR` (Charge Detail Record) or GSMA-compliant settlement file.
5. **G5 — Pilot adoption.** One telecom pair (2 MNOs across two countries) and one EV pair (2 CPOs across two countries) in production.

## 5. Non-Goals

* Replacing OCPI, OCPP or GSMA processes.
* Building a payment processor.
* Operating physical infrastructure (RAN, charge points, meters).
* Tokenising user identity for transferable resale.

## 6. Functional Requirements

* **FR-1 Onboarding.** Operators onboard with a DID + role VC; users receive a wallet (managed or self-custody) and a Home Operator VC.
* **FR-2 ZK credential presentation.** Wallet generates a selective-disclosure proof for `(home-op valid, plan tier, credit-ok)` without revealing identity.
* **FR-3 Authorisation.** Foreign Operator verifies the proof against the Roaming Gateway and gets a yes/no with a session id and a max-cost cap.
* **FR-4 Bond reservation.** Home Operator's contract reserves funds against a pre-posted bond for the session's max-cost cap.
* **FR-5 Session record.** Foreign Operator submits a signed session record at end (or periodically for long sessions); contract releases bond and emits a `SettlementProposed` event.
* **FR-6 Dispute window.** Configurable per-operator-pair (e.g., 1 h for EV, 6 h for telecom) before final settlement.
* **FR-7 OCPI / GSMA export.** Produce a conforming `CDR` (OCPI) or GSMA settlement file from the on-chain session record.
* **FR-8 Reputation / fraud.** Anomaly detector flags impossible-velocity sessions, station-side abuse, and sim-box-style patterns.
* **FR-9 Revocation.** Home Operator can revoke a user VC; Foreign Operator's wallet integration honours revocation within ≤ 5 s.
* **FR-10 ESG tagging (EV).** Where a Guarantee-of-Origin or equivalent attestation exists, the session record carries the renewable-energy claim hash.

## 7. Non-Functional Requirements

* **NFR-1 Authorisation latency.** ≤ 2 s p95 for credential presentation → access granted.
* **NFR-2 Settlement latency.** ≤ 6 h p95 from session end to settled (after dispute window).
* **NFR-3 Throughput.** ≥ 500 sessions/sec authorised across the network at peak; raise per-deployment.
* **NFR-4 Availability.** 99.95 % monthly for the authorisation and settlement APIs.
* **NFR-5 Privacy.** No PII on-chain; selective disclosure via ZKP for service authorisation.
* **NFR-6 Standards.** Identity follows W3C DID / VC; EV session records map cleanly to OCPI 2.2+ CDRs; telecom records map to current GSMA / BCE formats.
* **NFR-7 Sustainability (SFC).** Network compliant with [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md): total measured energy < **1 GWh / yr**; no ASICs; monthly `EnergyAttested` + `CarbonAttested` per Operator; Net Zero per period via verified offsets; CSRD / ESRS E1 export on demand. Hot-path platform from SFC §2 (Fabric / Hedera / NEAR-class).

## 8. Success Metrics (KPIs)

| KPI | Target |
|---|---|
| p95 authorisation latency | < 2 s |
| p95 settlement latency | < 6 h |
| % sessions with valid OCPI CDR / GSMA export | 100 % |
| Settlement dispute rate | < 0.5 % of sessions |
| Detected fraud attempts blocked | 100 % of well-formed anomaly patterns |

## 9. Constraints and Assumptions

* Operators run existing OSS/BSS or CPO software; integration is via adapters.
* Wallets are either operator-managed (default) or self-custody (advanced users).
* Pre-posted bonds are economically reasonable for the volume served.
* Regulators accept signed session bundles for audit (jurisdiction-specific).

## 10. Out-of-Scope (Phase 1)

* Consumer-facing billing UX (we surface the data; operators bill).
* Tokenised tradable mobility credits.
* Cross-jurisdiction tax / currency settlement (handled by treasury, not us).
* Authentication for non-operator parties (e.g., embedded SIMs in IoT) — Phase 2.

## 11. Milestones

| # | Milestone | Exit criteria |
|---|---|---|
| M1 | Spec frozen | [SPEC.md](SPEC.md) v1.0 reviewed. |
| M2 | Registry + DID/VC issuance | FR-1 / FR-2 live on testnet. |
| M3 | Authorisation contract | FR-3 / FR-4 live, NFR-1 met. |
| M4 | Settlement + dispute | FR-5 / FR-6 live, NFR-2 met. |
| M5 | OCPI / GSMA export | FR-7 producing conforming files. |
| M6 | Pilot live | One telecom and one EV pair in production for ≥ 60 days. |

## 12. Open Decisions

* Whether to issue the user VC as a JWT-VC or a JSON-LD VC (toolchain trade-off).
* Bond size / replenishment policy per operator pair.
* Cross-chain need: real cross-chain (IBC / CCIP) vs. one consortium ledger with adapters.
* Whether the gateway runs as a public consortium service or per-region.
