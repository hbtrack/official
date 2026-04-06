---
module: "video"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "readme"
module_scope_ref: "./MODULE_SCOPE_VIDEO.md"
domain_rules_ref: "./DOMAIN_RULES_VIDEO.md"
invariants_ref: "./INVARIANTS_VIDEO.md"
test_matrix_ref: "./TEST_MATRIX_VIDEO.md"
contract_path_ref: "../../../../contracts/openapi/paths/video.yaml"
schemas_ref: "../../../../contracts/schemas/video/"
---

# video

## Objetivo
O módulo `video` é responsável por **captura ao vivo, ingestão, sincronização temporal, transcodificação e distribuição de mídia** integrada ao sistema operacional do HB Track.

## Responsabilidades
- Captura de vídeo ao vivo na arena (edge-first com fallback local)
- Ingestão de feeds externos (TV, produtora, múltiplos ângulos)
- Sincronização temporal com tracking, scouting e placar
- Transcodificação para perfis técnicos (baixa latência) e públicos (CDN)
- Clipping automático e manual com índice semântico
- Distribuição técnica restrita (banco, tribuna, comissão) e pública (broadcasting)

## Fora do escopo
- Broadcast como domínio de negócio autônomo (futuro: módulo `media`)
- Edição editorial de pós-produção completa
- CDN global de varejo
- Monetização OTT como produto independente

## Artefatos do módulo
- `MODULE_SCOPE_VIDEO.md`
- `DOMAIN_RULES_VIDEO.md`
- `INVARIANTS_VIDEO.md`
- `TEST_MATRIX_VIDEO.md`
- `contracts/openapi/paths/video.yaml`
- `contracts/schemas/video/*.schema.json`

### Artefatos condicionais (quando aplicável)
- `STATE_MODEL_VIDEO.md` (quando houver machine de estados de captura/transcode)
- `PERMISSIONS_VIDEO.md` (quando RBAC for introduzido)

## Source graph estruturado
- Manifesto do módulo: `docs/hbtrack/modulos/video/graph/module_manifest.yaml`
- Entidades: `docs/hbtrack/modulos/video/graph/entity_graph.yaml`
- Endpoints: `docs/hbtrack/modulos/video/graph/endpoints.yaml`
- Erros: `docs/hbtrack/modulos/video/graph/errors.yaml`
- Obrigações de teste: `docs/hbtrack/modulos/video/graph/test_obligations.yaml`

Este conjunto ativa `video` na trilha soberana de source graph. Ele deve permanecer alinhado com `contracts/`, `src/video/` e os documentos normativos do módulo.

## Dependências
- Sistema: `SYSTEM_SCOPE.md`
- Domínio esportivo: `HANDBALL_RULES_DOMAIN.md`
- Contrato HTTP: `contracts/openapi/paths/video.yaml`
- Schemas: `contracts/schemas/video/`

## Regras
1. Nenhuma interface pública do módulo existe fora do contrato OpenAPI.
2. Nenhuma entidade pública estável do módulo existe fora de schema.
3. Toda mudança de estado deve obedecer invariantes documentadas em `INVARIANTS_VIDEO.md`.

## Navegação rápida
1. Leia `MODULE_SCOPE_VIDEO.md`
2. Leia `DOMAIN_RULES_VIDEO.md`
3. Leia `INVARIANTS_VIDEO.md`
4. Leia `TEST_MATRIX_VIDEO.md`
5. Leia `contracts/openapi/paths/video.yaml`
