# Changelog - HB Track
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Adicionado
* **AI Governance Canonical Templates** (2026-02-12): Implementação da suite de governança e protocolos para agentes de IA:
  - `AI_GOVERNANCE_INDEX.md`: Índice centralizador.
  - `AI_INCIDENT_RESPONSE_POLICY.md`: Protocolo para falhas e alucinações.
  - `AI_TASK_VERSIONING_POLICY.md`: Gestão de versões de tarefas.
  - `AI_PROTOCOL_CHECKLIST.md`: Checklist de pré-emissão de tarefas.
  - `AI_ARCH_EXEC_PROTOCOL.md`: Protocolo Architect vs Executor.
  - `TASK_BRIEF.md` & `EVIDENCE_PACK.md`: Templates de input/output determinísticos.

### Pendente CI/CD
* GitHub Actions workflow para validar quality-gates e approved-commands em PRs (próximo passo)
* Implementação de `generate-ai-index.py` (ainda é placeholder TODO)
* Adicionar `validate-quality-gates-schema.py` como validador de schema

### Adicionado
* **AI Infrastructure Validation & Smoke Tests** (2026-02-12): Validação completa da infraestrutura de IA com testes locais e CI/CD:
  - **Smoke Tests (7/7 PASS)**: Utils (json_loader, yaml_loader), Extractors (approved-commands, troubleshooting), Generators (handshake, invocation-examples, checklist)
  - **Artefatos Gerados**:
    - `docs/_ai/_context/approved-commands.yml` (5 categorias extraídas)
    - `docs/_ai/_maps/troubleshooting-map.json` (4 exit codes mapeados)
    - `docs/_ai/_specs/invocation-examples.yml` (exemplos de invocação)
    - `docs/_ai/_specs/checklist-models.yml` (checklist de models)
    - `.github/copilot-handshake.md` (protocolo de handshake)
  - **Validadores (2/2 PASS)**: Quality gates (✅ passed, radon opcional), Approved commands (⚠️ requer whitelist update)
  - **Code Review Pipeline**: `scripts/dev/run_code_review.sh` implementado com 13 steps (setup, testes, extratores, validadores, linters, métricas)
  - **Exit Code Semantics**: 0=PASS, 1=CRITICAL_FAIL, 2=WARNING, 3=FATAL_ERROR (alinhado com canônico)

* **AI Infrastructure: scripts/_ia/ + GitHub Actions Workflows** (2026-02-11): Construção completa de infraestrutura para automação e validação de agentes:
  - **9 Arquivos Python Implementados** (substituindo placeholders, status: MERGED 2026-02-11):
    - **Utilities (2)**: `scripts/_ia/utils/json_loader.py`, `scripts/_ia/utils/yaml_loader.py`
    - **Extractors (2)**: `scripts/_ia/extractors/extract-approved-commands.py`, `scripts/_ia/extractors/extract-troubleshooting.py`
    - **Validators (2)**: `scripts/_ia/validators/validate-approved-commands.py`, `scripts/_ia/validators/validate-quality-gates.py`
    - **Generators (3)**: `scripts/_ia/generators/generate-handshake-template.py`, `scripts/_ia/generators/generate-invocation-examples.py`, `scripts/_ia/generators/generate-checklist-yml.py`
  - **Implementações**:
    - Error handling robusto (FileNotFoundError, JSONDecodeError, YAMLError)
    - UTF-8 encoding explícito em todas as operações de arquivo
    - Smoke tests básicos nas utilities
    - Saída clara e exit codes (0=pass, 1=fail)
    - Sem hardcoded credentials ou PII
  - **Status:** Código implementado, PR foi fundido (merged). Próximo passo: criar workflows de CI/CD para validar e executar essas ferramentas automaticamente.

### Alterado
* `docs/_ai/` reorganizado anteriormente (2026-02-11) — agora com implementações executáveis em `scripts/_ia/` (utilities, extractors, validators, generators).

### Removido
* Placeholders antigos em `scripts/_ia/` substituídos por implementações funcionais.

---

## [2026-02-11]
### Adicionado
* Implementação inicial de infraestrutura AI (scripts/_ia) e documentação de suporte.

---

## Notas
- CI/CD: adicionar GitHub Actions que executem `validate-quality-gates.py` e `validate-approved-commands.py` em PRs.
- Segurança: instalar dependências listadas em `scripts/_ia/requirements.txt` em runners CI antes de executar radon/lizard.