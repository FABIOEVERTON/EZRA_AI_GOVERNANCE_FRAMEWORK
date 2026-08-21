# AIGP Model Selection Gate

## Gate: Model Selection
**Phase**: Identify
**AGCP CRs**: CR-003, CR-031, CR-036, CR-037, CR-038
**Trigger**: New model proposal submitted

---

## Purpose

Validate that a proposed model meets governance requirements before any development resources are committed.

---

## Input Requirements

```yaml
required_inputs:
  - model_card: "Complete model card per transparency-docs.md"
  - risk_assessment: "Initial risk assessment per risk-mgmt-lifecycle.md"
  - intended_use: "Clear statement of intended use cases and out-of-scope"
  - legal_basis: "LGPD Art. 7 legal basis for any personal data processing"
  - governance_domain: "Assigned governance domain"
  - tenant_id: "Assigned tenant"
```

---

## Evaluation Criteria

| Criterion | Check | AGCP CR | Pass Condition |
|-----------|-------|---------|----------------|
| **Hard Invariants** | No prohibited practices (Art. 5 EU AI Act) | CR-003 | Zero violations |
| **Dual Authorization** | Conflicting actions prevented | CR-031 | No dual authorized conflicts |
| **Intent Declaration** | Proposal declares operational intent | CR-036 | Intent field populated |
| **Target Identification** | Proposal identifies target resource | CR-037 | Target field populated |
| **Effect Declaration** | Proposal declares intended effect | CR-038 | Effect field populated |
| **Risk Tier** | Risk tier assigned per EU AI Act | CR-007 | Tier ∈ {unacceptable, high, limited, minimal} |
| **Legal Basis** | LGPD Art. 7 basis for personal data | CR-006, CR-007 | Valid basis identified |

---

## Decision Logic

```python
def evaluate_model_selection(proposal):
    # Hard invariant check (CR-003)
    if violates_prohibited_practices(proposal):
        return STRUCTURAL_REFUSAL("CR-003: Prohibited practice detected")
    
    # Dual authorization check (CR-031)
    if has_dual_authorized_conflict(proposal):
        return STRUCTURAL_REFUSAL("CR-031: Dual authorized conflicting actions")
    
    # Proposal integrity (CR-036, CR-037, CR-038)
    if not proposal.has_intent() or not proposal.has_target() or not proposal.has_effect():
        return STRUCTURAL_REFUSAL("CR-036/037/038: Missing intent/target/effect")
    
    # Risk tier assignment (CR-007)
    risk_tier = assign_risk_tier(proposal)
    if risk_tier == "unacceptable":
        return STRUCTURAL_REFUSAL("CR-003: Unacceptable risk")
    
    # Legal basis (CR-006, CR-007)
    if proposal.processes_personal_data() and not proposal.has_legal_basis():
        return STRUCTURAL_REFUSAL("CR-006/007: No legal basis for personal data")
    
    return AUTHORIZED(risk_tier=risk_tier)
```

---

## Output

```yaml
gate_output:
  decision: "AUTHORIZED|STRUCTURAL_REFUSAL"
  risk_tier: "high|limited|minimal"
  assigned_invariants: []
  assigned_constraints: []
  hitl_required: true/false
  next_gate: "development"
  ledger_event: "GOVERNANCE_DECISION"
  evidence:
    - risk_assessment_hash: "sha256:..."
    - model_card_hash: "sha256:..."
    - legal_basis_hash: "sha256:..."
```

---

## Ledger Entry (DS-040)

```json
{
  "event_type": "GOVERNANCE_DECISION",
  "event_category": "LIFECYCLE",
  "event_subject": {
    "subject_type": "MODEL_PROPOSAL",
    "subject_id": "model-uuid"
  },
  "governance_basis": {
    "policy_refs": ["governance-policy"],
    "constraint_refs": ["risk-tier-assignment", "legal-basis"],
    "invariant_refs": ["prohibited-practices", "dual-auth-conflict"]
  },
  "decision": "AUTHORIZED",
  "risk_tier": "high",
  "next_gate": "development"
}
```

---

## Verification

```bash
# Test model selection gate
python3 -m agcp.lifecycle gate model_selection --proposal proposal.yaml

# Verify ledger entry
python3 -m agcp.ledger query --event-type GOVERNANCE_DECISION --subject-type MODEL_PROPOSAL
```