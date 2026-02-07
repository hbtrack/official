Fluxo “canônico” para o agente analisar e fechar pendências das invariantes (sem suposições, só com evidência).
“gerar fontes de verdade → extrair → comparar → fechar pendência → revalidar”.

1. Atualizar fontes de verdade (sempre primeiro)
   Objetivo: garantir que o agente está lendo o estado real do sistema.

* Rodar o script `docs\scripts\run_training_docs_checks.py` para gerar/atualizar: 
  
  Em `Hb Track - Backend/docs/_generated/`
  * `openapi.json` (contratos)
  * `schema.sql` (tabelas/constraints/triggers)
  * `alembic_state.txt` (estado migrations)
  * `manifest.json` (checksum/rastreabilidade, se você usa)
    Saída: esses arquivos viram a base de tudo. Sem isso, o agente só “acha”.

  Em `docs/_generated/`
  * `trd_training_openapi_operationIds.txt` operationIds do OpenAPI (Training scope) 
  * `trd_training_trd_operationIds.txt` operationIds citados no TRD
  * `trd_training_schema_tables.txt` tabelas do schema (Training scope) 
  * `trd_training_trd_tables.txt` tabelas citadas no TRD
  * `trd_training_verification_report.txt` tabelas + operationIds (Training scope) x TRD
  * `trd_training_permissions_report.txt` permissões mapeadas (Training scope endpoints)
      

2. Revisar pendências das invariantes com método (uma a uma)
   Objetivo: para cada invariante pendente, classificar e fechar com evidência.
   Para cada item em `INVARIANTS_TRAINING.md`, o agente faz:

* Procurar evidência no `schema.sql`
(constraint/trigger/function) OU no código (service:linha).
* Classificar a pendência:
  A) “Já existe” → só faltava evidência (vira CONFIRMADA com file:line / constraint).
  B) “Não existe” → é regra desejada (vira BACKLOG de implementação + teste).
  C) “Não deveria existir” → doc/spec estava errada (corrige texto e encerra).
  Saída: cada pendência vira “fechada” (A/C) ou “vira tarefa” (B).

3. Atualizar `INVARIANTS_TRAINING.md` (e só o que for necessário no TRD)
   Objetivo: transformar achados em documentação utilizável por IA.

* Para cada invariante:

  * Status (CONFIRMADA / PRETENDIDA / BACKLOG)
  * Onde é imposta (DB constraint / trigger / service validation)
  * Evidência objetiva (nome da constraint OU arquivo:linha)
  * Teste associado (ou GAP explícito)
  * Se a invariante impacta mapeamento PRD-FR, atualizar o TRD (Evidence Ledger / seção do FR) com a mesma âncora.

3.1 Produzir um “Invariants Status Report” (controle de progresso, não só texto)
   Objetivo: deixar claro, de forma auditável, o que está CONFIRMADO vs PRETENDIDO vs BACKLOG.


4. Transformar pendências B em tarefas de implementação + teste (Definition of Done objetiva)
   Objetivo: cada pendência que “não existe” virar uma ação concreta com critério de aceite.

Para cada pendência do tipo B (implementação faltando), o agente cria um “cartão” com:
* Onde implementar (DB constraint? service validation? ambos?)
* Onde testar (unit/integration/e2e) e qual nome do teste
* Evidência esperada ao final (constraint X OU file:line + teste Y)

5. Revalidar e “fechar o ciclo” (não termina sem isso)
   Objetivo: garantir que nada ficou incoerente depois das edições.

* Rodar de novo:

  * geração dos `_generated/` (se mexeu em código/DB)
  * scripts de verificação (o report tem que bater)
  * testes (se você adicionou/alterou validações)
    Saída: commit com docs + evidências + (se aplicável) testes.

  Regra simples de “Definition of Done” para uma invariante
  Só considere “pendência resolvida” quando tiver:

* 1 âncora verificável (constraint/trigger OU file:linha), e
* 1 teste mapeado (ou GAP escrito explicando por que ainda não tem).
  E só depois disso atualizar o `INVARIANTS_TRAINING.md` marcando “BACKLOG” com essas referências.
