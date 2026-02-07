<!-- STATUS: DEPRECATED | arquivado -->

# Análise de Cobertura: Backend vs Frontend

## ✅ Endpoints de Autenticação - COMPLETO

Todos os 10 endpoints de autenticação estão implementados no frontend:

1. ✅ POST `/auth/login` - `loginAction()`
2. ✅ GET `/auth/me` - `getMeAction()`
3. ✅ GET `/auth/permissions` - `getPermissionsAction()`
4. ✅ GET `/auth/context` - `getContextAction()`
5. ✅ POST `/auth/logout` - `logoutAction()`
6. ✅ POST `/auth/forgot-password` - (já existia)
7. ✅ POST `/auth/reset-password` - (já existia)
8. ✅ POST `/auth/set-password` - `setPasswordAction()`
9. ✅ POST `/auth/change-password` - `changePasswordAction()`
10. ✅ POST `/auth/initial-setup` - `initialSetupAction()`

---

## 📊 Outros Routers do Backend

### ✅ **Reports** - IMPLEMENTADO
📁 Frontend: `lib/reports/actions.ts`

Endpoints implementados:
- Training Performance Reports (R1)
- Athlete Individual Reports (R2)
- Wellness Summary Reports (R3)
- Medical Summary Reports (R4)

---

## ⚠️ Routers SEM Server Actions no Frontend

### 1. **Athletes** (`/athletes`)
**Backend:** 8 endpoints
- GET `/athletes` - Listar atletas (com paginação)
- GET `/athletes/stats` - Estatísticas de atletas
- GET `/athletes/available-today` - Atletas disponíveis hoje
- POST `/athletes` - Criar atleta
- GET `/athletes/{id}` - Buscar atleta por ID
- PATCH `/athletes/{id}` - Atualizar atleta
- DELETE `/athletes/{id}` - Deletar atleta
- GET `/athletes/{id}/history` - Histórico do atleta

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - CRUD básico de atletas

---

### 2. **Teams** (`/teams`)
**Backend:** 6 endpoints
- GET `/teams` - Listar equipes
- POST `/teams` - Criar equipe
- GET `/teams/{id}` - Buscar equipe
- PATCH `/teams/{id}` - Atualizar equipe
- DELETE `/teams/{id}` - Deletar equipe
- POST `/teams/{id}/coaches` - Adicionar treinador

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - CRUD básico de equipes

---

### 3. **Seasons** (`/seasons`)
**Backend:** 7 endpoints
- GET `/seasons` - Listar temporadas
- POST `/seasons` - Criar temporada
- GET `/seasons/{id}` - Buscar temporada
- PATCH `/seasons/{id}` - Atualizar temporada
- POST `/seasons/{id}/activate` - Ativar temporada
- POST `/seasons/{id}/close` - Fechar temporada
- DELETE `/seasons/{id}` - Deletar temporada

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Gerenciamento de temporadas

---

### 4. **Organizations** (`/organizations`)
**Backend:** 4 endpoints
- GET `/organizations` - Listar organizações
- POST `/organizations` - Criar organização
- GET `/organizations/{id}` - Buscar organização
- PATCH `/organizations/{id}` - Atualizar organização

**Frontend:** ❌ Não há server actions
**Impacto:** Baixo - Apenas para superadmin (initial-setup já cobre dirigente)

---

### 5. **Users** (`/users`)
**Backend:** 7 endpoints
- GET `/users` - Listar usuários
- POST `/users` - Criar usuário
- GET `/users/by-email/{email}` - Buscar por email
- GET `/users/{id}` - Buscar usuário
- PATCH `/users/{id}` - Atualizar usuário
- DELETE `/users/{id}` - Deletar usuário
- POST `/users/{id}/resend-welcome` - Reenviar email de boas-vindas

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Gerenciamento de usuários

---

### 6. **Memberships** (`/memberships`, `/organizations/{org_id}/memberships`)
**Backend:** 3 endpoints
- GET `/organizations/{org_id}/memberships` - Listar vínculos
- PATCH `/memberships/{id}` - Atualizar vínculo
- POST `/organizations/{org_id}/memberships` - Criar vínculo

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Gerenciamento de vínculos organização-usuário

---

### 7. **Training Sessions** (`/training-sessions`)
**Backend:** 6 endpoints
- GET `/training-sessions` - Listar treinos
- POST `/training-sessions` - Criar treino
- GET `/training-sessions/{id}` - Buscar treino
- PATCH `/training-sessions/{id}` - Atualizar treino
- DELETE `/training-sessions/{id}` - Deletar treino
- POST `/training-sessions/{id}/finalize` - Finalizar treino

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - CRUD de treinos

---

### 8. **Matches** (`/matches`)
**Backend:** 8 endpoints
- GET `/matches` - Listar jogos
- POST `/matches` - Criar jogo
- GET `/matches/upcoming` - Próximos jogos
- GET `/matches/{id}` - Buscar jogo
- PATCH `/matches/{id}` - Atualizar jogo
- POST `/matches/{id}/start` - Iniciar jogo
- DELETE `/matches/{id}` - Deletar jogo
- POST `/matches/{id}/finalize` - Finalizar jogo

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - CRUD de jogos

---

### 9. **Match Events** (`/matches/{match_id}/events`)
**Backend:** 7 endpoints
- GET `/matches/{match_id}/events` - Listar eventos
- POST `/matches/{match_id}/events` - Criar evento
- PATCH `/matches/{match_id}/events/{id}` - Atualizar evento
- POST `/matches/{match_id}/events/{id}/validate` - Validar evento
- DELETE `/matches/{match_id}/events/{id}` - Deletar evento
- GET `/matches/{match_id}/statistics` - Estatísticas do jogo
- POST `/matches/{match_id}/statistics/export` - Exportar estatísticas

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Registro de eventos em jogos (gols, faltas, etc)

---

### 10. **Attendance** (`/teams/{team_id}/trainings/{training_id}/attendance`)
**Backend:** 3 endpoints
- GET - Listar presenças
- POST - Registrar presença
- PATCH - Atualizar presença

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Controle de presença em treinos

---

### 11. **Match Attendance** (`/teams/{team_id}/matches/{match_id}/attendance`)
**Backend:** Similar ao Attendance

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Controle de presença em jogos

---

### 12. **Match Roster** (`/teams/{team_id}/matches/{match_id}/roster`)
**Backend:** 3 endpoints
- GET - Listar convocação
- POST - Convocar atleta
- PATCH - Atualizar convocação

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Convocação para jogos

---

### 13. **Match Teams** (`/teams/{team_id}/matches/{match_id}/teams`)
**Backend:** 3 endpoints
- GET - Listar equipes do jogo
- POST - Adicionar equipe
- PATCH - Atualizar equipe

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Configuração de equipes em jogos

---

### 14. **Team Registrations** (`/teams/{team_id}/registrations`)
**Backend:** 4 endpoints
- GET - Listar inscrições
- POST - Criar inscrição
- PATCH - Atualizar inscrição
- GET `/{registration_id}` - Buscar inscrição

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Inscrição de atletas em equipes

---

### 15. **Wellness Pre** (`/wellness-pre`)
**Backend:** 4 endpoints
- GET - Listar registros pré-treino
- POST - Criar registro
- GET `/{id}` - Buscar registro
- PATCH `/{id}` - Atualizar registro

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Avaliação pré-treino (fadiga, sono, etc)

---

### 16. **Wellness Post** (`/wellness-post`)
**Backend:** 4 endpoints
- GET - Listar registros pós-treino
- POST - Criar registro
- GET `/{id}` - Buscar registro
- PATCH `/{id}` - Atualizar registro

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Avaliação pós-treino (RPE, dor muscular, etc)

---

### 17. **Intake (Ficha Única)** (`/intake`)
**Backend:** 8 endpoints
- POST `/intake/person` - Criar pessoa
- POST `/intake/athlete` - Criar atleta
- POST `/intake/person-athlete` - Criar pessoa + atleta
- GET `/intake/status/{person_id}` - Status do cadastro
- GET `/intake/completeness/{person_id}` - Completude do cadastro
- GET `/intake/pendencies/{person_id}` - Pendências
- POST `/intake/guardian/{person_id}` - Adicionar responsável
- POST `/intake/medical/{person_id}` - Adicionar dados médicos

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Cadastro unificado (Ficha Única)

---

### 18. **Athlete Import** (`/athletes/import`)
**Backend:** 3 endpoints
- GET `/template` - Download de template Excel
- POST `/validate` - Validar arquivo
- POST - Importar atletas

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Importação em massa de atletas

---

### 19. **Athlete States** (`/athletes/{athlete_id}/states`)
**Backend:** 2 endpoints
- GET - Listar histórico de estados
- POST - Criar novo estado (ativo, lesionado, suspenso, etc)

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Controle de estado de atletas (lesões, suspensões)

---

### 20. **Alerts** (`/alerts`)
**Backend:** 2 endpoints
- GET `/alerts` - Listar alertas (sobrecarga, lesões)
- GET `/alerts/summary` - Resumo de alertas

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Sistema de alertas (RP8)

---

### 21. **Persons** (`/persons`)
**Backend:** 20+ endpoints
- CRUD completo de pessoas
- Contatos, endereços, documentos, mídias

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Gestão de pessoas (separado de atletas)

---

### 22. **Lookup** (`/lookup`)
**Backend:** 7 endpoints
- GET `/positions/offensive` - Posições ofensivas
- GET `/positions/defensive` - Posições defensivas
- GET `/categories` - Categorias
- GET `/schooling-levels` - Níveis de escolaridade
- GET `/organizations` - Organizações (lookup)
- GET `/seasons` - Temporadas (lookup)
- GET `/teams` - Equipes (lookup)

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Tabelas de referência para formulários

---

### 23. **Media** (`/media`)
**Backend:** 2 endpoints
- GET `/media/images/{image_id}` - Buscar imagem
- GET `/media/list/{entity_type}/{entity_id}` - Listar mídias de entidade

**Frontend:** ❌ Não há server actions
**Impacto:** Baixo - Integração com Cloudinary (upload provavelmente via client-side)

---

### 24. **Dashboard** (`/dashboard`)
**Backend:** 3 endpoints
- GET `/dashboard/overview` - Visão geral otimizada
- POST `/dashboard/custom` - Dashboard customizado
- GET `/dashboard/health-check` - Health check do dashboard

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Dashboard principal do sistema

---

### 25. **Positions** (`/positions`)
**Backend:** 3 endpoints
- GET `/positions` - Listar posições
- GET `/positions/{id}` - Buscar posição
- GET `/positions/by-type/{type}` - Buscar por tipo

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Gestão de posições

---

### 26. **Categories** (`/categories`)
**Backend:** 4 endpoints
- GET - Listar categorias
- POST - Criar categoria
- GET `/{id}` - Buscar categoria
- PUT `/{id}` - Atualizar categoria

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Gestão de categorias

---

### 27. **Roles** (`/roles`)
**Backend:** 3 endpoints
- GET `/roles` - Listar roles
- GET `/roles/{id}` - Buscar role
- GET `/roles/{role_name}/permissions` - Permissões da role

**Frontend:** ❌ Não há server actions
**Impacto:** Baixo - Gerenciamento de roles (provavelmente só admin)

---

### 28. **Permissions** (`/permissions`)
**Backend:** 2 endpoints
- GET `/permissions` - Listar todas as permissões
- GET `/permissions/by-role/{role_name}` - Permissões por role

**Frontend:** ❌ Não há server actions
**Impacto:** Baixo - Gerenciamento de permissões (provavelmente só admin)

---

### 29. **Competitions** (`/competitions`)
**Backend:** 4 endpoints
- GET - Listar competições
- POST - Criar competição
- GET `/{id}` - Buscar competição
- PATCH `/{id}` - Atualizar competição

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Gestão de competições

---

### 30. **Competition Seasons** (`/competition-seasons`)
**Backend:** 5 endpoints
- GET - Listar temporadas de competição
- POST - Criar temporada de competição
- GET `/{id}` - Buscar temporada
- PATCH `/{id}` - Atualizar temporada
- GET `/{id}/matches` - Jogos da temporada

**Frontend:** ❌ Não há server actions
**Impacto:** Médio - Gestão de competições por temporada

---

### 31. **Audit Logs** (`/audit-logs`)
**Backend:** 2 endpoints
- GET `/audit-logs` - Listar logs de auditoria
- GET `/audit-logs/{id}` - Buscar log específico

**Frontend:** ❌ Não há server actions
**Impacto:** Baixo - Auditoria (R31-R32, provavelmente só admin)

---

### 32. **Unified Registration** (`/unified-registration`)
**Backend:** 2 endpoints
- POST `/unified-registration` - Cadastro unificado
- GET `/unified-registration/{person_id}` - Buscar cadastro

**Frontend:** ❌ Não há server actions
**Impacto:** Alto - Sistema de cadastro unificado (legacy?)

---

### 33. **Admin Neon** (`/admin/neon`)
**Backend:** 4 endpoints (administrativos)
- GET `/neon/check-and-seed` - Verificar e popular banco
- GET `/health/utc-season` - Health check de temporadas
- GET `/cache/stats` - Estatísticas de cache
- POST `/cache/clear` - Limpar cache

**Frontend:** ❌ Não há server actions
**Impacto:** Baixo - Endpoints administrativos (só superadmin)

---

## 📊 Resumo Executivo

### Cobertura Atual:
- ✅ **Auth:** 10/10 endpoints (100%)
- ✅ **Reports:** 4/4 grupos (100%)
- ❌ **Demais recursos:** 0/160+ endpoints (~0%)

### Prioridade de Implementação:

#### 🔴 **PRIORIDADE ALTA** (Funcionalidades Core)
1. **Athletes** - CRUD de atletas
2. **Teams** - CRUD de equipes
3. **Users** - Gerenciamento de usuários
4. **Training Sessions** - CRUD de treinos
5. **Matches** - CRUD de jogos
6. **Match Events** - Eventos em jogos
7. **Attendance** - Presença em treinos
8. **Match Roster** - Convocação para jogos
9. **Team Registrations** - Inscrição de atletas
10. **Athlete States** - Estados de atletas
11. **Intake** - Ficha Única de cadastro
12. **Dashboard** - Dashboard principal
13. **Lookup** - Tabelas de referência

#### 🟡 **PRIORIDADE MÉDIA** (Funcionalidades Importantes)
14. **Seasons** - Gestão de temporadas
15. **Wellness Pre/Post** - Avaliações wellness
16. **Match Attendance** - Presença em jogos
17. **Athlete Import** - Importação em massa
18. **Competitions** - Gestão de competições
19. **Positions** - Gestão de posições
20. **Categories** - Gestão de categorias
21. **Alerts** - Sistema de alertas

#### 🟢 **PRIORIDADE BAIXA** (Funcionalidades Administrativas)
22. **Organizations** - Gestão de organizações
23. **Memberships** - Gestão de vínculos
24. **Persons** - Gestão de pessoas
25. **Roles** - Gestão de roles
26. **Permissions** - Gestão de permissões
27. **Audit Logs** - Logs de auditoria
28. **Media** - Gestão de mídias
29. **Admin Neon** - Endpoints administrativos

---

## ✅ Conclusão

**O sistema de autenticação está 100% completo**, incluindo:
- Login com permissões
- Setup inicial para dirigentes
- Troca de senha
- Definir senha no primeiro acesso
- Contexto do usuário

**Porém, há uma lacuna significativa** nos demais recursos:
- **~33 routers** do backend sem implementação no frontend
- **~160+ endpoints** disponíveis no backend
- Apenas **2 routers** (Auth + Reports) possuem server actions

**Recomendação:** 
Priorizar a implementação dos 13 recursos de **Alta Prioridade** para ter um sistema funcional end-to-end. Depois, implementar os recursos de média e baixa prioridade conforme demanda.
