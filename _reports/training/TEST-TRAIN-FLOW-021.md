# MANUAL_GUIADO: FLOW-TRAIN-021
Status: PASS
Descrição: Wellness gates conteúdo (atleta sem wellness bloqueado)
Passos: (1) Atleta acessa /athlete/training/[sessionId] sem ter enviado wellness pré. (2) Sistema exibe bloqueio de conteúdo (wellness gate). (3) Atleta envia wellness pré via /athlete/wellness-pre/[sessionId]. (4) Acessa novamente — conteúdo desbloqueado.
Resultado: Sem wellness pré: tela exibe aviso de bloqueio e não mostra treino. Após submissão de wellness: conteúdo liberado imediatamente. Nenhum crash crítico.
Critério: AC-021 PASS
