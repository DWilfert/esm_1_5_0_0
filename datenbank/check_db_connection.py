"""Kleines Hilfsskript, um DB-Verbindung schnell zu prüfen.

Verwendung:
  python check_db_connection.py --host HOST --user USER --database DB
oder setze MYSQL_* Umgebungsvariablen.
"""
import os
import argparse
import mysql.connector
from mysql.connector import Error


def get_params(args):
    host = args.host or os.environ.get("MYSQL_HOST")
    user = args.user or os.environ.get("MYSQL_USER")
    password = args.password or os.environ.get("MYSQL_PASSWORD")
    database = args.database or os.environ.get("MYSQL_DATABASE")
    port = int(args.port or os.environ.get("MYSQL_PORT", 3306))
    return host, user, password, database, port


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--user")
    parser.add_argument("--password")
    parser.add_argument("--database")
    parser.add_argument("--port", type=int)
    args = parser.parse_args()

    host, user, password, database, port = get_params(args)
    if not (host and user and database):
        print("Bitte --host, --user und --database angeben oder MYSQL_* Umgebungsvariablen setzen.")
        return

    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database, port=port, connection_timeout=10)
        if conn.is_connected():
            print(f"Erfolgreich verbunden mit {host}:{port} -> Datenbank: {database}")
            conn.close()
        else:
            print("Verbindung fehlgeschlagen (keine Verbindung).")
    except Error as e:
        print(f"Fehler beim Verbinden: {e}")


if __name__ == "__main__":
    main()
