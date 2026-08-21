#!/usr/bin/env python3
# generate_mappings.py — Generate regulatory → AGCP CR mappings

import csv
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
FRAMEWORK_DIR = SCRIPT_DIR.parent / "framework"
UPSTREAM_DIR = SCRIPT_DIR.parent / "upstream"
MAPPINGS_DIR = FRAMEWORK_DIR / "mappings"
MAPPINGS_DIR.mkdir(parents=True, exist_ok=True)

# NIST AI RMF 22 subcategories → AGCP CR mapping
NIST_TO_AGCP = [
    # GOVERN (6)
    ("GOVERN-1.1", "Governance policies, processes, and procedures", "CR-001,CR-007,CR-011"),
    ("GOVERN-1.2", "Accountability structures", "CR-040,CR-044,CR-065"),
    ("GOVERN-1.3", "Workforce AI literacy", "CR-110,CR-111"),
    ("GOVERN-1.4", "Risk management culture", "CR-003,CR-031"),
    ("GOVERN-1.5", "Stakeholder engagement", "CR-043,CR-070"),
    ("GOVERN-1.6", "Legal and regulatory compliance", "CR-006,CR-007"),
    # MAP (5)
    ("MAP-1.1", "Context identification", "CR-036,CR-037,CR-038"),
    ("MAP-1.2", "Stakeholder mapping", "CR-043,CR-070"),
    ("MAP-1.3", "Impact assessment", "CR-048,CR-049,CR-050"),
    ("MAP-1.4", "Risk identification", "CR-003,CR-031,CR-033"),
    ("MAP-1.5", "Risk prioritization", "CR-032,CR-033,CR-034"),
    # MEASURE (5)
    ("MEASURE-1.1", "Metrics and monitoring", "CR-083,CR-084,CR-099"),
    ("MEASURE-1.2", "Evaluation and testing", "CR-079,CR-080,CR-087"),
    ("MEASURE-1.3", "Drift detection", "CR-032,CR-033,CR-091"),
    ("MEASURE-1.4", "Independent assessment", "CR-085,CR-086,CR-089"),
    ("MEASURE-1.5", "Continuous improvement", "CR-101,CR-122"),
    # MANAGE (6)
    ("MANAGE-1.1", "Risk response", "CR-019,CR-020,CR-021"),
    ("MANAGE-1.2", "Resource allocation", "CR-102,CR-119"),
    ("MANAGE-1.3", "Incident response", "CR-053,CR-054,CR-058"),
    ("MANAGE-1.4", "Recovery planning", "CR-100,CR-101"),
    ("MANAGE-1.5", "Governance review", "CR-081,CR-082,CR-083"),
    ("MANAGE-1.6", "Communication and reporting", "CR-010,CR-062,CR-063"),
]

# EU AI Act → AGCP CR mapping
EU_AI_ACT_TO_AGCP = [
    ("Art. 5", "Prohibited AI practices", "CR-003", "Unacceptable risk"),
    ("Art. 6", "High-risk classification", "CR-007,CR-036,CR-037", "High risk"),
    ("Art. 7", "High-risk list (Annex III)", "CR-007,CR-036,CR-037", "High risk"),
    ("Art. 8", "Compliance with requirements", "CR-019,CR-020,CR-021", "High risk"),
    ("Art. 9", "Risk management system", "CR-003,CR-031,CR-032,CR-033", "High risk"),
    ("Art. 10", "Data governance", "CR-036,CR-037,CR-038,CR-062,CR-064", "High risk"),
    ("Art. 11", "Technical documentation", "CR-010,CR-062,CR-063,CR-085", "High risk"),
    ("Art. 12", "Record keeping (logging)", "CR-062,CR-063,CR-064,CR-066,CR-067", "High risk"),
    ("Art. 13", "Transparency and information", "CR-010,CR-085,CR-086", "High risk"),
    ("Art. 14", "Human oversight", "CR-002,CR-012,CR-013,CR-014,CR-015,CR-016,CR-017,CR-018", "High risk"),
    ("Art. 15", "Accuracy, robustness, cybersecurity", "CR-032,CR-033,CR-119,CR-120,CR-121", "High risk"),
    ("Art. 16", "Provider obligations", "CR-007,CR-019,CR-022", "High risk"),
    ("Art. 17", "Quality management", "CR-110,CR-111,CR-112", "High risk"),
    ("Art. 18", "Conformity assessment", "CR-079,CR-080,CR-089", "High risk"),
    ("Art. 19", "EU declaration of conformity", "CR-010,CR-062,CR-085", "High risk"),
    ("Art. 20", "CE marking", "CR-010,CR-085", "High risk"),
    ("Art. 21", "Post-market monitoring", "CR-083,CR-084,CR-099,CR-122", "High risk"),
    ("Art. 22", "Incident reporting", "CR-053,CR-054,CR-058,CR-059,CR-060", "High risk"),
    ("Art. 50", "Transparency obligations", "CR-010,CR-085,CR-086", "Limited risk"),
    ("Art. 51-56", "GPAI obligations", "CR-062,CR-064,CR-119,CR-120,CR-121", "GPAI"),
]

# AIGP → AGCP CR mapping
AIGP_TO_AGCP = [
    ("Accountability", "Governance structure", "CR-040,CR-044,CR-065"),
    ("Accountability", "RACI matrix", "CR-043,CR-044,CR-045"),
    ("Accountability", "Executive sponsorship", "CR-110,CR-111"),
    ("Fairness", "Bias testing", "CR-079,CR-080,CR-087"),
    ("Fairness", "Disparate impact analysis", "CR-083,CR-084"),
    ("Fairness", "Ongoing monitoring", "CR-083,CR-084,CR-099"),
    ("Transparency", "Model cards", "CR-010,CR-085"),
    ("Transparency", "System cards", "CR-010,CR-085,CR-086"),
    ("Transparency", "Decision explanations", "CR-085,CR-086"),
    ("Privacy by Design", "Data minimization", "CR-036,CR-037,CR-119"),
    ("Privacy by Design", "Anonymization", "CR-119,CR-120,CR-121"),
    ("Privacy by Design", "Purpose limitation", "CR-036,CR-037,CR-038"),
    ("Risk Management", "Identify", "CR-003,CR-031"),
    ("Risk Management", "Assess", "CR-032,CR-033,CR-048"),
    ("Risk Management", "Treat", "CR-019,CR-020,CR-021"),
    ("Risk Management", "Monitor", "CR-083,CR-084,CR-099"),
    ("Risk Management", "Review", "CR-081,CR-082,CR-122"),
]

# LGPD → AGCP CR mapping
LGPD_TO_AGCP = [
    ("Art. 6", "Principles (finalidade, adequação, necessidade)", "CR-036,CR-037,CR-038"),
    ("Art. 6", "Principles (livre acesso, qualidade, transparência)", "CR-010,CR-085,CR-086"),
    ("Art. 6", "Principles (segurança, prevenção, não discriminação)", "CR-119,CR-120,CR-121"),
    ("Art. 6", "Princípio (responsabilização)", "CR-040,CR-044,CR-065"),
    ("Art. 7", "Base legal: consentimento", "CR-005,CR-040"),
    ("Art. 7", "Base legal: cumprimento obrigação legal", "CR-006,CR-007"),
    ("Art. 7", "Base legal: administração pública", "CR-006,CR-007"),
    ("Art. 7", "Base legal: pesquisa", "CR-036,CR-037"),
    ("Art. 7", "Base legal: execução contrato", "CR-036,CR-037"),
    ("Art. 7", "Base legal: exercício direitos", "CR-010,CR-085"),
    ("Art. 7", "Base legal: proteção vida", "CR-053,CR-054"),
    ("Art. 7", "Base legal: tutela saúde", "CR-053,CR-054"),
    ("Art. 7", "Base legal: interesse legítimo", "CR-031,CR-032,CR-033"),
    ("Art. 7", "Base legal: proteção crédito", "CR-036,CR-037"),
    ("Art. 18", "Direito: confirmação e acesso", "CR-010,CR-062"),
    ("Art. 18", "Direito: correção", "CR-062,CR-064"),
    ("Art. 18", "Direito: anonimização/bloqueio/eliminação", "CR-053,CR-054,CR-119"),
    ("Art. 18", "Direito: portabilidade", "CR-010,CR-085"),
    ("Art. 18", "Direito: eliminação", "CR-053,CR-054"),
    ("Art. 18", "Direito: informação compartilhamento", "CR-062,CR-063"),
    ("Art. 18", "Direito: revogação consentimento", "CR-005,CR-015"),
    ("Art. 18", "Direito: oposição", "CR-053,CR-054"),
    ("Art. 18", "Direito: revisão decisões automatizadas", "CR-085,CR-086,CR-002"),
    ("Art. 46", "Medidas de segurança", "CR-119,CR-120,CR-121"),
    ("Art. 48", "Comunicação incidente (72h)", "CR-053,CR-054,CR-058,CR-059"),
    ("Art. 49", "Comunicação ao titular", "CR-010,CR-062,CR-063"),
    ("Art. 50", "Medidas adotadas", "CR-062,CR-064,CR-066"),
    ("Art. 33-36", "Transferência internacional", "CR-026,CR-027,CR-028,CR-029,CR-030"),
    ("Art. 41", "DPO", "CR-040,CR-044,CR-065"),
]

def write_csv(filename, headers, rows):
    path = MAPPINGS_DIR / filename
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Written: {path}")

def main():
    print("Generating regulatory → AGCP mappings...")
    
    write_csv("nist-to-agcp.csv", 
              ["NIST_Subcategory", "Description", "AGCP_CRs"],
              [(r[0], r[1], r[2]) for r in NIST_TO_AGCP])
    
    write_csv("eu-ai-act-to-agcp.csv",
              ["Article", "Title", "AGCP_CRs", "Risk_Tier"],
              EU_AI_ACT_TO_AGCP)
    
    write_csv("aigp-to-agcp.csv",
              ["Domain", "Subdomain", "AGCP_CRs"],
              AIGP_TO_AGCP)
    
    write_csv("lgpd-to-agcp.csv",
              ["Article", "Requirement", "AGCP_CRs"],
              LGPD_TO_AGCP)
    
    # Combined master mapping
    all_rows = []
    for r in NIST_TO_AGCP:
        all_rows.append(["NIST AI RMF", r[0], r[1], r[2]])
    for r in EU_AI_ACT_TO_AGCP:
        all_rows.append(["EU AI Act", r[0], r[1], r[2]])
    for r in AIGP_TO_AGCP:
        all_rows.append(["AIGP", r[0], r[1], r[2]])
    for r in LGPD_TO_AGCP:
        all_rows.append(["LGPD", r[0], r[1], r[2]])
    
    write_csv("master-regulatory-to-agcp.csv",
              ["Framework", "Reference", "Description", "AGCP_CRs"],
              all_rows)
    
    print("All mappings generated successfully!")

if __name__ == "__main__":
    main()