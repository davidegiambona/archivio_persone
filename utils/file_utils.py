# utils/file_utils.py

import subprocess
import sys
import os

def open_file(path: str):
    """Apre un file col programma di default (Windows/macOS/Linux)."""
    if not path:
        raise FileNotFoundError("Percorso file vuoto.")
    if not os.path.exists(path):
        raise FileNotFoundError(f"File non trovato: {path}")

    if sys.platform.startswith("darwin"):
        subprocess.call(("open", path))
    elif sys.platform.startswith("win"):
        subprocess.call(("start", path), shell=True)
    else:
        subprocess.call(("xdg-open", path))

def open_pdf(path: str):
    open_file(path)