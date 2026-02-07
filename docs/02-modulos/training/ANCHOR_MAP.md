# Mapa de Âncoras — Módulo de Treinamento


1) Tabela — Fluxo/ação → operationId(s) → tabelas/colunas → invariantes aplicáveis (INV-*)

Fluxo/ação (UI)	operationId(s)	tabelas/colunas (âncora)	invariantes aplicáveis
Listar templates	list_session_templates_api_v1_session_templates_get	session_templates (âncora: ck_session_templates_focus_sum)	PRETENDIDA (nenhuma invariável confirmada específica para leitura)
Criar template	create_session_template_api_v1_session_templates_post	session_templates (âncora: ck_session_templates_focus_sum)	INV-TRAIN-001 (âncora: ck_session_templates_focus_sum)
Visualizar template	get_session_template_api_v1_session_templates__template_id__get	session_templates (âncora: ck_session_templates_focus_sum)	PRETENDIDA (nenhuma invariável confirmada específica para leitura)
Atualizar template	update_session_template_api_v1_session_templates__template_id__patch	session_templates (âncora: ck_session_templates_focus_sum)	INV-TRAIN-001 (âncora: ck_session_templates_focus_sum)
Excluir template	delete_session_template_api_v1_session_templates__template_id__delete	session_templates (âncora: ck_session_templates_focus_sum)	PRETENDIDA (nenhuma invariável confirmada específica para delete)
Favoritar template	toggle_favorite_template_api_v1_session_templates__template_id__favorite_patch	session_templates (âncora: ck_session_templates_focus_sum)	PRETENDIDA (nenhuma invariável confirmada específica para favorite)

2) Lacunas reais (sem suposições)
UI de templates (componentes/rotas frontend) PRETENDIDA — sem âncora file:line no evidence pack.
Campos exibidos/editáveis no Template UI PRETENDIDA — sem âncora file:line ou constraint específica no evidence pack.
Comportamento de delete (soft vs hard) no Template UI PRETENDIDA — sem âncora no evidence pack.

3) Perguntas que precisam decisão (máx 5)

Quais campos de session_templates a UI deve expor/editar?
O “favoritar template” é por usuário, por organização, ou global?
O delete deve ser soft delete ou hard delete para templates?
A UI deve validar localmente o limite de foco ≤120% (INV-TRAIN-001) ou confiar apenas no backend?
Há necessidade de versionamento/duplicação de templates na UI (além do CRUD atual)?