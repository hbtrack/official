<!-- STATUS: NEEDS_REVIEW -->

Treinos – alertas, desvios e aprendizado assistido

1) Planejado vs executado (prefill, não imposição)
- Planejamento nunca escreve nos dados reais da sessão; gera sugestões iniciais editáveis.
- Sessão criada a partir de microciclo planejado: sliders de foco são pré-preenchidos e rotulados “Sugestão baseada no planejamento semanal”; qualquer ajuste troca rótulo para “Valores ajustados”.
- Armazenar planejado no microciclo; sessão guarda apenas executado + microcycle_id. Nada de campos de foco planejado em training_sessions.

2) Alerta de desvio de planejamento
- Calculado no fechamento da sessão: compara foco planejado (microciclo) x foco executado; critério derivado (ex.: desvio >= X pontos ou %).
- UX na sessão fechada: bloco leve explicando desvio; nunca bloqueia; justificativa opcional (chips rápidas tipo “time curto”, “adaptação tática”, “condição física”).
- Em /statistics (operacional) aparece badge discreto “Desvio de planejamento” que leva à sessão com explicação visível.
- Sem novas tabelas obrigatórias; planning_deviation_flag pode ser persistido como derivado.

3) Visibilidade por perfil (imediato x agregado)
- Comissão técnica: sempre vê alerta individual na sessão e badge no operacional; foco é reflexão e ajuste do próximo microciclo.
- Coordenação/direção: vê apenas visão agregada semanal/mensal (percentual de sessões com desvio, tipos de desvio) em /statistics/teams ou painel dedicado; nunca link direto para “treino problemático”; nada de notificações automáticas.
- RBAC existente governa acesso; coordenação não edita Treinos.

4) Sistema de aprendizado assistido
- Objetivo: aprender padrões recorrentes de desvio para sugerir ajustes no planejamento futuro sem corrigir treinador.
- Critério mínimo: mesmo foco desviando no mesmo sentido em ≥3 microciclos equivalentes (contexto = equipe, fase/temporada, tipo de microciclo). Até lá, nenhuma sugestão.
- Sugestões não aparecem na sessão; vivem no fluxo de planejamento ao criar/duplicar microciclo. Cards com rótulo e explicação; botões Aplicar | Ignorar; no máximo uma por camada.

5) Níveis de aprendizado e tipos de sugestão
- Nível 1 (por equipe): aprende a partir da própria equipe/temporada; aparece ao criar/duplicar microciclo (“Nos últimos 4 microciclos deste tipo, foco físico executado +12% vs planejado. Ajustar?”).
- Nível 2 (transversal): observa padrões entre equipes da organização (contextualizado, sem citar sessões individuais); usado para coordenação/direção.
- Tipos de sugestão (prioridade): A) focos de treino (percentuais planejados); B) carga semanal (dose: reduzir/aumentar faixa); C) distribuição de tipos de sessão (ex.: manter regenerativo). Aparece no planejamento, nunca no operacional.

6) Regras de governança das sugestões
- Explicabilidade obrigatória (mostrar base histórica e direção do desvio). Nada de “caixa-preta”.
- Nunca prescritivo: aplicar é opcional e totalmente editável depois. Sem contadores de adesão.
- Sem recomendações em nível de sessão individual ou atleta; foco é planejamento de microciclo/mesociclo.
