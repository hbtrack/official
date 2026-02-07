# HB Track — Regras gerais (sempre)

- Não invente: antes de sugerir ou editar, leia arquivos reais e cite quais arquivos/trechos sustentam a decisão.
- Se faltar informação crítica, pare e liste exatamente o que falta (sem chute).
- Mudanças pequenas: 1 objetivo por rodada, com lista de arquivos alterados.
- Ao finalizar: diga como validar e onde ver o resultado.

## PROTOCOLO MANDATÓRIO — TESTES DE INVARIANTES (HB TRACK / TRAINING)

Autoridade:

* Você está ESTRITAMENTE VINCULADO ao arquivo `docs/02-modulos/training/INVARIANTS_TESTING_CANON.md`.
* A lista de trabalho é `docs/02-modulos/training/INVARIANTS_TRAINING.md`.
* Artefatos canônicos de referência: `Hb Track - Backend/docs/_generated/schema.sql`, `Hb Track - Backend/docs/_generated/openapi.json`, `Hb Track - Backend/docs/_generated/alembic_state.txt`, `Hb Track - Backend/docs/_generated/manifest.json`.
* É PROIBIDO inventar campos, tabelas, constraints, enums, endpoints, nomes de erro, ou regras não ancoradas.

Regra de Engajamento (workflow obrigatório):

1. Construir Worklist (sem escrever teste ainda)

   * Ler `INVARIANTS_TRAINING.md` e listar todas as invariantes com:
     a) ID (ex: INV-TRAIN-037)
     b) enunciado
     c) evidência (arquivo + símbolo/constraint; linha opcional)
   * Classificar cada invariante nas classes A/B/C1/C2/D/E1/E2/F usando a Matriz do Canon.
   * Se faltar evidência ou estiver ambígua, marcar como PENDING (não codar).

2. Pré-codificação obrigatória (por invariante)
   Antes de escrever qualquer arquivo de teste, emitir:

   * Obrigação A: requisitos de inserção/setup ancorados no schema (Tabela + Coluna + Constraint/Enum) OU no model quando a classe não for DB.
   * Obrigação B: critério de falha (Classe de violação/SQLSTATE + constraint_name quando exposto; para Service/RBAC/OpenAPI, o critério canônico equivalente).
     Se não conseguir preencher A e B, parar e marcar PENDING.

3. Geração do teste (exatamente 1 por invariante)

   * Criar o arquivo em `tests/invariants/test_inv_train_XXX_<slug>.py` e classe `TestInvTrainXXX<Slug>`.
   * Docstring deve conter a evidência estável (Arquivo + Símbolo/Constraint/OperationId).
   * Seguir DoD-3 a DoD-7 do Canon: payload mínimo, anti-falso-positivo, sensibilidade (mínima violação específica), isolamento de sessão.

4. Regras por classe (resumo operacional)

   * A (DB Constraint): Runtime Integration com `async_db`. 1 caso válido + 2 inválidos. Validar SQLSTATE + constraint_name quando exposto. Proibido depender de mensagem humana.
   * B (Trigger/Function): Runtime Integration com `async_db`. Provar efeito colateral/estado.
   * C1 (Service puro): Unit sem IO. Exceção de negócio.
   * C2 (Service com DB): Integration com `async_db`, sem mock de DB. Provar exceção de negócio (não “erro do banco” como regra principal).
   * D (Router/RBAC): API test com `client` (401) e `auth_client` (403/200). Evidência mínima: router + permission guard + fonte de mapeamento.
   * E1/E2 (Celery): chamada direta. E2 valida estado no DB.
   * F (OpenAPI): contract test lendo `openapi.json` e validando JSON Pointers específicos; não usar DB fixtures.

5. Saída obrigatória da execução
   Ao final, produzir um “Relatório de Cobertura” contendo:

   * Lista de invariantes: {ID, classe, arquivo de teste criado, evidência usada}
   * Lista PENDING: {ID, motivo objetivo, evidência faltante}
   * Confirmação de conformidade com: DoD-0..DoD-9 (sim/não) por arquivo.

Regras de parada (anti-alucinação):

* Se `schema.sql`/`openapi.json` não contiver a âncora mencionada na invariante, NÃO INVENTE. Marque PENDING e peça o artefato atualizado.
* Não executar refactors fora do escopo: apenas criar/atualizar testes em `tests/invariants/`.

---

