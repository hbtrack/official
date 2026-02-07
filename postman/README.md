# Postman Collection - HB Track Notifications API

Coleção completa para testar endpoints REST do sistema de notificações implementado nos **Steps 8-15+17**.

## 📦 Arquivos

- `HB_Track_Notifications_API.postman_collection.json` - Collection com todos os endpoints
- `HB_Track_Environment.postman_environment.json` - Variáveis de ambiente (baseUrl, token)
- `README.md` - Este arquivo

## 🚀 Setup

### 1. Importar no Postman

**Opção A: Importar via Postman Desktop**
1. Abrir Postman
2. Clicar em **Import** (canto superior esquerdo)
3. Arrastar os arquivos `.json` ou clicar em **Upload Files**
4. Selecionar:
   - `HB_Track_Notifications_API.postman_collection.json`
   - `HB_Track_Environment.postman_environment.json`
5. Clicar em **Import**

**Opção B: Importar via Postman Web**
1. Acessar https://web.postman.co/
2. Workspace → Import → Upload Files
3. Importar ambos os arquivos

### 2. Configurar Environment

1. Selecionar environment **"HB Track - Local"** no dropdown superior direito
2. Verificar variáveis:
   - `baseUrl`: `http://localhost:8000` ✅
   - `token`: (vazio, será preenchido após login) ⏳
   - `user_id`: (vazio, será preenchido após login) ⏳

### 3. Garantir Backend rodando

```powershell
cd "c:\HB TRACK\Hb Track - Backend"
$env:ENV="test"
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Verificar: http://localhost:8000/


## 🧪 Testes - Ordem de Execução

### ✅ 1. Auth → Login
**Executa primeiro para obter token JWT**

- Request: `POST /api/v1/auth/login`
- **Content-Type:** `application/x-www-form-urlencoded` (NÃO JSON!)
- Body (form-data):
  - `username`: `e2e.admin@teste.com` (campo é 'username', mas valor é email)
  - `password`: `HBTrackE2E2024!`
- **Nota:** OAuth2PasswordRequestForm aceita APENAS form-urlencoded
- Script automático: Salva `{{token}}` e `{{user_id}}` no environment

**Response esperada:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "uuid",
  "email": "e2e.admin@teste.com",
  "role_code": "dirigente",
  "is_superadmin": false
}
```

**Credenciais Seed E2E (BANCO REAL):**
Todas as senhas: `HBTrackE2E2024!`
- Admin/Dirigente: `e2e.admin@teste.com`
- Coordenador: `e2e.coordenador@teste.com`
- Treinador: `e2e.treinador@teste.com`
- Atleta: `e2e.atleta@teste.com`
- Membro: `e2e.membro@teste.com`

**Superadmin (migration):**
- Email: `adm@handballtrack.app` / Senha: `Admin@123!`

### 📬 2. Notifications → List All Notifications
**Lista todas as notificações (lidas e não lidas)**

- Request: `GET /api/v1/notifications?page=1&limit=50`
- Headers: `Authorization: Bearer {{token}}`

**Response esperada:**
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "team_assignment",
      "message": "Você foi designado como treinador da equipe Sub-17",
      "notification_data": {"team_id": "uuid", "team_name": "Sub-17"},
      "is_read": false,
      "read_at": null,
      "created_at": "2026-01-14T17:00:00"
    }
  ],
  "total": 10,
  "unread_count": 3,
  "page": 1,
  "limit": 50
}
```

### 🔔 3. Notifications → List Unread Notifications
**Lista apenas não lidas**

- Request: `GET /api/v1/notifications?unread_only=true&page=1&limit=20`
- Headers: `Authorization: Bearer {{token}}`

**Use case:** Atualizar contador do sino no TopBar

### ✅ 4. Notifications → Mark Notification as Read
**Marca uma notificação específica como lida**

- Request: `PATCH /api/v1/notifications/:notification_id/read`
- Headers: `Authorization: Bearer {{token}}`
- Path variable: Substituir `:notification_id` por UUID real da lista

**Response esperada:**
```json
{"success": true}
```

**Erros possíveis:**
- `400`: `invalid_notification_id` (UUID malformado)
- `404`: `notification_not_found`
- `403`: `not_your_notification` (tentando marcar notificação de outro usuário)

### ✅✅ 5. Notifications → Mark All as Read
**Marca todas as notificações do usuário como lidas**

- Request: `POST /api/v1/notifications/read-all`
- Headers: `Authorization: Bearer {{token}}`
- Body: Vazio

**Response esperada:**
```json
{
  "success": true,
  "count": 5
}
```

### 📊 6. Metrics → Prometheus Metrics
**Métricas do sistema (sem autenticação)**

- Request: `GET /api/v1/metrics`
- Headers: Nenhum

**Response esperada (Prometheus text format):**
```
# HELP websocket_active_connections Active WebSocket connections
# TYPE websocket_active_connections gauge
websocket_active_connections 0.0

# HELP websocket_reconnections_total Total WebSocket reconnections
# TYPE websocket_reconnections_total counter
websocket_reconnections_total 0.0

# HELP websocket_message_latency_seconds WebSocket message delivery latency
# TYPE websocket_message_latency_seconds histogram
websocket_message_latency_seconds_bucket{le="0.005"} 0.0
...
```

### 💚 7. Health → Health Check
**Verifica status do backend**

- Request: `GET /health`
- Headers: Nenhum

**Response esperada:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "test",
  "database": "connected"
}
```

## 🔐 Autenticação

Todos os endpoints de notificações requerem **JWT Bearer Token** no header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Como obter token:

1. **Via Postman:** Executar request `Auth → Login` (token salvo automaticamente)
2. **Via Frontend:** DevTools → Application → Local Storage → `auth_token`
3. **Manualmente:** Copiar `access_token` da response do login

## 📝 Notas

### Variáveis de ambiente

A collection usa variáveis do Postman para facilitar testes:

- `{{baseUrl}}` - URL base da API (http://localhost:8000)
- `{{token}}` - JWT token (auto-preenchido após login)
- `{{user_id}}` - ID do usuário logado (auto-preenchido)

### Scripts automáticos

**Request "Login"** contém script de teste que:
1. Valida response status 200
2. Extrai `access_token` do JSON
3. Salva em `pm.environment.set('token', ...)`
4. Log confirmação no console

### Credenciais default

**Ambiente:** test  
**Email:** admin@hbtrack.com  
**Password:** admin123

(Ajustar conforme seed do banco de dados)

## 🐛 Troubleshooting

### ❌ Erro: "Connection refused"
**Causa:** Backend não está rodando  
**Fix:** Iniciar backend com `uvicorn app.main:app --reload`

### ❌ Erro: "401 Unauthorized"
**Causa:** Token expirado ou inválido  
**Fix:** Executar request `Auth → Login` novamente

### ❌ Erro: "404 notification_not_found"
**Causa:** UUID da notificação não existe  
**Fix:** Executar `List All Notifications` primeiro e copiar UUID real

### ❌ Erro: "403 not_your_notification"
**Causa:** Tentando marcar notificação de outro usuário  
**Fix:** Verificar se está usando token correto

## 🔗 Endpoints Implementados

| Method | Endpoint | Step | Descrição |
|--------|----------|------|-----------|
| POST | `/api/v1/auth/login` | - | Autenticação |
| GET | `/api/v1/notifications` | 14 | Listar notificações |
| PATCH | `/api/v1/notifications/{id}/read` | 14 | Marcar como lida |
| POST | `/api/v1/notifications/read-all` | 14 | Marcar todas como lidas |
| GET | `/api/v1/metrics` | 15 | Métricas Prometheus |
| WS | `/api/v1/notifications/stream` | 13 | WebSocket stream* |
| GET | `/health` | - | Health check |

_*WebSocket não testável via Postman REST, usar Postman WebSocket ou wscat_

## 📚 Documentação Adicional

- **Plano completo:** `docs\_PLANO_GESTAO_STAFF.md`
- **Logs de implementação:** `LOGS.md`
- **Instruções de teste:** `LOGS.md` (seção "Testes REST")

## ✅ Status de Implementação

**Steps concluídos:** 1-15+17 (44% do plano)
- ✅ Backend Core (1-7)
- ✅ Notification System (8-15+17)

**Pendente:** Steps 16, 18-34 (gestão de convites, frontend, QA)

---

**Versão:** 1.0.0  
**Data:** 2026-01-14  
**Mantido por:** GitHub Copilot
