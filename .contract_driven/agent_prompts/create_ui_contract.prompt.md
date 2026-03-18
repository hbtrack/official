
## Prompt Operacional — Criar/atualizar contrato de UI (por módulo)

**Objetivo**: criar `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md` e, quando necessário, `SCREEN_MAP_<MODULE>.md`, mantendo alinhamento com OpenAPI.

### Leitura mínima obrigatória (ordem)
1. `.contract_driven/CONTRACT_SYSTEM_RULES.md`
2. `.contract_driven/CONTRACT_SYSTEM_LAYOUT.md`
3. `docs/_canon/UI_CONTRACT_GUIDE.md`
4. `contracts/openapi/openapi.yaml` + `contracts/openapi/paths/<module>.yaml`
5. docs do módulo (README/MODULE_SCOPE/DOMAIN_RULES/INVARIANTS)

### Bloqueios (falhar cedo)
- Se `module` não existir no LAYOUT: **bloquear** com `BLOCKED_MISSING_MODULE`.
- Se não existir UI real (tela/form): **não criar** UI_CONTRACT (artefato condicional).
- Se o contrato de UI depender de endpoint inexistente no OpenAPI: **bloquear** com `BLOCKED_MISSING_CANON_ARTIFACT`.

---

### Fase de Benchmark Competitivo (obrigatória antes de qualquer decisão de tela)

**Esta fase é executada ANTES de apresentar opções ao humano para cada decisão de UI relevante.**

Assuma o papel de arquiteto de software especialista em Design UX/UI de plataformas esportivas.

**Procedimento:**

1. **Identificar o contexto de mercado** do módulo atual:
   - Para módulos de treinamento/performance (`training`, `wellness`, `medical`): referenciar plataformas líderes em gestão esportiva profissional (ex.: Hudl, Catapult, Kinexon, Teamworks, SportsCode, Coach Logic, Metrifit, Coach's Eye).
   - Para módulos de competição/scouts (`competitions`, `matches`, `scout`): referenciar plataformas de análise tática e scouting (ex.: Wyscout, InStat, Hudl Sportscode, StatsPerform, Opta).
   - Para módulos de gestão e acesso (`users`, `teams`, `seasons`, `identity_access`): referenciar sistemas de gestão de clubes e federações (ex.: Sportserv, Engage Sports, Sport80, LeagueApps).
   - Para módulos transversais (`analytics`, `reports`, `notifications`, `audit`, `ai_ingestion`): referenciar as melhores práticas dos líderes acima + ferramentas especializadas (ex.: Tableau para analytics, Amplitude para comportamento de usuário).

2. **Para cada decisão de tela a ser apresentada**, identificar:
   - O que as plataformas líderes de mercado fazem (padrão consolidado).
   - Quais dessas decisões são responsáveis pela posição de mercado que ocupam.
   - Onde existe espaço para o HB Track superar esses padrões (diferenciação competitiva).

3. **Formato obrigatório das opções ao humano** (substituir o formato genérico de "3 opções"):

```
📊 O que o mercado faz hoje:
[Descrever o padrão dominante nas plataformas líderes, em linguagem de produto]

🎯 3 caminhos para o HB Track:
A) Seguir o mercado — [o que as líderes fazem, por que funciona]
B) Evoluir o padrão — [versão melhorada do padrão de mercado, com diferencial]
C) Superar o mercado — [decisão que nenhuma líder tomou ainda, mas que resolve o problema de forma superior]

⭐ Recomendação: [opção] — [motivo em linguagem de produto, conectado ao que as líderes NÃO oferecem]
```

4. **Critérios de qualidade do benchmark:**
   - A análise deve ser específica para o domínio do módulo (não genérica).
   - A recomendação deve sempre apontar para diferenciação, não para paridade.
   - Se o módulo for de handebol especificamente, considerar também soluções específicas para esportes coletivos europeus.

---

### Regras
- UI_CONTRACT deve listar: telas/fluxos, estados (loading/empty/error/success), ações do usuário e os endpoints/operationIds correspondentes.
- Nenhum detalhe de API é inferido: a UI referencia apenas o que existe em OpenAPI.
- Toda decisão de tela registrada no UI_CONTRACT deve ter sua opção escolhida rastreável ao benchmark competitivo (campo `benchmark_basis` no contrato).
- Usar templates SSOT quando aplicável:
  - `.contract_driven/templates/modulos/UI_CONTRACT_{{MODULE_NAME_UPPER}}.md`
  - `.contract_driven/templates/modulos/SCREEN_MAP_{{MODULE_NAME_UPPER}}.md`
- Header YAML canônico é obrigatório (ver `.contract_driven/templates/modulos/snippets/module_human_docs_header.yaml`, referenciado por `.contract_driven/GLOBAL_TEMPLATES.md` seção 3).

### Saída
- `docs/hbtrack/modulos/<module>/UI_CONTRACT_<MODULE>.md` (quando aplicável) — com campo `benchmark_basis` em cada decisão de tela.
- `docs/hbtrack/modulos/<module>/SCREEN_MAP_<MODULE>.md` (quando aplicável).
