#!/bin/bash
# HB Track - WSL Environment Setup
# Carrega nvm e configura o ambiente para desenvolvimento

export NVM_DIR="/home/davis/.nvm"
[ -s "/nvm.sh" ] && \. "/nvm.sh"
[ -s "/bash_completion" ] && \. "/bash_completion"

# Ativa versão LTS do Node
nvm use default >/dev/null 2>&1

# Exibe versões
echo "✓ Environment ready:"
echo "  Node: "
echo "  Python: Python 3.12.3"
echo "  HB CLI: HB Track Protocol v1.3.0"
