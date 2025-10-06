import sqlite3
from typing import List, Optional
from datetime import date
from src.dao.db import get_connection
from src.model.manutencao import Manutencao
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento


def criar_tabela_manutencao():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS manutencoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('Preventiva','Corretiva','Preditiva')) NOT NULL,
            equipamento_id INTEGER NOT NULL,
            responsavel_id INTEGER NOT NULL,
            data_prevista DATE NOT NULL,
            data_execucao DATE,
            documento TEXT,
            acoes_realizadas TEXT,
            observacoes TEXT,
            status TEXT CHECK(status IN (
                'Pendente','Em Análise','Em Manutenção','Concluída','Revisada','Disponível','Descontinuado'
            )) NOT NULL,
            FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id),
            FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
        )
    """)
    conn.commit()
    conn.close()


def inserir_manutencao(manutencao: Manutencao) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO manutencoes 
        (tipo, equipamento_id, responsavel_id, data_prevista, data_execucao, documento, 
         acoes_realizadas, observacoes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        manutencao.tipo,
        manutencao.equipamento.id,
        manutencao.responsavel.id,
        manutencao.data_prevista,
        manutencao.data_execucao,
        manutencao.documento,
        manutencao.acoes_realizadas,
        manutencao.observacoes,
        manutencao.status
    ))
    manutencao_id = cur.lastrowid
    conn.commit()
    conn.close()
    return manutencao_id


def listar_manutencoes() -> List[Manutencao]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.tipo, 
               e.id, e.nome, e.tipo, e.numero_serie, e.setor_id, e.status, e.fabricante, e.data_aquisicao,
               u.id, u.nome, u.login, u.senha, u.perfil, u.contato, u.status,
               m.data_prevista, m.data_execucao, m.documento, m.acoes_realizadas, m.observacoes, m.status
        FROM manutencoes m
        JOIN equipamentos e ON m.equipamento_id = e.id
        JOIN usuarios u ON m.responsavel_id = u.id
    """)
    rows = cur.fetchall()
    manutencoes = []
    for row in rows:
        equipamento = Equipamento(
            id=row[2], nome=row[3], tipo=row[4], numero_serie=row[5],
            setor=row[6], status=row[7], fabricante=row[8], data_aquisicao=row[9]
        )
        usuario = Usuario(
            id=row[10], nome=row[11], login=row[12], senha=row[13],
            perfil=row[14], contato=row[15], status=row[16]
        )
        manutencao = Manutencao(
            id=row[0], tipo=row[1],
            equipamento=equipamento,
            responsavel=usuario,
            data_prevista=row[17],
            data_execucao=row[18],
            documento=row[19],
            acoes_realizadas=row[20],
            observacoes=row[21],
            status=row[22]
        )
        manutencoes.append(manutencao)
    cur.close()
    conn.close()
    return manutencoes


def buscar_manutencao_por_id(manutencao_id: int) -> Optional[Manutencao]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.tipo, 
               e.id, e.nome, e.tipo, e.numero_serie, e.setor, e.status, e.fabricante, e.data_aquisicao,
               u.id, u.nome, u.login, u.senha, u.perfil, u.contato, u.status,
               m.data_prevista, m.data_execucao, m.documento, m.acoes_realizadas, m.observacoes, m.status
        FROM manutencoes m
        JOIN equipamentos e ON m.equipamento_id = e.id
        JOIN usuarios u ON m.responsavel_id = u.id
        WHERE m.id = ?
    """, (manutencao_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        equipamento = Equipamento(
            id=row[2], nome=row[3], tipo=row[4], numero_serie=row[5],
            setor=row[6], status=row[7], fabricante=row[8], data_aquisicao=row[9]
        )
        usuario = Usuario(
            id=row[10], nome=row[11], login=row[12], senha=row[13],
            perfil=row[14], contato=row[15], status=row[16]
        )
        return Manutencao(
            id=row[0], tipo=row[1],
            equipamento=equipamento,
            responsavel=usuario,
            data_prevista=row[17],
            data_execucao=row[18],
            documento=row[19],
            acoes_realizadas=row[20],
            observacoes=row[21],
            status=row[22]
        )
    return None


def atualizar_manutencao(manutencao: Manutencao) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE manutencoes SET
            tipo=?, equipamento_id=?, responsavel_id=?, data_prevista=?, data_execucao=?, 
            documento=?, acoes_realizadas=?, observacoes=?, status=?
        WHERE id=?
    """, (
        manutencao.tipo,
        manutencao.equipamento.id,
        manutencao.responsavel.id,
        manutencao.data_prevista,
        manutencao.data_execucao,
        manutencao.documento,
        manutencao.acoes_realizadas,
        manutencao.observacoes,
        manutencao.status,
        manutencao.id
    ))
    conn.commit()
    conn.close()


def excluir_manutencao(manutencao_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM manutencoes WHERE id=?", (manutencao_id,))
    conn.commit()
    conn.close()
