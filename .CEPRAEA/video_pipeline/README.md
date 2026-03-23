# Pacote Operacional do Pipeline de Video

Este diretorio contem os artefatos minimos para operar o pipeline com controle de custo:

- `config_video.json`: stack, limites e teto financeiro
- `cenas_premium_autorizadas.csv`: allowlist de geracao paga
- `logs/geracao_log.csv`: ledger obrigatorio de requests pagos
- `logs/render_log.txt`: log de renderizacao
- `scripts/preflight_pipeline.py`: valida ambiente e arquivos
- `scripts/verificar_orcamento.py`: trava o teto antes de cada chamada paga

Regra de uso:

1. executar `preflight_pipeline.py`
2. executar `verificar_orcamento.py`
3. simular a proxima chamada com `verificar_orcamento.py --next-scene ... --next-seconds ...`
4. somente depois chamar o Veo
