# AR_275 — Superficie TRAINING reconciliada: Flows, Screens, UI ledger + traceability

**Status**: 🔲 PENDENTE
**Versão do Protocolo**: 1.3.0

## Descrição
ARQUIVO 1: docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md
(a) Localizar FLOW-TRAIN-002 e remover toda referencia a 'publicar sessao', 'publish', POST /publish. Substituir por 'agendar sessao' (schedule) como acao humana valida.
(b) Atualizar flows de AI coach: substituir 'publicar' por 'schedule'.
(c) Atualizar flows de attendance/revisao: 'finalizar sessao' (finalize) como borda humana.
(d) Garantir que transicoes automaticas (scheduled->in_progress, in_progress->pending_review) nao tem botao humano no flow — sao exclusivas do sistema.
(e) Adicionar flow para visualizacao do ledger (Planned / Realized / Adjustments).

ARQUIVO 2: docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md
(a) SCREEN-TRAIN-020 (Detalhe/cockpit): atualizar de PARCIAL para especificacao completa. Incluir:
  - secao Planned (data-test-id='training-session-planned-section')
  - secao Realized (data-test-id='training-session-realized-section')
  - secao Adjustments (data-test-id='training-session-adjustments-section')
  - Remover qualquer affordance de lifecycle legado (publish/close).
  - Status badge exibindo exclusivamente: draft, scheduled, in_progress, pending_review, readonly.
(b) SCREEN-TRAIN-022 (Revisao/Finalizacao): atualizar de GAP para especificacao. Tela de revisao operacional pending_review -> readonly. Ao finalizar, travar edicao e exibir estado imutavel.
(c) SCREEN-TRAIN-025 (AI Coach Review): atualizar de GAP para especificacao. Substituir 'publish' por 'schedule'. Preview do contrato/plano antes do apply. Forcsar revisao humana antes de gerar Planned_State.
(d) SCREEN-TRAIN-001 (Agenda/Lista): garantir badges exclusivamente canonicos.

ARQUIVO 3: Hb Track - Frontend/src/app/(admin)/training/sessions/[id] (NOVO ou REFATORAR)
Implementar tela de detalhe da sessao (SCREEN-TRAIN-020). Deve incluir:
  - data-test-id='training-session-planned-section'
  - data-test-id='training-session-realized-section'
  - data-test-id='training-session-adjustments-section'
  - Status badge canonico (draft/scheduled/in_progress/pending_review/readonly)
  - Sem botoes para scheduled->in_progress ou in_progress->pending_review
  - Composicao por primitives do TRAINING_UI_CONTRACT.md (sem CSS inline, sem cores hardcoded)

ARQUIVO 4: Hb Track - Frontend/src/app/(admin)/training/sessions/[id]/revisao (NOVO)
Implementar tela de revisao/finalizacao (SCREEN-TRAIN-022):
  - Aceita apenas sessoes em pending_review
  - Botao 'Finalizar' chama POST /finalize
  - Apos finalizacao: status readonly, edicao travada
  - data-test-id='session-finalize-button'

ARQUIVO 5: Hb Track - Frontend/src/app/(admin)/training/sessions/[id]/ai-coach (NOVO ou REFATORAR)
Implementar tela de AI Coach Review (SCREEN-TRAIN-025):
  - Exibe preview do plano antes de aplicar/agendar
  - Substitui semantica 'publish' por 'schedule'
  - Forcsa revisao humana antes de gerar Planned_State
  - data-test-id='ai-coach-schedule-button'

ARQUIVO 6: Hb Track - Frontend/src/app/(admin)/training/agenda/AgendaClient.tsx (ATUALIZAR)
SCREEN-TRAIN-001: garantir status badges exibindo apenas vocabulario canonico.
Remover qualquer referencia a 'publicado', 'fechado', 'publish', 'close'.

ARQUIVO 7: docs/hbtrack/modulos/treinos/_evidence/traceability_training_core.csv
Preencher com linhas reais para os flows/screens tocados:
  FLOW-TRAIN-002, SCREEN-TRAIN-001, SCREEN-TRAIN-020, SCREEN-TRAIN-022, SCREEN-TRAIN-025.
Formato: SCREEN_ID|FLOW_ID|STATUS|data|descricao
AR_275 deve deixar o arquivo com pelo menos 5 linhas de dados (nao apenas headers).

RESTRICOES:
  - Proibido manter publish/close como verbo de lifecycle em qualquer arquivo listado
  - Proibido CSS inline fora da camada autorizada (TRAINING_UI_CONTRACT.md)
  - Proibido cores hardcoded (#XXXXXX, rgb(), hsl())
  - Proibido criar botoes para transicoes automaticas
  - data-test-id obrigatorio nas 3 secoes do ledger (G7)

## Critérios de Aceite
1) TRAINING_USER_FLOWS.md sem /publish /close /publicar sessao; com /schedule e /finalize.
2) TRAINING_SCREENS_SPEC.md sem /publish /close; SCREEN-TRAIN-020/022/025 especificados.
3) FE src: data-test-id training-session-planned-section, training-session-realized-section, training-session-adjustments-section presentes.
4) traceability_training_core.csv com >= 5 linhas de dados reais.
5) FE src: sem 'publish' ou 'close' como verbo de lifecycle.
6) validation_command exit=0.

## Write Scope
- docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md
- docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md
- docs/hbtrack/modulos/treinos/_evidence/traceability_training_core.csv
- Hb Track - Frontend/src/app/*/training/sessions
- Hb Track - Frontend/src/app/*/training/agenda

## Validation Command (Contrato)
```
python -c "import pathlib,re;uf=pathlib.Path('docs/hbtrack/modulos/treinos/TRAINING_USER_FLOWS.md').read_text('utf-8');ss=pathlib.Path('docs/hbtrack/modulos/treinos/TRAINING_SCREENS_SPEC.md').read_text('utf-8');assert not re.search(r'/publish|publicar.sessao|POST /publish',uf,re.I),'G1a:publish in flows';assert 'schedule' in uf.lower(),'G2a:schedule absent flows';assert 'finalize' in uf.lower(),'G2b:finalize absent flows';assert not re.search(r'/publish|POST /publish',ss,re.I),'G1b:publish in screens';tc=pathlib.Path('docs/hbtrack/modulos/treinos/_evidence/traceability_training_core.csv').read_text('utf-8');rows=[l for l in tc.split('
') if l.strip() and not l.startswith('#')];assert len(rows)>=5,'G10a:traceability skeleton (need 5+ data rows)';assert any('SCREEN-TRAIN-020' in l or 'FLOW-TRAIN-002' in l for l in rows),'G10b:key items absent';fe=[p for p in pathlib.Path('Hb Track - Frontend/src').rglob('*.tsx') if 'training' in str(p).lower()];fec=''.join(p.read_text('utf-8',errors='ignore') for p in fe[:30]);assert 'training-session-planned-section' in fec,'G7a:planned-section';assert 'training-session-realized-section' in fec,'G7b:realized-section';assert 'training-session-adjustments-section' in fec,'G7c:adjustments-section';print('PASS AR_275 Gates 1-10 OK')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_275/executor_main.log`

## Notas do Arquiteto
Telas-alvo: SCREEN-TRAIN-020 (detalhe/cockpit), SCREEN-TRAIN-022 (revisao/finalizacao), SCREEN-TRAIN-025 (AI Coach review), SCREEN-TRAIN-001 (agenda badges). O Executor cria ou refatora os componentes no diretorio sessions/. data-test-id obrigatorio para as 3 secoes do ledger (Gate 7). PROOF: TRUTH_BE no contexto de superfície — data-test-ids presentes, validation_command exit=0; testes E2E opcionais (TRUTH_FE futura). TRACE: TRAINING_USER_FLOWS.md FLOW-TRAIN-002 reconciliado, TRAINING_SCREENS_SPEC.md SCREEN-020/022/025 especificados, traceability_training_core.csv >= 5 linhas, FE com 3 data-test-ids do ledger.

## Riscos
- AgendaClient.tsx pode ter referencia a badge com status ingles 'published'/'closed' — verificar com grep antes de editar
- traceability_training_core.csv tem delimitador CSV ou pipes — verificar formato antes de adicionar linhas
- TRAINING_SCREENS_SPEC.md pode ter secao de especificacao com formato rigoroso — Executor verificar estrutura antes de adicionar linhas
- Telas novas podem requerer componentes UI nao existentes — usar composicao de primitives existentes per TRAINING_UI_CONTRACT.md
- CSS inline proibido mas alguns componentes legados podem ter — Executor NAO deve tocar legado fora do write_scope

## Análise de Impacto
_(A ser preenchido pelo Executor)_

---
## Carimbo de Execução
_(Gerado por hb report)_

