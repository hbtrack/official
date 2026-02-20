# SPEC_GEN_DOCS_SSOT — scripts/generate/docs/gen_docs_ssot.py (v1.0)

status: SPEC
scope: ssot_generator
outputs_dir: docs/ssot/
evidence_dir: docs/evidence/

1) Objetivo
Este script é o gerador/validador canônico dos SSOTs em docs/ssot/.
Ele MUST suportar:
- generate: gerar SSOT (FS_WRITE permitido)
- validate: regenerar em temp e comparar (FS_WRITE no destino proibido)

2) Autoridade e escopo
2.1. Output canônico MUST ser somente:
- <REPO_ROOT>/docs/ssot/

2.2. O script MUST NOT:
- espelhar/copy SSOT para outros diretórios (backend/docs/ssot, docs/soot, etc.)
- engolir erros críticos com "except: pass"

2.3. SSOTs sob gestão (MUST):
- openapi.json
- schema.sql
- alembic_state.txt

2.4. Evidência (não-SSOT)
- manifest/checksums/timestamps são EVIDÊNCIA.
- EVIDÊNCIA SHOULD ir para docs/evidence/ (ex.: docs/evidence/ssot_manifest.json).
- EVIDÊNCIA MUST NOT ser critério de PASS do gate SSOT_VALIDATE (ela não participa do validate canônico).

3) Interface CLI (MUST)
O script MUST aceitar:
- seleção:
  --all | --openapi | --schema | --alembic
- modo:
  --mode generate|validate   (default: generate)
- profile:
  --profile <string>         (default: vps)
- controle de nondeterminismo:
  --allow-http-fallback      (default: false; FORBIDDEN em validate)

4) Regras por SSOT (MUST)

4.1 openapi.json
- MUST gerar via import (app.openapi()).
- MUST NOT depender de DB.
- MUST NOT depender de backend rodando.
- HTTP fallback:
  - default FORBIDDEN
  - se --allow-http-fallback=true:
    - MAY usar HTTP somente em --mode generate
    - MUST imprimir "NONDETERMINISTIC_PATH=true"
    - MUST falhar em --mode validate (gate canônico)

- MUST serializar determinístico:
  json.dump(..., sort_keys=True, indent=2, ensure_ascii=False) + newline final

4.2 schema.sql
- Fonte: DB canônico da VPS.
- MUST exigir:
  - DATABASE_URL (ou equivalente) disponível no ambiente
  - pg_dump disponível
  - DB acessível
- MUST usar pg_dump schema-only e flags normativas:
  --schema-only --no-owner --no-privileges
- SHOULD usar --no-comments
- MUST NOT inserir header próprio com timestamp.
- MUST NOT produzir conteúdo contendo timestamps ISO-8601.
- MUST NOT depender de backend rodando.

4.3 alembic_state.txt
- MUST exigir alembic instalado no ambiente.
- MUST gerar HEADS (repo) e CURRENT (db).
- MUST aplicar policy single-head:
  - heads_count==1, current_count==1, current==head
- MUST emitir formato parseável conforme CONTRATOS FIXOS HB TRACK — SSOT (v1.0).
- MUST NOT incluir stderr e MUST NOT incluir timestamps (linha "Generated:" é FORBIDDEN).

5) Modo validate (MUST)
Em --mode validate, o script MUST:
1) gerar SSOT(s) solicitado(s) em diretório temporário
2) validar invariantes estruturais do SSOT gerado (conforme contrato SSOT)
3) comparar com o arquivo existente em docs/ssot/:
   - openapi.json: byte-a-byte
   - schema.sql: byte-a-byte
   - alembic_state.txt: byte-a-byte
4) NÃO escrever em docs/ssot/ e NÃO modificar working tree
5) exit code:
   - 0 somente se TODOS passaram e TODOS bateram
   - 1 caso contrário

6) Escrita atômica (MUST)
Em --mode generate:
- MUST escrever via arquivo temporário + rename (atomic replace) para evitar SSOT parcial.
- Se qualquer SSOT falhar, o script MUST sair com exit code 1.

7) Erros determinísticos e stdout (MUST)
O stdout MUST terminar com resumo fixo:
- PASS|FAIL SSOT_OPENAPI
- PASS|FAIL SSOT_SCHEMA
- PASS|FAIL SSOT_ALEMBIC
- PASS|FAIL SSOT_VALIDATE_MATCH  (somente no validate)

Em FAIL, MUST imprimir exatamente um code por SSOT que falhar:
- E_IMPORT_OPENAPI
- E_HTTP_FALLBACK_FORBIDDEN
- E_OPENAPI_INVALID
- E_PGDUMP_MISSING
- E_DB_UNREACHABLE
- E_SCHEMA_VOLATILE
- E_SCHEMA_INVALID
- E_ALEMBIC_MISSING
- E_ALEMBIC_FORMAT_INVALID
- E_MULTIPLE_HEADS
- E_MULTIPLE_CURRENT
- E_DB_NOT_AT_HEAD
- E_MISMATCH_OPENAPI
- E_MISMATCH_SCHEMA
- E_MISMATCH_ALEMBIC

8) Gate canônico habilitado por esta SPEC
Comando:
python scripts/generate/docs/gen_docs_ssot.py --all --mode validate --profile vps

PASS:
- exit 0
- todos PASS no resumo

FAIL:
- exit 1
- code determinístico no stdout