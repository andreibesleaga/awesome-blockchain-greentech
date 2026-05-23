# Sustainability Climate Change — Technical Specification (SPEC)

> Minimal technical spec for the MRV-anchored carbon-credit registry described in [PRD.md](PRD.md). Companion to [README.md](README.md), [ARCH.md](ARCH.md).

## 1. Identifiers

| Entity | Format | Example |
|---|---|---|
| Participant | `did:scc:<role>:<key-fingerprint>` | `did:scc:proj:z6Mkproj…` |
| Methodology | URN `urn:scc:method:<body>:<id>:<version>` | `urn:scc:method:verra:vm0042:v2.0` |
| Project | URN `urn:scc:project:<issuer>:<localId>` | `urn:scc:project:RO-GOV:2026-FOR-001` |
| MRV Evidence | CID (IPFS) + `urn:scc:mrv:<projectId>:<periodId>` | `urn:scc:mrv:urn:scc:project:…:2026-Q1` |
| Credit Batch | URN `urn:scc:credit:<projectId>:<vintage>:<batch>` | `urn:scc:credit:urn:scc:project:…:2026:001` |
| Event | `<subject>#evt-<monotonic>` | `urn:scc:credit:…#evt-5` |

## 2. Token Model

### 2.1 CreditBatch (semi-fungible)

```jsonc
{
  "id":            "urn:scc:credit:urn:scc:project:RO-GOV:2026-FOR-001:2026:001",
  "project":       "urn:scc:project:RO-GOV:2026-FOR-001",
  "vintage":       "2026",
  "quantityTCO2e": 5000,
  "methodologyHash":"sha256:abc…",
  "mrvRefs":       ["urn:scc:mrv:urn:scc:project:…:2026-Q1"],
  "status":        "issued | partly-retired | retired | disputed",
  "holder":        "did:scc:buyer:z6Mk…"
}
```

Per-batch invariants:

* Total `transferred + retired + bridged-out` MUST NOT exceed `quantityTCO2e`.
* `retired` is monotonic non-decreasing; cannot decrease.
* While `status == disputed`, all transfers and retirements are blocked.

### 2.2 RetirementClaim (non-transferable, soul-bound)

```jsonc
{
  "id":          "urn:scc:retire:RO-CO:2026:001",
  "batchRef":    "urn:scc:credit:…",
  "quantity":    1200,
  "beneficiary": "did:scc:buyer:z6Mkbuy…",
  "scope":       "Scope-3 emissions, reporting year 2026",
  "reportYear":  2026,
  "retiredAt":   "2026-05-23T10:14:00Z"
}
```

## 3. Methodology Anchor

```jsonc
{
  "id":           "urn:scc:method:verra:vm0042:v2.0",
  "body":         "Verra",
  "publishedAt":  "2023-05-18",
  "documentCid":  "bafy…",        // canonical PDF on IPFS
  "documentHash": "sha256:…",     // SHA-256 over the canonical PDF
  "paramsCid":    "bafy…",        // machine-readable parameters JSON
  "paramsHash":   "sha256:…",
  "supersedes":   "urn:scc:method:verra:vm0042:v1.0"
}
```

The registry MUST refuse `Issued` events whose `methodologyHash` does not match a registered methodology.

## 4. Event Schema

Signed envelope shared by all events:

```jsonc
{
  "type":     "MethodologyRegistered | ProjectRegistered | MRVSubmitted | Validated | Rejected | Issued | Transferred | Retired | Disputed | DisputeResolved | BridgeBurned | BridgeMinted",
  "subject":  "<projectId | batchId | methodologyId>",
  "actor":    "<did>",
  "prev":     "<previous event hash or null>",
  "ts":       "2026-05-23T10:14:00Z",
  "payload":  { /* type-specific */ },
  "sig":      { "alg": "Ed25519", "value": "base64url(…)" }
}
```

### 4.1 Per-type payloads (essentials)

| Type | Required payload |
|---|---|
| `MethodologyRegistered` | `methodologyId`, `documentCid`, `documentHash`, `paramsCid`, `paramsHash` |
| `ProjectRegistered` | `projectId`, `methodologyRef`, `geofence`, `developerDid` |
| `MRVSubmitted` | `evidenceCid`, `period`, `sensorRefs[]`, `measurementsHash` |
| `Validated` | `verifierDid`, `mrvRef`, `tCO2eClaimed`, `notesCid?` |
| `Rejected` | `verifierDid`, `mrvRef`, `reason` |
| `Issued` | `batchId`, `tCO2e`, `vintage`, `methodologyHash`, `mrvRefs[]` |
| `Transferred` | `batchId`, `from`, `to`, `quantity` |
| `Retired` | `batchId`, `quantity`, `beneficiary`, `scope`, `reportYear` |
| `Disputed` | `batchId`, `reason`, `evidenceCid?` |
| `DisputeResolved` | `batchId`, `resolution`, `actionTakenCid?` |
| `BridgeBurned` | `batchId`, `quantity`, `targetChain`, `targetTxRef?` |
| `BridgeMinted` | `batchId`, `quantity`, `sourceChain`, `sourceTxRef`, `sourceBurnHash` |

## 5. Public API

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/methodologies` | Register a methodology version. |
| `POST` | `/v1/projects` | Register a project. |
| `POST` | `/v1/mrv` | Submit MRV evidence. |
| `POST` | `/v1/validations` | Verifier emits Validated / Rejected. |
| `POST` | `/v1/credits/issue` | Mint a CreditBatch (after Validated). |
| `POST` | `/v1/credits/{id}/transfer` | Transfer a quantity. |
| `POST` | `/v1/credits/{id}/retire` | Retire a quantity. |
| `POST` | `/v1/credits/{id}/dispute` | Open a dispute. |
| `POST` | `/v1/credits/{id}/bridge` | Burn for bridge-out, or mint from bridge-in. |
| `GET`  | `/v1/credits/{id}` | Current state and lineage. |
| `GET`  | `/v1/projects/{id}/events` | Project event chain. |
| `GET`  | `/v1/audit/buyer?buyer=…&year=…` | Signed retirement bundle for a buyer / report year. |

Errors follow RFC 7807.

## 6. Cryptography

* **Signatures:** Ed25519 primary; ECDSA-P256 for HSM-bound institutional keys.
* **Hashing:** SHA-256 for event chaining, methodology and MRV-evidence hashing.
* **Canonical JSON:** RFC 8785 JCS before signing.
* **MRV evidence integrity:** sensor measurements signed at source where a secure element exists; otherwise signed by the project gateway and the delegation recorded.
* **Anchoring (optional hybrid mode):** daily Merkle root anchored to an EVM L2 contract `PublicAnchor.commit(root, dayUtc)`.

## 7. Smart Contracts (Core)

| Contract | Responsibility |
|---|---|
| `Registry` | Onboards Projects, Verifiers, Registry Operators, Buyers, Auditors; manages role VCs. |
| `Methodology` | Anchors methodology versions; enforces immutability per version. |
| `CreditRegistry` | Mint / transfer / retire CreditBatches; enforces invariants. |
| `Dispute` | Locks credits during dispute; records resolution. |
| `Bridge` | Burn / mint with cross-chain reference; requires proof-of-burn from source side. |
| `EventLog` | Append-only signed event chain. |
| `PublicAnchor` | (Optional L2) daily Merkle roots. |

## 8. Conformance Tests (minimum set)

* **C-1** Issuance with a methodology hash not registered is rejected.
* **C-2** Issuance without a corresponding `Validated` event is rejected.
* **C-3** Retiring more than the held quantity is rejected.
* **C-4** A `Retired` quantity cannot later be transferred (immutability of retirement).
* **C-5** A second `BridgeMinted` for the same source burn proof is rejected (no double-mint across chains).
* **C-6** While `status == disputed`, any transfer or retirement is rejected.
* **C-7** Buyer audit bundle reconstructs to the same retirement totals as the on-chain events alone.
* **C-8** Tampering with any event byte invalidates the signature check.

## 9. Methodology and Reporting Alignment

* Methodologies referenced SHOULD be published by recognised bodies (Verra, Gold Standard, Puro.earth, national programs registered through Hedera Guardian).
* Buyer retirement claims SHOULD use scopes aligned with the [GHG Protocol Corporate Standard](https://ghgprotocol.org/corporate-standard) and the [GHG Protocol Product Standard](https://ghgprotocol.org/product-standard).
* For EU buyers: align retirement claims with [CSRD ESRS E1](https://efrag.org/lab6) climate disclosures and, where relevant, [CBAM](https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism_en) reporting.

## 10. Sustainability Events & API (SFC profile, self-applied)

Conforms to and *self-applies* [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Event vocabulary extended with `EnergyAttested` and `CarbonAttested` (monthly per Operator). Net Zero invariant per period. Where the operator retires offsets to satisfy Net Zero, the retirement events used MAY be drawn from this very registry (`Retired` events on `CreditBatch`es) — closing the loop and enabling auditors to trace every claimed offset back to a verified MRV chain.

API endpoints (signed JOSE): `/v1/sustainability/operator/{did}`, `/v1/sustainability/network`, `/v1/sustainability/csrd?period=YYYY-MM&operator=did`, `/v1/sustainability/sfc`. Field schemas: [SFC_COMPLIANCE.md §4–§5](../SFC_COMPLIANCE.md).

## 11. Versioning

* Spec follows SemVer.
* Methodology versions are immutable; supersession is explicit via `supersedes`.
* Event schema CIDs are pinned in the Registry; clients MUST refuse unknown schema CIDs.
* Project's SFC pin: `sustainability-profile: SFC-PROFILE v1.1`.
