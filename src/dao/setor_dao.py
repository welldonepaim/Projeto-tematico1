from src.dao.db import get_connection

def criar_tabela_setores():
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



def listar_setores():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, responsavel FROM setores WHERE status='Ativo' ORDER BY id")
    dados = cur.fetchall()
    cur.close()
    conn.close()
    return dados




def inserir_setor(nome, responsavel=None, status="Ativo"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO setores (nome, responsavel, status)
        VALUES (?, ?, ?)
    """, (nome, responsavel, status))
    conn.commit()
    cur.close()
    conn.close()



def atualizar_setor(setor_id, nome=None, responsavel=None, status=None, limpar_resp=False):
    conn = get_connection()
    cur = conn.cursor()

    if limpar_resp:
        cur.execute("UPDATE setores SET responsavel=NULL WHERE id=?", (setor_id,))
    elif nome is not None and responsavel is not None and status is not None:
        cur.execute("UPDATE setores SET nome=?, responsavel=?, status=? WHERE id=?",
                    (nome, responsavel, status, setor_id))
    elif nome is not None and responsavel is not None:
        cur.execute("UPDATE setores SET nome=?, responsavel=? WHERE id=?",
                    (nome, responsavel, setor_id))
    elif nome is not None:
        cur.execute("UPDATE setores SET nome=? WHERE id=?", (nome, setor_id))
    elif responsavel is not None:
        cur.execute("UPDATE setores SET responsavel=? WHERE id=?", (responsavel, setor_id))
    elif status is not None:
        cur.execute("UPDATE setores SET status=? WHERE id=?", (status, setor_id))

    conn.commit()
    cur.close()
    conn.close()

def desativar_setor(setor_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE setores SET status='Inativo' WHERE id=?", (setor_id,))
    conn.commit()
    cur.close()
    conn.close()
