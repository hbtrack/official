# 006-ADR-TRAIN — Timezone Canônico

**Status:** Aceita
**Data:** 2026-02-08
**Autor:** Equipe HB Track
**Fase:** F2
**Módulos Afetados:** backend | database | frontend

---

## Contexto

Treinos dependem de horário local para agendamento e execução, mas precisam ser comparáveis e ordenáveis globalmente para analytics, relatórios e coordenação entre equipes em diferentes fusos.

Armazenar timestamps em timezone local cria ambiguidade, especialmente durante transições de horário de verão.

**Componentes Relacionados:**
- Modelo de dados: `training_sessions.scheduled_date`, `training_sessions.created_at`, `attendance.created_at`
- API endpoints: todos os endpoints que retornam ou recebem datas
- Frontend: componentes de calendário e agendamento

---

## Decisão

- **Timezone canônico do sistema:** UTC
- Todos os timestamps são armazenados em UTC no banco de dados
- **Conversão para timezone local** ocorre **apenas na borda** (UI/cliente)
- Backend nunca assume timezone local

### Detalhes Técnicos

```python
# Backend: todos os timestamps em UTC
from datetime import datetime, timezone

now = datetime.now(timezone.utc)  # CORRETO
now = datetime.now()               # INCORRETO — timezone-naive
```

```sql
-- PostgreSQL: colunas TIMESTAMP WITH TIME ZONE armazenam em UTC
-- A conversão é responsabilidade do frontend
```

**Stack envolvida:**
- Database: PostgreSQL — `TIMESTAMP WITH TIME ZONE` (armazena UTC internamente)
- Backend: FastAPI/Python — `datetime.now(timezone.utc)`
- Frontend: Next.js — conversão via `Intl.DateTimeFormat` ou lib de datas

---

## Alternativas Consideradas

### Alternativa 1: Armazenar em timezone local do clube

**Prós:**
- Leitura direta no banco sem conversão
- Mais intuitivo para DBAs

**Contras:**
- Ambiguidade durante horário de verão (mesma hora pode existir duas vezes)
- Comparação entre clubes em fusos diferentes é complexa
- Necessidade de armazenar timezone do clube junto a cada timestamp

**Razão da rejeição:** A ambiguidade temporal é inaceitável para um sistema de agendamento e analytics.

### Alternativa 2: Armazenar como Unix timestamp (epoch)

**Prós:**
- Sem ambiguidade (inteiro monotônico)
- Ordenação trivial

**Contras:**
- Não legível por humanos no banco
- Queries de data (filtro por dia/semana/mês) são mais complexas
- PostgreSQL tem suporte nativo superior para TIMESTAMPTZ

**Razão da rejeição:** PostgreSQL oferece TIMESTAMPTZ como solução superior, com ordenação e queries nativas.

---

## Consequências

### Positivas
- ✅ Elimina ambiguidade temporal (sem bugs de horário de verão)
- ✅ Simplifica recorrência e agendamento entre fusos
- ✅ Comparação e ordenação globais triviais
- ✅ Alinhamento com padrão ISO 8601

### Negativas
- ⚠️ Frontend deve sempre converter para exibição local
- ⚠️ Testes devem considerar UTC, não timezone do desenvolvedor

### Neutras
- ℹ️ PostgreSQL armazena TIMESTAMPTZ internamente em UTC, alinhado com esta decisão

---

## Validação

### Critérios de Conformidade
- [x] Colunas de data usam `TIMESTAMP WITH TIME ZONE`
- [x] Backend gera timestamps em UTC
- [x] Frontend responsável pela conversão para timezone local

---

## Referências

- `docs/TRD_TRAINING.md`: tratamento explícito de timezone
- ADRs relacionados: ADR-TRAIN-001 (SSOT), ADR-TRAIN-003 (lifecycle — scheduling depende de timezone)

---

## Revisões

| Data | Autor | Mudança | Versão |
|------|-------|---------|--------|
| 2026-02-08 | Equipe HB Track | Criação inicial | 1.0 |
| 2026-02-08 | Equipe HB Track | Adequação ao template padrão ADR | 1.1 |
