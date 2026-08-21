"""Tests for scripts/validate_framework.py against synthetic framework trees."""

import validate_framework as vf


def _patch(monkeypatch, fw_dir):
    monkeypatch.setattr(vf, "FRAMEWORK_DIR", fw_dir)
    monkeypatch.setattr(vf, "ERRORS", [])
    monkeypatch.setattr(vf, "WARNINGS", [])


def test_valid_tree_passes(valid_framework, monkeypatch, capsys):
    _patch(monkeypatch, valid_framework)
    assert vf.main() == 0
    out = capsys.readouterr().out
    assert "All validations passed" in out


def test_missing_skill_file_is_error(valid_framework, monkeypatch):
    (valid_framework / "skills" / "aigp-lifecycle" / "SKILL.txt").unlink()
    _patch(monkeypatch, valid_framework)
    assert vf.main() == 1
    assert any("MISSING" in e and "aigp-lifecycle" in e for e in vf.ERRORS)


def test_empty_mapping_is_warning(valid_framework, monkeypatch):
    (valid_framework / "mappings" / "nist-to-agcp.csv").write_text("", encoding="utf-8")
    _patch(monkeypatch, valid_framework)
    assert vf.main() == 0
    assert any("EMPTY" in w and "nist-to-agcp.csv" in w for w in vf.WARNINGS)


def test_mapping_without_data_rows_warns(valid_framework, monkeypatch):
    (valid_framework / "mappings" / "lgpd-to-agcp.csv").write_text("col1,col2\n", encoding="utf-8")
    _patch(monkeypatch, valid_framework)
    assert vf.main() == 0
    assert any("no data rows" in w and "lgpd-to-agcp.csv" in w for w in vf.WARNINGS)


def test_invalid_yaml_template_fails_validation(valid_framework, monkeypatch):
    (valid_framework / "templates" / "risk-assessment.yaml").write_text(
        "# broken\n```yaml\nrisk:\n  - [unclosed\n", encoding="utf-8"
    )
    _patch(monkeypatch, valid_framework)
    assert vf.main() == 1
    assert any("invalid syntax" in e and "risk-assessment.yaml" in e for e in vf.ERRORS)


def test_invalid_json_template_fails_validation(valid_framework, monkeypatch):
    (valid_framework / "templates" / "ledger-event.json").write_text("{not json", encoding="utf-8")
    _patch(monkeypatch, valid_framework)
    assert vf.main() == 1
    assert any("invalid syntax" in e and "ledger-event.json" in e for e in vf.ERRORS)


def test_real_repo_passes_validation():
    """The committed framework tree must pass its own validator (exit 0)."""
    import subprocess

    result = subprocess.run(
        ["python3", str(vf.Path(__file__).parent.parent / "scripts" / "validate_framework.py")],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
