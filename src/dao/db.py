import sqlite3
from src.model.usuario import Usuario

DB_NAME = "manusys.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """Cria as tabelas se não existirem e garante que o admin exista"""
    from src.dao.usuario_dao import criar_tabela_usuario, inserir_usuario
    from src.dao.setor_dao import criar_tabela_setores
    from src.dao.equipamento_dao import criar_tabela_equipamento
    from src.dao.manutencao_dao import criar_tabela_manutencao

    criar_tabela_usuario()
    criar_tabela_setores()
    criar_tabela_equipamento()
    criar_tabela_manutencao()

    # garante usuário admin
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE login='admin'")
    admin = cur.fetchone()
    cur.close()
    conn.close()
        
    if not admin:
        usuario_admin = Usuario(
            id=None,
            nome="Administrador",
            login="admin",
            senha="admin",
            perfil="Administrador",
            contato="5499123456789",
            status="Ativo"
        )
        inserir_usuario(usuario_admin)
        print("Usuário admin criado (login: admin / senha: admin).")

    else:
        print("Usuário admin já existe.")
