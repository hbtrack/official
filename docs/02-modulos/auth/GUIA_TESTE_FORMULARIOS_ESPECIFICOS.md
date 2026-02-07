<!-- STATUS: DEPRECATED | razao: guia de teste, nao referencia canonica -->

# 🧪 Guia Rápido - Testar Formulários Específicos

## Status: ✅ Implementação Concluída

---

## 🎯 O Que Foi Implementado

**4 formulários diferentes** baseados no tipo de convite:

1. **AthleteProfileForm** - Para atletas (altura, peso, posições)
2. **CoachProfileForm** - Para treinadores (certificações, especialização)
3. **CoordinatorProfileForm** - Para coordenadores (área de atuação)
4. **GenericProfileForm** - Para membro/dirigente (campos básicos)

---

## 🚀 Como Testar

### Pré-requisito: Backend e Frontend Rodando

```powershell
# Backend
cd "c:\HB TRACK\Hb Track - Backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (outro terminal)
cd "c:\HB TRACK\Hb Track - Fronted"
npm run dev
```

---

## 📋 Teste 1: Convite de Atleta

### 1. Login como Dirigente
- URL: http://localhost:3000/signin
- Email: `e2e.dirigente@teste.com`
- Senha: `Admin@123`

### 2. Criar Convite de Atleta

**Opção A - Via API (mais fácil para testar)**:

Abrir PowerShell e executar:

```powershell
# Fazer login e obter token
$loginResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"email":"e2e.dirigente@teste.com","password":"Admin@123"}' `
  -SessionVariable session

# Obter ID da primeira equipe
$teamsResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/teams" `
  -Method GET `
  -WebSession $session

$teams = ($teamsResponse.Content | ConvertFrom-Json).items
$teamId = $teams[0].id

# Enviar convite de ATLETA
$inviteResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/teams/$teamId/invites" `
  -Method POST `
  -ContentType "application/json" `
  -WebSession $session `
  -Body '{"email":"atleta.teste@teste.com","invitee_kind":"athlete","role":"atleta"}'

Write-Host "Convite enviado! Atleta: atleta.teste@teste.com"
```

**Opção B - Via UI (requer mudança temporária)**:

Atualmente a UI envia `invitee_kind` baseado no `role` selecionado. Você pode:
1. Abrir DevTools (F12)
2. Na aba Network, interceptar o POST do convite
3. Editar o payload para incluir `"invitee_kind": "athlete"`

### 3. Buscar Token de Welcome

```powershell
# Conectar ao banco e buscar token
$env:PGPASSWORD='hbtrack_dev_pwd'
$token = psql -h localhost -p 5433 -U hbtrack_dev -d hb_track_e2e -t -c "SELECT token FROM password_resets WHERE token_type='welcome' AND used=false ORDER BY created_at DESC LIMIT 1;"
$token = $token.Trim()

Write-Host "Token: $token"
Write-Host "Link: http://localhost:3000/welcome?token=$token"
```

### 4. Acessar Link de Welcome

Copiar o link gerado e abrir no navegador.

### 5. Validar Formulário de Atleta

✅ **Deve exibir**:
- Campos básicos: Nome, Telefone, Data Nascimento, Gênero
- **Seção "Informações do Atleta"**:
  - Altura (cm)
  - Peso (kg)
  - Lateralidade (destro/canhoto/ambidestro)
  - Posições (múltipla escolha com botões)

### 6. Preencher e Completar

```
Nome: João Silva Atleta
Telefone: (11) 98765-4321
Data Nascimento: 2005-03-15
Gênero: masculino
Altura: 185
Peso: 78
Lateralidade: destro
Posições: Ponta Direita, Armador Central
```

Clicar em **"Concluir Cadastro"**

### 7. Validações Finais

✅ Deve redirecionar para `/inicio`  
✅ Top bar deve mostrar o nome "João Silva Atleta"  
✅ Papel deve aparecer correto

**Verificar no Banco**:
```powershell
$env:PGPASSWORD='hbtrack_dev_pwd'
psql -h localhost -p 5433 -U hbtrack_dev -d hb_track_e2e -c "
SELECT a.id, p.full_name, a.height, a.weight, a.laterality 
FROM athletes a 
JOIN persons p ON a.person_id = p.id 
WHERE p.full_name LIKE '%João Silva%';
"
```

✅ Deve retornar o atleta com altura, peso e lateralidade preenchidos

---

## 📋 Teste 2: Convite de Treinador

### 1. Enviar Convite via API

```powershell
# (Assumindo session já criada no Teste 1)
$inviteResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/teams/$teamId/invites" `
  -Method POST `
  -ContentType "application/json" `
  -WebSession $session `
  -Body '{"email":"treinador.teste@teste.com","invitee_kind":"coach","role":"treinador"}'
```

### 2. Buscar Token

```powershell
$token = psql -h localhost -p 5433 -U hbtrack_dev -d hb_track_e2e -t -c "SELECT token FROM password_resets WHERE token_type='welcome' AND used=false ORDER BY created_at DESC LIMIT 1;"
$token = $token.Trim()
Write-Host "http://localhost:3000/welcome?token=$token"
```

### 3. Validar Formulário de Treinador

✅ **Deve exibir**:
- Campos básicos
- **Seção "Informações Profissionais"**:
  - Certificações (textarea)
  - Especialização (select: Treinador Principal, Auxiliar, Preparador Físico, etc.)

### 4. Preencher

```
Nome: Maria Costa Treinadora
Certificações: CBHb Nível 1, CBHb Nível 2, Curso de Metodologia
Especialização: Treinador Principal
```

### 5. Validar Metadata

```powershell
$env:PGPASSWORD='hbtrack_dev_pwd'
psql -h localhost -p 5433 -U hbtrack_dev -d hb_track_e2e -c "
SELECT p.full_name, p.metadata 
FROM persons p 
WHERE p.full_name LIKE '%Maria Costa%';
"
```

✅ Metadata deve conter:
```json
{
  "certifications": "CBHb Nível 1, CBHb Nível 2, Curso de Metodologia",
  "specialization": "treinador_principal"
}
```

---

## 📋 Teste 3: Convite de Coordenador

### 1. Enviar Convite

```powershell
$inviteResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/teams/$teamId/invites" `
  -Method POST `
  -ContentType "application/json" `
  -WebSession $session `
  -Body '{"email":"coordenador.teste@teste.com","invitee_kind":"coordinator","role":"coordenador"}'
```

### 2. Validar Formulário

✅ **Seção "Informações de Coordenação"**:
- Área de Atuação (select: Coordenação Técnica, de Categorias, Administrativa, etc.)

### 3. Preencher

```
Nome: Pedro Santos Coordenador
Área de Atuação: Coordenação Técnica
```

---

## 📋 Teste 4: Convite de Membro (Genérico)

### 1. Enviar Convite

```powershell
$inviteResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/teams/$teamId/invites" `
  -Method POST `
  -ContentType "application/json" `
  -WebSession $session `
  -Body '{"email":"membro.teste@teste.com","role":"membro"}'
```

**Nota**: Sem `invitee_kind` ou com qualquer valor diferente de "athlete/coach/coordinator" → usa GenericProfileForm

### 2. Validar Formulário

✅ **Apenas campos básicos**:
- Nome, Telefone, Data Nascimento, Gênero
- **SEM** campos extras

---

## 🔍 Checklist de Validação Completa

### Frontend
- [ ] Atleta: formulário mostra altura/peso/posições
- [ ] Treinador: formulário mostra certificações/especialização
- [ ] Coordenador: formulário mostra área de atuação
- [ ] Membro: formulário genérico (sem extras)
- [ ] Todos redirecionam para `/inicio`
- [ ] Loading states funcionam
- [ ] Erros são exibidos corretamente

### Backend
- [ ] Atleta: registro criado em `athletes` table
- [ ] Atleta: posições linkadas em `athlete_positions`
- [ ] Treinador: metadata salva em `persons.metadata`
- [ ] Coordenador: metadata salva em `persons.metadata`
- [ ] Token marcado como `used=true` após sucesso
- [ ] TeamMembership status muda para "ativo"
- [ ] Cookies JWT são criados corretamente

### UX
- [ ] Stepper mostra "Senha" → "Perfil" corretamente
- [ ] Botão "Voltar" funciona
- [ ] Botão submit desabilita durante envio
- [ ] Mensagens de erro são claras
- [ ] Dark mode funciona em todos os forms

---

## 🐛 Troubleshooting

### Problema: "invitee_kind não está sendo enviado"

**Solução Temporária**: Enviar convites via API (PowerShell) conforme exemplos acima.

**Solução Permanente**: Atualizar `MembersTab.tsx` para incluir campo `invitee_kind` no modal de convite baseado no `role` selecionado.

### Problema: "Formulário genérico aparece para atleta"

**Causa**: Backend não retornou `invitee_kind` correto no `/welcome/verify`

**Verificar**:
```sql
SELECT email, metadata FROM password_resets 
WHERE token_type='welcome' 
ORDER BY created_at DESC LIMIT 5;
```

O campo `metadata` deve conter `{"invitee_kind": "athlete"}`

---

## 📊 Resultados Esperados

### Teste Completo - 4 Convites

| Papel | Email | Formulário | Campos Extras |
|-------|-------|-----------|---------------|
| Atleta | atleta.teste@teste.com | AthleteProfileForm | ✅ altura/peso/posições |
| Treinador | treinador.teste@teste.com | CoachProfileForm | ✅ certificações/especialização |
| Coordenador | coordenador.teste@teste.com | CoordinatorProfileForm | ✅ área de atuação |
| Membro | membro.teste@teste.com | GenericProfileForm | ❌ sem extras |

**Todos redirecionam para `/inicio` após sucesso** ✅

---

**Status**: 🟢 **PRONTO PARA TESTE**  
**Próximo**: Implementar Etapa 3 (separar MembersTab)
