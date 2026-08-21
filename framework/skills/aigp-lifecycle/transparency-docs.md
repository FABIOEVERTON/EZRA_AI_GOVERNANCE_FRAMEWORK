# AIGP Transparency Documentation

## AIGP Domain: Transparency

Maps to AGCP: GET Authorized (CR-010), Decision Reconstructable (CR-085), Receipt Reproduces (CR-086), Evidence Integrity (CR-062, CR-064, CR-066, CR-067)

---

## Transparency Artifacts

| Artifact | Purpose | AGCP CR | Runtime Generation |
|----------|---------|---------|-------------------|
| **Model Card** | Document model capabilities, limitations, intended use | CR-010, CR-085 | Generated at deployment gate |
| **System Card** | Document system architecture, data flows, governance | CR-010, CR-085, CR-086 | Generated at deployment gate |
| **Decision Explanation** | Explain individual governance decisions | CR-085, CR-086 | Generated per decision |
| **Governance Receipt** | Receipt for every authorized action | CR-085, CR-086 | Generated at commit boundary |
| **Audit Trail** | Complete reconstructable history | CR-082, CR-085, CR-086 | Continuous via ledger |

---

## Model Card Template (AGCP-Aligned)

```yaml
model_card:
  model_identity:
    name: ""
    version: ""
    provider: ""
    date: ""
    agcp_conformance: "L4"
  
  intended_use:
    primary_use_cases: []
    out_of_scope: []
    governance_domain: ""
  
  training_data:
    sources: []
    size: ""
    preprocessing: ""
    copyright_compliance: true
    data_digest: "sha256:..."
  
  evaluation:
    benchmarks: []
    fairness_metrics: {}
    robustness_tests: []
    governance_tests: []
  
  limitations:
    known_biases: []
    failure_modes: []
    governance_constraints: []
  
  governance:
    risk_tier: "high|medium|low"
    hitl_required: true
    invariants: []
    blink_radius: {}
    ledger_integration: true
  
  transparency:
    decision_explanation_format: "structured"
    receipt_format: "DS-026"
    audit_trail_access: "GET /agcp/v2/governance-evidence/{id}"
```

---

## System Card Template

```yaml
system_card:
  system_identity:
    name: ""
    version: ""
    components: []
    governance_domain: ""
  
  architecture:
    diagram: "mermaid|plantuml"
    data_flows: []
    trust_boundaries: []
  
  governance_integration:
    control_plane: "ezra-control-plane"
    agcp_version: "v2.0.8"
    conformance_level: "L4"
    interfaces:
      - IF-001: "HTTP /agcp/v2"
      - IF-002: "PEC (OPA/Rego)"
    ledger: "DS-040 append-only"
    provenance: "Detached signatures ES256"
  
  risk_management:
    risk_tiers: ["critical", "high", "medium", "low"]
    invariants: []
    blink_radius: {}
    hitl_gates: []
  
  monitoring:
    observability: "S22"
    fairness: "S14"
    audit: "S08"
    alerting: []
  
  incident_response:
    structural_refusal: "CR-053"
    escalation: "CR-002, CR-012-018"
    recovery: "CR-101"
```

---

## Decision Explanation Format

Every governance decision produces structured explanation:

```json
{
  "decision_explanation": {
    "proposal_id": "uuid",
    "decision": "AUTHORIZED|DENIED|STRUCTURAL_REFUSAL|PENDING_HITL|DEFERRED",
    "governance_basis": {
      "policies_evaluated": ["policy-uuid"],
      "constraints_evaluated": ["constraint-uuid"],
      "invariants_evaluated": ["invariant-uuid"],
      "exceptions_considered": ["exception-uuid"]
    },
    "evaluation_trace": [
      {
        "stage": "PROPOSAL_QUALIFICATION",
        "result": "QUALIFIED",
        "checks": ["CR-036", "CR-037", "CR-038", "CR-004", "CR-005"]
      },
      {
        "stage": "POLICY_EVALUATION",
        "result": "AUTHORIZED",
        "pem_result": "ALLOW",
        "constraints_satisfied": true,
        "invariants_satisfied": true
      },
      {
        "stage": "HITL_ESCALATION",
        "result": "APPROVED",
        "quorum_met": true,
        "approvers": ["human-uuid"]
      },
      {
        "stage": "COMMIT_BOUNDARY",
        "result": "COMMITTED",
        "authorization_ref": "auth-uuid",
        "canonical_state_qualified": true
      }
    ],
    "canonical_state_snapshot": {
      "state_digest": "sha256:...",
      "ledger_position": 42,
      "qualified": true
    },
    "evidence_refs": ["evidence-uuid"],
    "receipt_ref": "receipt-uuid",
    "replay_instructions": "GET /agcp/v2/governance-evidence/{evidence-id}"
  }
}
```

---

## Governance Receipt (DS-026 Aligned)

```json
{
  "governance_receipt": {
    "receipt_id": "uuid",
    "receipt_version": "2.0.8",
    "proposal_id": "uuid",
    "authorization_id": "uuid",
    "decision": "AUTHORIZED",
    "ledger_event_id": "uuid",
    "ledger_position": 42,
    "canonical_state_digest": "sha256:...",
    "evidence_digests": ["sha256:..."],
    "transparency_metadata": {
      "ai_disclosed": true,
      "content_labeled": true,
      "subject_notified": true
    },
    "replay_verification": {
      "replay_hash": "sha256:...",
      "verification_status": "VERIFIED"
    },
    "timestamp": "2026-08-18T10:00:00Z"
  }
}
```

---

## Audit Trail Access

```bash
# Get decision explanation
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.agcp.ai/agcp/v2/governance-evidence/{evidence-id}"

# Get full audit trail for proposal
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.agcp.ai/agcp/v2/proposals/{proposal-id}?include=full_trace"

# Verify receipt
python3 -m agcp.receipt verify --receipt-id uuid --ledger-id tenant-domain
```

---

## Verification

```bash
# Generate model card
python3 -m agcp.transparency model-card --model-id uuid --output model-card.yaml

# Generate system card
python3 -m agcp.transparency system-card --system-id uuid --output system-card.yaml

# Verify decision reconstructability
python3 -m agcp.replay verify --proposal-id uuid --ledger-id tenant-domain
```