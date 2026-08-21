# LGPD Principles Checklist (Art. 6)

## Principles

| Principle | Article | Description | AGCP CR | Implementation | Status |
|-----------|---------|-------------|---------|----------------|--------|
| **Finalidade** | Art. 6.I | Purpose limitation - specific, explicit, legitimate | CR-036, CR-037, CR-038 | Proposal intent/target/effect binding | ☐ |
| **Adequação** | Art. 6.II | Compatibility with informed purposes | CR-036, CR-037 | Intent binding prevents scope creep | ☐ |
| **Necessidade** | Art. 6.III | Data minimization - limited to necessary | CR-036, CR-037, CR-119 | PII filter + proposal minimal fields | ☐ |
| **Livre Acesso** | Art. 6.IV | Free access to data and processing info | CR-010, CR-085 | GET authorized + decision reconstructable | ☐ |
| **Qualidade dos Dados** | Art. 6.V | Accuracy, clarity, relevance, updated | CR-062, CR-064 | Evidence integrity + canonical state | ☐ |
| **Transparência** | Art. 6.VI | Clear, precise, accessible information | CR-010, CR-085, CR-086 | Transparency metadata in receipts | ☐ |
| **Segurança** | Art. 6.VII | Technical/admin measures for protection | CR-119, CR-120, CR-121 | PEP enforcement + no bypass | ☐ |
| **Prevenção** | Art. 6.VIII | Prevent damage from processing | CR-003, CR-031, CR-032, CR-033 | Invariants + risk tiers + blink radius | ☐ |
| **Não Discriminação** | Art. 6.IX | No discriminatory processing | CR-079, CR-080, CR-087 | Fairness monitoring + structural refusal | ☐ |
| **Responsabilização** | Art. 6.X | Accountability for compliance | CR-040, CR-044, CR-065 | Authority lineage + signer identity | ☐ |

---

## Compliance Verification

```yaml
principles_verification:
  finalidade:
    check: "proposal_intent_matches_processing_purpose"
    agcp_cr: "CR-036"
    evidence: "proposal_intent_field"
  
  adequacao:
    check: "processing_compatible_with_disclosed_purpose"
    agcp_cr: "CR-037"
    evidence: "target_resource_matches_purpose"
  
  necessidade:
    check: "pii_filter_reduces_to_minimum"
    agcp_cr: "CR-119, CR-120"
    evidence: "pii_filter_log"
  
  livre_acesso:
    check: "governance_evidence_accessible"
    agcp_cr: "CR-010, CR-085"
    evidence: "GET_governance_evidence_endpoint"
  
  qualidade:
    check: "canonical_state_accurate_and_current"
    agcp_cr: "CR-048, CR-049, CR-050"
    evidence: "state_qualification_result"
  
  transparencia:
    check: "decision_explanation_provided"
    agcp_cr: "CR-085, CR-086"
    evidence: "decision_explanation_format"
  
  seguranca:
    check: "pep_enforces_all_paths"
    agcp_cr: "CR-121"
    evidence: "pep_audit_log"
  
  prevencao:
    check: "invariants_prevent_harm"
    agcp_cr: "CR-003, CR-031"
    evidence: "invariant_evaluation_results"
  
  nao_discriminacao:
    check: "fairness_metrics_within_threshold"
    agcp_cr: "CR-079, CR-080, CR-087"
    evidence: "fairness_assessment_evidence"
  
  responsabilizacao:
    check: "authority_lineage_complete"
    agcp_cr: "CR-040, CR-044, CR-065"
    evidence: "governance_approval_artifact"
```

---

## Automated Checks

```bash
# Run all principles checks
python3 -m agcp.lgpd principles-check --tenant-id tenant-uuid --model-id uuid

# Individual principle
python3 -m agcp.lgpd principle finalidade --proposal-id uuid
python3 -m agcp.lgpd principle necessidade --model-id uuid
python3 -m agcp.lgpd principle seguranca --pep-config pep.yaml
```