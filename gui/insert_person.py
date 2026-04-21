# gui/insert_person.py

import os
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QFormLayout, QFileDialog, QMessageBox,
    QHBoxLayout, QComboBox, QDateEdit, QCompleter, QSizePolicy
)
from PyQt6.QtCore import QDate, Qt, QStringListModel
from PyQt6.QtGui import QPixmap

from models import Persona
from utils.person_service import PersonService


ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")

TOP_RIGHT_ICON = os.path.join(ASSETS_DIR, "icopds.png")
ARROW_PNG = os.path.join(ASSETS_DIR, "arrow_down.png")
CAL_PNG = os.path.join(ASSETS_DIR, "calendar.png")

NATIONALITIES = [
    "Italiana", "Statunitense", "Spagnola", "Francese", "Tedesca", "Britannica",
    "Rumena", "Polacca", "Ucraina", "Marocchina", "Tunisina", "Egiziana",
    "Indiana", "Cinese", "Giapponese", "Brasiliana", "Argentina", "Apolide"
]


def _style(arrow_icon: str | None, cal_icon: str | None) -> str:
    navy = "#0B2A4A"
    navy2 = "#0A2340"
    navy3 = "#081B33"
    white = "#FFFFFF"

    arrow_css = f'image: url("{arrow_icon}");' if arrow_icon else ""
    cal_css = f'image: url("{cal_icon}");' if cal_icon else ""

    return f"""
    QWidget {{
        background: rgba(11, 42, 74, 0.86);
        color: {white};
        font-size: 13px;
    }}

    QLabel#title {{
        font-size: 18px;
        font-weight: 900;
        padding: 6px 0px 10px 0px;
        color: {white};
    }}

    QLineEdit, QComboBox, QDateEdit {{
        padding: 10px 12px;
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 12px;
        background: rgba(255,255,255,0.10);
        color: {white};
        font-weight: 800;
        min-height: 18px;
    }}
    QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{
        border: 1px solid rgba(255,255,255,0.45);
        background: rgba(255,255,255,0.14);
    }}

    QComboBox {{
        padding-right: 42px;
    }}
    QComboBox::drop-down {{
        border: none;
        width: 38px;
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
        background: rgba(255,255,255,0.14);
    }}
    QComboBox::drop-down:hover {{
        background: rgba(255,255,255,0.22);
    }}
    QComboBox::down-arrow {{
        {arrow_css}
        width: 14px;
        height: 14px;
    }}

    QDateEdit {{
        padding-right: 42px;
    }}
    QDateEdit::drop-down {{
        border: none;
        width: 38px;
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
        background: rgba(255,255,255,0.14);
    }}
    QDateEdit::drop-down:hover {{
        background: rgba(255,255,255,0.22);
    }}
    QDateEdit::down-arrow {{
        {cal_css}
        width: 16px;
        height: 16px;
    }}

    QComboBox QAbstractItemView, QListView {{
        background: rgba(255,255,255,0.98);
        color: #111111;
        border: 1px solid rgba(0,0,0,0.12);
        border-radius: 12px;
        padding: 6px;
        outline: 0;
        selection-background-color: rgba(11,42,74,0.14);
        selection-color: #111111;
    }}

    QPushButton {{
        padding: 10px 14px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.18);
        background: {navy};
        color: {white};
        font-weight: 900;
        min-width: 140px;
    }}
    QPushButton:hover {{ background: {navy2}; }}
    QPushButton:pressed {{ background: {navy3}; }}
    """


class InsertPersonWindow(QWidget):
    def __init__(self, edit_id=None, preload=None):
        super().__init__()
        self.service = PersonService()
        self.edit_id = edit_id
        self.preload = preload
        self.pdf_path = ""

        self.setFixedSize(500, 500)

        arrow_icon = ARROW_PNG if os.path.exists(ARROW_PNG) else None
        cal_icon = CAL_PNG if os.path.exists(CAL_PNG) else None
        self.setStyleSheet(_style(arrow_icon, cal_icon))

        self.setWindowTitle("Inserimento Persona" if edit_id is None else f"Modifica Persona (ID {edit_id})")

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(18, 16, 18, 16)
        root_layout.setSpacing(12)

        header = QHBoxLayout()
        header.setSpacing(10)

        title = QLabel("Inserisci nuova persona" if edit_id is None else "Modifica dati persona")
        title.setObjectName("title")

        self.logo = QLabel()
        self.logo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        if os.path.exists(TOP_RIGHT_ICON):
            pix = QPixmap(TOP_RIGHT_ICON)
            self.logo.setPixmap(
                pix.scaled(96, 96, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )

        header.addWidget(title, alignment=Qt.AlignmentFlag.AlignVCenter)
        header.addStretch(1)
        header.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignVCenter)
        root_layout.addLayout(header)

        divider = QWidget()
        divider.setFixedHeight(2)
        divider.setStyleSheet("background-color: #1E5AA8; border-radius: 1px;")
        root_layout.addWidget(divider)

        form = QFormLayout()
        form.setVerticalSpacing(12)
        form.setHorizontalSpacing(16)

        self.nome = QLineEdit()
        self.cognome = QLineEdit()
        self.cui = QLineEdit()

        self.nome.setPlaceholderText("Mario")
        self.cognome.setPlaceholderText("Rossi")
        self.cui.setPlaceholderText("CUI")

        self.data = QDateEdit()
        self.data.setCalendarPopup(True)
        self.data.setDisplayFormat("yyyy-MM-dd")
        self.data.setDate(QDate.currentDate())

        self.nazionalita = QComboBox()
        self.nazionalita.setEditable(True)
        self.nazionalita.addItems(NATIONALITIES)
        self.nazionalita.setCurrentText("Italiana" if "Italiana" in NATIONALITIES else (NATIONALITIES[0] if NATIONALITIES else ""))

        model = QStringListModel(NATIONALITIES, self)
        completer = QCompleter(model, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        le = self.nazionalita.lineEdit()
        le.setCompleter(completer)
        completer.setWidget(le)

        form.addRow("Nome", self.nome)
        form.addRow("Cognome", self.cognome)
        form.addRow("CUI", self.cui)
        form.addRow("Data di nascita", self.data)
        form.addRow("Nazionalità", self.nazionalita)

        root_layout.addLayout(form)

        self.pdf_label = QLabel("PDF: (nessuno selezionato)")
        self.pdf_label.setWordWrap(True)
        root_layout.addWidget(self.pdf_label)

        row_btn = QHBoxLayout()
        row_btn.setSpacing(10)

        btn_pdf = QPushButton("Seleziona PDF" if edit_id is None else "Seleziona nuovo PDF (opzionale)")
        btn_pdf.clicked.connect(self.select_pdf)
        row_btn.addWidget(btn_pdf)

        btn_save = QPushButton("Salva" if edit_id is None else "Salva modifiche")
        btn_save.clicked.connect(self.save)
        row_btn.addWidget(btn_save)

        root_layout.addLayout(row_btn)
        self.setLayout(root_layout)

        if self.preload:
            # preload = (id, nome, cognome, cui, data_nascita, nazionalita, pdf_foto, data_inserimento)
            self.nome.setText(str(self.preload[1] or ""))
            self.cognome.setText(str(self.preload[2] or ""))
            self.cui.setText(str(self.preload[3] or ""))

            existing_date = str(self.preload[4] or "")
            qd = QDate.fromString(existing_date, "yyyy-MM-dd")
            if qd.isValid():
                self.data.setDate(qd)

            existing_nat = str(self.preload[5] or "")
            if existing_nat:
                self.nazionalita.setCurrentText(existing_nat)

            existing_pdf = str(self.preload[6] or "")
            if existing_pdf:
                self.pdf_label.setText(f"PDF attuale: {existing_pdf}")
            else:
                self.pdf_label.setText("PDF attuale: (non presente)")

    def select_pdf(self):
        file, _ = QFileDialog.getOpenFileName(self, "Seleziona PDF", "", "PDF (*.pdf)")
        if file:
            self.pdf_path = file
            self.pdf_label.setText(f"PDF selezionato: {file}")

    def save(self):
        try:
            data_str = self.data.date().toString("yyyy-MM-dd")
            naz_str = (self.nazionalita.currentText() or "").strip()

            persona = Persona(
                id=None,
                nome=self.nome.text(),
                cognome=self.cognome.text(),
                cui=self.cui.text(),
                data_nascita=data_str,
                nazionalita=naz_str,
                pdf_foto=""
            )

            if self.edit_id is None:
                if not self.pdf_path:
                    raise ValueError("Seleziona un PDF prima di salvare.")
                new_id = self.service.add_persona(persona, self.pdf_path)
                QMessageBox.information(self, "OK", f"Persona inserita correttamente (ID {new_id})")
                self.close()
            else:
                new_pdf = self.pdf_path if self.pdf_path else None
                self.service.update_persona(self.edit_id, persona, new_pdf_path=new_pdf)
                QMessageBox.information(self, "OK", "Modifiche salvate correttamente")
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))