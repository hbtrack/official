"""Create training triggers for internal_load, audit, and cache invalidation

Revision ID: 0035_training_triggers
Revises: 24e84ef16638
Create Date: 2026-01-16

Step 2: Implementar triggers no banco de dados em ordem crítica:
1. tr_calculate_internal_load (wellness_post BEFORE INSERT/UPDATE)
2. tr_audit_session_status (training_sessions AFTER UPDATE)
3. tr_invalidate_analytics_cache (training_sessions AFTER INSERT/UPDATE/DELETE)
4. tr_update_wellness_response_timestamp (wellness_pre/post AFTER INSERT)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0035'
down_revision = '0034'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria triggers em ordem específica conforme _PLANO_TRAINING.md Step 2:
    
    1º trigger: Calcular internal_load automaticamente
    2º trigger: Auditar mudanças de status
    3º trigger: Invalidar cache de analytics
    4º trigger: Atualizar timestamp de resposta wellness
    """
    
    # =========================================================================
    # 1º TRIGGER: Calculate Internal Load (wellness_post BEFORE INSERT/UPDATE)
    # =========================================================================
    # Formula: internal_load = minutes_effective × session_rpe
    # Executado BEFORE para garantir que o valor esteja disponível no INSERT
    
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_calculate_internal_load()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Calcular internal_load: minutes_effective × session_rpe
            -- COALESCE garante 0 se algum valor for NULL
            NEW.internal_load := COALESCE(NEW.minutes_effective, 0) * COALESCE(NEW.session_rpe, 0);
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER tr_calculate_internal_load
        BEFORE INSERT OR UPDATE ON wellness_post
        FOR EACH ROW
        EXECUTE FUNCTION fn_calculate_internal_load();
    """)
    
    op.execute("""
        COMMENT ON FUNCTION fn_calculate_internal_load() IS 
        'Step 2: Calcula internal_load automaticamente como minutes_effective × session_rpe';
    """)
    
    # =========================================================================
    # 2º TRIGGER: Audit Session Status Changes (training_sessions AFTER UPDATE)
    # =========================================================================
    # Registra mudanças de status em audit_logs com metadata JSON
    # Executado AFTER para garantir que o registro já foi atualizado
    
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_audit_session_status()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Apenas auditar se o status mudou
            IF OLD.status IS DISTINCT FROM NEW.status THEN
                INSERT INTO audit_logs (
                    organization_id,
                    user_id,
                    entity_type,
                    entity_id,
                    action,
                    changes,
                    metadata,
                    created_at
                ) VALUES (
                    NEW.organization_id,
                    NEW.updated_by_user_id,  -- Assumindo que existe campo updated_by_user_id
                    'training_session',
                    NEW.id,
                    'status_change',
                    jsonb_build_object(
                        'old_status', OLD.status,
                        'new_status', NEW.status
                    ),
                    jsonb_build_object(
                        'session_at', NEW.session_at,
                        'session_type', NEW.session_type,
                        'team_id', NEW.team_id
                    ),
                    NOW()
                );
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER tr_audit_session_status
        AFTER UPDATE ON training_sessions
        FOR EACH ROW
        WHEN (OLD.status IS DISTINCT FROM NEW.status)
        EXECUTE FUNCTION fn_audit_session_status();
    """)
    
    op.execute("""
        COMMENT ON FUNCTION fn_audit_session_status() IS 
        'Step 2: Registra mudanças de status de sessões de treino em audit_logs';
    """)
    
    # =========================================================================
    # 3º TRIGGER: Invalidate Analytics Cache (training_sessions AFTER INSERT/UPDATE/DELETE)
    # =========================================================================
    # Marca cache_dirty = true em training_analytics_cache para:
    # - Weekly: microcycle_id específico
    # - Monthly: mês (YYYY-MM) da sessão
    # Executado AFTER para garantir consistência dos dados
    
    # Nota: training_analytics_cache será criada no Step 3 (infraestrutura)
    # Este trigger funcionará quando a tabela existir
    
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_invalidate_analytics_cache()
        RETURNS TRIGGER AS $$
        DECLARE
            v_session_month DATE;
            v_microcycle_id UUID;
        BEGIN
            -- Determinar valores OLD ou NEW dependendo da operação
            IF TG_OP = 'DELETE' THEN
                v_session_month := DATE_TRUNC('month', OLD.session_at);
                v_microcycle_id := OLD.microcycle_id;
            ELSE
                v_session_month := DATE_TRUNC('month', NEW.session_at);
                v_microcycle_id := NEW.microcycle_id;
            END IF;
            
            -- Invalidar cache weekly (se microcycle_id existir)
            IF v_microcycle_id IS NOT NULL THEN
                UPDATE training_analytics_cache
                SET cache_dirty = TRUE,
                    calculated_at = NULL
                WHERE microcycle_id = v_microcycle_id
                  AND granularity = 'weekly';
            END IF;
            
            -- Invalidar cache monthly
            UPDATE training_analytics_cache
            SET cache_dirty = TRUE,
                calculated_at = NULL
            WHERE month = v_session_month
              AND granularity = 'monthly';
            
            -- Retornar registro apropriado
            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            ELSE
                RETURN NEW;
            END IF;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    op.execute("""
        CREATE TRIGGER tr_invalidate_analytics_cache
        AFTER INSERT OR UPDATE OR DELETE ON training_sessions
        FOR EACH ROW
        EXECUTE FUNCTION fn_invalidate_analytics_cache();
    """)
    
    op.execute("""
        COMMENT ON FUNCTION fn_invalidate_analytics_cache() IS 
        'Step 2: Invalida cache de analytics ao modificar sessões de treino (weekly/monthly)';
    """)
    
    # =========================================================================
    # 4º TRIGGER: Update Wellness Response Timestamp (wellness_pre/post AFTER INSERT)
    # =========================================================================
    # Atualiza wellness_reminders.responded_at quando atleta responde wellness
    # Executado AFTER INSERT para garantir que o wellness foi criado
    
    # Nota: wellness_reminders será criada no Step 3 (infraestrutura)
    # Este trigger funcionará quando a tabela existir
    
    op.execute("""
        CREATE OR REPLACE FUNCTION fn_update_wellness_response_timestamp()
        RETURNS TRIGGER AS $$
        BEGIN
            -- Atualizar wellness_reminders quando atleta responder
            UPDATE wellness_reminders
            SET responded_at = NOW()
            WHERE training_session_id = NEW.training_session_id
              AND athlete_id = NEW.athlete_id
              AND responded_at IS NULL;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Trigger para wellness_pre
    op.execute("""
        CREATE TRIGGER tr_update_wellness_pre_response
        AFTER INSERT ON wellness_pre
        FOR EACH ROW
        EXECUTE FUNCTION fn_update_wellness_response_timestamp();
    """)
    
    # Trigger para wellness_post
    op.execute("""
        CREATE TRIGGER tr_update_wellness_post_response
        AFTER INSERT ON wellness_post
        FOR EACH ROW
        EXECUTE FUNCTION fn_update_wellness_response_timestamp();
    """)
    
    op.execute("""
        COMMENT ON FUNCTION fn_update_wellness_response_timestamp() IS 
        'Step 2: Atualiza responded_at em wellness_reminders quando atleta responde wellness';
    """)
    
    # =========================================================================
    # ADICIONAR COLUNA internal_load em wellness_post (se não existir)
    # =========================================================================
    # Necessária para o trigger 1º funcionar
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'wellness_post' 
                AND column_name = 'internal_load'
            ) THEN
                ALTER TABLE wellness_post 
                ADD COLUMN internal_load NUMERIC(10, 2) DEFAULT 0;
                
                COMMENT ON COLUMN wellness_post.internal_load IS 
                'Carga interna calculada automaticamente: minutes_effective × session_rpe';
            END IF;
        END $$;
    """)
    
    # =========================================================================
    # ADICIONAR COLUNA minutes_effective em wellness_post (se não existir)
    # =========================================================================
    # Necessária para cálculo de internal_load
    
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'wellness_post' 
                AND column_name = 'minutes_effective'
            ) THEN
                ALTER TABLE wellness_post 
                ADD COLUMN minutes_effective SMALLINT;
                
                COMMENT ON COLUMN wellness_post.minutes_effective IS 
                'Minutos efetivos de participação do atleta (usado para cálculo de internal_load)';
            END IF;
        END $$;
    """)


def downgrade() -> None:
    """
    Remove triggers e funções na ordem inversa.
    """
    
    # Remover triggers wellness_pre/post
    op.execute("DROP TRIGGER IF EXISTS tr_update_wellness_post_response ON wellness_post;")
    op.execute("DROP TRIGGER IF EXISTS tr_update_wellness_pre_response ON wellness_pre;")
    op.execute("DROP FUNCTION IF EXISTS fn_update_wellness_response_timestamp();")
    
    # Remover trigger cache invalidation
    op.execute("DROP TRIGGER IF EXISTS tr_invalidate_analytics_cache ON training_sessions;")
    op.execute("DROP FUNCTION IF EXISTS fn_invalidate_analytics_cache();")
    
    # Remover trigger audit
    op.execute("DROP TRIGGER IF EXISTS tr_audit_session_status ON training_sessions;")
    op.execute("DROP FUNCTION IF EXISTS fn_audit_session_status();")
    
    # Remover trigger internal_load
    op.execute("DROP TRIGGER IF EXISTS tr_calculate_internal_load ON wellness_post;")
    op.execute("DROP FUNCTION IF EXISTS fn_calculate_internal_load();")
    
    # Remover colunas adicionadas (opcional - apenas se foram criadas por esta migration)
    op.execute("""
        DO $$
        BEGIN
            -- Não remover internal_load e minutes_effective pois podem ter sido
            -- criadas antes ou serem necessárias para outros componentes
            NULL;
        END $$;
    """)
