# utils/validators.py

import re
from datetime import datetime

_CUI_RE = re.compile(r"^[A-Z0-9]{1,32}$", re.IGNORECASE)  # flessibile


def is_valid_date_yyyy_mm_dd(s: str) -> bool:
    s = (s or "").strip()
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def normalize_cui(cui: str) -> str:
    return (cui or "").strip().upper()


def is_valid_cui(cui: str) -> bool:
    """
    Validazione 'soft' del CUI:
    - alfanumerico
    - 1..32 caratteri
    Se vuoi regole più strette, dimmi lo standard del tuo CUI e lo adattiamo.
    """
    cui = normalize_cui(cui)
    return bool(_CUI_RE.match(cui))