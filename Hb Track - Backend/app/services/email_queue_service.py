"""
Serviço de fila de emails com retry automático

Responsabilidades:
- Enfileirar emails para envio assíncrono
- Processar fila de emails pendentes
- Retry automático com backoff exponencial
- Tracking de status e erros

Benefícios:
- Cadastro não bloqueia se provedor de email estiver lento
- Retry automático (3 tentativas: 1min, 5min, 15min)
- Dashboard de emails falhos
- Performance melhorada
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select

from app.models.email_queue import EmailQueue
from app.services.intake.email_service_v2 import email_service_v2

logger = logging.getLogger(__name__)


async def enqueue_email(
    db: AsyncSession,
    template_type: str,
    to_email: str,
    template_data: Dict[str, Any],
    created_by_user_id: Optional[UUID] = None,
    max_attempts: int = 3
) -> EmailQueue:
    """
    Enfileira email para envio assíncrono.
    
    Args:
        db: Sessão do banco
        template_type: Tipo do template ('invite', 'welcome', 'reset_password')
        to_email: Email do destinatário
        template_data: Dados dinâmicos do template
        created_by_user_id: ID do usuário que criou
        max_attempts: Máximo de tentativas (default: 3)
    
    Returns:
        EmailQueue: Registro criado
    
    Usage:
        email_job = enqueue_email(
            db=db,
            template_type='invite',
            to_email='joao@email.com',
            template_data={
                'person_name': 'João Silva',
                'organization_name': 'Clube ABC',
                'role_name': 'Treinador',
                'activation_link': 'https://...',
                'cta_text': 'Criar senha',
                'cta_link': 'https://...',
                'app_name': 'HB Track'
            },
            created_by_user_id=ctx.user_id
        )
    """
    
    # Criar registro na fila
    email_job = EmailQueue(
        template_type=template_type,
        to_email=to_email,
        template_data=template_data,
        status='pending',
        attempts=0,
        max_attempts=max_attempts,
        next_retry_at=datetime.now(timezone.utc),  # Enviar imediatamente
        created_by_user_id=created_by_user_id
    )
    
    db.add(email_job)
    await db.commit()
    await db.refresh(email_job)
    
    logger.info(
        f"Email enqueued | id={email_job.id} | type={template_type} | "
        f"to={to_email} | max_attempts={max_attempts}"
    )
    
    return email_job


async def process_pending_emails(db: AsyncSession, batch_size: int = 10) -> Dict[str, int]:
    """
    Processa emails pendentes da fila.
    
    Args:
        db: Sessão do banco
        batch_size: Número de emails a processar (default: 10)
    
    Returns:
        Dict com estatísticas: {'sent': 2, 'failed': 1, 'retried': 1}
    
    Usage (cronjob a cada 1 minuto):
        from app.services.email_queue_service import process_pending_emails
        from app.db.session import SessionLocal
        
        db = SessionLocal()
        try:
            stats = process_pending_emails(db, batch_size=50)
            print(f"Processed: {stats}")
        finally:
            db.close()
    """
    
    stats = {'sent': 0, 'failed': 0, 'retried': 0, 'skipped': 0}
    
    # Buscar emails pendentes prontos para envio
    now = datetime.now(timezone.utc)
    stmt = select(EmailQueue).where(
        and_(
            EmailQueue.status == 'pending',
            EmailQueue.next_retry_at <= now,
            EmailQueue.attempts < EmailQueue.max_attempts
        )
    ).limit(batch_size)
    result = await db.execute(stmt)
    pending_emails = result.scalars().all()
    
    if not pending_emails:
        logger.debug("No pending emails to process")
        return stats
    
    logger.info(f"Processing {len(pending_emails)} pending emails")
    
    for email_job in pending_emails:
        try:
            # Tentar enviar
            success = _send_email(email_job)
            
            # Incrementar tentativas
            email_job.attempts += 1
            
            if success:
                # Sucesso: marcar como enviado
                email_job.status = 'sent'
                email_job.sent_at = datetime.now(timezone.utc)
                email_job.last_error = None
                stats['sent'] += 1
                
                logger.info(
                    f"Email sent successfully | id={email_job.id} | "
                    f"to={email_job.to_email} | attempts={email_job.attempts}"
                )
            else:
                # Falhou: verificar se ainda tem tentativas
                if email_job.attempts >= email_job.max_attempts:
                    # Esgotou tentativas: marcar como failed
                    email_job.status = 'failed'
                    stats['failed'] += 1
                    
                    logger.error(
                        f"Email failed permanently | id={email_job.id} | "
                        f"to={email_job.to_email} | attempts={email_job.attempts} | "
                        f"error={email_job.last_error}"
                    )
                else:
                    # Ainda tem tentativas: agendar retry com backoff
                    retry_delay = _calculate_retry_delay(email_job.attempts)
                    email_job.next_retry_at = datetime.now(timezone.utc) + retry_delay
                    stats['retried'] += 1
                    
                    logger.warning(
                        f"Email retry scheduled | id={email_job.id} | "
                        f"to={email_job.to_email} | attempts={email_job.attempts} | "
                        f"next_retry_in={retry_delay.total_seconds()}s"
                    )
            
            await db.commit()
            
        except Exception as e:
            logger.exception(f"Error processing email {email_job.id}: {str(e)}")
            email_job.last_error = str(e)[:1000]  # Truncar erro
            await db.commit()


def _send_email(email_job: EmailQueue) -> bool:
    """
    Envia email usando EmailServiceV2.
    
    Args:
        email_job: Registro da fila
    
    Returns:
        True se enviado com sucesso
    """
    try:
        template_data = email_job.template_data
        
        if email_job.template_type == 'invite':
            success = email_service_v2.send_invite_email(
                to_email=email_job.to_email,
                person_name=template_data['person_name'],
                token=template_data['token'],
                app_url=template_data['app_url'],
                organization_name=template_data.get('organization_name'),
                role_name=template_data.get('role_name')
            )
        elif email_job.template_type == 'welcome':
            success = email_service_v2.send_welcome_email(
                to_email=email_job.to_email,
                person_name=template_data['person_name'],
                organization_name=template_data.get('organization_name')
            )
        else:
            logger.error(f"Unknown template type: {email_job.template_type}")
            email_job.last_error = f"Template type não suportado: {email_job.template_type}"
            return False
        
        return success
        
    except Exception as e:
        logger.exception(f"Error sending email {email_job.id}: {str(e)}")
        email_job.last_error = str(e)[:1000]
        return False


def _calculate_retry_delay(attempt: int) -> timedelta:
    """
    Calcula delay para próxima tentativa com backoff exponencial.
    
    Estratégia:
    - Tentativa 1: 1 minuto
    - Tentativa 2: 5 minutos
    - Tentativa 3: 15 minutos
    
    Args:
        attempt: Número da tentativa (1, 2, 3)
    
    Returns:
        timedelta com delay
    """
    delays = {
        1: timedelta(minutes=1),
        2: timedelta(minutes=5),
        3: timedelta(minutes=15),
    }
    return delays.get(attempt, timedelta(minutes=1))


async def cancel_email(db: AsyncSession, email_id: UUID) -> bool:
    """
    Cancela email pendente.
    
    Args:
        db: Sessão do banco
        email_id: ID do email
    
    Returns:
        True se cancelado
    """
    stmt = select(EmailQueue).where(EmailQueue.id == email_id)
    result = await db.execute(stmt)
    email_job = result.scalar_one_or_none()
    
    if not email_job:
        return False
    
    if email_job.status != 'pending':
        logger.warning(f"Cannot cancel email {email_id} with status {email_job.status}")
        return False
    
    email_job.status = 'cancelled'
    await db.commit()
    
    logger.info(f"Email cancelled | id={email_id} | to={email_job.to_email}")
    return True


async def get_failed_emails(db: AsyncSession, limit: int = 100) -> list[EmailQueue]:
    """
    Retorna emails que falharam permanentemente.
    
    Útil para dashboard de monitoramento.
    
    Args:
        db: Sessão do banco
        limit: Máximo de registros
    
    Returns:
        Lista de EmailQueue com status='failed'
    """
    stmt = select(EmailQueue).where(
        EmailQueue.status == 'failed'
    ).order_by(
        EmailQueue.updated_at.desc()
    ).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
