from src.dao.db import get_connection
from src.model.usuario import Usuario
import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, login, perfil, contato, status FROM usuarios")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [Usuario(*row) for row in rows]

def criar_tabela_usuario():
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

def verificar_login(login, senha):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nome, perfil FROM usuarios WHERE login=? AND senha=?",
        (login, hash_senha(senha))
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id": row[0], "nome": row[1], "perfil": row[2]}
    return None

def atualizar_usuario(id, nome=None, login=None, senha=None, perfil=None, contato=None, status=None):
    conn = get_connection()
    cur = conn.cursor()
    fields = []
    params = []

    if nome is not None:
        fields.append("nome=?")
        params.append(nome)
    if login is not None:
        fields.append("login=?")
        params.append(login)
    if senha:
        fields.append("senha=?")
        params.append(hash_senha(senha))
    if perfil is not None:
        fields.append("perfil=?")
        params.append(perfil)
    if contato is not None:
        fields.append("contato=?")
        params.append(contato)
    if status is not None:
        fields.append("status=?")
        params.append(status)

    params.append(id)
    cur.execute(f"UPDATE usuarios SET {', '.join(fields)} WHERE id=?", params)
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
