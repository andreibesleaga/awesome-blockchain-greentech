# Certification Supply-Chain — Technical Specification (SPEC)

> Minimal technical spec. Companion to [README.md](README.md), [PRD.md](PRD.md), [ARCH.md](ARCH.md).

## 1. Identifiers

All identifiers MUST be resolvable through the Registry's DID resolver and SHOULD also map to a GS1 Digital Link URI for shared tooling.

| Entity | Format | Example |
|---|---|---|
| Participant | `did:csc:<network>:<key-fingerprint>` | `did:csc:main:z6Mkrtl…` |
| ItemToken | URN `urn:csc:item:<issuer>:<serial>` | `urn:csc:item:LEATHER-CO:2026-000451` |
| BatchToken | URN `urn:csc:batch:<issuer>:<lot>` | `urn:csc:batch:OLIVE-FARM:2026-H2-LOT-007` |
| Certification | URN `urn:csc:cert:<scheme>:<credential-id>` | `urn:csc:cert:eu-organic:abc-123` |
| Event | `<tokenId>#evt-<monotonic>` | `urn:csc:item:…#evt-00012` |

## 2. Token Types

### 2.1 ItemToken (ERC-721 style, per-item)

```jsonc
{
  "id":           "urn:csc:item:LEATHER-CO:2026-000451",
  "issuer":       "did:csc:main:z6Mkrtl…",
  "category":     "leather-good",
  "origin":       { "country": "IT", "region": "Tuscany", "geohash": "spzpgxc" },
  "composition":  [ { "material": "leather", "pctMass": 92.5 } ],
  "manufactured": "2026-03-11",
  "markType":     "laser-engraved",
  "markPubKey":   "z6Mk…",
  "currentOwner": "did:csc:main:z6Mklog…",
  "certifications": [ "urn:csc:cert:fair-trade:xyz-991" ],
  "lifecycleStage": "minted | in-transit | at-retail | sold | recalled"
}
```

### 2.2 BatchToken (ERC-1155 style, per-lot)

```jsonc
{
  "id":           "urn:csc:batch:OLIVE-FARM:2026-H2-LOT-007",
  "issuer":       "did:csc:main:z6Mkfarm…",
  "material":     "extra-virgin-olive-oil",
  "unitMassKg":   0.75,
  "quantity":     4000,
  "origin":       { "country": "GR", "region": "Kalamata", "geohash": "swbb…" },
  "certifications": [ "urn:csc:cert:eu-organic:abc-123" ],
  "parent":       null,
  "children":     []
}
```

`split` and `merge` operations MUST conserve `quantity * unitMassKg` modulo a declared `lossKg` field.

## 3. Certification as Verifiable Credential

A certification is a W3C Verifiable Credential (VC) signed by a Registry-listed certifier:

```jsonc
{
  "@context":        ["https://www.w3.org/2018/credentials/v1"],
  "type":            ["VerifiableCredential", "SupplyChainCertification"],
  "id":              "urn:csc:cert:eu-organic:abc-123",
  "issuer":          "did:csc:main:z6Mkcert…",
  "issuanceDate":    "2026-04-01T00:00:00Z",
  "expirationDate":  "2027-04-01T00:00:00Z",
  "credentialSubject": {
    "id":     "urn:csc:batch:OLIVE-FARM:2026-H2-LOT-007",
    "scheme": "EU-Organic-2018/848",
    "scope":  "batch",
    "evidence": [ { "cid": "bafy…", "type": "audit-report" } ]
  },
  "proof": { "type": "Ed25519Signature2020", "verificationMethod": "did:csc:main:z6Mkcert…#k1", "proofValue": "…" }
}
```

Only the VC's SHA-256 hash is stored on-chain (`CertificationAttached` event). The VC itself lives off-chain and is fetched by CID when needed.

## 4. Event Schema

Every event is a signed envelope:

```jsonc
{
  "type":     "Minted | CertificationAttached | CertificationRevoked | CustodyTransferred | ConditionReported | Inspected | Sold | Recalled | BatchSplit | BatchMerge",
  "subject":  "<tokenId>",
  "actor":    "<did>",
  "prev":     "<previous event hash or null>",
  "ts":       "2026-05-23T10:14:00Z",
  "payload":  { /* type-specific */ },
  "sig":      { "alg": "Ed25519", "value": "base64url(…)" }
}
```

The contract MUST reject any event whose `prev` does not equal the current head of `subject`.

### 4.1 Per-type payloads (essentials)

| Type | Required payload fields |
|---|---|
| `Minted` | `tokenType`, `metaCid` |
| `CertificationAttached` | `vcId`, `vcHash`, `vcCid` |
| `CertificationRevoked` | `vcId`, `reason` |
| `CustodyTransferred` | `from`, `to`, `receiptCid` |
| `ConditionReported` | `tempC?`, `rhPct?`, `geohash`, `sensorId`, `viaGateway?` |
| `Inspected` | `inspectorDid`, `result`, `reportCid?` |
| `Sold` | `buyerDid?`, `posId`, `priceCommit?` |
| `Recalled` | `reason`, `scope` |
| `BatchSplit` | `into[{newBatchId, quantity}]`, `lossKg` |
| `BatchMerge` | `from[batchId]`, `intoBatchId` |

## 5. Marking Rules

* **Hard goods (per-item):** Laser-engrave the UID as a Data Matrix code (ISO/IEC 16022). The mark MUST include a 16-byte payload: `version(1) | tokenId-hash(8) | issuer-fingerprint(4) | crc(3)`. The full URN is resolved server-side from the hash.
* **Packaging (per-item or per-batch):** GS1 Digital Link URI in QR plus a short Ed25519 signature; tamper-evident substrate.
* **Soft produce (batch only):** "Natural branding" mark identifies the batch. Per-item identification is NOT claimed.
* **NFC (high-value):** Secure-element-backed tag; signs a challenge to prove physical possession (anti-cloning).

## 6. Public API (REST + JSON)

Base URL: `https://api.certchain.example`. Writes require a signed JWS body; reads are public.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/items` | Mint ItemToken. |
| `POST` | `/v1/batches` | Mint BatchToken. |
| `POST` | `/v1/certifications` | Anchor a VC against one or more tokens. |
| `POST` | `/v1/events` | Append a lifecycle event. |
| `GET`  | `/v1/items/{id}` / `/v1/batches/{id}` | Current state. |
| `GET`  | `/v1/items/{id}/events` | Full event chain with signatures. |
| `GET`  | `/v1/verify/{tokenId}` | Verdict: chain valid, certifications active, last known state. |
| `GET`  | `/v1/carbon?token=…` | GHG-Protocol product carbon report. |
| `GET`  | `/v1/reports/csrd?producer=…&from=…&to=…` | Signed CSRD / CBAM bundle. |
| `GET`  | `/v1/registry/{did}` | Resolve participant DID + roles. |

Errors follow RFC 7807.

## 7. Cryptography

* **Signatures:** Ed25519 primary; ECDSA-P256 accepted for HSM-bound or secure-element keys.
* **Hashing:** SHA-256 for event chaining and VC anchoring.
* **Canonical JSON:** RFC 8785 JCS before signing.
* **Key custody:** Participants manage their own keys; rotation expressed via a `KeyRotated` VC.
* **Anchoring (hybrid mode):** Daily Merkle root committed to a public EVM L2 contract `PublicAnchor.commit(root, dayUtc)`.

## 8. Smart Contracts (Core)

| Contract | Responsibility |
|---|---|
| `Registry` | Onboard participants; resolve DIDs; manage roles and revocation. |
| `ItemNFT` | Mint / burn / transfer of ItemTokens; bind UID → tokenId. |
| `Batch1155` | Mint / split / merge BatchTokens; conservation invariant. |
| `CertRegistry` | Anchor VC hashes; track active vs. revoked. |
| `EventLog` | Append-only per-subject log; signature verification. |
| `PublicAnchor` | (Public L2) records daily Merkle roots. |
| `OracleAdapter` | Verifies sensor / gateway signatures. |

## 9. Conformance Tests (minimum set)

* **C-1** Replaying the full event chain reproduces the current token state.
* **C-2** Attempting to mint a second token bound to the same UID fails.
* **C-3** A custody transfer signed by a non-current-owner is rejected.
* **C-4** Batch split / merge conserves mass within declared `lossKg`.
* **C-5** A certification VC whose hash on-chain does not match the off-chain document fails verification.
* **C-6** A revoked sensor key's measurement is rejected, even if otherwise well-formed.
* **C-7** The daily anchored Merkle root verifies against the public-chain `PublicAnchor` record.
* **C-8** Two identical scans within an impossible-velocity window raise an anomaly flag.

## 10. Sustainability Events & API (SFC profile)

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Event vocabulary extended with:

* `EnergyAttested` — monthly per-operator electricity consumption (kWh, CCRI methodology, evidence CID).
* `CarbonAttested` — monthly per-operator Scope 2 + Scope 3 kgCO2e, grid-intensity reference, offsets retired, Net Zero boolean.

Net Zero invariant: `scope2 + scope3 ≤ offsets`. API endpoints (all signed JOSE):

* `GET /v1/sustainability/operator/{did}` — last attestation + 12-month rollup.
* `GET /v1/sustainability/network` — network-wide rollup vs. SFC cap (1 GWh / yr).
* `GET /v1/sustainability/csrd?period=YYYY-MM&operator=did` — signed CSRD / ESRS E1 block.
* `GET /v1/sustainability/sfc` — SFC self-report.

Schema details: [SFC_COMPLIANCE.md §4–§5](../SFC_COMPLIANCE.md).

## 11. Versioning

* Spec follows SemVer.
* Event envelopes carry the Registry-published schema CID; clients MUST refuse unknown schema CIDs.
* Project's SFC pin: `sustainability-profile: SFC-PROFILE v1.1`.
