# src/dao/planejamento_dao.py
import sqlite3
from datetime import date
from typing import List, Optional
from src.dao.db import get_connection
from src.view.planejamento import Planejamento
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento

def criar_tabela_planejamento():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS planejamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('Preventiva','Corretiva','Preditiva')) NOT NULL,
            descricao TEXT NOT NULL,
            frequencia TEXT NOT NULL,
            dias_previstos INTEGER NOT NULL,
            data_inicial DATE NOT NULL,
            criticidade TEXT,
            responsavel_id INTEGER,
            equipamento_id INTEGER,
            estagio TEXT,
            FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
            FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id)
        )
    """)
    conn.commit()
    conn.close()

def inserir_planejamento(planejamento: Planejamento) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO planejamentos
        (tipo, descricao, frequencia, dias_previstos, data_inicial, criticidade, responsavel_id, equipamento_id, estagio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        planejamento.tipo,
        planejamento.descricao,
        planejamento.frequencia,
        planejamento.dias_previstos,
        planejamento.data_inicial,
        planejamento.criticidade,
        planejamento.responsavel.id if planejamento.responsavel else None,
        planejamento.equipamento.id if planejamento.equipamento else None,
        planejamento.estagio
    ))
    planejamento_id = cur.lastrowid
    conn.commit()
    conn.close()
    return planejamento_id

def listar_planejamentos() -> List[Planejamento]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.tipo, p.descricao, p.frequencia, p.dias_previstos, p.data_inicial,
               p.criticidade,
               u.id, u.nome, u.login, u.senha, u.perfil, u.contato, u.status,
               e.id, e.nome, e.tipo, e.numero_serie, e.setor, e.status, e.fabricante, e.data_aquisicao
        FROM planejamentos p
        LEFT JOIN usuarios u ON p.responsavel_id = u.id
        LEFT JOIN equipamentos e ON p.equipamento_id = e.id
    """)
    rows = cur.fetchall()
    planejamentos = []
    for row in rows:
        responsavel = Usuario(
            id=row[7], nome=row[8], login=row[9], senha=row[10],
            perfil=row[11], contato=row[12], status=row[13]
        ) if row[7] else None

        equipamento = Equipamento(
            id=row[14], nome=row[15], tipo=row[16], numero_serie=row[17],
            setor=row[18], status=row[19], fabricante=row[20], data_aquisicao=row[21]
        ) if row[14] else None

        planejamento = Planejamento(
            id=row[0],
            tipo=row[1],
            descricao=row[2],
            frequencia=row[3],
            dias_previstos=row[4],
            data_inicial=row[5],
            criticidade=row[6],
            responsavel=responsavel,
            equipamento=equipamento,
            estagio=row[22] if len(row) > 22 else None
        )
        planejamentos.append(planejamento)
    conn.close()
    return planejamentos

def atualizar_planejamento(planejamento: Planejamento) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE planejamentos SET
            tipo=?, descricao=?, frequencia=?, dias_previstos=?, data_inicial=?, criticidade=?, 
            responsavel_id=?, equipamento_id=?, estagio=?
        WHERE id=?
    """, (
        planejamento.tipo,
        planejamento.descricao,
        planejamento.frequencia,
        planejamento.dias_previstos,
        planejamento.data_inicial,
        planejamento.criticidade,
        planejamento.responsavel.id if planejamento.responsavel else None,
        planejamento.equipamento.id if planejamento.equipamento else None,
        planejamento.estagio,
        planejamento.id
    ))
    conn.commit()
    conn.close()

def excluir_planejamento(planejamento_id: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM planejamentos WHERE id=?", (planejamento_id,))
    conn.commit()
    conn.close()
