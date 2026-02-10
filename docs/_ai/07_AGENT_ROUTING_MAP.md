# docs/_canon/07_AGENT_ROUTING_MAP.md

| Propriedade | Valor |
|---|---|
| ID | CANON-AGENT-ROUTING-007 |
| Status | CANÔNICO |
| Última verificação | 2026-02-09 (America/Sao_Paulo) |
| Porta de entrada | docs/_canon/00_START_HERE.md |
| Objetivo | Mapear “ação → instruções carregadas → docs canônicos → comandos” |

# Mapa Canônico: Ação → Instruções do Agent → Documentação a Usar

Este documento define, para cada ação típica no Hb Track, quais:
1) **Instruções** devem estar presentes em `.github/instructions/`
2) **Documentos canônicos** devem ser usados como SSOT
3) **Comandos** (quando aplicável) são os aprovados

---

## 1) Arquivos de instruções (camadas)

Recomendado manter 3 instruções:

1) `.github/instructions/00_general.instructions.md`
- Carrega sempre (`applyTo: "**/*"`)
- Porta única, SSOT e regras globais (sem temporários, capturar exit code, etc.)

2) `.github/instructions/10_models_gate.instructions.md`
- Carrega quando envolve models/gate/baseline/parity/requirements
- Regras determinísticas do pipeline de models

3) `.github/instructions/20_docs.instructions.md`
- Carrega quando envolve docs (canon/ADR/guides/changelog/executionlog)

---

## 2) Documentação canônica (SSOT de operação)

- `docs/_canon/00_START_HERE.md` — porta única e “como navegar”
- `docs/_canon/01_AUTHORITY_SSOT.md` — precedência e SSOT
- `docs/_canon/05_MODELS_PIPELINE.md` — pipeline models (guard → parity → requirements)
- `docs/_canon/06_AGENT_PROMPTS_MODELS.md` — prompts prontos (detectar/corrigir/baseline/docs)
- `docs/_canon/07_AGENT_ROUTING_MAP.md` — este documento (ação → rota)

---

## 3) Mapa: ação → instrução → docs → execução

### A) “Entender o projeto / começar uma tarefa”
**Quando:** qualquer dúvida geral, onboarding, entender SSOT, onde mexer.  
**Instruções carregadas:** `00_general`  
**Docs canônicos:**  
- `docs/_canon/00_START_HERE.md`  
- `docs/_canon/01_AUTHORITY_SSOT.md`  

**Regra:** sempre começar pelo 00_START_HERE e só depois abrir arquivos específicos.

---

### B) “Varredura: detectar quais models estão OK/FAIL”
**Quando:** você tem lista de tabelas e quer triagem PASS/FAIL sem alterar models.  
**Instruções carregadas:** `00_general` + `10_models_gate`  
**Docs canônicos:**  
- `docs/_canon/05_MODELS_PIPELINE.md` (seção DETECTAR)  
- `docs/_canon/06_AGENT_PROMPTS_MODELS.md` (Prompt A)  

**Comandos aprovados (resumo):**
1) `git status --porcelain` (deve estar vazio)
2) `inv.ps1 refresh` (1 vez)
3) `venv\Scripts\python.exe scripts\model_requirements.py --table <T> --profile strict`

**Saída esperada:** tabela PASS/FAIL por tabela; sem sujar o repo.

---

### C) “Corrigir models que falharam (somente FAIL)”
**Quando:** após varredura, corrigir apenas tabelas FAIL.  
**Instruções carregadas:** `00_general` + `10_models_gate`  
**Docs canônicos:**  
- `docs/_canon/05_MODELS_PIPELINE.md` (seção CORRIGIR)  
- `docs/_canon/06_AGENT_PROMPTS_MODELS.md` (Prompt B)  

**Regra crítica:** corrigir **1 tabela por vez**; parar na primeira falha.

**Comandos aprovados (resumo):**
- `.\scripts\models_autogen_gate.ps1 -Table "<T>" -Profile strict`
- Para ciclos (quando aplicável): `-Profile fk -AllowCycleWarning`
- Limpar gerados com `git restore` após validar.

---

### D) “Atualizar baseline do guard (snapshot)”
**Quando:** você fez mudanças intencionais e quer “promover” o novo estado como baseline.  
**Instruções carregadas:** `00_general` + `10_models_gate`  
**Docs canônicos:**  
- `docs/_canon/05_MODELS_PIPELINE.md` (política de baseline)  
- `docs/_canon/06_AGENT_PROMPTS_MODELS.md` (Prompt C)  

**Regra:** snapshot só com autorização explícita.

**Comando canônico:**
```powershell
& "venv\Scripts\python.exe" scripts\agent_guard.py snapshot `
  --root "." `
  --out ".hb_guard/baseline.json" `
  --exclude "venv,.venv,__pycache__,.pytest_cache,docs\_generated"
````

Depois: commit separado do baseline.

---

### E) “Atualizar CHANGELOG / EXECUTIONLOG”

**Quando:** fechar um lote (após gates OK) e registrar execução.
**Instruções carregadas:** `00_general` + `20_docs`
**Docs canônicos:**

* `docs/_canon/05_MODELS_PIPELINE.md` (política: docs só no final)
* (se existirem) `docs/adr/architecture/CHANGELOG.md`, `EXECUTIONLOG.md`

**Regra:** nunca durante varredura/correção automática. Fazer no final, commit separado.

---

### F) “Criar/atualizar documentação canônica (_canon)”

**Quando:** criar guias, runbooks, mapear intenções/fluxos.
**Instruções carregadas:** `00_general` + `20_docs`
**Docs canônicos:**

* `docs/_canon/00_START_HERE.md`
* `docs/_canon/01_AUTHORITY_SSOT.md`

**Regra:** docs canônicos devem apontar para SSOT e não duplicar conteúdo volátil.

---

### G) “Abrir PR / fluxo Git”

**Quando:** subir mudanças e abrir PR.
**Instruções carregadas:** `00_general` (e `20_docs` se PR de docs)
**Docs canônicos:**

* (opcional) convenções internas do repo

**Regra:** commits pequenos por intenção. PR pelo `gh` ou navegador.

---

## 4) Quick Reference (tabela rápida)

| Ação                             | Instruções                  | Doc(s) principal(is)                     |
| -------------------------------- | --------------------------- | ---------------------------------------- |
| Onboarding / entender SSOT       | 00_general                  | 00_START_HERE, 01_AUTHORITY_SSOT         |
| Detectar PASS/FAIL (scan)        | 00_general + 10_models_gate | 05_MODELS_PIPELINE, 06_AGENT_PROMPTS (A) |
| Corrigir FAIL                    | 00_general + 10_models_gate | 05_MODELS_PIPELINE, 06_AGENT_PROMPTS (B) |
| Atualizar baseline               | 00_general + 10_models_gate | 05_MODELS_PIPELINE, 06_AGENT_PROMPTS (C) |
| Atualizar changelog/executionlog | 00_general + 20_docs        | 05_MODELS_PIPELINE + docs/adr/...        |
| Criar docs canônicos             | 00_general + 20_docs        | 00_START_HERE, 01_AUTHORITY_SSOT         |

---

## 5) Política anti-“tentativa e erro” do agent

Para tarefas operacionais (PowerShell/Git):

* usar comandos canônicos,
* capturar `$LASTEXITCODE` imediatamente,
* stop-on-first-failure,
* não inventar variações.

Para análise:
* explicar hipótese e pedir evidência (paths/output) quando necessário.

