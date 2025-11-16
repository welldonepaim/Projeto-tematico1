from dataclasses import dataclass
from typing import Optional
from datetime import date
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento
from src.model.planejamento import Planejamento


@dataclass
class Manutencao:
    id: Optional[int] = None  # ID no banco
    tipo: str = ""  # Preventiva / Corretiva / Preditiva
    equipamento: Optional[Equipamento] = None  # Equipamento já cadastrado
    responsavel: Optional[Usuario] = None  # Usuário já cadastrado
    data_prevista: Optional[date] = None  # Data prevista para execução
    data_execucao: Optional[date] = None  # Data real da execução
    documento: Optional[str] = None  # Caminho/arquivo do laudo
    acoes_realizadas: Optional[str] = None  # Ações executadas
    observacoes: Optional[str] = None  # Observações adicionais
    prioridade: Optional[str] = None  # nova prioridade
    status: str = "Pendente"  # Status inicial padrão
    planejamento: Optional[Planejamento] = None  # Planejamento associado (se for preventiva programada)

    TIPOS = ("Preventiva", "Corretiva", "Preditiva")
    STATUS = (
        "Pendente",
        "Em Análise",
        "Em Manutenção",
        "Concluída",
        
    )
