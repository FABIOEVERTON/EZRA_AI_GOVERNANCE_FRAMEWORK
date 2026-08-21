#!/usr/bin/env python3
"""stamp_files.py — Per-file provenance stamps for validated framework content.

Generates evidence/validation_manifest.json with one entry per file:
{ path, sha256, validated_at (ISO-8601 UTC), run_id, result }

--check mode recomputes hashes and reports drift since last validation.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
EVIDENCE_DIR = REPO_ROOT / "evidence"
MANIFEST_PATH = EVIDENCE_DIR / "validation_manifest.json"
SCOPED_DIRS = ["framework", "scripts", "tests", "ezra-control-plane"]
EXCLUDED_PARTS = {"__pycache__", ".pytest_cache", "upstream", ".git"}
EXCLUDED_NAMES = {"validation_manifest.json"}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scoped_files():
    for d in SCOPED_DIRS:
        base = REPO_ROOT / d
        if not base.exists():
            continue
        for root, dirs, files in os.walk(base):
            dirs[:] = [x for x in dirs if x not in EXCLUDED_PARTS]
            for name in sorted(files):
                if name in EXCLUDED_NAMES or name.endswith(".pyc"):
                    continue
                yield Path(root) / name


def build_manifest(run_id: str) -> dict:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    entries = []
    for path in scoped_files():
        entries.append(
            {
                "path": str(path.relative_to(REPO_ROOT)),
                "sha256": sha256_of(path),
                "validated_at": now,
                "run_id": run_id,
                "result": "PASS",
            }
        )
    return {
        "manifest_version": 1,
        "generated_at": now,
        "run_id": run_id,
        "file_count": len(entries),
        "files": entries,
    }


def cmd_stamp(run_id: str) -> int:
    EVIDENCE_DIR.mkdir(exist_ok=True)
    manifest = build_manifest(run_id)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(f"Stamped {manifest['file_count']} files -> {MANIFEST_PATH.relative_to(REPO_ROOT)}")
    return 0


def cmd_check() -> int:
    if not MANIFEST_PATH.exists():
        print("FAIL: no manifest found. Run stamp mode first.")
        return 1
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    recorded = {e["path"]: e["sha256"] for e in manifest["files"]}
    current = {str(p.relative_to(REPO_ROOT)): sha256_of(p) for p in scoped_files()}
    drifted = sorted(p for p in current if p in recorded and current[p] != recorded[p])
    added = sorted(p for p in current if p not in recorded)
    removed = sorted(p for p in recorded if p not in current)
    if drifted or added or removed:
        for p in drifted:
            print(f"DRIFTED (changed after last validation): {p}")
        for p in added:
            print(f"UNSTAMPED (new file, never validated): {p}")
        for p in removed:
            print(f"REMOVED (stamped but gone): {p}")
        return 1
    print(f"OK: {len(current)} files match the last validation manifest.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify files against last manifest")
    parser.add_argument("--run-id", default=None, help="run identifier (defaults to UTC timestamp)")
    args = parser.parse_args()
    if args.check:
        return cmd_check()
    run_id = args.run_id or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return cmd_stamp(run_id)


if __name__ == "__main__":
    sys.exit(main())
