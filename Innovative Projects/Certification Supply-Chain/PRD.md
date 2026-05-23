# Certification Supply-Chain — Product Requirements Document (PRD)

> Minimal PRD. Companion to [README.md](README.md), [SPEC.md](SPEC.md), [ARCH.md](ARCH.md).

## 1. Problem

Sustainability and fair-trade certifications today rely on paper certificates, peel-off labels, and PDF audit reports. Any of these can be forged, swapped, or back-dated, and there is no shared cryptographic ground truth across producers, certifiers, logistics, retailers and consumers. The result is greenwashing and weak regulator trust just as the EU CSRD and CBAM are pushing for verifiable product-level data.

## 2. Vision

Bind every certified item or batch to an **indelible physical mark** (laser-engraved UID) and to a **token** on a shared ledger. Every supply-chain event is a signed transaction; every certification is a signed credential; every consumer scan returns a verifiable history.

## 3. Users and Jobs-to-be-Done

| Persona | Job |
|---|---|
| Producer / Manufacturer | Mark items, mint tokens, attach certifications and origin metadata. |
| Certifier (organic, fair-trade, …) | Issue Verifiable Credentials bound to a producer DID and a scope (batch, period). |
| Logistics / Carrier | Submit signed scan + condition events at handoff points. |
| Distributor / Retailer | Verify provenance on receipt; record sale events; optionally trigger consumer rewards. |
| Consumer | Scan UID and see provenance + certifications without an account. |
| Regulator | Pull signed exports for CSRD / CBAM / EUDR reporting. |
| Auditor | Run conformance checks across an entire producer's chain in one query. |

## 4. Goals (12-month horizon)

1. **G1 — Verifiable claims.** Every active certification on the ledger is backed by a signed Verifiable Credential from a Registry-recognised certifier.
2. **G2 — Tamper-evident handoffs.** Every custody change carries a signed event from both sender and receiver, or a single signed event with explicit hand-receipt semantics.
3. **G3 — Per-batch carbon.** The system can output a GHG-Protocol-aligned carbon footprint per ItemToken / BatchToken from the recorded transport and storage events.
4. **G4 — Sub-second consumer verify.** Public scan-to-result latency < 1 s at p95.
5. **G5 — Pilot adoption.** At least one hard-goods category (e.g., leather, machined parts) and one batch-marked produce category in production with three independent participants.

## 5. Non-Goals

* Issuing certifications ourselves (we record and verify them; we do not certify).
* Acting as the legal trust anchor for any specific national certification scheme.
* On-chain storage of business-sensitive pricing or PII.
* Replacing existing ERP / WMS systems.

## 6. Functional Requirements

* **FR-1 Marking.** Engrave a UID and a short signed payload onto product or packaging via Direct Part Marking; bind the UID to a token at mint time.
* **FR-2 Tokenisation.** Mint `ItemToken` (per-item) or `BatchToken` (per-lot) with origin, composition and EPR-relevant metadata.
* **FR-3 Certification Attach.** A certifier issues a Verifiable Credential referencing one or more tokens; the VC's hash is anchored on-chain.
* **FR-4 Custody Events.** Record `CustodyTransferred`, `ConditionReported`, `Inspected`, `Sold` events signed by the relevant actor.
* **FR-5 Oracle Ingest.** Accept signed measurements from registered sensors / gateways; reject those whose key is not in the Registry or whose certificate is revoked.
* **FR-6 Verify API.** Public read endpoint: given a UID, return current state + ordered event chain + signature-verification result.
* **FR-7 Carbon Export.** Generate per-token or per-batch carbon footprint reports aligned with the GHG Protocol Product Standard.
* **FR-8 Compliance Export.** Signed CSRD / CBAM / EUDR data bundles per producer and period.
* **FR-9 Anomaly Detection.** Off-chain workers flag duplicate scans, impossible-velocity moves, geofence violations and mass-balance breaches.

## 7. Non-Functional Requirements

* **NFR-1 Throughput.** ≥ 200 events/sec sustained on the chosen network with batching.
* **NFR-2 Latency.** Public verify endpoint < 1 s p95.
* **NFR-3 Privacy.** No PII on-chain; selective disclosure of business-sensitive facts via ZKP where required.
* **NFR-4 Availability.** 99.9 % monthly for the verify API.
* **NFR-5 Interoperability.** Identifiers follow GS1 EPCIS 2.0 vocabulary; URIs follow GS1 Digital Link.
* **NFR-6 Sensor Trust.** Where supported, IoT readings are signed in a secure element (TPM / NFC SE / ATECC608A); otherwise a trusted gateway signs and the event records the delegation explicitly.
* **NFR-7 Sustainability (SFC).** Network compliant with [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md): total measured energy < **1 GWh / yr**; no ASICs; monthly `EnergyAttested` + `CarbonAttested` per operator; Net Zero per period via verified offsets; CSRD / ESRS E1 export on demand.

## 8. Success Metrics (KPIs)

| KPI | Target |
|---|---|
| % of items / batches with a complete signed chain from mint to terminal event | ≥ 90 % within pilot scope |
| % of certifications backed by a verifiable VC | 100 % |
| Verify-portal p95 latency | < 1 s |
| Detected scan / mass anomalies per 10 000 events | < 5 |
| Producer carbon-report generation time | < 60 s per producer per month |

## 9. Constraints and Assumptions

* Laser marking is feasible on the target substrate; for soft produce, only batch-level marking is in scope.
* IoT devices either ship with a secure element or are deployed behind a trusted gateway.
* Certifiers will adopt Verifiable Credentials with DIDs (a non-trivial change-management lift).
* The chosen public anchor chain has predictable fees.

## 10. Out-of-Scope (Phase 1)

* Tokenised carbon offsets or trading markets.
* Reverse-logistics or returns flows.
* Hardware design of laser-marking stations.
* Cross-jurisdiction legal harmonisation of certification meaning.

## 11. Milestones

| # | Milestone | Exit criteria |
|---|---|---|
| M1 | Spec & data model frozen | [SPEC.md](SPEC.md) v1.0 reviewed and signed off. |
| M2 | Registry + token contracts | FR-1 / FR-2 / FR-3 live on testnet; conformance tests green. |
| M3 | Oracle + event ingest | FR-4 / FR-5 / FR-9 live; latency NFR met. |
| M4 | Verify portal | FR-6 live and meeting NFR-2. |
| M5 | Compliance & carbon export | FR-7 / FR-8 producing regulator-accepted bundles. |
| M6 | Pilot in production | Three participants live across one hard-goods and one batch-marked category. |

## 12. Open Decisions

* **Public vs. consortium chain.** Public L2 (Polygon / Arbitrum / VeChainThor) maximises consumer trust; permissioned (Fabric) maximises throughput and confidentiality. A hybrid (consortium core + daily public anchor) keeps the option open.
* **ZKP scope.** Which facts warrant selective-disclosure proofs vs. plain VCs.
* **Reward economics.** Producer-bonus formulas for sustained low-anomaly performance.
