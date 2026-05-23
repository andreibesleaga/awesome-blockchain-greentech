# RecyclingChain — Technical Specification (SPEC)

> Minimal technical spec. Companion to [README.md](README.md), [PRD.md](PRD.md), [ARCH.md](ARCH.md).

## 1. Identifiers

| Entity | Format | Example |
|---|---|---|
| Participant | `did:rcy:<network>:<key-fingerprint>` | `did:rcy:main:z6Mkfriq…` |
| ItemToken | URN `urn:rcy:item:<issuer>:<serial>` | `urn:rcy:item:RO-ARG:2025-000123` |
| BatchToken | URN `urn:rcy:batch:<issuer>:<lot>` | `urn:rcy:batch:RO-ARG:2025-Q3-PET-04` |
| MaterialToken | URN `urn:rcy:mat:<recycler>:<stream>:<run>` | `urn:rcy:mat:GR-REC:rPET:2025-09-002` |
| Event | `<itemId>#evt-<monotonic>` | `urn:rcy:item:…#evt-000007` |

All identifiers MUST be resolvable through the Registry's DID Resolver.

## 2. Token Types

### 2.1 ItemToken (NFT)

```jsonc
{
  "id":             "urn:rcy:item:RO-ARG:2025-000123",
  "manufacturerId": "did:rcy:main:z6Mkfriq…",
  "model":          "WashMachine-X1",
  "serial":         "WMX1-2025-000123",
  "manufactureDate":"2025-08-20",
  "composition": [
    { "material": "steel",     "pctMass": 62.4 },
    { "material": "plastic",   "pctMass": 18.1 },
    { "material": "copper",    "pctMass":  4.2 },
    { "material": "electronics","pctMass": 15.3 }
  ],
  "currentOwner":   "did:rcy:main:z6Mkrtl…",
  "custodyStatus":  "in-transit | held | locked",
  "locationHint":   "geohash:u8m3q",
  "lifecycleStage": "registered | distributed | sold | collected | sorted | locked | recycled"
}
```

### 2.2 BatchToken (Semi-Fungible, ERC-1155-style)

```jsonc
{
  "id":           "urn:rcy:batch:RO-ARG:2025-Q3-PET-04",
  "material":     "PET",
  "unitMassKg":   1.0,
  "quantity":     12480,
  "parent":       null,
  "children":     []
}
```

Split / merge operations MUST conserve `quantity * unitMassKg` minus a declared `contaminationKg`.

### 2.3 MaterialToken (Fungible, ERC-20-style)

```jsonc
{
  "id":         "urn:rcy:mat:GR-REC:rPET:2025-09-002",
  "stream":     "rPET-flake",
  "supplyKg":   8920.5,
  "sourceRefs": ["urn:rcy:item:…", "urn:rcy:batch:…"],
  "method":     "mechanical",
  "issuedAt":   "2026-05-23T10:14:00Z"
}
```

`burn(amount, claimRef)` retires units against a brand's recycled-content claim.

## 3. Event Schema

All events share an envelope:

```jsonc
{
  "type":     "ManufactureRegistered | CustodyTransferred | ConditionReported | DecommissionRequested | RecycleCompleted | BatchSplit | BatchMerge",
  "subject":  "<itemId | batchId>",
  "actor":    "<did>",
  "prev":     "<previous event hash or null>",
  "ts":       "2026-05-23T10:14:00Z",
  "payload":  { /* type-specific */ },
  "sig":      { "alg": "Ed25519", "value": "base64url(…)" }
}
```

Events are append-only. The ledger MUST reject any event whose `prev` does not match the current head of `subject` (optimistic concurrency).

### 3.1 Per-type payloads (essentials)

| Type | Required payload fields |
|---|---|
| `ManufactureRegistered` | `composition`, `epr`, `labelPubKey` |
| `CustodyTransferred` | `from`, `to`, `receiptCid` |
| `ConditionReported` | `weightKg`, `contaminationPct`, `photoCid?`, `oracleSig?` |
| `DecommissionRequested` | `recycler`, `expectedMethod`, `lockTtlSec` |
| `RecycleCompleted` | `method`, `yields[{material, pctMass}]`, `residues[{material, kg, disposition}]`, `mintRefs[]` |
| `BatchSplit` | `into[{newBatchId, quantity}]` |
| `BatchMerge` | `from[batchId]`, `intoBatchId` |

## 4. Public API (REST + JSON)

Base URL: `https://api.recyclingchain.example`. All write endpoints require a signed JWS request body; read endpoints are public.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/items` | Mint ItemToken (`ManufactureRegistered`). |
| `POST` | `/v1/batches` | Mint BatchToken. |
| `POST` | `/v1/events` | Append a lifecycle event. |
| `POST` | `/v1/materials/{id}/burn` | Retire MaterialToken units. |
| `GET`  | `/v1/items/{id}` | Current state + composition. |
| `GET`  | `/v1/items/{id}/events` | Full event chain with signatures. |
| `GET`  | `/v1/verify/{itemId}` | One-shot verification: chain valid? terminal event? |
| `GET`  | `/v1/reports/epr?producer=…&from=…&to=…` | Signed EPR / DPP export (PDF + JSON). |
| `GET`  | `/v1/registry/{did}` | Resolve participant DID + roles. |

Errors follow RFC 7807 (`application/problem+json`).

## 5. QR / NFC Label

URI scheme: `recy://i/<itemId>?d=<base64url-json>&sig=<base64url>&alg=Ed25519`

Canonical signed payload (kept short for QR density):

```jsonc
{
  "id":  "RC-RO-ARG-2025-000123",  // short itemId form
  "mfd": "2025-08-20",
  "b":   "4B192A",                  // short batch code
  "s":   "MFA298_pubkey"            // issuer key hint
}
```

* Signature algorithm: Ed25519 over the canonical (RFC 8785) JSON.
* Offline verification: any device with the issuer's public key can validate authenticity without a network round-trip.
* PII MUST NOT appear in the payload.

## 6. Cryptography

* **Signature suite:** Ed25519 (primary); ECDSA-P256 accepted for HSM-bound keys.
* **Hashing:** SHA-256 for event chaining; BLAKE3 permitted for IoT-side batching.
* **Key custody:** Participants are responsible for their keys; the Registry MUST support key rotation via a `KeyRotated` Verifiable Credential.
* **Anchoring:** A daily Merkle root of all core-ledger events is committed to an EVM L2 contract (`PublicAnchor.commit(root, dayUtc)`).

## 7. Smart Contracts (Core)

| Contract | Responsibility |
|---|---|
| `Registry` | Onboard participants; resolve DIDs; enforce role-based ACLs. |
| `ItemNFT` | Mint/burn ItemTokens; restricted to whitelisted Manufacturers. |
| `Batch1155` | Mint/split/merge BatchTokens; conservation invariant enforced. |
| `MaterialERC20` | Mint on `RecycleCompleted`; burn on brand retirement. |
| `Lockbox` | Single-active-decommission lock keyed by `itemId`. |
| `RewardsVault` | Escrow + payout for deposits, bounties, eco-credits. |
| `PublicAnchor` | Receives daily Merkle roots from the core ledger. |
| `OracleAdapter` | Verifies oracle signatures and forwards to event ingestion. |

## 8. Conformance Tests (minimum set)

* **C-1** Replaying the full event chain reproduces the current state of any token.
* **C-2** Attempting a second `DecommissionRequested` on a locked item is rejected.
* **C-3** `RecycleCompleted` yields + residues sum (within ε) to accepted mass.
* **C-4** Tampering with any event byte invalidates the signature check.
* **C-5** Daily anchored Merkle root verifies against the on-chain `PublicAnchor` record.
* **C-6** EPR export round-trips: signed JSON parses back to identical event set.

## 9. Sustainability Events & API (SFC profile)

This project conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). The event vocabulary is extended with:

* `EnergyAttested` — monthly per-operator electricity consumption (kWh, CCRI-aligned methodology, evidence CID).
* `CarbonAttested` — monthly per-operator Scope 2 + Scope 3 kgCO2e, grid-intensity reference, offsets retired, Net Zero boolean.

Net Zero invariant per period: `scope2 + scope3 ≤ offsets`. Sustainability endpoints exposed by the gateway:

* `GET /v1/sustainability/operator/{did}` — last attestation + 12-month rollup.
* `GET /v1/sustainability/network` — network-wide rollup vs. SFC cap (1 GWh / yr).
* `GET /v1/sustainability/csrd?period=YYYY-MM&operator=did` — signed CSRD / ESRS E1 block.
* `GET /v1/sustainability/sfc` — SFC self-report (platform, measured annual energy, compliance status).

Schema and exact field names: see [SFC_COMPLIANCE.md §4–§5](../SFC_COMPLIANCE.md).

## 10. Versioning

* Spec follows SemVer. Breaking schema changes bump MAJOR.
* Event envelopes carry an implicit version via the Registry's published schema CID; clients MUST refuse events whose schema CID is unknown.
* Project's SFC pin: `sustainability-profile: SFC-PROFILE v1.1`.
