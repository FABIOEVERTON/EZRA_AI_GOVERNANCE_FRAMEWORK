#!/usr/bin/env python3
# validate_framework.py — Validate framework structure and completeness

import os
import json
import csv
from pathlib import Path

FRAMEWORK_DIR = Path(__file__).parent.parent / "framework"
ERRORS = []
WARNINGS = []

def check_exists(path, description):
    if not path.exists():
        ERRORS.append(f"MISSING: {description} at {path}")
        return False
    return True

def check_file_not_empty(path, description):
    if path.exists() and path.stat().st_size == 0:
        WARNINGS.append(f"EMPTY: {description} at {path}")
        return False
    return True

def validate_skills():
    print("Validating skills...")
    skills = [
        "nist-ai-rmf-mapping",
        "eu-ai-act-compliance", 
        "aigp-lifecycle",
        "lgpd-operational"
    ]
    for skill in skills:
        skill_dir = FRAMEWORK_DIR / "skills" / skill
        check_exists(skill_dir / "SKILL.txt", f"Skill {skill} SKILL.txt")
        check_file_not_empty(skill_dir / "SKILL.txt", f"Skill {skill} SKILL.txt")

def validate_mappings():
    print("Validating mappings...")
    mappings = [
        "nist-to-agcp.csv",
        "eu-ai-act-to-agcp.csv",
        "aigp-to-agcp.csv",
        "lgpd-to-agcp.csv",
        "master-regulatory-to-agcp.csv"
    ]
    for mapping in mappings:
        path = FRAMEWORK_DIR / "mappings" / mapping
        check_exists(path, f"Mapping {mapping}")
        check_file_not_empty(path, f"Mapping {mapping}")
        # Validate CSV structure
        if path.exists():
            try:
                with open(path, 'r') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if len(rows) < 2:
                        WARNINGS.append(f"Mapping {mapping} has no data rows")
            except Exception as e:
                ERRORS.append(f"Mapping {mapping} invalid CSV: {e}")

def validate_templates():
    print("Validating templates...")
    templates = [
        "risk-assessment.yaml",
        "conformity-checklist.yaml",
        "audit-trail-format.json",
        "governance-approval-artifact.json",
        "proposal-submit-request.json",
        "commit-boundary-request.json",
        "evidence-binding.json",
        "ledger-event.json",
        "provenance.json",
        "content-digest.json"
    ]
    for template in templates:
        path = FRAMEWORK_DIR / "templates" / template
        check_exists(path, f"Template {template}")
        check_file_not_empty(path, f"Template {template}")
        # Validate JSON/YAML syntax
        if path.exists():
            try:
                if path.suffix == '.json':
                    with open(path) as f:
                        json.load(f)
                elif path.suffix in ['.yaml', '.yml']:
                    import yaml
                    with open(path) as f:
                        yaml.safe_load(f)
            except Exception as e:
                ERRORS.append(f"Template {template} invalid syntax: {e}")

def validate_agcp_reference():
    print("Validating AGCP reference...")
    refs = [
        "CR-requirements.csv",
        "IF-001-http-spec.md",
        "IF-002-pec-spec.md",
        "DS-040-ledger-event.md",
        "conformance-levels.md"
    ]
    for ref in refs:
        path = FRAMEWORK_DIR / "agcp-reference" / ref
        check_exists(path, f"AGCP Reference {ref}")
        check_file_not_empty(path, f"AGCP Reference {ref}")

def validate_conformance():
    print("Validating conformance test vectors...")
    levels = ["L1-schema-validation", "L2-ordered-mediation", "L3-deterministic", "L4-execution-auth"]
    for level in levels:
        level_dir = FRAMEWORK_DIR / "conformance" / level
        check_exists(level_dir, f"Conformance level {level}")

def validate_ezra_control_plane():
    print("Validating ezra-control-plane integration...")
    files = [
        "SPEC.md",
        "architecture-agcp.md",
        "policy-evaluation-contract.md",
        "commit-boundary-spec.md",
        "ledger-spec.md",
        "provenance-spec.md",
        "canonical-state.md",
        "gaps-analysis.md"
    ]
    for f in files:
        path = FRAMEWORK_DIR.parent / "ezra-control-plane" / f
        check_exists(path, f"Ezra Control Plane {f}")
        check_file_not_empty(path, f"Ezra Control Plane {f}")

def main():
    print("=== Framework Validation ===\n")
    
    validate_skills()
    validate_mappings()
    validate_templates()
    validate_agcp_reference()
    validate_conformance()
    validate_ezra_control_plane()
    
    print(f"\n=== Results ===")
    print(f"Errors: {len(ERRORS)}")
    print(f"Warnings: {len(WARNINGS)}")
    
    if ERRORS:
        print("\nERRORS:")
        for e in ERRORS:
            print(f"  - {e}")
    
    if WARNINGS:
        print("\nWARNINGS:")
        for w in WARNINGS:
            print(f"  - {w}")
    
    if not ERRORS and not WARNINGS:
        print("\n✅ All validations passed!")
        return 0
    elif not ERRORS:
        print("\n⚠️  Valid with warnings")
        return 0
    else:
        print("\n❌ Validation failed")
        return 1

if __name__ == "__main__":
    exit(main())