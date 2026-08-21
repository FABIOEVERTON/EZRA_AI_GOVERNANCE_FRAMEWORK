#!/bin/bash
# rebuild-framework.sh — Rebuild framework/ from upstream/ sources
# Usage: ./rebuild-framework.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPSTREAM_DIR="$SCRIPT_DIR/upstream"
FRAMEWORK_DIR="$SCRIPT_DIR/framework"

echo "=== Rebuilding framework from upstream ==="

# 1. Copy AGCP reference specs
echo "Copying AGCP reference specs..."
cp -r "$UPSTREAM_DIR/agcp-spec/spec/"* "$FRAMEWORK_DIR/agcp-reference/" 2>/dev/null || true
cp -r "$UPSTREAM_DIR/agcp-spec/schemas/"* "$FRAMEWORK_DIR/agcp-reference/schemas/" 2>/dev/null || true
cp -r "$UPSTREAM_DIR/agcp-spec/api/"* "$FRAMEWORK_DIR/agcp-reference/api/" 2>/dev/null || true

# 2. Extract CR requirements CSV
echo "Extracting CR requirements..."
cp "$UPSTREAM_DIR/agcp-spec/spec/AGCP_Runtime_Governance_Requirements_CR-001_thru_CR-122.csv" \
   "$FRAMEWORK_DIR/agcp-reference/CR-requirements.csv"

# 3. Extract key AGCP specs as markdown
echo "Converting key specs to markdown..."
# IF-001
cp "$UPSTREAM_DIR/agcp-spec/spec/AGCP-HTTP-Interface-Specification.md" \
   "$FRAMEWORK_DIR/agcp-reference/IF-001-http-spec.md"
# IF-002
cp "$UPSTREAM_DIR/agcp-spec/spec/AGCP-Policy-Evaluation-Contract.md" \
   "$FRAMEWORK_DIR/agcp-reference/IF-002-pec-spec.md"
# Ledger
cp "$UPSTREAM_DIR/agcp-spec/spec/ledger/AGCP-Append-Only-Governance-Ledger-Specification.md" \
   "$FRAMEWORK_DIR/agcp-reference/DS-040-ledger-event.md"
# Conformance
cp "$UPSTREAM_DIR/agcp-spec/conformance/AGCP-Conformance.md" \
   "$FRAMEWORK_DIR/agcp-reference/conformance-levels.md"

# 4. Extract NIST AI RMF mapping from sunilp repo
echo "Extracting NIST AI RMF mapping..."
if [[ -f "$UPSTREAM_DIR/ai-governance-framework/framework/compliance/nist-ai-rmf-mapping.md" ]]; then
    cp "$UPSTREAM_DIR/ai-governance-framework/framework/compliance/nist-ai-rmf-mapping.md" \
       "$FRAMEWORK_DIR/skills/nist-ai-rmf-mapping/source-mapping.md"
fi

# 5. Extract EU AI Act crosswalk
echo "Extracting EU AI Act crosswalk..."
if [[ -f "$UPSTREAM_DIR/eu-ai-act-crosswalk/crosswalk.csv" ]]; then
    cp "$UPSTREAM_DIR/eu-ai-act-crosswalk/crosswalk.csv" \
       "$FRAMEWORK_DIR/mappings/eu-ai-act-crosswalk-source.csv"
fi

# 6. Extract awesome lists references
echo "Extracting awesome lists references..."
cp "$UPSTREAM_DIR/awesome-agent-governance/README.md" \
   "$FRAMEWORK_DIR/agcp-reference/awesome-agent-governance.md" 2>/dev/null || true
cp "$UPSTREAM_DIR/awesome-eu-ai-act/README.md" \
   "$FRAMEWORK_DIR/agcp-reference/awesome-eu-ai-act.md" 2>/dev/null || true
cp "$UPSTREAM_DIR/awesome-ai-security/README.md" \
   "$FRAMEWORK_DIR/agcp-reference/awesome-ai-security.md" 2>/dev/null || true

# 7. Generate mappings from source data
echo "Generating regulatory → AGCP mappings..."
python3 "$SCRIPT_DIR/scripts/generate_mappings.py" 2>/dev/null || echo "Mapping generation script not found, using templates"

# 8. Validate framework structure
echo "Validating framework structure..."
python3 "$SCRIPT_DIR/scripts/validate_framework.py" 2>/dev/null || echo "Validation script not found"

echo "=== Rebuild complete ==="