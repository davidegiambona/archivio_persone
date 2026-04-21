# utils/backup.py

import shutil
from datetime import datetime
from pathlib import Path

from utils.app_paths import user_data_dir, db_path


def _backups_dir() -> Path:
    d = Path(user_data_dir()) / "backups"
    d.mkdir(parents=True, exist_ok=True)
    return d


def backup_db_daily(max_backups: int = 5) -> None:
    """
    Crea un backup del DB al massimo 1 volta al giorno.
    Mantiene solo gli ultimi `max_backups` backup (elimina i più vecchi).
    """
    backups_dir = _backups_dir()
    src_db = Path(db_path())

    # Se il DB non esiste ancora, non facciamo niente
    if not src_db.exists():
        return

    today = datetime.now().strftime("%Y-%m-%d")
    dst = backups_dir / f"database_{today}.db"

    # già fatto oggi
    if dst.exists():
        return

    shutil.copy2(src_db, dst)

    # Rotazione: tieni solo gli ultimi N backup "giornalieri"
    backups = sorted(
        backups_dir.glob("database_????-??-??.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    for old in backups[max_backups:]:
        try:
            old.unlink()
        except Exception:
            pass


def list_backups() -> list[Path]:
    """Ritorna i backup disponibili (giornalieri) ordinati dal più recente al più vecchio."""
    backups_dir = _backups_dir()
    backups = sorted(
        backups_dir.glob("database_????-??-??.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    return backups


def restore_backup(backup_file: Path) -> None:
    """
    Ripristina un backup sovrascrivendo il DB attuale.
    Prima salva una copia di sicurezza del DB corrente.
    """
    src = Path(backup_file)
    if not src.exists():
        raise FileNotFoundError(f"Backup non trovato: {src}")

    current_db = Path(db_path())
    backups_dir = _backups_dir()

    # Safety copy del DB corrente (così puoi tornare indietro anche dal restore)
    if current_db.exists():
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        safety = backups_dir / f"database_pre_restore_{stamp}.db"
        shutil.copy2(current_db, safety)

    shutil.copy2(src, current_db)