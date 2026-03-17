# SESSION HANDOFF — HB TRACK
> Atualizar ao final de cada sessão produtiva. Este arquivo é lido pelo agente ANTES de qualquer outra coisa.

## Estado Geral
data_ultima_sessao: 2026-03-17
branch_ativo: hb-track-contratos-driven
ci_status: PASS
modulo_foco: pipeline (F0–F5)

## O Que Foi Feito (últimas 3 sessões)
### Sessão 2026-03-17
- [x] F0 — Baseline estabilizado: CI GREEN (30 PASS + 2 SKIP), commit `ee75ad2`
- [x] F1 — CLAUDE.md criado na raiz (88 linhas), boot context reduzido de 60% para ~4%
- [x] F1 — CONTRACT_PIPELINE.md §1 atualizado com referência ao CLAUDE.md como artefato de boot
- [x] F2 — SESSION_HANDOFF.template.md criado em `docs/_canon/templates/`
- [x] F2 — SESSION_HANDOFF.md (este arquivo) criado na raiz com estado atual

## Próximos Passos (ordenados por prioridade)
1. F2 — Adicionar instrução de SESSION_HANDOFF ao `pre_contract_orchestrator.prompt.md` (F2.3)
2. F2 — Documentar SESSION_HANDOFF como evidência do estágio Pre-contract em CONTRACT_PIPELINE.md §2 (F2.4)
3. F3 — Criar `docs/_canon/HUMAN_INTERFACE_POLICY.md` (sem decisão humana pendente)
4. F4 — Criar `docs/_canon/FEATURE_REGISTRY.yaml` para o módulo training
5. F5 — Criar worker `adversarial_analysis.prompt.md`

## Decisões Pendentes do Humano
| Decisão | Contexto | Urgência |
|---------|----------|---------|
| D2 — Versionamento de contratos | Como tratar mudanças incompatíveis na API? (Fase 6) | antes do primeiro módulo em produção |
| D1 — Consumidores da API | Quem vai usar o HB Track? App interno, parceiros externos? (Fase 7) | antes do primeiro release externo |
| D3 — Pact Broker | Servidor para testes de integração (Fase 7) | antes do primeiro release externo |
| D4 — Stack tecnológica | Backend, banco de dados, frontend (Fase 8) | antes de gerar qualquer código |
| D5 — Plataforma de deploy | Onde o HB Track vai rodar? (Fase 9) | antes do primeiro deploy |
| D6 — Aprovação de deploy | Automático ou com aprovação humana? (Fase 9) | antes do primeiro deploy |
| D7 — Escopo do frontend | Web, mobile ou ambos? (Fase 13) | antes de gerar código frontend |

## Bloqueios Ativos
| Código | Módulo | Descrição | Próxima ação |
|--------|--------|-----------|-------------|
| — | — | Nenhum bloqueio ativo | — |

## Contratos em Andamento
| Módulo | Recurso | Status | Próximo passo |
|--------|---------|--------|--------------|
| training | Sessões de treino | implementation_ready | Análise adversarial (F5) antes de gerar código |

## ADRs Recentes (últimas 5)
| ADR | Título | Status |
|-----|--------|--------|
| ADR-021 | media-delivery-boundary | accepted |
| ADR-019 | layer-separation-domain-dto-viewmodel | accepted |
| ADR-018 | hybrid-persistence-pattern | accepted |
| ADR-017 | training-session-state-machine | accepted |
| ADR-016 | mcp-surface (deferido pós-v1.0) | deferred |

## Contexto Importante
- Pipeline definido em `pipeline.md` — executar fases em sequência
- F0–F2 podem ser executadas sem decisão humana; F6–F13 dependem das decisões D2–D7
- O pré-commit hook executa `validate_contracts.py` a cada commit (lento — ~90s)
- CLAUDE.md é artefato de boot ativo; qualquer alteração requer ADR
- `docs/_canon/templates/SESSION_HANDOFF.template.md` é o template canônico para novos handoffs
