"""Import-Skript für die SQL-Dumps in ../dump_1_5_0_0

Verhalten:
- Liest alle `*.sql` Dateien im Projektordner `dump_1_5_0_0` (alphabetisch)
- Entfernt problematische `DEFINER` / `SQL SECURITY DEFINER` Clauses
- Versucht, die bereinigten Dateien mit dem System-`mysql`-Client zu importieren (falls vorhanden)
- Fallback: versucht Import per `mysql.connector` (geeignet für normale DDL/INSERTs, kann Probleme mit DELIMITER haben)

Verbindungsdaten: aus Umgebungsvariablen (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE, MYSQL_PORT)
oder als Kommandozeilen-Argumente.
"""
from __future__ import annotations
import os
import re
import glob
import shutil
import subprocess
import tempfile
import argparse
from typing import Tuple

import mysql.connector
from mysql.connector import Error


def get_params_from_env_or_args(args: argparse.Namespace) -> Tuple[str, str, str, str, int]:
    host = args.host or os.environ.get("MYSQL_HOST") or os.environ.get("DB_HOST")
    user = args.user or os.environ.get("MYSQL_USER") or os.environ.get("DB_USER")
    password = args.password or os.environ.get("MYSQL_PASSWORD") or os.environ.get("DB_PASSWORD")
    database = args.database or os.environ.get("MYSQL_DATABASE") or os.environ.get("DB_NAME")
    port = int(args.port or os.environ.get("MYSQL_PORT", 3306))
    return host, user, password, database, port


def clean_sql(content: str) -> str:
    # Entferne DEFINER=`user`@`host`
    content = re.sub(r"DEFINER=`[^`]+`@`[^`]+`", "", content, flags=re.IGNORECASE)
    # Entferne SQL SECURITY DEFINER
    content = re.sub(r"SQL\s+SECURITY\s+DEFINER", "", content, flags=re.IGNORECASE)
    return content


def import_with_mysql_client(path: str, host: str, user: str, password: str, database: str, port: int) -> Tuple[bool, str]:
    mysql_exe = shutil.which("mysql")
    if not mysql_exe:
        return False, "mysql client not found"

    cmd = [mysql_exe, f"--host={host}", f"--user={user}", f"--port={port}", database]
    env = os.environ.copy()
    if password:
        # MYSQL_PWD avoids password prompt (note: exposes in env for the subprocess only)
        env["MYSQL_PWD"] = password

    try:
        with open(path, "rb") as fh:
            subprocess.check_call(cmd, stdin=fh, env=env)
        return True, "imported via mysql client"
    except subprocess.CalledProcessError as e:
        return False, str(e)


def import_with_connector(path: str, host: str, user: str, password: str, database: str, port: int) -> Tuple[bool, str]:
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            sql = fh.read()
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database, port=port, connection_timeout=10)
        cursor = conn.cursor()
        # Versuche multi=True (neuere mysql-connector-python unterstützt das)
        try:
            for res in cursor.execute(sql, multi=True):
                pass
            conn.commit()
            cursor.close()
            conn.close()
            return True, "imported via connector (multi)"
        except TypeError as te:
            # Manche Cursor-Implementierungen unterstützen 'multi' nicht. Fallback: einfache Splits
            msg_te = str(te)
            if "multi" in msg_te or "unexpected" in msg_te:
                # Einfacher Fallback: split by ';' — Hinweis: kann bei PROCEDUREs/DELIMITER scheitern
                statements = [s.strip() for s in sql.split(";") if s.strip()]
                try:
                    for stmt in statements:
                        try:
                            cursor.execute(stmt)
                        except Exception:
                            # Ignoriere einzelne Fehler, damit restliche Statements laufen
                            pass
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return True, "imported via connector (split statements fallback)"
                except Exception as e2:
                    return False, f"fallback-split-failed: {e2}"
            else:
                return False, msg_te
        except Exception as e:
            # Andere Fehler
            try:
                conn.rollback()
            except Exception:
                pass
            cursor.close()
            conn.close()
            return False, str(e)
    except Error as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--database")
    parser.add_argument("--port", type=int)
    parser.add_argument("--dump-dir", default=None, help="Pfad zu dump_1_5_0_0 (Standard: Projekt-Root/dump_1_5_0_0)")
    args = parser.parse_args()

    host, user, password, database, port = get_params_from_env_or_args(args)
    if not (host and user and database):
        print("Fehlende Verbindungsparameter. Setze MYSQL_HOST, MYSQL_USER und MYSQL_DATABASE oder übergib --host/--user/--database.")
        return

    # Ermittle dump-Ordner relativ zum Projekt
    here = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    project_root = os.path.abspath(os.path.join(here, ".."))
    dump_dir = args.dump_dir or os.path.join(project_root, "dump_1_5_0_0")
    if not os.path.isdir(dump_dir):
        print(f"Dump-Ordner nicht gefunden: {dump_dir}")
        return

    sql_files = sorted(glob.glob(os.path.join(dump_dir, "*.sql")))
    if not sql_files:
        print(f"Keine .sql Dateien in {dump_dir} gefunden.")
        return

    print(f"Gefundene Dumps: {len(sql_files)}. Import starte (host={host}, db={database}).")

    for f in sql_files:
        print(f"\n==> Verarbeite: {os.path.basename(f)}")
        with open(f, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()

        cleaned = clean_sql(content)
        # Schreibe temporäre bereinigte Datei
        with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".sql") as tmp:
            tmp.write(cleaned)
            tmp_path = tmp.name

        # Versuche system mysql client
        ok, msg = import_with_mysql_client(tmp_path, host, user, password, database, port)
        if ok:
            print(f"  Erfolgreich (mysql client): {msg}")
            os.unlink(tmp_path)
            continue

        # Fallback: mysql.connector (kann bei Routinen/DELIMITER scheitern)
        ok2, msg2 = import_with_connector(tmp_path, host, user, password, database, port)
        if ok2:
            print(f"  Erfolgreich (connector): {msg2}")
        else:
            print(f"  Import fehlgeschlagen. mysql-client-Fehler: {msg}; connector-Fehler: {msg2}")

        try:
            os.unlink(tmp_path)
        except Exception:
            pass

    print("\nImport-Vorgang beendet.")


if __name__ == "__main__":
    main()
