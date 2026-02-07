<!-- STATUS: DEPRECATED | arquivado -->

UX componentes validados + checklist de QA

1) Componentes (uso fechado)
- Modal de Heranca Inteligente: em Planejamento/inicio de temporada; preview explicito, aplicacao so apos confirmacao.
- Empty State de inicio de ciclo: em Treinos → Planejamento; CTA unico para Ritual de Inicio.
- Sticky Header da atleta: em listas longas de Statistics/Reports para evitar perda de contexto.
- Campo Markdown com limite dinamico: em Reports (sumario/interpretacao); controla densidade sem engessar.
- Stepper de Progresso da Temporada: em Planejamento/visao de temporada (pre/comp/trans).
- Toggle de visibilidade (governanca): apenas em notas institucionais.
- FAB: somente em Sessao de Treino/Scout ao vivo; nunca em planejamento/analise.
- Dashboard de cards colapsaveis: em Statistics equipes/mesociclo para progressive disclosure.
- Badge de status de auditoria: herancas/preferencias/governanca; feedback de estado, nao punitivo.
- Breadcrumbs hierarquicos: obrigatorios em telas profundas para orientar (Clube > Equipe > Temporada > Ciclo).
- Botao “Copia Suja”: em heranca de planejamento, deixando revisao esperada explicita.
- Timeline lateral de versoes: em anotacoes da coordenacao; leitura passiva.
- Visualizador de PDF in-app: em Reports com toggle Tecnica | Executiva (exec tem max 5 graficos e ordem fixa).
- Date Range Picker travado: em Statistics/Reports para impedir intervalos invalidos.
- Quick Search Filter: em listas longas de atletas; busca semantica.

2) Checklist de navegacao/arquitetura
- Sidebar respeita RBAC; Treinos, Statistics e Reports nunca se misturam. Breadcrumbs corretos; trocar equipe/temporada limpa contexto.

3) Treinos – Planejamento
- Empty state aparece sem ciclo/microciclo e CTA leva ao Ritual de Inicio. Modal de heranca mostra preview, nao aplica sem confirmacao; review_required visivel. Stepper reflete fase atual. Sugestoes: max 1 por camada (foco/carga/tipo), sempre explicam base historica, nunca auto-aplicadas. Planejamento nao gera estatistica nem aparece em Statistics.

4) Treinos – Sessoes
- Criar sessao em poucos segundos; FAB so em sessao/scout. Prefill de focos funciona com planejamento e e totalmente editavel. Fechamento valida presenca e focos, nao bloqueia por desvio; apos fechar, tela read_only e recarregar nao reabre.

5) Statistics – leitura
- /statistics mostra apenas sessoes closed; badges de risco/desvio visuais, nao bloqueantes. /statistics/teams so dados agregados (coordenacao sem detalhe de sessao). /statistics/athletes tem sticky header e quick search. Date range travado aos marcos da temporada.

6) Reports – formalizacao
- Pode criar apenas para periodo elegivel (mesociclo fechado ou temporada). Snapshot congela na criacao; alterar dados depois nao muda relatorio. Markdown tem contador e limite correto. Toggle de visibilidade funciona (interno nao aparece fora). Timeline de versoes mostra historico e versões antigas sao read_only. PDF viewer toggle Tecnica|Executiva respeita limite de 5 graficos e ordem fixa na executiva.

7) Governanca e continuidade
- Campo de interpretacao final: opcional, editavel ate fechamento do proximo ciclo, depois read_only; nao usado para metricas. Painel de Continuidade: herancas visiveis, aplicar opcional, confirmacao de ciencia obrigatoria; badge de auditoria correto; coordenação nao acessa textos individuais.

8) Infra/Confiabilidade (impacto direto em UX)
- Repetir acao critica com mesma Idempotency-Key retorna mesma resposta e nao duplica efeito. Falha do worker: evento fica em outbox_events e processa ao retomar; processed_events impede reprocessar. UI nunca mostra estado intermediario confuso (sessao fechada mas estatistica parcial).

9) Teste de confianca do usuario
- Usuario entende claramente diferenca entre planejamento, execucao, analise e relatorio; nenhuma acao gera surpresa ou sensacao de vigilancia; sempre existe proximo passo claro.
