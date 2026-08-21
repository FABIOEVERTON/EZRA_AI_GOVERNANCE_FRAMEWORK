# ezra-control-plane — Ledger Specification (DS-040 Compliance)

## Overview

This document specifies the **Append-Only Governance Ledger** implementation in ezra-control-plane, compliant with **AGCP DS-040 Governance Ledger Event Specification v2.0.8**.

**Status**: Normative
**AGCP Version**: v2.0.8
**DS-040 Version**: 2.0.8

---

## 1. Purpose

The ledger is the **authoritative, immutable record** of governance-significant events providing:
- Governance integrity
- Deterministic replay
- Auditability
- Evidence preservation

---

## 2. Storage

```sql
-- SQLite with append-only semantics
PRAGMA journal_mode = WAL;
PRAGMA synchronous = FULL;
PRAGMA foreign_keys = ON;

CREATE TABLE governance_ledger (
    ledger_event_id TEXT PRIMARY KEY,
    event_version TEXT NOT NULL DEFAULT '2.0.8',
    record_type TEXT NOT NULL DEFAULT 'GOVERNANCE_LEDGER_EVENT',
    event_type TEXT NOT NULL,
    event_category TEXT NOT NULL,
    ledger_id TEXT NOT NULL,
    ordering_scope TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    predecessor_event_id TEXT,
    previous_event_digest TEXT,
    tenant_id TEXT NOT NULL,
    governance_domain_id TEXT NOT NULL,
    event_subject_type TEXT NOT NULL,
    event_subject_id TEXT NOT NULL,
    event_artifact_refs TEXT NOT NULL,  -- JSON
    governance_basis TEXT NOT NULL,      -- JSON
    evidence_binding TEXT NOT NULL,      -- JSON
    causality TEXT,                      -- JSON
    event_time TEXT NOT NULL,
    append_status TEXT NOT NULL DEFAULT 'APPENDED',
    append_only_controls TEXT NOT NULL,  -- JSON
    integrity_protection TEXT NOT NULL,  -- JSON
    attribution TEXT NOT NULL,           -- JSON
    provenance TEXT NOT NULL,            -- JSON
    replay_material TEXT NOT NULL,       -- JSON
    semantic_assertions TEXT NOT NULL,   -- JSON
    event_uri TEXT NOT NULL
);

-- Indexes for deterministic retrieval
CREATE INDEX idx_ledger_ordering ON governance_ledger(ledger_id, ordering_scope, sequence);
CREATE INDEX idx_ledger_proposal ON governance_ledger(ordering_scope);
CREATE INDEX idx_ledger_tenant ON governance_ledger(tenant_id, governance_domain_id);
CREATE INDEX idx_ledger_event_type ON governance_ledger(event_type);
CREATE INDEX idx_ledger_time ON governance_ledger(event_time);

-- Integrity view
CREATE VIEW ledger_integrity AS
SELECT 
    ledger_event_id,
    sequence,
    previous_event_digest,
    integrity_protection,
    CASE 
        WHEN sequence = 0 THEN 'GENESIS'
        WHEN json_extract(previous_event_digest, '$.value') = 
             lag(json_extract(integrity_protection, '$.digest')) OVER (PARTITION BY ledger_id, ordering_scope ORDER BY sequence)
        THEN 'VALID'
        ELSE 'BROKEN'
    END as chain_status
FROM governance_ledger
WHERE ledger_id = ? AND ordering_scope = ?
ORDER BY sequence;
```

---

## 3. DS-040 Event Representation

Every appended record conforms to **DS-040** with these required properties:

| Property | Type | Description |
|----------|------|-------------|
| `ledger_event_id` | UUID | Unique event identifier |
| `event_version` | String | "2.0.8" |
| `record_type` | String | "GOVERNANCE_LEDGER_EVENT" |
| `event_type` | Enum | See Event Types below |
| `event_category` | Enum | LIFECYCLE, EXECUTION, EVIDENCE, ADMINISTRATIVE, INCIDENT, COMPLIANCE |
| `ledger_id` | String | Tenant-governance domain |
| `ordering_scope` | UUID | Proposal ID for ordering |
| `ledger_position` | Object | Sequence, predecessor, digests |
| `tenant_id` | UUID | Tenant identifier |
| `governance_domain_id` | UUID | Governance domain |
| `event_subject` | Object | Subject type + ID |
| `event_artifact_refs` | Array | Typed artifact references |
| `governance_basis` | Object | Policy/constraint/invariant refs |
| `evidence_binding` | Object | Evidence references |
| `causality` | Object | Parent/dependency events |
| `event_time` | ISO8601 | Authoritative timestamp |
| `append_status` | String | "APPENDED" |
| `append_only_controls` | Object | Immutable + correction by subsequent |
| `integrity_protection` | Object | Algorithm, digest, chain digest |
| `attribution` | Object | Actor ID, type, role |
| `provenance` | Object | ES256 detached signature |
| `replay_material` | Object | Reconstruction data |
| `semantic_assertions` | Object | Append-only, ordering, isolation, etc. |
| `event_uri` | URI | agcp://tenant/domain/ledger/uuid |

---

## 4. Event Types

| Event Type | Category | Description |
|------------|----------|-------------|
| `PROPOSAL_SUBMITTED` | LIFECYCLE | Proposal received |
| `PROPOSAL_QUALIFIED` | LIFECYCLE | Proposal passed qualification |
| `GOVERNANCE_DECISION` | LIFECYCLE | GDF decision (authorized/denied/refused) |
| `GOVERNANCE_APPROVAL` | LIFECYCLE | HITL approval (DS-026) |
| `EXECUTION_AUTHORIZATION` | EXECUTION | Authorization issued |
| `COMMIT_BOUNDARY` | EXECUTION | Commit boundary processing |
| `EXECUTION_COMPLETE` | EXECUTION | Tool execution finished |
| `STRUCTURAL_REFUSAL` | LIFECYCLE | Hard refusal (invariant/evidence) |
| `HUMAN_ADJUDICATION_PENDING` | LIFECYCLE | HITL queued |
| `HUMAN_ADJUDICATION_COMPLETE` | LIFECYCLE | HITL resolved |
| `DEGRADED_STATE_ENTERED` | LIFECYCLE | CR-091 |
| `DEGRADED_STATE_RECOVERED` | LIFECYCLE | CR-101 |
| `CONTINUATION_INTEGRITY_CHECK` | LIFECYCLE | CR-098 |
| `INCIDENT_DETECTED` | INCIDENT | Security/compliance incident |
| `CONTAINMENT_ACTION` | INCIDENT | Containment executed |
| `ANPD_NOTIFICATION_SENT` | COMPLIANCE | LGPD Art. 48 |
| `SUBJECT_NOTIFICATION_SENT` | COMPLIANCE | LGPD Art. 49 |
| `REMEDIATION_DEPLOYED` | INCIDENT | Fix deployed |
| `INCIDENT_CLOSED` | INCIDENT | Incident resolved |
| `PII_FILTER_APPLIED` | COMPLIANCE | PII redaction at PEP |
| `CREDENTIAL_DERIVED` | EXECUTION | Credential broker derivation |
| `POLICY_REGISTERED` | ADMINISTRATIVE | Policy artifact registered |
| `CONSTRAINT_REGISTERED` | ADMINISTRATIVE | Constraint registered |
| `INVARIANT_REGISTERED` | ADMINISTRATIVE | Invariant registered |
| `GOVERNANCE_CONFIGURATION_CHANGED` | ADMINISTRATIVE | Config updated |

---

## 5. Ordering Scope and Ledger Position

```json
{
  "ledger_position": {
    "sequence": 5,
    "predecessor_event_id": "uuid-of-sequence-4",
    "previous_event_digest": {
      "algorithm": "SHA-256",
      "value": "a1b2c3d4e5f6..."
    },
    "event_id": "same-as-ledger_event_id"
  }
}
```

**Rules:**
- Genesis event: sequence=0, no predecessor
- Non-genesis: sequence≥1, must have predecessor + previous digest
- Sequence strictly increasing within ordering_scope
- No duplicate sequences
- Timestamps NOT authoritative for ordering

---

## 6. Append-Only Guarantee

```python
class AppendOnlyLedger:
    def append(self, event: DS040Event) -> AppendResult:
        # 1. Validate DS-040 structure
        self.validate_ds040(event)
        
        # 2. Check predecessor binding
        if event.ledger_position.sequence > 0:
            pred = self.get_event(event.ledger_position.predecessor_event_id)
            if not pred:
                raise IntegrityError("Predecessor not found")
            if pred.integrity_protection.digest != event.ledger_position.previous_event_digest:
                raise IntegrityError("Predecessor digest mismatch")
        
        # 3. Check sequence uniqueness
        if self.sequence_exists(event.ledger_id, event.ordering_scope, event.ledger_position.sequence):
            raise IntegrityError("Duplicate sequence")
        
        # 4. Compute integrity protection
        event.integrity_protection = self.compute_integrity(event)
        
        # 5. Append (single transaction)
        with self.db.transaction():
            self.insert_event(event)
            self.update_chain_digest(event)
        
        return AppendResult(appended=True, ledger_position=event.ledger_position)
    
    def compute_integrity(self, event: DS040Event) -> IntegrityProtection:
        # Event content digest
        content = self.canonicalize(event)
        digest = sha256(content)
        
        # Chain digest (includes predecessor)
        if event.ledger_position.sequence == 0:
            chain_digest = digest
        else:
            pred = self.get_event(event.ledger_position.predecessor_event_id)
            chain_digest = sha256(pred.integrity_protection.chain_digest + digest)
        
        return IntegrityProtection(
            algorithm="SHA-256",
            digest=f"sha256:{digest.hex()}",
            chain_digest=f"sha256:{chain_digest.hex()}"
        )
```

---

## 7. Integrity and Provenance

```json
{
  "integrity_protection": {
    "algorithm": "SHA-256",
    "digest": "sha256:a1b2c3d4e5f6...",
    "chain_digest": "sha256:f6e5d4c3b2a1..."
  },
  "attribution": {
    "actor_id": "uuid",
    "actor_type": "SYSTEM",
    "role": "EXECUTOR"
  },
  "provenance": {
    "signer": "system-uuid",
    "kid": "ledger-signing-key-001",
    "alg": "ES256",
    "signed_at": "2026-08-18T10:00:00Z",
    "nonce": "base64",
    "scope": "GOVERNANCE_LEDGER_EVENT",
    "signature": "base64"
  }
}
```

---

## 8. Replay Material and Semantic Assertions

```json
{
  "replay_material": {
    "ordered_event_content": {},
    "governance_basis": {},
    "artifact_reference_set": [],
    "evidence_reference_set": [],
    "causality": {},
    "ledger_chain_digests": []
  },
  "semantic_assertions": {
    "append_only": true,
    "authoritative_ordering": true,
    "tenant_isolation": true,
    "reference_resolvability": true,
    "provenance_chain_continuity": true,
    "non_authorizing_semantics": true,
    "correction_by_subsequent_event": true
  }
}
```

---

## 9. Correction and Retention

```json
{
  "correction_record": {
    "corrected_event_id": "uuid",
    "correction_type": "EVIDENCE_UPDATE|ATTRIBUTION_CORRECTION",
    "correction_reason": "string",
    "corrected_at": "ISO8601",
    "corrected_by": "uuid"
  },
  "retention_record": {
    "retention_policy": "LIFETIME_PLUS_10_YEARS",
    "retention_until": "ISO8601",
    "legal_hold": false
  }
}
```

**Correction Rule**: Only by appending subsequent `LEDGER_CORRECTION_RECORDED` event. Original event preserved.

---

## 10. Deterministic Retrieval

```python
def retrieve_events(
    ledger_id: str,
    ordering_scope: str = None,
    sequence_start: int = 0,
    sequence_end: int = None,
    event_type: str = None,
    tenant_id: str = None,
    governance_domain_id: str = None
) -> List[DS040Event]:
    """
    Deterministic retrieval preserving authoritative sequence order.
    """
    query = "SELECT * FROM governance_ledger WHERE ledger_id = ?"
    params = [ledger_id]
    
    if ordering_scope:
        query += " AND ordering_scope = ?"
        params.append(ordering_scope)
    
    if sequence_start:
        query += " AND sequence >= ?"
        params.append(sequence_start)
    
    if sequence_end:
        query += " AND sequence <= ?"
        params.append(sequence_end)
    
    if event_type:
        query += " AND event_type = ?"
        params.append(event_type)
    
    if tenant_id:
        query += " AND tenant_id = ?"
        params.append(tenant_id)
    
    if governance_domain_id:
        query += " AND governance_domain_id = ?"
        params.append(governance_domain_id)
    
    query += " ORDER BY sequence ASC"
    
    return self.db.execute(query, params)
```

---

## 11. Isolation

```python
def verify_isolation(event: DS040Event) -> bool:
    """Verify tenant and governance-domain isolation."""
    # Event must have tenant_id and governance_domain_id
    if not event.tenant_id or not event.governance_domain_id:
        return False
    
    # All references must preserve isolation
    for ref in event.event_artifact_refs:
        if not ref.artifact_uri.startswith(f"agcp://{event.tenant_id}/{event.governance_domain_id}/"):
            return False
    
    for ref in event.evidence_binding.governance_evidence_refs:
        if not ref.startswith(f"agcp://{event.tenant_id}/{event.governance_domain_id}/"):
            return False
    
    return True
```

---

## 12. Conformance Verification

```bash
# Verify DS-040 compliance
python3 -m agcp.ledger verify-ds040 --ledger-id tenant-domain

# Verify chain integrity
python3 -m agcp.ledger verify-chain --ledger-id tenant-domain --ordering-scope proposal-uuid

# Verify isolation
python3 -m agcp.ledger verify-isolation --tenant-id tenant-uuid

# Verify retrieval determinism
python3 -m agcp.ledger test-retrieval --ledger-id tenant-domain --iterations 100

# Export for audit
python3 -m agcp.ledger export --ledger-id tenant-domain --format jsonl --output audit.jsonl
```