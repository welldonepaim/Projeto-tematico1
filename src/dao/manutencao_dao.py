import sqlite3
from typing import List, Optional
from datetime import date, datetime
from src.dao.db import get_connection
from src.model.manutencao import Manutencao
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento


def criar_tabela_manutencao():
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS manutencoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT CHECK(tipo IN ('Preventiva','Corretiva','Preditiva')) NOT NULL,
                equipamento_id INTEGER NOT NULL,
                responsavel_id INTEGER NOT NULL,
                data_prevista DATE NOT NULL,
                documento TEXT,
                acoes_realizadas TEXT,
                observacoes TEXT,
                status TEXT CHECK(status IN (
                    'Programada','Pendente','Em Análise','Em Manutenção','Concluída','Revisada','Disponível','Descontinuado'
                )) NOT NULL,
                prioridade TEXT CHECK(prioridade IN ('Urgente','Alta','Média','Baixa','Sem Prioridade')) NOT NULL DEFAULT 'Sem Prioridade',
                FOREIGN KEY (equipamento_id) REFERENCES equipamentos(id),
                FOREIGN KEY (responsavel_id) REFERENCES usuarios(id)
            )
        """)
        conn.commit()


def inserir_manutencao(manutencao: Manutencao) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO manutencoes 
            (tipo, equipamento_id, responsavel_id, data_prevista, documento, 
             acoes_realizadas, observacoes, status, prioridade)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            manutencao.tipo,
            manutencao.equipamento.id,
            manutencao.responsavel.id,
            manutencao.data_prevista.isoformat() if manutencao.data_prevista else None,
            manutencao.documento,
            manutencao.acoes_realizadas,
            manutencao.observacoes,
            manutencao.status,
            manutencao.prioridade or "Sem Prioridade"
        ))
        return cur.lastrowid


def _parse_date(data_str: Optional[str]) -> Optional[date]:
    """Converte string de data do SQLite para datetime.date"""
    if not data_str:
        return None
    data_str = str(data_str)
    if "T" in data_str:
        data_str = data_str.split("T")[0]
    try:
        return datetime.strptime(data_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def listar_manutencoes() -> List[Manutencao]:
    manutencoes = []
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.tipo, 
                   e.id, e.nome, e.tipo, e.numero_serie, e.setor_id, e.status, e.fabricante, e.data_aquisicao,
                   u.id, u.nome, u.login, u.senha, u.perfil, u.contato, u.status,
                   m.data_prevista, m.documento, m.acoes_realizadas, m.observacoes, m.status, m.prioridade
            FROM manutencoes m
            JOIN equipamentos e ON m.equipamento_id = e.id
            JOIN usuarios u ON m.responsavel_id = u.id
        """)
        rows = cur.fetchall()
        for row in rows:
            equipamento = Equipamento(
                id=row[2], nome=row[3], tipo=row[4], numero_serie=row[5],
                setor=row[6], status=row[7], fabricante=row[8], data_aquisicao=row[9]
            )
            usuario = Usuario(
                id=row[10], nome=row[11], login=row[12], senha=row[13],
                perfil=row[14], contato=row[15], status=row[16]
            )
            data_prevista = _parse_date(row[17])

            manutencao = Manutencao(
                id=row[0], tipo=row[1],
                equipamento=equipamento,
                responsavel=usuario,
                data_prevista=data_prevista,
                documento=row[18],
                acoes_realizadas=row[19],
                observacoes=row[20],
                status=row[21],
                prioridade=row[22]
            )
            manutencoes.append(manutencao)
    return manutencoes


def buscar_manutencao_por_id(manutencao_id: int) -> Optional[Manutencao]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.id, m.tipo, 
                   e.id, e.nome, e.tipo, e.numero_serie, e.setor_id, e.status, e.fabricante, e.data_aquisicao,
                   u.id, u.nome, u.login, u.senha, u.perfil, u.contato, u.status,
                   m.data_prevista, m.documento, m.acoes_realizadas, m.observacoes, m.status, m.prioridade
            FROM manutencoes m
            JOIN equipamentos e ON m.equipamento_id = e.id
            JOIN usuarios u ON m.responsavel_id = u.id
            WHERE m.id = ?
        """, (manutencao_id,))
        row = cur.fetchone()
        if row:
            equipamento = Equipamento(
                id=row[2], nome=row[3], tipo=row[4], numero_serie=row[5],
                setor=row[6], status=row[7], fabricante=row[8], data_aquisicao=row[9]
            )
            usuario = Usuario(
                id=row[10], nome=row[11], login=row[12], senha=row[13],
                perfil=row[14], contato=row[15], status=row[16]
            )
            data_prevista = _parse_date(row[17])

            return Manutencao(
                id=row[0], tipo=row[1],
                equipamento=equipamento,
                responsavel=usuario,
                data_prevista=data_prevista,
                documento=row[18],
                acoes_realizadas=row[19],
                observacoes=row[20],
                status=row[21],
                prioridade=row[22]
            )
    return None


def atualizar_manutencao(manutencao: Manutencao) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            UPDATE manutencoes SET
            tipo=?, equipamento_id=?, responsavel_id=?, data_prevista=?,
            documento=?, acoes_realizadas=?, observacoes=?, status=?, prioridade=?
            WHERE id=?
        """, (
            manutencao.tipo,
            manutencao.equipamento.id,
            manutencao.responsavel.id,
            manutencao.data_prevista.isoformat() if manutencao.data_prevista else None,
            manutencao.documento,
            manutencao.acoes_realizadas,
            manutencao.observacoes,
            manutencao.status,
            manutencao.prioridade or "Sem Prioridade",
            manutencao.id
        ))


def excluir_manutencao(manutencao_id: int) -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM manutencoes WHERE id=?", (manutencao_id,))

