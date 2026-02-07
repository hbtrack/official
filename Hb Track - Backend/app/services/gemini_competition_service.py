"""
Gemini AI Service para parsing de PDFs de regulamento de competições.

Este serviço utiliza o Google Gemini 1.5 Flash para extrair informações
estruturadas de PDFs de regulamento de competições de handebol.

Características:
- Não usa OCR (Gemini processa PDF nativo)
- Prompt especializado para handebol brasileiro
- Retorna confidence scores por campo
- Suporta múltiplos formatos de competição

Configuração:
- GEMINI_API_KEY: Chave da API do Google Gemini
"""

import base64
import json
import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, date

from google import genai
from google.genai import types
from google.genai.types import HttpOptions 

from app.core.config import settings
from app.schemas.competitions_v2 import (
    AIExtractedCompetition,
    AIExtractedPhase,
    AIExtractedTeam,
    AIExtractedMatch,
    AIParseResponse,
)

logger = logging.getLogger(__name__)


# =============================================================================
# PROMPT ESPECIALIZADO PARA HANDEBOL
# =============================================================================

HANDBALL_COMPETITION_PROMPT = """
Você é um especialista em análise de regulamentos de competições de HANDEBOL brasileiro.
Analise o PDF fornecido e extraia TODAS as informações estruturadas da competição.

CONTEXTO IMPORTANTE - HANDEBOL:
- É um esporte coletivo jogado com as mãos
- Placares típicos: 20-35 gols por time (diferente de futebol!)
- Competições comuns: Ligas estaduais, Copa Brasil, Campeonatos de base (Sub-14 a Sub-21)
- Categorias: Masculino, Feminino, Misto
- Pontuação: Normalmente 2 pontos por vitória, 1 por empate (algumas ligas usam 3)

ESTRUTURA DE RESPOSTA (JSON):
{
  "name": "Nome oficial da competição",
  "season": "2025" ou "2024/2025",
  "modality": "masculino" | "feminino" | "misto",
  "competition_type": "turno_unico" | "turno_returno" | "grupos" | "grupos_mata_mata" | "mata_mata" | "triangular" | "quadrangular" | "custom",
  "format_details": {
    "num_grupos": 4,
    "classificados_por_grupo": 2,
    "tem_terceiro_lugar": true,
    "numero_rodadas": 7
  },
  "tiebreaker_criteria": ["pontos", "saldo_gols", "gols_pro", "confronto_direto"],
  "points_per_win": 2,
  "regulation_notes": "Observações importantes do regulamento",
  
  "teams": [
    {
      "name": "Nome Completo do Clube/Equipe",
      "short_name": "SIGLA",
      "city": "Cidade",
      "group_name": "A",
      "confidence_score": 0.95
    }
  ],
  
  "phases": [
    {
      "name": "Fase de Grupos",
      "phase_type": "group",
      "order_index": 0,
      "confidence_score": 0.9
    },
    {
      "name": "Semifinais",
      "phase_type": "semifinal",
      "order_index": 1,
      "confidence_score": 0.9
    }
  ],
  
  "matches": [
    {
      "external_reference_id": "JOGO_001",
      "home_team_name": "Nome Time Casa",
      "away_team_name": "Nome Time Visitante",
      "match_date": "2025-03-15",
      "match_time": "15:00",
      "location": "Ginásio Municipal",
      "round_number": 1,
      "round_name": "1ª Rodada",
      "home_score": null,
      "away_score": null,
      "confidence_score": 0.85
    }
  ],
  
  "overall_confidence_score": 0.87
}

REGRAS DE EXTRAÇÃO:
1. Se um campo não estiver claro, use null e reduza o confidence_score
2. Para datas, use formato ISO: YYYY-MM-DD
3. Para horários, use formato 24h: HH:MM
4. external_reference_id deve ser único (ex: "R1_JOGO01", "SF_JOGO1")
5. Extraia TODAS as equipes mencionadas, mesmo parcialmente
6. Se houver tabela de jogos, extraia todos os confrontos
7. O confidence_score varia de 0.0 (incerto) a 1.0 (certeza absoluta)

TIPOS DE COMPETIÇÃO:
- turno_unico: Todos jogam contra todos uma vez
- turno_returno: Todos jogam 2x (ida e volta)
- grupos: Fase de grupos apenas
- grupos_mata_mata: Grupos + eliminatórias
- mata_mata: Eliminatórias diretas
- triangular: 3 equipes se enfrentam
- quadrangular: 4 equipes se enfrentam
- custom: Formato especial

TIPOS DE FASE:
- group: Fase de grupos
- round_robin: Todos contra todos
- knockout: Eliminatória genérica
- round_of_16: Oitavas de final
- quarterfinal: Quartas de final
- semifinal: Semifinal
- third_place: Disputa de 3º lugar
- final: Final

Analise o documento e retorne APENAS o JSON, sem explicações adicionais.
"""


# =============================================================================
# GEMINI SERVICE CLASS
# =============================================================================

class GeminiCompetitionService:
    """
    Serviço para extração de dados de competições via Gemini AI.
    Usa o novo pacote google-genai (recomendado).
    """

    def __init__(self):
        """Inicializa o serviço com a API key do Gemini."""
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            logger.warning("GEMINI_API_KEY não configurada. Serviço de IA desabilitado.")
            self.client = None
            return

        # Configura o cliente com a nova API
        self.client = genai.Client(api_key=self.api_key)
        # Usar gemini-2.0-flash-exp (modelo mais recente disponível)
        self.model_name = "gemini-2.0-flash-exp"
        
        logger.info("GeminiCompetitionService inicializado com sucesso (google-genai)")

    def is_available(self) -> bool:
        """Verifica se o serviço está disponível."""
        return self.client is not None

    def parse_regulation_pdf(
        self,
        pdf_base64: str,
        our_team_name: Optional[str] = None,
        hints: Optional[Dict[str, Any]] = None,
    ) -> AIParseResponse:
        """
        Extrai dados estruturados de um PDF de regulamento.
        VERSÃO SÍNCRONA - compatível com Neon free.
        
        Args:
            pdf_base64: Conteúdo do PDF em base64
            our_team_name: Nome da nossa equipe (para identificar nossos jogos)
            hints: Dicas adicionais (número de equipes esperado, formato, etc.)
            
        Returns:
            AIParseResponse com os dados extraídos ou erro
        """
        if not self.is_available():
            return AIParseResponse(
                success=False,
                error_message="Serviço Gemini não está disponível. Verifique GEMINI_API_KEY.",
            )

        start_time = time.time()
        
        try:
            # Decodifica o PDF
            try:
                pdf_bytes = base64.b64decode(pdf_base64)
            except Exception as e:
                return AIParseResponse(
                    success=False,
                    error_message=f"PDF base64 inválido: {str(e)}",
                )

            # Monta o prompt com contexto adicional
            prompt = self._build_prompt(our_team_name, hints)
            
            # Prepara o conteúdo para o Gemini (nova API)
            pdf_part = types.Part.from_bytes(
                data=pdf_bytes,
                mime_type="application/pdf",
            )
            
            # Configuração de geração
            generation_config = types.GenerateContentConfig(
                temperature=0.1,  # Baixa temperatura para respostas consistentes
                top_p=0.95,
                top_k=40,
                max_output_tokens=8192,
                response_mime_type="application/json",
            )
            
            # Chama o Gemini SÍNCRONO - Forçando modelo gemini-2.5-flash
            # (gemini-1.5-flash foi descontinuado, usar 2.5-flash)
            logger.info("Enviando PDF para Gemini (síncrono, gemini-2.5-flash)...")
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",  # HARDCODED - modelo mais recente disponível
                contents=[prompt, pdf_part],
                config=generation_config,
            )
            
            # Processa a resposta
            processing_time = int((time.time() - start_time) * 1000)
            
            if not response.text:
                return AIParseResponse(
                    success=False,
                    error_message="Gemini retornou resposta vazia",
                    processing_time_ms=processing_time,
                )

            # Parse do JSON retornado
            try:
                extracted_data = self._parse_gemini_response(response.text, our_team_name)
            except Exception as e:
                logger.error(f"Erro ao parsear resposta do Gemini: {e}")
                return AIParseResponse(
                    success=False,
                    error_message=f"Erro ao processar resposta da IA: {str(e)}",
                    processing_time_ms=processing_time,
                )

            # Calcula tokens usados (estimativa)
            tokens_used = None
            if hasattr(response, 'usage_metadata'):
                tokens_used = (
                    response.usage_metadata.prompt_token_count +
                    response.usage_metadata.candidates_token_count
                )

            return AIParseResponse(
                success=True,
                extracted_data=extracted_data,
                processing_time_ms=processing_time,
                tokens_used=tokens_used,
            )

        except Exception as e:
            logger.exception(f"Erro ao processar PDF com Gemini: {e}")
            processing_time = int((time.time() - start_time) * 1000)
            return AIParseResponse(
                success=False,
                error_message=f"Erro interno: {str(e)}",
                processing_time_ms=processing_time,
            )

    def _build_prompt(
        self,
        our_team_name: Optional[str],
        hints: Optional[Dict[str, Any]],
    ) -> str:
        """Constrói o prompt com contexto adicional."""
        prompt = HANDBALL_COMPETITION_PROMPT
        
        # Adiciona informações sobre nossa equipe
        if our_team_name:
            prompt += f"""

INFORMAÇÃO ADICIONAL:
Nossa equipe se chama "{our_team_name}".
Quando encontrar jogos desta equipe, marque como nossos jogos para facilitar a identificação.
"""

        # Adiciona hints do usuário
        if hints:
            prompt += "\n\nDICAS DO USUÁRIO:\n"
            if hints.get("expected_teams_count"):
                prompt += f"- Espera-se {hints['expected_teams_count']} equipes na competição\n"
            if hints.get("expected_format"):
                prompt += f"- Formato esperado: {hints['expected_format']}\n"
            if hints.get("category"):
                prompt += f"- Categoria: {hints['category']}\n"
            if hints.get("additional_notes"):
                prompt += f"- Observações: {hints['additional_notes']}\n"

        return prompt

    def _parse_gemini_response(
        self,
        response_text: str,
        our_team_name: Optional[str],
    ) -> AIExtractedCompetition:
        """Parseia a resposta JSON do Gemini."""
        
        # Tenta extrair JSON da resposta
        json_str = response_text.strip()
        
        # Remove possíveis marcadores de código
        if json_str.startswith("```json"):
            json_str = json_str[7:]
        if json_str.startswith("```"):
            json_str = json_str[3:]
        if json_str.endswith("```"):
            json_str = json_str[:-3]
        
        json_str = json_str.strip()
        
        # Parse do JSON
        data = json.loads(json_str)
        
        # Converte para os schemas Pydantic
        teams = [
            AIExtractedTeam(
                name=t.get("name", ""),
                short_name=t.get("short_name"),
                city=t.get("city"),
                group_name=t.get("group_name"),
                confidence_score=t.get("confidence_score"),
            )
            for t in data.get("teams", [])
        ]
        
        phases = [
            AIExtractedPhase(
                name=p.get("name", ""),
                phase_type=p.get("phase_type", "custom"),
                order_index=p.get("order_index", idx),
                teams=[],  # Teams são listados separadamente
                matches=[],  # Matches são listados separadamente
                confidence_score=p.get("confidence_score"),
            )
            for idx, p in enumerate(data.get("phases", []))
        ]
        
        matches = []
        for m in data.get("matches", []):
            # Converte datas
            match_date = None
            if m.get("match_date"):
                try:
                    match_date = datetime.strptime(m["match_date"], "%Y-%m-%d").date()
                except:
                    pass
            
            match_time = None
            if m.get("match_time"):
                try:
                    match_time = datetime.strptime(m["match_time"], "%H:%M").time()
                except:
                    pass
            
            matches.append(AIExtractedMatch(
                external_reference_id=m.get("external_reference_id"),
                home_team_name=m.get("home_team_name", ""),
                away_team_name=m.get("away_team_name", ""),
                match_date=match_date,
                match_time=match_time,
                location=m.get("location"),
                round_number=m.get("round_number"),
                round_name=m.get("round_name"),
                home_score=m.get("home_score"),
                away_score=m.get("away_score"),
                confidence_score=m.get("confidence_score"),
            ))
        
        return AIExtractedCompetition(
            name=data.get("name", "Competição sem nome"),
            season=data.get("season"),
            modality=data.get("modality"),
            competition_type=data.get("competition_type"),
            format_details=data.get("format_details"),
            tiebreaker_criteria=data.get("tiebreaker_criteria"),
            points_per_win=data.get("points_per_win"),
            regulation_notes=data.get("regulation_notes"),
            phases=phases,
            teams=teams,
            matches=matches,
            overall_confidence_score=data.get("overall_confidence_score"),
        )

    def validate_extraction(
        self,
        extracted_data: AIExtractedCompetition,
    ) -> Dict[str, Any]:
        """
        Valida os dados extraídos e retorna warnings/sugestões.
        VERSÃO SÍNCRONA.
        
        Returns:
            Dict com:
            - is_valid: bool
            - warnings: List[str]
            - suggestions: List[str]
        """
        warnings = []
        suggestions = []
        
        # Verifica campos obrigatórios
        if not extracted_data.name:
            warnings.append("Nome da competição não identificado")
        
        if not extracted_data.teams:
            warnings.append("Nenhuma equipe identificada no regulamento")
        
        if not extracted_data.competition_type:
            warnings.append("Formato da competição não identificado")
            suggestions.append("Selecione o formato manualmente")
        
        # Verifica consistência
        if extracted_data.competition_type in ["grupos", "grupos_mata_mata"]:
            groups = set(t.group_name for t in extracted_data.teams if t.group_name)
            if not groups:
                warnings.append("Competição com grupos mas nenhum grupo identificado nas equipes")
        
        # Verifica confidence scores
        low_confidence_teams = [
            t.name for t in extracted_data.teams
            if t.confidence_score and t.confidence_score < 0.7
        ]
        if low_confidence_teams:
            warnings.append(f"Equipes com baixa confiança: {', '.join(low_confidence_teams[:3])}")
            suggestions.append("Revise os nomes das equipes com baixa confiança")
        
        # Verifica se há jogos
        if not extracted_data.matches:
            suggestions.append("Nenhum jogo extraído. Você pode adicionar manualmente.")
        
        # Overall confidence
        if extracted_data.overall_confidence_score:
            if extracted_data.overall_confidence_score < 0.5:
                warnings.append("Confiança geral da extração está baixa. Revise todos os dados.")
            elif extracted_data.overall_confidence_score < 0.7:
                suggestions.append("Alguns dados podem precisar de revisão manual")
        
        return {
            "is_valid": len(warnings) == 0,
            "warnings": warnings,
            "suggestions": suggestions,
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Instância global do serviço
_gemini_service: Optional[GeminiCompetitionService] = None


def get_gemini_service() -> GeminiCompetitionService:
    """Retorna a instância singleton do serviço Gemini."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiCompetitionService()
    return _gemini_service
