from dataclasses import dataclass
from typing import Optional
from datetime import date, timedelta
from src.model.usuario import Usuario
from src.model.equipamento import Equipamento


@dataclass
class Planejamento:
    id: Optional[int] = None
    tipo: str = "Preventiva"  
    descricao: Optional[str] = None
    frequencia: Optional[str] = None  # Ex: Diario, Semanal, Mensal...
    dias_previstos: Optional[int] = None  # intervalo em dias entre execuções
    data_inicial: Optional[date] = None  # data do primeiro agendamento
    criticidade: Optional[str] = None
    responsavel: Optional[Usuario] = None
    equipamento: Optional[Equipamento] = None
    estagio: Optional[str] = None
    last_gerada: Optional[date] = None  # última manutenção gerada a partir do planejamento


    FREQUENCIAS = ("Diario", "Semanal", "Mensal", "Trimestral", "Semestral", "Anual")

    def _frequencia_para_dias(self) -> Optional[int]:
        """Converte a string de frequência para número de dias, se aplicável."""
        mapping = {
            "Diario": 1,
            "Semanal": 7,
            "Mensal": 30,
            "Trimestral": 90,
            "Semestral": 180,
            "Anual": 365,
        }
        if self.dias_previstos:
            return int(self.dias_previstos)
        if self.frequencia:
            return mapping.get(self.frequencia)
        return None

    def proxima_data(self) -> Optional[date]:
        """Retorna a próxima data prevista para geração da manutenção."""
   
        if not self.data_inicial:
            return None

        if not self.last_gerada:
            return self.data_inicial

        dias = self._frequencia_para_dias()
        if dias is None:
            return None
        return self.last_gerada + timedelta(days=dias)

    def deve_gerar(self, referencia: Optional[date] = None) -> bool:
        """Se a data é igual a hoje, deve gerar a manutenção.
        Se for ontem  também deve gerar.
        caracterizada "atrasada" se for o caso.
        """
        if referencia is None:
            referencia = date.today()

        proxima = self.proxima_data()
        if not proxima:
            return False

        ontem = referencia - timedelta(days=1)
        return proxima == referencia or proxima == ontem

    def avançar_last_gerada(self) -> Optional[date]:
        """Atualiza `last_gerada` para a próxima data prevista (se houver) e retorna-a."""
        proxima = self.proxima_data()
        if proxima:
            self.last_gerada = proxima
            return proxima
        return None
