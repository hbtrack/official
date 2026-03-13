---
doc_type: canon
version: "1.0.0"
last_reviewed: "2026-03-11"
status: active
---

# Documentação Canônica — HB Track

Este diretório contém os artefatos normativos soberanos do HB Track. Todo módulo, agente e implementação deriva daqui.

## Propósito

`docs/_canon/` é a camada normativa global do sistema. Enquanto a documentação de módulo (`docs/hbtrack/modulos/`) governa comportamento específico de cada módulo, os documentos aqui presentes estabelecem as regras, convenções e escopo que todos os módulos devem respeitar sem exceção.

Nenhuma implementação, contrato de módulo ou decisão técnica pode contradizer os artefatos deste diretório sem processo formal de revisão.

## Hierarquia Normativa

```
CONTRACT_SYSTEM_RULES.md        ← nível máximo (regras do sistema contract-driven)
  └── docs/_canon/              ← nível global normativo (este diretório)
        └── docs/hbtrack/modulos/   ← nível de módulo
              └── implementação     ← código, migrations, testes
```

Regra: em caso de conflito entre níveis, o nível superior prevalece sempre.

**Nota importante (APIs)**: convenções, regras de validação e templates de **API HTTP/OpenAPI** têm SSOT em `.contract_driven/templates/api/api_rules.yaml` (conforme `.contract_driven/CONTRACT_SYSTEM_RULES.md`). `docs/_canon/API_CONVENTIONS.md` existe como guia/ponteiro.

## Artefatos Canônicos Globais

| # | Arquivo | Responsabilidade |
|---|---------|-----------------|
| 1 | `README.md` | Este guia de navegação — estrutura, hierarquia, ordem de leitura |
| 2 | `SYSTEM_SCOPE.md` | Missão do sistema, 5 atores canônicos, 9 macrodomínios, o que está fora do escopo |
| 3 | `ARCHITECTURE.md` | Stack canônica, 5 princípios arquiteturais, estrutura de camadas, ADRs registradas |
| 4 | `MODULE_MAP.md` | Taxonomia dos 16 módulos canônicos, responsabilidades, dependências entre módulos |
| 5 | `GLOBAL_INVARIANTS.md` | Invariantes globais (INV-*) — guardrails soberanos cross-módulo |
| 6 | `SECURITY_RULES.md` | Regras globais de segurança — autenticação/autorização, dados sensíveis, logging, hardening |
| 7 | `API_CONVENTIONS.md` | Guia/ponteiro de API — SSOT em `.contract_driven/templates/api/api_rules.yaml` |
| 8 | `ERROR_MODEL.md` | Modelo canônico de erros HTTP: estrutura de payload, códigos de erro, políticas de resposta |
| 9 | `DATA_CONVENTIONS.md` | IDs, datas, enums, soft delete, naming de tabelas e campos |
| 10 | `CI_CONTRACT_GATES.md` | Gates de CI/qualidade para contratos (OpenAPI/AsyncAPI/JSON Schema/Arazzo) |
| 11 | `TEST_STRATEGY.md` | Estratégia de testes (unit/integration/contract/e2e) e evidências aceitas |
| 12 | `UI_FOUNDATIONS.md` | Fundamentos de UI/UX (a11y, responsividade, estados, linguagem) |
| 13 | `DESIGN_SYSTEM.md` | Design system (tokens, componentes, grids, tipografia) |
| 14 | `C4_CONTEXT.md` | C4 — Contexto (atores/sistemas externos, limites) |
| 15 | `C4_CONTAINERS.md` | C4 — Containers (frontend, backend, workers, DB, integrações) |
| 16 | `CHANGE_POLICY.md` | Como propor, revisar e aprovar mudanças em artefatos canônicos e contratos de módulo |
| 17 | `DOMAIN_GLOSSARY.md` | Glossário de termos do domínio: handebol, sistema, governança contract-driven |
| 18 | `HANDBALL_RULES_DOMAIN.md` | Regras IHF documentadas (HBR-001..) — âncora normativa para módulos handball-sensíveis |
| 19 | `security/OWASP_API_CONTROL_MATRIX.yaml` | Matriz normativa (OWASP → declaração → evidência → gate) para controles de segurança de API |
| 20 | `MODULE_SOURCE_AUTHORITY_MATRIX.yaml` | Matriz normativa por módulo: fontes permitidas, artefatos obrigatórios e limites de inferência (gera gates de boundary/async/autoridade) |

## Ordem Recomendada de Leitura

Para novos colaboradores e agentes, leia nesta sequência:

1. **`SYSTEM_SCOPE.md`** — entenda o que o sistema é, quem são os atores, o que está dentro e fora do escopo
2. **`ARCHITECTURE.md`** — entenda a stack, os princípios e a estrutura de camadas
3. **`MODULE_MAP.md`** — entenda os 16 módulos, suas responsabilidades e dependências
4. **`GLOBAL_INVARIANTS.md`** — conheça guardrails globais (INV-*) antes de propor contratos ou invariantes de módulo
5. **`SECURITY_RULES.md`** — segurança global antes de qualquer contrato público (dados de atletas/comissão técnica)
6. **`.contract_driven/templates/api/api_rules.yaml`** — SSOT de convenções/validações/templates de API HTTP (OpenAPI/JSON/URLs/paginação/erros/segurança)
7. **`API_CONVENTIONS.md`** — visão geral e ponteiros para a SSOT de API
8. **`ERROR_MODEL.md`** — consulte antes de definir respostas de erro em qualquer endpoint
9. **`DATA_CONVENTIONS.md`** — convenções de dados antes de criar qualquer schema ou migration
10. **`CI_CONTRACT_GATES.md`** — entenda quais validações/gates tornam um contrato “pronto”
11. **`TEST_STRATEGY.md`** — entenda evidências e níveis de teste esperados
12. **`HANDBALL_RULES_DOMAIN.md`** — leia se for trabalhar em módulos handball-sensíveis (training, matches, competitions, scout, analytics)
13. **`DOMAIN_GLOSSARY.md`** — consulte sempre que encontrar um termo do domínio que não é imediatamente claro
14. **`CHANGE_POLICY.md`** — leia antes de propor qualquer alteração em artefatos normativos

Após ler os canônicos globais, leia a documentação do módulo em que for trabalhar (`docs/hbtrack/modulos/<módulo>/`).

## Regra Cardinal

> **Nenhuma implementação sem contrato vigente.**

Isso significa:
- Nenhum endpoint HTTP sem contrato OpenAPI correspondente
- Nenhuma migration sem invariante documentada para constraints críticas
- Nenhuma regra de negócio derivada do handebol sem âncora em `HANDBALL_RULES_DOMAIN.md`
- Nenhum evento assíncrono sem contrato AsyncAPI
- Nenhum workflow multi-step sem definição Arazzo quando formalmente exigido

## Artefatos Relacionados

- **Sistema de contratos**: `.contract_driven/CONTRACT_SYSTEM_RULES.md`
- **Layout canônico**: `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
- **Templates**: `.contract_driven/GLOBAL_TEMPLATES.md`
- **Documentação de módulos**: `docs/hbtrack/modulos/`
- **CLI de governança**: `scripts/run/hb_cli.py`

---

*Última revisão: 2026-03-11*
