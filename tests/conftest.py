"""Shared fixtures: build a minimal valid framework tree in tmp_path."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

SKILLS = ["nist-ai-rmf-mapping", "eu-ai-act-compliance", "aigp-lifecycle", "lgpd-operational"]
MAPPINGS = [
    "nist-to-agcp.csv",
    "eu-ai-act-to-agcp.csv",
    "aigp-to-agcp.csv",
    "lgpd-to-agcp.csv",
    "master-regulatory-to-agcp.csv",
]
JSON_TEMPLATES = [
    "audit-trail-format.json",
    "governance-approval-artifact.json",
    "proposal-submit-request.json",
    "commit-boundary-request.json",
    "evidence-binding.json",
    "ledger-event.json",
    "provenance.json",
    "content-digest.json",
]
YAML_TEMPLATES = ["risk-assessment.yaml", "conformity-checklist.yaml"]
AGCP_REFS = [
    "CR-requirements.csv",
    "IF-001-http-spec.md",
    "IF-002-pec-spec.md",
    "DS-040-ledger-event.md",
    "conformance-levels.md",
]
CONFORMANCE_LEVELS = ["L1-schema-validation", "L2-ordered-mediation", "L3-deterministic", "L4-execution-auth"]
CONTROL_PLANE_FILES = [
    "SPEC.md",
    "architecture-agcp.md",
    "policy-evaluation-contract.md",
    "commit-boundary-spec.md",
    "ledger-spec.md",
    "provenance-spec.md",
    "canonical-state.md",
    "gaps-analysis.md",
]


def build_valid_framework(root: Path) -> Path:
    fw = root / "framework"
    for skill in SKILLS:
        d = fw / "skills" / skill
        d.mkdir(parents=True)
        (d / "SKILL.txt").write_text(f"skill: {skill}\n", encoding="utf-8")
    mappings = fw / "mappings"
    mappings.mkdir(parents=True)
    for m in MAPPINGS:
        (mappings / m).write_text("col1,col2\nval1,val2\n", encoding="utf-8")
    templates = fw / "templates"
    templates.mkdir(parents=True)
    for t in JSON_TEMPLATES:
        (templates / t).write_text('{"template": true}\n', encoding="utf-8")
    for t in YAML_TEMPLATES:
        (templates / t).write_text("template:\n  version: '1.0'\n", encoding="utf-8")
    refs = fw / "agcp-reference"
    refs.mkdir(parents=True)
    for r in AGCP_REFS:
        (refs / r).write_text(f"ref: {r}\n", encoding="utf-8")
    for level in CONFORMANCE_LEVELS:
        (fw / "conformance" / level).mkdir(parents=True)
    cp = root / "ezra-control-plane"
    cp.mkdir(parents=True)
    for f in CONTROL_PLANE_FILES:
        (cp / f).write_text(f"# {f}\n", encoding="utf-8")
    return fw


@pytest.fixture
def valid_framework(tmp_path):
    return build_valid_framework(tmp_path)
