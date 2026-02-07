"""
Schemas para relatórios

Referências RAG:
- R18, R22: Relatórios de treino
- R12, R13, R14: Relatórios de atleta
- RP6, RP7, RP8: Relatórios de wellness
- R13, R14, RP7: Relatórios médicos
"""

from app.schemas.reports.training import (
    TrainingPerformanceMetrics,
    TrainingPerformanceReport,
    TrainingPerformanceFilters,
    TrainingPerformanceTrend,
)

from app.schemas.reports.athlete import (
    AthleteReadinessMetrics,
    AthleteTrainingLoadMetrics,
    AthleteAttendanceMetrics,
    AthleteWellnessMetrics,
    AthleteIndividualReport,
    AthleteIndividualFilters,
)

from app.schemas.reports.wellness import (
    WellnessSummaryMetrics,
    WellnessSummaryReport,
    WellnessSummaryFilters,
)

from app.schemas.reports.medical import (
    MedicalCasesSummaryMetrics,
    MedicalCasesReport,
    MedicalCasesFilters,
)

__all__ = [
    # Training
    "TrainingPerformanceMetrics",
    "TrainingPerformanceReport",
    "TrainingPerformanceFilters",
    "TrainingPerformanceTrend",
    # Athlete
    "AthleteReadinessMetrics",
    "AthleteTrainingLoadMetrics",
    "AthleteAttendanceMetrics",
    "AthleteWellnessMetrics",
    "AthleteIndividualReport",
    "AthleteIndividualFilters",
    # Wellness
    "WellnessSummaryMetrics",
    "WellnessSummaryReport",
    "WellnessSummaryFilters",
    # Medical
    "MedicalCasesSummaryMetrics",
    "MedicalCasesReport",
    "MedicalCasesFilters",
]