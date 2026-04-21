# database.py

import sqlite3
from utils.app_paths import db_path


class Database:
    def __init__(self, path: str | None = None):
        self.db_path = path or db_path()
        self._ensure_db()

    def connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db(self):
        conn = self.connect()
        cur = conn.cursor()

        # 1) se la tabella esiste, controlla colonne
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='persone'")
        exists = cur.fetchone() is not None

        if exists:
            cur.execute("PRAGMA table_info(persone)")
            cols = [row[1] for row in cur.fetchall()]
            # Se manca cui -> schema vecchio: ricrea (visto che DB vuoto/accettato)
            if "cui" not in cols:
                cur.execute("DROP TABLE persone")
                conn.commit()

        # 2) crea tabella corretta (se non esiste o appena droppata)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS persone (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cognome TEXT NOT NULL,
            cui TEXT NOT NULL UNIQUE,
            data_nascita TEXT NOT NULL,
            nazionalita TEXT NOT NULL,
            pdf_foto TEXT NOT NULL,
            data_inserimento TEXT NOT NULL
        )
        """)

        conn.commit()
        conn.close()

    def search_persona(self, keyword: str):
        conn = self.connect()
        cur = conn.cursor()

        kw = f"%{keyword}%"
        cur.execute("""
            SELECT * FROM persone
            WHERE nome LIKE ?
               OR cognome LIKE ?
               OR cui LIKE ?
            ORDER BY id ASC
        """, (kw, kw, kw))

        rows = cur.fetchall()
        conn.close()
        return rows

    def get_persona_by_id(self, persona_id: int):
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT * FROM persone WHERE id = ?", (persona_id,))
        row = cur.fetchone()
        conn.close()
        return row