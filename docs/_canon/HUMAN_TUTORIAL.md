# Fluxo humano — HB_Track (com novos artefatos)

Este documento descreve o fluxo de desenvolvimento voltado para humanos usando os artefatos adicionados recentemente.

Sumário rápido (evidências citadas):
- Política de handshake / requisito de ACK: .github/copilot-handshake.md
- Implementação e resumo da infra AI: IMPLEMENTATION_SUMMARY.md
- Lista de comandos aprovados e exemplos: docs/_ai/_context/approved-commands.yml
- Mapas de troubleshooting: docs/_ai/_maps/troubleshooting-map.json
- Checklists e exemplos de invocação: docs/_ai/_specs/checklist-models.yml, docs/_ai/_specs/invocation-examples.yml
- Scripts utilitários, extractors, generators, validators: scripts/_ia/** (ver arquivos listados)

1) Setup (pré-requisitos)

- Ambiente Python/virtualenv
  - Observação: alguns scripts referenciam um virtualenv em `.envinash.exe` (ver `docs/_ai/_context/approved-commands.yml`).
  - PENDENTE: validar no ambiente local — verificar se há um requirements.txt e instalar dependências (arquivo/ação para validar: procurar `requirements.txt` na raiz do repo; comando sugerido para validar: `python -m pip install -r requirements.txt`).

- Dependências observadas nos scripts:
  - PyYAML é requerido (ver `scripts/_ia/utils/yaml_loader.py` — checa `import yaml`).  
    PENDENTE: validar no ambiente local — executar `python -c "import yaml; print(yaml.__version__)