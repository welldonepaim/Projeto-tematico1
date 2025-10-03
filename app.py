from src.view.ui import iniciar_interface
from src.dao.db import inicializar_banco

inicializar_banco()

if __name__ == "__main__":
    iniciar_interface()
