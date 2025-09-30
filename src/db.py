import sqlite3
import hashlib

DB_NAME = "manusys.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def criar_tabela():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT CHECK(perfil IN ('Administrador', 'Técnico', 'Gestor', 'Usuário')) NOT NULL,
            contato TEXT,
            status TEXT CHECK(status IN ('Ativo', 'Inativo')) NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def inserir_usuario(nome, login, senha, perfil, contato, status="Ativo"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarios (nome, login, senha, perfil, contato, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, login, hash_senha(senha), perfil, contato, status))
    conn.commit()
    cur.close()
    conn.close()

def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, login, perfil, contato, status FROM usuarios")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return dados

def atualizar_usuario(id, nome, login, senha, perfil, contato, status):
    conn = get_connection()
    cur = conn.cursor()
    if senha:  # se usuário digitou nova senha
        #salt = gerar_salt()
        #senha_hash = hash_senha(senha, salt)
        senha_hash = hash_senha(senha)
        cur.execute("""
            UPDATE usuarios
            SET nome=?, login=?, senha=?, perfil=?, contato=?, status=?
            WHERE id=?
        """, (nome, login, senha_hash, perfil, contato, status, id))
    else:  # não alterar senha
        cur.execute("""
            UPDATE usuarios
            SET nome=?, login=?, perfil=?, contato=?, status=?
            WHERE id=?
        """, (nome, login, perfil, contato, status, id))
    conn.commit()
    cur.close()
    conn.close()


def excluir_usuario(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=?", (id,))
    conn.commit()
    cur.close()
    conn.close()

def verificar_login(email, senha):
    """
    Retorna um dicionário do usuário se o login for válido, ou None se inválido.
    """
    conn = get_connection()  # corrigido para usar a função existente
    cursor = conn.cursor()
    senha_hash = hash_senha(senha)  # gera hash da senha informada
    cursor.execute(
        "SELECT id, nome, perfil FROM usuarios WHERE login = ? AND senha = ?",
        (email, senha_hash)
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return {"id": row[0], "nome": row[1], "perfil": row[2]}
    else:
        return None

