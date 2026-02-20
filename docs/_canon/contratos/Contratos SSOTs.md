# CONTRATOS FIXOS HB TRACK — SSOT (v1.0)

0. Definições
SSOT (Single Source of Truth): artefato DERIVED (gerado) que define a verdade canônica de um aspecto do sistema.
EVIDÊNCIA: logs/manifestos/artefatos voláteis (timestamps, checksums, commit hash) usados para auditoria, mas não são SSOT.

1. Diretório canônico e paths permitidos
1.1. SSOT_DIR_CANONICO MUST ser:
- docs/ssot/

1.2. O diretório docs/soot/ é FORBIDDEN.
Exceção (MAY): se existir symlink docs/soot -> docs/ssot (mesmo filesystem) e isso for comprovado por evidência, pode ser tratado como alias. Sem symlink, é FAIL.

1.3. Lista canônica de SSOTs (nomes fixos)
Os SSOTs do projeto MUST ser exatamente:
- docs/ssot/openapi.json
- docs/ssot/schema.sql
- docs/ssot/alembic_state.txt

Qualquer SSOT adicional MUST ser declarado explicitamente neste documento (não por convenção implícita).

2. Regras globais aplicáveis a todos os SSOTs
2.1. Origem e edição
- Todos os SSOTs acima MUST ser DERIVED (gerados por script).
- Edição manual direta é FORBIDDEN.
- Validação oficial MUST ser: regenerar e comparar contra o versionado (com regras de comparação explicitadas neste contrato).

2.2. Encoding e newline
- MUST ser UTF-8.
- MUST usar '\n' como newline.
- MUST terminar com newline final.

2.3. Determinismo de conteúdo
- SSOT MUST NOT conter conteúdo volátil (timestamps, paths locais, PID, “generated at”, commit hash, checksums).
- Se algum campo volátil for inevitável, o contrato MUST definir a regra exata e limitada de comparação (ex.: “ignorar somente a linha X”). Sem regra explícita, o SSOT é inválido.

2.4. Segurança
- SSOT MUST NOT conter segredos (tokens, senhas, DATABASE_URL com senha, etc.).
- O gerador MUST NOT imprimir segredos no stdout/stderr.

3. CONTRATO: docs/ssot/openapi.json
3.1. Finalidade
Representar o contrato público das APIs do backend (OpenAPI 3.x), de forma determinística.

3.2. Geração (pré-condições)
- MUST ser gerado via import da app (ex.: app.openapi()).
- MUST NOT depender de backend rodando.
- MUST NOT depender de DB.
- HTTP fallback é FORBIDDEN no gate canônico. Se habilitado por flag explícita, MUST marcar como NONDETERMINISTIC e MUST falhar no modo validate canônico.

3.3. Invariantes de formato (MUST)
- JSON válido.
- Campo "openapi" iniciando com "3.".
- Campo "paths" existente (objeto/dict).
- SHOULD conter "components" (objeto/dict; pode estar vazio).
- Serialização determinística MUST:
  - sort_keys=true
  - indent=2
  - ensure_ascii=false
  - newline final

3.4. Validação (PASS/FAIL)
PASS se e somente se:
- JSON válido e invariantes estruturais verdadeiras; e
- comparação com o gerado (modo validate) resultar em MATCH (ver seção 6).

4. CONTRATO: docs/ssot/schema.sql
4.1. Finalidade
Representar a estrutura do banco (DDL) como verdade de schema.

4.2. Fonte de verdade
- Fonte: dump do DB canônico (VPS).
- Logo, gerar schema.sql MUST exigir DB acessível.

4.3. Geração (pré-condições)
- MUST exigir pg_dump disponível.
- MUST exigir conexão ao DB canônico via DATABASE_URL (ou equivalente definida no config.py/.env).
- MUST NOT exigir backend rodando.

4.4. Comando canônico (normativo)
schema.sql MUST ser derivado de comando equivalente a:
- pg_dump --schema-only --no-owner --no-privileges --no-comments ...

4.5. Invariantes de determinismo (MUST)
- O gerador MUST NOT inserir headers próprios com timestamp (ex.: “-- Schema dump generated: <timestamp>” é FORBIDDEN).
- O arquivo MUST NOT conter timestamps (heurística proibida; regra objetiva):
  - MUST NOT conter padrões ISO-8601 (ex.: 2026-02-20T03:01:05Z).
- MUST preservar apenas DDL (sem dados).
- MUST terminar com newline final.

4.6. Validação (PASS/FAIL)
PASS se e somente se:
- arquivo existe e size > 0; e
- atende invariantes acima; e
- comparação com o gerado (modo validate) resultar em MATCH (ver seção 6).

5. CONTRATO: docs/ssot/alembic_state.txt
5.1. Finalidade
SSOT do estado de migrações: compara HEADS do repo vs CURRENT aplicado no DB (tabela alembic_version).

5.2. Política adotada (cenário atual)
- Política MUST ser single-head.
- Profile MUST ser vps (DB canônico único).

5.3. Estrutura obrigatória (parseável)
O arquivo MUST conter, nesta ordem, os blocos abaixo. Marcadores `=== ... ===` são literais.

=== ALEMBIC META ===
profile: <string>
script_location: <string>
version_table: <string>
python: <string>
alembic: <string>

=== ALEMBIC HEADS (REPO) ===
<rev_id_1>
<rev_id_2>
...

=== ALEMBIC CURRENT (DB) ===
<rev_id_db_1>
<rev_id_db_2>
...

=== DERIVED CHECKS ===
db_reachable: true|false
repo_heads_count: <int>
db_current_count: <int>
db_at_head: true|false

5.4. Regras de conteúdo (MUST)
- HEADS e CURRENT MUST conter apenas revision ids hex, 1 por linha, sem sufixos (“(head)” é FORBIDDEN).
- STDERR MUST NOT ser embutido no SSOT.
- Listas MUST estar em ordem lexicográfica ascendente quando houver múltiplos.

5.5. Invariantes (PASS/FAIL) — single-head
- repo_heads_count == 1
- db_reachable == true
- db_current_count == 1
- db_at_head == true
- CURRENT[0] == HEADS[0]

5.6. Modo offline
Para este projeto, modo offline para alembic_state.txt é FORBIDDEN no gate canônico.

5.7. Timestamp
Para manter validação byte-a-byte, alembic_state.txt MUST NOT conter timestamp.
Linha "Generated:" é FORBIDDEN (timestamp pertence a EVIDÊNCIA, não ao SSOT).

6. Comparação e validação canônica (regra executável)
6.1. Método oficial de validação MUST ser:
- regenerar em diretório temporário; validar invariantes; comparar com docs/ssot/ (byte-a-byte).

6.2. Exceções de comparação
- Nenhuma exceção é permitida nesta versão (v1.0).
Se no futuro quiser exceção (ex.: ignorar linha X), isso MUST virar regra explícita nesta seção e ser implementado no gerador.

7. Regras de atualização (triggers)
- Mudanças em rotas/handlers/schemas que afetem OpenAPI -> MUST regenerar openapi.json
- Mudanças em migrações/alembic config/schema real do DB -> MUST regenerar schema.sql e alembic_state.txt
- Mudanças em migrations/versions/*, alembic.ini, migrations/env.py -> MUST regenerar alembic_state.txt e MUST manter db_at_head=true

8. Gate canônico (mínimo)
8.1. Gate: SSOT_VALIDATE_VPS
Comando:
python scripts/generate/docs/gen_docs_ssot.py --all --mode validate --profile vps

PASS:
- exit code 0
- stdout com PASS de todos SSOTs solicitados

FAIL:
- exit code 1
- stdout com código determinístico (ver SPEC do gerador)