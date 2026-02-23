# AR_019 — Hb cli Spec v1.0.8: §10 hb verify, §11 novos status, §12 hb check atualizado

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.0.6

## Descrição
ATUALIZAR docs/_canon/specs/Hb cli Spec.md com 3 blocos novos.

MUDANÇA 1 — Linha 1 (header):
Substituir 'SPEC_HB_CLI — scripts/run/hb_cli.py (HB CLI) — v1.0.6' por 'SPEC_HB_CLI — scripts/run/hb_cli.py (HB CLI) — v1.0.8'

MUDANÇA 2 — §1 (HB_PROTOCOL_VERSION):
Substituir '1.0.6' por '1.0.8' em TODAS as ocorrências de §1.

MUDANÇA 3 — Adicionar ao FINAL do arquivo (antes de qualquer linha final) as seções §10, §11, §12:

---INÍCIO DO BLOCO A ADICIONAR---
## 10. hb verify — Testador independente

Assinatura:
- hb verify <id>

Função: re-executa o validation_command da AR de forma independente e gera TESTADOR_REPORT.

Pipeline (ordem exata):

V1) Localizar AR_<id>_*.md em AR_DIR
    Se não encontrar: FAIL E_AR_NOT_FOUND (exit 2)

V2) Verificar que AR contém '✅ SUCESSO'
    Se não: FAIL E_VERIFY_NOT_READY com mensagem 'AR must have ✅ SUCESSO before verify' (exit 4)

V3) Extrair validation_command (entre ``` de ## Validation Command (Contrato))
    Se ausente: FAIL E_VERIFY_NO_CMD (exit 4)

V4) Re-executar validation_command (independente — não reutilizar output do Executor)

V5) Ler Evidence Pack (caminho de ## Evidence File (Contrato)):
    - Extrair 'Exit Code: N' do Evidence Pack
    - Se Evidence Pack ausente: registrar evidence_pack_complete=false

V6) Determinar consistency:
    - executor_exit extraído do Evidence Pack
    - testador_exit = exit code da re-execução
    - consistency = 'OK' se iguais; 'AH_DIVERGENCE' se executor=0 mas testador!=0

V7) Gerar TESTADOR_REPORT em _reports/testador/AR_<id>_<git_hash_7>/:
    - context.json (run_id, timestamp, git.commit, environment.python_version)
    - result.json (ar_id, validation_command, testador_exit_code, executor_exit_code, consistency, status, ah_flags, evidence_pack_complete, rejection_reason)
    - stdout.log (stdout da re-execução)
    - stderr.log (stderr da re-execução)

V8) Atualizar **Status** header da AR via re.sub:
    - testador_exit == 0 AND consistency == 'OK': '✅ VERIFICADO'
    - testador_exit != 0 OR consistency == 'AH_DIVERGENCE': '🔴 REJEITADO'
    - ERROR_INFRA (exit 3): '⏸️ BLOQUEADO_INFRA'

V9) Append stamp de verificação à AR:
    ### Verificação Testador em <hash_7>
    **Status Testador**: <✅ VERIFICADO | 🔴 REJEITADO | ⏸️ BLOQUEADO_INFRA>
    **Consistency**: <OK | AH_DIVERGENCE>
    **Exit Testador**: <n> | **Exit Executor**: <n>
    **TESTADOR_REPORT**: `_reports/testador/AR_<id>_<hash>/result.json`

Exit codes do hb verify:
- 0: VERIFICADO (re-execução exit 0 + consistency OK)
- 2: REJEITADO (re-execução exit != 0 OU AH_DIVERGENCE)
- 3: BLOCKED_INFRA (ERROR_INFRA na re-execução)
- 4: BLOCKED_INPUT (AR não pronta ou sem validation command)

## 11. Novos Status de AR (v1.0.8)

Status válidos (completo):
- DRAFT
- 🏗️ EM_EXECUCAO
- ✅ SUCESSO (Executor claims success — NÃO final em v1.0.8+)
- ✅ VERIFICADO (Testador confirmou — FINAL, permite commit)
- ❌ FALHA (Executor encontrou falha)
- 🔴 REJEITADO (Testador rejeitou — Executor deve corrigir e rodar hb report novamente)
- ⏸️ BLOQUEADO_INFRA (Testador encontrou ERROR_INFRA — waiver necessário)
- ⛔ SUPERSEDED (AR obsoleta, substituída por outra)

Regra: hb check (v1.0.8+) aceita APENAS ✅ VERIFICADO para ARs com Versão do Protocolo >= 1.0.8.

## 12. hb check atualizado — C3 com VERIFICADO

C3 atualizado (substitui regra anterior):

C3) Se SSOT STAGED => MUST existir AR STAGED que:
  a) marcou [x] o SSOT em SSOT Touches
  b) tem status final válido:
     - Se AR tem 'Versão do Protocolo': 1.0.8 ou superior: MUST ter '✅ VERIFICADO'
     - Se AR tem protocolo anterior: aceita '✅ SUCESSO' (migração)
  c) Evidence File existe e está STAGED com 'Exit Code: 0'

Novos error codes:
- E_VERIFY_NOT_READY: AR não tem ✅ SUCESSO — Executor não terminou
- E_VERIFY_NO_CMD: AR não tem Validation Command — não verificável
- E_VERIFY_REQUIRES_VERIFIED: AR v1.0.8+ staged sem ✅ VERIFICADO (Testador não rodou)
---FIM DO BLOCO A ADICIONAR---

ARQUIVO A MODIFICAR (ÚNICO): docs/_canon/specs/Hb cli Spec.md
NAO modificar nenhum outro arquivo.

## Critérios de Aceite
1) Hb cli Spec.md contém '## 10. hb verify'. 2) Contém 'E_VERIFY_NOT_READY', 'E_VERIFY_NO_CMD'. 3) Contém '✅ VERIFICADO' e '🔴 REJEITADO'. 4) Contém '## 11. Novos Status'. 5) Contém '## 12. hb check atualizado'. 6) Header reporta v1.0.8. 7) §1 menciona 1.0.8.

## Validation Command (Contrato)
```
python -c "import pathlib; c=pathlib.Path('docs/_canon/specs/Hb cli Spec.md').read_text(encoding='utf-8'); required={'hb_verify':'## 10. hb verify' in c,'E_VERIFY_NOT_READY':'E_VERIFY_NOT_READY' in c,'E_VERIFY_NO_CMD':'E_VERIFY_NO_CMD' in c,'VERIFICADO':'✅ VERIFICADO' in c,'REJEITADO':'🔴 REJEITADO' in c,'novos_status':'## 11. Novos Status' in c,'hb_check_atualizado':'## 12. hb check atualizado' in c,'v108':'1.0.8' in c}; failed=[k for k,v in required.items() if not v]; print(f'FAIL: {failed}') if failed else print(f'PASS: Hb CLI Spec v1.0.8 OK — {len(required)} checks')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_019_gov_hb_cli_spec_v108.log`

## Riscos
- O arquivo Hb cli Spec.md tem o nome 'Hb cli Spec.md' (não 'Hb CLI Spec.md') — verificar com glob antes de editar.
- A mudança 1 (header) e mudança 2 (§1) devem substituir TODAS as ocorrências de 1.0.6 dentro de §1, sem afetar exemplos ou outros contextos.
- As seções §10, §11, §12 devem ser adicionadas ao FINAL do arquivo sem sobrescrever §9 existente.

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_


### Execução em b2e7523
**Status Final**: ✅ SUCESSO
**Comando**: `python -c "import pathlib; c=pathlib.Path('docs/_canon/specs/Hb cli Spec.md').read_text(encoding='utf-8'); required={'hb_verify':'## 10. hb verify' in c,'E_VERIFY_NOT_READY':'E_VERIFY_NOT_READY' in c,'E_VERIFY_NO_CMD':'E_VERIFY_NO_CMD' in c,'VERIFICADO':'✅ VERIFICADO' in c,'REJEITADO':'🔴 REJEITADO' in c,'novos_status':'## 11. Novos Status' in c,'hb_check_atualizado':'## 12. hb check atualizado' in c,'v108':'1.0.8' in c}; failed=[k for k,v in required.items() if not v]; print(f'FAIL: {failed}') if failed else print(f'PASS: Hb CLI Spec v1.0.8 OK — {len(required)} checks')"`
**Exit Code**: 0
**Evidence File**: `docs/hbtrack/evidence/AR_019_gov_hb_cli_spec_v108.log`
**Python Version**: 3.11.9


### Verificacao Testador em b2e7523
**Status Testador**: ✅ VERIFICADO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_019_b2e7523/result.json`
