"""Tests for scripts/generate_mappings.py: determinism, schema and repo consistency."""

import csv
from pathlib import Path

import generate_mappings as gm

REPO_ROOT = Path(__file__).parent.parent
EXPECTED_FILES = {
    "nist-to-agcp.csv": ["NIST_Subcategory", "Description", "AGCP_CRs"],
    "eu-ai-act-to-agcp.csv": ["Article", "Title", "AGCP_CRs", "Risk_Tier"],
    "aigp-to-agcp.csv": ["Domain", "Subdomain", "AGCP_CRs"],
    "lgpd-to-agcp.csv": ["Article", "Requirement", "AGCP_CRs"],
    "master-regulatory-to-agcp.csv": ["Framework", "Reference", "Description", "AGCP_CRs"],
}


def test_generation_is_deterministic(tmp_path, monkeypatch):
    out_a, out_b = tmp_path / "a", tmp_path / "b"
    for out in (out_a, out_b):
        out.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(gm, "MAPPINGS_DIR", out)
        gm.main()
    for filename in EXPECTED_FILES:
        assert (out_a / filename).read_bytes() == (out_b / filename).read_bytes(), filename


def test_generated_files_match_repo_committed_csvs(tmp_path, monkeypatch):
    """Golden file check: generator output must equal the CSVs committed in the repo."""
    monkeypatch.setattr(gm, "MAPPINGS_DIR", tmp_path)
    gm.main()
    committed_dir = REPO_ROOT / "framework" / "mappings"
    for filename in EXPECTED_FILES:
        generated = (tmp_path / filename).read_bytes()
        committed = (committed_dir / filename).read_bytes()
        assert generated == committed, f"{filename} diverged from committed version"


def test_master_mapping_is_union_of_all_frameworks(tmp_path, monkeypatch):
    monkeypatch.setattr(gm, "MAPPINGS_DIR", tmp_path)
    gm.main()
    with open(tmp_path / "master-regulatory-to-agcp.csv", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    frameworks = {r["Framework"] for r in rows}
    assert frameworks == {"NIST AI RMF", "EU AI Act", "AIGP", "LGPD"}
    expected_total = (
        len(gm.NIST_TO_AGCP) + len(gm.EU_AI_ACT_TO_AGCP) + len(gm.AIGP_TO_AGCP) + len(gm.LGPD_TO_AGCP)
    )
    assert len(rows) == expected_total


def test_every_row_maps_to_at_least_one_cr(tmp_path, monkeypatch):
    monkeypatch.setattr(gm, "MAPPINGS_DIR", tmp_path)
    gm.main()
    for filename in EXPECTED_FILES:
        with open(tmp_path / filename, encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        assert rows, f"{filename} has no data rows"
        for row in rows:
            crs = row["AGCP_CRs"].strip()
            assert crs, f"{filename}: empty AGCP_CRs in {row}"
            for cr in crs.split(","):
                assert cr.strip().startswith("CR-"), f"{filename}: bad CR ref '{cr}'"


def test_headers_match_expected_schema(tmp_path, monkeypatch):
    monkeypatch.setattr(gm, "MAPPINGS_DIR", tmp_path)
    gm.main()
    for filename, headers in EXPECTED_FILES.items():
        with open(tmp_path / filename, encoding="utf-8") as f:
            reader = csv.reader(f)
            assert next(reader) == headers, filename


def test_validator_accepts_generator_output(valid_framework, tmp_path, monkeypatch):
    """Integration: a tree whose mappings come from the generator passes the validator."""
    mappings_dir = valid_framework / "mappings"
    for f in mappings_dir.iterdir():
        f.unlink()
    monkeypatch.setattr(gm, "MAPPINGS_DIR", mappings_dir)
    gm.main()
    import validate_framework as vf

    monkeypatch.setattr(vf, "FRAMEWORK_DIR", valid_framework)
    monkeypatch.setattr(vf, "ERRORS", [])
    monkeypatch.setattr(vf, "WARNINGS", [])
    assert vf.main() == 0
