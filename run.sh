#!/bin/bash
# Script para rodar a interface do Projeto-tematico no Linux

# Caminho para o virtualenv
VENV_DIR="venv"

# Ativar o virtualenv
if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
else
    echo "Virtualenv não encontrado em $VENV_DIR"
    exit 1
fi

# Garantir que o Python veja a raiz do projeto
export PYTHONPATH=$(pwd)

# Rodar o módulo principal
python3 -m src.ui

