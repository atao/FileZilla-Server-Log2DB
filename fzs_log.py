# coding: utf-8

import hashlib
import re
import sqlite3
from pathlib import Path


DB_PATH = Path(r"C:\temp\fzs_log.db")
LOG_PATH = Path(r"C:\Program Files (x86)\FileZilla Server\Logs")

LOG_REGEX = re.compile(
    r"\((\d+)\)\s+"
    r"(\d{2}/\d{2}/\d{4})\s+"
    r"(\d{2}:\d{2}:\d{2})\s+-\s+"
    r"(.*?)\s+"
    r"\(((?:\d{1,3}\.){3}\d{1,3})\)>\s+"
    r"(.*)"
)


def calculate_checksum(line: str) -> str:
    """
    Calcule une empreinte stable sur 10 chiffres.
    """
    digest = hashlib.sha1(line.encode("utf-8")).hexdigest()
    return str(int(digest, 16) % (10 ** 10))


def create_database(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS fzs_log (
            id TEXT,
            date TEXT,
            hour TEXT,
            user TEXT,
            ip TEXT,
            message TEXT,
            logFile TEXT,
            checksum TEXT PRIMARY KEY
        )
        """
    )
    connection.commit()


def process_log_file(
    connection: sqlite3.Connection,
    log_file: Path
) -> int:
    """
    Traite un fichier de log et retourne le nombre de lignes insérées.
    """
    inserted = 0

    print(f"Traitement de {log_file.name}...")

    with log_file.open("r", encoding="utf-8", errors="replace") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.rstrip("\n")

            match = LOG_REGEX.search(line)

            if not match:
                print(
                    f"Ligne {line_number} ignorée "
                    f"dans {log_file.name} : {line}"
                )
                continue

            log_id, date, hour, user, ip, message = match.groups()
            checksum = calculate_checksum(line)

            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO fzs_log
                (
                    id,
                    date,
                    hour,
                    user,
                    ip,
                    message,
                    logFile,
                    checksum
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    date,
                    hour,
                    user,
                    ip,
                    message,
                    log_file.name,
                    checksum,
                ),
            )

            if cursor.rowcount == 1:
                inserted += 1

    return inserted


def main() -> None:
    if not LOG_PATH.is_dir():
        print(f"Dossier de logs non trouvé : {LOG_PATH}")
        return

    # Tri par date de modification, puis conservation des deux plus récents.
    log_files = sorted(
        (
            file
            for file in LOG_PATH.iterdir()
            if file.is_file()
        ),
        key=lambda file: file.stat().st_mtime,
        reverse=True,
    )[:2]

    if not log_files:
        print("Aucun fichier de log trouvé.")
        return

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        create_database(connection)

        total_inserted = 0

        for log_file in reversed(log_files):
            total_inserted += process_log_file(connection, log_file)

        connection.commit()

    print(f"{total_inserted} nouvelle(s) ligne(s) insérée(s).")


if __name__ == "__main__":
    main()
