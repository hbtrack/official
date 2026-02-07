<!-- STATUS: NEEDS_REVIEW -->

Dominios Statistics e Reports + eventos/infra de confianca

1) STATISTICS (leitura analitica)
- Escopo: interpreta dados ja fechados; agrega, compara e sinaliza. Nao escreve dados esportivos, nao planeja, nao gera PDFs/narrativa. Consome TREINOS; alimenta REPORTS.
- Fontes: training_sessions status=closed; attendance/load/rpe/minutes; focos executados; team_registrations/memberships; metadados de ciclo/microciclo. Sessoes abertas sao invisiveis.
- Entidades logicas: OperationalSnapshot (dia; total sessoes, presenca media, carga media, flags de risco/desvio), TeamAggregate (semana/mes; medias/dispersoes de carga, distribuicao de focos, % sessoes com desvio, consistencia), AthleteAggregate (carga acumulada, historico de presenca, metricas individuais, percentil opcional). Preferir calculo on-the-fly ou cache leve.
- Regras: RBAC rigoroso (atleta so vê dados proprios; comissao vê equipe; coordenação vê agregado); planning_deviation derivado de foco planejado (microciclo) x executado; indicadores de risco sao informativos, nunca erros.
- APIs: GET /statistics (operacional: sessoes recentes, indicadores, badges de risco/desvio, links de leitura contextual); GET /statistics/teams?team_id&season_id&period (agregados por periodo, cards colapsaveis por mesociclo, % desvio, consistencia; sem texto livre ou detalhe de sessao); GET /statistics/athletes?team_id&season_id&filters (metricas individuais + percentis com sticky header e filtros); GET /statistics/snapshots/{scope}/{id} (scope=mesocycle|season) para Reports.
- Nao faz: nao edita, nao fecha periodos, nao cria textos, nao gera PDFs, nao dispara notificacoes, nao aprende padroes (isso e Planejamento).

2) REPORTS (formalizacao institucional)
- Escopo: consolida periodos fechados, transforma dados analiticos em narrativa oficial e gera artefatos imutaveis (PDF). Consome STATISTICS; nunca TREINOS direto.
- Principio: trabalha com snapshots; cada versao reflete estado no fechamento e e imutavel (rastreamento completo).
- Tipos: relatorio de mesociclo (team_id, season_id, mesocycle_id; 1 por mesociclo) e relatorio final da temporada (team_id, season_id; 1 por temporada).
- Modelo de dados: reports (id, org/team/season, scope mesocycle|season, status draft|finalized|locked, created_by, created_at, finalized_at, locked_at); report_snapshots (conteudo consolidado, referenciando report_id, scope_id, payload, created_at); report_narratives (texto markdown com limites dinamicos, state draft/finalized, versionamento leve); report_institutional_notes (visibilidade toggle interna/externa).
- Estados: relatorio draft -> finalized -> locked (institucional). Narrativa editavel somente em draft. Lock impede qualquer mudanca.
- APIs: criar (POST /reports), ler (GET /reports/{id}), editar narrativa draft (PATCH narrative), finalizar (POST /reports/{id}/finalize), lock institucional (POST /reports/{id}/lock). PDF viewer in-app com toggle Tecnica|Executiva; versao executiva fixa max 5 graficos e ordem travada.
- RBAC: comissao tecnica cria/edita; coordenacao/direcao le; superadmin segue RBAC, sem acesso automatico a visao atleta. Nao faz: nao calcula metricas primarias, nao interpreta operacional, nao planeja/ executa.

3) Eventos de dominio e arquitetura event-driven
- Emissores: Treinos (fechar sessao/microciclo/ciclo), Statistics (gerar snapshot), Reports (criar/finalizar/lock), Continuity.
- Eventos principais: training.session.closed; training.microcycle.closed; training.cycle.closed; statistics.*; report.created/finalized/locked; season.continuity.confirmed. Consumers tratam idempotencia.
- Regra: leitura/decisao/narrativa em dominios separados; eventos garantem integracao sem reabrir estados fechados.

4) Confiabilidade: outbox + idempotencia
- outbox_events (Transactional Outbox no mesmo Postgres/Neon): id UUID PK, event_type, payload JSONB, occurred_at, status (pending|published), published_at; indices por status/event_type. Gravado na mesma transacao do evento de dominio (ex.: fechar sessao).
- processed_events: id PK, event_id, event_type, processed_at; garante idempotencia no consumidor (Statistics/Reports).
- idempotency_keys: key PK, request_hash, response JSONB, created_at; usado em endpoints criticos (fechar sessao, finalizar/lock report) para retry seguro.
- Fluxo exemplo fechar sessao: API fecha e grava outbox + responde; worker publica; Statistics consome, checa processed_events, processa uma vez; UI ve sessao fechada imediata, estatisticas segundos depois.
- Alembic: criar tabelas em ordem (outbox_events -> processed_events -> idempotency_keys); nao misturar com migrations de negocio. Retries nao expõem fila ao frontend; garantem previsibilidade de UX.
