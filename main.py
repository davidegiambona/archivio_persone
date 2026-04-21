# main.py

import sys
from PyQt6.QtWidgets import QApplication

from gui.main_window import MainWindow
from utils.backup import backup_db_daily

def main():
    # ✅ Backup automatico (max 5, 1 al giorno)
    backup_db_daily(max_backups=5)
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()