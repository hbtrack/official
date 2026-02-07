<!-- STATUS: NEEDS_REVIEW -->

# Regras Canônicas de Gerenciamento de Atletas

**Versão:** 1.0 (Canonizada em 31/12/2025)

Este documento contém as regras **definitivas e sem ambiguidades** do gerenciamento de atletas, consolidadas após análise das regras do sistema (REGRAS.md) e estrutura real do banco de dados (Neon PostgreSQL).

---

## 📋 Decisões Canônicas Fundamentais

Este documento foi canonizado com base nas seguintes decisões arquiteturais:

1. **Dados Pessoais**: Uso exclusivo de tabelas normalizadas (`person_documents`, `person_contacts`, `person_addresses`). Campos duplicados removidos de `athletes`.
2. **organization_id**: Campo opcional e **derivado automaticamente** quando há `team_registration` ativo (copiado de `teams.organization_id`). Caso contrário, `NULL`.
3. **Validação de Categoria (R15)**: Executada na **criação do vínculo** (`team_registration`) e na **convocação para partidas** (última linha de defesa).
4. **Validação de Gênero**: Sistema **valida e bloqueia** incompatibilidade entre `persons.gender` e `teams.gender` (regra de elegibilidade). **CANÔNICO: Gênero vem de `persons.gender`, NÃO de `athletes`.**
5. **Endereços**: Campo `state_address` **removido**; usar exclusivamente `person_addresses.state`.
6. **Atleta sem Vínculo**: **Permitido** existir com `organization_id = NULL` e sem `team_registration` (fase de captação/avaliação).

---

## 1. Regras Estruturais de Atleta

### R1. Pessoa
Pessoa representa o indivíduo real e é independente de função esportiva. Atleta é vinculada a uma pessoa através de `athletes.person_id`.

### R2. Usuário (V1.2)
Atletas podem existir **sem usuário** (sem login). Criação de usuário para atleta é **opcional**, definida por checkbox "Criar acesso ao sistema" no cadastro.

### R4. Papéis do Sistema
Papéis organizacionais válidos: Dirigente, Coordenador, Treinador, **Atleta**.

### R5. Papéis não acumuláveis
Uma pessoa não pode ter múltiplos papéis ativos simultaneamente. Mudanças de papel exigem encerramento de vínculo e criação de novo, sem sobreposição temporal.

### R11. Atleta como papel permanente
Atleta é papel permanente no histórico: uma pessoa nunca deixa de ser atleta no histórico, embora não possa acumular papéis simultaneamente.

### **CANÔNICO: Estrutura de Dados Normalizada**

**Tabelas relacionadas a atletas:**
```
persons (dados básicos da pessoa)
├── person_documents (RG, CPF - separado por tipo de documento)
├── person_contacts (telefone, email - múltiplos contatos possíveis)
├── person_addresses (endereço completo - múltiplos endereços possíveis)
└── athletes (dados exclusivos do papel de atleta)
    └── team_registrations (vínculos com equipes)
```

**Campos em `athletes` (após canonização):**
- `id` (UUID, PK)
- `person_id` (UUID, FK → persons.id, **OBRIGATÓRIO**)
- `organization_id` (UUID, FK → organizations.id, **NULLABLE, DERIVADO**)
- `nickname` (VARCHAR, apelido esportivo, opcional)
- `height` (INTEGER, altura em cm, opcional)
- `weight` (DECIMAL, peso em kg, opcional)
- `gender` (ENUM: **'male', 'female'** - **OBRIGATÓRIO**, apenas masculino e feminino)
- `dominance` (ENUM: 'destro', 'canhoto', 'ambidestro', opcional)
- `defensive_position_id` (SMALLINT, FK → defensive_positions.id, **OBRIGATÓRIO**)
- `offensive_position_id` (SMALLINT, FK → offensive_positions.id, **OBRIGATÓRIO**)
- `state` (ENUM: 'ativa', 'dispensada', 'arquivada')
- `injured` (BOOLEAN, flag de lesão)
- `medical_restriction` (BOOLEAN, flag de restrição médica)
- `suspended_until` (DATE, data fim da suspensão)
- `load_restricted` (BOOLEAN, flag de carga restrita)
- `created_at`, `updated_at`, `deleted_at`, `deleted_reason`

**CAMPOS OBRIGATÓRIOS:**
✅ `person_id` (vínculo com pessoa)
✅ `gender` (apenas 'male' ou 'female' - handebol não possui categoria mista)
✅ `defensive_position_id` (posição defensiva principal)
✅ `offensive_position_id` (posição ofensiva principal)

**EXCEÇÃO PARA GOLEIRAS:**
⚠️ `offensive_position_id` pode ser **NULL** para goleiras (`defensive_position_id = 'goleira'`), pois goleira não atua ofensivamente (RD13). Evita dados artificiais e mantém consistência com regras esportivas.

**REMOVIDOS da tabela `athletes`:**
- ❌ `athlete_rg`, `athlete_cpf` → usar `person_documents`
- ❌ `athlete_phone`, `athlete_email` → usar `person_contacts`
- ❌ `zip_code`, `street`, `neighborhood`, `city`, `state_address`, `address_number`, `address_complement` → usar `person_addresses`

### **CANÔNICO: organization_id Derivado**

**Regra de preenchimento automático:**
```sql
-- Quando atleta tem team_registration ativo:
athletes.organization_id = teams.organization_id (via team_registrations.team_id)

-- Quando atleta NÃO tem team_registration ativo:
athletes.organization_id = NULL
```

**Comportamentos:**
- Atleta **recém-cadastrada sem equipe**: `organization_id = NULL` (fase de captação)
- Atleta **vinculada a equipe**: sistema atualiza automaticamente `organization_id` para `teams.organization_id`
- Atleta **com múltiplos vínculos ativos (mesma organização)**: `organization_id` representa a organização única onde possui vínculos
- Atleta **dispensada ou sem vínculos ativos**: `organization_id = NULL`

**REGRA CANÔNICA:** Atleta só pode ter vínculos ativos em **uma única organização por vez**. Múltiplos vínculos são permitidos apenas entre equipes da mesma organização (ex: joga em Infantil e Cadete do mesmo clube).

**Importante:** Este campo é **desnormalizado intencionalmente** para facilitar consultas, mas é **sempre derivado** e **nunca editado manualmente**.

---

## 2. Estados e Flags da Atleta

### R12. Estados operacionais da atleta

**Estado base único (enum):**
| Estado | Descrição |
|--------|-----------|
| `ativa` | Operacional e disponível |
| `dispensada` | Não participa mais da equipe; encerra todos os `team_registrations` ativos |
| `arquivada` | Registro histórico; sem participação operacional |
### **CANÔNICO: Ciclo de Vida Completo da Atleta**

**Estados definidos:**

1. **`ativa`** (operacional)
   - Pode treinar, jogar, ser convocada
   - Possui vínculo ativo ou está em captação
   - Estado padrão no cadastro

2. **`dispensada`** (desligamento)
   - Não participa mais de atividades da organização
   - Encerra automaticamente TODOS os `team_registrations` ativos
   - `organization_id = NULL`
   - Aparece apenas em histórico
   - **Pode retornar:** Sim, sem período de carência (reativa vínculo)

3. **`arquivada`** (histórico)
   - Registro histórico preservado
   - Sem participação operacional
   - Não recebe comunicação
   - **Pode reativar:** Sim, mudando estado para `ativa`

**Transições de estado permitidas:**
```
ativa → dispensada  (encerramento)
ativa → arquivada   (arquivamento)
dispensada → ativa  (retorno sem carência)
arquivada → ativa   (reativação)
```

**Reativação de atleta `arquivada`:**
- Dirigente/Coordenador pode mudar estado para `ativa`
- Sistema exige justificativa
- Gera auditoria completa
- Não restaura vínculos antigos automaticamente (criar novo `team_registration`)

**Retorno de atleta `dispensada`:**
- Mesma pessoa pode ser vinculada novamente à organização
- Sem período de carência
- Cria novo `team_registration` (não reabre anterior)
- Histórico anterior preservado
**Flags de restrição (camadas adicionais, independentes):**
| Flag | Tipo | Descrição |
|------|------|-----------|
| `injured` | boolean | Lesionada; NÃO pode treinar nem jogar; afastamento total |
| `medical_restriction` | boolean | Impedimento médico; pode treinar/jogar com limitações |
| `suspended_until` | date | Suspensa; NÃO entra em súmulas/jogos até data X; pode treinar |
| `load_restricted` | boolean | Restrita de carga; participa com limitação de volume |

**Combinações válidas:** Estado base + múltiplas flags podem coexistir.
- Exemplo: `ativa + injured + suspended_until` (lesionada e suspensa simultaneamente)

### R13. Impacto dos estados e flags

| Combinação | Comportamento |
|------------|---------------|
| `ativa` (sem flags) | Participa de tudo normalmente |
| `ativa + medical_restriction` | Participa com alertas; movimentos limitados; decisão médica registrada |
| `ativa + injured` | NÃO pode treinar/jogar; sistema **bloqueia** escalação em súmulas/convocações |
| `ativa + suspended_until` | NÃO entra em súmulas/jogos; **bloqueio automático** até data; pode treinar |
| `ativa + load_restricted` | Participa com alertas de carga; limitação de minutos/volume |
| `dispensada` | Aparece apenas em histórico; todos os `team_registrations` ativos são encerrados automaticamente |
| `arquivada` | Apenas histórico; sem operação; não recebe comunicação |

---

## 3. Regras de Categoria

### R14. Categorias globais
Categorias são globais e definidas por idade máxima (`max_age`). **Não possuem idade mínima** (`min_age`), permitindo atletas jogarem em categorias superiores.

### R15. Regra etária obrigatória
A atleta pode atuar na sua categoria natural ou em categorias acima (superior), **nunca em categorias abaixo** (inferior).

**Cálculo da categoria natural:**
```sql
idade = ano_temporada - ano_nascimento
categoria_natural = SELECT FROM categories WHERE idade <= max_age ORDER BY max_age ASC LIMIT 1
```

### **CANÔNICO: Validação de Categoria (R15)**

**Momento de validação OBRIGATÓRIA:**

1. **Na criação do vínculo (`team_registrations`):**
   - Sistema valida se `categoria_natural_atleta <= categoria_equipe`
   - Se violar, **BLOQUEIA** criação do vínculo com erro HTTP 400
   - Mensagem: "Atleta não pode ser vinculada a categoria inferior à sua categoria natural"

2. **Na convocação para partida (`match_events` ou súmulas):**
   - Sistema revalida a regra R15 (última linha de defesa)
   - Se violar, **BLOQUEIA** escalação com erro HTTP 400
   - Mensagem: "Atleta não elegível para esta categoria de partida"

**Por que dupla validação?**
- Primeira validação previne vínculos inválidos
- Segunda validação protege contra mudanças de data de nascimento ou categorias após vínculo criado

### Tabela de Categorias (RDB11)
| ID | Nome | Idade Máxima |
|----|------|--------------|
| 1 | Mirim | 12 |
| 2 | Infantil | 14 |
| 3 | Cadete | 16 |
| 4 | Juvenil | 18 |
| 5 | Júnior | 21 |
| 6 | Adulto | 36 |
| 7 | Master | 60 |

### **CANÔNICO: Gênero no Handebol**

**Regra fundamental:**
No handebol, **não existe categoria mista**. Apenas gêneros masculino e feminino são permitidos para atletas e equipes.

**Valores válidos:**
- `persons.gender`: **'masculino'** ou **'feminino'** (OBRIGATÓRIO para atletas)
- `teams.gender`: **'masculino'** ou **'feminino'** (OBRIGATÓRIO)

**CANÔNICO (31/12/2025):** Gênero do atleta vem de `persons.gender`, NÃO de `athletes`.

### **CANÔNICO: Validação de Elegibilidade por Gênero**

**Regra de elegibilidade por gênero:**

Sistema valida compatibilidade entre `persons.gender` e `teams.gender`:

| persons.gender | teams.gender | Permitido? |
|----------------|--------------|------------|
| feminino | feminino | ✅ Sim |
| masculino | masculino | ✅ Sim |
| feminino | masculino | ❌ **BLOQUEADO** |
| masculino | feminino | ❌ **BLOQUEADO** |

**IMPORTANTE:** Categoria 'misto' foi removida do sistema conforme regras do handebol.

**Momento de validação:**
- Na criação de `team_registration`
- Na convocação para partida

**Comportamento ao violar:**
- Sistema **BLOQUEIA** operação com HTTP 400
- Mensagem: "Atleta de gênero [X] não pode ser vinculada a equipe de gênero [Y]"

---

## 4. Regras de Vínculo com Equipes

### R6. Vínculo organizacional
Atleta possui vínculo esportivo com equipes (via `team_registrations`). O campo `athletes.organization_id` é **derivado automaticamente** do vínculo com equipe.

### R7. Vínculo ativo e exclusividade
Atleta pode ter **múltiplos `team_registrations` ativos simultâneos** em equipes diferentes **da mesma organização**, permitindo jogar em categorias superiores ou participar de desenvolvimento em múltiplas equipes.

**IMPORTANTE:** Atleta **NÃO pode ter vínculos simultâneos em organizações diferentes**. Vínculo é exclusivo por organização (evita conflitos regulatórios/jurídicos do handebol).

### R16. Múltiplas equipes (V1.2)
A participação da atleta em equipes é temporal (via `team_registrations`). Atleta pode ter múltiplos vínculos ativos simultâneos em equipes diferentes.

**Exemplo prático:**
- Atleta Infantil (13 anos) joga em:
  - Equipe "Infantil Feminino" (categoria natural)
  - Equipe "Cadete Feminino" (categoria superior)
- Estatísticas separadas por equipe + agregação total por temporada.

### R32. Regra de ouro do sistema (V1.2)
Nada acontece fora de um vínculo. Nada relevante é apagado. Nada histórico é sobrescrito sem rastro.

### **CANÔNICO: Atleta Sem Vínculo**

**Permitido:** Atleta pode existir cadastrada sem `team_registration` ativo.

**Cenários válidos:**
1. **Captação**: Atleta identificada em peneira, cadastrada para acompanhamento
2. **Avaliação**: Atleta em período de testes antes de ser oficialmente vinculada
3. **Transição**: Atleta encerrou vínculo com equipe anterior e aguarda nova vinculação
4. **Dispensada**: Atleta dispensada de todas as equipes (`state='dispensada'`)

**Comportamento no sistema:**
- `athletes.organization_id = NULL`
- Não aparece em listagens de equipes
- Não pode ser convocada para partidas
- Pode ter dados pessoais editados
- Pode ter perfil visualizado por dirigente/coordenador com permissões apropriadas

**Restrições:**
- Não pode participar de treinos registrados
- Não pode ser escalada em súmulas
- Não gera estatísticas operacionais (apenas histórico)

**Para operação efetiva:** Atleta precisa ter pelo menos 1 `team_registration` com `end_at = NULL` (vínculo ativo).

---

## 5. Regras Operacionais de Cadastro

### RF1. Cadeia hierárquica de criação
| Papel | Pode criar Atleta? |
|-------|-------------------|
| Super Administrador | ✅ Sim |
| Dirigente | ✅ Sim |
| Coordenador | ✅ Sim |
| Treinador | ✅ Sim |
| Atleta | ❌ Não |

### RF1.1. Vínculo automático ao cadastrar atleta

**Ao cadastrar atleta, o sistema cria:**
1. `persons` (dados pessoais básicos)
2. `athletes` (dados do papel de atleta, com `organization_id = NULL` inicialmente)

**Criação CONDICIONAL (conforme dados fornecidos):**
- `person_documents` (se RG ou CPF informados)
- `person_contacts` (se telefone ou email informados)
- `person_addresses` (se endereço informado)
- `users` (se checkbox "Criar acesso ao sistema" marcado)
- `team_registrations` (se equipe selecionada no cadastro)

**IMPORTANTE:** 
- Se `team_registration` criado → sistema atualiza automaticamente `athletes.organization_id = teams.organization_id`
- Se cadastro sem equipe → `athletes.organization_id = NULL` (atleta em captação)

### RF2. Identidade baseada em papel
Pessoas só existem no sistema se identificadas como dirigente, coordenador, treinador ou atleta.

### RF3. Usuário sem vínculo ativo (V1.2)
Atleta sem `team_registration` ativo mantém acesso **somente leitura** ao próprio histórico (R40). Não opera sem vínculo ativo.

---

## 5.1. Edição de Dados Cadastrais

### **CANÔNICO: Campos Editáveis Após Cadastro**

**SEMPRE EDITÁVEIS (sem restrição):**
- ✅ Nome completo (persons.full_name)
- ✅ Foto de perfil (athletes.athlete_photo_path)
- ✅ Telefone (person_contacts.contact_value onde contact_type='phone')
- ✅ Endereço completo (person_addresses - todos os campos)
- ✅ Upload/atualização de documentos anexos (não o número do documento)

**EDITÁVEIS COM RESTRIÇÃO:**

| Campo | Quem pode editar | Requisitos |
|-------|-----------------|------------|
| RG (person_documents) | Dirigente, Coordenador, Treinador | Justificativa obrigatória + auditoria completa |
| CPF (person_documents) | Dirigente, Coordenador, Treinador | Justificativa obrigatória + auditoria completa |
| Email (person_contacts) | Dirigente, Coordenador, Treinador | Validação de unicidade + auditoria obrigatória |

**NÃO EDITÁVEIS (ou somente por exceção):**

| Campo | Regra |
|-------|-------|
| Data de nascimento | **Antes de vínculo:** Editável por Dirigente/Coordenador/Treinador com auditoria<br>**Após vínculo ativo:** BLOQUEADA (exceção exige aprovação especial do Dirigente) |

**Motivo do bloqueio:** Data de nascimento afeta categoria natural (R15) e elegibilidade em competições.

### **CANÔNICO: Permissões por Contexto**

#### Atleta em CAPTAÇÃO (sem vínculo)
**Permissões flexíveis:**
- Dirigente/Coordenador/Treinador podem editar todos os dados pessoais
- Data de nascimento pode ser corrigida livremente
- Documentos (RG/CPF) podem ser ajustados
- Não há impacto regulatório (não está em competição)

#### Atleta com VÍNCULO ATIVO
**Permissões rígidas:**
- Data de nascimento BLOQUEADA (impacta elegibilidade)
- RG/CPF/Email exigem justificativa + auditoria
- Todas as edições são auditadas com `old_value` e `new_value`
- Dados esportivos (posições, altura, peso) editáveis por Coordenador/Treinador

### **CANÔNICO: Matriz de Permissões de Edição**

| Tipo de Dado | Atleta (próprio perfil) | Treinador | Coordenador | Dirigente |
|--------------|------------------------|-----------|-------------|----------|
| Foto de perfil | ✅ Sim | ✅ Sim | ✅ Sim | ✅ Sim |
| Nome completo | ❌ Não | ✅ Sim | ✅ Sim | ✅ Sim |
| Telefone | ✅ Sim | ✅ Sim | ✅ Sim | ✅ Sim |
| Endereço | ❌ Não | ✅ Sim | ✅ Sim | ✅ Sim |
| RG/CPF | ❌ Não | ✅ Com justificativa | ✅ Com justificativa | ✅ Com justificativa |
| Email de login | ❌ Não | ✅ Com justificativa | ✅ Com justificativa | ✅ Com justificativa |
| Data de nascimento (sem vínculo) | ❌ Não | ✅ Com auditoria | ✅ Com auditoria | ✅ Com auditoria |
| Data de nascimento (com vínculo) | ❌ Não | ❌ Bloqueado | ❌ Bloqueado | ✅ Exceção especial |
| Posições (defensiva/ofensiva) | ❌ Não | ✅ Sim | ✅ Sim | ✅ Sim |
| Altura/Peso | ❌ Não | ✅ Sim | ✅ Sim | ✅ Sim |
| Estado (ativa/dispensada/arquivada) | ❌ Não | ✅ Sim | ✅ Sim | ✅ Sim |

---

## 5.2. Transferências e Movimentação Entre Equipes

### **CANÔNICO: Movimentação Dentro da Mesma Organização**

**NÃO É TRANSFERÊNCIA** - atleta pode ter múltiplos vínculos simultâneos.

**Cenários válidos:**
1. **Promoção para categoria superior:**
   - Atleta Infantil (13 anos) vinculada a "Infantil Feminino"
   - Cria novo vínculo com "Cadete Feminino" (categoria superior)
   - Ambos os vínculos ativos simultaneamente (R7)

2. **Mudança de equipe (mesma categoria):**
   - Encerra vínculo com Equipe A (`end_at = NOW()`)
   - Cria novo vínculo com Equipe B (`start_at = NOW()`)
   - Sem período de carência entre vínculos

3. **Desenvolvimento em múltiplas equipes:**
   - Atleta pode treinar/jogar em até N equipes simultaneamente
   - Estatísticas separadas por equipe

**Validações:**
- Sempre validar R15 (categoria) no novo vínculo
- Sempre validar gênero no novo vínculo
- Não permitir múltiplos vínculos ativos na MESMA equipe

### **CANÔNICO: Movimentação Entre Organizações**

**NÃO EXISTE TRANSFERÊNCIA INTERCLUBE NO SISTEMA.**

**Motivo:** 
- Organizações são independentes e autônomas (R33)
- Evita conflitos regulatórios e jurídicos do handebol real
- Atleta **não pode ter vínculos simultâneos em organizações diferentes** (R7 restrito a intra-organização)

**Fluxo correto:**
1. **Clube A:** Atleta é dispensada (`state='dispensada'`)
   - Encerra **TODOS** os `team_registrations` ativos automaticamente
   - `organization_id = NULL`
   - Sistema **bloqueia** criação de novo vínculo em Clube A até reativação explícita
2. **Clube B:** Atleta é cadastrada como novo registro
   - Mesma pessoa (person_id diferente ou reuso depende da implementação)
   - Novo contexto organizacional
   - Histórico do Clube A **não é visível** no Clube B

**Importante:** Esta regra respeita a autonomia organizacional e previne conflitos de elegibilidade em competições oficiais.

---

## 5.3. Responsável Legal (Menores de Idade)

### **CANÔNICO: Responsável Legal OPCIONAL**

**Regra:** Cadastro de responsável legal é **opcional**, mas recomendado para menores de 18 anos.

**Campos disponíveis em `athletes`:**
- `guardian_name` (VARCHAR, opcional)
- `guardian_phone` (VARCHAR, opcional)

**Múltiplos responsáveis:**
- Sistema permite apenas 1 responsável direto em `athletes.guardian_name`
- Para pai + mãe, usar campo `notes` em persons ou criar registros em `person_contacts` com tag especial

**Validações:**
- Se atleta < 18 anos e `guardian_name` vazio → **AVISO não bloqueante** no cadastro
- Sistema não valida maioridade automaticamente
- Responsável não tem acesso ao sistema (não cria `user`)

**Recomendação futura:**
- Considerar tabela `guardians` separada para múltiplos responsáveis
- Permitir responsáveis terem login para visualizar dados da atleta

---

## 5.4. Fotos e Documentos Anexos (person_media)

### **CANÔNICO: Ficha Única - Fotos para TODOS os Papéis**

**Conceito:** A tabela `person_media` armazena fotos e mídias para **TODOS** os papéis do sistema (Dirigentes, Coordenadores, Treinadores, Atletas). Faz parte da Ficha Única de Cadastro centrada em `persons`.

**Estrutura da tabela `person_media`:**
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `id` | UUID | ✅ Sim | PK |
| `person_id` | UUID | ✅ Sim | FK → persons.id (qualquer pessoa) |
| `media_type` | VARCHAR(50) | ✅ Sim | `'foto_perfil'`, `'foto_documento'`, `'video'`, `'outro'` |
| `file_url` | TEXT | ✅ Sim | URL do arquivo armazenado |
| `file_name` | VARCHAR(255) | ❌ Não | Nome original do arquivo |
| `file_size` | INTEGER | ❌ Não | Tamanho em bytes |
| `mime_type` | VARCHAR(100) | ❌ Não | MIME type do arquivo |
| `is_primary` | BOOLEAN | ✅ Sim | Se é a mídia principal do tipo (default: false) |
| `description` | TEXT | ❌ Não | Descrição opcional |

**Constraint único:** Apenas uma foto primária por tipo por pessoa:
```sql
UNIQUE (person_id, media_type) WHERE is_primary = true AND deleted_at IS NULL
```

### **CANÔNICO: Fotos de Perfil**

**Armazenamento:**
- Tabela: `person_media` com `media_type = 'foto_perfil'`
- Formatos aceitos: **JPG, JPEG, PNG**
- Tamanho máximo: **2 MB**
- Conversão automática: Backend converte para JPEG padrão

**⚠️ CAMPO LEGADO:** O campo `athletes.athlete_photo_path` é **LEGADO** e será removido em versão futura. Usar exclusivamente `person_media`.

### **CANÔNICO: Remoção de Fundo (OBRIGATÓRIA)**

**Objetivo:** Padronização visual do sistema - todas as fotos de perfil devem ter fundo branco.

**Fluxo de processamento:**
1. Usuário faz upload da foto original
2. Backend recebe e salva arquivo original temporariamente
3. **Processamento automático de remoção de fundo:**
   - Usar biblioteca Python `rembg` (local, gratuita) ou API externa (ex: remove.bg)
   - Aplicar fundo branco (#FFFFFF) na imagem processada
   - Converter para JPEG com qualidade 85%
   - Redimensionar para dimensões padrão (ex: 400x400px, mantendo proporção)
4. Salvar imagem processada no storage (S3, local, etc.)
5. Registrar URL final em `person_media.file_url`

**Configuração de processamento:**
```python
# Opção 1: rembg (local, gratuito)
from rembg import remove
from PIL import Image

def process_profile_photo(input_path: str) -> str:
    # Remove background
    input_img = Image.open(input_path)
    output_img = remove(input_img)
    
    # Apply white background
    white_bg = Image.new("RGBA", output_img.size, (255, 255, 255, 255))
    white_bg.paste(output_img, mask=output_img.split()[3])
    
    # Convert to RGB (JPEG)
    final_img = white_bg.convert("RGB")
    
    # Resize to standard dimensions
    final_img.thumbnail((400, 400), Image.Resampling.LANCZOS)
    
    # Save
    output_path = f"processed_{uuid4()}.jpg"
    final_img.save(output_path, "JPEG", quality=85)
    return output_path
```

**Fallback:**
- Se processamento falhar, usar imagem original com aviso ao usuário
- Log de erro para análise posterior
- Permitir reprocessamento manual pelo admin

**Resultado esperado:**
- Todas as fotos de perfil com fundo branco padronizado
- Visual consistente em todo o sistema
- Melhor apresentação em relatórios e fichas PDF

### **CANÔNICO: Permissões de Edição de Foto**

**Qualquer pessoa pode editar sua própria foto de perfil.**

| Papel | Própria foto | Foto de outros |
|-------|--------------|----------------|
| Atleta | ✅ Sim | ❌ Não |
| Treinador | ✅ Sim | ✅ Atletas de suas equipes |
| Coordenador | ✅ Sim | ✅ Todos da organização |
| Dirigente | ✅ Sim | ✅ Todos da organização |

**Auditoria:**
- Registrar: `person_id`, `uploaded_by`, `uploaded_at`
- Não exige justificativa (identidade visual, não impacta regras esportivas)

### **CANÔNICO: Documentos Anexos**

**Armazenamento via `person_media`:**
- `media_type = 'foto_documento'` para fotos de documentos (RG, atestados)
- `media_type = 'outro'` para demais anexos

**Tipos de documentos:**
1. **Foto do RG** (opcional)
2. **Atestado médico** (opcional)
3. **Autorização dos pais** (opcional, para menores)
4. **Outros documentos** (certificados, laudos, etc.)

**Armazenamento:**
- Formatos aceitos: **JPG, JPEG, PNG, PDF**
- Tamanho máximo: **5 MB**
- Backend valida: formato, MIME type, bloqueia executáveis
- Armazenar no banco: apenas URL do arquivo (não o binário)

**Permissões de visualização:**
- ✅ Dirigentes (todos)
- ✅ Coordenadores (todos da organização)
- ✅ Treinadores (apenas de suas equipes)
- ❌ Atletas (não visualizam documentos de outras pessoas)

**Validade:**
- Sistema **NÃO valida automaticamente** a validade de documentos
- Documentos podem ser substituídos quantas vezes necessário
- Não há data de expiração controlada pelo sistema

**Auditoria:**
- Toda submissão gera log: quem enviou, quando, tipo de documento, person_id

---

## 5.5. Dados Médicos e Histórico de Saúde

### **CANÔNICO: Informações Médicas OPCIONAIS**

**Campos disponíveis (futuro - não implementado na V1):**
- Histórico de lesões (tabela separada `athlete_injuries`)
- Alergias/condições crônicas (campo text em `athletes.medical_notes`)
- Tipo sanguíneo (campo enum em `athletes.blood_type`)
- Contato de emergência (campo em `person_contacts` com tipo especial)

**Estrutura sugerida para V2:**

```sql
CREATE TABLE athlete_injuries (
  id UUID PRIMARY KEY,
  athlete_id UUID REFERENCES athletes(id),
  injury_type VARCHAR(100),
  injury_date DATE,
  recovery_date DATE,
  description TEXT,
  created_by UUID,
  created_at TIMESTAMPTZ
);
```

**Acesso aos dados médicos:**
- ✅ Dirigentes (visualização completa)
- ✅ Coordenadores (visualização completa)
- ✅ Treinadores (apenas de suas equipes)
- ⚠️ **PRIVACIDADE LGPD:** Dados sensíveis de saúde

**Alertas automáticos (futuros):**
- Atleta lesionada há mais de 30 dias
- Lesões recorrentes (mesmo tipo em < 6 meses)
- Atestado médico vencido (se implementado controle de validade)

**V1 (atual):**
- Usar apenas flags: `injured`, `medical_restriction`
- Dados detalhados em `persons.notes` ou `athletes.guardian_name` (temporário)

---

## 5.6. Importação em Massa (Bulk Cadastro)

### **CANÔNICO: Cadastro por CSV/Excel**

**Funcionalidade:**
- Sistema permite cadastro de múltiplas atletas via planilha Excel/CSV
- Template padrão gerado pelo sistema (download)

**Template mínimo:**
```csv
full_name,birth_date,rg,phone,email,gender,defensive_position_id,offensive_position_id,team_id
"Maria Silva","2010-05-15","12345678","11987654321","maria@email.com","female",1,2,"uuid-da-equipe"
```

**Fluxo de importação:**
1. **Upload do arquivo** (CSV ou XLSX)
2. **Pré-validação obrigatória:**
   - Valida formato de cada campo
   - Valida unicidade (RG, CPF, email, telefone)
   - Valida categoria vs equipe (R15)
   - Valida gênero vs equipe
   - Retorna lista de erros ANTES de processar
3. **Processamento linha a linha:**
   - Erros em uma linha NÃO param toda importação
   - Linhas válidas são processadas
   - Linhas com erro são ignoradas e retornadas no relatório
4. **Relatório final:**
   - Sucesso: X atletas cadastradas
   - Erros: Y linhas rejeitadas (detalhes de cada erro)

**Vínculo em massa:**
- ✅ Permitido vincular atletas a equipes via coluna `team_id` no CSV
- Validações R15 e gênero aplicadas a cada linha

**Auditoria completa:**
- Log registra: quem importou, quando, quantas linhas processadas, sucesso/erro

**Permissões:**
- ✅ Dirigente (qualquer organização)
- ✅ Coordenador (sua organização)
- ❌ Treinador (não permite importação em massa)

---

## 6. Regras de Alteração de Estado

### RF16. Alteração do estado da atleta
O estado base e flags de restrição podem ser alterados por:
- ✅ Dirigentes
- ✅ Coordenadores
- ✅ Treinadores

**Toda alteração é auditável.**

**Comportamentos automáticos:**
| Ação | Resultado automático |
|------|---------------------|
| Mudança para "dispensada" | Encerra automaticamente todos os `team_registrations` ativos |
| `injured=true` | Bloqueia escalação em convocações/súmulas |
| `suspended_until=date` | Bloqueia participação em jogos até data |

### RF17. Encerramento manual de vínculos
- Coordenadores e Treinadores podem encerrar `team_registrations` de atletas
- Encerramento exige data de término (`end_at`)

---

## 7. Regras de Posição (Goleira)

### 2.X.6. Bloqueios para erro de posição de goleira
- Se posição defensiva principal for **"goleira"**, sistema bloqueia estatísticas típicas de atleta de linha
- Backend rejeita tentativas de lançamento de estatísticas bloqueadas para goleira (HTTP 400)
- Ao alterar jogadora de goleira para linha ou vice-versa, sistema **exige confirmação explícita**

### RD13. Goleira - Estatísticas
**Regra geral:** Goleira é exclusiva da posição e não atua como jogadora de linha.

**Estatísticas PERMITIDAS para goleira:**
- Defesas totais, por zona, por situação
- Arremessos sofridos
- Gols sofridos (totais e por zona)
- Defesas de 7 metros
- Assistências de goleira (passe direto que resulta em gol)
- Gols marcados (gol a gol)
- Tempo em quadra como goleira
- Exclusões e cartões

**Estatísticas BLOQUEADAS para goleira:**
- Arremessos de linha
- Gols e aproveitamento de linha
- Assistências em ataque posicional
- Bloqueios defensivos de linha
- Fintas, dribles, roubos de bola
- Tempo em quadra como jogadora de linha

---

## 8. Regras de Auditoria

### R30. Ações críticas auditáveis
Obrigatoriamente auditadas no contexto de atletas:
- Mudança de estado de atleta
- Aplicação/remoção de flags de restrição
- Encerramento/reativação de vínculo
- Correção de estatística

### R31. Log obrigatório
Todo evento crítico deve registrar:
| Campo | Descrição |
|-------|-----------|
| `actor_id` | Quem fez a ação |
| `timestamp` | Quando |
| `action` | O quê |
| `context` | Detalhes |
| `old_value` | Valor anterior |
| `new_value` | Novo valor |

### R34. Imutabilidade dos logs
Logs de auditoria são **absolutamente imutáveis**, não podendo ser alterados ou removidos, nem pelo Super Administrador.

---

## 9. Regras de Exclusão

### R28. Exclusão lógica
Nenhuma atleta é apagada fisicamente (**soft delete obrigatório** via `deleted_at` + `deleted_reason`).

### R10. Histórico imutável
Vínculos encerrados jamais são apagados ou alterados retroativamente.

### R29. Reativação de vínculo (V1.2)
Vínculos podem ser reativados desde que não violem exclusividade. Reativação cria **nova linha** com novo UUID; não reabre linha anterior.

---

## 9.1. Notificações Automáticas

### **CANÔNICO: Alertas do Sistema**

**Sistema notifica automaticamente sobre:**

1. **Atleta lesionada prolongadamente:**
   - Trigger: `injured=true` há mais de 30 dias
   - Mensagem: "Atleta [nome] lesionada há [X] dias"
   - Destinatários: Dirigente, Coordenador, Treinador, própria atleta

2. **Atleta fora de atividades:**
   - Trigger: `injured=true` ou `suspended_until` ativo
   - Mensagem: "Atleta [nome] indisponível para jogos/treinos ([motivo])"
   - Destinatários: Treinador da equipe

3. **Atleta sem vínculo ativo prolongadamente:**
   - Trigger: Sem `team_registration` ativo há mais de 15 dias
   - Mensagem: "Atleta [nome] sem vínculo há [X] dias (captação)"
   - Destinatários: Dirigente, Coordenador

4. **Suspensão próxima de expirar:**
   - Trigger: `suspended_until` em 3 dias
   - Mensagem: "Suspensão de [nome] expira em [data]"
   - Destinatários: Treinador, Coordenador

**Canal de notificação:**
- ✅ **Notificação in-app** (prioritário)
- ⏳ Email (futuro)

**Frequência:**
- Alertas não repetitivos (uma vez ao atingir condição)
- Pode ser marcado como "lido" pelo usuário

**Permissões de visualização:**
- Cada papel vê apenas notificações relevantes ao seu escopo
- Atleta vê apenas notificações sobre si mesma

---

## 10. Filtros da Página de Gerenciamento

### Filtros Obrigatórios
| Filtro | Opções | Descrição |
|--------|--------|-----------|
| Estado | ativa, dispensada, arquivada | Estado base da atleta |
| Categoria | Mirim, Infantil, Cadete, Juvenil, Júnior, Adulto, Master | Categoria natural calculada |
| Posição | Todas as posições defensivas | Posição principal da atleta |
| Equipe | Lista de equipes da organização | Vínculo ativo via team_registration |
| Com equipe | Sim/Não | Se possui team_registration ativo |

### Filtros de Restrição (Flags)
| Filtro | Descrição |
|--------|-----------|
| Lesionada | `injured = true` |
| Restrição médica | `medical_restriction = true` |
| Suspensa | `suspended_until IS NOT NULL AND suspended_until > now()` |
| Carga restrita | `load_restricted = true` |
---

## 10.1. Busca e Filtros Avançados

### **CANÔNICO: Busca por Texto**

**Search bar com autocomplete:**
- Busca por **nome completo** (persons.full_name)
- Busca por **apelido esportivo** (athletes.nickname)
- Busca por **RG parcial** (últimos 4 dígitos)
- Busca por **CPF parcial** (últimos 4 dígitos)

**Exemplo:**
```
Digitou: "Maria"
Resultados:
- Maria Silva (ativa, Infantil Feminino)
- Ana Maria Santos (ativa, Cadete Feminino)
- Marianne Oliveira (dispensada)
```

### **CANÔNICO: Filtros Avançados Adicionais**

**Além dos filtros obrigatórios (seção 10), adicionar:**

1. **Faixa etária:**
   - Input: idade mínima e máxima (ex: 14-16 anos)
   - Cálculo: baseado em `birth_date` e ano atual

2. **Altura/Peso:**
   - Filtro por range (ex: 160-175 cm, 50-60 kg)
   - Útil para análises táticas

3. **Dominância:**
   - Checkbox: destro, canhoto, ambidestro
   - Útil para montagem de elenco

4. **Aptas para jogo:**
   - Filtro rápido que exclui:
     - `injured=true`
     - `suspended_until >= hoje`
     - `state='dispensada'` ou `'arquivada'`
   - Retorna apenas atletas disponíveis para convocação

5. **Posição ofensiva/defensiva secundária:**
   - Filtro adicional além das principais

### **CANÔNICO: Salvar Filtros Favoritos**

**Funcionalidade:**
- Usuário pode salvar combinações de filtros
- Nomear filtro salvo (ex: "Cadetes aptas", "Captação recente")
- Carregar filtro salvo com 1 clique

**Armazenamento:**
- Tabela `saved_filters`: `user_id`, `filter_name`, `filter_json`
- JSON contém todos os parâmetros de filtro

**Exemplo de filtro salvo:**
```json
{
  "name": "Cadetes aptas para jogo",
  "filters": {
    "category": "Cadete",
    "injured": false,
    "suspended_until": null,
    "state": "ativa"
  }
}
```

---

## 10.2. Relatórios Essenciais

### **CANÔNICO: Relatórios Prioritários**

**1. Lista Geral de Atletas**
- **Objetivo:** Visão completa do elenco
- **Campos:** Nome, idade, categoria, equipe, posições, estado, contato
- **Filtros:** Todos disponíveis
- **Exportação:** PDF, Excel, CSV
- **Permissão:** Dirigente, Coordenador

**2. Atletas por Categoria/Equipe**
- **Objetivo:** Organização esportiva por categoria
- **Agrupamento:** Por categoria ou por equipe
- **Campos:** Nome, idade, posições, altura/peso, dominância
- **Exportação:** PDF, Excel
- **Permissão:** Todos os papéis

**3. Atletas por Estado**
- **Objetivo:** Quem está ativa, dispensada ou arquivada
- **Filtro:** Por estado
- **Campos:** Nome, estado, data da última mudança, motivo (se dispensada)
- **Exportação:** Excel, CSV
- **Permissão:** Dirigente, Coordenador

**4. Atletas em Captação**
- **Objetivo:** Pipeline de atletas sem vínculo
- **Filtro:** `organization_id IS NULL`
- **Campos:** Nome, idade, categoria natural, data de cadastro, quem cadastrou
- **Exportação:** Excel
- **Permissão:** Dirigente, Coordenador

**5. Histórico de Vínculos**
- **Objetivo:** Em quais equipes a atleta já atuou dentro da organização
- **Agrupamento:** Por atleta
- **Campos:** Nome da equipe, data início, data fim, categoria no período
- **Exportação:** PDF
- **Permissão:** Todos os papéis

**6. Status Médico**
- **Objetivo:** Atletas com restrição, lesão ou atestado vencido
- **Filtro:** `injured=true` OR `medical_restriction=true`
- **Campos:** Nome, tipo de restrição, data início, observações
- **Exportação:** Excel (dados sensíveis)
- **Permissão:** Dirigente, Coordenador (LGPD)

**7. Distribuição Estatística**
- **Objetivo:** Análises estratégicas
- **Gráficos:**
  - Distribuição por idade
  - Distribuição por posição (defensiva/ofensiva)
  - Distribuição por categoria
  - Altura/peso médios por categoria
- **Exportação:** PDF com gráficos
- **Permissão:** Dirigente, Coordenador

### **CANÔNICO: Formato de Exportação**

**PDF:**
- Layout profissional com logo da organização
- Cabeçalho: nome do relatório, data/hora geração, quem gerou
- Tabelas formatadas
- Paginação automática

**Excel/CSV:**
- Headers em português
- Formatação de datas (DD/MM/YYYY)
- Colunas ajustadas automaticamente
- Totalizadores no rodapé (quando aplicável)

**Filtros aplicados:**
- Sempre incluir no relatório quais filtros foram usados
- Rodapé: "Filtros aplicados: Categoria=Cadete, Estado=Ativa"
---

## 11. Campos do Cadastro de Atleta

### **CANÔNICO: Dados Pessoais (tabelas normalizadas)**

#### persons
| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| full_name | VARCHAR | ✅ Sim | Mínimo 3 caracteres |
| first_name | VARCHAR | ✅ Sim | Extraído de full_name |
| last_name | VARCHAR | ✅ Sim | Extraído de full_name |
| birth_date | DATE | ✅ Sim | Pessoa deve ter entre 8-60 anos |
| gender | ENUM | ❌ Não | male, female, other |
| nationality | VARCHAR | ❌ Não | - |
| notes | TEXT | ❌ Não | Observações gerais |

#### person_documents
| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| person_id | UUID | ✅ Sim | FK → persons.id |
| document_type | ENUM | ✅ Sim | 'rg', 'cpf', 'passport', etc. |
| document_number | VARCHAR | ✅ Sim | **Único no sistema por tipo** |
| issuer | VARCHAR | ❌ Não | Órgão emissor |
| issue_date | DATE | ❌ Não | Data de emissão |

**OBRIGATORIEDADE PARA ATLETAS:**
- ✅ **RG obrigatório** (document_type='rg') - documento mínimo para cadastro de atleta
- ❌ CPF opcional (pode ser adicionado depois)

**JUSTIFICATIVA RG OBRIGATÓRIO:** Identificação mínima necessária para registro esportivo e prevenção de duplicidade cadastral.

**Validações especiais:**
- RG: unicidade obrigatória no sistema
- CPF: validar dígitos verificadores (se informado)
- Um documento por tipo por pessoa

#### person_contacts
| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| person_id | UUID | ✅ Sim | FK → persons.id |
| contact_type | ENUM | ✅ Sim | 'phone', 'email', 'whatsapp' |
| contact_value | VARCHAR | ✅ Sim | **Único no sistema por tipo** |
| is_primary | BOOLEAN | ❌ Não | Apenas um primary por tipo |

**OBRIGATORIEDADE PARA ATLETAS:**
- ✅ **Telefone obrigatório** (contact_type='phone') - canal primário de contato emergencial
- ✅ **Email obrigatório** (contact_type='email') - **canal primário de comunicação e notificações**

**JUSTIFICATIVA EMAIL OBRIGATÓRIO:**
- Email serve como **canal primário de contato**, não implica criação automática de usuário
- Evita retrabalho futuro quando acesso ao sistema for necessário (mesmo endereço reutilizado)
- Criação de login é **opcional** (checkbox "Criar acesso ao sistema")
- Até criação de usuário, email usado **exclusivamente** para comunicação/notificações
- Armazenado como contato primário da pessoa, **não como credencial de acesso**
- Alterações no email exigem restrição e auditoria (dado sensível, potencial identificador futuro)

**Validações especiais:**
- Email: formato válido (regex RFC 5322)
- Telefone: formato brasileiro (+55) obrigatório
- Múltiplos contatos permitidos por pessoa

#### person_addresses
| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| person_id | UUID | ✅ Sim | FK → persons.id |
| zip_code | VARCHAR(9) | ❌ Não | Formato: 12345-678 |
| street | VARCHAR | ❌ Não | - |
| number | VARCHAR | ❌ Não | Permite "S/N" |
| complement | VARCHAR | ❌ Não | Apto, bloco, etc. |
| neighborhood | VARCHAR | ❌ Não | Bairro |
| city | VARCHAR | ❌ Não | Cidade |
| state | VARCHAR(2) | ❌ Não | **Sigla UF (SP, RJ, MG, etc.)** |
| country | VARCHAR | ❌ Não | Padrão: Brasil |
| is_primary | BOOLEAN | ❌ Não | Apenas um primary por pessoa |

**CAMPO REMOVIDO:** ❌ `state_address` (confuso, substituído por `state` com padrão UF)

### Dados Esportivos (athletes)
| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| person_id | UUID | ✅ Sim | FK → persons.id |
| organization_id | UUID | ❌ Não | **DERIVADO automaticamente** de team_registration |
| nickname | VARCHAR | ❌ Não | Apelido esportivo |
| defensive_position_id | SMALLINT | ✅ **SIM** | FK → defensive_positions.id |
| offensive_position_id | SMALLINT | ✅ **SIM** | FK → offensive_positions.id |

**CAMPOS OBRIGATÓRIOS CRÍTICOS:**
1. ✅ `gender` - masculino ou feminino (sem categoria mista) VEM DA TABELA PERSONS
2. ✅ `defensive_position_id` - posição defensiva principal obrigatória
3. ✅ `offensive_position_id` - posição ofensiva principal obrigatória

**Categoria:** Derivada automaticamente da idade (não é campo direto em athletes)

### Estado e Flags
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| state | ENUM | 'ativa' | Estado base |
| injured | BOOLEAN | false | Lesionada |
| medical_restriction | BOOLEAN | false | Restrição médica |
| suspended_until | DATE | null | Data fim da suspensão |
| load_restricted | BOOLEAN | false | Carga restrita |

### Vínculo com Equipe (team_registration)
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| athlete_id | UUID | ✅ Sim | FK → athletes.id |
| team_id | UUID | ✅ Sim | FK → teams.id |
| start_at | TIMESTAMPTZ | ✅ Sim | Data início do vínculo |
| end_at | TIMESTAMPTZ | ❌ Não | NULL = vínculo ativo |

**Validações ao criar team_registration:**
1. Validar R15 (categoria natural ≤ categoria da equipe)
2. Validar gênero (`persons.gender` compatível com `teams.gender`)
3. Não permitir sobreposição de períodos na mesma equipe
4. Atualizar automaticamente `athletes.organization_id = teams.organization_id`

### Acesso ao Sistema (user)
| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| Criar acesso | CHECKBOX | ❌ Não | Se marcado, cria user |
| Email de acesso | VARCHAR | ✅ (se criar acesso) | Usa email de person_contacts como login |
| Senha temporária | VARCHAR | ✅ (se criar acesso) | Gerada automaticamente ou definida |

---

## 11.1. Formulário de Cadastro de Atleta

**Estrutura:** Formulário único com seções expansíveis/colapsáveis

### Seção 1: Dados Pessoais (obrigatória)
**Campos obrigatórios:**
- Nome completo (mínimo 3 caracteres)
- Data de nascimento (idade 8-60 anos)
- RG (único no sistema)
- Telefone (formato brasileiro)
- Email (formato válido, único no sistema)

**Campos opcionais:**
- CPF
- Nacionalidade
- Observações gerais

### Seção 2: Dados Esportivos (obrigatória)
**Campos obrigatórios:**
- Gênero (masculino/feminino)
- Posição defensiva principal (dropdown)
- Posição ofensiva principal (dropdown)

**Campos opcionais:**
- Apelido esportivo
- Altura (cm)
- Peso (kg)
- Dominância (destro/canhoto/ambidestro)
- Posição defensiva secundária
- Posição ofensiva secundária
- Escolaridade
- Responsável legal (nome + telefone)

### Seção 3: Endereço (opcional - colapsada por padrão)
**Todos os campos opcionais:**
- CEP
- Rua
- Número
- Complemento
- Bairro
- Cidade
- Estado (sigla UF)
- País (padrão: Brasil)

### Seção 4: Vínculo com Equipe (opcional)
**Comportamento:**
- Se nenhuma equipe selecionada: atleta cadastrada em captação (`organization_id = NULL`)
- Se equipe selecionada:
  - Validar categoria (R15)
  - Validar gênero (compatibilidade)
  - Criar `team_registration` e derivar `organization_id`

**Campos:**
- Equipe (dropdown - lista de equipes da organização)
- Data início do vínculo (default: hoje)

### Seção 5: Acesso ao Sistema (opcional - colapsada por padrão)
**Checkbox:** "Criar acesso ao sistema"

**Se marcado, exibir:**
- Email para login (pré-preenchido com email da Seção 1)
- Opção de senha:
  - Gerar senha temporária automaticamente (default)
  - Definir senha manualmente

**Comportamento:**
- Se desmarcado: atleta cadastrada sem login (acessa apenas se precisar depois)
- Se marcado: cria `users` com email como login e senha definida

### Validações no Envio do Formulário

**Bloqueios (HTTP 400):**
1. Campos obrigatórios vazios
2. RG duplicado no sistema
3. Email duplicado no sistema
4. Telefone duplicado no sistema
5. CPF inválido (se informado)
6. Idade fora da faixa 8-60 anos
7. Categoria incompatível com equipe selecionada (R15)
8. Gênero incompatível com equipe selecionada

**Avisos (não bloqueantes):**
1. Altura/peso fora da faixa esperada
2. Responsável legal não informado para menor de idade
3. Endereço não preenchido

---

## 12. Validações de Negócio

### **CANÔNICO: Validações ao Cadastrar**

1. **Pessoa (persons):**
   - `full_name`: mínimo 3 caracteres
   - `birth_date`: idade entre 8-60 anos
   - `first_name` e `last_name`: extraídos automaticamente de `full_name`

2. **Documentos (person_documents):**
   - CPF: validar dígitos verificadores (algoritmo padrão)
   - RG/Passaporte: apenas unicidade
   - Verificar unicidade por `document_type + document_number` em todo sistema

3. **Contatos (person_contacts):**
   - Email: formato válido (regex RFC 5322)
   - Telefone: formato brasileiro (regex)
   - Verificar unicidade por `contact_type + contact_value` em todo sistema

4. **Atleta (athletes):**
   - `gender`: **OBRIGATÓRIO** - apenas 'male' ou 'female' (handebol não possui misto)
   - `defensive_position_id`: **OBRIGATÓRIO** - posição defensiva principal
   - `offensive_position_id`: **OBRIGATÓRIO** - posição ofensiva principal
   - `height`: se informado, entre 100-250 cm
   - `weight`: se informado, entre 30-150 kg
   - `organization_id`: sempre NULL no cadastro inicial (será derivado depois)

5. **Documentos obrigatórios (person_documents):**
   - **RG obrigatório** (document_type='rg')
   - CPF opcional (pode ser adicionado depois)

6. **Contatos obrigatórios (person_contacts):**
   - **Telefone obrigatório** (contact_type='phone')
   - **Email obrigatório** (contact_type='email')

5. **Vínculo (team_registration - se informado):**
   - **Validar R15:** categoria natural da atleta ≤ categoria da equipe
   - **Validar gênero:** `persons.gender` compatível com `teams.gender`
   - Se validações passarem: criar vínculo e atualizar `athletes.organization_id`

### **CANÔNICO: Validações ao Alterar Estado**

1. **Mudança para `dispensada`:**
   - Sistema encerra automaticamente todos os `team_registrations` ativos (`end_at = NOW()`)
   - Sistema atualiza `athletes.organization_id = NULL`
   - Gera log de auditoria com razão da dispensa

2. **Mudança de flags de restrição:**
   - `injured=true`: valida se não há convocações futuras pendentes
   - `suspended_until=date`: valida se data é futura
   - Toda mudança gera log de auditoria

3. **Múltiplas flags simultâneas:**
   - Sistema permite combinações (ex: `injured + suspended_until`)
   - Interface deve alertar usuário sobre restrições ativas

### **CANÔNICO: Validações ao Vincular a Equipe (team_registration)**

1. **Validação de Categoria (R15):**
   ```sql
   categoria_natural = calcular_categoria(athlete.birth_date, season.year)
   categoria_equipe = team.category_id
   
   IF categoria_natural > categoria_equipe THEN
     RETURN ERROR 400 "Atleta não pode jogar em categoria inferior"
   END IF
   ```

2. **Validação de Gênero:**
   ```sql
   -- CANÔNICO: Gênero vem de persons.gender (via athletes.person_id)
   person_gender = SELECT gender FROM persons WHERE id = athlete.person_id
   
   IF person_gender = 'feminino' AND teams.gender = 'masculino' THEN
     RETURN ERROR 400 "Atleta feminina não pode jogar em equipe masculina"
   ELSIF person_gender = 'masculino' AND teams.gender = 'feminino' THEN
     RETURN ERROR 400 "Atleta masculino não pode jogar em equipe feminina"
   END IF
   ```

3. **Validação de Sobreposição:**
   ```sql
   -- Não permitir múltiplos vínculos ativos na MESMA equipe
   IF EXISTS (
     SELECT 1 FROM team_registrations
     WHERE athlete_id = ? AND team_id = ? AND end_at IS NULL
   ) THEN
     RETURN ERROR 400 "Atleta já possui vínculo ativo com esta equipe"
   END IF
   ```

4. **Atualização de organization_id:**
   ```sql
   -- Após criar team_registration com sucesso:
   UPDATE athletes
   SET organization_id = (SELECT organization_id FROM teams WHERE id = ?)
   WHERE id = ?
   ```

### **CANÔNICO: Validações ao Convocar para Partida**

**Segunda linha de defesa (validações redundantes intencionais):**

1. **Revalidar R15 (categoria):**
   - Calcular categoria natural novamente (pode ter mudado se birth_date foi corrigida)
   - Validar se atleta elegível para categoria da partida

2. **Revalidar gênero:**
   - Confirmar compatibilidade `persons.gender` vs `teams.gender`

3. **Validar flags de restrição:**
   ```sql
   IF athletes.injured = true THEN
     RETURN ERROR 400 "Atleta lesionada não pode ser convocada"
   END IF
   
   IF athletes.suspended_until >= match.date THEN
     RETURN ERROR 400 "Atleta suspensa até [data]"
   END IF
   ```

4. **Validar vínculo ativo:**
   ```sql
   IF NOT EXISTS (
     SELECT 1 FROM team_registrations
     WHERE athlete_id = ? AND team_id = ? AND end_at IS NULL
   ) THEN
     RETURN ERROR 400 "Atleta não possui vínculo ativo com esta equipe"
   END IF
   ```

### Validações ao Excluir (Soft Delete)

1. `deleted_reason` é obrigatório
2. Não apagar fisicamente, usar `deleted_at`
3. Atletas excluídas não aparecem em listagens padrão (WHERE deleted_at IS NULL)
4. Histórico de vínculos e estatísticas preservado (R10 - histórico imutável)

---

## 13. Permissões por Papel

### Visualização
| Papel | Ver listagem | Ver detalhes | Ver histórico |
|-------|--------------|--------------|---------------|
| Super Admin | ✅ Todos clubes | ✅ Sim | ✅ Sim |
| Dirigente | ✅ Sua organização | ✅ Sim | ✅ Sim |
| Coordenador | ✅ Sua organização | ✅ Sim | ✅ Sim |
| Treinador | ✅ Suas equipes | ✅ Sim | ✅ Sim |
| Atleta | ❌ Não | ✅ Apenas próprio | ✅ Apenas próprio |

### Edição
| Papel | Criar | Editar dados | Alterar estado | Vincular equipe | Excluir |
|-------|-------|--------------|----------------|-----------------|---------|
| Super Admin | ✅ | ✅ | ✅ | ✅ | ✅ |
| Dirigente | ✅ | ✅ | ✅ | ✅ | ✅ |
| Coordenador | ✅ | ✅ | ✅ | ✅ | ❌ |
| Treinador | ✅ | ✅ (suas equipes) | ✅ (suas equipes) | ✅ (suas equipes) | ❌ |

---

## 13. Seed Mínimo e Recuperação do Sistema

### **CANÔNICO: Seed Estrutural Obrigatório**

**Seed mínimo obrigatório contém:**
1. ✅ `roles` (Dirigente, Coordenador, Treinador, Atleta)
2. ✅ `superadmin` (Super Administrador estrutural)

**Seeds funcionais (não estruturais):**
- ❌ `categories` (Mirim, Infantil, Cadete, Juvenil, Júnior, Adulto, Master)
- ❌ `defensive_positions`, `offensive_positions`
- ❌ `schooling_levels`

**Motivo da separação:**
- **Seed estrutural:** Necessário para funcionamento básico do sistema (autenticação, autorização)
- **Seeds funcionais:** Podem ser reaplicados por migrations ou importados posteriormente

**Recuperação do sistema (Disaster Recovery):**
1. Admin/Superadmin acessa área especial "Recuperação do Sistema"
2. Comando restaura seed mínimo obrigatório (roles + superadmin)
3. Ação registrada obrigatoriamente em `audit_logs`
4. Usuários comuns bloqueados até restauração completa
5. Seeds funcionais reaplicados via migrations ou importação manual

**Validação do seed:**
- Sistema valida presença de roles e superadmin no startup
- Ausência/corrupção exibe tela de manutenção para usuários comuns
- Apenas superadmin acessa painel de recuperação

---

## 14. Features de Alto Impacto e Baixo Esforço

### **CANÔNICO: Funcionalidades Prioritárias**

#### 14.1. Autocompletar CEP → Endereço

**Objetivo:** Reduzir erros de digitação e agilizar cadastro.

**Implementação:**
- Integração com **ViaCEP API** (gratuita, pública)
- Ao digitar CEP válido, preenche automaticamente:
  - `street` (logradouro)
  - `neighborhood` (bairro)
  - `city` (cidade)
  - `state` (UF)
- Campos preenchidos ficam editáveis (caso API retorne dados incorretos)

**Fluxo:**
```javascript
// Frontend
const cep = "01310-100";
const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`);
const data = await response.json();
// Preenche campos: rua, bairro, cidade, estado
```

**Validações:**
- CEP deve ter formato válido (12345-678)
- Se API retornar erro, permite preenchimento manual
- Não bloqueia cadastro (fallback para manual)

**Impacto:** MÉDIO | **Esforço:** BAIXO | **Prioridade:** 8

---

#### 14.2. Validação de RG/CPF no Frontend

**Objetivo:** Prevenir erros de digitação antes de enviar ao backend.

**Implementação:**
- Validar **dígitos verificadores do CPF** (algoritmo padrão)
- Validar **formato do RG** (sem dígitos verificadores, apenas formato)
- Bibliotecas JS prontas: `cpf-cnpj-validator`, `validate-cpf`

**Fluxo:**
```javascript
import { cpf } from 'cpf-cnpj-validator';

// Validar CPF
if (!cpf.isValid('123.456.789-09')) {
  alert('CPF inválido! Verifique os dígitos.');
  return;
}

// Validar formato RG (apenas números + comprimento)
if (!/^\d{7,9}$/.test(rg)) {
  alert('RG deve conter 7-9 dígitos.');
  return;
}
```

**Validações:**
- CPF: validar dígitos verificadores (algoritmo mod 11)
- RG: validar apenas formato (sem verificação de dígito)
- Mensagens de erro claras para usuário
- Validação duplicada no backend (segurança)

**Impacto:** MÉDIO | **Esforço:** BAIXO | **Prioridade:** 6

---

#### 14.3. Exportação de "Ficha da Atleta" em PDF

**Objetivo:** Compilar todos os dados da atleta em PDF profissional.

**Usado em:**
- Transferências entre organizações
- Apresentações para patrocinadores
- Relatórios administrativos
- Arquivamento físico

**Implementação:**
- Backend: Biblioteca ReportLab (Python) ou WeasyPrint
- Endpoint: `GET /athletes/:id/export-pdf`
- Template padronizado com logo da organização

**Conteúdo do PDF:**
1. **Dados Pessoais:**
   - Nome completo, data nascimento, idade atual
   - RG, CPF (se informado)
   - Telefone, email
   - Endereço completo
   - Foto de perfil (se disponível)

2. **Dados Esportivos:**
   - Gênero, categoria natural
   - Posições (defensiva/ofensiva)
   - Altura, peso, dominância
   - Estado atual (ativa/lesionada/suspensa)

3. **Vínculos Atuais:**
   - Equipes ativas (nome, categoria, data início)
   - Organização atual

4. **Histórico de Vínculos:**
   - Equipes anteriores (nome, período, categoria)
   - Organizações anteriores (se aplicável)

5. **Estatísticas Resumidas:**
   - Jogos disputados (total)
   - Gols marcados (total)
   - Assistências (total)
   - Defesas (se goleira)

6. **Observações:**
   - Responsável legal (se menor)
   - Restrições médicas ativas
   - Notas administrativas

**Layout:**
```
┌─────────────────────────────────────┐
│ [Logo Organização]                  │
│ FICHA DE ATLETA                     │
│                                     │
│ [Foto]  Nome: Maria Silva           │
│         Idade: 15 anos              │
│         Categoria: Cadete Feminino  │
│                                     │
│ DADOS PESSOAIS                      │
│ RG: 12.345.678-9                    │
│ Email: maria@email.com              │
│ ...                                 │
│                                     │
│ ESTATÍSTICAS                        │
│ Jogos: 45 | Gols: 127               │
│ ...                                 │
└─────────────────────────────────────┘
```

**Permissões:**
- ✅ Dirigente (qualquer atleta da organização)
- ✅ Coordenador (qualquer atleta da organização)
- ✅ Treinador (apenas atletas de suas equipes)
- ✅ Atleta (apenas a própria ficha)

**Segurança:**
- PDF gerado on-demand (não armazenado)
- Marca d'água com data/hora de geração
- Log de auditoria: quem exportou, quando, qual atleta

**Impacto:** MÉDIO-ALTO | **Esforço:** MÉDIO | **Prioridade:** 5

---

## 15. Referências

- **REGRAS.md**: Documento principal com todas as regras do sistema
- **RDB17**: Estrutura da tabela athletes
- **RDB10**: Estrutura da tabela team_registrations
- **RDB11**: Estrutura da tabela categories
- **Seção 4**: Visibilidade do Perfil Atleta
- **Seção 5**: Regras de Participação da Atleta
