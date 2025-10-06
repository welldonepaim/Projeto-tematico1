from dataclasses import dataclass
from typing import Optional
from datetime import date
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento

@dataclass
class Manutencao:
    id: Optional[int]                # ID no banco
    tipo: str                        # Preventiva / Corretiva / Preditiva
    equipamento: Equipamento         # Equipamento já cadastrado
    responsavel: Usuario             # Usuário já cadastrado
    data_prevista: date              # Data prevista para execução
    data_execucao: Optional[date]    # Data real da execução (pode ser nula até executar)
    documento: Optional[str]         # Caminho/arquivo do laudo
    acoes_realizadas: Optional[str]  # Ações executadas
    observacoes: Optional[str]       # Observações adicionais
    status: str                      # Concluída, Pendente, Em Análise, Revisada, etc.

    TIPOS = ("Preventiva", "Corretiva", "Preditiva")   # choices fixos
    STATUS = ("Pendente", "Em Análise", "Em Manutenção", "Concluída", "Revisada", "Disponível", "Descontinuado")
