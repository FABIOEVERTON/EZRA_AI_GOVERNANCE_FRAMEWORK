# LGPD Data Subject Rights Procedures (Art. 18)

## 9 Rights + AGCP Runtime Implementation

| Right | Article | Description | AGCP CR | Runtime Procedure |
|-------|---------|-------------|---------|-------------------|
| **1. Confirmação e Acesso** | Art. 18.I | Confirm processing + access data | CR-010, CR-062 | GET /governance-evidence/{id} |
| **2. Correção** | Art. 18.II | Correct incomplete, inaccurate, outdated | CR-062, CR-064 | Submit correction proposal |
| **3. Anonimização/Bloqueio/Eliminação** | Art. 18.III | Anonymize, block, or delete unnecessary | CR-053, CR-054, CR-119 | Structural refusal + PII filter |
| **4. Portabilidade** | Art. 18.IV | Portable format to another provider | CR-010, CR-085 | Export receipts + evidence |
| **5. Eliminação** | Art. 18.V | Delete data processed with consent | CR-053, CR-054 | Structural refusal (retention policy) |
| **6. Informação Compartilhamento** | Art. 18.VI | Info about shared entities | CR-062, CR-063 | Evidence binding references |
| **7. Revogação Consentimento** | Art. 18.VII | Revoke consent | CR-005, CR-015 | Invalidate approvals |
| **8. Oposição** | Art. 18.VIII | Object to processing | CR-053, CR-054 | Structural refusal |
| **9. Revisão Decisões Automatizadas** | Art. 18.IX | Review automated decisions | CR-085, CR-086, CR-002 | Decision explanation + HITL |

---

## Procedure 1: Confirmation and Access (Art. 18.I)

```yaml
procedure_access:
  trigger: "data_subject_request_access"
  agcp_cr: "CR-010, CR-062"
  steps:
    - verify_identity: "data_subject_authentication"
    - locate_data: "query_governance_ledger + evidence_store"
    - compile_response: "proposal_history + decisions + evidence"
    - deliver: "secure_channel within 15 days"
  response_format:
    - processing_purposes: []
    - data_categories: []
    - recipients: []
    - retention_period: ""
    - rights_info: []
    - automated_decisions: []
    - international_transfers: []
  ledger_entry: "GOVERNANCE_EVIDENCE_ACCESS_REQUEST"
```

---

## Procedure 2: Correction (Art. 18.II)

```yaml
procedure_correction:
  trigger: "data_subject_request_correction"
  agcp_cr: "CR-062, CR-064"
  steps:
    - verify_identity: "data_subject_authentication"
    - validate_correction: "check_accuracy_completeness"
    - submit_proposal: "CORRECTION_PROPOSAL with evidence"
    - governance_evaluation: "GDF evaluates"
    - if_authorized: "apply_correction + ledger_entry"
    - notify_subject: "correction_applied"
  ledger_entry: "GOVERNANCE_DECISION + CORRECTION_APPLIED"
```

---

## Procedure 3: Anonymization/Blocking/Deletion (Art. 18.III)

```yaml
procedure_anonymization:
  trigger: "data_subject_request_anonymize|block|delete"
  agcp_cr: "CR-053, CR-054, CR-119"
  steps:
    - verify_identity: "data_subject_authentication"
    - check_legal_basis: "if consent -> can delete; if legal_obligation -> block"
    - if_eligible:
        - submit_proposal: "ANONYMIZATION_PROPOSAL"
        - governance_evaluation: "GDF evaluates"
        - if_authorized: "apply_anonymization + PII_filter_update"
    - else: "structural_refusal with rationale"
  retention_policy:
    - legal_obligation: "block_until_obligation_ends"
    - consent_only: "anonymize_or_delete"
  ledger_entry: "STRUCTURAL_REFUSAL|ANONYMIZATION_COMPLETE"
```

---

## Procedure 4: Portability (Art. 18.IV)

```yaml
procedure_portability:
  trigger: "data_subject_request_portability"
  agcp_cr: "CR-010, CR-085"
  steps:
    - verify_identity: "data_subject_authentication"
    - compile_data: "structured_format (JSON/CSV)"
    - include: "proposals + decisions + evidence + receipts"
    - deliver: "secure_download_link within 15 days"
  format:
    - proposals: []
    - governance_decisions: []
    - evidence: []
    - receipts: []
    - ledger_events: []
  ledger_entry: "GOVERNANCE_EVIDENCE_PORTABILITY_REQUEST"
```

---

## Procedure 5: Deletion (Art. 18.V)

```yaml
procedure_deletion:
  trigger: "data_subject_request_deletion"
  agcp_cr: "CR-053, CR-054"
  steps:
    - verify_identity: "data_subject_authentication"
    - check_legal_basis: "only if consent was sole basis"
    - if_eligible:
        - submit_proposal: "DELETION_PROPOSAL"
        - governance_evaluation: "GDF evaluates"
        - if_authorized: "delete_personal_data + retain_governance_records"
    - else: "structural_refusal with legal basis rationale"
  note: "Governance ledger records retained per Art. 16 LGPD"
  ledger_entry: "STRUCTURAL_REFUSAL|DELETION_COMPLETE"
```

---

## Procedure 6: Information on Sharing (Art. 18.VI)

```yaml
procedure_sharing_info:
  trigger: "data_subject_request_sharing_info"
  agcp_cr: "CR-062, CR-063"
  steps:
    - verify_identity: "data_subject_authentication"
    - query_evidence: "evidence_binding.governance_evidence_refs"
    - compile: "all entities with data access"
    - deliver: "list with purposes and legal bases"
  ledger_entry: "GOVERNANCE_EVIDENCE_SHARING_REQUEST"
```

---

## Procedure 7: Consent Revocation (Art. 18.VII)

```yaml
procedure_revocation:
  trigger: "data_subject_revoke_consent"
  agcp_cr: "CR-005, CR-015"
  steps:
    - verify_identity: "data_subject_authentication"
    - locate_consent: "consent_record in governance artifacts"
    - invalidate: "mark consent_revoked_at timestamp"
    - cascade: "invalidate dependent approvals (CR-015)"
    - notify: "processing_stopped_for_revoked_purposes"
  ledger_entry: "CONSENT_REVOKED + GOVERNANCE_APPROVAL_INVALIDATED"
```

---

## Procedure 8: Opposition (Art. 18.VIII)

```yaml
procedure_opposition:
  trigger: "data_subject_oppose_processing"
  agcp_cr: "CR-053, CR-054"
  steps:
    - verify_identity: "data_subject_authentication"
    - assess: "legitimate_interest vs rights (Art. 10 LGPD)"
    - if_rights_override:
        - submit_proposal: "OPPOSITION_PROPOSAL"
        - governance_evaluation: "GDF evaluates"
        - if_authorized: "stop_processing + structural_refusal_future"
    - else: "continue with rationale"
  ledger_entry: "STRUCTURAL_REFUSAL|OPPOSITION_UPHELD"
```

---

## Procedure 9: Automated Decision Review (Art. 18.IX)

```yaml
procedure_automated_review:
  trigger: "data_subject_request_review_automated_decision"
  agcp_cr: "CR-085, CR-086, CR-002"
  steps:
    - verify_identity: "data_subject_authentication"
    - retrieve_decision: "decision_explanation + receipt"
    - provide: "logic + significance + consequences"
    - offer_hitl: "human_review_if_requested"
    - if_hitl_requested: "escalate_to_human_reviewer"
  ledger_entry: "AUTOMATED_DECISION_REVIEW_REQUEST"
```

---

## Unified Request Handler

```yaml
unified_handler:
  endpoint: "POST /lgpd/rights-request"
  authentication: "data_subject_credentials"
  request_schema:
    right_type: "enum[access,correction,anonymization,portability,deletion,sharing,revocation,opposition,review]"
    data_subject_id: "uuid"
    details: "object"
    proof_of_identity: "string"
  response:
    request_id: "uuid"
    status: "received|processing|completed|refused"
    estimated_completion: "ISO8601"
    ledger_ref: "agcp://tenant/domain/ledger/uuid"
  sla_days: 15
```

---

## Verification

```bash
# Submit rights request
python3 -m agcp.lgpd rights-request --right access --subject-id uuid --identity-proof proof.pdf

# Check request status
python3 -m agcp.lgpd rights-status --request-id uuid

# Verify all procedures
python3 -m agcp.lgpd procedures-test --all
```