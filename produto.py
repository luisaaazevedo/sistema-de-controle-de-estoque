from dataclasses import dataclass
from typing import List

@dataclass
class Produto:
    nome: str
    preco: float
    quantidade: int
    def to_row(self) -> List[str]:
        return [self.nome, f"{self.preco:.2f}", str(self.quantidade)]
   
    @staticmethod
    def from_row(row: List[str])  -> "Produto":
        return Produto(row[0], float(row[1]), int(row[2]))
    
