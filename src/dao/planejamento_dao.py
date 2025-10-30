# src/dao/planejamento_dao.py
import sqlite3
from datetime import date, datetime, timedelta
from typing import List, Optional
from src.dao.db import get_connection
from src.model.planejamento import Planejamento
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento
from src.dao import manutencao_dao

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
            last_gerada DATE,
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
        (tipo, descricao, frequencia, dias_previstos, data_inicial, last_gerada, criticidade, responsavel_id, equipamento_id, estagio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        planejamento.tipo,
        planejamento.descricao,
        planejamento.frequencia,
        planejamento.dias_previstos,
        planejamento.data_inicial,
        planejamento.last_gerada,
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
     SELECT p.id, p.tipo, p.descricao, p.frequencia, p.dias_previstos, p.data_inicial, p.criticidade, p.last_gerada, p.estagio,
         u.id, u.nome, u.login, u.senha, u.perfil, u.contato, u.status,
         e.id, e.nome, e.tipo, e.numero_serie, e.setor_id, e.status, e.fabricante, e.data_aquisicao
        FROM planejamentos p
        LEFT JOIN usuarios u ON p.responsavel_id = u.id
        LEFT JOIN equipamentos e ON p.equipamento_id = e.id
    """)
    rows = cur.fetchall()
    planejamentos = []
    for row in rows:
        responsavel = Usuario(
            id=row[9], nome=row[10], login=row[11], senha=row[12],
            perfil=row[13], contato=row[14], status=row[15]
        ) if row[9] else None

        equipamento = Equipamento(
            id=row[16], nome=row[17], tipo=row[18], numero_serie=row[19],
            setor=row[20], status=row[21], fabricante=row[22], data_aquisicao=row[23]
        ) if row[16] else None

        # índices: 0..8 -> planejamento, 9..15 -> usuario, 16..23 -> equipamento
        last_gerada = row[7]
        # converter string de data para date se necessário
        if isinstance(last_gerada, str):
            try:
                last_gerada = datetime.strptime(last_gerada.split('T')[0], "%Y-%m-%d").date()
            except Exception:
                last_gerada = None

        planejamento = Planejamento(
            id=row[0],
            tipo=row[1],
            descricao=row[2],
            frequencia=row[3],
            dias_previstos=row[4],
            data_inicial=row[5],
            criticidade=row[6],
            last_gerada=last_gerada,
            responsavel=responsavel,
            equipamento=equipamento,
            estagio=row[8] if len(row) > 8 else None
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
            last_gerada=?, responsavel_id=?, equipamento_id=?, estagio=?
        WHERE id=?
    """, (
        planejamento.tipo,
        planejamento.descricao,
        planejamento.frequencia,
        planejamento.dias_previstos,
        planejamento.data_inicial,
        planejamento.criticidade,
        planejamento.last_gerada,
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


def buscar_planejamento_por_id(planejamento_id: int) -> Optional[Planejamento]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.tipo, p.descricao, p.frequencia, p.dias_previstos, p.data_inicial, p.criticidade, p.last_gerada, p.estagio,
            u.id, u.nome, u.login, u.senha, u.perfil, u.contato, u.status,
            e.id, e.nome, e.tipo, e.numero_serie, e.setor_id, e.status, e.fabricante, e.data_aquisicao
        FROM planejamentos p
        LEFT JOIN usuarios u ON p.responsavel_id = u.id
        LEFT JOIN equipamentos e ON p.equipamento_id = e.id
        WHERE p.id = ?
    """, (planejamento_id,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    responsavel = Usuario(
        id=row[9], nome=row[10], login=row[11], senha=row[12],
        perfil=row[13], contato=row[14], status=row[15]
    ) if row[9] else None

    equipamento = Equipamento(
        id=row[16], nome=row[17], tipo=row[18], numero_serie=row[19],
        setor=row[20], status=row[21], fabricante=row[22], data_aquisicao=row[23]
    ) if row[16] else None

    last_gerada = row[7]
    if isinstance(last_gerada, str):
        try:
            last_gerada = datetime.strptime(last_gerada.split('T')[0], "%Y-%m-%d").date()
        except Exception:
            last_gerada = None

    planejamento = Planejamento(
        id=row[0],
        tipo=row[1],
        descricao=row[2],
        frequencia=row[3],
        dias_previstos=row[4],
        data_inicial=row[5],
        criticidade=row[6],
        last_gerada=last_gerada,
        responsavel=responsavel,
        equipamento=equipamento,
        estagio=row[8] if len(row) > 8 else None
    )
    conn.close()
    return planejamento


def gerar_manutencoes_automaticas():
    """Verifica planejamentos ativos e gera manutenções quando a data prevista for alcançada.
    A função atualiza o campo last_gerada para avançar o próximo agendamento.
    """
    planejamentos = listar_planejamentos()
    hoje = date.today()
    for p in planejamentos:
        # precisa ter configuração mínima
        if not p.data_inicial:
            continue

        # verifica usando a lógica do próprio modelo
        try:
            if not p.deve_gerar(hoje):
                continue
        except Exception:
            continue

        proxima = p.proxima_data()
        if not proxima:
            continue

        # cria uma manutenção com data prevista como hoje (indicando que foi gerada hoje)
        manutencao = manutencao_dao.Manutencao(
            id=None,
            tipo=p.tipo,
            equipamento=p.equipamento,
            responsavel=p.responsavel,
            data_prevista=hoje,
            documento=None,
            acoes_realizadas=None,
            observacoes=(p.descricao or "") + f" (Gerada automaticamente a partir do planejamento; data original: {proxima})",
            prioridade=p.criticidade,
            status='Programada'
        )
        # associe o planejamento antes de inserir para que o DAO persista planejamento_id
        manutencao.planejamento = p
        try:
            manutencao_dao.inserir_manutencao(manutencao)
        except Exception:
            # não conseguir inserir a manutenção, passar para o próximo planejamento
            continue

        # avançar last_gerada através do próprio objeto Planejamento e persistir
        try:
            p.avançar_last_gerada()
            atualizar_planejamento(p)
        except Exception:
            # ignore falhas de atualização e continue
            pass
