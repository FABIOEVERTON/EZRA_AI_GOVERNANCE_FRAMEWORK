# AIGP Development Gate

## Gate: Development Assessment
**Phase**: Assess
**AGCP CRs**: CR-032, CR-033, CR-048, CR-049, CR-050
**Trigger**: Model development complete, ready for validation

---

## Purpose

Validate that the developed model meets all assessment criteria and canonical state is established.

---

## Input Requirements

```yaml
required_inputs:
  - model_artifact: "Trained model with version"
  - training_data_digest: "sha256 of training data"
  - hyperparameters: "Complete hyperparameter set"
  - evaluation_results: "Benchmark + fairness + robustness results"
  - canonical_state_snapshot: "Authoritative state for this model version"
```

---

## Evaluation Criteria

| Criterion | Check | AGCP CR | Pass Condition |
|-----------|-------|---------|----------------|
| **Stale Authorization** | No stale auth after prior commit | CR-032 | Current canonical state used |
| **Divergent State** | Execution authority valid under current assumptions | CR-033 | Assumptions validated |
| **Canonical State Available** | Authoritative state for evaluation | CR-048 | State resolved |
| **Stale Canonical State** | Sufficiently current state | CR-049 | State freshness < threshold |
| **Conflicting Sources** | Single authoritative state | CR-050 | State unified |
| **Fairness Metrics** | Within thresholds | CR-079, CR-080 | All metrics pass |
| **Robustness** | Adversarial testing passed | CR-119, CR-120 | No critical vulnerabilities |
| **Security** | Penetration testing passed | CR-119, CR-120, CR-121 | No critical findings |

---

## Canonical State Establishment

```yaml
canonical_state:
  model_version: "v1.2.3"
  training_data_digest: "sha256:..."
  hyperparameters: {}
  evaluation_results:
    benchmarks: {}
    fairness: {}
    robustness: {}
    security: {}
  governance_metadata:
    risk_tier: "high"
    invariants: []
    constraints: []
    hitl_gates: []
  state_digest: "sha256:..."
  qualified: true
  qualified_at: "2026-08-18T10:00:00Z"
  qualified_by: "governance-decision-function"
```

---

## Decision Logic

```python
def evaluate_development(model_artifact, canonical_state):
    # Canonical state checks (CR-048, CR-049, CR-050)
    if not canonical_state.is_available():
        return STRUCTURAL_REFUSAL("CR-048: Canonical state unavailable")
    
    if canonical_state.is_stale(threshold_hours=24):
        return STRUCTURAL_REFUSAL("CR-049: Stale canonical state")
    
    if canonical_state.has_conflicting_sources():
        return STRUCTURAL_REFUSAL("CR-050: Conflicting canonical state sources")
    
    # Stale authorization (CR-032)
    if has_stale_authorization(model_artifact):
        return STRUCTURAL_REFUSAL("CR-032: Stale authorization after prior commit")
    
    # Divergent state (CR-033)
    if has_divergent_state_assumptions(model_artifact):
        return STRUCTURAL_REFUSAL("CR-033: Divergent state assumption conflict")
    
    # Fairness evaluation (CR-079, CR-080)
    if not fairness_metrics_pass(model_artifact):
        return STRUCTURAL_REFUSAL("CR-079/080: Fairness metrics below threshold")
    
    # Robustness (CR-119, CR-120)
    if not robustness_tests_pass(model_artifact):
        return STRUCTURAL_REFUSAL("CR-119/120: Robustness tests failed")
    
    return AUTHORIZED(canonical_state=canonical_state)
```

---

## Output

```yaml
gate_output:
  decision: "AUTHORIZED|STRUCTURAL_REFUSAL"
  canonical_state: "qualified"
  state_digest: "sha256:..."
  next_gate: "validation"
  ledger_event: "GOVERNANCE_DECISION"
  evidence:
    - canonical_state_hash: "sha256:..."
    - fairness_results_hash: "sha256:..."
    - robustness_results_hash: "sha256:..."
    - security_results_hash: "sha256:..."
```

---

## Verification

```bash
# Test development gate
python3 -m agcp.lifecycle gate development --model-id uuid --canonical-state state.json

# Verify canonical state
python3 -m agcp.canonical-state verify --model-id uuid --digest sha256:...
```