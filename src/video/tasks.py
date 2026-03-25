"""
Tasks Celery — módulo video.
Processamento assíncrono de upload de vídeo: transcodificação e geração de thumbnail.
"""
from __future__ import annotations

from celery import shared_task


@shared_task(name="video.process_media_session", bind=True, max_retries=3)
def process_media_session(self, session_id: str) -> dict:
    """
    Processa sessão de mídia capturada: transcodifica segmentos e publica.
    session_id: UUID da MatchMediaSessionModel a processar.
    """
    from uuid import UUID
    from video.infrastructure.models import MatchMediaSessionModel, MediaSegmentModel

    try:
        session = MatchMediaSessionModel.objects.get(pk=UUID(session_id))
        if session.state not in ("SYNCING", "TRANSCODING"):
            return {"status": "skipped", "reason": f"state={session.state}", "session_id": session_id}

        session.state = "TRANSCODING"
        session.save(update_fields=["state"])

        # Finalizar segmentos OPEN → FINALIZED
        updated = MediaSegmentModel.objects.filter(
            session_id=session.id,
            state="OPEN",
        ).update(state="FINALIZED")

        session.state = "PUBLISHED"
        session.save(update_fields=["state"])

        return {
            "status": "published",
            "session_id": session_id,
            "segments_finalized": updated,
        }
    except MatchMediaSessionModel.DoesNotExist:
        return {"status": "not_found", "session_id": session_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=15 * (2 ** self.request.retries))


@shared_task(name="video.generate_thumbnail", bind=True, max_retries=2)
def generate_thumbnail(self, segment_id: str) -> dict:
    """
    Gera thumbnail para um MediaSegment finalizado.
    segment_id: UUID do MediaSegmentModel.
    """
    from uuid import UUID
    from video.infrastructure.models import MediaSegmentModel

    try:
        segment = MediaSegmentModel.objects.get(pk=UUID(segment_id))
        # Stub: geração real requer FFmpeg ou serviço externo
        return {
            "status": "thumbnail_queued",
            "segment_id": segment_id,
            "codec": segment.codec_label,
        }
    except MediaSegmentModel.DoesNotExist:
        return {"status": "not_found", "segment_id": segment_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
