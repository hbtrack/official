# AR_197 — INVARIANTS_TRAINING.md v1.5.0: 31 itens GAP/PARCIAL/DIVERGENTE → IMPLEMENTADO

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Classe G (Governanca documental). NAO altera codigo. Editar SOMENTE docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md. INSTRUCOES PRECISAS:

(A) HEADER: Alterar 'Versão: v1.4.0' para 'Versão: v1.5.0'. Alterar 'Última revisão: 2026-02-27' para 'Última revisão: 2026-03-02'. Adicionar bloco de changelog v1.5.0 ANTES do changelog v1.4.0:
> Changelog v1.5.0 (2026-03-02):
> - **Sync pós-Batch 3..5**: promovidos 31 invariantes GAP/PARCIAL/DIVERGENTE_DO_SSOT → IMPLEMENTADO
>   - INV-013/024 (PARCIAL→IMPLEMENTADO): evidência AR_195 (hb seal 2026-03-01)
>   - INV-014/023 (DIVERGENTE_DO_SSOT→IMPLEMENTADO): evidência AR_175/176 (hb seal 2026-02-28)
>   - INV-025 (PARCIAL→IMPLEMENTADO): evidência AR_179/180 (hb seal 2026-02-28)
>   - INV-047..053 (GAP→IMPLEMENTADO): evidência AR_181/182 (hb seal 2026-03-01)
>   - INV-EXB-ACL-001..007 (GAP→IMPLEMENTADO): evidência AR_181/182/183 (hb seal 2026-03-01)
>   - INV-054..056 (GAP→IMPLEMENTADO): evidência AR_189 (hb seal 2026-03-01)
>   - INV-057 (GAP→IMPLEMENTADO): evidência AR_190 (hb seal 2026-03-01)
>   - INV-058..059 (PARCIAL→IMPLEMENTADO): evidência AR_190 (hb seal 2026-03-01)
>   - INV-060..062 (GAP→IMPLEMENTADO): evidência AR_182/183 (hb seal 2026-03-01)
>   - INV-079..081 (GAP→IMPLEMENTADO): evidência AR_192 (hb seal 2026-03-01)

(B) INVARIANTES PARCIAL/DIVERGENTE (5 itens):
- INV-TRAIN-013: alterar 'status: PARCIAL' para 'status: IMPLEMENTADO'. Atualizar 'note:' para: 'Regra backend gamification_badge_eligibility evidenciada. Promovido por Kanban+evidencia: AR_195 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_195/executor_main.log'
- INV-TRAIN-014: alterar 'status: DIVERGENTE_DO_SSOT' para 'status: IMPLEMENTADO'. Atualizar 'note:' para: 'Divergencia UUID/int resolvida por fix de tipagem em alerts/suggestions. Promovido por Kanban+evidencia: AR_175 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_175/executor_main.log'
- INV-TRAIN-023: alterar 'status: DIVERGENTE_DO_SSOT' para 'status: IMPLEMENTADO'. Atualizar 'note:' para: 'Divergencia team_id UUID+wellness self-only resolvida. Promovido por Kanban+evidencia: AR_175/AR_176 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_175/executor_main.log'
- INV-TRAIN-024: alterar 'status: PARCIAL' para 'status: IMPLEMENTADO'. Atualizar 'note:' para: 'WebSocket broadcast backend evidenciado; testes cobrindo integracao. Promovido por Kanban+evidencia: AR_195 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_195/executor_main.log'
- INV-TRAIN-025: alterar 'status: PARCIAL' para 'status: IMPLEMENTADO'. Adicionar ou atualizar 'note:' para: 'Exports reabilitados + estado degradado sem worker. Promovido por Kanban+evidencia: AR_179/AR_180 (hb seal 2026-02-28), paths: docs/hbtrack/evidence/AR_179/executor_main.log'

(C) INV-TRAIN-047..053 (7 itens, todos GAP→IMPLEMENTADO):
Para cada um, alterar 'status: GAP' para 'status: IMPLEMENTADO' e adicionar 'note:' com evidencia:
- INV-047 (exercise_scope_valid): 'Promovido por Kanban+evidencia: AR_181 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_181/executor_main.log'
- INV-048 (system_exercise_immutable_for_org_users): 'Promovido por Kanban+evidencia: AR_182 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_182/executor_main.log'
- INV-049 (org_exercise_single_organization): 'Promovido por Kanban+evidencia: AR_181 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_181/executor_main.log'
- INV-050 (favorite_unique_per_user_exercise): 'Promovido por Kanban+evidencia: AR_181 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_181/executor_main.log'
- INV-051 (catalog_visibility_respects_organization): 'Promovido por Kanban+evidencia: AR_182 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_182/executor_main.log'
- INV-052 (exercise_media_type_reference_valid): 'Promovido por Kanban+evidencia: AR_181 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_181/executor_main.log'
- INV-053 (soft_delete_exercise_no_break_historic_session): 'Promovido por Kanban+evidencia: AR_182 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_182/executor_main.log'

(D) INV-TRAIN-EXB-ACL-001..007 (7 itens, todos GAP→IMPLEMENTADO):
- EXB-ACL-001 (exercise_org_visibility_mode_valid): AR_181 (hb seal 2026-03-01)
- EXB-ACL-002 (acl_only_for_org_restricted): AR_182 (hb seal 2026-03-01)
- EXB-ACL-003 (acl_anti_cross_org): AR_182/AR_183 (hb seal 2026-03-01)
- EXB-ACL-004 (acl_authority_creator_only): AR_182 (hb seal 2026-03-01)
- EXB-ACL-005 (creator_implicit_access): AR_182 (hb seal 2026-03-01)
- EXB-ACL-006 (acl_unique_per_exercise_user): AR_181 (hb seal 2026-03-01)
- EXB-ACL-007 (acl_change_no_retrobreak_historic_session): AR_182 (hb seal 2026-03-01)
Formato note: 'Promovido por Kanban+evidencia: AR_### (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_###/executor_main.log'

(E) INV-TRAIN-054..059 (6 itens):
- INV-054 (cycle_hierarchy_mandatory, GAP): AR_189 (hb seal 2026-03-01)
- INV-055 (meso_overlap_allowed, GAP): AR_189 (hb seal 2026-03-01)
- INV-056 (micro_contained_in_meso, GAP): AR_189 (hb seal 2026-03-01)
- INV-057 (standalone_session_explicit_flag, GAP): AR_190 (hb seal 2026-03-01)
- INV-058 (PARCIAL→IMPLEMENTADO): AR_190 (hb seal 2026-03-01). Note: 'order_index validado em session_exercise_service.py. Promovido por Kanban+evidencia: AR_190 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_190/executor_main.log'
- INV-059 (PARCIAL→IMPLEMENTADO): AR_190 (hb seal 2026-03-01). Note: mesma rastreabilidade que INV-058.

(F) INV-TRAIN-060..062 (3 itens, todos GAP→IMPLEMENTADO):
- INV-060 (org_exercise_default_restricted): AR_182 (hb seal 2026-03-01)
- INV-061 (system_exercise_copy_not_edit): AR_183 (hb seal 2026-03-01)
- INV-062 (exercise_visibility_required_for_session_add): AR_182/AR_183 (hb seal 2026-03-01)

(G) INV-TRAIN-079..081 (3 itens, todos GAP→IMPLEMENTADO):
- INV-079 (individual_recognition_no_intimate_leak): AR_192 (hb seal 2026-03-01)
- INV-080 (ai_coach_draft_only): AR_192 (hb seal 2026-03-01)
- INV-081 (ai_suggestion_requires_justification): AR_192 (hb seal 2026-03-01)
Formato note: 'Promovido por Kanban+evidencia: AR_192 (hb seal 2026-03-01), paths: docs/hbtrack/evidence/AR_192/executor_main.log'

## Critérios de Aceite
AC-001: INVARIANTS_TRAINING.md nao contem 'status: GAP', 'status: PARCIAL' nem 'status: DIVERGENTE_DO_SSOT' em nenhum bloco yaml de invariante (regex (?m)^status:\s*(GAP|PARCIAL|DIVERGENTE_DO_SSOT) retorna zero matches). AC-002: Versao do documento atualizada para v1.5.0 com changelog v1.5.0 descrevendo os 31 itens promovidos. AC-003: Cada invariante promovido tem campo note: com texto 'Promovido por Kanban+evidencia: AR_' (rastreabilidade minima). AC-004: Nenhum arquivo fora de docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md foi alterado.

## Write Scope
- docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md

## Validation Command (Contrato)
```
python -c "import sys,re;c=open('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md',encoding='utf-8').read();g=re.findall(r'(?m)^status:\s*(GAP|PARCIAL|DIVERGENTE_DO_SSOT)',c);[print(f'FAIL: {len(g)} still not promoted: {sorted(set(g))}') for _ in [1]] if g else print('PASS: all invariants IMPLEMENTADO');v=re.search(r'Versão:\s*v(\S+)',c);vok=v and v.group(1)=='1.5.0';[print('FAIL: version not v1.5.0, found '+str(v.group(0) if v else 'NONE'))] if not vok else print('PASS: version v1.5.0 ok');tr='Promovido por Kanban+evidencia: AR_' in c;[print('FAIL: no traceability note found')] if not tr else print('PASS: traceability note present');sys.exit(len(g)+(0 if vok else 1)+(0 if tr else 1))"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_197/executor_main.log`

## Notas do Arquiteto
Classe G pura. Arquivo alvo: docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md. Total: 31 invariantes. Zero toque em Backend/Frontend. Nao criar novos IDs de invariante. Rastreabilidade obrigatoria por item. Evidence paths seguem o padrao docs/hbtrack/evidence/AR_<origem>/executor_main.log — cada item aponta para a AR que o implementou (nao AR_197).

## Riscos
- INVARIANTS_TRAINING.md usa blocos yaml delimitados por ```yaml ... ```. Alterar SOMENTE os campos 'status:' e 'note:' dentro dos blocos corretos. NAO alterar 'status:' no cabecalho do documento nem nas secoes de convencoes.
- Regex de validacao usa (?m)^status: — que nao corresponde a texto nas convencoes (linha comeca com '-' e backtick). Seguro.
- Alguns invariantes ja tem campo 'note:' — atualizar o existente, nao criar duplicado.
- Alguns invariantes NAO tem campo 'note:' — adicionar apos o campo 'status:' (ordem: id, class, name, rule, tables/services/evidence, status, note, rationale).
- INV-014 e INV-023: status DIVERGENTE_DO_SSOT (nao GAP nem PARCIAL) — garantir que regex captura corretamente e que ambos sao alterados.
- INV-058/059: verificar o nome exato do campo e a posicao no bloco yaml antes de editar.
- NAO alterar invariantes com status IMPLEMENTADO (INV-001..012, 015..022, 026..046, 063..078 — todos ja ok).
- Conferir que a versao no cabecalho e 'v1.4.0' antes de alterar para 'v1.5.0' (para evitar double-bump).

## Análise de Impacto

**Executor**: Copilot Executor v1.3.0 | **Data**: 2026-03-02

**Arquivo alvo**: `docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md` (v1.4.0 → v1.5.0)  
**Total de invariantes a promover**: 31  
**Estado confirmado pré-execução**: 31 blocos yaml com status GAP/PARCIAL/DIVERGENTE_DO_SSOT (verificado por script Python)  
**Versão confirmada**: `Versão: v1.4.0` (pronto para bump)  

**Mapa de impacto por grupo**:
| Grupo | IDs | Status→ | AR Evidência |
|---|---|---|---|
| B | INV-013, 024 | PARCIAL→IMPLEMENTADO | AR_195 |
| B | INV-014, 023 | DIVERGENTE_DO_SSOT→IMPLEMENTADO | AR_175/176 |
| B | INV-025 | PARCIAL→IMPLEMENTADO | AR_179/180 |
| C | INV-047..053 (7) | GAP→IMPLEMENTADO | AR_181/182 |
| D | INV-EXB-ACL-001..007 (7) | GAP→IMPLEMENTADO | AR_181/182/183 |
| E | INV-054..056 (3) | GAP→IMPLEMENTADO | AR_189 |
| E | INV-057 | GAP→IMPLEMENTADO | AR_190 |
| E | INV-058..059 (2) | PARCIAL→IMPLEMENTADO | AR_190 |
| F | INV-060..062 (3) | GAP→IMPLEMENTADO | AR_182/183 |
| G | INV-079..081 (3) | GAP→IMPLEMENTADO | AR_192 |

**Arquivos NÃO tocados**: Backend, Frontend, scripts, demais SSOT — conforme write_scope.  
**Estratégia**: aplicação via script Python atômico (transform in-memory + write) para garantir 31 edições consistentes sem risco de merge parcial.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import sys,re;c=open('docs/hbtrack/modulos/treinos/INVARIANTS_TRAINING.md',encoding='utf-8').read();g=re.findall(r'(?m)^status:\s*(GAP|PARCIAL|DIVERGENTE_DO_SSOT)',c);[print(f'FAIL: {len(g)} still not promoted: {sorted(set(g))}') for _ in [1]] if g else print('PASS: all invariants IMPLEMENTADO');v=re.search(r'Versão:\s*v(\S+)',c);vok=v and v.group(1)=='1.5.0';[print('FAIL: version not v1.5.0, found '+str(v.group(0) if v else 'NONE'))] if not vok else print('PASS: version v1.5.0 ok');tr='Promovido por Kanban+evidencia: AR_' in c;[print('FAIL: no traceability note found')] if not tr else print('PASS: traceability note present');sys.exit(len(g)+(0 if vok else 1)+(0 if tr else 1))"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-02T03:17:37.478614+00:00
**Behavior Hash**: 024a3407e37d128be4ad7ecc858489ed86dd9762fb3afdbf89ac89236d8d3cbf
**Evidence File**: `docs/hbtrack/evidence/AR_197/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_197_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-02T04:01:53.158171+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_197_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_197/executor_main.log`
