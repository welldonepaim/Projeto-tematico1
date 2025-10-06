# src/dao/equipamento_dao.py

from src.dao import db
from src.model.equipamento import Equipamento
from src.dao import setor_dao


def criar_tabela_equipamento():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS equipamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tipo TEXT NOT NULL,
            numero_serie TEXT UNIQUE,
            setor_id INTEGER,
            status TEXT CHECK(status IN ('Disponível', 'Em Manutenção', 'Indisponível')) NOT NULL DEFAULT 'Disponível',
            fabricante TEXT,
            data_aquisicao DATE
        )
    """)
    conn.commit()
    conn.close()


def inserir_equipamento(equipamento: Equipamento):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO equipamentos (nome, tipo, numero_serie, setor_id, status, fabricante, data_aquisicao)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        equipamento.nome,
        equipamento.tipo,
        equipamento.numero_serie,
        equipamento.setor.id,
        equipamento.status,
        equipamento.fabricante,
        equipamento.data_aquisicao
    ))
    conn.commit()
    conn.close()


def listar_equipamentos():
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, tipo, numero_serie, setor_id, status, fabricante, data_aquisicao
        FROM equipamentos
    """)
    rows = cur.fetchall()
    conn.close()
    return [Equipamento(*row) for row in rows]


def buscar_equipamento_por_id(equipamento_id: int):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nome, tipo, numero_serie, setor_id, status, fabricante, data_aquisicao
        FROM equipamentos
        WHERE id = ?
    """, (equipamento_id,))
    row = cur.fetchone()
    conn.close()
    return Equipamento(*row) if row else None


def atualizar_equipamento(equipamento: Equipamento):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE equipamentos
        SET nome=?, tipo=?, numero_serie=?, setor_id=?, status=?, fabricante=?, data_aquisicao=?
        WHERE id=?
    """, (
        equipamento.nome,
        equipamento.tipo,
        equipamento.numero_serie,
        equipamento.setor.id,
        equipamento.status,
        equipamento.fabricante,
        equipamento.data_aquisicao,
        equipamento.id
    ))
    conn.commit()
    conn.close()


def excluir_equipamento(equipamento_id: int):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM equipamentos WHERE id=?", (equipamento_id,))
    conn.commit()
    conn.close()
