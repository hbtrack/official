# AR_021 — Dual Executor Contract: protocolo de 2 agentes Executores paralelos

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
PROBLEMA: Hoje 1 único Executor processa ARs em série enquanto outros agentes ficam completamente ociosos. Com 9 ARs pendentes (010-012, 016-020), o gargalo é o Executor único.

SOLUÇÃO: Protocolo formal de 2 Executores paralelos com partição estática de domínio de arquivos.

FIX: Criar arquivo docs/_canon/contratos/Dual Executor Contract.md com o seguinte conteúdo exato:

---INÍCIO DO CONTEÚDO---
# Dual Executor Contract
> version: 1.0
> protocolo: v1.0.6+
> canon: docs/_canon/contratos/Dev Flow.md
> criado: 2026-02-20

## 1. Rationale

Com múltiplas ARs pendentes cujos domínios de arquivo são disjuntos, é possível executar 2 agentes Executores em paralelo, cada um em sua própria branch Git, reduzindo o tempo total de execução em aproximadamente 50%.

Paralelismo ocorre ENTRE executores. Dentro de cada executor, as ARs são executadas em ordem sequencial conforme definido no batch assignment.

## 2. Partição de Domínios (File Ownership)

Regra fundamental: cada arquivo modificado em um batch MUST pertencer a exatamente 1 executor. Nenhum arquivo pode aparecer no domínio de ambos os executores no mesmo batch.

Domínios canônicos padrão (podem ser redefinidos por batch via BATCH YAML):

| Domínio | Executor Padrão | Arquivos Típicos |
|---|---|---|
| CLI/Infra | Executor A | scripts/run/hb_cli.py, docs/_canon/contratos/Dev Flow.md |
| Docs/Specs | Executor B | docs/hbtrack/*.md, docs/_canon/specs/*.md, docs/_canon/contratos/ (exceto Dev Flow.md) |

Conflito de merge após execução = violação de File Ownership = falha de governança.

## 3. Branch Protocol

Para cada batch (identificado por NNN, ex: 001, 002):
- Executor A trabalha em: `executor-a/batch-<NNN>`
- Executor B trabalha em: `executor-b/batch-<NNN>`
- Base: branch principal informada no BATCH YAML (campo `base_branch`)

Cada executor MUST criar sua branch a partir do MESMO base_commit definido no BATCH YAML. Os executores trabalham de forma INDEPENDENTE — sem rebases entre si durante a execução.

## 4. Assignment Manifest (BATCH_NNN)

Antes de iniciar qualquer execução, o Arquiteto define o batch em:
`docs/_canon/agentes/BATCH_<NNN>_exec_assignments.yaml`

Formato obrigatório:
```yaml
batch_id: BATCH_<NNN>
base_branch: <branch>
base_commit: <hash>  # hash exato no momento de iniciar
created_at: <ISO date>
protocol_ref: docs/_canon/contratos/Dual Executor Contract.md

executor_a:
  branch: executor-a/batch-<NNN>
  ar_sequence: [<id1>, <id2>, ...]
  file_ownership:
    - <path1>
    - <path2>
  notes: <observações sobre dependências internas>

executor_b:
  branch: executor-b/batch-<NNN>
  ar_sequence: [<id1>, <id2>, ...]
  file_ownership:
    - <path1>
    - <path2>
  notes: <observações sobre dependências internas>

file_ownership_conflict_check:
  shared_files: []  # MUST ser vazio — qualquer arquivo aqui é violação de governança

completion_signals:
  executor_a: 'BATCH_<NNN>_EXEC_A: CONCLUÍDO — branch executor-a/batch-<NNN> pronta para merge'
  executor_b: 'BATCH_<NNN>_EXEC_B: CONCLUÍDO — branch executor-b/batch-<NNN> pronta para merge'

merge_order:
  - executor-a/batch-<NNN>
  - executor-b/batch-<NNN>
```

## 5. Regras de Execução (DE-1 a DE-10)

**DE-1**: Nenhum executor inicia sem um BATCH YAML definido e aprovado pelo Arquiteto em `docs/_canon/agentes/BATCH_<NNN>_exec_assignments.yaml`.

**DE-2**: Cada executor MUST criar sua branch antes de qualquer modificação de arquivo: `git checkout -b executor-<a|b>/batch-<NNN>`.

**DE-3**: Cada executor MUST respeitar estritamente seu `file_ownership`. PROIBIDO tocar arquivos do domínio do outro executor.

**DE-4**: Dentro de um executor, a sequência de ARs definida em `ar_sequence` MUST ser respeitada. Não pular ARs, não reordenar sem nova aprovação do Arquiteto.

**DE-5**: Cada AR executada MUST gerar Evidence Pack conforme Manual Deterministico.md. O carimbo na AR MUST ser appendado via `hb report`.

**DE-6**: `hb check` MUST PASS na branch de cada executor ANTES de sinalizar conclusão ao Arquiteto.

**DE-7**: Ao concluir TODAS as suas ARs, o executor emite o sinal de conclusão definido em `completion_signals` do BATCH YAML.

**DE-8**: O merge é responsabilidade EXCLUSIVA do Arquiteto. Nenhum executor faz merge por conta própria.

**DE-9**: Conflito de merge após pull de ambas as branches indica violação de DE-3 (file ownership). O Arquiteto DEVE investigar antes de resolver manualmente.

**DE-10 (Anti-Hallucination)**: Cada executor MUST seguir individualmente as regras AH-1..AH-7 do Testador Contract. A paralelização NÃO relaxa as regras anti-alucinação.

## 6. Dependências entre Executores

Se AR-X (Executor B) depende do resultado de AR-Y (Executor A), então AR-X MUST ser movida para o mesmo executor que AR-Y, logo após ela na sequência.

Regra de ouro: dependência cross-executor = violação de design do batch. O Arquiteto DEVE redesenhar o batch antes de iniciar a execução.

## 7. Merge Protocol (Arquiteto)

Após ambos os executores emitirem seus sinais de conclusão:
1. `git checkout <base_branch>`
2. `git merge executor-a/batch-<NNN>` — MUST ser sem conflito
3. `git merge executor-b/batch-<NNN>` — MUST ser sem conflito
4. Se conflito em qualquer etapa: investigar violação DE-3. NÃO resolver manualmente sem entender causa.
5. Após merge bem-sucedido: deletar branches executor-a e executor-b do batch concluído.
---FIM DO CONTEÚDO---

ARQUIVO A CRIAR (ÚNICO): docs/_canon/contratos/Dual Executor Contract.md
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) docs/_canon/contratos/Dual Executor Contract.md existe. 2) Contém as seções §1 Rationale, §2 File Ownership, §3 Branch Protocol, §4 Assignment Manifest, §5 Regras de Execução, §6 Dependências, §7 Merge Protocol. 3) Contém todas as 10 regras DE-1 a DE-10. 4) Contém o formato YAML do Assignment Manifest com os campos: batch_id, base_branch, base_commit, executor_a, executor_b, ar_sequence, file_ownership, file_ownership_conflict_check, completion_signals, merge_order. 5) Contém tabela de domínios canônicos padrão com Executor A (CLI/Infra) e Executor B (Docs/Specs).

## Validation Command (Contrato)
```
python -c "import pathlib; content = pathlib.Path('docs/_canon/contratos/Dual Executor Contract.md').read_text(encoding='utf-8'); assert 'DE-1' in content, 'FAIL: DE-1 ausente'; assert 'DE-10' in content, 'FAIL: DE-10 ausente'; assert 'file_ownership' in content, 'FAIL: file_ownership ausente'; assert 'ar_sequence' in content, 'FAIL: ar_sequence ausente'; assert 'base_commit' in content, 'FAIL: base_commit ausente'; assert 'Merge Protocol' in content, 'FAIL: Merge Protocol ausente'; assert 'completion_signals' in content, 'FAIL: completion_signals ausente'; assert 'merge_order' in content, 'FAIL: merge_order ausente'; print('PASS: Dual Executor Contract.md valido com DE-1..DE-10 e Merge Protocol')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_021_gov_dual_executor_contract.log`

## Riscos
- Branches executor-a e executor-b DEVEM partir do MESMO base_commit para que o merge do Arquiteto seja limpo — qualquer divergência de base pode gerar conflito espúrio.
- AR_020 toca hb_cli.py (CLI) E docs/_canon/contratos/Dev Flow.md (Docs) — o Dev Flow.md deve estar no domínio de Executor A no BATCH_001, não no domínio padrão de B.
- Se um executor abandonar o batch incompleto, o Arquiteto pode realocar as ARs restantes para o outro executor criando um BATCH_002 com o subconjunto pendente.
- O protocolo não cobre 3+ executores — extensão futura requer novo contrato ou adendo.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; content = pathlib.Path('docs/_canon/contratos/Dual Executor Contract.md').read_text(encoding='utf-8'); assert 'DE-1' in content, 'FAIL: DE-1 ausente'; assert 'DE-10' in content, 'FAIL: DE-10 ausente'; assert 'file_ownership' in content, 'FAIL: file_ownership ausente'; assert 'ar_sequence' in content, 'FAIL: ar_sequence ausente'; assert 'base_commit' in content, 'FAIL: base_commit ausente'; assert 'Merge Protocol' in content, 'FAIL: Merge Protocol ausente'; assert 'completion_signals' in content, 'FAIL: completion_signals ausente'; assert 'merge_order' in content, 'FAIL: merge_order ausente'; print('PASS: Dual Executor Contract.md valido com DE-1..DE-10 e Merge Protocol')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_021_gov_dual_executor_contract.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_021_b2e7523/result.json`
