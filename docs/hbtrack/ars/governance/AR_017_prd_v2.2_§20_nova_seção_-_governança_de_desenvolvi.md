# AR_017 — PRD v2.2: §20 nova seção — Governança de Desenvolvimento IA (Determinismo Máximo)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA CRÍTICO: O PRD não documenta o processo de desenvolvimento determinístico baseado em IA, que é a infraestrutura operacional do produto. Para um sistema desenvolvido por IA, a ausência desta documentação cria risco de perda de contexto, decisões inconsistentes e impossibilidade de auditoria. Esta tarefa adiciona a §20 ao PRD.

O Executor deve adicionar a seguinte seção ao FINAL do arquivo (antes de 'FIM DO DOCUMENTO'), após a seção §19:

---
INSERIR O SEGUINTE BLOCO no arquivo docs/hbtrack/PRD Hb Track.md, imediatamente ANTES da linha '---\n\n**FIM DO DOCUMENTO**':

```
---

## 20. Governança de Desenvolvimento IA (Processo Determinístico)

> Este sistema é desenvolvido com assistência de IA. A governança determinística é **peça fundamental** para garantir auditabilidade, rastreabilidade e consistência entre sessões de desenvolvimento.

### 20.1 Princípio de Determinismo

Todo desenvolvimento do HB Track segue o **HBTRACK_DEV_FLOW_CONTRACT** (`docs/_canon/contratos/Dev Flow.md`), que define um processo de 7 passos com evidências obrigatórias. O princípio central: **"chat não é estado"** — nenhuma decisão ou execução existe se não houver evidência persistida em `_reports/`.

### 20.2 Artefatos Canônicos do Processo

| Artefato | Localização | Responsável | Descrição |
|----------|-------------|-------------|----------|
| **PRD** (este documento) | `docs/hbtrack/PRD Hb Track.md` | Arquiteto | Referência de negócio |
| **SSOT Schema** | `docs/ssot/schema.sql` | Sistema | Verdade do banco de dados |
| **SSOT OpenAPI** | `docs/ssot/openapi.json` | Sistema | Contrato da API |
| **SSOT Alembic** | `docs/ssot/alembic_state.txt` | Sistema | Estado das migrações |
| **Plan JSON** | `docs/_canon/planos/*.json` | Arquiteto | Plano de execução (schema-validated) |
| **AR (Architectural Record)** | `docs/hbtrack/ars/AR_NNN_*.md` | Executor | Materialização do plano |
| **AR Index** | `docs/hbtrack/ars/_INDEX.md` | Auto-gerado | Índice de todas as ARs (NÃO editar manualmente) |
| **Evidence Pack** | `docs/hbtrack/evidence/*.log` | Executor | Evidência de validação por AR |
| **Audit Report** | `docs/hbtrack/evidence/<AR_ID>/` | Executor | Evidências estruturadas por AR |

### 20.3 Ciclo de Vida de uma Tarefa (7 Passos)

```
Passo 1 — REFERÊNCIA     Arquiteto lê PRD + SSOT
Passo 2 — PLANO          Arquiteto gera Plan JSON em docs/_canon/planos/
Passo 3 — MATERIALIZAÇÃO python scripts/run/hb_cli.py plan <plan.json> → AR criada
Passo 4 — ANÁLISE        Executor preenche 'Análise de Impacto' na AR
Passo 5 — AÇÃO           Executor implementa no código
Passo 6 — VALIDAÇÃO      python scripts/run/hb_cli.py report <id> "<cmd>"
Passo 7 — FECHAMENTO     git commit → hook pré-commit (hb check) valida tudo
```

### 20.4 Regras de Imutabilidade e Proteção

| Regra | Mecanismo | Enforcement |
|-------|-----------|-------------|
| **ARs SUCESSO são imutáveis** | Pre-commit hook bloqueia edição manual do corpo | `E_AR_IMMUTABLE` |
| **_INDEX.md é auto-gerado** | Gerado por `hb plan`/`hb report` | `E_AR_INDEX_NOT_STAGED` |
| **SSOT não pode ter mudanças unstaged** | Pre-commit hook bloqueia | `E_SSOT_UNSTAGED` |
| **SSOT staged exige AR com evidência** | Pre-commit hook exige AR staged com ✅ SUCESSO | `E_SSOT_NO_VALID_AR` |
| **Código governado exige AR staged** | Pre-commit hook exige ao menos 1 AR | `E_GOVERNED_NO_AR` |

### 20.5 Exit Codes Canônicos

| Código | Status | Significado |
|--------|--------|-------------|
| `0` | PASS | Sucesso — evidência válida |
| `2` | FAIL_ACTIONABLE | Falha lógica/mérito — corrigível |
| `3` | ERROR_INFRA | Erro de infraestrutura (VPS, DB, rede) |
| `4` | BLOCKED_INPUT | Input inválido ou gate inexistente |

### 20.6 CLI de Governança (hb_cli.py)

```bash
python scripts/run/hb_cli.py plan <plan.json>    # Materializa ARs a partir do plano
python scripts/run/hb_cli.py report <id> "<cmd>" # Executa validação e grava evidência
python scripts/run/hb_cli.py check --mode pre-commit  # Valida integridade antes do commit
python scripts/run/hb_cli.py version             # Reporta versão do protocolo
```

**Regra crítica:** Scripts de automação MUST ser Python (`.py`). Arquivos `.sh` e `.ps1` são proibidos.

### 20.7 Anti-padrões Proibidos

- ❌ Marcar tarefa como PASS sem Evidence Pack em `_reports/`
- ❌ Editar AR com Status ✅ SUCESSO manualmente
- ❌ Criar Plan JSON sem validar contra `ar_contract.schema.json`
- ❌ Usar snapshot como evidência de validação
- ❌ Criar automação/infra em `.sh` ou `.ps1`
- ❌ Inventar/alterar policies, gates ou SSOTs por iniciativa própria

### 20.8 Protocolo de Verdade

Nenhum resultado de execução é válido sem Evidence Pack. A fonte de verdade do sistema em qualquer momento é:

1. `docs/ssot/schema.sql` — estado do banco
2. `docs/ssot/openapi.json` — contrato da API
3. `docs/hbtrack/ars/_INDEX.md` — todas as ARs e seus status
4. `docs/hbtrack/evidence/` — evidências de execução

Chat, mensagens e comentários não são estado. Estado vive em arquivos.
```

ARQUIVO A MODIFICAR (ÚNICO): docs/hbtrack/PRD Hb Track.md
Localização de inserção: imediatamente ANTES da linha '---\n\n**FIM DO DOCUMENTO**' (última linha do arquivo).

## Critérios de Aceite
1) PRD contém seção '## 20. Governança de Desenvolvimento IA'. 2) §20 contém subseções 20.1 a 20.8. 3) §20 referencia 'docs/_canon/contratos/Dev Flow.md'. 4) §20 contém tabela de artefatos com Plan JSON, AR, Evidence Pack, Audit Report. 5) §20 contém tabela de exit codes (0, 2, 3, 4). 6) §20 contém a frase 'chat não é estado' ou equivalente. 7) §20 contém os anti-padrões proibidos.

## Validation Command (Contrato)
```
python -c "import pathlib; prd=pathlib.Path('docs/hbtrack/PRD Hb Track.md').read_text(encoding='utf-8'); checks={'sec_20':'## 20.' in prd or '## 20. Governan' in prd,'subsec_20_1':'20.1' in prd,'subsec_20_8':'20.8' in prd,'dev_flow_ref':'Dev Flow' in prd,'exit_codes_0':'exit_code: 0' in prd.lower() or '| `0`' in prd or 'Exit Code: 0' in prd or 'Código | Status' in prd,'anti_patterns':'Anti-padr' in prd or 'Proibidos' in prd,'chat_nao_estado':'chat' in prd.lower() and 'estado' in prd.lower(),'plan_json_ref':'Plan JSON' in prd,'evidence_pack_ref':'Evidence Pack' in prd}; failed=[k for k,v in checks.items() if not v]; [print(f'FAIL: {k}') for k in failed]; exit(len(failed)) if failed else print(f'PASS: PRD §20 Governança IA — {len(checks)} checks OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_017_prd_v22_governance_section.log`

## Rollback Plan (Contrato)
```
git revert HEAD
# OU: git restore "docs/hbtrack/PRD Hb Track.md"
# Verifica rollback: python -c "import pathlib; prd=pathlib.Path('docs/hbtrack/PRD Hb Track.md').read_text(encoding='utf-8'); assert '## 20.' not in prd, 'rollback falhou'; print('PASS rollback: §20 removida com sucesso')"
```
⚠️ **ATENÇÃO**: Este AR modifica banco. Execute rollback em caso de falha.

## Riscos
- A inserção deve ser ANTES de '---\n\n**FIM DO DOCUMENTO**' — não após. Verificar a posição exata com grep antes de inserir.
- O bloco Mermaid-like no Passo 3 (ciclo de vida) usa aspas simples — garantir que o parser de markdown não quebre o código block.
- A seção §20.6 mostra o CLI com comandos exatos — verificar que os comandos batem com hb_cli.py atual (não inventar flags que não existem).
- Não duplicar conteúdo: §20 deve referenciar Dev Flow.md ao invés de replicar o contrato completo.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; prd=pathlib.Path('docs/hbtrack/PRD Hb Track.md').read_text(encoding='utf-8'); checks={'sec_20':'## 20.' in prd or '## 20. Governan' in prd,'subsec_20_1':'20.1' in prd,'subsec_20_8':'20.8' in prd,'dev_flow_ref':'Dev Flow' in prd,'exit_codes_0':'exit_code: 0' in prd.lower() or '| `0`' in prd or 'Exit Code: 0' in prd or 'Código | Status' in prd,'anti_patterns':'Anti-padr' in prd or 'Proibidos' in prd,'chat_nao_estado':'chat' in prd.lower() and 'estado' in prd.lower(),'plan_json_ref':'Plan JSON' in prd,'evidence_pack_ref':'Evidence Pack' in prd}; failed=[k for k,v in checks.items() if not v]; [print(f'FAIL: {k}') for k in failed]; exit(len(failed)) if failed else print(f'PASS: PRD §20 Governança IA — {len(checks)} checks OK')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_017_prd_v22_governance_section.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_017_b2e7523/result.json`
