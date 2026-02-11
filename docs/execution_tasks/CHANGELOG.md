# Changelog - HB Track
Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]
### Adicionado
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