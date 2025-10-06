from src.dao.db import get_connection
from src.model.usuario import Usuario
import hashlib

def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()

def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, login, senha, perfil, contato, status FROM usuarios")
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

def inserir_usuario(usuario: Usuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO usuarios (nome, login, senha, perfil, contato, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        usuario.nome,
        usuario.login,
        hash_senha(usuario.senha),
        usuario.perfil,
        usuario.contato,
        usuario.status
    ))
    conn.commit()
    cur.close()
    conn.close()

def verificar_login(login, senha):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nome, login, senha, perfil, contato, status FROM usuarios WHERE login=? AND senha=?",
        (login, hash_senha(senha))
    )
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return Usuario(*row)
    return None

def atualizar_usuario(usuario: Usuario):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE usuarios
        SET nome=?, login=?, senha=?, perfil=?, contato=?, status=?
        WHERE id=?
    """, (
        usuario.nome,
        usuario.login,
        hash_senha(usuario.senha) if usuario.senha else None,
        usuario.perfil,
        usuario.contato,
        usuario.status,
        usuario.id
    ))
    conn.commit()
    cur.close()
    conn.close()

def excluir_usuario(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM usuarios WHERE id=?", (usuario_id,))
    conn.commit()
    cur.close()
    conn.close()

def buscar_usuario_por_id(usuario_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, login, senha, perfil, contato, status FROM usuarios WHERE id=?", (usuario_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return Usuario(*row)
    return None

# APENAS PARA DESENVOLVIMENTO
def buscar_usuario_por_login(login):
    """
    Retorna um objeto Usuario pelo login, ou None se não existir.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, login, senha, perfil, contato, status FROM usuarios WHERE login=?", (login,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return Usuario(*row)
    return None

