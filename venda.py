from dataclasses import dataclass
from datetime import datetime
from typing import List    
@dataclass
class Venda:
    data_iso: datetime
    produto: str
    quantidade: int
    valor_total: float
    def to_row(self) -> List[str]:
        return [self.data_iso.isoformat(), self.produto, str(self.quantidade), f"{self.valor_total:.2f}"]
   
    @staticmethod
    def from_row(row: List[str])  -> "Venda":
        return Venda(
            datetime.fromisoformat(row[0]),
            row[1],
            int(row[2]),
            float(row[3])
        )