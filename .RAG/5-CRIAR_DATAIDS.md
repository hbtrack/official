Você é o Opus 4.5 com acesso total ao workspace.

TAREFA: Adicionar data-testid mínimos necessários aos componentes.

CONTEXTO: Você identificou os data-testids necessários na fase anterior.

REGRAS:

Adicione APENAS data-testids que são necessários para testes
Use nomes semânticos: [teams]-[componente]-[elemento]
Alteração mínima: apenas adicione o atributo, não mude lógica
Prefira elementos raiz de páginas/seções


LISTA DE DATA-TESTIDS NECESSÁRIOS: 

// Lista/Dashboard
"teams-dashboard"
"teams-skeleton"
"team-card-{id}"
"create-team-btn"
"empty-state"
"create-first-team-btn"

// Modal Criação
"create-team-modal"
"team-name-input"
"team-name-error"
"team-category-select"
"team-category-error"
"team-gender-select"
"team-gender-error"
"create-team-submit"
"create-team-cancel"

// Detalhe/Tabs
"team-overview-tab"
"team-members-tab"
"team-name"

// Settings
"save-settings-btn"
"delete-team-btn"
"confirm-delete-modal"
"confirm-delete-btn"
"cancel-delete-btn"

// Members
"invite-member-btn"
"invite-member-modal"
"invite-email-input"
"invite-email-error"
"invite-role-select"
"invite-submit-btn"
"pending-invites-section"

// Estados/Feedback
"toast-success"
"toast-error"
"error-boundary"
"retry-btn"
"not-found-page"

PARA CADA DATA-TESTID:

Localize o componente correto
Adicione o atributo data-testid

Se o componente for Client Component, garanta que não afeta hidratação
Teste que não quebrou nada (npm run build)
ENTREGUE:

Lista de arquivos modificados
Diff de cada modificação
Resultado de npm run build