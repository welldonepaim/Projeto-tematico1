from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Equipamento:
    id: Optional[int]             # ID gerado pelo banco
    nome: str                     # Nome do equipamento
    tipo: str                     # Categoria (ex: Bomba, Compressor, Motor)
    numero_serie: str             # Número de série único
    setor: str                    # Setor/área onde está instalado
    status: str                   # Disponível / Em Manutenção / Indisponível
    
    fabricante: Optional[str] = None   # Marca/Fabricante (opcional)
    data_aquisicao: Optional[date] = None  # Data de compra/instalação (opcional)

    STATUS = ("Disponível", "Em Manutenção", "Indisponível")
