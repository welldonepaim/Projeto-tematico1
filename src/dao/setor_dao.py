from src.dao.db import get_connection

def criar_tabela_setor():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS setores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            responsavel TEXT,
            status TEXT CHECK(status IN ('Ativo','Inativo')) NOT NULL DEFAULT 'Ativo'
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def inserir_setor(nome, responsavel=None, status="Ativo"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO setores (nome, responsavel, status) VALUES (?, ?, ?)",
                (nome, responsavel, status))
    conn.commit()
    cur.close()
    conn.close()

def listar_setores():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, responsavel FROM setores WHERE status='Ativo' ORDER BY id")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return dados

def atualizar_setor(setor_id, nome=None, responsavel=None, status=None):
    conn = get_connection()
    cur = conn.cursor()
    fields = []
    params = []

    if nome is not None:
        fields.append("nome=?")
        params.append(nome)
    if responsavel is not None:
        fields.append("responsavel=?")
        params.append(responsavel)
    if status is not None:
        fields.append("status=?")
        params.append(status)

    params.append(setor_id)
    cur.execute(f"UPDATE setores SET {', '.join(fields)} WHERE id=?", params)
    conn.commit()
    cur.close()
    conn.close()

def desativar_setor(setor_id):
    atualizar_setor(setor_id, status="Inativo")
