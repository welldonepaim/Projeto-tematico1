import sqlite3

DB_NAME = "manusys.db"  # arquivo local do banco

def get_connection():
    return sqlite3.connect(DB_NAME)

def criar_tabela():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            email TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def inserir_usuario(nome, email):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO usuarios (nome, email) VALUES (?, ?)", (nome, email))
    conn.commit()
    cur.close()
    conn.close()

def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, email FROM usuarios")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return dados
