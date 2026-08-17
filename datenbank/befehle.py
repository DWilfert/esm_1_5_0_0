import pandas as pd

from verbindung import hole_datenbank_verbindung


def hole_anlagen_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM anlagen", con=conn)
        finally:
            conn.close()
    return pd.DataFrame()


def hole_wartungsvertraege_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM vertragsanalyse", con=conn)
        finally:
            conn.close()
    return pd.DataFrame()


def hole_firmen_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM firmeninfo", con=conn)
        finally:
            conn.close()
    return pd.DataFrame()