---
module: "video"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
contract_path_ref: "../../../../contracts/openapi/paths/video.yaml"
schemas_ref: "../../../../contracts/schemas/video/"
---

# TEST_MATRIX_VIDEO.md

## Objetivo
Definir a matriz mínima de testes e evidências que sustentam os contratos do módulo.

## Matriz (mínimo)

| ID | Artefato | Tipo de verificação | Obrigatório | Evidência |
|---|---|---|:---:|---|
| TM-001 | `contracts/openapi/paths/video.yaml` | Lint OpenAPI (Redocly/Spectral) | Sim | `_reports/contract_gates/latest.json` |
| TM-002 | `contracts/schemas/video/` | Validação JSON Schema | Sim | `_reports/contract_gates/latest.json` |
| TM-003 | `DOMAIN_RULES_VIDEO.md` | Revisão normativa + testes de regra (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-004 | `INVARIANTS_VIDEO.md` | Teste de invariantes (quando existir) | Condicional | `_reports/contract_gates/latest.json` |
| TM-005 | Endpoints de captura/ingest | Teste funcional: simulação de captura ao vivo | Sim | `_reports/test_results/video_capture_*.json` |
| TM-006 | Endpoints de transcode | Teste funcional: validação de perfis transcoded | Sim | `_reports/test_results/video_transcode_*.json` |
| TM-007 | Sincronização de timecode | Teste de invariante INV-VID-001/010/011 | Sim | `_reports/test_results/video_sync_*.json` |
| TM-008 | Distribuição e auditoria | Teste de invariante INV-VID-009/012 | Sim | `_reports/test_results/video_distribution_*.json` |

## Plano de Testes (v1.0)

### Fase 1: Validação de Contrato (Imediato)
- ✓ Lint OpenAPI (Redocly)
- ✓ Validação JSON Schema
- ✓ Crossref DOMAIN_RULES ↔ INVARIANTS

### Fase 2: Testes de Captura (Sprint após contracts)
- Criar sessão de mídia (`POST /video/sessions`)
- Simular ingest de segmento (`POST /video/segments`)
- Validar timecode lógico gerado

### Fase 3: Testes de Sincronização (Sprint após Fase 2)
- Mock `scout` enviando eventos de sincronização
- Validar `SyncService` resolvendo desalinhamentos
- Verificar INV-VID-010 (scout timecode nunca muda)

### Fase 4: Testes de Distribuição (Sprint após Fase 3)
- Simular requisição de clip para distribuição
- Validar auditoria sendo registrada
- Testar idempotência (INV-VID-012)

### Fase 5: Testes de Retenção (Sprint final v1.0)
- Validar retenção padrão conservadora (INV-VID-008)
- Simular expiração e limpeza
- Validar auditoria de deleção

## Matriz de Rastreabilidade

| Regra de Domínio | Invariante(s) Relacionado(s) | Teste(s) |
|---|---|---|
| DR-VID-001 | INV-VID-001, INV-VID-010 | TM-007 |
| DR-VID-002 | INV-VID-004 | TM-006 |
| DR-VID-003 | (infraestrutura, integração) | TM-005 |
| DR-VID-004 | INV-VID-005 | TM-008 |
| DR-VID-005 | (padrão append-only) | TM-001 (schema validation) |
| DR-VID-006 | (implementação, não regra) | TM-006 |
| DR-VID-007 | INV-VID-006 | (teste de autorização, fora deste escopo v1) |
| DR-VID-008 | INV-VID-007, INV-VID-008 | TM-005 (Fase 5) |
| DR-VID-009 | INV-VID-009 | TM-008 |
| DR-VID-010 | INV-VID-010, INV-VID-011 | TM-007 |

## Critérios de Sucesso

- **Lint OpenAPI:** 0 erros, 0 warnings
- **JSON Schema:** Todos os tipos validáveis
- **Captura:** Segmento criado com timecode lógico correto
- **Sincronização:** Desalinhamento >100ms resolvido, evento `VIDEO_SYNC_ADJUSTMENT` emitido
- **Distribuição:** Clip entregue a CDN com auditoria registrada
- **Retenção:** Padrão de 7 dias aplicado; expiração testada

