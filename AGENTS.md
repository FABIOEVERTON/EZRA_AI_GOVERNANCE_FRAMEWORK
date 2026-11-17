# AGENTS.md — Wize Dev Kit (EZRA_AI_GOVERNANCE_FRAMEWORK)

Este repositório segue o ciclo de vida **Wize Dev Kit** (artifact-first, 8 fases, 10 personas, 6 gates TEA) sob supervisão do **EZRA (Foreman + OpenJEV)**.

## 1. Estrutura de Artefatos (`.wize/`)
- `.wize/config/` — `project.toml`, `user.toml`, `tea.toml`
- `.wize/planning/` — `brief.md`, `research.md`, `ux/`, `prd.md`, `tech-vision.md`, `nfr-principles.md`
- `.wize/solutioning/` — `architecture.md`, `adrs/`, `epics/`, `stories/`
- `.wize/implementation/` — `sprint-status.md`, `retrospective.md`, `tea/` (gates)
- `.wize/knowledge/` — documentação de longo prazo e referências
- `.wize/security/` — `scope.md`, `report.md`, `report.html`, `security-backlog.md`

## 2. Ciclo de Vida em 8 Fases
1. **Triage** (`/wize-orchestrator` / `/wize-help next`): Ler `.wize/` antes de agir, detectar fase e definir a próxima ação.
2. **Discovery** (`/wize-grill` -> `/wize-product-brief` -> `/wize-trigger-map`): Consolidar `brief.md`.
3. **Product Definition** (`/wize-create-prd` -> `/wize-validate-prd`): Definir objetivos, escopo e ACs numerados.
4. **UX Strategy** (`/wize-ux-scenarios` -> `/wize-ux-design`): Quando aplicável.
5. **Solution Strategy** (`/wize-tech-vision` -> `/wize-nfr-principles`): Stack, NFRs e orçamentos.
6. **Architecture & Slicing** (`/wize-create-architecture` -> `/wize-design-system` -> `/wize-create-epics-and-stories`): ADRs e stories do tamanho de 1 PR.
7. **Implementation & Quality Gates**: `/wize-sprint-planning` -> `/wize-tea-risk` -> `/wize-tea-design` -> `/wize-create-story` -> `/wize-dev-story` (TDD) -> `/wize-code-review` -> `/wize-tea-trace` -> `/wize-tea-review` -> `/wize-tea-gate`.
8. **Tracking & Retro** (`/wize-sprint-status` -> `/wize-retrospective`).

## 3. Personas
Wizer (Orchestrator), Pepper Potts (Analyst), Peggy Carter (Tech Writer), Maria Hill (PM), Mantis (UX), Nick Fury (Strategy), Tony Stark (Architect), Hawkeye (Test Architect / TEA), Shuri (Senior Dev / TDD), Natasha Romanoff (Red-Teamer / OWASP).

## 4. Regras Invioláveis
- **Trava de 3 Ciclos:** Se uma correção falhar 3 vezes seguidas, parar e replanejar (`/wize-correct-course`).
- **Revisão em 4 Camadas (`/wize-code-review`):** Blind spots, edge cases, subtração (`/wize-subtract`) e auditoria dos ACs.
- **Pré-PR (`/wize-pre-pr-check`):** Rodar lint, formatação, build e testes (`pytest` / `CONFORMANCE.md`) antes de abrir/atualizar PR.
- **Rastreabilidade:** Nunca fabricar resultados de testes ou commitar segredos; sincronizar decisões com `MEMORIA_ESTADO_*` no Google Drive.
