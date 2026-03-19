---
module: "video"
system_scope_ref: "../../../_canon/SYSTEM_SCOPE.md"
handball_rules_ref: "../../../_canon/HANDBALL_RULES_DOMAIN.md"
handball_semantic_applicability: false
type: "permissions"
adr_refs:
  - "ADR-008: authz-strategy (RBAC flat, 5 roles)"
  - "ADR-007: auth-strategy (JWT Bearer)"
  - "ADR-033: Video Module Canonicalization"
domain_rules_ref: "./DOMAIN_RULES_VIDEO.md"
invariants_ref: "./INVARIANTS_VIDEO.md"
state_model_ref: "./STATE_MODEL_VIDEO.md"
updated_at: "2026-03-19"
---

# PERMISSIONS_VIDEO.md

> **Nota canônica:** O módulo `identity_access` é a fonte soberana de autenticação e atribuição de roles.
> Este artefato **documenta** como `video` aplica autorização — não redefine roles.
> Roles canônicos: `admin`, `coordinator`, `coach`, `athlete`, `member` (ADR-008).
> Enforcement por operação, via guards no Router (BFLA) e Service (BOLA, BOPLA).
>
> **Escopo de conteúdo:** Uma MatchMediaSession pertence a uma partida (matchId).
> Autorização é scopada ao nível de **MatchMediaSession** (INV-VID-006, DR-VID-007):
> quem tem acesso à captura de uma partida vê **todo** o conteúdo de vídeo dessa partida,
> ou nenhum (sem acesso granular a nível de segmento ou clip).
> O role `member` (espectador) acessa apenas vídeos de partidas públicas (futuro: implementar public_match flag).

---

## Tabela de Permissões por Operação

| Operação (operationId) | admin | coordinator | coach | athlete | member | Observação |
|---|---|---|---|---|---|---|
| `createSession` | ✅ | ✅ | ✅ | ❌ | ❌ | Cria nova MatchMediaSession em estado DRAFT (DR-VID-001); requer acesso à partida matchId |
| `listSessions` | ✅ | ✅ | ✅ | ✅ | ✅ (filtered) | Todos autenticados; resultado filtrado por matchId scope (INV-VID-006); member vê apenas partidas públicas |
| `getSession` | ✅ | ✅ | ✅ | ✅ (se matchId acessível) | ✅ (se partida pública) | BOLA: usuário deve ter acesso à partida; scope = MatchMediaSession (INV-VID-006) |
| `updateSession` | ✅ | ✅ | ✅ (se estado < SYNCING) | ❌ | ❌ | Altera campos editáveis (retentionPolicy, captureMode, etc.) antes de SYNCING (INV-VID-007); PUBLISHED é irrevogável (INV-VID-002) |
| `transitionSession` | ✅ | ✅ | ✅ | ❌ | ❌ | Muda estado (DRAFT→CAPTURING→SYNCING→TRANSCODING→PUBLISHED) via PATCH operação (STATE_MODEL_VIDEO.md) |
| `ingestSegment` | ✅ | ✅ | ✅ (edge node service account) | ❌ | ❌ | POST /segments: apenas durante estado CAPTURING; tipicamente via edge service account autenticado (DR-VID-003) |
| `createClip` | ✅ | ✅ | ✅ | ✅ | ❌ | Cria ClipDefinition (semântico, com scout_event_id ou zone_label); athlete pode criar clips para análise pessoal (INV-VID-005) |
| `listClips` | ✅ | ✅ | ✅ | ✅ | ✅ (herdado da sessão) | Visibilidade herdada da MatchMediaSession pai (INV-VID-006) |
| `getClip` | ✅ | ✅ | ✅ | ✅ | ✅ (herdado) | BOLA: acesso ao clip = acesso à sessão pai |
| `publishDistribution` | ✅ | ✅ | ✅ | ❌ | ❌ | POST /distribution: publica clip em CDN/broadcast para target type (DR-VID-009); requer aprovação ou role admin/coordinator |
| `listDistributions` | ✅ | ✅ | ✅ | ✅ | ✅ (herdado) | Visibilidade herdada; public links visíveis a all; audit log acessível apenas a admin/coordinator |
| `getDistribution` | ✅ | ✅ | ✅ | ✅ | ✅ (se público) | BOLA: acesso ao distribution = acesso à sessão + permissão targetType |

---

## Regras de Contexto Cross-Operação

| ID | Regra | Ref |
|---|---|---|
| PERM-VID-001 | Toda MatchMediaSession é scopada a 1 partida (matchId); autorização é "all or nothing" no nível de sessão (INV-VID-006) | STATE_MODEL_VIDEO, INV-VID-006 |
| PERM-VID-002 | `athlete` e `member` têm acesso read-only; nunca criam sessões, alteram estado ou publicam para broadcast | DR-VID-007 |
| PERM-VID-003 | Coach é dono de MatchMediaSession que criou (ao menos durante DRAFT/CAPTURING); pode transicionar estados enquanto autorizado | STATE_MODEL_VIDEO.md |
| PERM-VID-004 | Estado PUBLISHED é irrevogável (INV-VID-002); ninguém (nem admin) pode reverter ou editar pós-publicação | INV-VID-002 |
| PERM-VID-005 | Retenção de vídeo é governada por retentionPolicy explícita (DRAFT: editável; PUBLISHED: imutável); sem fallback silencioso (INV-VID-007, INV-VID-008) | DOMAIN_RULES_VIDEO.md |
| PERM-VID-006 | ClipDefinition pode ser criada por athlete durante ou pós-captura (para análise pessoal); requer contexto semântico: scout_event_id, zone_label ou athlete_ids (INV-VID-005, DR-VID-004) | INVARIANTS_VIDEO.md |
| PERM-VID-007 | Publicação em broadcast requer role admin/coordinator (segurança: não expor vídeos inteiros sem aprovação) | PERM-VID-004 |
| PERM-VID-008 | Cada leitura de segmento (playback) auditada: user_id, session_id, segment_id, timestamp, duration_watched (INV-VID-009) | DOMAIN_RULES_VIDEO.md|
| PERM-VID-009 | Edge service account (ingestão de segments) é serviço interno autenticado via mTLS ou service-to-service token; nunca é role de usuário final | DR-VID-003, ADR-031 |
| PERM-VID-010 | Toda ação de write (create session, publish clip, publish distribution) gera evento de auditoria consumido pelo módulo `audit` | MODULE_SCOPE_VIDEO.md |
| PERM-VID-011 | Access por clip público (via CDN): qualquer pessoa com URL pode ver; sem RBAC por recurso interno; only audit tracked | PUBLIC_CDN target type (DR-VID-002) |

---

## Role Mapping by MatchMediaSession Lifecycle

### DRAFT State
- **admin, coordinator, coach:** Podem alterar metadados (retentionPolicy, captureMode) antes de iniciar
- **athlete, member:** Read-only (se accessível via partida)

### CAPTURING State
- **admin, coordinator, coach (via edge service account):** Edge node queue ingestão de segments
- **athlete, member:** Read-only, podem parametrizar clips para análise pessoal (não publicam)

### SYNCING State
- **admin, coordinator, coach:** Só observam; system automático sincroniza vs scout
- **athlete, member:** Read-only

### TRANSCODING State
- **admin, coordinator, coach:** Só observam; system automático executa Celery jobs (ADR-031)
- **athlete, member:** Read-only

### PUBLISHED State
- **admin, coordinator:** Podem republish em outros targets ou revoke access (futuro)
- **coach, athlete, member:** Read-only (público ou scope-restricted conforme targetType)

---

## Technical Enforcement Points

1. **Router Layer (BFLA):** Valida role antes de despachar ao operationId
2. **Service Layer (BOLA):** Valida que usuário tem acesso ao matchId da sessão; filtra resultados por scope
3. **Data Layer (BOPLA):** Audit logging em toda write; read filtering por ACL + role

## Testing Coverage (TEST_MATRIX_VIDEO.md)

- [x] RBAC: admin > coordinator > coach > athlete > member (hierarchy enforced)
- [x] BOLA: usuário acessa sessão apenas se tiver acesso ao matchId
- [x] INV-VID-006 enforcement: sessão é all-or-nothing, nunca granular por segmento
- [x] INV-VID-002 enforcement: PUBLISHED state não pode ser alterado por ninguém
- [x] Auditoria: toda write gera evento consumido por `audit` module

