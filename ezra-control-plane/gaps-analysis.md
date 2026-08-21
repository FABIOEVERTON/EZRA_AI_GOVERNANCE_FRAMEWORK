# ezra-control-plane — AGCP L4 Gaps Analysis

## Overview

This document identifies gaps between the current ezra-control-plane implementation and **AGCP v2.0.8 Level L4 (Execution Authorization Control)** conformance requirements.

**Status**: Living document
**AGCP Version**: v2.0.8
**Target Conformance**: L4
**Current Assessment**: ~90% L4 coverage

---

## Gap Summary

| Category | Total CRs | Implemented | Partial | Missing | Coverage |
|----------|-----------|-------------|---------|---------|----------|
| **L1 Schema & Envelope** | 8 | 8 | 0 | 0 | 100% |
| **L2 Ordered Mediation** | 15 | 14 | 1 | 0 | 93% |
| **L3 Deterministic** | 18 | 17 | 1 | 0 | 94% |
| **L4 Execution Auth** | 35 | 32 | 2 | 1 | 91% |
| **L5 Multitenant** | 10 | 0 | 0 | 10 | 0% |
| **TOTAL** | 86 | 71 | 4 | 11 | 83% |

---

## Detailed Gap Analysis

### L1 — Schema & Envelope Validation (100% ✅)

| CR | Requirement | Status | Notes |
|----|-------------|--------|-------|
| CR-004 | Schema validation failure | ✅ | JSON Schema on all endpoints |
| CR-005 | Provenance validation | ✅ | ES256 on all artifacts |
| CR-010 | GET authorized action | ✅ | `/agcp/v2/execution-authorizations/{id}` |
| CR-036 | Missing intent | ✅ | Proposal validation |
| CR-037 | Missing target | ✅ | Proposal validation |
| CR-038 | Missing effect | ✅ | Proposal validation |
| CR-039 | Expired proposal | ✅ | Validity period enforcement |
| CR-040 | Malformed delegation | ✅ | Delegation chain validation |

---

### L2 — Ordered Governance Mediation (93% ⚠️)

| CR | Requirement | Status | Gap |
|----|-------------|--------|-------|
| CR-001 | Submit → Authorized | ✅ | |
| CR-002 | Submit → Pending HITL | ✅ | |
| CR-003 | Submit → Rejected | ✅ | |
| CR-006 | Tenant inactive | ✅ | |
| CR-007 | Policy not found | ✅ | |
| CR-011 | Transient state not observable | ✅ | |
| CR-043 | Mission/task lineage | ✅ | |
| CR-044 | Broken delegation chain | ✅ | |
| CR-045 | Conflicting originating actor | ✅ | |
| CR-046 | Context overrides canonical | ✅ | |
| CR-047 | Provenance continuity | ✅ | |
| CR-081 | Valid lifecycle transitions | ✅ | |
| **CR-008** | **Idempotent replay** | ⚠️ | **Partial: Idempotency-Key header implemented, but replay verification not fully tested** |
| **CR-009** | **Idempotency conflict** | ⚠️ | **Partial: Conflict detection exists, edge cases untested** |

**Action Items:**
- [ ] Complete idempotency replay testing (1000 iterations)
- [ ] Test idempotency conflict edge cases (concurrent same key, different payloads)

---

### L3 — Deterministic Governance (94% ⚠️)

| CR | Requirement | Status | Gap |
|----|-------------|--------|-------|
| CR-034 | Concurrent authorization race | ✅ | Serialized ledger appends |
| CR-048 | Canonical state unavailable | ✅ | State qualification |
| CR-049 | Stale canonical state | ✅ | 300s freshness threshold |
| CR-050 | Conflicting canonical sources | ✅ | Single authoritative resolution |
| CR-051 | Telemetry vs canonical | ✅ | Canonical precedence enforced |
| CR-052 | Canonical-state hash mismatch | ✅ | SHA-256 chain verification |
| CR-076 | Same proposal+state+invariants=same decision | ✅ | Deterministic OPA |
| CR-077 | Same proposal across nodes | ✅ | Stateless GDF |
| CR-078 | Determinism under non-deterministic agent | ✅ | GDF independent |
| CR-082 | Derived state matches ledger | ✅ | State reconstruction |
| CR-083 | Canonical state and decision synchronized | ✅ | Decision references state digest |
| CR-085 | Decision fully reconstructable | ✅ | Replay material in DS-040 |
| CR-086 | Receipt reproduces decision | ✅ | Governance receipt |
| **CR-084** | **Commit uses latest canonical state** | ⚠️ | **Partial: Re-derivation at commit implemented, but not stress-tested under load** |

**Action Items:**
- [ ] Stress test CR-084 under high concurrency (1000+ concurrent commits)
- [ ] Verify canonical state freshness under load

---

### L4 — Execution Authorization Control (91% ⚠️)

| CR | Requirement | Status | Gap |
|----|-------------|--------|-------|
| CR-019 | Commit authorized action | ✅ | |
| CR-020 | Commit while pending HITL | ✅ | |
| CR-021 | Commit while rejected | ✅ | |
| CR-022 | Authorization reference mismatch | ✅ | |
| CR-023 | Replay commit after executed | ✅ | |
| CR-024 | Tenant suspended before commit | ✅ | |
| CR-025 | Tenant decommissioned | ✅ | |
| CR-031 | Dual authorized conflicting actions | ✅ | |
| CR-032 | Stale authorization after commit | ✅ | |
| CR-033 | Divergent state assumption | ✅ | |
| CR-035 | Canonical state changes during HITL | ✅ | |
| CR-053 | Structural refusal invariant | ✅ | |
| CR-054 | Structural refusal missing evidence | ✅ | |
| CR-055 | Structural refusal canonical conflict | ✅ | |
| CR-056 | Refusal record attribution | ✅ | |
| CR-057 | Refusal record replayable | ✅ | |
| CR-058 | Escalation required missing artifact | ✅ | |
| CR-059 | Escalation resolved to commit | ✅ | |
| CR-060 | Escalation resolved to refusal | ✅ | |
| CR-061 | Deferred authorization expires | ✅ | |
| CR-062 | Missing canonical-state reference | ✅ | |
| CR-063 | Missing invariant references | ✅ | |
| CR-064 | Missing evidence hashes | ✅ | |
| CR-065 | Invalid signer identity | ✅ | |
| CR-066 | Receipt replay hash mismatch | ✅ | |
| CR-067 | Evidence changes between proposal/commit | ✅ | |
| CR-068 | Evidence unavailable at commit | ✅ | |
| CR-069 | Evidence lineage gap across agents | ✅ | |
| CR-079 | Authorized actions commit | ✅ | |
| CR-080 | Unauthorized never commit | ✅ | |
| CR-087 | Inadmissible produce structural refusal | ✅ | |
| CR-088 | Refused actions never execute | ✅ | |
| CR-091 | Degraded governance state | ✅ | |
| CR-092 | DEGRADED non-terminal | ✅ | |
| CR-093 | Re-evaluation from DEGRADED | ✅ | |
| CR-096 | Authority re-derivation at commit | ✅ | |
| CR-098 | Continuation integrity preservation | ✅ | |
| CR-099 | Admissible path viability tracking | ✅ | |
| CR-100 | Degraded continuation detection | ✅ | |
| CR-101 | Continuation recovery support | ✅ | |
| CR-102 | Governance realization layer | ✅ | |
| CR-119 | Enforcement context availability | ✅ | |
| CR-120 | Enforcement decision integrity | ✅ | |
| CR-121 | Governance enforcement binding | ✅ | |
| CR-115 | Recursive authority containment | ✅ | |
| CR-118 | Autonomous coordination bounds | ✅ | |
| **CR-122** | **Risk-based re-evaluation** | ⚠️ | **Partial: Framework exists, but automated trigger on material changes not fully implemented** |

**Action Items:**
- [ ] Implement automated risk-based re-evaluation triggers (CR-122)
- [ ] Add material change detection (policy updates, credential rotation, canonical state changes)

---

### L5 — Multitenant Governance Isolation (0% ❌)

| CR | Requirement | Status | Gap |
|----|-------------|--------|-----|
| CR-026 | Cross-tenant GET | ❌ | Single-tenant deployment |
| CR-027 | Cross-tenant cosign | ❌ | Single-tenant deployment |
| CR-028 | Cross-tenant commit | ❌ | Single-tenant deployment |
| CR-029 | Cross-tenant policy resolution | ❌ | Single-tenant deployment |
| CR-030 | Cross-tenant ledger access | ❌ | Single-tenant deployment |
| CR-105 | Composite proposals | ❌ | Not required for single-agent |
| CR-106 | Governance dependency graph | ❌ | Not required |
| CR-107 | Composite admissibility re-eval | ❌ | Not required |
| CR-108 | Coupling classification | ❌ | Not required |
| CR-109 | Partial bind governance | ❌ | Not required |
| CR-116 | Cross-domain authority isolation | ❌ | Single governance domain |
| CR-089 | Implementation passes conformance suite | ❌ | Not tested against suite |
| CR-090 | Independent implementations equivalent | ❌ | Single implementation |

**Decision**: L5 gaps are **accepted** for current single-tenant, single-governance-domain deployment model. Will address when multi-tenancy is required.

---

## Non-CR Gaps

### Testing & Validation

| Gap | Priority | Effort | Status |
|-----|----------|--------|--------|
| AGCP Conformance Test Suite execution | High | 2 weeks | ❌ Not run |
| Determinism stress test (1000+ iterations) | High | 1 week | ❌ Not run |
| Concurrency stress test (1000+ concurrent) | High | 1 week | ❌ Not run |
| Chaos engineering (kill/restart during commit) | Medium | 1 week | ❌ Not run |
| Penetration testing (PEP bypass attempts) | High | 2 weeks | ❌ Not run |
| Formal verification of Rego policies | Medium | 2 weeks | ❌ Not run |

### Documentation

| Gap | Priority | Effort | Status |
|-----|----------|--------|--------|
| Runbook for incident response | Medium | 3 days | ❌ |
| Operational playbooks | Medium | 1 week | ❌ |
| Disaster recovery procedures | High | 1 week | ❌ |
| Capacity planning guide | Low | 3 days | ❌ |

### Operational

| Gap | Priority | Effort | Status |
|-----|----------|--------|--------|
| Key rotation automation | High | 1 week | ⚠️ Partial |
| Monitoring/alerting rules | High | 1 week | ❌ |
| Log aggregation | Medium | 3 days | ❌ |
| Backup/restore procedures | High | 1 week | ❌ |

---

## Remediation Plan

### Phase 1: Core L4 Completion (2 weeks)
- [ ] Complete CR-122 risk-based re-evaluation automation
- [ ] Complete idempotency testing (CR-008, CR-009)
- [ ] Stress test CR-084 under load
- [ ] Run AGCP Conformance Test Suite

### Phase 2: Operational Hardening (2 weeks)
- [ ] Key rotation automation
- [ ] Monitoring/alerting
- [ ] Penetration testing
- [ ] Chaos engineering

### Phase 3: Documentation & Runbooks (1 week)
- [ ] Incident response runbook
- [ ] Disaster recovery
- [ ] Operational playbooks

### Phase 4: L5 Decision (Future)
- [ ] Evaluate multi-tenancy requirements
- [ ] If needed: implement L5 CRs

---

## Conformance Claim Status

**Current Claim**: AGCP v2.0.8 L4 with noted gaps
**Gaps Documented**: Yes (this document)
**Test Evidence**: Partial (see test-results-L4.json)
**Independent Verification**: No

**Next Milestone**: Full L4 conformance claim with complete test evidence by 2026-09-01