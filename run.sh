#!/bin/bash
# Script para rodar a interface do Projeto-tematico no Linux

# Garantir que o Python veja a raiz do projeto
export PYTHONPATH=$(pwd)

# Rodar o módulo principal
python3 -m src.ui

