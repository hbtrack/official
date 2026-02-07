"""
Services para relatórios

Referências RAG:
- R18, R22: Relatórios de treino
- R12, R13, R14: Relatórios de atleta
- RP6, RP7, RP8: Relatórios de wellness
- R13, R14, RP7: Relatórios médicos
"""

from app.services.reports.training_report_service import TrainingReportService
from app.services.reports.athlete_report_service import AthleteReportService
from app.services.reports.wellness_report_service import WellnessReportService
from app.services.reports.medical_report_service import MedicalReportService

__all__ = [
    "TrainingReportService",
    "AthleteReportService",
    "WellnessReportService",
    "MedicalReportService",
]