from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Cliente:
    cpf: str
    nome: str
    datanascimento: str
    endereco: str
    telefone: str

    def to_row(self) -> List[str]:
        return [self.cpf, self.nome, self.datanascimento, self.endereco, self.telefone]

    @staticmethod
    def from_row(row: List[str]) -> "Cliente":
        return Cliente(row[0], row[1], row[2], row[3], row[4])
