# Healthcare Pharma — Technical Specification (SPEC)

> Minimal technical spec. Companion to [README.md](README.md), [PRD.md](PRD.md), [ARCH.md](ARCH.md).

## 1. Identifiers

All identifiers MUST be resolvable through the Registry's DID resolver. Clinical payloads MUST follow HL7 FHIR R5; drug-unit identifiers MUST follow GS1 SGTIN.

| Entity | Format | Example |
|---|---|---|
| Patient | `did:hcx:patient:<key-fingerprint>` | `did:hcx:patient:z6Mkpat…` |
| Clinician | `did:hcx:clin:<key-fingerprint>` | `did:hcx:clin:z6Mkdoc…` |
| Institution (hospital, pharmacy, mfr) | `did:hcx:org:<key-fingerprint>` | `did:hcx:org:z6Mkrxchain…` |
| RecordHash | URN `urn:hcx:rec:<sha256>` | `urn:hcx:rec:9f86d0…` |
| Prescription | URN `urn:hcx:rx:<clinDid>:<serial>` | `urn:hcx:rx:z6Mkdoc…:2026-000182` |
| DrugUnit (SGTIN) | URN `urn:epc:id:sgtin:<companyPrefix>.<itemRef>.<serial>` | `urn:epc:id:sgtin:0614141.107346.0001` |
| Event | `<subject>#evt-<monotonic>` | `urn:hcx:rx:…#evt-3` |

## 2. Consent (W3C Verifiable Credential)

```jsonc
{
  "@context":     ["https://www.w3.org/2018/credentials/v1"],
  "type":         ["VerifiableCredential", "HealthDataConsent"],
  "id":           "urn:hcx:consent:c0ffee",
  "issuer":       "did:hcx:patient:z6Mkpat…",
  "issuanceDate": "2026-05-23T10:00:00Z",
  "expirationDate": "2026-08-23T10:00:00Z",
  "credentialSubject": {
    "id":         "did:hcx:org:z6Mkpharm…",   // grantee
    "dataCategory": ["Prescription", "Allergy", "Immunization"],
    "purpose":    "dispensing",
    "patient":    "did:hcx:patient:z6Mkpat…",
    "constraints": { "maxAccesses": 3, "maxAgeDays": 90 }
  },
  "proof": { "type": "Ed25519Signature2020", "verificationMethod": "did:hcx:patient:z6Mkpat…#k1", "proofValue": "…" }
}
```

The patient retains the VC; the grantee presents it to obtain access. The contract checks issuer signature, expiry, scope, and on-chain revocation status.

## 3. Token Types

### 3.1 Prescription (NFT-style, mint-once, dispense-limited)

```jsonc
{
  "id":          "urn:hcx:rx:z6Mkdoc…:2026-000182",
  "patient":     "did:hcx:patient:z6Mkpat…",
  "prescriber":  "did:hcx:clin:z6Mkdoc…",
  "drug":        { "code": "RxNorm:198440", "name": "Amoxicillin 500mg cap" },
  "qty":         21,
  "directions":  "1 cap PO TID x 7 days",
  "refills":     0,
  "dispensesUsed": 0,
  "validFrom":   "2026-05-23",
  "validUntil":  "2026-06-23",
  "status":      "open | dispensed | expired | cancelled"
}
```

### 3.2 DrugUnit (NFT, per serialised pack)

```jsonc
{
  "id":           "urn:epc:id:sgtin:0614141.107346.0001",
  "manufacturer": "did:hcx:org:z6Mkmfr…",
  "product":      { "gtin": "00614141107346", "lot": "LX-2026-04", "expiry": "2028-03" },
  "currentCustodian": "did:hcx:org:z6Mkdist…",
  "lifecycleStage":   "minted | shipped | received | dispensed | recalled"
}
```

## 4. Event Schema

Signed envelope used by every event:

```jsonc
{
  "type":     "RecordAnchored | AccessRequested | AccessGranted | AccessDenied | ConsentRevoked | PrescriptionMinted | Dispensed | DrugUnitMinted | CustodyTransferred | ConditionReported | Recalled",
  "subject":  "<recordHash | rxId | drugUnitId | patientDid>",
  "actor":    "<did>",
  "prev":     "<previous event hash or null>",
  "ts":       "2026-05-23T10:14:00Z",
  "payload":  { /* type-specific */ },
  "sig":      { "alg": "Ed25519", "value": "base64url(…)" }
}
```

The contract MUST reject any event whose `prev` does not equal the current head of `subject` (per-subject optimistic concurrency).

### 4.1 Per-type payloads (essentials)

| Type | Required payload |
|---|---|
| `RecordAnchored` | `recordHash`, `policyHash`, `cid` |
| `AccessRequested` | `requester`, `recordHash`, `vcRef` |
| `AccessGranted` / `AccessDenied` | `requester`, `recordHash`, `decisionReason` |
| `ConsentRevoked` | `vcRef`, `reason` |
| `PrescriptionMinted` | `rxId`, `drug`, `qty`, `refills`, `validUntil` |
| `Dispensed` | `rxId`, `pharmacy`, `drugUnitIds[]`, `qty` |
| `DrugUnitMinted` | `drugUnitId`, `gtin`, `lot`, `expiry` |
| `CustodyTransferred` | `from`, `to`, `receiptCid` |
| `ConditionReported` | `tempC?`, `geohash`, `sensorId`, `viaGateway?` |
| `Recalled` | `scope`, `reason` |

## 5. Public API (REST + JSON)

Base URL: `https://api.healthchain.example`. All write requests are signed JWS; reads require an OAuth token bound to a DID role.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/records` | Anchor an encrypted FHIR record (`RecordAnchored`). |
| `POST` | `/v1/access/request` | Submit an access request with consent VC. |
| `POST` | `/v1/consent/revoke` | Revoke a previously issued consent. |
| `POST` | `/v1/prescriptions` | Mint a Prescription. |
| `POST` | `/v1/prescriptions/{id}/dispense` | Record a Dispense. |
| `POST` | `/v1/drug-units` | Mint a DrugUnit. |
| `POST` | `/v1/events` | Append a supply-chain event (custody / condition). |
| `GET`  | `/v1/records/{hash}` | Status of a record anchor (NOT the record itself). |
| `GET`  | `/v1/prescriptions/{id}` | Current state. |
| `GET`  | `/v1/drug-units/{sgtin}/verify` | DSCSA / FMD-style genuineness check. |
| `GET`  | `/v1/audit/access?subject=…&from=…&to=…` | Signed access log. |
| `GET`  | `/v1/reports/regulator?topic=…&period=…` | Signed compliance bundle (with ZK-proofs where applicable). |

Errors follow RFC 7807.

## 6. Cryptography

* **Signatures:** Ed25519 primary; ECDSA-P256 for HSM-bound institutional keys.
* **Symmetric encryption (off-chain payloads):** AES-256-GCM with per-record content encryption keys (CEKs).
* **Key wrapping:** ECIES (P-256) or X25519 to wrap CEKs for the patient's wallet and any active grantees.
* **Hashing:** SHA-256 for record / event chaining.
* **Canonical JSON:** RFC 8785 JCS before signing.
* **Anchoring (hybrid mode):** Daily Merkle root of all events committed to a public EVM L2 contract `PublicAnchor.commit(root, dayUtc)`.

## 7. Smart Contracts (Core)

| Contract | Responsibility |
|---|---|
| `Registry` | Onboards participants; resolves DIDs; manages roles, revocation lists, and key rotation. |
| `Consent` | Tracks active consent VCs by hash; allows on-chain revocation. |
| `AccessControl` | Verifies VC presentation against `Consent` and emits a signed access decision. |
| `RecordAnchor` | Stores `(recordHash, policyHash, cid)` tuples per anchored record. |
| `Prescription` | Mints prescriptions; enforces refill / dispense limits. |
| `Dispense` | Validates dispense requests against `Prescription`; atomic single-dispense window. |
| `DrugUnit` | NFT contract for serialised drug packs (GS1 SGTIN). |
| `EventLog` | Append-only, signature-verified, per-subject chain. |
| `PublicAnchor` | (Public L2) records daily Merkle roots for external verification. |

## 8. Conformance Tests (minimum set)

* **C-1** Replaying the full event chain reproduces the current state of any Prescription, RecordAnchor, or DrugUnit.
* **C-2** Two concurrent `Dispensed` events against the same Prescription succeed at most once (atomicity).
* **C-3** An access request without a valid consent VC is denied; a request with a revoked VC is denied.
* **C-4** A revoked institutional key cannot sign any new event after the revocation block.
* **C-5** Right-to-be-forgotten purges off-chain payloads while preserving on-chain hashes; the verify endpoint returns `payload-unavailable` but the integrity proof for prior actions still verifies.
* **C-6** A ZK-proof asserting "all dispenses in period P were authorised" verifies against the on-chain access log without revealing patient identities.
* **C-7** A DrugUnit verify call rejects an SGTIN whose chain shows no `DrugUnitMinted` event for the claimed manufacturer.
* **C-8** Tampering with any event byte invalidates the signature check.

## 9. Compliance and Regulatory Alignment

* **HIPAA (US):** off-chain PHI; ledger holds only hashes and access decisions. Access decisions form the audit log; institutions sign BAAs as usual.
* **GDPR (EU):** PHI off-chain and deletable; right-to-be-forgotten preserved by hash-only on-chain footprint. DPIA expected before pilot.
* **DSCSA (US):** Drug-unit serialisation aligned with FDA's interoperable, electronic system requirements; events map to EPCIS.
* **EU FMD / EMVS:** Pack-level verification at dispense; integrate with national medicines verification systems where applicable.
* **HL7 FHIR R5:** Mandatory for clinical record payloads.

## 10. Sustainability Events & API (SFC profile)

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Event vocabulary extended with `EnergyAttested` and `CarbonAttested` (monthly per institution). Net Zero invariant: `scope2 + scope3 ≤ offsets` per period. API endpoints (signed JOSE): `/v1/sustainability/operator/{did}`, `/v1/sustainability/network`, `/v1/sustainability/csrd?period=YYYY-MM&operator=did`, `/v1/sustainability/sfc`. Field schemas: [SFC_COMPLIANCE.md §4–§5](../SFC_COMPLIANCE.md).

Particular relevance for healthcare: hospital groups and pharma manufacturers are typical CSRD-in-scope undertakings. The signed ESRS E1 block emitted by `/v1/sustainability/csrd` can be ingested directly by their corporate ESG tooling.

## 11. Versioning

* Spec follows SemVer; breaking schema changes bump MAJOR.
* Event envelopes carry the Registry's schema CID; clients MUST refuse unknown schema CIDs.
* Project's SFC pin: `sustainability-profile: SFC-PROFILE v1.1`.
