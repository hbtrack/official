"""
Athlete Data Export Service - Step 24 (LGPD Compliance)

Serviço para exportação de dados pessoais do atleta conforme LGPD Art. 18.

Features:
- Export completo de dados pessoais (wellness, attendance, badges, medical)
- Formatos JSON e CSV (ZIP com múltiplos arquivos)
- NÃO inclui data_access_logs (conforme LGPD)
- Registra exportação em audit_logs
- Validação de ownership (apenas próprios dados)
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import csv
import io
import zipfile
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.models.athlete import Athlete
from app.models.person import Person
from app.models.wellness_pre import WellnessPre
from app.models.wellness_post import WellnessPost
from app.models.attendance import Attendance
from app.models.medical_case import MedicalCase
from app.models.athlete_badge import AthleteBadge
from app.models.audit_logs import AuditLog
from app.core.exceptions import NotFoundError as NotFoundException, BusinessError as BadRequestException


class AthleteDataExportService:
    """
    Service para exportação de dados do atleta (LGPD)
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def export_athlete_data(
        self,
        user_id: UUID,
        athlete_id: UUID,
        export_format: str = 'json',
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Exporta todos os dados do atleta em formato JSON ou CSV
        
        LGPD Compliance:
        - Atleta pode exportar apenas seus próprios dados
        - Inclui: wellness_pre, wellness_post, attendance, medical_cases, badges
        - NÃO inclui: data_access_logs (logs de quem acessou seus dados)
        - Registra exportação em audit_logs
        
        Args:
            user_id: ID do usuário solicitante
            athlete_id: ID do atleta (deve pertencer ao user_id)
            export_format: 'json' ou 'csv'
            ip_address: IP do solicitante (para audit)
            user_agent: User agent (para audit)
        
        Returns:
            {
                "format": "json" | "csv",
                "data": {...} | None,  # JSON data
                "file_content": bytes | None,  # CSV ZIP bytes
                "file_name": str,
                "generated_at": ISO datetime,
                "total_records": int
            }
        
        Raises:
            NotFoundException: Atleta não encontrado
            BadRequestException: Formato inválido ou atleta não pertence ao user
        """
        
        # 1. Validar formato
        if export_format not in ['json', 'csv']:
            raise BadRequestException(f"Formato inválido: {export_format}. Use 'json' ou 'csv'")
        
        # 2. Buscar atleta e validar ownership
        result = await self.db.execute(
            select(Athlete)
            .options(selectinload(Athlete.person))
            .where(Athlete.id == athlete_id)
        )
        athlete = result.scalar_one_or_none()
        
        if not athlete:
            raise NotFoundException(f"Atleta {athlete_id} não encontrado")
        
        if athlete.user_id != user_id:
            raise BadRequestException("Você só pode exportar seus próprios dados")
        
        # 3. Coletar todos os dados
        personal_info = await self._get_personal_info(athlete)
        wellness_pre_history = await self._get_wellness_pre_history(athlete_id)
        wellness_post_history = await self._get_wellness_post_history(athlete_id)
        attendance_history = await self._get_attendance_history(athlete_id)
        medical_cases = await self._get_medical_cases(athlete_id)
        badges = await self._get_badges(athlete_id)
        
        total_records = (
            len(wellness_pre_history) +
            len(wellness_post_history) +
            len(attendance_history) +
            len(medical_cases) +
            len(badges)
        )
        
        generated_at = datetime.now().isoformat()
        
        # 4. Gerar no formato solicitado
        if export_format == 'json':
            data = {
                "personal_info": personal_info,
                "wellness_pre_history": wellness_pre_history,
                "wellness_post_history": wellness_post_history,
                "attendance_history": attendance_history,
                "medical_cases": medical_cases,
                "badges": badges,
                "generated_at": generated_at,
                "total_records": total_records,
                "lgpd_notice": "Seus dados pessoais conforme LGPD Art. 18. NÃO inclui logs de acesso."
            }
            
            file_name = f"athlete_data_{athlete_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            result_data = {
                "format": "json",
                "data": data,
                "file_content": None,
                "file_name": file_name,
                "generated_at": generated_at,
                "total_records": total_records
            }
        
        else:  # CSV
            zip_content = await self._generate_csv_zip(
                personal_info=personal_info,
                wellness_pre=wellness_pre_history,
                wellness_post=wellness_post_history,
                attendance=attendance_history,
                medical=medical_cases,
                badges=badges,
                athlete_id=athlete_id
            )
            
            file_name = f"athlete_data_{athlete_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            
            result_data = {
                "format": "csv",
                "data": None,
                "file_content": zip_content,
                "file_name": file_name,
                "generated_at": generated_at,
                "total_records": total_records
            }
        
        # 5. Registrar em audit_logs
        await self._log_export(
            user_id=user_id,
            athlete_id=athlete_id,
            export_format=export_format,
            total_records=total_records,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return result_data
    
    async def _get_personal_info(self, athlete: Athlete) -> Dict[str, Any]:
        """Informações pessoais do atleta"""
        person = athlete.person
        
        return {
            "athlete_id": str(athlete.id),
            "full_name": person.full_name if person else None,
            "nickname": athlete.nickname,
            "birth_date": person.birth_date.isoformat() if person and person.birth_date else None,
            "gender": athlete.gender,
            "position": athlete.position,
            "jersey_number": athlete.jersey_number,
            "height_cm": athlete.height_cm,
            "weight_kg": athlete.weight_kg,
            "dominant_hand": athlete.dominant_hand,
            "created_at": athlete.created_at.isoformat() if athlete.created_at else None
        }
    
    async def _get_wellness_pre_history(self, athlete_id: UUID) -> List[Dict[str, Any]]:
        """Histórico de wellness pre-treino"""
        result = await self.db.execute(
            select(WellnessPre)
            .where(WellnessPre.athlete_id == athlete_id)
            .order_by(WellnessPre.filled_at.desc())
        )
        records = result.scalars().all()
        
        return [
            {
                "session_id": str(r.training_session_id),
                "filled_at": r.filled_at.isoformat(),
                "sleep_hours": float(r.sleep_hours) if r.sleep_hours else None,
                "sleep_quality": r.sleep_quality,
                "fatigue": r.fatigue,
                "stress": r.stress,
                "muscle_soreness": r.muscle_soreness,
                "mood": r.mood,
                "readiness": r.readiness,
                "notes": r.notes
            }
            for r in records
        ]
    
    async def _get_wellness_post_history(self, athlete_id: UUID) -> List[Dict[str, Any]]:
        """Histórico de wellness pós-treino"""
        result = await self.db.execute(
            select(WellnessPost)
            .where(WellnessPost.athlete_id == athlete_id)
            .order_by(WellnessPost.filled_at.desc())
        )
        records = result.scalars().all()
        
        return [
            {
                "session_id": str(r.training_session_id),
                "filled_at": r.filled_at.isoformat(),
                "minutes": r.minutes,
                "rpe": r.rpe,
                "internal_load": float(r.internal_load) if r.internal_load else None,
                "fatigue_after": r.fatigue_after,
                "mood_after": r.mood_after,
                "notes": r.notes
            }
            for r in records
        ]
    
    async def _get_attendance_history(self, athlete_id: UUID) -> List[Dict[str, Any]]:
        """Histórico de presenças"""
        result = await self.db.execute(
            select(Attendance)
            .where(Attendance.athlete_id == athlete_id)
            .order_by(Attendance.created_at.desc())
        )
        records = result.scalars().all()
        
        return [
            {
                "session_id": str(r.training_session_id),
                "status": r.status,
                "participation_pct": r.participation_pct,
                "notes": r.notes,
                "created_at": r.created_at.isoformat()
            }
            for r in records
        ]
    
    async def _get_medical_cases(self, athlete_id: UUID) -> List[Dict[str, Any]]:
        """Histórico médico (casos registrados)"""
        result = await self.db.execute(
            select(MedicalCase)
            .where(MedicalCase.athlete_id == athlete_id)
            .order_by(MedicalCase.created_at.desc())
        )
        records = result.scalars().all()
        
        return [
            {
                "id": str(r.id),
                "type": r.type,
                "severity": r.severity,
                "body_part": r.body_part,
                "description": r.description,
                "created_at": r.created_at.isoformat(),
                "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None
            }
            for r in records
        ]
    
    async def _get_badges(self, athlete_id: UUID) -> List[Dict[str, Any]]:
        """Badges conquistados"""
        result = await self.db.execute(
            select(AthleteBadge)
            .where(AthleteBadge.athlete_id == athlete_id)
            .order_by(AthleteBadge.earned_at.desc())
        )
        records = result.scalars().all()
        
        return [
            {
                "type": r.type,
                "month_reference": r.month_reference,
                "earned_at": r.earned_at.isoformat(),
                "response_rate": float(r.response_rate) if r.response_rate else None
            }
            for r in records
        ]
    
    async def _generate_csv_zip(
        self,
        personal_info: Dict,
        wellness_pre: List[Dict],
        wellness_post: List[Dict],
        attendance: List[Dict],
        medical: List[Dict],
        badges: List[Dict],
        athlete_id: UUID
    ) -> bytes:
        """Gera ZIP com múltiplos CSVs"""
        
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # 1. Personal info
            if personal_info:
                csv_content = self._dict_to_csv([personal_info])
                zip_file.writestr('personal_info.csv', csv_content)
            
            # 2. Wellness Pre
            if wellness_pre:
                csv_content = self._dict_to_csv(wellness_pre)
                zip_file.writestr('wellness_pre.csv', csv_content)
            
            # 3. Wellness Post
            if wellness_post:
                csv_content = self._dict_to_csv(wellness_post)
                zip_file.writestr('wellness_post.csv', csv_content)
            
            # 4. Attendance
            if attendance:
                csv_content = self._dict_to_csv(attendance)
                zip_file.writestr('attendance.csv', csv_content)
            
            # 5. Medical Cases
            if medical:
                csv_content = self._dict_to_csv(medical)
                zip_file.writestr('medical_cases.csv', csv_content)
            
            # 6. Badges
            if badges:
                csv_content = self._dict_to_csv(badges)
                zip_file.writestr('badges.csv', csv_content)
            
            # 7. README
            readme_content = f"""
LGPD - Exportação de Dados Pessoais
=====================================

Atleta ID: {athlete_id}
Gerado em: {datetime.now().isoformat()}

Arquivos incluídos:
- personal_info.csv: Informações pessoais
- wellness_pre.csv: Wellness pré-treino
- wellness_post.csv: Wellness pós-treino
- attendance.csv: Presenças em treinos
- medical_cases.csv: Histórico médico
- badges.csv: Badges conquistados

IMPORTANTE:
- Este export NÃO inclui logs de acesso (data_access_logs)
- Conforme LGPD Art. 18 - Direito à portabilidade
- Para dúvidas: contato@handballtrack.app
"""
            zip_file.writestr('README.txt', readme_content)
        
        zip_buffer.seek(0)
        return zip_buffer.read()
    
    def _dict_to_csv(self, data: List[Dict]) -> str:
        """Converte lista de dicts para CSV string"""
        if not data:
            return ""
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        
        return output.getvalue()
    
    async def _log_export(
        self,
        user_id: UUID,
        athlete_id: UUID,
        export_format: str,
        total_records: int,
        ip_address: Optional[str],
        user_agent: Optional[str]
    ):
        """Registra exportação em audit_logs"""
        
        audit_log = AuditLog(
            user_id=user_id,
            action="athlete_data_export",
            entity_type="athlete",
            entity_id=athlete_id,
            old_values=None,
            new_values={
                "export_format": export_format,
                "total_records": total_records,
                "generated_at": datetime.now().isoformat()
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.db.add(audit_log)
        await self.db.commit()
