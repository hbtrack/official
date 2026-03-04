# MANUAL_GUIADO: FLOW-TRAIN-013
Status: PASS
Descrição: Visualizar rankings wellness e top performers
Passos: (1) Treinador acessa /training/rankings. (2) Visualiza ranking de atletas por RSE médio. (3) Navega para /training/top-performers/[teamId]. (4) Acessa lista de top performers via CONTRACT-076.
Resultado: Rankings carregam corretamente. Lista top performers via `/teams/{id}/wellness-top-performers` (CONTRACT-076). Filtros por período e equipe funcionam. Nenhum crash crítico.
Critério: AC-013 PASS
