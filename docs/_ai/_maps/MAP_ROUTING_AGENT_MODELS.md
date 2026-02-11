# MAP_ROUTING_AGENT_MODELS.md

## Descrição
Mapa de roteamento para tarefas de models: quando executar qual gate, em que sequência, com que profiles, e critérios de sucesso.

---

## Árvore de Decisão: Qual Gate?

### 1. Diagnosticar (read-only)
```
Pergunta: Preciso saber seu estado do model?
├─ Sim → parity_scan.ps1 -TableFilter <T>
└─ Saída: parity_report.json (sem acesso a schema.sql)
```

### 2. Atualizar Schema (write)
```
Pergunta: Alterei schema.sql ou adicionei coluna?
├─ Sim → inv.ps1 refresh (repo root)
└─ Output: schema.sql atualizado em docs/_generated/
```

### 3. Regenerar Model (write)
```
Pergunta: Preciso fazer autogen de novo?
├─ Sim, e repo está limpo:
│   └─ models_autogen_gate.ps1 -Table <T> -Profile <P>
├─ Sim, mas repo está sujo:
│   └─ git status --porcelain (revisar, commit ou stash)
└─ Saída: model.py atualizado, guard baseline refreshed
```

### 4. Validar (read-only)
```
Pergunta: Qual validação?
├─ Estrutural (DB vs Model)?
│   └─ parity_gate.ps1 (exit=2 se diff)
├─ Regras de negócio?
│   └─ model_requirements.py -Profile <P> (exit=4 se violations)
└─ Drift do baseline?
    └─ agent_guard.py (exit=3 se drift)
```

---

## Profile Decision Table

| Profile | Quando | Ciclos FK | Warnings | Exit=4 Triggers |
|---------|--------|----------|----------|-----------------|
| **strict** | Tabelas normais | Não permitido | Erro | Qualquer violation |
| **fk** | Ciclos de FK conhecidos | Permitido c/ flag | Erro | Violations (excl. ciclos) |
| **lenient** | Debug/experimento | Permitido | Aviso | Apenas erros críticos |

---

## Checklist: Gate Success

- [ ] `git status --porcelain` vazio ANTES
- [ ] Gate executado com exit=0
- [ ] parity_report.json sem DIFFs
- [ ] model.py editado (revisado, não reescrito)
- [ ] Nenhum arquivo temporário deixado
- [ ] baseline.json **não** adicionado ao git

---

## TODO
- [ ] Criar script de auto-selection de profile
- [ ] Documentar quando usar -DryRun
- [ ] Adicionar recovery path se gate travado
