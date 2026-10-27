# Roaming Data Exchange — Technical Specification (SPEC)

> Minimal technical spec. Companion to [README.md](README.md), [PRD.md](PRD.md), [ARCH.md](ARCH.md).

## 1. Identifiers

| Entity | Format | Example |
|---|---|---|
| User | `did:rdx:user:<key-fingerprint>` | `did:rdx:user:z6Mkusr…` |
| Operator | `did:rdx:op:<country>:<key-fingerprint>` | `did:rdx:op:DE:z6Mkop…` |
| Roaming Pair | `urn:rdx:pair:<homeDid>:<foreignDid>` | `urn:rdx:pair:did:rdx:op:DE:z6Mk…:did:rdx:op:FR:z6Mk…` |
| Session | `urn:rdx:session:<foreignDid>:<localId>` | `urn:rdx:session:did:rdx:op:FR:z6Mk…:2026-CDR-000123` |
| Event | `<sessionId>#evt-<monotonic>` | `urn:rdx:session:…#evt-3` |

User DIDs are issued by the Home Operator. Operator DIDs are issued by the Registry.

## 2. Verifiable Credential — Roaming Plan

```jsonc
{
  "@context":     ["https://www.w3.org/2018/credentials/v1"],
  "type":         ["VerifiableCredential", "RoamingPlan"],
  "id":           "urn:rdx:vc:cafe…",
  "issuer":       "did:rdx:op:DE:z6Mkop…",
  "issuanceDate": "2026-05-01T00:00:00Z",
  "expirationDate":"2027-05-01T00:00:00Z",
  "credentialSubject": {
    "id":          "did:rdx:user:z6Mkusr…",
    "planTier":    "standard",
    "fairUseMb":   25000,
    "creditOk":    true,
    "allowedDomains": ["telecom", "ev-charging"]
  },
  "proof": { "type": "Ed25519Signature2020", "verificationMethod": "did:rdx:op:DE:z6Mkop…#k1", "proofValue": "…" }
}
```

Wallets present a **selective-disclosure JWT** (SD-JWT) or a BBS+ proof revealing only `(issuer is Registry-listed, creditOk == true, allowedDomains contains <X>, expirationDate > now)`.

## 3. On-Chain Contracts

| Contract | Responsibility |
|---|---|
| `Registry` | Onboards Operators with DIDs and role VCs; manages key rotation and revocation. |
| `PairAgreement` | Holds bilateral parameters per Operator pair (tariff schedule, fair-use, dispute window, bond requirement). |
| `BondVault` | Per-Operator pre-posted bonds; reserves and releases per session. |
| `Authorisation` | Verifies user VC presentation against Registry; emits `AccessGranted` / `AccessDenied`. |
| `Session` | Stores session lifecycle events; enforces single-active-session invariants. |
| `Settlement` | Triggers micro-settlement after the dispute window; emits `Settled`. |
| `OracleAdapter` | Verifies signed measurements from meters / probes if non-CPO inputs are used. |

## 4. Event Schema

Every event uses a signed envelope:

```jsonc
{
  "type":     "AccessRequested | AccessGranted | AccessDenied | SessionStarted | SessionMetered | SessionEnded | SettlementProposed | Disputed | Settled | Revoked",
  "subject":  "<sessionId | did | pairId>",
  "actor":    "<did>",
  "prev":     "<previous event hash or null>",
  "ts":       "2026-05-23T10:14:00Z",
  "payload":  { /* type-specific */ },
  "sig":      { "alg": "Ed25519", "value": "base64url(…)" }
}
```

The chain is per subject and type: `prev` is the hash of the previous event of the same `subject` and `type`.

### 4.1 Per-type payloads (essentials)

| Type | Required payload |
|---|---|
| `AccessRequested` | `userVcProof`, `foreignOp`, `requestedService`, `maxCostCents` |
| `AccessGranted` | `homeOp`, `sessionId`, `bondReservedCents`, `expiresAt` |
| `AccessDenied` | `reason` |
| `SessionStarted` | `sessionId`, `serviceType`, `startTs`, `meterStart` |
| `SessionMetered` | `meter`, `consumed`, `costSoFarCents` |
| `SessionEnded` | `meterEnd`, `totalConsumed`, `totalCostCents`, `cdrCid?` (OCPI export pointer) |
| `SettlementProposed` | `sessionId`, `payerOp`, `payeeOp`, `amountCents`, `currency` |
| `Disputed` | `sessionId`, `reason`, `evidenceCid?` |
| `Settled` | `sessionId`, `settlementRef` |
| `Revoked` | `vcId`, `userDid`, `reason` |

## 5. Public API (REST + JSON)

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/v1/access` | Foreign Operator submits a credential proof, gets `AccessGranted`/`Denied`. |
| `POST` | `/v1/sessions` | Open a session after `AccessGranted`. |
| `POST` | `/v1/sessions/{id}/meter` | Periodic metering update. |
| `POST` | `/v1/sessions/{id}/end` | Close session and trigger `SettlementProposed`. |
| `POST` | `/v1/sessions/{id}/dispute` | Raise a dispute. |
| `GET`  | `/v1/sessions/{id}` | Current session state and chain of events. |
| `GET`  | `/v1/pairs/{id}` | Effective `PairAgreement` for the operator pair. |
| `GET`  | `/v1/cdr/{sessionId}` | OCPI 2.2 `CDR` export for an EV session. |
| `GET`  | `/v1/audit/operator?op=…&from=…&to=…` | Signed settlement bundle. |

Writes require signed JWS; reads are restricted to Registry-listed Operators or auditors.

## 6. Cryptography

* **Signatures:** Ed25519 primary; ECDSA-P256 accepted for HSM-bound operator keys.
* **Hashing:** SHA-256 for event chaining.
* **Canonical JSON:** RFC 8785 JCS before signing.
* **ZK presentation:** SD-JWT (default) or BBS+ for richer selective disclosure.
* **Bonds:** Held in `BondVault` as stablecoin / fiat-backed deposit (per operator-pair policy).

## 7. Standards Mapping

* **EV (OCPI 2.2+):** Each `Session` maps to an OCPI `CDR`. The Roaming Gateway runs an OCPI Access Point and exposes both an OCPI and a DLT view of the same data.
* **EV (OCPP 2.0.1 / IEC 63584):** The charge point ↔ CPO link is untouched; the gateway sees CPO-side session data only.
* **Telecom (GSMA eBusiness Network):** Session aggregates translate into the GSMA-defined settlement file format; settlement events can be posted to the GSMA Fabric network through an adapter.
* **Identity:** W3C DID Core 1.0; W3C VC Data Model; SD-JWT VCs (IETF SD-JWT working draft).

## 8. Conformance Tests (minimum set)

* **C-1** A revoked user VC fails `AccessRequested` within 5 s of revocation.
* **C-2** Replay of a previously accepted ZK proof in a new session fails (nonce binding).
* **C-3** A `SettlementProposed` with an amount exceeding the reserved bond fails.
* **C-4** A session marked `Disputed` does not auto-settle until the dispute is resolved.
* **C-5** A `SessionEnded` reconstructs to a valid OCPI 2.2 `CDR` (EV path).
* **C-6** A second concurrent `SessionStarted` against the same `userDid` + same `serviceType` is rejected (single-active-session invariant).
* **C-7** Tampering with any event byte invalidates the signature check.
* **C-8** A renewable-energy ESG tag references a verifiable Guarantee-of-Origin or is dropped.
* **C-SFC** Run the profile 2.0 deep check (9.4) on the network declaration with a read of the network's ledger. The overall result (9.5) is PASS, with the C-SFC-3 row DECLARED. Without a read, D1 and C-SFC-7 are NOT-EVALUABLE ("no ledger read given"), so the overall result cannot be PASS.

## 9. Privacy and GDPR

* The Foreign Operator never receives the user's identity — only the credential proof.
* Session records on-chain reference `userDid`s issued ephemerally per Home Operator policy (rotation possible).
* Right-to-be-forgotten: Home Operator can stop issuing new VCs and request purge of off-chain payloads; on-chain pseudonymous events remain but no longer link to a person.

## 10. Sustainability events and API (defined in SFC profile 2.0)

SFC: this design follows [SFC profile 2.0](../SFC_COMPLIANCE.md); its project facts are in ARCH.md, section "SFC Compliance Profile". The profile defines the events in sections 5.2 to 5.4 and the declaration in sections 7 and 8.

## 11. Versioning

* Spec follows SemVer.
* Contracts upgrade via a registry-pinned version per `PairAgreement`.
