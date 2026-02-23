Aqui vai um Plan JSON de teste com 2 tasks (1 não-DB, 1 DB), já no formato do schema v1.2.0 (plan.version = schema_version) e com `rollback_plan` whitelist-only. O `evidence_file` está omitido (hb_cli deve preencher determinísticamente para `docs/hbtrack/evidence/AR_<id>/executor_main.log`).

Cole como, por exemplo: `docs/_canon/planos/smoke_protocol_1_2_0.json`

```json
{
  "project": "HB Track",
  "version": "1.2.0",
  "notes": "SMOKE TEST — Protocol v1.2.0 / schema_version 1.2.0. Objetivo: validar plan->report->verify->seal->check com evidence determinístico, rollback whitelist e enforcement de stage.",
  "assumptions": [
    "Workspace limpo antes de hb verify (hard fail se sujo).",
    "hb plan preencherá evidence_file determinístico (executor_main.log)."
  ],
  "tasks": [
    {
      "id": "001",
      "title": "Smoke: alterar um arquivo doc e validar determinismo do fluxo",
      "description": "Mudança mínima e inofensiva para exercitar o pipeline. O Executor deve editar APENAS um arquivo de documentação não-SSOT (ex.: docs/hbtrack/SMOKE_NOTE.md) adicionando uma linha com timestamp ISO (mas cuidado: timestamp deve ficar no conteúdo do arquivo, não no stdout do comando).",
      "criteria": "PASS se: (1) arquivo docs/hbtrack/SMOKE_NOTE.md existe e contém a string 'SMOKE_PROTOCOL_1_2_0_OK'; (2) hb report exit 0 e gerou evidence canônico; (3) hb verify PASS com triple_consistency OK; (4) hb seal promove ✅ VERIFICADO; (5) hb check --mode pre-commit PASS.",
      "gate": "SMOKE_DOC_FLOW",
      "validation_command": "python -c \"from pathlib import Path; p=Path('docs/hbtrack/SMOKE_NOTE.md'); assert p.exists(), 'missing'; t=p.read_text(encoding='utf-8'); assert 'SMOKE_PROTOCOL_1_2_0_OK' in t, 'marker missing'; print('OK')\"",
      "ssot_touches": [],
      "notes": "Executor: criar/editar apenas docs/hbtrack/SMOKE_NOTE.md e inserir a linha: SMOKE_PROTOCOL_1_2_0_OK",
      "risks": [
        "Não imprimir timestamps no stdout do validation_command para não causar flaky output."
      ]
    },
    {
      "id": "002",
      "title": "Smoke DB: marcar ssot_touches de schema e validar rollback whitelist",
      "description": "Task de banco simulada para testar: detecção de DB task, obrigatoriedade de rollback_plan e whitelist estrita. Não executar TRUNCATE real em produção. O Executor deve tocar o schema.sql de forma controlada (ex.: adicionar um comentário) apenas para exercitar o gate SSOT-touch + rollback + seal.",
      "criteria": "PASS se: (1) docs/ssot/schema.sql staged com alteração controlada (comentário); (2) rollback_plan passa whitelist; (3) hb report exit 0 e evidence canônico gerado; (4) hb verify PASS e TESTADOR_REPORT staged; (5) hb seal promove ✅ VERIFICADO; (6) hb check --mode pre-commit PASS.",
      "gate": "SMOKE_DB_ROLLBACK_WHITELIST",
      "validation_command": "python -c \"from pathlib import Path; p=Path('docs/ssot/schema.sql'); assert p.exists(), 'missing'; t=p.read_text(encoding='utf-8'); assert 'SMOKE_DB_PROTOCOL_1_2_0_OK' in t, 'marker missing'; print('OK')\"",
      "ssot_touches": [
        "docs/ssot/schema.sql"
      ],
      "rollback_plan": "git checkout -- docs/ssot/schema.sql",
      "notes": "Executor: adicionar um comentário no final de docs/ssot/schema.sql contendo: SMOKE_DB_PROTOCOL_1_2_0_OK. Não alterar SQL funcional; apenas comentário.",
      "risks": [
        "Esta task toca SSOT. Só selar após verify PASS + artifacts staged."
      ]
    }
  ]
}
```

Observações rápidas (para evitar falha por motivo “bobo”):

* O `validation_command` imprime sempre “OK” e não depende de timestamps em stdout (evita FLAKY_OUTPUT).
* A task DB usa rollback_plan whitelist-only (`git checkout -- file`).
* A task DB toca `docs/ssot/schema.sql` apenas com comentário para você testar o enforcement SSOT-touch + seal.
* Se seu `hb plan` ainda exigir `evidence_file` no schema (não opcional), você deve atualizar o schema ou adicionar `evidence_file` explícito em cada task. Se precisar, eu te mando a versão com `evidence_file` preenchido.

Se quiser maximizar determinismo, rode o smoke test em ordem:

1. `hb plan ... --dry-run`
2. `hb plan ...`
3. executar Task 001 completa (report→verify→seal→check)
4. executar Task 002 completa (report→verify→seal→check)
