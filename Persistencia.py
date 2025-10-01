from Setor import Setor
import os
import json
class Persistencia:
    setores = []
    ARQUIVO = "setores.json"


    # Persistência de dados

    def carregar_dados():
        global setores
        if os.path.exists(ARQUIVO) and os.path.getsize(ARQUIVO) > 0:
            with open(ARQUIVO, "r", encoding="utf-8") as f:
                try:
                    dados = json.load(f)
                    setores = [Setor(**s) for s in dados]
                except json.JSONDecodeError:
                    setores = []
        atualizar_lista()

    def salvar_dados():
        with open(ARQUIVO, "w", encoding="utf-8") as f:
            json.dump([s.__dict__ for s in setores], f, indent=4, ensure_ascii=False)
    ######################################################################################

