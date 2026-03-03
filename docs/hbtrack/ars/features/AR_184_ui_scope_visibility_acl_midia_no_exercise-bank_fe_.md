# AR_184 — UI scope/visibility/ACL/midia no exercise-bank FE (ExerciseCard + ACLModal + exercises.ts)

**Status**: ✅ VERIFICADO
**Versão do Protocolo**: 1.3.0

## Descrição
Implementar no FE Hb Track - Frontend/src/components/training/exercises/ExerciseCard.tsx: badge SYSTEM ou ORG visivel, botao Duplicar para Meu Banco quando scope=SYSTEM, toggle de visibilidade (org_wide|restricted) e botao Gerenciar ACL quando scope=ORG e usuario e criador, preview de midia se exercise.media presente. Criar Hb Track - Frontend/src/components/training/exercises/ExerciseACLModal.tsx: modal que chama GET /exercises/{id}/acl, lista users, permite POST (adicionar) e DELETE (remover) users da mesma org. Criar Hb Track - Frontend/src/components/training/exercises/ExerciseVisibilityToggle.tsx: toggle org_wide|restricted via PATCH /exercises/{id}/visibility. Atualizar Hb Track - Frontend/src/lib/api/exercises.ts: adicionar funcoes copyExerciseToOrg, patchExerciseVisibility, getExerciseACL, addUserToACL, removeUserFromACL. Atualizar page.tsx em src/app (exercise-bank) se necessario para passar scope/ACL ao ExerciseCard. RBAC FE: acoes de edicao visıveis apenas se current_user.role === Treinador. Proibido: modificar BE.

## Critérios de Aceite
1) ExerciseCard.tsx exibe badge scope (SYSTEM|ORG) e botao copy-to-org para SYSTEM. 2) exercises.ts tem funcoes copyExerciseToOrg e endpoints de ACL. 3) ExerciseACLModal.tsx existe com chamadas GET/POST/DELETE para /acl. 4) Acoes de edicao verificam role RBAC antes de renderizar. 5) Imports TypeScript sem erros de compilacao.

## Write Scope
- Hb Track - Frontend/src/lib/api/exercises.ts
- Hb Track - Frontend/src/components/training/exercises
- Hb Track - Frontend/src/app

## Validation Command (Contrato)
```
python -c "import os; b='Hb Track - Frontend'; c1=open(os.path.join(b,'src','lib','api','exercises.ts')).read(); assert 'copy-to-org' in c1 or 'copyExercise' in c1,'exercises.ts missing copy-to-org'; assert 'acl' in c1.lower(),'exercises.ts missing ACL'; c2=open(os.path.join(b,'src','components','training','exercises','ExerciseCard.tsx')).read(); assert 'scope' in c2 or 'SYSTEM' in c2,'ExerciseCard missing scope'; assert os.path.exists(os.path.join(b,'src','components','training','exercises','ExerciseACLModal.tsx')),'ExerciseACLModal missing'; print('PASS AR_184')"
```

## Evidence File (Contrato)
`docs/hbtrack/evidence/AR_184/executor_main.log`

## Notas do Arquiteto
page.tsx do exercise-bank esta em src/app/(admin)/training/exercise-bank/page.tsx — caminho com parenteses nao pode ser listado no write_scope do schema, mas e coberto por src/app. ExerciseACLModal e ExerciseVisibilityToggle sao arquivos novos — Executor cria dentro do diretorio de componentes existente. Preview de midia pode ser placeholder img/video se dados nao estiverem populados.

## Riscos
- Tipo Exercise no FE pode nao ter campos scope/visibility_mode/media — Executor deve adicionar ao tipo/interface em exercises.ts ou types existentes
- Chamadas de ACL requerem error handling para 403/404 — Executor deve tratar estados de erro na UI

## Análise de Impacto
- **exercises.ts (lido)**: Interface Exercise sem scope/visibility_mode. Sem funções ACL/copy-to-org.
- **ExerciseCard.tsx (lido)**: Sem badge scope. Props: exercise, tags, isFavorite, onToggleFavorite, onClick, isDragging.
- **ExerciseACLModal.tsx**: Não existe — criar.
- **ExerciseVisibilityToggle.tsx**: Não existe — criar.
- **Mudanças**:
  1. exercises.ts: ADD scope/visibility_mode ao interface Exercise; ADD ExerciseACLEntry interface; ADD copyExerciseToOrg, patchExerciseVisibility, getExerciseACL, addUserToACL, removeUserFromACL
  2. ExerciseCard.tsx: ADD scope badge (SYSTEM=azul/ORG=cinza); ADD botão Duplicar para scope=SYSTEM; ADD onCopyToOrg, onManageACL, onToggleVisibility props; ADD lógica RBAC (exibir ações apenas se isCreator)
  3. ExerciseACLModal.tsx: CRIAR modal com lista ACL (GET /acl), add user (POST /acl), remove user (DELETE /acl/{user_id})
  4. ExerciseVisibilityToggle.tsx: CRIAR toggle org_wide|restricted (PATCH /visibility)
- **RBAC FE**: Ações de edição visíveis apenas quando exercise.created_by_user_id === currentUserId
- **Sem mudanças no BE**.

---
## Carimbo de Execução
_(Gerado por hb report)_

### Execução Executor em b123a58
**Status Executor**: 🏗️ EM_EXECUCAO
**Comando**: `python -c "import os; b='Hb Track - Frontend'; c1=open(os.path.join(b,'src','lib','api','exercises.ts')).read(); assert 'copy-to-org' in c1 or 'copyExercise' in c1,'exercises.ts missing copy-to-org'; assert 'acl' in c1.lower(),'exercises.ts missing ACL'; c2=open(os.path.join(b,'src','components','training','exercises','ExerciseCard.tsx')).read(); assert 'scope' in c2 or 'SYSTEM' in c2,'ExerciseCard missing scope'; assert os.path.exists(os.path.join(b,'src','components','training','exercises','ExerciseACLModal.tsx')),'ExerciseACLModal missing'; print('PASS AR_184')"`
**Exit Code**: 0
**Timestamp UTC**: 2026-03-01T03:24:25.532148+00:00
**Behavior Hash**: a038f04e873dce35696016e055c90a9b8915fa533881588c66090a5afbc308ac
**Evidence File**: `docs/hbtrack/evidence/AR_184/executor_main.log`
**Python Version**: 3.11.9


### Verificacao Testador em b123a58
**Status Testador**: ✅ SUCESSO
**Consistency**: OK
**Triple-Run**: OK (3x)
**Exit Testador**: 0 | **Exit Executor**: 0
**TESTADOR_REPORT**: `_reports/testador/AR_184_b123a58/result.json`

### Selo Humano em b123a58
**Status Humano**: ✅ VERIFICADO
**Timestamp UTC**: 2026-03-01T03:49:20.783080+00:00
**Motivo**: —
**TESTADOR_REPORT**: `_reports/testador/AR_184_b123a58/result.json`
**Evidence File**: `docs/hbtrack/evidence/AR_184/executor_main.log`
