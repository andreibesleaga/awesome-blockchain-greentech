# Paperless Billing — Technical Specification (SPEC)

> Minimal technical spec. Companion to [README.md](README.md), [PRD.md](PRD.md), [ARCH.md](ARCH.md).

## 1. Identifiers

| Entity | Format | Example |
|---|---|---|
| Vendor | `did:pbil:<network>:<key-fingerprint>` | `did:pbil:main:z6Mkvend…` |
| Customer (optional) | `did:pbil:user:<key-fingerprint>` | `did:pbil:user:z6Mkbuy…` |
| BillId | URN `urn:pbil:bill:<vendor>:<serial>` | `urn:pbil:bill:RO-MERCH:2026-00001234` |
| CID | IPFS CID v1 | `bafy…` |
| Event | `<billId>#evt-<monotonic>` | `urn:pbil:bill:…#evt-2` |

Vendor DIDs MUST be bound to a verifiable tax-id (VAT number / EIN) via a Registry credential.

## 2. Bill Payloads

Two profiles. Both are JSON; both are encrypted before pinning.

### 2.1 B2C compact receipt

```jsonc
{
  "billId":    "urn:pbil:bill:RO-MERCH:2026-00001234",
  "vendor":    { "did": "did:pbil:main:z6Mkvend…", "name": "ACME Coffee", "vatId": "RO12345678" },
  "issuedAt":  "2026-05-23T10:14:00+02:00",
  "currency":  "EUR",
  "items": [
    { "sku": "ESP-DBL", "desc": "Double Espresso", "qty": 1, "unitNet": 2.50, "vatPct": 9 },
    { "sku": "CRO-1",   "desc": "Croissant",        "qty": 1, "unitNet": 1.80, "vatPct": 9 }
  ],
  "totals":    { "net": 4.30, "vat": 0.39, "gross": 4.69 },
  "payment":   { "method": "card", "last4": "4242" },
  "customer":  null
}
```

### 2.2 B2B invoice — Peppol BIS 3.0 / EN 16931

Use a UBL 2.1 Invoice (or CII) document conforming to **Peppol BIS Billing 3.0**. The on-chain anchor carries:
* `billHash` = SHA-256 over the canonical XML.
* `cid` = IPFS pointer to the encrypted UBL payload.
* `totals` (Net, VAT, Gross), `vatBreakdown[]`, `counterparty` DID + VAT ID.

## 3. On-Chain Anchor

The receipt-anchor contract exposes:

```solidity
// EVM reference. Equivalent NEAR Rust function follows the same shape.
event BillIssued(
  bytes32 indexed billHash,
  bytes   cid,                // multihash / CIDv1
  address indexed vendor,
  bytes32 indexed counterparty, // 0x0 for B2C
  uint256 net,                 // smallest unit
  uint256 vat,
  uint256 gross,
  uint16  currency,            // ISO 4217 numeric
  uint64  issuedAt             // unix sec
);

event BillVoided(bytes32 indexed billHash, bytes reason);
event BillRefunded(bytes32 indexed billHash, uint256 refundGross, bytes32 refundBillHash);

function issue(bytes32 billHash, bytes calldata cid, bytes32 counterparty,
               uint256 net, uint256 vat, uint256 gross,
               uint16 currency, uint64 issuedAt) external;
function void(bytes32 billHash, bytes calldata reason) external;
function refund(bytes32 billHash, uint256 refundGross, bytes32 refundBillHash) external;
```

Contract invariants:
* `issue` MUST revert if `billHash` already anchored.
* `void` / `refund` MUST revert if `billHash` is unknown or already voided.
* Sum of `refund.refundGross` for a given `billHash` MUST NOT exceed the original `gross`.
* Only the vendor whose DID matches `msg.sender` may issue / void / refund their own bills (Registry-resolved).

## 4. Crypto and Encryption

* **CEK:** AES-256-GCM with a per-bill 256-bit content-encryption key.
* **Key wrap:** ECIES (P-256) or X25519 to wrap CEKs for `(vendor, customer, any granted regulator)`.
* **Signatures:** Ed25519 primary; ECDSA secp256k1 accepted on EVM targets.
* **Hashing:** SHA-256.
* **Canonical JSON:** RFC 8785 JCS before hashing.
* **Bill hash:**
  * B2C: `billHash = SHA256(JCS(JSON payload))`.
  * B2B: `billHash = SHA256(canonical UBL XML)` per Peppol canonicalisation.

## 5. Public API (REST + JSON)

Base URL: `https://api.paperlessbill.example`. Writes require a signed JWS; reads are public.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/bills` | Submit a new bill: API encrypts, pins, and anchors. |
| `POST` | `/v1/bills/{id}/void` | Void a previously anchored bill. |
| `POST` | `/v1/bills/{id}/refund` | Record a refund event. |
| `GET`  | `/v1/bills/{id}` | Public anchor state (totals + hash + cid; no line items). |
| `GET`  | `/v1/bills/{id}/payload` | Encrypted payload (CEK-wrapped). Caller decrypts locally. |
| `POST` | `/v1/bills/{id}/grant` | Grant another DID decryption access to this bill. |
| `GET`  | `/v1/verify?cid=…&hash=…` | Integrity verdict ("valid" / "tampered"). |
| `GET`  | `/v1/audit/vendor?vendor=…&from=…&to=…` | Signed vendor-period bundle. |

Errors follow RFC 7807.

## 6. Customer Linking Flows

* **At-issuance scan:** The POS shows a QR `pbil://claim/<billId>?one_time=<token>`; the customer wallet posts to `/v1/bills/{id}/claim` with their DID + token; contract emits `BillClaimed`.
* **Post-hoc claim:** Vendor publishes a magic link; same `/v1/bills/{id}/claim` endpoint.

A bill can only be claimed once. Claiming binds the bill to a customer DID but does NOT publish the customer DID on-chain (the link is recorded off-chain under the customer's wallet).

## 7. Tax Authority Integration

* Authority issues a Verifiable Credential to itself (or to a specific auditor) listing the audit scope (vendor, period).
* Vendor's gateway honours the VC by streaming the encrypted payloads + wrapped CEKs to the authority's endpoint, or by issuing a `Granted` event referencing the VC hash.
* National e-invoicing systems (Italy SdI, Spain Veri*factu, France Chorus Pro, Romania e-Factura) are integrated through adapters that translate the canonical UBL into the national submission format.

## 8. Conformance Tests (minimum set)

* **C-1** Two anchors with the same `billHash` — the second fails.
* **C-2** A `void` for an unknown `billHash` fails.
* **C-3** Cumulative refunds cannot exceed original gross.
* **C-4** A modified payload (any byte) fails `/v1/verify`.
* **C-5** A B2B payload validates against Peppol BIS Billing 3.0.
* **C-6** A vendor cannot issue / void a bill whose `vendor` field does not match the signing DID.
* **C-7** A regulator with a valid grant VC can decrypt; without the grant, decryption is impossible (no on-chain leakage).
* **C-8** Audit export for a vendor + period reconstructs to the same `totals` from the on-chain events alone (no off-chain dependency for the totals).

## 9. Sustainability Events & API (SFC profile)

Conforms to [Sustainability-First Consensus profile v1.1](../SFC_COMPLIANCE.md). Gateway operators publish `EnergyAttested` and `CarbonAttested` events monthly (chain-tier energy reported by the NEAR Foundation per their public certification). Net Zero invariant: `scope2 + scope3 ≤ offsets` per period. API endpoints (signed JOSE): `/v1/sustainability/operator/{did}`, `/v1/sustainability/network`, `/v1/sustainability/csrd?period=YYYY-MM&operator=did`, `/v1/sustainability/sfc`. Field schemas: [SFC_COMPLIANCE.md §4–§5](../SFC_COMPLIANCE.md).

CSRD-in-scope retailers using this project ingest the signed ESRS E1 block as a Scope-3 input for the digital-receipt service they consume.

## 10. Versioning

* Spec follows SemVer.
* Anchor contract uses an upgrade pattern with explicit version pinning per bill (a bill is bound to the contract version active at issuance time).
* Project's SFC pin: `sustainability-profile: SFC-PROFILE v1.1`.
