"""
Service para refresh de materialized views.

Referências RAG: RF29 (performance), RD85 (índices), R21 (atualização)
"""

from typing import Literal
from sqlalchemy import text
from sqlalchemy.orm import Session


# Mapeamento de nomes amigáveis para nomes de views
VIEW_MAP = {
    "training_performance": "mv_training_performance",
    "athlete_training_summary": "mv_athlete_training_summary",
    "wellness_summary": "mv_wellness_summary",
    "medical_cases_summary": "mv_medical_cases_summary",
}

ViewName = Literal[
    "training_performance",
    "athlete_training_summary",
    "wellness_summary",
    "medical_cases_summary"
]


class RefreshService:
    """Service para refresh de materialized views."""

    @staticmethod
    def refresh_view(db: Session, view_name: ViewName, concurrent: bool = True) -> dict:
        """
        Refresh de uma materialized view específica.

        Args:
            db: SQLAlchemy session
            view_name: Nome da view (friendly name)
            concurrent: Se True, usa CONCURRENTLY (não bloqueia leituras)

        Returns:
            dict com status e mensagem

        Raises:
            ValueError: Se view_name for inválido
        """
        if view_name not in VIEW_MAP:
            raise ValueError(f"View inválida: {view_name}. Opções: {list(VIEW_MAP.keys())}")

        mv_name = VIEW_MAP[view_name]
        concurrently = "CONCURRENTLY" if concurrent else ""

        try:
            # Execute refresh
            db.execute(text(f"REFRESH MATERIALIZED VIEW {concurrently} {mv_name}"))
            db.commit()

            # Get row count
            result = db.execute(text(f"SELECT COUNT(*) as cnt FROM {mv_name}"))
            count = result.fetchone()['cnt']

            return {
                "status": "success",
                "view": mv_name,
                "message": f"View {mv_name} refreshed successfully",
                "concurrent": concurrent,
                "rows": count
            }

        except Exception as e:
            db.rollback()
            return {
                "status": "error",
                "view": mv_name,
                "message": f"Error refreshing {mv_name}: {str(e)}",
                "concurrent": concurrent
            }

    @staticmethod
    def refresh_all(db: Session, concurrent: bool = True) -> dict:
        """
        Refresh de todas as materialized views.

        Args:
            db: SQLAlchemy session
            concurrent: Se True, usa CONCURRENTLY

        Returns:
            dict com resultados de todas as views
        """
        results = {}
        success_count = 0
        error_count = 0

        for view_name in VIEW_MAP.keys():
            result = RefreshService.refresh_view(db, view_name, concurrent)
            results[view_name] = result

            if result["status"] == "success":
                success_count += 1
            else:
                error_count += 1

        return {
            "status": "success" if error_count == 0 else "partial" if success_count > 0 else "error",
            "total_views": len(VIEW_MAP),
            "success_count": success_count,
            "error_count": error_count,
            "results": results
        }

    @staticmethod
    def get_view_stats(db: Session) -> dict:
        """
        Retorna estatísticas de todas as materialized views.

        Returns:
            dict com informações sobre cada view
        """
        stats = {}

        for friendly_name, mv_name in VIEW_MAP.items():
            try:
                # Get row count
                result = db.execute(text(f"SELECT COUNT(*) as cnt FROM {mv_name}"))
                count = result.fetchone()['cnt']

                # Get last refresh time (from pg_stat_user_tables)
                result = db.execute(text(f"""
                    SELECT
                        schemaname,
                        matviewname,
                        last_autovacuum,
                        n_tup_ins,
                        n_tup_upd,
                        n_tup_del
                    FROM pg_stat_user_tables
                    WHERE relname = '{mv_name}'
                """))
                pg_stats = result.fetchone()

                stats[friendly_name] = {
                    "view_name": mv_name,
                    "rows": count,
                    "schema": pg_stats['schemaname'] if pg_stats else None,
                    "last_vacuum": str(pg_stats['last_autovacuum']) if pg_stats and pg_stats['last_autovacuum'] else None,
                }

            except Exception as e:
                stats[friendly_name] = {
                    "view_name": mv_name,
                    "error": str(e)
                }

        return stats
