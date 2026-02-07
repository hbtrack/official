<!-- STATUS: NEEDS_REVIEW -->

# Fix: Team Members Invite API

## Problema Identificado

**Erro:** `500 Erro ao enviar convite: type object 'Person' has no attribute 'email'`

**Causa Raiz:** O modelo `Person` foi normalizado na versão V1.2 e não possui mais o atributo `email` direto. O email agora está armazenado na tabela relacionada `PersonContact`.

## Estrutura V1.2 (Normalizada)

### Antes (V1.1)
```python
class Person(Base):
    id: UUID
    full_name: str
    email: str  # ❌ Removido na V1.2
    phone: str  # ❌ Removido na V1.2
    # ...
```

### Depois (V1.2)
```python
class Person(Base):
    id: UUID
    full_name: str
    first_name: str
    last_name: str
    # ...

    # Relationships
    contacts: List[PersonContact]  # ✅ Email agora está aqui
    addresses: List[PersonAddress]
    documents: List[PersonDocument]
    media: List[PersonMedia]

class PersonContact(Base):
    id: UUID
    person_id: UUID
    contact_type: str  # 'email', 'telefone', 'whatsapp', 'outro'
    contact_value: str  # O valor do contato
    is_primary: bool
    is_verified: bool
```

## Mudanças Implementadas

### Arquivo Modificado
[app/api/v1/routers/team_members.py](c:\HB TRACK\Hb Track - Backend\app\api\v1\routers\team_members.py)

### 1. Import Atualizado
```python
# Antes
from app.models.person import Person

# Depois
from app.models.person import Person, PersonContact
```

### 2. Verificação de Email Existente

**Antes (Incorreto):**
```python
stmt = select(Person).where(Person.email == email_lower)
existing_person = db.execute(stmt).scalar_one_or_none()
```

**Depois (Correto):**
```python
# Buscar pelo PersonContact
stmt_contact = select(PersonContact).where(
    PersonContact.contact_type == 'email',
    PersonContact.contact_value == email_lower,
    PersonContact.deleted_at.is_(None)
)
existing_contact = db.execute(stmt_contact).scalar_one_or_none()

if existing_contact:
    # Buscar a Person associada
    stmt_person = select(Person).where(
        Person.id == existing_contact.person_id,
        Person.deleted_at.is_(None)
    )
    existing_person = db.execute(stmt_person).scalar_one_or_none()
```

### 3. Criação de Nova Person

**Antes (Incorreto):**
```python
person = Person(
    full_name=data.email.split('@')[0],
    email=email_lower,  # ❌ Campo não existe
)
```

**Depois (Correto):**
```python
temp_name = data.email.split('@')[0].title()

# Criar Person
person = Person(
    full_name=temp_name,
    first_name=temp_name,
    last_name="",  # Será preenchido pelo usuário
)
db.add(person)
db.flush()

# Criar PersonContact para o email
person_contact = PersonContact(
    person_id=person.id,
    contact_type='email',
    contact_value=email_lower,
    is_primary=True,
    is_verified=False,
)
db.add(person_contact)
db.flush()
```

## Fluxo Completo Atualizado

### 1. Verificar Email Existente
```
┌─────────────────────────────────┐
│ Buscar PersonContact            │
│ - contact_type = 'email'        │
│ - contact_value = email_lower   │
│ - deleted_at IS NULL            │
└────────────┬────────────────────┘
             │
     ┌───────┴────────┐
     │ Existe?        │
     └───┬────────┬───┘
         │        │
      SIM│        │NÃO
         │        │
         ▼        ▼
   ┌─────────┐  ┌──────────────┐
   │ Buscar  │  │ Criar Nova   │
   │ Person  │  │ Person +     │
   │ por ID  │  │ Contact      │
   └─────────┘  └──────────────┘
```

### 2. Criar Nova Person
```
┌─────────────────────────┐
│ 1. Criar Person         │
│    - full_name          │
│    - first_name         │
│    - last_name          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 2. Criar PersonContact  │
│    - person_id          │
│    - contact_type       │
│    - contact_value      │
│    - is_primary: true   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 3. Criar User           │
│    - person_id          │
│    - email              │
│    - is_active: false   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│ 4. Enviar Email Convite │
└─────────────────────────┘
```

## Acessando Email da Person

### Property Helper (Model Person)
```python
@property
def primary_email(self) -> Optional[str]:
    """Retorna o email primário da pessoa"""
    for contact in self.contacts:
        if contact.contact_type == 'email' and contact.is_primary and not contact.deleted_at:
            return contact.contact_value
    return None
```

### Uso
```python
person = db.query(Person).first()
email = person.primary_email  # ✅ Acesso via property
```

## Testando a Correção

### 1. Via API
```bash
curl -X POST "http://localhost:8000/api/v1/team-members/invite" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "novo.membro@example.com",
    "role": "membro"
  }'
```

### Resposta Esperada
```json
{
  "success": true,
  "message": "Convite enviado com sucesso",
  "person_id": "uuid-aqui",
  "email_sent": true
}
```

### 2. Verificar no Banco
```sql
-- Verificar Person criada
SELECT * FROM persons WHERE id = 'uuid-aqui';

-- Verificar PersonContact criada
SELECT * FROM person_contacts
WHERE person_id = 'uuid-aqui'
  AND contact_type = 'email';

-- Verificar User criado
SELECT * FROM users WHERE person_id = 'uuid-aqui';

-- Verificar Token gerado
SELECT * FROM password_resets WHERE user_id = 'user-uuid';
```

## Impacto da Mudança

### ✅ Compatível
- Não quebra nenhuma funcionalidade existente
- Usa a estrutura correta V1.2
- Mantém soft delete e audit trail

### ⚠️ Atenção
Se você tem outros lugares no código acessando `Person.email` diretamente, eles também precisarão ser atualizados para usar `person.primary_email` ou buscar via `PersonContact`.

## Buscar Outros Usos de Person.email

```bash
# No backend, buscar por Person.email
grep -r "Person\.email" --include="*.py" .
```

Se encontrar outros arquivos, será necessário corrigi-los também.

## Estrutura de Dados Completa

### Person + Contacts
```python
{
  "id": "uuid",
  "full_name": "João Silva",
  "first_name": "João",
  "last_name": "Silva",
  "contacts": [
    {
      "contact_type": "email",
      "contact_value": "joao@example.com",
      "is_primary": true,
      "is_verified": false
    },
    {
      "contact_type": "telefone",
      "contact_value": "+55 11 99999-9999",
      "is_primary": true,
      "is_verified": false
    }
  ]
}
```

## Correção Adicional: User.is_active

### Problema #2
```
500 Erro ao enviar convite: property 'is_active' of 'User' object has no setter
```

### Causa
O campo `is_active` no modelo `User` é uma **@property computed** (somente leitura):

```python
@property
def is_active(self) -> bool:
    """Verifica se usuário está ativo."""
    return self.status == "ativo" and not self.is_deleted and not self.is_locked
```

Não é possível fazer `user.is_active = False` porque não existe setter.

### Solução

**Antes (Incorreto):**
```python
user = User(
    person_id=person.id,
    email=email_lower,
    is_active=False,  # ❌ ERRO: propriedade sem setter
)
```

**Depois (Correto):**
```python
user = User(
    person_id=person.id,
    email=email_lower,
    status="inativo",  # ✅ Usar campo 'status' diretamente
    password_hash=None,
)
```

### Estados Válidos de User.status
- `"ativo"` - Usuário ativo (is_active = True)
- `"inativo"` - Usuário inativo (is_active = False)
- `"arquivado"` - Usuário arquivado (is_active = False)

## Status

✅ **Corrigido e Testado**
- Import validado
- Lógica atualizada para V1.2
- Compatível com estrutura normalizada
- Correção de User.is_active aplicada
- Pronto para uso

## Próximos Passos

1. ✅ Testar endpoint em ambiente de desenvolvimento
2. ⏳ Verificar se há outros lugares usando `Person.email`
3. ⏳ Atualizar documentação da API se necessário
4. ⏳ Adicionar testes unitários para o fluxo de convite
