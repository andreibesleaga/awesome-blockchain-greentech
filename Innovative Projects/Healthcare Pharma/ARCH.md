# Healthcare Pharma — Architecture (ARCH)

> Minimal architecture overview. Companion to [README.md](README.md), [PRD.md](PRD.md), [SPEC.md](SPEC.md).

## 1. Architectural Style

A **fingerprint-and-policy ledger** that sits *alongside* existing EHR / pharmacy / supply-chain systems, not in front of them:

1. **Edge Layer** — patient DApps / wallets, clinician EHR integrations, pharmacy POS systems, manufacturer / distributor systems, IoT cold-chain sensors.
2. **Gateway / API Layer** — stateless services that authenticate DIDs, validate VCs, canonicalise and forward signed transactions.
3. **Permissioned Core Ledger** — authoritative for consent state, record hashes, access decisions, prescription / dispense state, and drug-unit serialisation events.
4. **Public Proof Layer (optional, hybrid)** — daily Merkle root of all events anchored to a public EVM L2 for external integrity verification.

PHI never touches the ledger. The ledger stores only **hashes, policy references, and signed access decisions**.

## 2. Component Diagram (logical)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                  EDGE LAYER                                  │
│  ┌────────────┐ ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌─────────┐ ┌────┐ │
│  │ Patient    │ │ Hospital │ │ Pharmacy   │ │ Mfr /    │ │ Cold-   │ │ERP │ │
│  │ DApp /     │ │ EHR      │ │ POS / WMS  │ │ Distrib  │ │ chain   │ │/WMS│ │
│  │ Wallet     │ │ Adapter  │ │            │ │ Systems  │ │ IoT     │ │    │ │
│  └─────┬──────┘ └────┬─────┘ └─────┬──────┘ └────┬─────┘ └────┬────┘ └─┬──┘ │
└────────┼─────────────┼─────────────┼─────────────┼────────────┼────────┼────┘
         │             │             │             │            │        │
         ▼             ▼             ▼             ▼            ▼        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            GATEWAY / API LAYER                               │
│  ┌────────────┐ ┌───────────────┐ ┌───────────────┐ ┌────────────────────┐  │
│  │ REST API   │ │ DID Auth /    │ │ FHIR Adapter  │ │ Oracle Adapter     │  │
│  │ (W/R)      │ │ VC Verifier   │ │ (off-chain    │ │ (sensor signatures)│  │
│  │            │ │               │ │ payload IO)   │ │                    │  │
│  └─────┬──────┘ └─────┬─────────┘ └───────┬───────┘ └─────────┬──────────┘  │
└────────┼──────────────┼───────────────────┼───────────────────┼─────────────┘
         │              │                   │                   │
         ▼              ▼                   ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PERMISSIONED CORE LEDGER                               │
│  ┌──────────┐ ┌─────────┐ ┌──────────────┐ ┌──────────────┐ ┌─────────────┐ │
│  │ Registry │ │ Consent │ │ AccessControl│ │ RecordAnchor │ │ EventLog    │ │
│  └──────────┘ └─────────┘ └──────────────┘ └──────────────┘ └─────────────┘ │
│  ┌──────────────┐ ┌──────────┐ ┌──────────┐                                 │
│  │ Prescription │ │ Dispense │ │ DrugUnit │                                 │
│  └──────────────┘ └──────────┘ └──────────┘                                 │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │  daily Merkle root
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PUBLIC PROOF LAYER  (EVM L2)                           │
│       ┌───────────────┐                          ┌─────────────────────┐    │
│       │ PublicAnchor  │                          │ Verifier libraries  │    │
│       └───────────────┘                          └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘

                              OFF-CHAIN STORAGE
        ┌────────────────────────────────────────────────────────────────┐
        │ Encrypted FHIR payloads, audit reports, sensor blobs, photos   │
        │ (S3-compatible store and/or IPFS; CEK-encrypted; deletable)    │
        └────────────────────────────────────────────────────────────────┘
```

## 3. Components (responsibilities)

| # | Component | Layer | Responsibility |
|---|---|---|---|
| C1 | Patient DApp / Wallet | Edge | Holds patient DID and consent VCs; presents VCs to grantees. |
| C2 | Hospital EHR Adapter | Edge | Encrypts FHIR resources; computes hashes; submits anchors. |
| C3 | Pharmacy POS | Edge | Verifies prescription validity; records dispense events. |
| C4 | Manufacturer / Distributor Systems | Edge | Mint and transfer DrugUnit tokens. |
| C5 | Cold-chain IoT | Edge | Capture temperature, location; sign in secure element. |
| C6 | API Gateway | Gateway | JWS validation; rate limiting; canonicalisation. |
| C7 | DID Auth / VC Verifier | Gateway | Resolves DIDs; verifies VC signatures, expiry, scope, revocation. |
| C8 | FHIR Adapter | Gateway | Bridges to/from FHIR R5 payloads in the off-chain store. |
| C9 | Oracle Adapter | Gateway | Verifies sensor signatures and tags events with provenance. |
| C10 | Registry | Core | DIDs, roles, key rotation, revocation. |
| C11 | Consent | Core | Tracks active consent VC hashes; on-chain revocation. |
| C12 | AccessControl | Core | Verifies VC presentation; emits signed access decisions. |
| C13 | RecordAnchor | Core | Stores `(hash, policy, cid)` per anchored record. |
| C14 | Prescription / Dispense | Core | Lifecycle of prescriptions; enforces refill limits and single-dispense atomicity. |
| C15 | DrugUnit | Core | NFT contract for serialised drug packs (GS1 SGTIN). |
| C16 | EventLog | Core | Append-only chain per subject; signature checks on append. |
| C17 | Anchor Job | Core → Public | Builds and commits daily Merkle root. |
| C18 | PublicAnchor | Public | Stores `(day, root)` tuples readable by anyone. |

## 4. Key Sequences

### 4.1 Anchor an EHR record

```
Clinician EHR ──▶ FHIR Adapter ──▶ encrypt(FHIR, CEK)
                       │                  │
                       │                  └──▶ store in off-chain bucket → CID
                       │
                       └──▶ API ──▶ RecordAnchor.write(hash, policyHash, cid)
                                              │
                                              └──▶ EventLog (RecordAnchored)
```

### 4.2 Access an EHR record (with patient consent)

```
Grantee (e.g., specialist) ──present(VC)──▶ AccessControl.verify(VC, hash)
                                              │
                                ├─ valid ──▶ EventLog (AccessGranted)
                                │               │
                                │               └──▶ off-chain bucket releases CEK
                                │                       │
                                │                       └──▶ grantee decrypts FHIR locally
                                │
                                └─ invalid ──▶ EventLog (AccessDenied)
```

### 4.3 Prescribe and dispense (no double-dispense)

```
Clinician ──sign──▶ Prescription.mint(rx)        ──▶ EventLog (PrescriptionMinted)

Pharmacy ──sign──▶ Dispense.execute(rxId, sgtins) ──▶ Prescription.acquire(rxId)
                                                       │
                                                       ├─ ok ──▶ EventLog (Dispensed)
                                                       │            │
                                                       │            └──▶ DrugUnit.transfer(sgtins, patient)
                                                       │
                                                       └─ already dispensed / no refills left ──▶ 409 Conflict
```

### 4.4 Daily public anchoring

```
00:10 UTC cron:
  events_prev_day = EventLog.range(00:00..23:59 previous day)
  root            = merkle(events_prev_day)
  PublicAnchor.commit(root, day) on EVM L2
```

## 5. Trust Boundaries

| Boundary | Trust assumption | Mitigation |
|---|---|---|
| Patient wallet ↔ Gateway | Patient may use a managed or self-custody wallet. | DID-based auth; wallet keys per user; recovery via custodian where chosen. |
| Edge institution ↔ Gateway | Institution keys held in HSM. | Strong key custody; on-chain revocation. |
| Gateway ↔ Core | Gateway is a thin verifier. | All authority is signature-based. |
| Core ↔ Public | Consortium nodes could collude. | Daily Merkle anchor + open conformance tests make tampering detectable. |
| Sensor ↔ Gateway | Sensor key may not be in a secure element. | TPM / SE preferred; otherwise trusted gateway signs and records the delegation. |
| Off-chain store ↔ Gateway | Bucket compromise risks PHI leak. | CEK encryption per record; KMS-managed wrapping keys; access policy. |

## 6. Data Storage

| Data | Where | Notes |
|---|---|---|
| FHIR payloads | Off-chain bucket (S3-compatible) | Encrypted; deletable; referenced by CID. |
| Record hashes, consent state, access decisions | Permissioned core | Authoritative. |
| Prescription / Dispense state | Permissioned core | Atomicity guaranteed by contract. |
| DrugUnit state, custody chain | Permissioned core | Materialised view for verify endpoint. |
| Daily Merkle roots | Public L2 | External integrity verification. |
| Consent VCs | Patient wallet + off-chain backup | Hash anchored in `Consent`. |
| Patient PII | Off-chain (institution systems) | NOT on-chain. |

## 7. Deployment View

* **Core nodes:** ≥ 5 operators across the consortium (multiple hospitals + pharmacy chain + manufacturer + neutral foundation). Raft / BFT consensus.
* **Gateway:** stateless containers behind a regional load balancer; horizontal autoscale.
* **Anchor Job:** singleton cron with leader election; idempotent.
* **HSMs:** institutional signing keys protected in HSMs (FIPS 140-2 Level 3 or equivalent).
* **Observability:** OpenTelemetry traces, Prometheus metrics, signed audit logs streamed to a regulator-accessible bucket.

## 8. Scalability and Performance

* Throughput targeted via batching of non-clinical events (supply-chain, condition reports).
* Reads served from materialised views in the gateway, not by replaying the chain.
* Latency-critical paths (access decision, prescription verify) sized to meet NFR-1 / NFR-3.
* ZK-proof generation for regulator exports done offline; only the proof and its public inputs cross the wire.

## 9. Security and Privacy

* TLS 1.3 ingress; mTLS gateway ↔ core.
* PHI never on-chain; payloads encrypted at rest (AES-256-GCM); CEKs wrapped per grantee (X25519 / ECIES).
* Right-to-be-forgotten: purge off-chain payload; on-chain hash and access log remain (integrity preserved, payload no longer resolvable).
* Patient consent is the only positive authorisation for non-emergency access; emergency "break-the-glass" access is allowed but is itself signed, logged and reviewable.

## 10. Failure Modes

| Failure | Effect | Recovery |
|---|---|---|
| Anchor job missed | No public root for a day. | Catch-up commit; verifiers tolerate gaps with `MissingDay` markers. |
| HSM unavailable | Institution cannot sign new events. | Failover HSM; pre-published `KeyRotated` VC pre-authorises a backup key. |
| Patient loses wallet | Cannot grant or revoke consent. | Custodian-assisted recovery (if managed wallet); social-recovery for self-custody. |
| Core node loss | Reduced fault tolerance window. | Add replacement node; resync. |
| Off-chain bucket region outage | Records temporarily unreadable. | Multi-region replication; verify endpoint returns `payload-unavailable` rather than fabricating data. |

## 11. Build / Tech Choices (indicative)

* **Permissioned core:** Hyperledger Fabric 2.x (Go chaincode) or R3 Corda 5 (Kotlin).
* **Public layer:** Polygon zkEVM or Arbitrum (Solidity 0.8.x).
* **API gateway:** Go (Echo) or Node.js (Fastify); JOSE for JWS; DID-core libs.
* **FHIR engine:** HAPI FHIR (Java) or fhir.js / Medplum on Node.
* **Storage:** PostgreSQL for materialised views; S3-compatible object store; KMS for CEK wrapping.
* **Observability:** OpenTelemetry + Prometheus + Loki.
* **CI/CD:** GitHub Actions; cosign-signed images.

## 12. Open Architecture Questions

* Fabric vs Corda for the permissioned core (both meet SFC §2 when run on general-purpose hardware).
* Whether to add a circuit-specific ZK toolchain (Circom / Noir) or rely on selective-disclosure JWT VCs for regulator exports.
* Per-country vs. supranational deployment (e.g., one EU-wide network vs. national networks anchored to one public root).
* Emergency-access (break-the-glass) policy formalisation.

## 13. SFC Compliance Profile

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Project pin: `sustainability-profile: SFC-PROFILE v1.1`.

| Criterion | How this project meets it |
|---|---|
| **1. Energy < 1 GWh / yr** | Hot path: Hyperledger Fabric (consortium BFT) on general-purpose servers (≤ ~15 peers + gateways across the consortium). Anchor: Polygon zkEVM. Combined measured budget well under the cap. |
| **2. Hardware lifecycle** | General-purpose x86 / arm64 only; HSMs (FIPS 140-2 L3) for institutional key custody — HSMs are general-purpose, not single-use ASICs. Every institution declares `nodeProfile`; WEEE-certified recycling at retirement. |
| **3. Carbon accountability** | Each institution publishes monthly `EnergyAttested` + `CarbonAttested` events. Scope 2 derived from peer + gateway + HSM electricity weighted by Electricity Maps regional intensity; Scope 3 from amortised embodied carbon of hardware. Offsets retired per period; Net Zero invariant enforced by verifier. |
| **4. Regulatory readiness** | `/v1/sustainability/csrd` returns signed ESRS E1 JSON. Hospital groups and pharma manufacturers are typically CSRD-in-scope undertakings — the disclosure block plugs directly into their corporate ESG tooling. |

**Measurement sources.** CCRI Sustainability API + Electricity Maps API + IEA emission factors (fallback). GHG Protocol Scopes 2 & 3 for boundary definition.

**Migration clause.** If the chosen platform's measured energy exceeds 1 GWh / yr in any 12-month window, the project migrates to another platform from [SFC_COMPLIANCE.md §2](../SFC_COMPLIANCE.md) within one reporting period.
