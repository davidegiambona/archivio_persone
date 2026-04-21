# utils/person_service.py

import os
import shutil
from datetime import datetime

from database import Database
from models import Persona
from utils.app_paths import pdf_dir


class PersonService:
    def __init__(self):
        self.db = Database()

    def add_persona(self, persona: Persona, pdf_original_path: str) -> int:
        if not persona.is_valid():
            raise ValueError("Dati persona non validi.")

        if not pdf_original_path or not os.path.exists(pdf_original_path):
            raise FileNotFoundError("File PDF non trovato.")
        if not pdf_original_path.lower().endswith(".pdf"):
            raise ValueError("Il file selezionato non è un PDF.")

        conn = self.db.connect()
        cur = conn.cursor()

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute("""
            INSERT INTO persone (nome, cognome, cui, data_nascita, nazionalita, pdf_foto, data_inserimento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            persona.nome.strip(),
            persona.cognome.strip(),
            persona.cui.strip().upper(),
            persona.data_nascita.strip(),
            persona.nazionalita.strip(),
            "",
            now
        ))
        persona_id = cur.lastrowid

        final_pdf_path = os.path.join(pdf_dir(), f"{persona_id}.pdf")
        shutil.copy(pdf_original_path, final_pdf_path)

        cur.execute("UPDATE persone SET pdf_foto = ? WHERE id = ?", (final_pdf_path, persona_id))

        conn.commit()
        conn.close()
        return persona_id

    def delete_persona(self, persona_id: int):
        conn = self.db.connect()
        cur = conn.cursor()

        cur.execute("SELECT pdf_foto FROM persone WHERE id = ?", (persona_id,))
        row = cur.fetchone()
        pdf_path = row[0] if row else None

        cur.execute("DELETE FROM persone WHERE id = ?", (persona_id,))
        conn.commit()
        conn.close()

        if pdf_path and os.path.exists(pdf_path):
            os.remove(pdf_path)

    def update_persona(self, persona_id: int, persona: Persona, new_pdf_path: str | None = None):
        if not persona.is_valid():
            raise ValueError("Dati persona non validi.")

        conn = self.db.connect()
        cur = conn.cursor()

        if new_pdf_path:
            if not os.path.exists(new_pdf_path):
                conn.close()
                raise FileNotFoundError("Nuovo PDF non trovato.")
            if not new_pdf_path.lower().endswith(".pdf"):
                conn.close()
                raise ValueError("Il file selezionato non è un PDF.")

            final_pdf_path = os.path.join(pdf_dir(), f"{persona_id}.pdf")
            shutil.copy(new_pdf_path, final_pdf_path)

            cur.execute("""
                UPDATE persone
                SET nome = ?, cognome = ?, cui = ?, data_nascita = ?, nazionalita = ?, pdf_foto = ?
                WHERE id = ?
            """, (
                persona.nome.strip(),
                persona.cognome.strip(),
                persona.cui.strip().upper(),
                persona.data_nascita.strip(),
                persona.nazionalita.strip(),
                final_pdf_path,
                persona_id
            ))
        else:
            cur.execute("""
                UPDATE persone
                SET nome = ?, cognome = ?, cui = ?, data_nascita = ?, nazionalita = ?
                WHERE id = ?
            """, (
                persona.nome.strip(),
                persona.cognome.strip(),
                persona.cui.strip().upper(),
                persona.data_nascita.strip(),
                persona.nazionalita.strip(),
                persona_id
            ))

        conn.commit()
        conn.close()