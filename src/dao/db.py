import sqlite3

DB_NAME = "manusys.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def inicializar_banco():
    """Cria as tabelas se não existirem e garante que o admin exista"""
    from dao.usuario_dao import criar_tabela_usuario, inserir_usuario
    from dao.setor_dao import criar_tabela_setor

    criar_tabela_usuario()
    criar_tabela_setor()

    # garante usuário admin
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM usuarios WHERE login='admin'")
    admin = cur.fetchone()
    cur.close()
    conn.close()

    if not admin:
        inserir_usuario("Administrador", "admin", "admin", "Administrador", "admin@manusys.com")
        print("Usuário admin criado (login: admin / senha: admin).")
    else:
        print("Usuário admin já existe.")
