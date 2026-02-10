<!-- STATUS: NEEDS_REVIEW -->

# 🏆 PLANO DE IMPLEMENTAÇÃO - MÓDULO COMPETIÇÕES COM IA

> **Objetivo**: Sistema onde a IA (Gemini) preenche automaticamente o formulário de cadastro de competição a partir de PDF, e o usuário apenas valida antes de salvar no banco.

---

## � STATUS DE IMPLEMENTAÇÃO

| FASE | Status | Data | Observações |
|------|--------|------|-------------|
| **FASE 1: Database** | ✅ CONCLUÍDA | 2026-01-08 | Migration aplicada - 5 tabelas criadas/alteradas |
| **FASE 2: Backend Models** | ✅ CONCLUÍDA | 2026-01-08 | 5 Models SQLAlchemy + Schemas Pydantic |
| **FASE 3: Backend Gemini** | ✅ CONCLUÍDA | 2026-01-08 | Serviço Gemini com prompt especializado handebol |
| **FASE 4: Backend Endpoints** | ✅ CONCLUÍDA | 2026-01-08 | 17 endpoints criados em competitions_v2.py |
| **FASE 5: Frontend Services** | ✅ CONCLUÍDA | 2026-01-08 | API Service + 6 React Hooks |
| **FASE 6: Frontend Components** | ✅ CONCLUÍDA | 2026-01-08 | Context + Wizard + UI Components |
| **FASE 7: Integração & Testes** | ✅ CONCLUÍDA | 2026-01-08 | Integração completa - pronto para uso |

### ✅ FASE 1 - Detalhes da Execução

**Arquivo Migration**: `Hb Track - Backend/db/migrations/add_competitions_module.sql`

**Tabelas Criadas/Alteradas**:
| Tabela | Ação | Descrição |
|--------|------|-----------|
| `competitions` | ALTER | Adicionados 15+ novos campos (team_id, season, competition_type, etc.) |
| `competition_phases` | CREATE | Fases da competição (grupos, mata-mata, etc.) |
| `competition_opponent_teams` | CREATE | Equipes adversárias com stats JSONB |
| `competition_matches` | CREATE | Jogos da competição com external_reference_id |
| `competition_standings` | CREATE | Cache de classificação por fase |

**Recursos Criados**:
- ✅ 5 tabelas com índices otimizados
- ✅ Constraints de validação (status, types, modality)
- ✅ Trigger automático para atualizar stats após resultados
- ✅ Suporte a `external_reference_id` para upsert de jogos (reimportação PDF)
- ✅ Campo `points_per_win` configurável (padrão 2 para handebol)
- ✅ Soft delete em competitions (deleted_at, deleted_reason)

### ✅ FASE 2 - Detalhes da Execução

**Models SQLAlchemy Criados/Atualizados**:
| Arquivo | Model | Status |
|---------|-------|--------|
| `app/models/competition.py` | `Competition` | ✅ Atualizado (15+ novos campos) |
| `app/models/competition_phase.py` | `CompetitionPhase` | ✅ Criado |
| `app/models/competition_opponent_team.py` | `CompetitionOpponentTeam` | ✅ Criado |
| `app/models/competition_match.py` | `CompetitionMatch` | ✅ Criado |
| `app/models/competition_standing.py` | `CompetitionStanding` | ✅ Criado |

**Schemas Pydantic Criados**:
| Arquivo | Schemas | Descrição |
|---------|---------|-----------|
| `app/schemas/competitions_v2.py` | 25+ schemas | Create, Update, Response para todas entidades + AI schemas |

**Destaques**:
- ✅ Enums para todos os tipos (CompetitionType, PhaseType, MatchStatus, etc.)
- ✅ Schemas para importação IA (AIExtractedCompetition, AIParseRequest/Response)
- ✅ Properties computadas nos models (is_finished, winner_id, etc.)
- ✅ Relationships bidirecionais configurados
- ✅ Exportados em `app/models/__init__.py`

### ✅ FASE 3 - Detalhes da Execução

**Serviço Gemini Criado**:
| Arquivo | Classe | Descrição |
|---------|--------|-----------|
| `app/services/gemini_competition_service.py` | `GeminiCompetitionService` | Serviço de parsing de PDF via Gemini |

**Características Implementadas**:
- ✅ **Prompt especializado para HANDEBOL** (placares típicos 20-35 gols, categorias brasileiras)
- ✅ **Confidence scores** por campo extraído (0.0 a 1.0)
- ✅ **Usa google-genai** (pacote atualizado, não o deprecated)
- ✅ **Gemini 1.5 Flash** (melhor custo-benefício para PDFs)
- ✅ **Suporte a hints** (dicas do usuário para melhorar extração)
- ✅ **Validação de extração** com warnings e sugestões

**Métodos Disponíveis**:
- `parse_regulation_pdf(pdf_base64, our_team_name, hints)` - Extrai dados do PDF
- `validate_extraction(extracted_data)` - Valida dados e retorna warnings
- `is_available()` - Verifica se serviço está configurado

**Configuração Necessária**:
```env
GEMINI_API_KEY=sua_chave_aqui
```

### ✅ FASE 4 - Detalhes da Execução

**Router Criado**: `app/api/v1/routers/competitions_v2.py`

**Endpoints Implementados (17 total)**:

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/competitions/v2` | POST | Criar competição V2 |
| `/competitions/v2/parse-pdf` | POST | Parse de PDF com IA Gemini |
| `/competitions/v2/{id}/import-from-ai` | POST | Importar dados extraídos pela IA |
| `/competitions/v2/{id}/full` | GET | Competição completa com relações |
| `/competitions/{id}/phases` | GET/POST | CRUD fases |
| `/competitions/{id}/phases/{phase_id}` | PATCH/DELETE | Atualizar/remover fase |
| `/competitions/{id}/opponent-teams` | GET/POST | CRUD equipes adversárias |
| `/competitions/{id}/opponent-teams/bulk` | POST | Criar equipes em lote |
| `/competitions/{id}/matches` | GET/POST | CRUD jogos |
| `/competitions/{id}/matches/bulk` | POST | Upsert jogos (via external_reference_id) |
| `/competitions/{id}/matches/{mid}/result` | PATCH | Atualizar resultado |
| `/competitions/{id}/standings` | GET | Classificação |

**Funcionalidades**:
- ✅ Criação de competição V2 com todos os novos campos
- ✅ Upload e parsing de PDF via Gemini IA
- ✅ Importação de dados extraídos pela IA para competição existente
- ✅ CRUD completo para fases, equipes adversárias e jogos
- ✅ Upsert de jogos via `external_reference_id` (reimportação de PDF)
- ✅ Cálculo de classificação com critérios de desempate configuráveis
- ✅ Integração com sistema de permissões existente

**Registrado em**: `app/api/v1/api.py` com tag `competitions-v2`

### ✅ FASE 5 - Detalhes da Execução

**Arquivos Criados**:

| Arquivo | Descrição |
|---------|-----------|
| `src/lib/api/competitions-v2.ts` | API Service completo com todos os types |
| `src/lib/hooks/useCompetitionsV2.ts` | 6 React Hooks para gerenciamento de estado |

**API Service (`competitions-v2.ts`)**:
- ✅ Todos os types TypeScript (Competition, Phase, OpponentTeam, Match, Standing, AI*)
- ✅ Enums: CompetitionType, PhaseType, MatchStatus, CompetitionStatus, Modality
- ✅ Métodos para todos os 17 endpoints do backend
- ✅ Helper `fileToBase64` para converter PDF

**React Hooks Criados**:

| Hook | Descrição |
|------|-----------|
| `useCompetitionV2` | Gerencia competição individual (CRUD) |
| `useAIParsePdf` | Processa PDF com Gemini IA |
| `useCompetitionPhases` | CRUD de fases |
| `useCompetitionOpponentTeams` | CRUD de equipes adversárias |
| `useCompetitionMatches` | CRUD de jogos + resultados |
| `useCompetitionStandings` | Classificação |

**Funcionalidades dos Hooks**:
- ✅ Auto-fetch ao montar componente
- ✅ Tratamento de erros centralizado (rede, 401, 403, 404)
- ✅ Atualização otimista do estado local
- ✅ Métodos de refetch
- ✅ `useAIParsePdf` com conversão de File para base64

**Exportados em**:
- `src/lib/api/index.ts`
- `src/lib/hooks/index.ts`

### ✅ FASE 7 - Integração & Testes (CONCLUÍDA 2026-01-08)

**Arquivos Modificados na Integração**:
- `CompetitionsLayoutWrapper.tsx` - Adicionado CompetitionV2Provider
- `CompetitionsHeader.tsx` - Dropdown com "Importar com IA" e "Criar manualmente"
- `CompetitionsDashboard.tsx` - Wizard integrado + botões no empty state
- `components/competitions/index.ts` - Exports duplicados corrigidos
- `lib/api/index.ts` - Re-exports de types V2 sem conflitos
- `CreateCompetitionWizard.tsx` - Props isOpen e teamId tornados opcionais

**Fluxo de Uso Implementado**:
1. Usuário acessa `/competitions`
2. Clica "Nova Competição" (dropdown aparece)
3. Escolhe "Importar com IA" (wizard modal abre)
4. Upload PDF do regulamento
5. IA Gemini processa
6. Revisão com badges de confiança
7. Confirma e salva no banco

---

## �📑 ÍNDICE

1. [Visão Geral do Fluxo](#1-visão-geral-do-fluxo)
2. [Migrations - Tabelas do Banco](#2-migrations---tabelas-do-banco)
3. [Backend - Endpoints e Integração Gemini](#3-backend---endpoints-e-integração-gemini)
4. [Frontend - Componentes e Fluxo UX](#4-frontend---componentes-e-fluxo-ux)
5. [Estrutura JSON da IA](#5-estrutura-json-da-ia)
6. [Formas de Disputa Suportadas](#6-formas-de-disputa-suportadas)
7. [Checklist de Implementação](#7-checklist-de-implementação)

---

## 1. VISÃO GERAL DO FLUXO

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FLUXO COMPLETO DO SISTEMA                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐│
│  │ 1.UPLOAD │───▶│ 2.GEMINI │───▶│ 3.REVIEW │───▶│ 4.VALIDAR│───▶│5.SALVAR││
│  │   PDF    │    │  LÊ PDF  │    │   FORM   │    │  USUÁRIO │    │  BANCO ││
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘    └────────┘│
│       │               │               │               │              │      │
│       ▼               ▼               ▼               ▼              ▼      │
│  Drag & Drop    Gemini 1.5     Form pré-      Usuário         Persiste:   │
│  ou click       lê PDF direto  preenchido     ajusta se       - competition│
│  arquivo        (visão comp.)  com badges:    necessário      - teams      │
│  .pdf           Sem OCR!       🟢 Detectado   e confirma      - phases     │
│                 Retorna JSON   🔶 Revisar                     - matches    │
│                 + confidence   🔴 Faltando                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### ⚠️ IMPORTANTE: Gemini como Parser (Sem OCR)

O **Gemini 1.5 Flash** possui **visão computacional** e lê PDFs diretamente!
- **NÃO precisa** de Tesseract ou AWS Textract
- **Evita erro comum** de OCR ler colunas de tabelas na ordem errada
- Backend envia o buffer do PDF direto para a API do Google
- IA retorna JSON estruturado com `confidence_scores`

### Tempo Estimado por Etapa
| Etapa | Tempo | Responsável |
|-------|-------|-------------|
| Upload PDF | 1s | Frontend |
| Processamento Gemini | 3-8s | Backend + Gemini API |
| Renderizar Form | 1s | Frontend |
| Validação Usuário | 30s-2min | Usuário |
| Salvar no Banco | 1s | Backend |

---

## 2. MIGRATIONS - TABELAS DO BANCO

### 2.1 Arquivo de Migration

**Arquivo**: `Hb Track - Backend/db/migrations/add_competitions_tables.sql`

```sql
-- ============================================================================
-- MIGRATION: Tabelas para Módulo de Competições
-- Data: 2026-01-08
-- Descrição: Cria estrutura completa para competições com fases, jogos e equipes
-- ============================================================================

-- 1. TABELA: competitions (Competição principal)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competitions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
    
    -- Informações básicas
    name VARCHAR(255) NOT NULL,
    season VARCHAR(50) NOT NULL,
    organization VARCHAR(255),
    modality VARCHAR(50) NOT NULL DEFAULT 'masculino',
    
    -- Forma de disputa
    competition_type VARCHAR(50) NOT NULL,
    format_details JSONB DEFAULT '{}',
    
    -- Critérios de desempate (ordenados por prioridade)
    tiebreaker_criteria JSONB DEFAULT '["pontos", "saldo_gols", "gols_pro", "confronto_direto"]',
    
    -- Status e controle
    status VARCHAR(50) DEFAULT 'draft',
    current_phase_id UUID,
    
    -- Regulamento
    regulation_file_url VARCHAR(500),
    regulation_notes TEXT,
    
    -- Auditoria
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    
    CONSTRAINT chk_competition_type CHECK (
        competition_type IN (
            'turno_unico',
            'turno_returno', 
            'grupos',
            'grupos_mata_mata',
            'mata_mata',
            'triangular',
            'quadrangular',
            'custom'
        )
    ),
    CONSTRAINT chk_modality CHECK (
        modality IN ('masculino', 'feminino', 'misto')
    ),
    CONSTRAINT chk_status CHECK (
        status IN ('draft', 'active', 'finished', 'cancelled')
    )
);

-- Índices
CREATE INDEX idx_competitions_team_id ON competitions(team_id);
CREATE INDEX idx_competitions_season ON competitions(season);
CREATE INDEX idx_competitions_status ON competitions(status);

-- ============================================================================
-- 2. TABELA: competition_phases (Fases da competição)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_phases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    
    name VARCHAR(100) NOT NULL,
    phase_type VARCHAR(50) NOT NULL,
    order_index INT NOT NULL DEFAULT 0,
    
    -- Configurações específicas da fase
    config JSONB DEFAULT '{}',
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_phase_type CHECK (
        phase_type IN (
            'group',           -- Fase de grupos
            'knockout',        -- Mata-mata
            'round_robin',     -- Todos contra todos
            'semifinal',
            'final',
            'third_place',     -- Disputa 3º lugar
            'custom'
        )
    ),
    CONSTRAINT chk_phase_status CHECK (
        status IN ('pending', 'in_progress', 'finished')
    )
);

CREATE INDEX idx_phases_competition ON competition_phases(competition_id);
CREATE INDEX idx_phases_order ON competition_phases(competition_id, order_index);

-- ============================================================================
-- 3. TABELA: competition_opponent_teams (Equipes adversárias na competição)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_opponent_teams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    
    -- Informações da equipe adversária
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(50),
    category VARCHAR(50),
    city VARCHAR(100),
    logo_url VARCHAR(500),
    
    -- Grupo (se houver fase de grupos)
    group_name VARCHAR(50),
    
    -- Estatísticas calculadas (atualizadas após cada jogo)
    stats JSONB DEFAULT '{
        "points": 0,
        "played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "goals_for": 0,
        "goals_against": 0,
        "goal_difference": 0
    }',
    
    -- Status na competição
    status VARCHAR(50) DEFAULT 'active',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_opponent_status CHECK (
        status IN ('active', 'eliminated', 'qualified', 'withdrawn')
    )
);

CREATE INDEX idx_opponent_teams_competition ON competition_opponent_teams(competition_id);
CREATE INDEX idx_opponent_teams_group ON competition_opponent_teams(competition_id, group_name);

-- ============================================================================
-- 4. TABELA: competition_matches (Jogos da competição)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_matches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    phase_id UUID REFERENCES competition_phases(id) ON DELETE SET NULL,
    
    -- ID externo para upsert (evita duplicação ao reimportar PDF)
    external_reference_id VARCHAR(100),
    
    -- Equipes do jogo
    home_team_id UUID REFERENCES competition_opponent_teams(id),
    away_team_id UUID REFERENCES competition_opponent_teams(id),
    
    -- Flag para identificar se é jogo da NOSSA equipe
    is_our_match BOOLEAN DEFAULT false,
    our_team_is_home BOOLEAN,
    
    -- Data e local
    match_date DATE,
    match_time TIME,
    match_datetime TIMESTAMP WITH TIME ZONE,
    location VARCHAR(255),
    
    -- Rodada/Round
    round_number INT,
    round_name VARCHAR(100),
    
    -- Resultado
    home_score INT,
    away_score INT,
    
    -- Resultado em caso de prorrogação/pênaltis
    home_score_extra INT,
    away_score_extra INT,
    home_score_penalties INT,
    away_score_penalties INT,
    
    -- Status do jogo
    status VARCHAR(50) DEFAULT 'scheduled',
    
    -- Observações
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_match_status CHECK (
        status IN ('scheduled', 'in_progress', 'finished', 'postponed', 'cancelled')
    ),
    CONSTRAINT chk_different_teams CHECK (home_team_id != away_team_id)
);

CREATE INDEX idx_matches_competition ON competition_matches(competition_id);
CREATE INDEX idx_matches_phase ON competition_matches(phase_id);
CREATE INDEX idx_matches_date ON competition_matches(match_date);
CREATE INDEX idx_matches_our ON competition_matches(competition_id, is_our_match);
CREATE INDEX idx_matches_status ON competition_matches(status);
CREATE UNIQUE INDEX idx_matches_external_ref ON competition_matches(competition_id, external_reference_id) WHERE external_reference_id IS NOT NULL;

-- ============================================================================
-- 5. TABELA: competition_standings (Classificação - cache para performance)
-- ============================================================================
CREATE TABLE IF NOT EXISTS competition_standings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    competition_id UUID NOT NULL REFERENCES competitions(id) ON DELETE CASCADE,
    phase_id UUID REFERENCES competition_phases(id) ON DELETE CASCADE,
    opponent_team_id UUID NOT NULL REFERENCES competition_opponent_teams(id) ON DELETE CASCADE,
    
    -- Posição e grupo
    position INT NOT NULL,
    group_name VARCHAR(50),
    
    -- Estatísticas
    points INT DEFAULT 0,
    played INT DEFAULT 0,
    wins INT DEFAULT 0,
    draws INT DEFAULT 0,
    losses INT DEFAULT 0,
    goals_for INT DEFAULT 0,
    goals_against INT DEFAULT 0,
    goal_difference INT DEFAULT 0,
    
    -- Forma recente (últimos 5 jogos: W, D, L)
    recent_form VARCHAR(10),
    
    -- Status de classificação
    qualification_status VARCHAR(50),
    
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT chk_qualification_status CHECK (
        qualification_status IN ('qualified', 'playoffs', 'relegation', 'eliminated', NULL)
    ),
    
    UNIQUE(competition_id, phase_id, opponent_team_id)
);

CREATE INDEX idx_standings_competition ON competition_standings(competition_id);
CREATE INDEX idx_standings_position ON competition_standings(competition_id, phase_id, position);

-- ============================================================================
-- 6. FUNÇÃO: Atualizar estatísticas após resultado de jogo
-- ============================================================================
CREATE OR REPLACE FUNCTION update_team_stats_after_match()
RETURNS TRIGGER AS $$
DECLARE
    home_points INT;
    away_points INT;
BEGIN
    -- Só atualiza se o jogo foi finalizado
    IF NEW.status = 'finished' AND NEW.home_score IS NOT NULL AND NEW.away_score IS NOT NULL THEN
        
        -- Calcula pontos
        IF NEW.home_score > NEW.away_score THEN
            home_points := 3;
            away_points := 0;
        ELSIF NEW.home_score < NEW.away_score THEN
            home_points := 0;
            away_points := 3;
        ELSE
            home_points := 1;
            away_points := 1;
        END IF;
        
        -- Atualiza estatísticas do time da casa
        UPDATE competition_opponent_teams
        SET stats = jsonb_set(
            jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                jsonb_set(
                                    stats,
                                    '{points}', to_jsonb((stats->>'points')::int + home_points)
                                ),
                                '{played}', to_jsonb((stats->>'played')::int + 1)
                            ),
                            '{wins}', to_jsonb((stats->>'wins')::int + CASE WHEN NEW.home_score > NEW.away_score THEN 1 ELSE 0 END)
                        ),
                        '{draws}', to_jsonb((stats->>'draws')::int + CASE WHEN NEW.home_score = NEW.away_score THEN 1 ELSE 0 END)
                    ),
                    '{losses}', to_jsonb((stats->>'losses')::int + CASE WHEN NEW.home_score < NEW.away_score THEN 1 ELSE 0 END)
                ),
                '{goals_for}', to_jsonb((stats->>'goals_for')::int + NEW.home_score)
            ),
            '{goals_against}', to_jsonb((stats->>'goals_against')::int + NEW.away_score)
        ),
        updated_at = NOW()
        WHERE id = NEW.home_team_id;
        
        -- Atualiza estatísticas do time visitante
        UPDATE competition_opponent_teams
        SET stats = jsonb_set(
            jsonb_set(
                jsonb_set(
                    jsonb_set(
                        jsonb_set(
                            jsonb_set(
                                jsonb_set(
                                    stats,
                                    '{points}', to_jsonb((stats->>'points')::int + away_points)
                                ),
                                '{played}', to_jsonb((stats->>'played')::int + 1)
                            ),
                            '{wins}', to_jsonb((stats->>'wins')::int + CASE WHEN NEW.away_score > NEW.home_score THEN 1 ELSE 0 END)
                        ),
                        '{draws}', to_jsonb((stats->>'draws')::int + CASE WHEN NEW.home_score = NEW.away_score THEN 1 ELSE 0 END)
                    ),
                    '{losses}', to_jsonb((stats->>'losses')::int + CASE WHEN NEW.away_score < NEW.home_score THEN 1 ELSE 0 END)
                ),
                '{goals_for}', to_jsonb((stats->>'goals_for')::int + NEW.away_score)
            ),
            '{goals_against}', to_jsonb((stats->>'goals_against')::int + NEW.home_score)
        ),
        updated_at = NOW()
        WHERE id = NEW.away_team_id;
        
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para atualizar estatísticas
DROP TRIGGER IF EXISTS trigger_update_stats_after_match ON competition_matches;
CREATE TRIGGER trigger_update_stats_after_match
    AFTER INSERT OR UPDATE ON competition_matches
    FOR EACH ROW
    EXECUTE FUNCTION update_team_stats_after_match();

-- ============================================================================
-- 7. COMENTÁRIOS NAS TABELAS
-- ============================================================================
COMMENT ON TABLE competitions IS 'Competições que a equipe participa';
COMMENT ON TABLE competition_phases IS 'Fases de cada competição (grupos, mata-mata, etc)';
COMMENT ON TABLE competition_opponent_teams IS 'Equipes adversárias em cada competição';
COMMENT ON TABLE competition_matches IS 'Jogos de cada competição';
COMMENT ON TABLE competition_standings IS 'Classificação/tabela de cada fase (cache)';

COMMENT ON COLUMN competitions.competition_type IS 'Tipo: turno_unico, turno_returno, grupos, grupos_mata_mata, mata_mata, triangular, quadrangular, custom';
COMMENT ON COLUMN competitions.tiebreaker_criteria IS 'Array JSON com critérios de desempate em ordem de prioridade';
COMMENT ON COLUMN competitions.format_details IS 'Detalhes específicos do formato (num_grupos, classificados_por_grupo, etc)';
```

### 2.2 Executar Migration

```bash
# No terminal, dentro de Hb Track - Backend
cd "c:\HB TRACK\Hb Track - Backend"
python -c "
from app.db.database import engine
import asyncio

async def run_migration():
    async with engine.begin() as conn:
        with open('db/migrations/add_competitions_tables.sql', 'r') as f:
            sql = f.read()
        await conn.execute(text(sql))
        print('Migration executada com sucesso!')

asyncio.run(run_migration())
"
```

---

## 3. BACKEND - ENDPOINTS E INTEGRAÇÃO GEMINI

### 3.1 Instalar Dependência Gemini

```bash
pip install -U google-generativeai
```

Adicionar em `requirements.txt`:
```
google-generativeai>=0.3.0
```

### 3.2 Serviço de Integração com Gemini

**Arquivo**: `Hb Track - Backend/app/services/gemini_competition_service.py`

```python
"""
Serviço de integração com Google Gemini para extração de dados de competições via PDF.
"""
import google.generativeai as genai
import json
import tempfile
import os
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCkOXjNkR9DKO527hQ_RWPMKSM8Hmygjus")

genai.configure(api_key=GEMINI_API_KEY)

# ============================================================================
# SCHEMAS DE RESPOSTA
# ============================================================================

class ExtractedMatch(BaseModel):
    """Jogo extraído do PDF"""
    round_number: Optional[int] = None
    round_name: Optional[str] = None
    home_team: str
    away_team: str
    date: Optional[str] = None  # formato: YYYY-MM-DD
    time: Optional[str] = None  # formato: HH:MM
    location: Optional[str] = None

class ExtractedTeam(BaseModel):
    """Equipe extraída do PDF"""
    name: str
    short_name: Optional[str] = None
    group: Optional[str] = None
    category: Optional[str] = None

class ExtractedPhase(BaseModel):
    """Fase extraída do PDF"""
    name: str
    type: str  # group, knockout, round_robin, etc
    order: int

class ExtractedCompetition(BaseModel):
    """Dados completos extraídos do PDF"""
    name: str
    season: Optional[str] = None
    organization: Optional[str] = None
    modality: Optional[str] = None  # masculino, feminino, misto
    competition_type: str  # turno_unico, grupos, mata_mata, etc
    tiebreaker_criteria: List[str] = []
    teams: List[ExtractedTeam] = []
    phases: List[ExtractedPhase] = []
    matches: List[ExtractedMatch] = []
    regulation_summary: Optional[str] = None
    warnings: List[str] = []  # Avisos sobre dados incompletos

# ============================================================================
# SYSTEM INSTRUCTION (PROMPT DA IA)
# ============================================================================

SYSTEM_INSTRUCTION = """
Você é um extrator especializado em dados de competições esportivas de HANDEBOL.
Sua tarefa é ler PDFs de regulamentos, tabelas de jogos e extrair dados estruturados.

## REGRAS DE EXTRAÇÃO:

1. **Nome da Competição**: Extraia o nome completo oficial
2. **Temporada**: Ano ou período (ex: "2026", "2025/2026")
3. **Organização**: Federação, liga ou entidade organizadora
4. **Modalidade**: masculino, feminino ou misto
5. **Tipo de Disputa** (competition_type):
   - "turno_unico": Todos jogam contra todos uma vez
   - "turno_returno": Todos jogam contra todos duas vezes (ida e volta)
   - "grupos": Fase de grupos apenas
   - "grupos_mata_mata": Grupos + eliminatórias
   - "mata_mata": Apenas eliminatórias diretas
   - "triangular": 3 equipes se enfrentam
   - "quadrangular": 4 equipes se enfrentam
   - "custom": Formato especial

6. **Critérios de Desempate** (tiebreaker_criteria):
   Extraia na ORDEM de prioridade. Valores possíveis:
   - "pontos"
   - "saldo_gols" 
   - "gols_pro"
   - "confronto_direto"
   - "gols_contra" (menos gols sofridos)
   - "cartoes" (menos cartões)
   - "sorteio"

7. **Equipes**: Nome completo, abreviação se houver, grupo (A, B, etc)

8. **Fases**: Nome da fase, tipo (group/knockout/round_robin), ordem

9. **Jogos**: 
   - Rodada (número e/ou nome)
   - Times (mandante e visitante)
   - Data no formato YYYY-MM-DD
   - Horário no formato HH:MM
   - Local (se disponível)
   - external_id: identificador único do jogo no PDF (ex: "J01", "R1-G1" ou número sequencial)

## REGRAS ESPECÍFICAS PARA HANDEBOL:

10. **Pontuação Diferenciada**: 
    - Verifique se há pontuação diferenciada (padrão handebol: 2 pontos vitória, 1 empate, 0 derrota)
    - Se encontrar "3 pontos por vitória", registre em points_per_win: 3
    - Caso contrário, assuma points_per_win: 2 (padrão handebol)

11. **Cruzamento Olímpico**:
    - Se houver cruzamento olímpico (1ºA x 2ºB e 1ºB x 2ºA), categorize como fase: "semifinal"
    - Identifique automaticamente este padrão nas tabelas de mata-mata

12. **Tipo de Disputa** (OBRIGATÓRIO usar apenas estes termos):
    - "grupos" - Fase de grupos apenas
    - "mata_mata" - Eliminação direta
    - "turno_unico" - Todos contra todos (1 turno)
    - "grupos_mata_mata" - Grupos + eliminatórias
    - Se não se encaixar, use "custom"

13. **Nível de Confiança**:
    - Para cada campo extraído, calcule um score de confiança (0.0 a 1.0)
    - Se encontrar o dado explicitamente no texto: 0.95-1.0
    - Se inferir de contexto: 0.7-0.9
    - Se for suposição/padrão: 0.5-0.7
    - Se não encontrar: null

## FORMATO DE RESPOSTA:
Retorne APENAS JSON válido, sem markdown, sem explicações.

## TRATAMENTO DE DADOS FALTANTES:
- Se não encontrar um dado, use null
- Adicione avisos na lista "warnings" sobre dados incompletos
- Nunca invente dados que não estão no documento

## EXEMPLO DE SAÍDA:
{
  "name": "Copa Estadual de Handebol Sub-18",
  "season": "2026",
  "organization": "Federação Paulista de Handebol",
  "modality": "masculino",
  "competition_type": "grupos_mata_mata",
  "points_per_win": 2,
  "tiebreaker_criteria": ["pontos", "saldo_gols", "confronto_direto", "gols_pro"],
  "teams": [
    {"name": "EC Pinheiros", "short_name": "PIN", "group": "A", "category": "Sub-18"},
    {"name": "Metodista", "short_name": "MET", "group": "A", "category": "Sub-18"}
  ],
  "phases": [
    {"name": "Fase de Grupos", "type": "group", "order": 1},
    {"name": "Semifinais", "type": "semifinal", "order": 2, "is_olympic_cross": true},
    {"name": "Final", "type": "final", "order": 3}
  ],
  "matches": [
    {
      "external_id": "R1-GA-01",
      "round_number": 1,
      "round_name": "1ª Rodada - Grupo A",
      "home_team": "EC Pinheiros",
      "away_team": "Metodista",
      "date": "2026-03-15",
      "time": "14:00",
      "location": null
    }
  ],
  "regulation_summary": "Competição com 2 grupos de 4 equipes...",
  "warnings": ["Horários de 3 jogos não identificados", "Local dos jogos não especificado"],
  "confidence_scores": {
    "name": 0.98,
    "season": 0.95,
    "organization": 0.90,
    "competition_type": 0.85,
    "teams": 0.92,
    "matches": 0.75,
    "tiebreaker_criteria": 0.60
  },
  "fields_to_review": ["matches", "tiebreaker_criteria"]
}
"""

# ============================================================================
# MODELO GEMINI CONFIGURADO
# ============================================================================

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.1,  # Baixa temperatura para respostas mais consistentes
    }
)

# ============================================================================
# FUNÇÃO PRINCIPAL DE EXTRAÇÃO
# ============================================================================

async def extract_competition_from_pdf(pdf_content: bytes, filename: str = "competition.pdf") -> dict:
    """
    Extrai dados de competição de um arquivo PDF usando Gemini.
    
    Args:
        pdf_content: Bytes do arquivo PDF
        filename: Nome do arquivo para referência
        
    Returns:
        Dict com dados extraídos ou erro
    """
    try:
        # 1. Salva PDF temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(pdf_content)
            tmp_path = tmp.name
        
        try:
            # 2. Upload para Gemini
            arquivo = genai.upload_file(path=tmp_path, display_name=filename)
            
            # 3. Processa com IA
            prompt = """
            Analise este PDF de competição esportiva e extraia TODOS os dados seguindo o formato especificado.
            
            IMPORTANTE:
            - Extraia TODAS as equipes mencionadas
            - Extraia TODOS os jogos com datas e horários
            - Identifique corretamente o tipo de disputa
            - Liste os critérios de desempate na ordem correta
            
            Retorne o JSON completo.
            """
            
            response = model.generate_content([arquivo, prompt])
            
            # 4. Parse do JSON
            result = json.loads(response.text)
            
            # 5. Validação básica e enriquecimento
            result = _enrich_and_validate(result)
            
            return {
                "success": True,
                "data": result,
                "message": "Dados extraídos com sucesso"
            }
            
        finally:
            # Limpa arquivo temporário
            os.unlink(tmp_path)
            
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "Erro ao processar resposta da IA",
            "details": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": "Erro ao processar PDF",
            "details": str(e)
        }


def _enrich_and_validate(data: dict) -> dict:
    """Enriquece e valida os dados extraídos."""
    
    warnings = data.get("warnings", [])
    
    # Valida campos obrigatórios
    if not data.get("name"):
        warnings.append("Nome da competição não identificado")
        data["name"] = "Competição sem nome"
    
    if not data.get("competition_type"):
        warnings.append("Tipo de disputa não identificado - usando 'turno_unico' como padrão")
        data["competition_type"] = "turno_unico"
    
    # Garante que temos critérios de desempate padrão
    if not data.get("tiebreaker_criteria"):
        data["tiebreaker_criteria"] = ["pontos", "saldo_gols", "gols_pro", "confronto_direto"]
        warnings.append("Critérios de desempate não encontrados - usando padrão")
    
    # Tenta inferir temporada se não encontrou
    if not data.get("season"):
        current_year = datetime.now().year
        data["season"] = str(current_year)
        warnings.append(f"Temporada não identificada - usando {current_year}")
    
    # Adiciona fases padrão se não encontrou
    if not data.get("phases") and data.get("matches"):
        data["phases"] = [{"name": "Fase Única", "type": "round_robin", "order": 1}]
        warnings.append("Fases não identificadas - criada fase única")
    
    # Valida equipes
    teams = data.get("teams", [])
    if not teams and data.get("matches"):
        # Extrai equipes dos jogos
        team_names = set()
        for match in data.get("matches", []):
            if match.get("home_team"):
                team_names.add(match["home_team"])
            if match.get("away_team"):
                team_names.add(match["away_team"])
        
        data["teams"] = [{"name": name, "group": None} for name in team_names]
        warnings.append(f"Equipes extraídas dos jogos: {len(data['teams'])} encontradas")
    
    # Conta estatísticas
    stats = {
        "teams_count": len(data.get("teams", [])),
        "matches_count": len(data.get("matches", [])),
        "phases_count": len(data.get("phases", [])),
        "matches_with_date": sum(1 for m in data.get("matches", []) if m.get("date")),
        "matches_with_time": sum(1 for m in data.get("matches", []) if m.get("time")),
    }
    
    data["extraction_stats"] = stats
    data["warnings"] = warnings
    
    # Calcula confidence_scores se não vier da IA
    if "confidence_scores" not in data:
        data["confidence_scores"] = _calculate_confidence_scores(data)
    
    # Define campos para revisão (confiança < 0.8)
    if "fields_to_review" not in data:
        data["fields_to_review"] = [
            field for field, score in data["confidence_scores"].items()
            if score < 0.8
        ]
    
    return data


def _calculate_confidence_scores(data: dict) -> dict:
    """Calcula scores de confiança para cada campo."""
    scores = {}
    
    # Nome: alta confiança se não for padrão
    scores["name"] = 0.95 if data.get("name") and data["name"] != "Competição sem nome" else 0.3
    
    # Temporada: alta se foi extraída, média se inferida
    scores["season"] = 0.9 if data.get("season") else 0.5
    
    # Organização
    scores["organization"] = 0.9 if data.get("organization") else 0.0
    
    # Tipo de competição
    scores["competition_type"] = 0.85 if data.get("competition_type") != "turno_unico" else 0.6
    
    # Equipes: baseado na quantidade
    teams_count = len(data.get("teams", []))
    scores["teams"] = min(0.95, 0.5 + (teams_count * 0.05)) if teams_count > 0 else 0.0
    
    # Jogos: baseado em completude
    matches = data.get("matches", [])
    if matches:
        with_date = sum(1 for m in matches if m.get("date"))
        with_time = sum(1 for m in matches if m.get("time"))
        completeness = (with_date + with_time) / (len(matches) * 2)
        scores["matches"] = 0.5 + (completeness * 0.45)
    else:
        scores["matches"] = 0.0
    
    # Critérios de desempate
    criteria = data.get("tiebreaker_criteria", [])
    scores["tiebreaker_criteria"] = 0.9 if len(criteria) > 2 else 0.5
    
    return scores


# ============================================================================
# FUNÇÃO PARA TESTE LOCAL
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    # Teste com arquivo local
    async def test():
        with open("test_competition.pdf", "rb") as f:
            result = await extract_competition_from_pdf(f.read())
            print(json.dumps(result, indent=2, ensure_ascii=False))
    
    asyncio.run(test())
```

### 3.3 Endpoints da API

**Arquivo**: `Hb Track - Backend/app/api/v1/endpoints/competitions.py`

Adicionar/atualizar os endpoints:

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from app.services.gemini_competition_service import extract_competition_from_pdf
from app.schemas.competition import (
    CompetitionCreate, 
    CompetitionResponse,
    CompetitionImportResponse
)

router = APIRouter(prefix="/competitions", tags=["competitions"])

# ============================================================================
# ENDPOINT: Importar PDF com IA
# ============================================================================

@router.post("/import-pdf", response_model=CompetitionImportResponse)
async def import_competition_from_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Processa um PDF de competição usando IA (Gemini) e retorna dados estruturados
    para pré-preencher o formulário.
    
    O usuário deve revisar os dados antes de salvar definitivamente.
    """
    # Validação do arquivo
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400, 
            detail="Apenas arquivos PDF são aceitos"
        )
    
    # Limite de tamanho (10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="Arquivo muito grande. Máximo: 10MB"
        )
    
    # Processa com Gemini
    result = await extract_competition_from_pdf(content, file.filename)
    
    if not result["success"]:
        raise HTTPException(
            status_code=422,
            detail=result.get("error", "Erro ao processar PDF")
        )
    
    return result


# ============================================================================
# ENDPOINT: Criar competição completa (após validação do usuário)
# ============================================================================

@router.post("/", response_model=CompetitionResponse)
async def create_competition(
    data: CompetitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cria uma competição completa com:
    - Dados básicos
    - Equipes adversárias
    - Fases
    - Jogos
    
    Este endpoint é chamado APÓS o usuário validar os dados extraídos pela IA.
    """
    async with db.begin():
        # 1. Cria a competição
        competition = Competition(
            team_id=current_user.team_id,
            name=data.name,
            season=data.season,
            organization=data.organization,
            modality=data.modality,
            competition_type=data.competition_type,
            tiebreaker_criteria=data.tiebreaker_criteria,
            format_details=data.format_details,
            status="draft",
            created_by=current_user.id
        )
        db.add(competition)
        await db.flush()  # Para obter o ID
        
        # 2. Cria as equipes adversárias
        team_map = {}  # nome -> id (para vincular aos jogos)
        for team_data in data.teams:
            opponent = CompetitionOpponentTeam(
                competition_id=competition.id,
                name=team_data.name,
                short_name=team_data.short_name,
                group_name=team_data.group,
                category=team_data.category
            )
            db.add(opponent)
            await db.flush()
            team_map[team_data.name] = opponent.id
        
        # 3. Cria as fases
        phase_map = {}  # nome -> id
        for phase_data in data.phases:
            phase = CompetitionPhase(
                competition_id=competition.id,
                name=phase_data.name,
                phase_type=phase_data.type,
                order_index=phase_data.order
            )
            db.add(phase)
            await db.flush()
            phase_map[phase_data.name] = phase.id
        
        # Define fase atual como a primeira
        if data.phases:
            competition.current_phase_id = phase_map[data.phases[0].name]
        
        # 4. Cria os jogos
        for match_data in data.matches:
            # Encontra IDs das equipes
            home_team_id = team_map.get(match_data.home_team)
            away_team_id = team_map.get(match_data.away_team)
            
            # Encontra ID da fase (se especificada)
            phase_id = None
            if match_data.phase_name:
                phase_id = phase_map.get(match_data.phase_name)
            elif data.phases:
                phase_id = phase_map[data.phases[0].name]
            
            match = CompetitionMatch(
                competition_id=competition.id,
                phase_id=phase_id,
                home_team_id=home_team_id,
                away_team_id=away_team_id,
                match_date=match_data.date,
                match_time=match_data.time,
                round_number=match_data.round_number,
                round_name=match_data.round_name,
                location=match_data.location,
                status="scheduled"
            )
            db.add(match)
        
        await db.commit()
        await db.refresh(competition)
        
        return competition
```

### 3.4 Schemas Pydantic

**Arquivo**: `Hb Track - Backend/app/schemas/competition.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time
from uuid import UUID

# ============================================================================
# SCHEMAS DE ENTRADA (Request)
# ============================================================================

class TeamCreate(BaseModel):
    name: str
    short_name: Optional[str] = None
    group: Optional[str] = None
    category: Optional[str] = None

class PhaseCreate(BaseModel):
    name: str
    type: str  # group, knockout, round_robin
    order: int

class MatchCreate(BaseModel):
    home_team: str
    away_team: str
    date: Optional[date] = None
    time: Optional[time] = None
    round_number: Optional[int] = None
    round_name: Optional[str] = None
    phase_name: Optional[str] = None
    location: Optional[str] = None

class CompetitionCreate(BaseModel):
    """Schema para criar competição completa"""
    name: str
    season: str
    organization: Optional[str] = None
    modality: str = "masculino"
    competition_type: str
    tiebreaker_criteria: List[str] = ["pontos", "saldo_gols", "gols_pro", "confronto_direto"]
    format_details: Optional[dict] = {}
    
    teams: List[TeamCreate] = []
    phases: List[PhaseCreate] = []
    matches: List[MatchCreate] = []
    
    regulation_notes: Optional[str] = None

# ============================================================================
# SCHEMAS DE SAÍDA (Response)
# ============================================================================

class ExtractionStats(BaseModel):
    teams_count: int
    matches_count: int
    phases_count: int
    matches_with_date: int
    matches_with_time: int

class ConfidenceScores(BaseModel):
    """Scores de confiança por campo (0.0 a 1.0)"""
    name: float = 0.0
    season: float = 0.0
    organization: float = 0.0
    competition_type: float = 0.0
    teams: float = 0.0
    matches: float = 0.0
    tiebreaker_criteria: float = 0.0

class CompetitionImportData(BaseModel):
    name: str
    season: Optional[str]
    organization: Optional[str]
    modality: Optional[str]
    competition_type: str
    points_per_win: int = 2  # Padrão handebol
    tiebreaker_criteria: List[str]
    teams: List[dict]
    phases: List[dict]
    matches: List[dict]
    regulation_summary: Optional[str]
    warnings: List[str]
    extraction_stats: ExtractionStats
    confidence_scores: ConfidenceScores  # NOVO: scores de confiança
    fields_to_review: List[str] = []     # NOVO: campos com score < 0.8

class CompetitionImportResponse(BaseModel):
    """Resposta do endpoint de importação PDF"""
    success: bool
    data: Optional[CompetitionImportData] = None
    message: Optional[str] = None
    error: Optional[str] = None

class CompetitionResponse(BaseModel):
    """Resposta após criar competição"""
    id: UUID
    name: str
    season: str
    competition_type: str
    status: str
    teams_count: int
    matches_count: int
    
    class Config:
        from_attributes = True
```

---

## 4. FRONTEND - COMPONENTES E FLUXO UX

### 4.1 Estrutura de Arquivos

```
src/
├── components/
│   └── competitions/
│       ├── import/
│       │   ├── PDFUploadModal.tsx       # Modal de upload
│       │   ├── ImportProgressBar.tsx    # Progresso do processamento
│       │   ├── AIReviewForm.tsx         # Form com dados da IA
│       │   └── FieldStatusBadge.tsx     # Badge 🟢🔶🔴
│       ├── form/
│       │   ├── CompetitionForm.tsx      # Form principal
│       │   ├── GeneralInfoSection.tsx   # Seção info básica
│       │   ├── TeamsSection.tsx         # Seção equipes
│       │   ├── PhasesSection.tsx        # Seção fases
│       │   ├── MatchesSection.tsx       # Seção jogos
│       │   └── SummarySection.tsx       # Resumo final
│       └── ...
├── lib/
│   └── api/
│       └── competitions.ts              # API service (já existe)
└── hooks/
    └── useCompetitionImport.ts          # Hook para importação
```

### 4.2 Hook de Importação

**Arquivo**: `src/hooks/useCompetitionImport.ts`

```typescript
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { competitionsApi } from '@/lib/api/competitions';
import { toast } from 'sonner';

export interface ImportedData {
  name: string;
  season: string | null;
  organization: string | null;
  modality: string | null;
  competition_type: string;
  tiebreaker_criteria: string[];
  teams: Array<{
    name: string;
    short_name?: string;
    group?: string;
    category?: string;
  }>;
  phases: Array<{
    name: string;
    type: string;
    order: number;
  }>;
  matches: Array<{
    home_team: string;
    away_team: string;
    date?: string;
    time?: string;
    round_number?: number;
    round_name?: string;
    location?: string;
  }>;
  warnings: string[];
  extraction_stats: {
    teams_count: number;
    matches_count: number;
    phases_count: number;
    matches_with_date: number;
    matches_with_time: number;
  };
}

export interface FieldStatus {
  status: 'detected' | 'review' | 'missing';
  value: any;
}

export function useCompetitionImport() {
  const [importedData, setImportedData] = useState<ImportedData | null>(null);
  const [fieldStatuses, setFieldStatuses] = useState<Record<string, FieldStatus>>({});

  const importMutation = useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      return competitionsApi.importPDF(formData);
    },
    onSuccess: (response) => {
      if (response.success && response.data) {
        setImportedData(response.data);
        calculateFieldStatuses(response.data);
        toast.success('PDF processado com sucesso!', {
          description: `${response.data.extraction_stats.teams_count} equipes e ${response.data.extraction_stats.matches_count} jogos encontrados`
        });
      }
    },
    onError: (error: any) => {
      toast.error('Erro ao processar PDF', {
        description: error.message || 'Tente novamente com outro arquivo'
      });
    }
  });

  const calculateFieldStatuses = (data: ImportedData) => {
    const statuses: Record<string, FieldStatus> = {};
    
    // USA CONFIDENCE_SCORES DA IA PARA DEFINIR STATUS
    const scores = data.confidence_scores || {};

    // Campos obrigatórios - usa score da IA
    statuses['name'] = {
      status: (scores.name || 0) >= 0.8 ? 'detected' : 
              (scores.name || 0) >= 0.5 ? 'review' : 'missing',
      value: data.name
    };

    statuses['competition_type'] = {
      status: (scores.competition_type || 0) >= 0.8 ? 'detected' : 
              (scores.competition_type || 0) >= 0.5 ? 'review' : 'missing',
      value: data.competition_type
    };

    // Campos opcionais - revisão se score < 0.8
    statuses['season'] = {
      status: (scores.season || 0) >= 0.8 ? 'detected' : 'review',
      value: data.season
    };

    statuses['organization'] = {
      status: (scores.organization || 0) >= 0.8 ? 'detected' : 'review',
      value: data.organization
    };

    // Equipes - usa score da IA
    statuses['teams'] = {
      status: (scores.teams || 0) >= 0.8 ? 'detected' : 
              data.teams.length > 0 ? 'review' : 'missing',
      value: data.teams
    };

    // Jogos - usa score da IA
    statuses['matches'] = {
      status: (scores.matches || 0) >= 0.8 ? 'detected' : 
              data.matches.length > 0 ? 'review' : 'missing',
      value: data.matches
    };

    setFieldStatuses(statuses);
  };

  const updateField = (field: string, value: any) => {
    if (!importedData) return;

    setImportedData(prev => prev ? { ...prev, [field]: value } : null);
    setFieldStatuses(prev => ({
      ...prev,
      [field]: { ...prev[field], status: 'detected', value }
    }));
  };

  const clearImport = () => {
    setImportedData(null);
    setFieldStatuses({});
  };

  return {
    importedData,
    fieldStatuses,
    isLoading: importMutation.isPending,
    error: importMutation.error,
    importPDF: importMutation.mutate,
    updateField,
    clearImport,
    hasWarnings: importedData?.warnings && importedData.warnings.length > 0,
    warnings: importedData?.warnings || []
  };
}
```

### 4.3 Fuzzy Search para Vinculação de Equipes

Para garantir **mínimo de digitação**, quando a IA retornar a lista de equipes, fazemos **busca aproximada** no banco de dados de equipes existentes.

**Arquivo**: `src/hooks/useTeamFuzzyMatch.ts`

```typescript
import { useMutation, useQuery } from '@tanstack/react-query';
import { teamsApi } from '@/lib/api/teams';
import Fuse from 'fuse.js';

interface TeamSuggestion {
  importedName: string;      // Nome da IA: "Handebol Taubaté"
  matchedTeam: {
    id: string;
    name: string;            // Nome no banco: "Taubaté Handebol"
    score: number;           // Similaridade: 0.85
  } | null;
  isNewTeam: boolean;        // true se não encontrou match
}

export function useTeamFuzzyMatch() {
  // Busca todas as equipes existentes no banco
  const { data: existingTeams } = useQuery({
    queryKey: ['teams', 'all'],
    queryFn: () => teamsApi.getAllTeams(),
  });

  // Configura Fuse.js para busca aproximada
  const fuse = new Fuse(existingTeams || [], {
    keys: ['name', 'short_name'],
    threshold: 0.4,  // 0 = match exato, 1 = aceita qualquer coisa
    includeScore: true,
  });

  const findMatches = (importedTeams: string[]): TeamSuggestion[] => {
    return importedTeams.map(importedName => {
      const results = fuse.search(importedName);
      
      if (results.length > 0 && results[0].score && results[0].score < 0.4) {
        return {
          importedName,
          matchedTeam: {
            id: results[0].item.id,
            name: results[0].item.name,
            score: 1 - (results[0].score || 0), // Inverte para % de similaridade
          },
          isNewTeam: false,
        };
      }
      
      return {
        importedName,
        matchedTeam: null,
        isNewTeam: true,
      };
    });
  };

  return { findMatches };
}
```

**Componente**: `src/components/competitions/form/TeamsSection.tsx`

```tsx
import { useTeamFuzzyMatch } from '@/hooks/useTeamFuzzyMatch';
import { Check, Plus, Link2 } from 'lucide-react';

interface TeamsSectionProps {
  importedTeams: Array<{ name: string; group?: string }>;
  onTeamLink: (importedName: string, existingTeamId: string) => void;
  onTeamCreate: (name: string) => void;
}

export function TeamsSection({ importedTeams, onTeamLink, onTeamCreate }: TeamsSectionProps) {
  const { findMatches } = useTeamFuzzyMatch();
  const suggestions = findMatches(importedTeams.map(t => t.name));

  return (
    <div className="space-y-3">
      <h3 className="font-semibold">Equipes Identificadas</h3>
      
      {suggestions.map((suggestion, idx) => (
        <div key={idx} className="flex items-center gap-3 p-3 border rounded-lg">
          {/* Nome da IA */}
          <span className="flex-1">{suggestion.importedName}</span>
          
          {suggestion.matchedTeam ? (
            // Encontrou match - mostrar botão de vincular
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                ≈ {suggestion.matchedTeam.name} 
                ({Math.round(suggestion.matchedTeam.score * 100)}%)
              </span>
              <button
                onClick={() => onTeamLink(suggestion.importedName, suggestion.matchedTeam!.id)}
                className="btn btn-sm btn-primary"
              >
                <Link2 className="w-4 h-4 mr-1" />
                Vincular
              </button>
            </div>
          ) : (
            // Não encontrou - mostrar botão de criar
            <button
              onClick={() => onTeamCreate(suggestion.importedName)}
              className="btn btn-sm btn-outline"
            >
              <Plus className="w-4 h-4 mr-1" />
              Criar Nova
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
```

**Instalar dependência**:
```bash
npm install fuse.js
```

> 💡 **UX Inteligente**: Se a IA retornar "Handebol Taubaté" e no banco existir "Taubaté Handebol", 
> o usuário só clica em **"Vincular"** em vez de digitar tudo novamente!

### 4.4 API Service Atualizado

**Adicionar em**: `src/lib/api/competitions.ts`

```typescript
// Adicionar ao arquivo existente

export const competitionsApi = {
  // ... métodos existentes ...

  /**
   * Importa PDF e extrai dados com IA
   */
  importPDF: async (formData: FormData): Promise<CompetitionImportResponse> => {
    const response = await api.post('/competitions/import-pdf', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  /**
   * Cria competição completa (após validação do usuário)
   */
  createComplete: async (data: CompetitionCreateRequest): Promise<Competition> => {
    const response = await api.post('/competitions', data);
    return response.data;
  },
};

// Types
export interface CompetitionImportResponse {
  success: boolean;
  data?: ImportedCompetitionData;
  message?: string;
  error?: string;
}

export interface ImportedCompetitionData {
  name: string;
  season: string | null;
  organization: string | null;
  modality: string | null;
  competition_type: string;
  tiebreaker_criteria: string[];
  teams: ImportedTeam[];
  phases: ImportedPhase[];
  matches: ImportedMatch[];
  warnings: string[];
  extraction_stats: ExtractionStats;
}

export interface ImportedTeam {
  name: string;
  short_name?: string;
  group?: string;
  category?: string;
}

export interface ImportedPhase {
  name: string;
  type: string;
  order: number;
}

export interface ImportedMatch {
  external_id?: string;  // NOVO: ID único para upsert
  home_team: string;
  away_team: string;
  date?: string;
  time?: string;
  round_number?: number;
  round_name?: string;
  location?: string;
}

export interface ExtractionStats {
  teams_count: number;
  matches_count: number;
  phases_count: number;
  matches_with_date: number;
  matches_with_time: number;
}

export interface CompetitionCreateRequest {
  name: string;
  season: string;
  organization?: string;
  modality: string;
  competition_type: string;
  tiebreaker_criteria: string[];
  format_details?: Record<string, any>;
  teams: ImportedTeam[];
  phases: ImportedPhase[];
  matches: ImportedMatch[];
  regulation_notes?: string;
}
```

---

## 5. ESTRUTURA JSON DA IA

### 5.1 Resposta Completa do Gemini

```json
{
  "name": "Copa Estadual de Handebol Sub-18 Masculino",
  "season": "2026",
  "organization": "Federação Paulista de Handebol",
  "modality": "masculino",
  "competition_type": "grupos_mata_mata",
  "tiebreaker_criteria": [
    "pontos",
    "saldo_gols",
    "confronto_direto",
    "gols_pro",
    "sorteio"
  ],
  "teams": [
    { "name": "EC Pinheiros", "short_name": "PIN", "group": "A", "category": "Sub-18" },
    { "name": "Metodista", "short_name": "MET", "group": "A", "category": "Sub-18" },
    { "name": "AABB São Paulo", "short_name": "AABB", "group": "A", "category": "Sub-18" },
    { "name": "Hebraica", "short_name": "HEB", "group": "A", "category": "Sub-18" },
    { "name": "Objetivo", "short_name": "OBJ", "group": "B", "category": "Sub-18" },
    { "name": "Guarulhos HC", "short_name": "GUA", "group": "B", "category": "Sub-18" },
    { "name": "Santo André", "short_name": "SAN", "group": "B", "category": "Sub-18" },
    { "name": "Taubaté", "short_name": "TAU", "group": "B", "category": "Sub-18" }
  ],
  "phases": [
    { "name": "Fase de Grupos", "type": "group", "order": 1 },
    { "name": "Semifinais", "type": "knockout", "order": 2 },
    { "name": "Disputa 3º Lugar", "type": "third_place", "order": 3 },
    { "name": "Final", "type": "final", "order": 4 }
  ],
  "matches": [
    {
      "round_number": 1,
      "round_name": "1ª Rodada - Grupo A",
      "home_team": "EC Pinheiros",
      "away_team": "Metodista",
      "date": "2026-03-15",
      "time": "14:00",
      "location": null
    },
    {
      "round_number": 1,
      "round_name": "1ª Rodada - Grupo A",
      "home_team": "AABB São Paulo",
      "away_team": "Hebraica",
      "date": "2026-03-15",
      "time": "16:00",
      "location": null
    },
    {
      "round_number": 1,
      "round_name": "1ª Rodada - Grupo B",
      "home_team": "Objetivo",
      "away_team": "Guarulhos HC",
      "date": "2026-03-16",
      "time": "10:00",
      "location": null
    }
  ],
  "regulation_summary": "Competição dividida em 2 grupos de 4 equipes. Os 2 primeiros de cada grupo avançam para as semifinais. Jogos em turno único dentro dos grupos.",
  "warnings": [
    "Local dos jogos não especificado no documento",
    "Horário de 2 jogos não identificado"
  ],
  "extraction_stats": {
    "teams_count": 8,
    "matches_count": 14,
    "phases_count": 4,
    "matches_with_date": 14,
    "matches_with_time": 12
  }
}
```

---

## 6. FORMAS DE DISPUTA SUPORTADAS

### 6.1 Tipos de Competição

| Tipo | Código | Descrição | Estrutura |
|------|--------|-----------|-----------|
| Turno Único | `turno_unico` | Todos contra todos, 1 jogo | N equipes → N*(N-1)/2 jogos |
| Turno e Returno | `turno_returno` | Todos contra todos, ida e volta | N equipes → N*(N-1) jogos |
| Fase de Grupos | `grupos` | Divisão em grupos | X grupos × Y equipes |
| Grupos + Mata-mata | `grupos_mata_mata` | Grupos → Eliminatórias | Mais comum em campeonatos |
| Mata-mata | `mata_mata` | Eliminação direta | 2^n equipes (8, 16, 32...) |
| Triangular | `triangular` | 3 equipes | 3 jogos |
| Quadrangular | `quadrangular` | 4 equipes | 6 jogos |
| Custom | `custom` | Formato especial | Configuração manual |

### 6.2 Pontuação no Handebol

| Sistema | Vitória | Empate | Derrota | Uso |
|---------|---------|--------|---------|-----|
| **Padrão Handebol** | 2 | 1 | 0 | Maioria das competições |
| Alternativo | 3 | 1 | 0 | Algumas ligas específicas |

> ⚠️ O campo `points_per_win` no JSON da IA indica qual sistema usar.

### 6.3 Critérios de Desempate

| Critério | Código | Descrição |
|----------|--------|-----------|
| Pontos | `pontos` | Maior número de pontos |
| Saldo de Gols | `saldo_gols` | GP - GC |
| Gols Pró | `gols_pro` | Mais gols marcados |
| Confronto Direto | `confronto_direto` | Resultado entre empatados |
| Gols Contra | `gols_contra` | Menos gols sofridos |
| Cartões | `cartoes` | Menos punições |
| Sorteio | `sorteio` | Último recurso |

### 6.4 Format Details (JSON)

```json
{
  "turno_unico": {
    "rounds": 1,
    "points_per_win": 2
  },
  "turno_returno": {
    "rounds": 2,
    "points_per_win": 2
  },
  "grupos": {
    "num_groups": 2,
    "teams_per_group": 4,
    "points_per_win": 2
  },
  "grupos_mata_mata": {
    "num_groups": 2,
    "teams_per_group": 4,
    "qualified_per_group": 2,
    "knockout_rounds": ["semifinal", "final"],
    "is_olympic_cross": true,
    "points_per_win": 2
  },
  "mata_mata": {
    "rounds": ["oitavas", "quartas", "semifinal", "final"],
    "has_third_place": true
  }
}
```

---

## 7. UPSERT DE JOGOS (Atualização sem Duplicação)

### 7.1 O Problema
Se o usuário subir o **mesmo PDF novamente** para atualizar datas/horários, não queremos duplicar os jogos.

### 7.2 A Solução: `external_reference_id`
A coluna `external_reference_id` na tabela `competition_matches` guarda o ID que a IA deu para o jogo no PDF.

**Exemplo de IDs gerados pela IA:**
- `R1-GA-01` → Rodada 1, Grupo A, Jogo 1
- `SF-01` → Semifinal, Jogo 1
- `FIN-01` → Final

### 7.3 Lógica de Upsert no Backend

```python
async def upsert_matches(competition_id: UUID, matches: List[MatchCreate], db: AsyncSession):
    """
    Insere novos jogos ou atualiza existentes baseado no external_reference_id.
    """
    for match_data in matches:
        external_id = match_data.external_id
        
        if external_id:
            # Tenta encontrar jogo existente
            existing = await db.execute(
                select(CompetitionMatch).where(
                    CompetitionMatch.competition_id == competition_id,
                    CompetitionMatch.external_reference_id == external_id
                )
            )
            existing_match = existing.scalar_one_or_none()
            
            if existing_match:
                # ATUALIZA o jogo existente
                existing_match.match_date = match_data.date
                existing_match.match_time = match_data.time
                existing_match.location = match_data.location
                existing_match.round_name = match_data.round_name
                continue
        
        # INSERE novo jogo
        new_match = CompetitionMatch(
            competition_id=competition_id,
            external_reference_id=external_id,
            match_date=match_data.date,
            match_time=match_data.time,
            location=match_data.location,
            # ... outros campos
        )
        db.add(new_match)
    
    await db.commit()
```

### 7.4 Fluxo de Reimportação

```
┌─────────────────────────────────────────────────────────────────┐
│  Usuário sobe PDF atualizado (mesma competição)                 │
├─────────────────────────────────────────────────────────────────┤
│  1. Gemini extrai jogos com external_id                         │
│  2. Backend compara external_id com banco                       │
│  3. Se existe: ATUALIZA (data, hora, local)                     │
│  4. Se não existe: INSERE novo jogo                             │
│  5. Toast: "3 jogos atualizados, 2 novos adicionados"           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. CHECKLIST DE IMPLEMENTAÇÃO

### ✅ Fase 1: Banco de Dados
- [ ] Criar arquivo de migration `add_competitions_tables.sql`
- [ ] Incluir coluna `external_reference_id` em `competition_matches`
- [ ] Executar migration no NeonDB
- [ ] Testar criação das tabelas
- [ ] Verificar triggers e funções

### ✅ Fase 2: Backend - Serviço Gemini
- [ ] Instalar `google-generativeai`
- [ ] Criar `gemini_competition_service.py`
- [ ] Configurar API key como variável de ambiente
- [ ] Implementar prompt específico para Handebol
- [ ] Retornar `confidence_scores` e `fields_to_review`
- [ ] Testar extração com PDF de exemplo

### ✅ Fase 3: Backend - Endpoints
- [ ] Endpoint `POST /competitions/import-pdf`
- [ ] Endpoint `POST /competitions` (criar completa)
- [ ] Implementar lógica de **upsert** com `external_reference_id`
- [ ] Schemas Pydantic com `ConfidenceScores`
- [ ] Testes de integração

### ✅ Fase 4: Frontend - Upload e Processamento
- [ ] `PDFUploadModal.tsx` com drag & drop
- [ ] `ImportProgressBar.tsx` com status
- [ ] Hook `useCompetitionImport.ts` com `confidence_scores`
- [ ] Atualizar `competitions.ts` API service

### ✅ Fase 5: Frontend - Formulário com IA
- [ ] `AIReviewForm.tsx` - form pré-preenchido
- [ ] `FieldStatusBadge.tsx` - badges baseados em `confidence < 0.8`
- [ ] `TeamsSection.tsx` com **Fuzzy Search** (fuse.js)
- [ ] `MatchesSection.tsx` - lista de jogos editável
- [ ] `PhasesSection.tsx` - fases editáveis

### ✅ Fase 6: Frontend - Validação e Submit
- [ ] `SummarySection.tsx` - resumo visual
- [ ] Validação de campos obrigatórios
- [ ] Botão "Criar Competição" condicional
- [ ] Toasts de sucesso/erro
- [ ] Redirecionamento após criar

### ✅ Fase 7: Testes e Refinamentos
- [ ] Testar com PDFs reais de federações
- [ ] Testar **reimportação** (upsert de jogos)
- [ ] Testar **vinculação fuzzy** de equipes
- [ ] Ajustar prompt do Gemini conforme necessário
- [ ] Testes de edge cases (PDF vazio, formato errado)
- [ ] Responsividade mobile
- [ ] Performance e loading states

---

## 📌 VARIÁVEIS DE AMBIENTE

```env
# .env (Backend)
GEMINI_API_KEY=AIzaSyCkOXjNkR9DKO527hQ_RWPMKSM8Hmygjus
```

---

## 📦 DEPENDÊNCIAS NECESSÁRIAS

### Backend (Python)
```bash
pip install -U google-generativeai
```

### Frontend (npm)
```bash
npm install fuse.js  # Para fuzzy search de equipes
```

---

## 🚀 COMANDOS PARA INICIAR

```bash
# 1. Backend - Instalar dependência
cd "c:\HB TRACK\Hb Track - Backend"
pip install -U google-generativeai

# 2. Executar migration
python -c "from app.db.database import run_migrations; run_migrations()"

# 3. Iniciar backend
python -m uvicorn app.main:app --reload

# 4. Frontend - Instalar fuse.js
cd "c:\HB TRACK\Hb Track - Fronted"
npm install fuse.js

# 5. Iniciar frontend
npm run dev
```

---

## 📋 RESUMO DOS COMPLEMENTOS ADICIONADOS

| # | Complemento | Descrição |
|---|-------------|-----------|
| 1 | **Prompt Handebol** | Regras específicas: pontuação diferenciada, cruzamento olímpico, tipos de disputa |
| 2 | **Confidence Scores** | Resposta do backend inclui `confidence_scores` e `fields_to_review` |
| 3 | **Gemini como Parser** | Sem OCR - Gemini 1.5 lê PDF diretamente via visão computacional |
| 4 | **Fuzzy Search** | Busca aproximada para vincular equipes existentes (fuse.js) |
| 5 | **external_reference_id** | Coluna para upsert de jogos sem duplicação ao reimportar PDF |

---

**Próximo passo**: Deseja que eu comece a implementação pela **Migration do banco** ou pelo **Serviço Gemini no backend**?
