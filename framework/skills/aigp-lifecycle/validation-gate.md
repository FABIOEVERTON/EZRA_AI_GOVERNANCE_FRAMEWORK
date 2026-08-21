# AIGP Validation Gate

## Gate: Validation Treatment
**Phase**: Treat
**AGCP CRs**: CR-019, CR-020, CR-021, CR-079, CR-080
**Trigger**: Model ready for deployment, all assessments passed

---

## Purpose

Validate that the model can be deployed with proper governance controls: commit-bound authorization, HITL gates, and PEP enforcement.

---

## Input Requirements

```yaml
required_inputs:
  - model_artifact: "Validated model artifact"
  - canonical_state: "Qualified canonical state from development gate"
  - deployment_config: "Target environment, scaling, monitoring config"
  - hitl_configuration: "HITL gates per risk tier"
  - pep_configuration: "Policy Enforcement Point config"
  - blink_radius: "Damage cards for all credentials"
```

---

## Evaluation Criteria

| Criterion | Check | AGCP CR | Pass Condition |
|-----------|-------|---------|----------------|
| **Commit After Auth** | Operational realization only after auth | CR-019 | PEP enforces pre-execution auth |
| **No Exec Pending HITL** | No execution while HITL pending | CR-020 | PEP blocks pending HITL |
| **Rejected Never Exec** | Rejected actions never execute | CR-021 | PEP enforces structural refusal |
| **Authorized Commit** | Governance correctly admits admissible | CR-079 | GDF + PEP aligned |
| **Unauthorized Reject** | Governance correctly rejects inadmissible | CR-080 | GDF + PEP aligned |
| **HITL Gates** | Configured per risk tier | CR-002, CR-012-018 | High-risk = mandatory HITL |
| **Blink Radius** | Damage cards for all credentials | CR-119, CR-120 | All credentials scoped |

---

## HITL Configuration by Risk Tier

```yaml
hitl_configuration:
  high_risk:
    mandatory: true
    quorum_required: 2
    timeout_seconds: 300
    approvers: ["risk_owner", "executive"]
    escalation: "auto_reject_on_timeout"
  
  critical_risk:
    mandatory: true
    quorum_required: 3
    timeout_seconds: 60
    approvers: ["risk_owner", "executive", "legal"]
    escalation: "auto_reject_on_timeout"
  
  medium_risk:
    mandatory: false
    optional_review: true
    timeout_seconds: 3600
  
  low_risk:
    mandatory: false
    auto_authorized: true
```

---

## PEP Configuration

```yaml
pep_configuration:
  enforcement_mode: "strict"
  agcp_cr: "CR-119, CR-120, CR-121"
  checks:
    - authorization_reference_match: true
    - canonical_state_current: true
    - invariant_satisfaction: true
    - constraint_satisfaction: true
    - hitl_quorum_met: true
    - approval_not_expired: true
    - approval_signature_valid: true
  bypass_prevention:
    - no_direct_execution: true
    - all_paths_through_pep: true
    - credential_derivation_required: true
```

---

## Blink Radius (Damage Cards)

```yaml
blink_radius:
  credentials:
    - name: "database_write"
      effect_kind: "write"
      resources: ["db.production.*"]
      irreversible: false
      max_damage: "partial_data_corruption"
      risk_score: "medium"
      rate_limit: "100/min"
    
    - name: "database_delete"
      effect_kind: "delete"
      resources: ["db.production.*"]
      irreversible: true
      max_damage: "all_data_loss"
      risk_score: "critical"
      rate_limit: "10/hour"
      hitl_required: true
    
    - name: "api_payment"
      effect_kind: "transfer"
      resources: ["payment.gateway.*"]
      irreversible: true
      max_damage: "full_balance"
      risk_score: "critical"
      rate_limit: "5/min"
      hitl_required: true
      quorum: 2
    
    - name: "deployment_prod"
      effect_kind: "exec"
      resources: ["k8s.production.*"]
      irreversible: false
      max_damage: "service_downtime"
      risk_score: "high"
      rate_limit: "5/hour"
      hitl_required: true
```

---

## Decision Logic

```python
def evaluate_validation(model_artifact, deployment_config):
    # Commit-bound authorization (CR-019)
    if not deployment_config.pep.enforces_pre_execution_auth():
        return STRUCTURAL_REFUSAL("CR-019: No pre-execution authorization enforcement")
    
    # No execution pending HITL (CR-020)
    if deployment_config.pep.allows_exec_pending_hitl():
        return STRUCTURAL_REFUSAL("CR-020: Execution allowed while HITL pending")
    
    # Rejected never execute (CR-021)
    if not deployment_config.pep.enforces_structural_refusal():
        return STRUCTURAL_REFUSAL("CR-021: Rejected actions can execute")
    
    # HITL gates configured (CR-002, CR-012-018)
    if not hitl_gates_configured(deployment_config):
        return STRUCTURAL_REFUSAL("CR-002: HITL gates not configured")
    
    # PEP enforcement (CR-119, CR-120, CR-121)
    if not pep_enforcement_complete(deployment_config):
        return STRUCTURAL_REFUSAL("CR-119/120/121: PEP enforcement incomplete")
    
    # Blink radius defined (CR-119, CR-120)
    if not blink_radius_complete(deployment_config):
        return STRUCTURAL_REFUSAL("CR-119/120: Blink radius incomplete")
    
    return AUTHORIZED(
        hitl_config=deployment_config.hitl,
        pep_config=deployment_config.pep,
        blink_radius=deployment_config.blink_radius
    )
```

---

## Output

```yaml
gate_output:
  decision: "AUTHORIZED|STRUCTURAL_REFUSAL"
  hitl_configuration: {}
  pep_configuration: {}
  blink_radius: {}
  next_gate: "deployment"
  ledger_event: "GOVERNANCE_DECISION"
  evidence:
    - hitl_config_hash: "sha256:..."
    - pep_config_hash: "sha256:..."
    - blink_radius_hash: "sha256:..."
```

---

## Verification

```bash
# Test validation gate
python3 -m agcp.lifecycle gate validation --model-id uuid --config deployment.yaml

# Verify PEP config
python3 -m agcp.pep validate --config pep.yaml

# Verify blink radius
python3 -m agcp.blink verify --credentials credentials.yaml
```