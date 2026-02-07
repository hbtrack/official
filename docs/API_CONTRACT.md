<!-- STATUS: NEEDS_REVIEW | verificar contra openapi.json -->

# CONTRATO DA API - HB TRACKING V1

## Convenções Gerais

- **Base URL**: `/api/v1`
- **Formato**: JSON (Content-Type: application/json)
- **Timezone**: UTC (RDB3)
- **IDs**: UUID v4 (RDB1, RDB2)
- **Paginação**: `?skip=0&limit=100` (padrão: 100 itens)
- **Autenticação**: Bearer Token (FASE 7)

## Códigos de Status HTTP

| Código | Uso | Exemplo |
|--------|-----|---------|
| **200** | Sucesso (GET, PUT, PATCH) | Dados retornados |
| **201** | Criado (POST) | Recurso criado |
| **204** | Sem conteúdo (DELETE lógico) | Soft delete executado |
| **400** | Requisição inválida | Dados malformados |
| **401** | Não autenticado | Token ausente/inválido |
| **403** | Não autorizado | Papel sem permissão (R25, R26) |
| **404** | Não encontrado | Recurso inexistente |
| **409** | Conflito | Violação de constraint (RDB9, RDB10) |
| **422** | Erro de validação | Falha em regra de negócio (R, RF, RD) |
| **500** | Erro interno | Falha não tratada |

## Estrutura de Erro Padrão

```json
{
  "error_code": "MEMBERSHIP_OVERLAP",
  "message": "Vínculo sobrepõe período existente",
  "details": {
    "field": "start_date",
    "constraint": "RDB9",
    "existing_membership_id": "uuid"
  },
  "timestamp": "2025-12-24T10:30:00Z",
  "request_id": "uuid"
}
```

## Endpoints por Recurso

### 🔐 Autenticação (FASE 7)

| Método | Endpoint | Descrição | Auth |
|--------|----------|-----------|------|
| POST | `/auth/login` | Login com credenciais | Público |
| POST | `/auth/logout` | Logout (invalidar token) | Requer token |
| GET | `/auth/me` | Dados do usuário autenticado | Requer token |

### 👤 Persons (R1)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/persons` | Listar pessoas | coordenador, dirigente | - |
| GET | `/persons/{id}` | Buscar pessoa | coordenador, dirigente | - |
| POST | `/persons` | Criar pessoa | coordenador, dirigente | R1 |
| PUT | `/persons/{id}` | Atualizar pessoa | coordenador, dirigente | R1 |
| DELETE | `/persons/{id}` | Soft delete | coordenador, dirigente | RDB4 |

### 👥 Users (R2, R3)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/users` | Listar usuários | dirigente | - |
| GET | `/users/{id}` | Buscar usuário | dirigente | - |
| POST | `/users` | Criar usuário | dirigente | R2 |
| PUT | `/users/{id}` | Atualizar usuário | dirigente | R3 (superadmin imutável) |
| DELETE | `/users/{id}` | Soft delete | dirigente | R3 (superadmin não deletável) |

### 🤝 Memberships (R6, R7, RDB9)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/memberships` | Listar vínculos | coordenador, dirigente | - |
| GET | `/memberships/active` | Vínculos ativos | coordenador, dirigente | R7 |
| GET | `/memberships/{id}` | Buscar vínculo | coordenador, dirigente | - |
| POST | `/memberships` | Criar vínculo | dirigente | RDB9 (sem overlap) |
| PUT | `/memberships/{id}` | Atualizar vínculo | dirigente | RDB9 |
| POST | `/memberships/{id}/end` | Encerrar vínculo | dirigente | R7 |

### 📅 Seasons (R8, RF5, RDB8)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/seasons` | Listar temporadas | todos | - |
| GET | `/seasons/active` | Temporada ativa | todos | VIEW v_seasons_with_status |
| GET | `/seasons/{id}` | Buscar temporada | todos | - |
| POST | `/seasons` | Criar temporada | dirigente | RDB8 (sem overlap) |
| PUT | `/seasons/{id}` | Atualizar temporada | dirigente | RDB8 |
| POST | `/seasons/{id}/cancel` | Cancelar temporada | dirigente | RF5.1 |
| POST | `/seasons/{id}/interrupt` | Interromper temporada | dirigente | RF5.2 |

### 🏃 Athletes (R12, R13, R14)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/athletes` | Listar atletas | coordenador, treinador | - |
| GET | `/athletes/{id}` | Buscar atleta | coordenador, treinador | - |
| POST | `/athletes` | Criar atleta | coordenador | R12 |
| PUT | `/athletes/{id}` | Atualizar atleta | coordenador | R12 |
| POST | `/athletes/{id}/state` | Alterar estado | coordenador | R13 (ativa, lesionada, dispensada) |
| GET | `/athletes/{id}/states` | Histórico de estados | coordenador, treinador | R13 |

### 🏆 Team Registrations (R17, RDB10)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/team-registrations` | Listar inscrições | coordenador, treinador | - |
| GET | `/teams/{team_id}/registrations` | Inscrições por equipe | coordenador, treinador | - |
| POST | `/team-registrations` | Inscrever atleta | coordenador | RDB10, RD2, RD3 (validação etária) |
| PUT | `/team-registrations/{id}/end` | Encerrar inscrição | coordenador | RDB10 |

### ⚽ Matches (R19, RDB13)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/matches` | Listar jogos | todos | - |
| GET | `/matches/{id}` | Buscar jogo | todos | - |
| POST | `/matches` | Criar jogo | treinador, coordenador | R19 |
| PUT | `/matches/{id}` | Atualizar jogo | treinador, coordenador | RDB13 |
| POST | `/matches/{id}/finalize` | Finalizar jogo | treinador, coordenador | RD8 |
| POST | `/matches/{id}/reopen` | Reabrir jogo | coordenador | RF15 |
| DELETE | `/matches/{id}` | Soft delete | coordenador | R29 |

### 📊 Match Events (RD, estatísticas)

| Método | Endpoint | Descrição | Papéis | Regras |
|--------|----------|-----------|--------|--------|
| GET | `/matches/{match_id}/events` | Eventos do jogo | todos | - |
| POST | `/matches/{match_id}/events` | Adicionar evento | treinador, coordenador | RD (validações por tipo) |
| PUT | `/matches/{match_id}/events/{id}` | Corrigir evento | coordenador | R23, R24 (admin_note obrigatório) |
| DELETE | `/matches/{match_id}/events/{id}` | Soft delete evento | coordenador | RDB4 |

## Schemas Pydantic (Exemplos)

### PersonCreate (R1)

```python
class PersonCreate(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=200)
    birth_date: Optional[date] = None
    cpf: Optional[str] = Field(None, pattern=r"^\d{11}$")
```

### MembershipCreate (R6, RDB9)

```python
class MembershipCreate(BaseModel):
    person_id: UUID
    role_id: UUID
    organization_id: UUID
    season_id: UUID
    start_date: date
    end_date: Optional[date] = None

    @model_validator(mode='after')
    def validate_dates(self):
        if self.end_date and self.end_date <= self.start_date:
            raise ValueError("end_date deve ser posterior a start_date")
        return self
```

### AthleteStateCreate (R13)

```python
class AthleteStateCreate(BaseModel):
    athlete_id: UUID
    state: Literal["ativa", "lesionada", "dispensada"]
    started_at: date
    reason: Optional[str] = Field(None, max_length=500)
    admin_note: Optional[str] = None  # Obrigatório para "dispensada"

    @model_validator(mode='after')
    def validate_dispense_note(self):
        if self.state == "dispensada" and not self.admin_note:
            raise ValueError("admin_note obrigatório para dispensa (R13)")
        return self
```

## Erros de Negócio (Error Codes)

### RDB Rules

| Error Code | HTTP | Descrição | Regra |
|------------|------|-----------|-------|
| `MEMBERSHIP_OVERLAP` | 409 | Vínculo sobrepõe período existente | RDB9 |
| `TEAM_REG_OVERLAP` | 409 | Inscrição sobrepõe período existente | RDB10 |
| `SEASON_OVERLAP` | 409 | Temporada sobrepõe período existente | RDB8 |
| `SOFT_DELETE_REASON_REQUIRED` | 422 | deleted_reason obrigatório | RDB4 |

### R Rules

| Error Code | HTTP | Descrição | Regra |
|------------|------|-----------|-------|
| `SUPERADMIN_IMMUTABLE` | 403 | Super Admin não pode ser modificado | R3 |
| `SUPERADMIN_REQUIRED` | 409 | Deve existir 1 Super Admin | R3, RDB6 |
| `NO_ACTIVE_MEMBERSHIP` | 403 | Usuário sem vínculo ativo | R42, RF3 |
| `ATHLETE_DISPENSE_NO_UNDO` | 422 | Dispensa não pode ser revertida | R13 |

### RD Rules

| Error Code | HTTP | Descrição | Regra |
|------------|------|-----------|-------|
| `AGE_BELOW_CATEGORY` | 422 | Atleta abaixo da idade mínima | RD2, RD3 |
| `MATCH_ALREADY_FINALIZED` | 409 | Jogo já finalizado | RD8 |
| `CORRECTION_NOTE_REQUIRED` | 422 | admin_note obrigatório na correção | R23, R24 |

---

## Validações de Regras por Endpoint

Consultar REGRAS_SISTEMAS.md (RAG V1.1) para enforcement:

- **7.1 - Apenas no DB**: Triggers bloqueiam violações (RDB1-RDB14, R4, R20, R29, R35)
- **7.2 - DB + Backend**: Services validam regras (R1-R3, R5-R8, R11-R13, R15-R17, etc.)
- **7.3 - Apenas Backend**: Cálculos, derivações, agregações (R10, R21, R22, R26, R27, R36, RD1-RD91)
- **7.4 - Backend + Frontend**: APIs REST, validação de entrada (R9, R14, R18, RF1-RF31, RP1-RP20)
