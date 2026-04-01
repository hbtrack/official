Plano de Execução — HB Track até o DONE
Onde estamos hoje
O Plano — 7 Etapas Sequenciais
ETAPA 1 — Corrigir autenticação (desbloqueia tudo)
O problema: 12 dos 17 módulos aceitam requisições sem login. O contrato diz "precisa de token JWT", mas o código finge que está tudo bem sem ele.

A ação: Padronizar as funções de autenticação em todos os módulos, seguindo o padrão que já funciona em teams e seasons (lançar erro 401 quando não tem token).

Módulos a corrigir:

Ciclo 1: training (apenas _get_actor_role)
Ciclo 2: matches, competitions, scout, video
Ciclo 3: medical, wellness, analytics, exercises, reports
Cross-cutting: audit, notifications (verificar)
Entrega: Nenhum endpoint aceita requisição anônima. Todos devolvem 401 sem token.

ETAPA 2 — Completar FASE 4 (Ciclo 1 validado em staging)
Com a autenticação corrigida, executar as tarefas pendentes:

Testes E2E em staging — fluxo completo: login → criar time → temporada → treino → presença
Schemathesis contra staging — confirmar que a API real bate com o contrato OpenAPI
Validar RBAC — treinador não faz o que só admin pode; atleta não edita treinos de outro time
Performance — listagens respondem em < 200ms; sem queries N+1
Segurança OWASP — BOLA, BFLA, headers, rate limiting
Entrega: Critério de Done da FASE 4 atingido.

ETAPA 3 — FASE 6: Deploy produção v0.1 🚀
Primeiro release para o mundo real.

QA final em staging (browser real, dados limpos)
Configurar banco de produção (chaves JWT, secrets)
Deploy via pipeline (aprovação humana)
Health check + SSL + criar admin
Monitoramento (UptimeRobot + logs)
Entrega: Um time de handebol real pode fazer login, criar time, planejar treinos e registrar presença. v0.1 no ar.

ETAPA 4 — FASES 7-9: Ciclo 2 (Operação de jogo → v0.2)
Validar constraints dos 4 módulos (matches, competitions, scout, video)
Definir armazenamento de vídeo (local vs S3)
Testes E2E em staging: criar campeonato → registrar partida ao vivo → scout → vídeo
Regenerar schema.d.ts com npm run api:generate
Frontend Ciclo 2: páginas de competições, partida ao vivo (WebSocket), scout, player de vídeo
Deploy produção v0.2 (aprovação humana)
Entrega: Partidas ao vivo, scouting e análise de vídeo funcionando. v0.2 no ar.

ETAPA 5 — FASES 10-12: Ciclo 3 (Inteligência → v1.0)
Implementar proteção LGPD no módulo medical (acesso restrito por role)
Validação de wellness (ranges corretos), audit (imutabilidade)
Notificações E2E: backend → Celery → WebSocket → frontend
Relatórios PDF assíncronos
Regenerar schema.d.ts
Frontend Ciclo 3: dashboards de analytics, registro de bem-estar, histórico médico, biblioteca de exercícios, notificações
QA completo: 17 módulos, teste de carga (50 usuários), OWASP, acessibilidade
Sentry + alertas de produção
Deploy produção v1.0 (aprovação humana)
Entrega: Plataforma completa com todos os 17 módulos. v1.0 no ar.

ETAPA 6 — FASE 13: Mobile v2.0
Monorepo (extrair lógica compartilhada para packages/shared/)
App React Native + Expo
Fluxo prioritário: login + treinos + bem-estar
Push notifications
Publicar nas lojas (TestFlight → App Store + Play Store)
Entrega: App mobile para atletas e treinadores. v2.0 no ar.

ETAPA 7 — Correções transversais (em paralelo às etapas acima)
Estes items da auditoria devem ser resolvidos ao longo do caminho:

Item	Quando resolver	Prioridade
AsyncAPI: mudar de AMQP para Redis	Antes da ETAPA 3	Média
Password reset + MFA	Antes da ETAPA 3 (v0.1 precisa)	Alta
Exemplos nos contratos OpenAPI	Antes de cada Frontend (etapas 4, 5)	Média
GET /teams/{id}/athletes (listar atletas)	Antes da ETAPA 3	Média
Rate limiting em endpoints de dados	Antes da ETAPA 3	Média
Testes de integração reais (não placeholder)	Contínuo a cada etapa	Média
Visão geral
