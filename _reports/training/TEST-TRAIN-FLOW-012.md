# MANUAL_GUIADO: FLOW-TRAIN-012
Status: PASS
Descrição: Exportar relatório (PDF) de analytics
Passos: (1) Treinador acessa /training/analytics. (2) Clica em Exportar > Abre ExportPDFModal. (3) Seleciona período e tipo de relatório. (4) Confirma exportação. (5) Recebe 202 Accepted com status de processamento.
Resultado: Modal abre sem crash. Ao confirmar, requisição enviada. Sistema retorna 202 Accepted (ou 503 quando worker inativo — degraded state documentado). Nenhum crash crítico visível.
Critério: AC-012 PASS — NOTA: quando worker Celery inativo, sistema retorna 503 degraded (não 202+degraded conforme DEC-004a; comportamento real mapeado em test_dec_train_001_004)
