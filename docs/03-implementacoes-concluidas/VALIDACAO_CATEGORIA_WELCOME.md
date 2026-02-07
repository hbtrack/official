<!-- STATUS: DEPRECATED | implementacao concluida -->

# Validação de Categoria no Welcome - Implementação Completa

**Data:** 14 de Janeiro de 2026
**Tipo:** Bug Fix Crítico
**Módulo:** Auth + Teams (Validação de Atletas)

---

## 1. PROBLEMA IDENTIFICADO

### 1.1. Bug Crítico
Pessoa com idade incompatível conseguia completar cadastro como atleta em categoria errada.

**Exemplo reproduzido:**
- Pessoa nascida em 1987 (39 anos em 2026)
- Convidada para equipe **Infantil** (max_age = 14 anos)
- ✅ Convite enviado com sucesso
- ✅ Email recebido com token de welcome
- ✅ Formulário de cadastro completado
- ✅ **Registro de atleta criado na categoria errada** ❌

### 1.2. Causa Raiz
O endpoint `/auth/welcome/complete` criava o registro em `athletes` **SEM validar** se a idade da pessoa era compatível com a categoria da equipe.

**Validação existente:** Função `validate_category_eligibility` em `athlete_validations.py` era usada apenas para `team_registration`, não para welcome flow.

---

## 2. REGRA DE NEGÓCIO (R15)

### 2.1. Regra Canônica
**R15 - Validação de Categoria:**
- Atleta pode jogar na sua categoria natural ou **SUPERIOR**
- Atleta **NUNCA** pode jogar em categoria inferior
- Categoria natural = menor categoria onde `idade <= max_age`
- Idade = `ano_temporada - ano_nascimento`

### 2.2. Aplicação no Welcome
**Quando validar:**
- No momento em que o membro completa o formulário de welcome
- **ANTES** de criar registro em `athletes`
- **APENAS** se o papel (role) for "atleta"

**Por que não validar no convite:**
- Convite é apenas intenção, não cria vínculos definitivos
- Permite flexibilidade administrativa
- UX melhor: pessoa descobre incompatibilidade ao tentar completar cadastro, não ao receber convite

---

## 3. IMPLEMENTAÇÃO

### 3.1. Arquivos Modificados

#### 3.1.1. Schema - `auth.py` (linha 277)
**Mudança:** Tornar `birth_date` obrigatório para todos os novos membros

```python
# ANTES
birth_date: Optional[date] = Field(None, description="Data de nascimento")

# DEPOIS
birth_date: date = Field(..., description="Data de nascimento (obrigatório)")
```

**Justificativa:** Todos os membros precisam de birth_date para auditoria e conformidade. Para atletas, é essencial para validação de categoria.

---

#### 3.1.2. Validação - `athlete_validations.py` (linha 319+)
**Mudança:** Nova função `validate_birth_date_for_team`

```python
def validate_birth_date_for_team(
    birth_date: date,
    team_id: UUID,
    season_year: int,
    db: Session,
    role_code: str
) -> None:
    """
    Valida se a data de nascimento é compatível com a categoria da equipe.
    
    Regra R15: Atleta só pode jogar na categoria natural ou superior, NUNCA inferior.
    Esta validação ocorre no fluxo de welcome_complete ANTES de criar registro em athletes.
    
    Args:
        birth_date: Data de nascimento do novo membro
        team_id: ID da equipe
        season_year: Ano da temporada ativa
        db: Sessão do banco de dados
        role_code: Código do papel (ex: "atleta", "treinador")
        
    Raises:
        ValidationError: Se data de nascimento incompatível com categoria da equipe
    """
    # Validar APENAS se for atleta
    if role_code != "atleta":
        return
    
    # Buscar equipe
    team = db.get(Team, team_id)
    if not team:
        raise ValidationError("Equipe não encontrada")
    
    # Verificar se equipe tem categoria definida
    if not team.category_id:
        raise ValidationError("Equipe não possui categoria definida")
    
    # Buscar categoria da equipe
    team_category = db.get(Category, team.category_id)
    if not team_category:
        raise ValidationError("Categoria da equipe não encontrada")
    
    # Calcular categoria natural do atleta
    athlete_category = calculate_athlete_category(
        birth_date,
        season_year,
        db
    )
    
    if not athlete_category:
        raise ValidationError("Não foi possível determinar categoria para esta data de nascimento")
    
    # Aplicar regra R15: categoria_natural <= categoria_equipe
    # Se max_age da categoria natural > max_age da categoria da equipe, significa que
    # o atleta é mais velho e está tentando jogar em categoria inferior (BLOQUEADO)
    if athlete_category.max_age > team_category.max_age:
        raise ValidationError(
            f"Não foi possível completar o cadastro! Sua idade não corresponde à "
            f"categoria {team_category.name} (até {team_category.max_age} anos). "
            f"Por favor, verifique com o administrador."
        )
```

**Características:**
- ✅ Validação apenas para atletas (early return para outros papéis)
- ✅ Reutiliza `calculate_athlete_category` (DRY)
- ✅ Mensagem de erro clara e orientada ao usuário
- ✅ Inclui nome da categoria e idade máxima na mensagem

---

#### 3.1.3. Endpoint - `auth.py` (welcome_complete)

**Mudança 1:** Adicionar imports (linha 24, 1499)
```python
# Linha 24
from sqlalchemy.orm import Session, joinedload

# Linha 1499
from app.core.athlete_validations import validate_birth_date_for_team
from app.core.exceptions import ValidationError
```

**Mudança 2:** Otimizar query com eager loading (linha 1625)
```python
# ANTES
team_memberships = db.query(TeamMembership).filter(
    TeamMembership.person_id == user.person_id,
    TeamMembership.status == "pendente",
    TeamMembership.deleted_at.is_(None),
).all()

# DEPOIS
team_memberships = db.query(TeamMembership).options(
    joinedload(TeamMembership.team),
    joinedload(TeamMembership.org_membership).joinedload(OrgMembership.role)
).filter(
    TeamMembership.person_id == user.person_id,
    TeamMembership.status == "pendente",
    TeamMembership.deleted_at.is_(None),
).all()
```

**Benefício:** Reduz N+1 queries ao carregar team e role junto com memberships.

**Mudança 3:** Buscar temporada ativa e validar categoria (linha 1668+)
```python
# Buscar temporada ativa e validar categoria se for atleta
if team and role_code == "atleta":
    active_season = db.query(Season).filter(
        Season.organization_id == team.organization_id,
        Season.status == 'ativa',
        Season.deleted_at.is_(None)
    ).first()
    
    if not active_season:
        raise HTTPException(
            status_code=400,
            detail={"message": "Não há temporada ativa para esta organização", "code": "NO_ACTIVE_SEASON"}
        )
    
    # Validar categoria antes de criar Athlete
    try:
        validate_birth_date_for_team(
            birth_date=payload.birth_date,
            team_id=team_membership.team_id,
            season_year=active_season.year,
            db=db,
            role_code=role_code
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"message": str(e), "code": "CATEGORY_VALIDATION_FAILED"}
        )
```

**Lógica:**
1. Validação ocorre **APÓS** determinar `role_code` (linha ~1670-1695)
2. Validação ocorre **ANTES** de criar registro `Athlete` (linha ~1580)
3. Busca temporada ativa da organização
4. Chama `validate_birth_date_for_team` com todos os parâmetros necessários
5. Captura `ValidationError` e converte para `HTTPException 400`

---

## 4. FLUXO COMPLETO (APÓS CORREÇÃO)

### 4.1. Fluxo de Sucesso
```
1. Admin envia convite para atleta → TeamMembership criado (status=pendente)
2. Atleta recebe email com token
3. Atleta acessa /welcome?token=...
4. Backend verifica token
5. Atleta preenche formulário (nome, senha, BIRTH_DATE obrigatório)
6. Atleta submete formulário → POST /auth/welcome/complete
7. Backend:
   a) Valida token
   b) Busca TeamMembership pendente
   c) Busca team e role
   d) Busca temporada ativa
   e) ✅ VALIDA CATEGORIA (se role=atleta)
   f) Atualiza Person com dados
   g) Cria registro Athlete (se passou validação)
   h) Ativa TeamMembership (status → ativo)
   i) Marca token como usado
   j) Cria sessão automática
8. Atleta redirecionado para /teams/{teamId}/overview
```

### 4.2. Fluxo de Erro (Idade Incompatível)
```
1-6. [Mesmo fluxo até submeter formulário]
7. Backend:
   a) Valida token ✅
   b) Busca TeamMembership pendente ✅
   c) Busca team e role ✅
   d) Busca temporada ativa ✅
   e) ❌ VALIDAÇÃO FALHA:
      - Calcula categoria natural: Adulto (max_age=99, pois nasceu 1987)
      - Categoria da equipe: Infantil (max_age=14)
      - Aplica R15: 99 > 14 → BLOQUEIA
   f) Retorna HTTP 400:
      {
        "message": "Não foi possível completar o cadastro! Sua idade não 
                    corresponde à categoria Infantil (até 14 anos). Por 
                    favor, verifique com o administrador.",
        "code": "CATEGORY_VALIDATION_FAILED"
      }
8. Frontend mostra mensagem de erro
9. TeamMembership permanece "pendente"
10. Registro Athlete NÃO é criado
```

---

## 5. TESTES

### 5.1. Casos de Teste Recomendados

#### Teste 1: Atleta com idade correta
```
Cenário: Pessoa nascida em 2010 (16 anos) para equipe Sub-17 (max_age=17)
Categoria natural: Sub-17 (idade 16 <= 17)
Categoria equipe: Sub-17
Regra R15: 17 <= 17 ✅
Resultado esperado: Cadastro completo com sucesso
```

#### Teste 2: Atleta com idade inferior (categoria superior)
```
Cenário: Pessoa nascida em 2012 (14 anos) para equipe Sub-17 (max_age=17)
Categoria natural: Infantil (max_age=14)
Categoria equipe: Sub-17
Regra R15: 14 < 17 ✅
Resultado esperado: Cadastro completo com sucesso (pode jogar em categoria superior)
```

#### Teste 3: Atleta com idade superior (categoria inferior) ❌
```
Cenário: Pessoa nascida em 2008 (18 anos) para equipe Sub-17 (max_age=17)
Categoria natural: Adulto (max_age=99)
Categoria equipe: Sub-17
Regra R15: 99 > 17 ❌ BLOQUEADO
Resultado esperado: HTTP 400 "Sua idade não corresponde à categoria Sub-17"
```

#### Teste 4: Treinador com qualquer idade
```
Cenário: Pessoa nascida em 1985 (41 anos) para equipe Sub-14, role=treinador
Validação: role_code != "atleta" → return early
Resultado esperado: Cadastro completo com sucesso (validação não se aplica)
```

#### Teste 5: Sem temporada ativa
```
Cenário: Organização sem temporada ativa
Resultado esperado: HTTP 400 "Não há temporada ativa para esta organização"
```

### 5.2. Integração com Testes E2E
Arquivo: `tests/e2e/teams/teams.welcome.spec.ts`

**Adicionar teste:**
```typescript
test('deve bloquear cadastro de atleta com idade incompatível', async ({ request, page }) => {
  // 1. Admin cria equipe Sub-14
  const teamId = await createTeamViaAPI(request, { 
    name: 'E2E-Sub14-Validation',
    category_id: 2 // Infantil (max_age=14)
  });
  
  // 2. Admin convida pessoa com email específico, role=atleta
  const email = 'atleta_velho@teste.com';
  await createTeamInviteViaAPI(request, teamId, email, 'atleta');
  
  // 3. Obter token via API de teste
  const tokenData = await getWelcomeTokenViaTestAPI(request, email);
  
  // 4. Acessar página de welcome
  await page.goto(`/welcome?token=${tokenData.token}`);
  
  // 5. Preencher formulário com data de nascimento incompatível
  await page.fill('[data-testid="full-name-input"]', 'Atleta Velho');
  await page.fill('[data-testid="birth-date-input"]', '1987-05-15'); // 39 anos
  await page.fill('[data-testid="password-input"]', 'Senha123!');
  await page.fill('[data-testid="confirm-password-input"]', 'Senha123!');
  
  // 6. Submeter formulário
  await page.click('[data-testid="welcome-submit-btn"]');
  
  // 7. Verificar mensagem de erro
  await expect(page.locator('[data-testid="welcome-error"]')).toContainText(
    /idade não corresponde à categoria/i
  );
  
  // 8. Verificar que atleta NÃO foi criado
  const athletes = await listAthletesViaAPI(request, teamId);
  expect(athletes.items).toHaveLength(0);
  
  // Cleanup
  await deleteTeamViaAPI(request, teamId);
});
```

---

## 6. IMPACTO E BENEFÍCIOS

### 6.1. Segurança
- ✅ Previne cadastros inválidos de atletas
- ✅ Garante integridade de dados (categoria vs idade)
- ✅ Conformidade com regras de competição

### 6.2. UX
- ✅ Mensagem clara para o usuário ("Sua idade não corresponde...")
- ✅ Usuário descobre problema no momento certo (ao completar cadastro)
- ✅ Não bloqueia envio de convite (flexibilidade administrativa)

### 6.3. Performance
- ✅ Eager loading reduz N+1 queries em welcome flow
- ✅ Validação eficiente (apenas 2 queries extras: season + category)

### 6.4. Manutenibilidade
- ✅ Reutiliza `calculate_athlete_category` existente (DRY)
- ✅ Validação centralizada em `athlete_validations.py`
- ✅ Fácil adicionar validações similares para outros papéis

---

## 7. DECISÕES DE DESIGN

### 7.1. Por que birth_date obrigatório para todos?
**Decisão:** Tornar `birth_date` obrigatório no schema `WelcomeCompleteRequest`

**Alternativas consideradas:**
1. ❌ Opcional para todos, validar apenas se fornecido
2. ❌ Obrigatório apenas para atletas (validação condicional no schema)
3. ✅ **Obrigatório para todos**

**Justificativa:**
- Todos os membros (atletas, treinadores, coordenadores) devem ter birth_date para auditoria
- Simplifica validação (não precisa lidar com `None`)
- Alinhado com boas práticas de compliance (LGPD, controle de menores)

### 7.2. Por que validar no welcome e não no convite?
**Decisão:** Validação ocorre em `/auth/welcome/complete`, não em `/teams/{teamId}/invites`

**Justificativa:**
- Convite é apenas intenção, não cria vínculo definitivo
- Permite flexibilidade: admin pode convidar antes de ter certeza da categoria
- UX: pessoa descobre incompatibilidade ao tentar se cadastrar, com mensagem clara
- Evita bloqueio administrativo (admin pode ajustar categoria da equipe antes do membro completar welcome)

### 7.3. Por que usar temporada ativa?
**Decisão:** Usar `Season.status='ativa'` para determinar `season_year`

**Alternativas consideradas:**
1. ❌ Usar `datetime.now().year` sempre
2. ✅ **Usar temporada ativa da organização**
3. ❌ Usar temporada da equipe

**Justificativa:**
- Temporada ativa reflete período competitivo real
- Organização sempre tem temporada ativa (se tem equipes, tem temporada)
- Validação mais precisa (ex: temporada 2025/2026 pode ter ano diferente de `now().year`)
- Alinhado com outras validações do sistema

---

## 8. CHECKLIST DE IMPLEMENTAÇÃO

- [x] **Schema:** Tornar `birth_date` obrigatório em `WelcomeCompleteRequest`
- [x] **Validação:** Criar função `validate_birth_date_for_team` em `athlete_validations.py`
- [x] **Imports:** Adicionar `joinedload`, `validate_birth_date_for_team`, `ValidationError` em `auth.py`
- [x] **Query:** Adicionar eager loading em `TeamMembership` query
- [x] **Busca:** Adicionar busca de temporada ativa após determinar `team` e `role_code`
- [x] **Validação:** Adicionar chamada de `validate_birth_date_for_team` antes de criar `Athlete`
- [x] **Erro:** Capturar `ValidationError` e retornar HTTP 400 com mensagem clara
- [ ] **Testes:** Adicionar casos de teste em `teams.welcome.spec.ts`
- [ ] **Documentação:** Atualizar `teams-CONTRACT.md` com nova validação
- [ ] **Seeds:** Criar seeds com atletas de idades variadas para testes
- [ ] **E2E:** Validar fluxo completo em ambiente de staging

---

## 9. PRÓXIMOS PASSOS

1. **Testes E2E:** Implementar casos de teste em `teams.welcome.spec.ts`
2. **Seeds:** Adicionar pessoas com idades variadas em `seed_e2e.py`
3. **Documentação:** Atualizar contrato em `teams-CONTRACT.md`
4. **Frontend:** Adicionar mensagem de erro específica no componente Welcome
5. **Monitoramento:** Adicionar log de tentativas bloqueadas para auditoria

---

**Status:** ✅ Implementação Completa (Backend)
**Pendente:** Testes E2E, Seeds, Documentação Contrato
