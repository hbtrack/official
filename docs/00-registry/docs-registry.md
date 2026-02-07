<!-- STATUS: VERIFIED | evidencia: registry gerado em 2026-01-27 -->

# HB Track - Documentation Registry

> Gerado em: 2026-01-27T11:30:00Z
> Total de arquivos: 201

## Legenda

### Status
- **VERIFIED**: Validado contra fonte canonica (_generated/)
- **NEEDS_REVIEW**: Requer revisao para confirmar atualidade
- **DEPRECATED**: Obsoleto ou arquivado

### Tipos
- **sistema**: Arquitetura, configuracao, schemas
- **modulo**: Documentacao de funcionalidades especificas
- **guia**: Procedimentos e troubleshooting
- **planejamento**: Sprints, roadmaps, planos
- **deploy**: Certificacao e deploy
- **resumo**: Executive summaries
- **log**: Historico, implementacoes concluidas

---

## Registry

### _generated/ (VERIFIED)

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| _generated/openapi.json | sistema | VERIFIED | _generated/openapi.json | fonte canonica API |
| _generated/schema.sql | sistema | VERIFIED | _generated/schema.sql | fonte canonica DB |
| _generated/alembic_state.txt | sistema | VERIFIED | _generated/alembic_state.txt | estado migrations |
| _generated/alembic_run.log | log | VERIFIED | _generated/alembic_run.log | log execucao |
| _generated/schema_run.log | log | VERIFIED | _generated/schema_run.log | log execucao |
| _generated/trd_training_permissions_report.txt | log | VERIFIED | _generated/trd_training_permissions_report.txt:27-32 | evidencias de permission_keys (Training templates) |

### Root - Indices Duplicados (DEPRECATED)

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| _README.md | sistema | DEPRECATED | - | replaced by docs/README.md |
| _INDICE.md | sistema | DEPRECATED | - | replaced by docs/README.md |
| _MAPA.md | sistema | DEPRECATED | - | replaced by docs/README.md |
| _ESTRUTURA_DOCS.md | sistema | DEPRECATED | - | replaced by docs/README.md |

### Root - Demais Arquivos

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| README.md | sistema | NEEDS_REVIEW | - | indice principal |
| _ANALISE_FLUXO_ATIVIDADES.md | sistema | NEEDS_REVIEW | - | - |
| _COBERTURA_E2E_TEAMS.md | log | NEEDS_REVIEW | - | - |
| _PERMISSIONS.md | sistema | NEEDS_REVIEW | - | - |
| _PLANO_CONTRATO_TRAINING.md | planejamento | NEEDS_REVIEW | - | - |
| _PLANO_GESTAO_STAFF.md | planejamento | NEEDS_REVIEW | - | - |
| _PLANO_TESTES.md | planejamento | NEEDS_REVIEW | - | - |
| _PLANO_TRAINING.md | planejamento | NEEDS_REVIEW | - | - |
| 1- ACCESSIBILITY_CHECKLIST.md | guia | NEEDS_REVIEW | - | - |
| 2 - CHECKLIST_VALIDACAO_PROXIMAS_ATIVIDADES.md | guia | NEEDS_REVIEW | - | - |
| 3 - CHECKLIST_VALIDACAO_STAFF_REMOVAL.md | guia | NEEDS_REVIEW | - | - |
| API_ANALYTICS_ENDPOINTS.md | sistema | NEEDS_REVIEW | - | verificar contra openapi.json |
| API_CONTRACT.md | sistema | NEEDS_REVIEW | - | verificar contra openapi.json |
| apply_migration_staging.py | guia | NEEDS_REVIEW | - | script |
| CHANGELOG.md | log | NEEDS_REVIEW | - | - |
| CHECKLIST_GO_LIVE_RAG.md | deploy | NEEDS_REVIEW | - | - |
| CHECKPOINT_PASSO_3.md | log | NEEDS_REVIEW | - | - |
| CORRECOES_BUILD_2026-01-20.md | log | NEEDS_REVIEW | - | - |
| deploy_producao.bat | deploy | NEEDS_REVIEW | - | script |
| DEPLOY_STATUS_FINAL.md | deploy | NEEDS_REVIEW | - | - |
| DEPLOYMENT_COMPLETO_SUCESSO.md | deploy | NEEDS_REVIEW | - | - |
| DEPLOYMENT_PRODUCAO.md | deploy | NEEDS_REVIEW | - | - |
| DEPLOYMENT_PRODUCAO_EXECUTADO.md | deploy | NEEDS_REVIEW | - | - |
| ENTREGA_FINAL_RAG_COMPLIANT.md | resumo | NEEDS_REVIEW | - | - |
| ESTRUTURA_BANCO.md | sistema | NEEDS_REVIEW | - | verificar contra schema.sql |
| FASE1_CONCLUIDA.md | log | NEEDS_REVIEW | - | - |
| FECHAMENTO_LOG.md | log | NEEDS_REVIEW | - | - |
| FECHAMENTO_TRAINING.md | log | NEEDS_REVIEW | - | - |
| FLUXO_FRONTEND.md | sistema | NEEDS_REVIEW | - | - |
| FRONTEND_INTEGRATION_PLAN.md | planejamento | NEEDS_REVIEW | - | - |
| FRONTEND_NEXTJS_PLAN.md | planejamento | NEEDS_REVIEW | - | - |
| IMPLEMENTACAO_RELATORIOS_STATUS.md | log | NEEDS_REVIEW | - | - |
| LOG_PERMISSIONS.md | log | NEEDS_REVIEW | - | - |
| LOGS.md | log | NEEDS_REVIEW | - | - |
| MANUAL_DE_RELATORIOS.md | guia | NEEDS_REVIEW | - | - |
| MIGRATIONS_SUMMARY.txt | log | NEEDS_REVIEW | - | verificar contra alembic_state |
| PASSO_1_VERIFICACAO_COMPLETA.md | log | NEEDS_REVIEW | - | - |
| PERMISSIONS.md | sistema | NEEDS_REVIEW | - | - |
| Plano.md | planejamento | NEEDS_REVIEW | - | - |
| PROJETO_CONCLUIDO.md | resumo | NEEDS_REVIEW | - | - |
| pytest.ini | guia | NEEDS_REVIEW | - | config |
| QUICK_FIX_RENDER.md | guia | NEEDS_REVIEW | - | - |
| README_RELATORIOS.md | guia | NEEDS_REVIEW | - | - |
| REGRAS_SISTEMAS.md | sistema | NEEDS_REVIEW | - | - |
| RENDER_API_TESTS.md | guia | NEEDS_REVIEW | - | - |
| RENDER_DEPLOY_INSTRUCTIONS.md | deploy | NEEDS_REVIEW | - | - |
| RENDER_FREE_TIER_SOLUTION.md | guia | NEEDS_REVIEW | - | - |
| RENDER_HOTFIX_MIGRATIONS.md | guia | NEEDS_REVIEW | - | - |
| review.sql | sistema | NEEDS_REVIEW | - | script |
| run_migration_staging.bat | deploy | NEEDS_REVIEW | - | script |
| SEED_CANONICO.md | guia | NEEDS_REVIEW | - | - |
| SEED_E2E_TRAINING_PLAN.md | planejamento | NEEDS_REVIEW | - | - |
| SISTEMA_RELATORIOS_PRONTO_PARA_PRODUCAO.md | resumo | NEEDS_REVIEW | - | - |
| TELAS INTERFACE.md | sistema | NEEDS_REVIEW | - | - |
| test_reports_staging.py | guia | NEEDS_REVIEW | - | script |
| TRAINING_LOG.md | log | NEEDS_REVIEW | - | - |
| TRAINING_LOG_2.md | log | NEEDS_REVIEW | - | - |
| TRAINING_TESTS.md | guia | NEEDS_REVIEW | - | - |
| validate_rag_prod.py | guia | NEEDS_REVIEW | - | script |
| VERIFICAR_MIGRATIONS_RENDER.md | guia | NEEDS_REVIEW | - | - |
| verify_staging.py | guia | NEEDS_REVIEW | - | script |

### 01-sistema-atual/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 01-sistema-atual/_SISTEMA_CONFIGURACAO_COMPLETA.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/ARQUITETURA_PERMISSOES_CANONICAS.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/DESIGN_SYSTEM.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/MANUAL_SISTEMA_HBTRACK.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/RBAC_MATRIX.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/SCHEMA_CANONICO_DATABASE.md | sistema | NEEDS_REVIEW | - | verificar contra schema.sql |
| 01-sistema-atual/SIDEBAR.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/SISTEMA_PERMISSOES.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/STATUS_GERAL_TEAMS_STAGING.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/system_rules.md | sistema | NEEDS_REVIEW | - | - |
| 01-sistema-atual/TOPBAR.md | sistema | NEEDS_REVIEW | - | - |

### 02-modulos/athletes/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 02-modulos/athletes/CHECKLIST_TESTES_PAGINA_ATLETAS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/athletes/FICHA_UNICA_REFACTORING_CHECKLIST.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/athletes/FICHA_UNICA_WIZARD_CONFIRMACAO.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/athletes/IMPLEMENTACAO_PAGINA_ATLETAS_3_COLUNAS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/athletes/INTEGRACAO_CADASTRO_ATLETAS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/athletes/REGRAS_GERENCIAMENTO_ATLETAS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/athletes/RESULTADO_TESTES_PAGINA_ATLETAS.md | modulo | NEEDS_REVIEW | - | - |

### 02-modulos/auth/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 02-modulos/auth/_CANON_AS_IS.md | canon | VERIFIED | openapi.json, schema.sql | referencia canonica do modulo |
| 02-modulos/auth/ANALISE_PAGINAS_LOGIN.md | modulo | DEPRECATED | - | analise de frontend |
| 02-modulos/auth/CAMPOS_OBRIGATORIOS_BANCO.md | modulo | VERIFIED | schema.sql | campos batem com schema |
| 02-modulos/auth/CORRECOES_FINAIS_WELCOME.md | modulo | DEPRECATED | - | historico de bug fixes |
| 02-modulos/auth/CORRECOES_FORMULARIOS_BANCO.md | modulo | DEPRECATED | - | historico de implementacao |
| 02-modulos/auth/GUIA_TESTE_FORMULARIOS_ESPECIFICOS.md | modulo | DEPRECATED | - | guia de teste |
| 02-modulos/auth/MELHORIAS_AUTENTICACAO_IMPLEMENTADAS.md | modulo | DEPRECATED | - | historico de implementacao |
| 02-modulos/auth/PADRONIZACAO_AUTH_CONTEXT.md | modulo | DEPRECATED | - | detalhes de implementacao |
| 02-modulos/auth/RELATORIO_AUDITORIA_LOGIN_AUTORIZACAO.md | modulo | DEPRECATED | - | auditoria historica |
| 02-modulos/auth/RESUMO_CORRECOES.md | modulo | DEPRECATED | - | resumo historico |
| 02-modulos/auth/SSR_COOKIE_FIX.md | modulo | DEPRECATED | - | fix tecnico de frontend |

### 02-modulos/games/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 02-modulos/games/PLANO_IMPLEMENTACAO_COMPETICOES_IA.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/games/RELATORIO_ROTA_GAMES.md | modulo | NEEDS_REVIEW | - | - |

### 02-modulos/statistics/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 02-modulos/statistics/ESTATISTICAS.MD | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/statistics/IMPLEMENTACOES_STATISTICS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/statistics/SESSAO_IMPLEMENTACAO_STATISTICS_PARTE2.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/statistics/STATISTICS_REPORTS_EVENTOS.md | modulo | NEEDS_REVIEW | - | - |

### 02-modulos/teams/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 02-modulos/teams/codigo-teams.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/Convidar membros.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/FIX_TEAM_MEMBERS_INVITE.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/IMPLEMENTACAO_PAGINA_TEAMS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/IMPLEMENTACAO_TEAMS_3_COLUNAS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/PLANO_MIGRACAO_TEAMS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/RELATORIO_ROTA_TEAMS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/RODAR_TEAMS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/TEAMS_ROTAS_CANONICAS.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/teams1.md | modulo | NEEDS_REVIEW | - | - |
| 02-modulos/teams/teams-CONTRACT.md | modulo | NEEDS_REVIEW | - | verificar contra openapi.json |

### 02-modulos/training/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 02-modulos/training/_CANON_AS_IS.md | canon | VERIFIED | _generated/openapi.json, _generated/schema.sql, _generated/alembic_state.txt | referencia canonica do modulo |
| 02-modulos/training/BUG_REPORT_training_session_service.md | modulo | NEEDS_REVIEW | - | relato de bug |
| 02-modulos/training/IMPLEMENTACAO_FOCOS_TREINO.md | modulo | DEPRECATED | - | historico (implementacao/tarefa concluida) |
| 02-modulos/training/IMPLEMENTACAO_MODULO_TREINOS_COMPLETO.md | modulo | DEPRECATED | - | historico (implementacao/tarefa concluida) |
| 02-modulos/training/IMPLEMENTACAO_TREINOS_F1.MD | modulo | DEPRECATED | - | historico (implementacao/tarefa concluida) |
| 02-modulos/training/PLANO_IMPLEMENTACAO_TREINOS.md | modulo | DEPRECATED | paths['/api/v1/training-sessions/{training_session_id}/reopen'] nao existe | conflito com AS-IS |
| 02-modulos/training/PROGRESSO_IMPLEMENTACAO_TREINOS_F1.MD | modulo | DEPRECATED | paths['/api/v1/training-sessions/{training_session_id}/reopen'] nao existe | conflito com AS-IS |
| 02-modulos/training/RELATORIO_ROTA_TRAINING.md | modulo | DEPRECATED | paths['/api/v1/training-sessions/{training_session_id}/reopen'] nao existe | conflito com AS-IS |
| 02-modulos/training/TAREFA_10_SUGESTOES_INTELIGENTES_IMPLEMENTADO.md | modulo | DEPRECATED | - | historico (implementacao/tarefa concluida) |
| 02-modulos/training/TAREFA_6_AUTO_SAVE_IMPLEMENTADO.md | modulo | DEPRECATED | - | historico (implementacao/tarefa concluida) |
| 02-modulos/training/TAREFA_7_8_PAGINA_DETALHES_IMPLEMENTADO.md | modulo | DEPRECATED | - | historico (implementacao/tarefa concluida) |
| 02-modulos/training/TAREFA_9_PLANEJAMENTO_SEMANAL_IMPLEMENTADO.md | modulo | DEPRECATED | - | historico (implementacao/tarefa concluida) |
| 02-modulos/training/TRAINING_V2_API.md | modulo | DEPRECATED | paths['/api/v1/training-v2'] nao existe | conflito com AS-IS |
| 02-modulos/training/TRAINING_V2_EXAMPLES.md | modulo | DEPRECATED | paths['/api/v1/training-v2'] nao existe | conflito com AS-IS |
| 02-modulos/training/training-CONTRACT.md | modulo | DEPRECATED | paths['/api/v1/training-sessions/{training_session_id}/reopen'] nao existe | conflito com AS-IS |
| 02-modulos/training/TRAINNIG.MD | modulo | NEEDS_REVIEW | - | UX/fluxo sem evidencia em _generated |
| 02-modulos/training/TRD_TRAINING.md | modulo | VERIFIED | _generated/trd_training_permissions_report.txt:27-32; pytest tests/e2e/test_training_flow_e2e.py -q (1 passed) | gaps GAP-001/GAP-002 com evidencias e execucao |
| 02-modulos/training/TREINOS_ALERTAS_APRENDIZADO.md | modulo | NEEDS_REVIEW | - | conceitual |
| 02-modulos/training/TREINOS_FLUXOS_E_DADOS.md | modulo | DEPRECATED | paths['/api/v1/training-cycles/{cycle_id}/close'] nao existe | conflito com AS-IS |
| 02-modulos/training/TREINOS_VISUALIZACOES_RELATORIOS_CONTINUIDADE.md | modulo | NEEDS_REVIEW | - | conceitual |

### 03-implementacoes-concluidas/ (DEPRECATED)

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 03-implementacoes-concluidas/_IMPLEMENTACAO_ASYNC.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/CORRECAO_CRITICA_COMPETITIONS_E_TRAINING.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/ETAPA1_VALIDACAO_MEMBRO_CONCLUIDA.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/ETAPA2_FORMULARIOS_ESPECIFICOS_CONCLUIDA.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/ETAPA3_SEPARACAO_MEMBROS_CONCLUIDA.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/FIX_CORS_APPLIED.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/IMPLEMENTACAO_EMAIL_PROFISSIONAL.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/INTEGRACAO_GAPS_COMPLETA.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/MELHORIAS_EMAIL_IMPLEMENTADAS.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/PROFESSIONAL_SIDEBAR_FUNCIONAMENTO.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/RELATORIO_TOPBAR_v2.0.md | log | DEPRECATED | - | implementacao concluida |
| 03-implementacoes-concluidas/VALIDACAO_CATEGORIA_WELCOME.md | log | DEPRECATED | - | implementacao concluida |

### 04-planejamento/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 04-planejamento/_SPRINT_3_4_FINAL.md | planejamento | NEEDS_REVIEW | - | - |
| 04-planejamento/PLANO_ACAO_EXECUTAVEL.md | planejamento | NEEDS_REVIEW | - | - |
| 04-planejamento/PLANO_VALIDACAO_STAGING.md | planejamento | NEEDS_REVIEW | - | - |

### 05-guias-procedimentos/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 05-guias-procedimentos/COMANDOS_VALIDACAO.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/email_invite_service.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/FLUXO_RESET_MIGRATION_SEED.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/FLUXO_VALIDACAO.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/HOTFIX_TEAM_INVITES_SQLALCHEMY.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/MIGRATION_GUIDE.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/PRONTO_PARA_EXECUTAR.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/README.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/REGRAS_GERENCIAMENTO_USUARIOS.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/team_tests_rules.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/TESTES_E2E_ATUALIZADOS.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/TESTIDS_MANIFEST.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/TROUBLESHOOTING_API_CONNECTION.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/TROUBLESHOOTING_GUIDE.md | guia | NEEDS_REVIEW | - | - |
| 05-guias-procedimentos/VALIDACAO_MANUAL_CONVITES.md | guia | NEEDS_REVIEW | - | - |

### 06-certificacao-deploy/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 06-certificacao-deploy/_CERTIFICACAO_FUNCIONAMENTO.md | deploy | NEEDS_REVIEW | - | - |
| 06-certificacao-deploy/_DEPLOY_CHECKLIST.md | deploy | NEEDS_REVIEW | - | - |
| 06-certificacao-deploy/_SISTEMA_VALIDADO_E_FUNCIONANDO.md | deploy | NEEDS_REVIEW | - | - |
| 06-certificacao-deploy/README.md | deploy | NEEDS_REVIEW | - | - |

### 07-organizacao-limpeza/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 07-organizacao-limpeza/_LIMPEZA_ARQUIVOS_MORTOS.md | guia | NEEDS_REVIEW | - | - |
| 07-organizacao-limpeza/_ORGANIZACAO_COMPLETA.md | guia | NEEDS_REVIEW | - | - |
| 07-organizacao-limpeza/README.md | guia | NEEDS_REVIEW | - | - |

### 08-resumos-executivos/

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| 08-resumos-executivos/_RESUMO_EXECUTIVO_ASYNC.md | resumo | NEEDS_REVIEW | - | - |
| 08-resumos-executivos/EXECUTIVE_SUMMARY.md | resumo | NEEDS_REVIEW | - | - |
| 08-resumos-executivos/README.md | resumo | NEEDS_REVIEW | - | - |
| 08-resumos-executivos/RESUMO_FINAL_IMPLEMENTACOES.md | resumo | NEEDS_REVIEW | - | - |

### openapi/ (NEEDS_REVIEW)

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| openapi/athletes.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/audit_logs.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/competitions.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/match_subresources.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/memberships.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/rbac.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/team_registrations.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/training_sessions.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |
| openapi/wellness.yaml | sistema | NEEDS_REVIEW | - | verificar contra _generated/openapi.json |

### fase8/ (DEPRECATED)

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| fase8/fase8_tests.txt | log | DEPRECATED | - | fase obsoleta |
| fase8/rag_validation.txt | log | DEPRECATED | - | fase obsoleta |

### _archived/ (DEPRECATED)

| Path | Tipo | Status | Evidencia | Nota |
|------|------|--------|-----------|------|
| _archived/analises/ANALISE_COBERTURA.md | log | DEPRECATED | - | arquivado |
| _archived/analises/ANALISE_COBERTURA_BACKEND_FRONTEND.md | log | DEPRECATED | - | arquivado |
| _archived/analises/CHECKLIST_COMPLETO_VERIFICACAO_FINAL.md | log | DEPRECATED | - | arquivado |
| _archived/analises/CHECKLIST_RESUMO_EXECUTIVO.md | log | DEPRECATED | - | arquivado |
| _archived/analises/CORRECOES_POS_TESTE.md | log | DEPRECATED | - | arquivado |
| _archived/analises/EXECUTIVE_SUMMARY.md | log | DEPRECATED | - | arquivado |
| _archived/analises/PROGRESSO_FASE3_FRONTEND.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RELATORIO_FINAL_FASE3_5.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RELATORIO_SIDEBAR.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RELATORIO_STATUS_ATUAL_REAL.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RELATORIO_TESTES_CADASTRO_STAFF.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RELATORIO_TESTES_CADASTRO_USUARIOS.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RELATORIO_TESTES_CADASTRO_USUARIOS2.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RESUMO_FINAL.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RESUMO_FINAL_IMPLEMENTACOES.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RUN10_SUMMARY.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RUN7_SUMMARY.md | log | DEPRECATED | - | arquivado |
| _archived/analises/RUN9_SUMMARY.md | log | DEPRECATED | - | arquivado |
| _archived/analises/SESSAO_IMPLEMENTACAO_2026-01-04.md | log | DEPRECATED | - | arquivado |
| _archived/analises/UX_COMPONENTES_E_CHECKLIST_FINAL.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/BACKEND_VALIDATION_NEEDED.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/CACHE_LIMITS.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/check_users.py | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/CONTRATO_ATUALIZADO.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/hb_pt.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/hbtrck.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/neondb.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/Nivel 3.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/OPENAPI_EXPORT.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/OPENAPI_SCHEMA_AUTOMATICO.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/PROBLEMA_409_ANALYSIS.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/RUN_LOG.md | log | DEPRECATED | - | arquivado |
| _archived/relatorios-antigos/VALIDACAO_STAGING_RESUMO.md | log | DEPRECATED | - | arquivado |

---

## Estatisticas

| Status | Quantidade |
|--------|------------|
| VERIFIED | 5 |
| DEPRECATED | 51 |
| NEEDS_REVIEW | 145 |
| **Total** | **201** |
