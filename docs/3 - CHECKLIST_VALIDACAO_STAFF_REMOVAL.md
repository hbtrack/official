<!-- STATUS: NEEDS_REVIEW -->

# Checklist de Validação - Steps 35-36 (Staff Management Backend)

## ✅ Pré-requisitos Técnicos

- [ ] Backend rodando em localhost:8000
- [ ] Database com migrations aplicadas (0027-0033+)
- [ ] Seed E2E executado (`python scripts/seed_e2e.py`)
- [ ] Postman ou Thunder Client instalado
- [ ] Token JWT de teste (dirigente ou coordenador)

## ✅ Validação Backend - Endpoint DELETE /teams/{id}/staff/{membership_id}

### Teste 1: Remover Coordenador (Soft Delete)

**Request:**
```http
DELETE http://localhost:8000/api/v1/teams/{team_id}/staff/{membership_id}
Authorization: Bearer {jwt_dirigente}
```

**Expected Response (200):**
```json
{
  "success": true,
  "team_without_coach": false,
  "message": "{Nome da pessoa} removido da equipe {Nome da equipe}"
}
```

**Validações:**
- [ ] Status 200 OK
- [ ] `team_without_coach === false` (não era treinador)
- [ ] Campo `deleted_at` populado no `team_memberships`
- [ ] Campo `deleted_reason` = "Removido por {nome_usuario}"
- [ ] Log no backend: "Staff member soft deleted"

**SQL Verification:**
```sql
SELECT id, status, deleted_at, deleted_reason
FROM team_memberships
WHERE id = '{membership_id}';
```

---

### Teste 2: Remover Treinador (Encerrar Vínculo)

**Request:**
```http
DELETE http://localhost:8000/api/v1/teams/{team_id}/staff/{coach_membership_id}
Authorization: Bearer {jwt_dirigente}
```

**Expected Response (200):**
```json
{
  "success": true,
  "team_without_coach": true,
  "message": "{Nome do treinador} removido da equipe {Nome da equipe}"
}
```

**Validações:**
- [ ] Status 200 OK
- [ ] `team_without_coach === true` (era o coach ativo)
- [ ] Campo `end_at` populado com timestamp atual
- [ ] Campo `status` = "inativo"
- [ ] `teams.coach_membership_id` = NULL
- [ ] Notificação criada na tabela `notifications`
- [ ] Log no backend: "Coach removed from team"

**SQL Verification:**
```sql
-- Verificar team_membership encerrado
SELECT id, status, end_at, start_at
FROM team_memberships
WHERE id = '{membership_id}';

-- Verificar team sem coach
SELECT id, name, coach_membership_id
FROM teams
WHERE id = '{team_id}';

-- Verificar notificação criada
SELECT user_id, type, message, notification_data
FROM notifications
WHERE notification_data->>'team_id' = '{team_id}'
AND type = 'coach_removal'
ORDER BY created_at DESC
LIMIT 1;
```

**Expected Notification:**
- `type`: "coach_removal"
- `message`: "Você foi removido como treinador da equipe {Nome}"
- `notification_data`: `{"team_id": "...", "team_name": "...", "removed_at": "...", "removed_by": "..."}`

---

### Teste 3: Erro 404 - Membership Não Encontrado

**Request:**
```http
DELETE http://localhost:8000/api/v1/teams/{team_id}/staff/00000000-0000-0000-0000-000000000000
Authorization: Bearer {jwt_dirigente}
```

**Expected Response (404):**
```json
{
  "detail": "membership_not_found"
}
```

---

### Teste 4: Erro 400 - Membership Não Pertence à Equipe

**Cenário:** Tentar remover membership de outra equipe

**Expected Response (400):**
```json
{
  "detail": "membership_does_not_belong_to_team"
}
```

---

### Teste 5: Erro 403 - Sem Permissão (Treinador Tenta Remover)

**Request:**
```http
DELETE http://localhost:8000/api/v1/teams/{team_id}/staff/{membership_id}
Authorization: Bearer {jwt_treinador}
```

**Expected Response (403):**
```json
{
  "detail": "insufficient_permissions" 
}
```

---

## ✅ Validação Frontend - API Client (teams.ts)

### Teste 1: Método removeStaffMember()

**Test Code (Console do Browser):**
```javascript
const { teamsService } = await import('/src/lib/api/teams');

// Remover coordenador
const result1 = await teamsService.removeStaffMember(
  'team-uuid',
  'membership-uuid'
);
console.log('Coordenador removido:', result1);
// Expected: { success: true, team_without_coach: false, message: "..." }

// Remover treinador
const result2 = await teamsService.removeStaffMember(
  'team-uuid',
  'coach-membership-uuid'
);
console.log('Treinador removido:', result2);
// Expected: { success: true, team_without_coach: true, message: "..." }
```

**Validações:**
- [ ] Método chama endpoint correto `/teams/{id}/staff/{id}`
- [ ] Usa verbo DELETE
- [ ] Retorna tipagem correta `{success, team_without_coach, message}`
- [ ] Sem erros TypeScript no console

---

### Teste 2: Método assignCoach()

**Test Code:**
```javascript
const { teamsService } = await import('/src/lib/api/teams');

const result = await teamsService.assignCoach(
  'team-uuid',
  'new-coach-membership-uuid'
);
console.log('Coach atribuído:', result);
// Expected: { success: true, message: "..." }
```

**Validações:**
- [ ] Método chama endpoint `/teams/{id}/coach`
- [ ] Usa verbo PATCH
- [ ] Payload correto: `{new_coach_membership_id: "..."}`
- [ ] Sem erros no console

---

### Teste 3: Método getAvailableCoaches()

**Test Code:**
```javascript
const { teamsService } = await import('/src/lib/api/teams');

const coaches = await teamsService.getAvailableCoaches({ active_only: true });
console.log('Coaches disponíveis:', coaches);
// Expected: { items: [{id, person_id, full_name, email, role: "treinador"}], total: N }
```

**Validações:**
- [ ] Método chama `/org-memberships`
- [ ] Query params: `role_id=3&active_only=true`
- [ ] Response tem estrutura `{items: Array, total: number}`
- [ ] Todos items têm `role_id === 3` (treinador)
- [ ] Se `active_only=true`, todos têm `end_at === null`

---

## ✅ Testes de Integração (WebSocket)

### Teste: Notificação em Tempo Real ao Remover Treinador

**Setup:**
1. Abrir duas janelas do navegador
2. Janela A: Logar como dirigente
3. Janela B: Logar como treinador (que será removido)
4. Verificar sino de notificações na Janela B

**Ações:**
1. Na Janela A: Remover treinador via DELETE `/staff/{coach_membership_id}`
2. Na Janela B: Verificar sino acende (badge vermelho)
3. Clicar no sino
4. Verificar notificação "Você foi removido como treinador da equipe X"

**Validações:**
- [ ] Notificação aparece instantaneamente (< 2s)
- [ ] Badge de contador atualiza
- [ ] Mensagem correta exibida
- [ ] Ao clicar, notificação marca como lida
- [ ] Ícone correto (AlertCircle)
- [ ] Metadata contém `team_id`, `team_name`, `removed_at`, `removed_by`

---

## ✅ Testes de Segurança & Permissões

### Teste: Permissões Revogadas Após Remoção

**Cenário:** Treinador removido tenta acessar equipe

**Steps:**
1. Logar como treinador
2. Acessar `/teams/{id}/overview` (deve funcionar)
3. Administrador remove o treinador
4. Tentar acessar `/teams/{id}/overview` novamente (sem refresh)
5. Fazer request para qualquer endpoint com `require_team=True`

**Expected:**
- [ ] Status 403 Forbidden
- [ ] Mensagem: "insufficient_permissions" ou similar
- [ ] Step 20 (permissions.py) valida `end_at IS NULL AND status == 'ativo'`
- [ ] Revogação imediata mesmo sem logout

---

## ✅ Performance & Database

### Teste: Índices de Performance

**Query Profiling:**
```sql
EXPLAIN ANALYZE
SELECT tm.*, p.full_name, om.role_id, r.code
FROM team_memberships tm
JOIN persons p ON tm.person_id = p.id
JOIN org_memberships om ON tm.org_membership_id = om.id
JOIN roles r ON om.role_id = r.id
WHERE tm.team_id = '{team_id}'
AND tm.status IN ('ativo', 'pendente')
AND tm.deleted_at IS NULL;
```

**Validações:**
- [ ] Usa índice `idx_team_memberships_active` (criado Step 24)
- [ ] Execution time < 10ms
- [ ] Sem sequential scans em tabelas grandes

---

## ✅ Edge Cases

### Teste 1: Remover Único Dirigente

**Cenário:** Equipe com apenas 1 dirigente, tentar remover

**Expected Behavior:**
- [ ] Deve permitir (não há validação de mínimo)
- [ ] ⚠️ **Considerar implementar:** Alerta "Equipe ficará sem administrador"

### Teste 2: Remover Coach Duas Vezes

**Cenário:** DELETE do mesmo membership_id consecutivo

**Expected:**
- [ ] Segunda requisição: 404 (membership já soft deleted ou end_at preenchido)
- [ ] Não duplica notificações

### Teste 3: Team Já Sem Coach

**Cenário:** `teams.coach_membership_id` já é NULL, remover outro staff

**Expected:**
- [ ] `team_without_coach === false` (não era o coach)
- [ ] Operação bem-sucedida

---

## 📋 Checklist Final

- [ ] ✅ Todos 5 testes do endpoint DELETE passaram
- [ ] ✅ Validações SQL confirmam estado correto no banco
- [ ] ✅ Notificações criadas e enviadas via WebSocket
- [ ] ✅ API client methods funcionando (TypeScript sem erros)
- [ ] ✅ Permissões revogadas imediatamente (Step 20)
- [ ] ✅ Performance satisfatória (< 10ms queries)
- [ ] ✅ Edge cases tratados
- [ ] ✅ Logs do backend sem erros
- [ ] ✅ TypeScript compila sem warnings

---

**Executado por:** _____________  
**Data:** _____________  
**Status:** ⏳ Pendente / ✅ Aprovado / ❌ Reprovado  
**Notas:** _____________________________________________

## 🔧 Troubleshooting

### Erro: "insufficient_permissions"
- Verificar token JWT é de dirigente ou coordenador
- Verificar `require_team=True` está validando corretamente
- Checar tabela `org_memberships` → `role_id IN (1, 2)`

### Erro: "membership_not_found"
- Verificar UUID está correto
- Verificar membership não está com `deleted_at` preenchido
- Usar query SQL para listar memberships da equipe

### Notificação Não Aparece
- Verificar WebSocket conectado (DevTools → Network → WS)
- Verificar `user_id` do treinador está correto
- Checar tabela `notifications` para confirmar criação
- Testar polling fallback (esperar 60s)

### Coach Não Foi Removido do Team
- Verificar lógica: `if team.coach_membership_id == org_membership.id`
- Checar joins: precisa do `org_membership_id`, não `team_membership.id`
- SQL debug: `SELECT coach_membership_id FROM teams WHERE id = '{team_id}'`
