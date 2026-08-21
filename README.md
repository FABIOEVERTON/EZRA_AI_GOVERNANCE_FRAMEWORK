# ezra_ai_governance_framework

![Framework Self-Validation](https://github.com/FABIOEVERTON/EZRA_AI_GOVERNANCE_FRAMEWORK/actions/workflows/ci.yml/badge.svg)
![Tests](https://img.shields.io/badge/tests-13%20passing-brightgreen)

**Deterministic Runtime Governance Framework for AI Agents — AGCP v2.0.8 L4 Conformant**

This framework provides the governance foundation for the Ezra AI agent ecosystem. It maps regulatory requirements (NIST AI RMF, EU AI Act, AIGP, LGPD) to AGCP (Agent Governance Control Plane) conformance requirements and implements them as enforceable runtime controls at the commit boundary.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    REGULATORY LAYER                             │
│  NIST AI RMF │ EU AI Act │ AIGP (IAPP) │ LGPD (Lei 13.709/2018) │
└─────────────────────────────────────────────────────────────────┘
                              ↓ mapping (framework/mappings/)
┌─────────────────────────────────────────────────────────────────┐
│                      SKILLS LAYER                               │
│  nist-ai-rmf-mapping │ eu-ai-act-compliance │ aigp-lifecycle  │
│  lgpd-operational                                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓ enforcement (AGCP Runtime)
┌─────────────────────────────────────────────────────────────────┐
│                      AGCP RUNTIME (L4)                          │
│  IF-001 HTTP Interface │ IF-002 PEC │ DS-040 Ledger │ Provenance │
└─────────────────────────────────────────────────────────────────┘
                              ↓ implementation
┌─────────────────────────────────────────────────────────────────┐
│                  EZRA CONTROL PLANE                             │
│  RGG Gate (GDF) │ Policy Engine (PEM) │ Ledger │ Credential Broker │
│  HITL Gates │ PEP Enforcement │ Sidecar Credential Isolation    │
└─────────────────────────────────────────────────────────────────┘
```

## Target Conformance

**AGCP v2.0.8 — Level L4 (Execution Authorization Control)**

| Level | Scope | Status |
|-------|-------|--------|
| L1 | Schema & Envelope Validation | ✅ Target |
| L2 | Ordered Governance Mediation | ✅ Target |
| L3 | Deterministic Governance | ✅ Target |
| L4 | Execution Authorization Control | ✅ Target |
| L5 | Multitenant Governance Isolation | 🔄 Future |

## Quick Start

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/FABIOEVERTON/ezra_ai_governance_framework.git

# Or update upstream references
./sync.sh

# Rebuild framework/ from upstream sources
./rebuild-framework.sh
```

## Validation & Evidence

This repository validates itself. Every push runs the structural validator, the test suite, and lint on GitHub Actions — and stamps every validated file with SHA-256 + UTC timestamp.

```bash
pip install -r requirements-dev.txt
bash scripts/run_evidence.sh                    # full suite -> evidence/YYYY-MM-DD_HHMMSS.log
python3 scripts/stamp_files.py --check          # detect files changed after last validation
```

- `evidence/` — dated execution logs + `validation_manifest.json` (per-file provenance)
- CI artifacts keep the log of every run; the manifest is committed back to `main` on each green build

See [docs/VALIDATION.md](docs/VALIDATION.md) for details.

## Structure

```
ezra_ai_governance_framework/
├── upstream/                    # Shallow clones of reference repos
├── framework/
│   ├── skills/                  # 4 governance skills (AGCP-mapped)
│   ├── mappings/                # Regulatory → AGCP CR mappings
│   ├── templates/               # Ready-to-use JSON/YAML templates
│   ├── conformance/             # L1-L4 test vectors
│   └── agcp-reference/          # AGCP specs offline
├── ezra-control-plane/          # Integration with Ezra Control Plane
└── docs/                        # Documentation
```

## Skills

| Skill | ID | Regulatory Source | AGCP CRs |
|-------|-----|-------------------|----------|
| nist-ai-rmf-mapping | S24 | NIST AI RMF (22 subcategories) | CR-001, CR-007, CR-011, CR-036-038, CR-083, CR-084, CR-088, CR-089 |
| eu-ai-act-compliance | S25 | EU AI Act (2024/1689) | CR-003, CR-019, CR-020, CR-062, CR-064, CR-119, CR-120, CR-121 |
| aigp-lifecycle | S26 | IAPP AIGP | CR-003, CR-031, CR-040, CR-044, CR-065, CR-083, CR-085, CR-086, CR-119, CR-121 |
| lgpd-operational | S27 | LGPD (Lei 13.709/2018) | CR-036, CR-037, CR-053, CR-054, CR-062, CR-064, CR-119, CR-121 |

## Templates

All templates conform to AGCP DS-040, DS-026, DS-045, and Provenance Wire Format specifications:

- `risk-assessment.yaml` — Risk assessment with AGCP CR mapping
- `conformity-checklist.yaml` — EU AI Act conformity checklist
- `audit-trail-format.json` — DS-040 compliant ledger entry
- `governance-approval-artifact.json` — DS-026 governance approval
- `proposal-submit-request.json` — DS-045 proposal submission
- `commit-boundary-request.json` — Commit boundary processing
- `evidence-binding.json` — Evidence binding structure
- `ledger-event.json` — DS-040 governance ledger event
- `provenance.json` — Detached signature format
- `content-digest.json` — SHA-256/BLAKE2B contract

## Conformance Testing

```bash
# Run L1-L4 test vectors
cd framework/conformance
python3 -m pytest test-vectors/ -v
```

## Documentation

- [Validation Guide](docs/VALIDATION.md) — how the framework validates itself, what each check means

## License

MIT License — see [LICENSE](LICENSE)

## References

- [AGCP Specification v2.0.8](https://github.com/jwillisSFT/agcp-spec)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [EU AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng)
- [IAPP AIGP](https://iapp.org/certify/aigp/)
- [LGPD](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/L13709.htm)