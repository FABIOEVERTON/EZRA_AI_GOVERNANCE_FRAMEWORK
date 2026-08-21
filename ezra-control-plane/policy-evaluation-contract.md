# ezra-control-plane — Policy Evaluation Contract (IF-002) Implementation

## Overview

This document specifies how ezra-control-plane implements the **AGCP Policy Evaluation Contract (PEC) — IF-002 v2.0.8**.

**Status**: Normative
**Interface Identifier**: IF-002
**Contract Version**: 2.0.8
**AGCP Specification Release**: v2.0.8

---

## 1. Purpose

The Policy Evaluation Contract (PEC) defines the normative behavioral contract between the **Governance Decision Function (GDF)** and the **Policy Evaluation Module (PEM)**.

In ezra-control-plane:
- **GDF** = RGG Gate (core orchestration)
- **PEM** = OPA/Rego Policy Engine

---

## 2. Architectural Context

```
┌─────────────────────────────────────────────────────────────┐
│                    Governance Decision Function (GDF)       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Proposal    │  │ Canonical   │  │ Policy Evaluation   │  │
│  │ Qualification│──▶│ State       │──▶│ Module (PEM)        │  │
│  └─────────────┘  └─────────────┘  └──────────┬──────────┘  │
│                                               │              │
│                                               ▼              │
│                                    ┌─────────────────────┐  │
│                                    │ Policy Interaction  │  │
│                                    │ Resolution          │  │
│                                    └──────────┬──────────┘  │
│                                               │              │
│                                               ▼              │
│                                    ┌─────────────────────┐  │
│                                    │ Governance Outcome  │  │
│                                    │ Determination       │  │
│                                    └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Design Principles (PEC §3)

| Principle | ezra-control-plane Implementation |
|-----------|-----------------------------------|
| **Deterministic** | OPA evaluation with fixed inputs; no time, random, env vars |
| **Side-effect free** | PEM only returns decision; no state mutation |
| **Replayable** | Identical inputs → identical outputs; replay via ledger |
| **Tenant isolated** | `tenant_id` + `governance_domain_id` in all inputs |
| **Governance-domain isolated** | Policies scoped to governance domain |
| **Canonical State driven** | All evaluation against qualified canonical state |
| **Implementation independent** | OPA/Rego as PEM; could swap engine |

---

## 4. Required Inputs (PEC §5)

The PEM receives these inputs from GDF:

```json
{
  "qualified_proposal": {
    "proposal_id": "uuid",
    "intent": "string",
    "target": {"resource_type": "string", "resource_id": "string"},
    "effect": "read|write|delete|transfer|exec",
    "risk_tier": "critical|high|medium|low",
    "blink_radius": {...},
    "tenant_id": "uuid",
    "governance_domain_id": "uuid"
  },
  "canonical_state_reference": "agcp://tenant/domain/state/uuid",
  "governance_context": {
    "mission_task_lineage": ["uuid"],
    "delegation_chain": ["uuid"],
    "validity_period": {"valid_from": "ISO8601", "valid_until": "ISO8601"}
  },
  "applicable_governance_policy": "agcp://tenant/domain/policy/governance-policy",
  "resolved_constraints": ["agcp://tenant/domain/constraint/..."],
  "resolved_invariants": ["agcp://tenant/domain/invariant/..."],
  "resolved_exceptions": ["agcp://tenant/domain/exception/..."],
  "authority_lineage": ["agcp://tenant/domain/delegation/..."],
  "tenant_context": {"tenant_id": "uuid", "status": "active"},
  "governance_domain_context": {"domain_id": "uuid", "status": "active"},
  "governance_configuration_reference": "agcp://tenant/domain/config/current"
}
```

All inputs are deterministic and replayable (stored in ledger).

---

## 5. Determinism Requirements (PEC §6)

The PEM **SHALL NOT** depend upon:

| Prohibited Dependency | ezra-control-plane Enforcement |
|----------------------|--------------------------------|
| Current system time | No `time.now()` in Rego; timestamps from inputs |
| Random values | No `rand()` in Rego |
| Environment variables | No `os.getenv()` in Rego |
| Mutable global state | OPA stateless; state from inputs only |
| Network access | No `http.send()` in Rego |
| External side effects | No side effects in Rego |

**Verification**: Identical authoritative inputs produce identical outputs.

```bash
# Determinism test
python3 -m agcp.test determinism --pem opa --iterations 1000
```

---

## 6. Evaluation Responsibilities (PEC §7)

The PEM evaluates:

| Responsibility | Implementation |
|----------------|----------------|
| **Constraints** | OPA rules for `constraint_refs` |
| **Invariants** | OPA rules for `invariant_refs` (hard stops) |
| **Governance Approval** | HITL approval artifact validation (DS-026) |
| **Policy Interactions** | Constraint/invariant/exception precedence resolution |

---

## 7. Governance Outcomes (PEC §8)

The PEM returns one of these outcomes:

| Outcome | Condition | GDF Action |
|---------|-----------|------------|
| **Authorized** | All constraints/invariants satisfied, HITL quorum met | Proceed to execution authorization |
| **Denied** | Constraint/invariant violation, no HITL path | Structural refusal |
| **Structural Refusal** | Hard invariant violation, missing evidence | Immediate deny, ledger entry |
| **Pending Human Review** | Policy requires HITL, quorum not met | Queue HITL |
| **Deferred** | Deferred authorization, validity period | Queue for later |
| **Governed Re-evaluation Required** | Degraded state, risk change | Re-evaluation trigger |

---

## 8. Canonical State (PEC §9)

All evaluations performed against **authoritative Canonical State**:

```rego
# Canonical state is input, not derived during evaluation
canonical_state := input.canonical_state

# Non-authoritative observations rejected
telemetry_state := input.telemetry  # IGNORED for authorization
cached_state := input.cache         # IGNORED for authorization
```

---

## 8. Authority Lineage (PEC §10)

```rego
# Authority lineage preserved, not expanded
authority_lineage := input.authority_lineage

# Delegation chain validation
valid_delegation(chain) {
    chain[0].delegator == "human-authority"
    all_valid_signatures(chain)
    no_authority_expansion(chain)
}
```

---

## 9. Governance Evidence (PEC §11)

PEM produces evidence for:

| Evidence Type | Purpose |
|---------------|---------|
| **Deterministic replay** | Input/output hashes for replay verification |
| **Governance interpretation** | Which rules fired, why |
| **Traceability** | Rule IDs, constraint/invariant references |
| **Attribution** | Actor identity from inputs |
| **Integrity** | Input/output digests |

---

## 10. Side Effects (PEC §12)

PEM **SHALL NOT**:

| Prohibited Action | Enforcement |
|-------------------|-------------|
| Commit execution | GDF handles commit boundary |
| Modify Canonical State | Read-only input |
| Update governance configuration | Config from inputs only |
| Append Governance Evidence directly | GDF appends to ledger |
| Modify external systems | No network, no filesystem |

All side effects occur in GDF (RGG Gate), not PEM.

---

## 11. Deterministic Replay (PEC §13)

```bash
# Replay verification
python3 -m agcp.pem replay \
  --input-hash sha256:... \
  --output-hash sha256:... \
  --ledger-id tenant-domain \
  --sequence 42
```

Replay using identical authoritative inputs reproduces:
- Same policy interpretation
- Same governance outcome
- Same evidence production

---

## 12. Conformance (PEC §14)

Conformant implementation satisfies all applicable AGCP Runtime Governance Requirements and Normative Statements governing:
- Proposal Qualification
- Governance Decision Function
- Canonical State
- Governance Evidence
- Authority Lineage
- Deterministic replay

---

## 14. Security (PEC §15)

| Requirement | Implementation |
|-------------|----------------|
| Integrity-protect PEM | OPA bundle signed, version-controlled |
| Version control | Git + signed commits |
| Cryptographic verification | Bundle digest verified at load |

---

## 15. Versioning (PEC §16)

| Change Type | Version Increment |
|-------------|-------------------|
| Breaking interface | MAJOR |
| Backward-compatible additions | MINOR |
| Editorial clarifications | PATCH |

Current: **IF-002 v2.0.8** (AGCP v2.0.8 baseline)

---

## 16. OPA/Rego Implementation Details

### Policy Structure

```
policies/
├── governance-policy.rego      # Main policy entry point
├── constraints/
│   ├── rate_limits.rego
│   ├── resource_limits.rego
│   └── time_windows.rego
├── invariants/
│   ├── prohibited_practices.rego
│   ├── dual_auth_conflicts.rego
│   └── data_minimization.rego
├── exceptions/
│   ├── emergency_override.rego
│   └── maintenance_window.rego
├── hitl/
│   ├── quorum.rego
│   ├── expiry.rego
│   └── signature_verification.rego
└── helpers/
    ├── canonical_state.rego
    ├── authority_lineage.rego
    └── evidence.rego
```

### Main Policy Entry Point

```rego
# governance-policy.rego
package agcp.governance

import future.keywords.in
import future.keywords.if

# Main decision
decision := outcome {
    outcome := evaluate_proposal(input)
}

evaluate_proposal(input) = outcome {
    # 1. Proposal qualification (already done by GDF)
    qualified := input.qualified_proposal
    
    # 2. Canonical state qualification
    state_qualified := qualify_canonical_state(input.canonical_state_reference)
    
    # 3. Invariant evaluation (hard stops)
    invariant_result := evaluate_invariants(qualified, input.resolved_invariants)
    invariant_result.violated == false
    
    # 4. Constraint evaluation
    constraint_result := evaluate_constraints(qualified, input.resolved_constraints)
    constraint_result.satisfied == true
    
    # 5. Exception evaluation
    exception_result := evaluate_exceptions(qualified, input.resolved_exceptions)
    
    # 6. Governance approval / HITL
    approval_result := evaluate_approval(qualified, input.governance_approval)
    
    # 7. Policy interaction resolution
    outcome := resolve_interactions(
        invariant_result,
        constraint_result,
        exception_result,
        approval_result
    )
}

# Outcome types
outcome := "authorized" { ... }
outcome := "denied" { ... }
outcome := "structural_refusal" { ... }
outcome := "pending_human_review" { ... }
outcome := "deferred" { ... }
outcome := "governed_reevaluation_required" { ... }
```

---

## Verification

```bash
# Test PEC compliance
python3 -m agcp.pem test --pec-version 2.0.8 --engine opa

# Determinism test
python3 -m agcp.pem determinism --iterations 1000

# Replay test
python3 -m agcp.pem replay --proposal-id uuid --ledger-id tenant-domain
```