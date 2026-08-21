# Validação do Framework

Este repositório valida a si mesmo. Toda alteração em `framework/`, `scripts/`, `tests/` ou `ezra-control-plane/` passa por três checagens antes de ser considerada válida.

## Comandos

```bash
pip install -r requirements-dev.txt

# Suíte completa com log de evidência datado
bash scripts/run_evidence.sh

# Apenas o validador estrutural
python3 scripts/validate_framework.py

# Apenas os testes unitários
python3 -m pytest tests/ -v

# Verificar se algum arquivo mudou desde a última validação carimbada
python3 scripts/stamp_files.py --check
```

## O que cada etapa verifica

| Etapa | Script | O que faz |
|-------|--------|-----------|
| **framework-validator** | `scripts/validate_framework.py` | Estrutura: skills com `SKILL.txt`, mappings CSV bem-formados, templates JSON/YAML sintaticamente válidos, referências AGCP presentes, níveis de conformidade, integração com o control-plane |
| **pytest** | `tests/` | Determinismo do gerador de mappings (golden file contra os CSVs commitados), schema dos CSVs, árvore mínima válida/inválida para o validador |
| **ruff** | lint estático | Qualidade de código em `scripts/` e `tests/` |
| **stamp-files** | `scripts/stamp_files.py` | Carimbo SHA-256 + timestamp UTC por arquivo em `evidence/validation_manifest.json` |

## Trilha de evidência

- `evidence/YYYY-MM-DD_HHMMSS.log` — log completo de cada execução local (comando, versões, resultado por etapa, exit codes)
- `evidence/validation_manifest.json` — manifest com hash e timestamp de cada arquivo validado; regenerado a cada execução que passa
- GitHub Actions — cada run publica os logs como artefatos e atualiza o manifest no branch `main`

Um arquivo alterado sem re-validação fica detectável: o `--check` compara o SHA-256 atual com o último manifest e reporta `DRIFTED`, `UNSTAMPED` ou `REMOVED`.
