# models.py

from dataclasses import dataclass
from utils.validators import is_valid_cui, is_valid_date_yyyy_mm_dd


@dataclass
class Persona:
    id: int | None
    nome: str
    cognome: str
    cui: str
    data_nascita: str
    nazionalita: str
    pdf_foto: str
    data_inserimento: str | None = None

    def is_valid(self) -> bool:
        if not (self.nome or "").strip():
            return False
        if not (self.cognome or "").strip():
            return False
        if not is_valid_cui(self.cui):
            return False
        if not is_valid_date_yyyy_mm_dd(self.data_nascita):
            return False
        if not (self.nazionalita or "").strip():
            return False
        return True