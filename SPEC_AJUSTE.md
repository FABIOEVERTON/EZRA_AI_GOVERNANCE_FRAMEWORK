# SPEC DE AJUSTE — ezra_ai_governance_framework

## Diagnóstico
- Framework documental sólido e já publicado (mappings, skills, control-plane, templates)
- **Zero testes** nos scripts (`validate_framework.py`, `generate_mappings.py`)
- **Zero CI** — um repositório de governança que não valida a si mesmo é contradição perfomativa
- `docs/` vazio (pasta morta no repo)
- `rebuild-framework.sh` nunca teve execução verificada publicamente (reprodutibilidade não provada)

## Objetivo
Tornar o repo **auto-validável e reproduzível**: o CI deve rodar o próprio validador do framework contra ele mesmo.

## Escopo

### 1. Testes (pytest, ≥6)
- `tests/test_validate_framework.py` — fixtures com árvore mínima válida → passa; inválida (skill sem SKILL.txt, mapping CSV sem coluna obrigatória) → erro esperado
- `tests/test_generate_mappings.py` — geração determinística: mesma entrada → mesmo CSV (golden file)

### 2. CI (`.github/workflows/ci.yml`)
- Job 1: `python scripts/validate_framework.py` (deve exit 0 no próprio repo)
- Job 2: `pytest` + `ruff check scripts/ tests/`
- Gatilho: push/PR em main

### 3. Reprodutibilidade
- Executar `rebuild-framework.sh` uma vez; se gerar diff inesperado ou falhar → corrigir ou documentar limitação no README

### 4. docs/
- Preencher com `docs/VALIDATION.md` curto: como validar o framework localmente + o que cada check significa (ou remover a pasta vazia — decidir na execução)

### 5. Logs de comprovação (evidência)
- `scripts/run_evidence.sh`: executa validador + pytest + ruff em sequência e grava log datado em `evidence/YYYY-MM-DD_HHMMSS.log` (comando, versão Python, resultado de cada etapa, exit codes)
- Fim do log imprime resumo: PASS/FAIL por etapa
- `.gitignore` mantém só os últimos N=5 logs? Não — evidência é acumulada; logs são pequenos (texto)
- No CI: artefatos do Actions também guardam o log de cada run
- Todo critério de aceite abaixo só vale com log correspondente em `evidence/`

### 5.1 Carimbo por arquivo (provenance)
- `scripts/stamp_files.py`: após validação PASS, gera `evidence/validation_manifest.json` com **um registro por arquivo testado**:
  `{ path, sha256, validated_at (ISO-8601 UTC), run_id, result }`
- Abrange: `framework/`, `scripts/`, `tests/`, `ezra-control-plane/`
- Local: regenerado a cada `run_evidence.sh`
- No Git (CI): ao passar, o workflow regenera o manifest e **commita de volta** em `main` com `[skip ci]` na mensagem (evita loop) + upload como artefato
- Arquivo alterado sem re-validação = sha256 divergente do manifest → detectável (`stamp_files.py --check`)

### 6. README
- Badge de CI + seção "Validação" com os comandos + menção à pasta `evidence/` como trilha de comprovação

## Critérios de aceite
- [ ] `validate_framework.py` exit 0 no repo atual — **com log em `evidence/`**
- [ ] `pytest` verde (≥6 testes) — **com log em `evidence/`**
- [ ] `ruff check` limpo em scripts/ e tests/ — **com log em `evidence/`**
- [ ] CI ativo no GitHub Actions (artefatos com log de cada run)
- [ ] `rebuild-framework.sh` executado; resultado documentado — **com log em `evidence/`**
- [ ] `upstream/` permanece ignorado; nada fora deste repo é alterado
- [ ] Substância das mappings/skills/specs **não é alterada**
- [ ] Commit único: `chore(ci): auto-validação do framework (testes + CI + evidência)`

## Fora de escopo
Conteúdo das mappings/skills, specs do control-plane, `upstream/`, qualquer outro repositório.

## Riscos
- `rebuild-framework.sh` pode sobrescrever arquivos com diffs — mitigação: rodar, inspecionar `git diff` antes de qualquer commit.
