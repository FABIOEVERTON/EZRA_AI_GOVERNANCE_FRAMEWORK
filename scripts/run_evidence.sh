#!/usr/bin/env bash
# run_evidence.sh — Run full validation suite and record dated evidence log.
# Usage: bash scripts/run_evidence.sh
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

EVIDENCE_DIR="evidence"
mkdir -p "$EVIDENCE_DIR"
STAMP="$(date -u +%Y-%m-%d_%H%M%S)"
LOG="$EVIDENCE_DIR/$STAMP.log"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"

declare -a STEP_NAMES=()
declare -a STEP_RESULTS=()

log() { echo "$@" | tee -a "$LOG"; }

run_step() {
    local name="$1"
    shift
    log ""
    log "=== STEP: $name ==="
    log "\$ $*"
    if "$@" >> "$LOG" 2>&1; then
        STEP_NAMES+=("$name"); STEP_RESULTS+=("PASS")
        log "--- $name: PASS (exit 0)"
        return 0
    else
        local code=$?
        STEP_NAMES+=("$name"); STEP_RESULTS+=("FAIL (exit $code)")
        log "--- $name: FAIL (exit $code)"
        return 1
    fi
}

: > "$LOG"
log "# EZRA AI Governance Framework — Evidence Run"
log "run_id:     $RUN_ID"
log "timestamp:  $(date -u +%Y-%m-%dT%H:%M:%SZ)"
log "python:     $(python3 --version 2>&1)"
log "git commit: $(git rev-parse HEAD 2>/dev/null || echo 'uncommitted')"
log "host:       $(uname -srm)"

FAILED=0
run_step "framework-validator" python3 scripts/validate_framework.py || FAILED=1
run_step "pytest"               python3 -m pytest tests/ -q             || FAILED=1
if command -v ruff >/dev/null 2>&1; then
    run_step "ruff" ruff check scripts/ tests/ || FAILED=1
elif python3 -m ruff --version >/dev/null 2>&1; then
    run_step "ruff" python3 -m ruff check scripts/ tests/ || FAILED=1
else
    log ""
    log "=== STEP: ruff === SKIPPED (ruff not installed)"
    STEP_NAMES+=("ruff"); STEP_RESULTS+=("SKIPPED")
fi

if [ "$FAILED" -eq 0 ]; then
    run_step "stamp-files" python3 scripts/stamp_files.py --run-id "$RUN_ID" || FAILED=1
else
    log ""
    log "Skipping file stamping: previous steps failed."
fi

log ""
log "================ SUMMARY ================"
for i in "${!STEP_NAMES[@]}"; do
    printf '%-22s %s\n' "${STEP_NAMES[$i]}" "${STEP_RESULTS[$i]}" | tee -a "$LOG"
done
log "========================================="
log "evidence log: $LOG"

exit "$FAILED"
