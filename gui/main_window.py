# gui/main_window.py

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QAbstractItemView, QLineEdit, QLabel, QInputDialog
)
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt

from gui.insert_person import InsertPersonWindow
from utils.person_service import PersonService
from utils.file_utils import open_pdf
from utils.app_paths import resource_path
from utils.backup import list_backups, restore_backup


BG_CANDIDATES = [
    resource_path("assets/background.png"),
    resource_path("assets/polizia_bg.png"),
]


def pick_background():
    for p in BG_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def stylesheet(bg_path: str | None) -> str:
    navy = "#0B2A4A"
    navy2 = "#0A2340"
    navy3 = "#081B33"
    white = "#FFFFFF"

    bg_css = ""
    if bg_path:
        bg_path = bg_path.replace("\\", "/")
        bg_css = f"""
        QWidget#central {{
            border-image: url("{bg_path}") 0 0 0 0 stretch stretch;
        }}
        """

    return f"""
    {bg_css}

    QWidget {{
        font-size: 13px;
        color: {white};
    }}

    QLabel#title {{
        font-size: 20px;
        font-weight: 900;
        padding: 6px 0px 10px 0px;
        color: {white};
    }}

    /* Search */
    QLineEdit {{
        padding: 10px 12px;
        border: 1px solid rgba(255,255,255,0.22);
        border-radius: 12px;
        background: rgba(11, 42, 74, 0.70);
        color: {white};
        font-weight: 800;
    }}
    QLineEdit:focus {{
        border: 1px solid rgba(255,255,255,0.45);
        background: rgba(11, 42, 74, 0.82);
    }}

    /* Buttons */
    QPushButton {{
        padding: 10px 14px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.18);
        background: {navy};
        color: {white};
        font-weight: 900;
        min-width: 110px;
    }}
    QPushButton:hover {{ background: {navy2}; }}
    QPushButton:pressed {{ background: {navy3}; }}

    /* Table */
    QTableWidget {{
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 14px;
        background: rgba(255,255,255,0.78);
        color: #101010;
        gridline-color: rgba(0,0,0,0.08);
        selection-background-color: rgba(11,42,74,0.25);
        selection-color: #101010;
        alternate-background-color: rgba(0,0,0,0.03);
    }}

    /* Header */
    QHeaderView::section {{
        padding: 10px 10px;
        border: none;
        background: rgba(11, 42, 74, 0.92);
        color: {white};
        font-weight: 900;
    }}

    QTableCornerButton::section {{
        background: rgba(11, 42, 74, 0.92);
        border: none;
    }}

    QTableWidget::item {{
        padding: 8px;
        border-bottom: 1px solid rgba(0,0,0,0.06);
    }}

    QTableWidget::item:selected {{
        background: rgba(11,42,74,0.20);
        color: #101010;
    }}

    QTableWidget QTableView {{
        outline: 0;
    }}
    """


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Archivio Persone")
        self.setGeometry(200, 200, 980, 560)
        self.setMinimumSize(800, 600)

        self.service = PersonService()

        self.central = QWidget()
        self.central.setObjectName("central")
        self.setCentralWidget(self.central)
        self.central.setStyleSheet(stylesheet(pick_background()))

        root = QVBoxLayout()
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title = QLabel("Archivio Persone")
        title.setObjectName("title")
        root.addWidget(title)

        # top bar
        top = QHBoxLayout()
        top.setSpacing(10)

        self.search = QLineEdit()
        self.search.setPlaceholderText("Cerca per nome, cognome o CUI…")
        self.search.textChanged.connect(self.load_table)
        top.addWidget(self.search, stretch=1)

        btn_insert = QPushButton("Inserisci")
        btn_insert.clicked.connect(self.open_insert)
        top.addWidget(btn_insert)

        btn_refresh = QPushButton("Aggiorna")
        btn_refresh.clicked.connect(self.load_table)
        top.addWidget(btn_refresh)

        root.addLayout(top)

        # table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Nome", "Cognome", "CUI", "Data Nascita", "Nazionalità"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)

        # no edit in table cells
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # ✅ niente vertical header grigio
        self.table.verticalHeader().setVisible(False)

        root.addWidget(self.table, stretch=1)

        # action buttons
        actions = QHBoxLayout()
        actions.setSpacing(10)

        btn_open_pdf = QPushButton("Apri PDF")
        btn_open_pdf.clicked.connect(self.open_selected_pdf)
        actions.addWidget(btn_open_pdf)

        btn_edit = QPushButton("Modifica")
        btn_edit.clicked.connect(self.edit_selected)
        actions.addWidget(btn_edit)

        btn_delete = QPushButton("Elimina")
        btn_delete.clicked.connect(self.delete_selected)
        actions.addWidget(btn_delete)

        btn_restore = QPushButton("Ripristina backup")
        btn_restore.clicked.connect(self.restore_backup_ui)
        actions.addWidget(btn_restore)

        actions.addStretch(1)
        root.addLayout(actions)

        self.central.setLayout(root)
        self.load_table()

    # ESC deselect
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            self.table.clearSelection()
            self.table.setCurrentCell(-1, -1)
            return
        super().keyPressEvent(event)

    def _get_selected_person_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        try:
            return int(item.text())
        except ValueError:
            return None

    def open_insert(self):
        self.insert_window = InsertPersonWindow()
        self.insert_window.show()
        self.insert_window.destroyed.connect(self.load_table)

    def load_table(self):
        keyword = (self.search.text() or "").strip()
        rows = self.service.db.search_persona(keyword)

        self.table.setRowCount(0)
        for r, p in enumerate(rows):
            self.table.insertRow(r)
            for c, val in enumerate(p[:6]):
                self.table.setItem(r, c, QTableWidgetItem(str(val)))

    def open_selected_pdf(self):
        persona_id = self._get_selected_person_id()
        if persona_id is None:
            QMessageBox.warning(self, "Attenzione", "Seleziona una riga.")
            return

        row = self.service.db.get_persona_by_id(persona_id)
        if not row:
            QMessageBox.warning(self, "Attenzione", "Record non trovato.")
            return

        pdf_path = row[6]
        try:
            open_pdf(pdf_path)
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def delete_selected(self):
        persona_id = self._get_selected_person_id()
        if persona_id is None:
            QMessageBox.warning(self, "Attenzione", "Seleziona una riga.")
            return

        reply = QMessageBox.question(
            self,
            "Conferma eliminazione",
            f"Vuoi eliminare la persona con ID {persona_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self.service.delete_persona(persona_id)
            self.load_table()
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

    def edit_selected(self):
        persona_id = self._get_selected_person_id()
        if persona_id is None:
            QMessageBox.warning(self, "Attenzione", "Seleziona una riga.")
            return

        row = self.service.db.get_persona_by_id(persona_id)
        if not row:
            QMessageBox.warning(self, "Attenzione", "Record non trovato.")
            return

        self.edit_window = InsertPersonWindow(edit_id=persona_id, preload=row)
        self.edit_window.show()
        self.edit_window.destroyed.connect(self.load_table)

    def restore_backup_ui(self):
        backups = list_backups()
        if not backups:
            QMessageBox.information(self, "Backup", "Nessun backup disponibile.")
            return

        labels = [b.name for b in backups]
        choice, ok = QInputDialog.getItem(
            self,
            "Ripristina backup",
            "Seleziona un backup da ripristinare:",
            labels,
            0,
            False
        )
        if not ok or not choice:
            return

        selected = next((b for b in backups if b.name == choice), None)
        if selected is None:
            QMessageBox.warning(self, "Errore", "Backup selezionato non valido.")
            return

        reply = QMessageBox.question(
            self,
            "Conferma ripristino",
            "Ripristinare questo backup sovrascriverà il database corrente.\n"
            "Verrà creato un backup di sicurezza del DB attuale.\n\n"
            f"Backup: {selected.name}\n\n"
            "Vuoi continuare?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            restore_backup(selected)
            self.load_table()
            QMessageBox.information(self, "Backup", "Ripristino completato.")
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))