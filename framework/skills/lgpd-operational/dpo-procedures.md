# LGPD DPO (Data Protection Officer) Procedures (Art. 41)

## Legal Requirements

| Article | Requirement | AGCP CR |
|---------|-------------|---------|
| **Art. 41.I** | Designate DPO | CR-040, CR-044 |
| **Art. 41.II** | DPO contact public | CR-010, CR-062 |
| **Art. 41.III** | DPO independence | CR-113, CR-117 |
| **Art. 41.IV** | DPO tasks | CR-040, CR-044, CR-065 |

---

## DPO Designation

```yaml
dpo_designation:
  required: true
  agcp_cr: "CR-040, CR-044"
  
  dpo_profile:
    name: ""
    email: "dpo@organization.com"
    phone: ""
    qualifications:
      - legal_knowledge: true
      - technical_knowledge: true
      - lgpd_expertise: true
      - agcp_knowledge: true
  
  independence:
    - no_conflict_of_interest: true
    - direct_report_to_top_management: true
    - no_instructions_on_tasks: true
    - resources_provided: true
    agcp_cr: "CR-113, CR-117"
  
  public_contact:
    - website: true
    - privacy_policy: true
    - anpd_registration: true
    agcp_cr: "CR-010, CR-062"
```

---

## DPO Tasks (Art. 41.IV) → AGCP Mapping

| DPO Task | Description | AGCP CR | Runtime Implementation |
|----------|-------------|---------|------------------------|
| **Accept complaints** | Receive data subject requests | CR-010, CR-062 | Rights request handler |
| **Inform/advise** | Advise controller on obligations | CR-006, CR-007 | Governance policy updates |
| **Monitor compliance** | Monitor LGPD compliance | CR-083, CR-084 | Observability + audit |
| **Cooperate with ANPD** | Liaison with authority | CR-006, CR-007 | Incident response |
| **Training** | Staff training on data protection | CR-110, CR-111 | Training modules |
| **Records** | Maintain processing records | CR-062, CR-063 | Governance ledger |
| **DPIA** | Advise on impact assessments | CR-036, CR-037, CR-038 | PIA gate |
| **Prior consultation** | Consult ANPD if high risk | CR-002, CR-012-018 | HITL escalation |

---

## DPO Runtime Procedures

### 1. Complaints Handling (Art. 18 Rights)

```yaml
dpo_complaints:
  endpoint: "POST /dpo/complaints"
  authentication: "data_subject_credentials"
  sla_days: 15
  agcp_cr: "CR-010, CR-062"
  
  workflow:
    - receive: "complaint logged in ledger"
    - acknowledge: "auto-reply with reference"
    - assess: "categorize + prioritize"
    - investigate: "query ledger + evidence"
    - resolve: "correction/deletion/explanation"
    - respond: "formal response to subject"
    - close: "ledger entry COMPLAINT_RESOLVED"
  
  escalation:
    - if_complex: "escalate_to_legal"
    - if_systemic: "escalate_to_executive"
    - if_anpd_involved: "direct_anpd_channel"
```

### 2. Compliance Monitoring

```yaml
dpo_monitoring:
  schedule: "continuous"
  agcp_cr: "CR-083, CR-084"
  
  metrics:
    - rights_requests_volume: "daily"
    - rights_requests_sla_compliance: "target 100%"
    - incidents_count: "daily"
    - incidents_severity_distribution: "weekly"
    - consent_revocation_rate: "monthly"
    - cross_border_transfers: "monthly"
    - dpia_completion_rate: "quarterly"
  
  dashboards:
    - real_time: "S22 observability"
    - weekly: "executive_summary"
    - monthly: "board_report"
    - quarterly: "anpd_readiness"
  
  alerts:
    - sla_breach: "immediate"
    - critical_incident: "immediate"
    - systemic_issue: "1 hour"
```

### 3. ANPD Cooperation

```yaml
dpo_anpd_cooperation:
  channel: "ANPD portal + registered email"
  agcp_cr: "CR-006, CR-007"
  
  procedures:
    - incident_notification: "72h per Art. 48"
    - prior_consultation: "high risk DPIA"
    - information_requests: "respond within deadline"
    - audits: "facilitate ANPD audits"
  
  evidence:
    - all_communications_logged: true
    - ledger_entries: "ANPD_COMMUNICATION"
    - response_times_tracked: true
```

### 4. Training Program

```yaml
dpo_training:
  agcp_cr: "CR-110, CR-111"
  
  modules:
    - name: "LGPD Fundamentals"
      audience: "all_staff"
      frequency: "annual"
      duration: "2 hours"
    
    - name: "Data Subject Rights"
      audience: "customer_facing + ops"
      frequency: "annual"
      duration: "3 hours"
    
    - name: "Incident Response"
      audience: "security + engineering"
      frequency: "semi_annual"
      duration: "4 hours"
    
    - name: "AGCP Governance Model"
      audience: "engineering + AI team"
      frequency: "annual"
      duration: "3 hours"
    
    - name: "DPO Specific"
      audience: "DPO + privacy team"
      frequency: "continuous"
      duration: "ongoing"
  
  tracking:
    - completion_rate: "target 100%"
    - assessment_scores: "minimum 80%"
    - records_in_ledger: true
```

### 5. Records of Processing (Art. 37)

```yaml
dpo_records:
  agcp_cr: "CR-062, CR-063"
  
  record_content:
    - controller_identity: ""
    - purposes: []
    - data_categories: []
    - data_subject_categories: []
    - recipients: []
    - international_transfers: []
    - retention_periods: []
    - security_measures: []
    - legal_bases: []
    - dpia_reference: ""
  
  agcp_integration:
    - source: "governance_ledger + evidence_store"
    - auto_generated: true
    - updated: "real_time"
    - export_format: "JSON/CSV for ANPD"
```

### 6. DPIA Advisory (Art. 38)

```yaml
dpo_dpia_advisory:
  trigger: "high_risk_processing_proposal"
  agcp_cr: "CR-036, CR-037, CR-038"
  
  process:
    - receive_proposal: "from_controller"
    - assess_need: "criteria_art38"
    - if_required:
        - guide_controller: "dpia_process"
        - review_dpia: "before_submission"
        - advise_on_measures: "technical_organizational"
        - prior_consultation_anpd: "if_residual_high_risk"
    - document: "DPIA_ADVISORY in ledger"
```

---

## DPO Governance Integration

```yaml
dpo_governance_integration:
  role_in_agcp:
    - policy_review: "reviews governance policies for LGPD"
    - invariant_approval: "approves LGPD-related invariants"
    - hitl_participation: "can be HITL approver for LGPD matters"
    - incident_authority: "can trigger structural refusal"
  
  authority_lineage:
    - delegated_by: "controller_top_management"
    - scope: "LGPD_compliance"
    - agcp_cr: "CR-040, CR-044, CR-045"
  
  evidence:
    - all_actions_logged: true
    - decisions_attributable: true
    - independence_verified: true
```

---

## Verification

```bash
# Submit complaint to DPO
python3 -m agcp.dpo complaint --subject-id uuid --type access --details "..."

# Check DPO dashboard
python3 -m agcp.dpo dashboard --period monthly

# Verify DPO independence
python3 -m agcp.dpo independence-check --dpo-id uuid

# Run training compliance
python3 -m agcp.dpo training-report --period quarterly
```