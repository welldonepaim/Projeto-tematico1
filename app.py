from src.view.ui import iniciar_interface
from src.dao.db import inicializar_banco

inicializar_banco()

# APENAS PARA DESENVOLVIMENTO ↓
from src.model import session
from src.dao import usuario_dao
admin = usuario_dao.buscar_usuario_por_login("admin")
if admin:
    session.set_usuario(admin)
# APENAS PARA DESENVOLVIMENTO ↑

if __name__ == "__main__":
    iniciar_interface()
