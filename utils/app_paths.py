# utils/app_paths.py

import os
import sys
from pathlib import Path


APP_NAME = "ArchivioPersone"


def resource_path(relative: str) -> str:
    """
    Percorso per risorse (assets) sia in sviluppo che in PyInstaller.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent
    return str(base / relative)


def user_data_dir() -> str:
    """
    Percorso persistente e scrivibile per DB e PDF.
    - Windows: %APPDATA%\\ArchivioPersone
    - macOS: ~/Library/Application Support/ArchivioPersone
    - Linux: ~/.local/share/ArchivioPersone
    """
    home = Path.home()

    if sys.platform.startswith("win"):
        base = Path(os.environ.get("APPDATA", str(home / "AppData" / "Roaming")))
    elif sys.platform.startswith("darwin"):
        base = home / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", str(home / ".local" / "share")))

    path = base / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


def db_path() -> str:
    return str(Path(user_data_dir()) / "database.db")


def pdf_dir() -> str:
    p = Path(user_data_dir()) / "pdf_segnaletiche"
    p.mkdir(parents=True, exist_ok=True)
    return str(p)