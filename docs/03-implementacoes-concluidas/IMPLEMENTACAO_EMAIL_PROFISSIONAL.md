<!-- STATUS: DEPRECATED | implementacao concluida -->

# Implementação Email Profissional - SendGrid Dynamic Templates

**Status:** Pronto para implementação  
**Data:** 01/01/2026  
**FASE:** 3 - Integração SendGrid Profissional

---

## 📋 Sumário

Esta implementação atende aos requisitos profissionais:

### ✅ a) Template dinâmico (obrigatório)
- Dynamic Templates do SendGrid (não HTML hardcoded)
- Campos: person_name, organization_name, role_name, activation_link, cta_text

### ✅ b) Segurança
- Token single-use (campo `used` em `password_resets`)
- Expira em 24h
- Armazenado com hash SHA-256 (não texto puro)

### ✅ c) UX do e-mail
- Assunto claro: "Ative seu acesso ao HB Track"
- Copy curta, sem jargão técnico
- Assinatura institucional (logo + nome do sistema)
- CTA único: "Criar senha"

---

## 🔧 Implementação Backend

### 1. Atualizar Router (intake.py)

Adicionar o envio de email com segurança aprimorada:

```python
# No início do arquivo, importar:
from fastapi import BackgroundTasks
from app.services.intake.email_service_v2 import email_service_v2
from app.models.auth import PasswordReset
import hashlib

# Atualizar a assinatura do endpoint:
@router.post(
    "/ficha-unica",
    response_model=FichaUnicaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar Ficha Única",
    description="..."
)
async def create_ficha_unica(
    payload: FichaUnicaRequest,
    background_tasks: BackgroundTasks,  # ADICIONAR
    ctx: ExecutionContext = Depends(permission_dep(
        roles=["dirigente", "coordenador", "treinador"],
        require_org=False
    )),
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    validate_only: bool = Query(False, alias="dry_run")
):
    """..."""
    
    # ... código existente de processamento ...
    
    # ADICIONAR APÓS O SUCESSO DO SERVIÇO:
    
    # 4) Pós-commit: enviar email de ativação (não bloqueia transação)
    if payload.create_user and payload.user and response.user_id:
        from app.models.person import Person
        from app.models.organization import Organization
        from app.models.role import Role
        
        # Buscar dados da pessoa
        person = db.query(Person).filter(Person.id == response.person_id).first()
        if not person:
            logger.warning(f"Person not found for email | person_id={response.person_id}")
        else:
            # Buscar nome da organização (se houver)
            organization_name = None
            if response.organization_id:
                org = db.query(Organization).filter(
                    Organization.id == response.organization_id
                ).first()
                if org:
                    organization_name = org.name
            
            # Buscar nome do papel
            role_name = None
            role = db.query(Role).filter(Role.id == payload.user.role_id).first()
            if role:
                role_name = role.name
            
            # CRIAR TOKEN SEGURO (single-use, 24h expiry)
            token = secrets.token_urlsafe(32)  # 32 bytes = 256 bits
            token_hash = hashlib.sha256(token.encode()).hexdigest()  # Hash SHA-256
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)  # 24h
            
            # Salvar registro de reset com hash
            reset_record = PasswordReset(
                user_id=response.user_id,
                token_hash=token_hash,  # ARMAZENADO COM HASH
                token_type='welcome',
                expires_at=expires_at,
                used=False,  # Single-use
                created_at=datetime.now(timezone.utc)
            )
            
            db.add(reset_record)
            db.commit()
            
            logger.info(
                f"Password reset token created | user_id={response.user_id} | "
                f"expires_in=24h | type=welcome"
            )
            
            # ENVIAR EMAIL EM BACKGROUND (não bloqueia resposta)
            background_tasks.add_task(
                email_service_v2.send_invite_email,
                to_email=payload.user.email,
                person_name=person.full_name,
                token=token,  # Token em texto puro SÓ NO EMAIL
                app_url=os.getenv("APP_PUBLIC_URL", "https://app.hbtrack.app"),
                organization_name=organization_name,
                role_name=role_name
            )
            
            logger.info(
                f"Invite email queued | to={payload.user.email} | "
                f"person={person.full_name} | org={organization_name or 'N/A'} | "
                f"role={role_name or 'N/A'}"
            )
    
    return response
```

### 2. Criar Endpoint de Validação de Token

Criar novo endpoint em `auth.py` para validar e consumir token:

```python
# app/api/v1/routers/auth.py

@router.post(
    "/set-password",
    status_code=200,
    summary="Definir senha com token",
    description="Valida token e define senha (single-use)"
)
async def set_password_with_token(
    token: str = Body(..., description="Token recebido no email"),
    password: str = Body(..., min_length=8, description="Nova senha (mínimo 8 caracteres)"),
    db: Session = Depends(get_db)
):
    """
    Valida token de ativação e define senha.
    
    SEGURANÇA:
    - Token single-use (marcado como `used`)
    - Expira em 24h
    - Validado via hash SHA-256
    """
    import hashlib
    from app.models.auth import PasswordReset
    from app.models.user import User
    from app.core.security import get_password_hash
    
    # Computar hash do token recebido
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # Buscar registro de reset válido
    reset = db.query(PasswordReset).filter(
        PasswordReset.token_hash == token_hash,
        PasswordReset.used == False,  # Não usado ainda
        PasswordReset.expires_at > datetime.now(timezone.utc)  # Não expirado
    ).first()
    
    if not reset:
        raise HTTPException(
            status_code=400,
            detail="Token inválido ou expirado"
        )
    
    # Buscar usuário
    user = db.query(User).filter(User.id == reset.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualizar senha
    user.password_hash = get_password_hash(password)
    user.is_active = True  # Ativar usuário
    user.updated_at = datetime.now(timezone.utc)
    
    # MARCAR TOKEN COMO USADO (single-use)
    reset.used = True
    reset.used_at = datetime.now(timezone.utc)
    
    db.commit()
    
    logger.info(
        f"Password set successfully | user_id={user.id} | "
        f"token_type={reset.token_type} | email={user.email}"
    )
    
    return {
        "success": True,
        "message": "Senha definida com sucesso",
        "user_id": str(user.id)
    }
```

---

## 📧 Configuração SendGrid Dashboard

### Passo 1: Criar Dynamic Template

1. Acessar: https://app.sendgrid.com/dynamic_templates
2. Clicar em "Create a Dynamic Template"
3. Nome: **"HB Track - Ativação de Conta"**
4. Clicar em "Add Version" → "Blank Template" → "Code Editor"

### Passo 2: Configurar Template

Colar o código HTML do arquivo `SENDGRID_TEMPLATES.md` (seção "Corpo do Email").

### Passo 3: Adicionar Campos Dinâmicos

No editor, adicionar Test Data (JSON):

```json
{
  "person_name": "João Silva",
  "organization_name": "Clube de Handebol ABC",
  "role_name": "Treinador",
  "activation_link": "https://app.hbtrack.app/set-password?token=abc123",
  "cta_text": "Criar senha",
  "cta_link": "https://app.hbtrack.app/set-password?token=abc123",
  "app_name": "HB Track"
}
```

### Passo 4: Configurar Assunto

No campo "Subject" do template:

```
Ative seu acesso ao HB Track
```

### Passo 5: Preview e Salvar

- Clicar em "Preview" para ver renderização
- Verificar em desktop e mobile
- Clicar em "Save"
- Copiar o **Template ID** (formato: `d-abc123...`)

---

## 🔐 Variáveis de Ambiente (.env)

Adicionar ao arquivo `.env`:

```bash
# SendGrid Configuration (Professional)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
SENDGRID_FROM_EMAIL=no-reply@hbtrack.app
SENDGRID_FROM_NAME=HB Track
SENDGRID_INVITE_TEMPLATE_ID=d-abc123...
SENDGRID_WELCOME_TEMPLATE_ID=d-xyz789...  # Opcional

# App URLs
APP_PUBLIC_URL=https://app.hbtrack.app
FRONTEND_URL=https://app.hbtrack.app
```

---

## 🧪 Teste Manual

### 1. Criar ficha com usuário

```bash
curl -X POST "http://localhost:8000/api/v1/intake/ficha-unica" \
  -H "Authorization: Bearer {seu_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "person": {
      "first_name": "João",
      "last_name": "Silva",
      "contacts": [
        {
          "contact_type": "email",
          "contact_value": "seu-email-real@example.com",
          "is_primary": true
        }
      ]
    },
    "create_user": true,
    "user": {
      "email": "seu-email-real@example.com",
      "role_id": "uuid-do-role-treinador"
    },
    "organization": {
      "mode": "select",
      "organization_id": "uuid-da-org"
    }
  }'
```

**Verificar:**
- ✅ Resposta 201 Created
- ✅ Email recebido em até 1 minuto
- ✅ Assunto: "Ative seu acesso ao HB Track"
- ✅ Nome correto no email
- ✅ Organização e papel aparecem
- ✅ Botão "Criar senha" funciona

### 2. Usar o token (primeira vez - deve funcionar)

Extrair token do link no email (`?token=abc123...`):

```bash
curl -X POST "http://localhost:8000/api/v1/auth/set-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123...",
    "password": "SenhaSegura123!"
  }'
```

**Esperado:**
```json
{
  "success": true,
  "message": "Senha definida com sucesso",
  "user_id": "uuid-do-usuario"
}
```

### 3. Tentar usar token novamente (deve falhar - single-use)

```bash
curl -X POST "http://localhost:8000/api/v1/auth/set-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123...",
    "password": "OutraSenha456!"
  }'
```

**Esperado:**
```json
{
  "detail": "Token inválido ou expirado"
}
```

### 4. Verificar banco de dados

```sql
-- Verificar registro do token
SELECT 
    pr.user_id,
    pr.token_type,
    pr.used,
    pr.used_at,
    pr.expires_at,
    pr.created_at,
    u.email
FROM password_resets pr
JOIN users u ON u.id = pr.user_id
WHERE pr.token_type = 'welcome'
ORDER BY pr.created_at DESC
LIMIT 5;
```

**Esperado:**
- `used = true` após uso
- `used_at` preenchido
- `expires_at` = created_at + 24h

---

## ✅ Checklist de Implementação

### Backend
- [x] Criar `email_service_v2.py` com Dynamic Templates
- [ ] Atualizar `intake.py` com BackgroundTasks
- [ ] Criar endpoint `/auth/set-password`
- [ ] Testar localmente
- [ ] Verificar logs de envio
- [ ] Testar single-use (tentar usar token 2x)
- [ ] Testar expiração (24h)

### SendGrid Dashboard
- [ ] Criar Dynamic Template "HB Track - Ativação de Conta"
- [ ] Configurar HTML do template
- [ ] Adicionar Test Data (JSON)
- [ ] Configurar assunto: "Ative seu acesso ao HB Track"
- [ ] Preview em desktop e mobile
- [ ] Copiar Template ID
- [ ] Configurar Domain Authentication (SPF/DKIM)
- [ ] Testar envio de teste

### Configuração
- [ ] Adicionar `SENDGRID_API_KEY` no `.env`
- [ ] Adicionar `SENDGRID_INVITE_TEMPLATE_ID` no `.env`
- [ ] Adicionar `APP_PUBLIC_URL` no `.env`
- [ ] Verificar `SENDGRID_FROM_EMAIL` (no-reply@hbtrack.app)
- [ ] Verificar `SENDGRID_FROM_NAME` (HB Track)

### Testes
- [ ] Teste E2E: criar ficha → receber email → definir senha
- [ ] Teste single-use: usar token 2x deve falhar
- [ ] Teste expiração: token antigo (>24h) deve falhar
- [ ] Teste campos dinâmicos: org e role aparecem
- [ ] Teste responsivo: email legível em mobile
- [ ] Teste clientes de email: Gmail, Outlook, Apple Mail

---

## 📊 Métricas de Sucesso

### SendGrid Analytics
- **Open Rate:** Taxa de abertura do email
- **Click Rate:** Taxa de cliques no CTA
- **Bounce Rate:** Emails não entregues (<5% esperado)
- **Spam Reports:** Marcações como spam (<0.1% esperado)

### Logs Backend
- Tokens gerados vs. tokens usados
- Tempo médio para ativar conta
- Tentativas de reutilização de token

---

## 🚨 Troubleshooting

### Email não recebido
1. Verificar logs: `logger.info("Invite email queued")`
2. Verificar SendGrid Activity Feed
3. Verificar bounce rate (email inválido?)
4. Verificar spam folder

### Token inválido
1. Verificar se token expirou (>24h)
2. Verificar se já foi usado (`used = true`)
3. Verificar hash no banco vs. hash computado

### Template não renderiza
1. Verificar Template ID correto
2. Verificar campos dinâmicos (Test Data)
3. Verificar sintaxe Handlebars (`{{person_name}}`)

---

## 📚 Referências

- **SendGrid Dynamic Templates:** https://docs.sendgrid.com/ui/sending-email/how-to-send-an-email-with-dynamic-templates
- **SendGrid API Reference:** https://docs.sendgrid.com/api-reference/mail-send/mail-send
- **Template Handlebars Syntax:** https://handlebarsjs.com/guide/
- **SHA-256 Token Security:** https://datatracker.ietf.org/doc/html/rfc6238

---

**Status:** Pronto para implementação  
**Próximos passos:** 
1. Implementar código no router
2. Configurar template no SendGrid
3. Testar fluxo completo
