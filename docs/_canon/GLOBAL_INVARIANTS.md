# GLOBAL_INVARIANTS.md

## Objetivo
Registrar regras que devem permanecer verdadeiras em todo o sistema.

## Invariantes Globais

### Contrato e API
1. Todo recurso público deve ter identificador estável.
2. Toda interface HTTP pública deve existir em `contracts/openapi/openapi.yaml`.
3. Toda convenção de API HTTP (design/validação/templates) deve seguir `.contract_driven/templates/api/api_rules.yaml`.
4. Todo payload público estável deve possuir schema correspondente.
5. Toda mudança breaking deve ser explicitamente classificada e revisada.
6. Toda regra de negócio derivada do handebol deve ser rastreável para `HANDBALL_RULES_DOMAIN.md`.
7. Toda resposta de erro HTTP deve seguir a SSOT (`.contract_driven/DOMAIN_AXIOMS.json#error_axioms` + `contracts/openapi/components/schemas/shared/problem.yaml`).
8. Toda tela que dependa de API pública deve estar alinhada ao contrato vigente.
9. Toda permissão sensível deve estar documentada e verificável.

### Operação ao vivo (jogo oficial)
10. Todo componente crítico de jogo ao vivo deve ter modo de operação degradada documentado — a plataforma não pode depender de processamento frágil durante uma partida oficial.
11. Eventos de jogo ao vivo não podem ser perdidos por falha de conexão — retransmissão é obrigatória.
12. Vídeo e eventos críticos de partida devem ter redundância de armazenamento.
13. Live stats, scouting ao vivo e dashboards de banco devem operar dentro dos SLAs definidos em `SLA-LIVE-*`.
14. Todo módulo que opera durante o jogo deve declarar explicitamente seu SLA de latência no contrato.

---

## Tabela de invariantes

| ID | Invariante | Escopo | Fonte | Como verificar |
|---|---|---|---|---|
| GI-001 | Nenhuma rota pública fora do OpenAPI | Global | contracts/openapi/openapi.yaml | Redocly lint + revisão de paths |
| GI-002 | Sem versionamento na URI | API HTTP | .contract_driven/templates/api/api_rules.yaml | Spectral ruleset + revisão |
| GI-003 | Erros seguem RFC 7807 + extensões aprovadas | API HTTP | .contract_driven/DOMAIN_AXIOMS.json + problem.yaml | Lint + testes de contrato |
| GI-004 | Componentes críticos de jogo declaram modo degradado | matches, scout, video | docs/guias/MVP_SCOPE.md | Revisão de design de módulo |
| GI-005 | Eventos de jogo têm garantia de entrega — retransmissão obrigatória | matches, scout | docs/guias/MVP_SCOPE.md | Teste de resiliência |
| GI-006 | Armazenamento de vídeo e eventos de partida é redundante | video, matches | docs/guias/MVP_SCOPE.md | Revisão de arquitetura |
| GI-007 | Todo módulo live declara SLA de latência no contrato | matches, scout, analytics | SLA-LIVE-001..003 abaixo | Revisão de contrato |

---

## SLAs de latência por contexto

> Referência normativa para design de módulos. Todo módulo que opera em jogo ao vivo deve
> referenciar o SLA correspondente em seu contrato e test_matrix.

| ID | Contexto de operação | Latência máxima | Módulos afetados |
|---|---|---|---|
| SLA-LIVE-001 | Live scouting, live stats, dashboards de banco e tribuna | **3 segundos** | matches, scout, analytics |
| SLA-LIVE-002 | Alertas táticos e físicos durante jogo | **10 segundos** | matches, scout, wellness |
| SLA-LIVE-003 | Clipping automático e sincronização enriquecida pós-evento | **5 minutos** | video, scout |
| SLA-POST-001 | Relatório pós-jogo completo (após encerramento) | **2 horas** | reports, analytics |
| SLA-POST-002 | Benchmarking consolidado e análises pesadas | **24 horas** | analytics, ai_ingestion |

---

## Violação
Qualquer violação de invariante global deve bloquear merge até resolução ou exceção formal registrada (ADR).
Violação de SLA deve ser documentada no contrato do módulo como exceção justificada.
