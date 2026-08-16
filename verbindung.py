import streamlit as st
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class MockCursor:
    def __init__(self, dictionary=False):
        self.dictionary = dictionary
    def execute(self, sql, params=None, multi=False): pass
    def fetchall(self): return []
    def fetchone(self): return None
    def close(self): pass
    def commit(self): pass

class MockVerbindung:
    def cursor(self, dictionary=False, **kwargs): return MockCursor(dictionary=dictionary)
    def is_connected(self): return True
    def close(self): pass
    def commit(self): pass
    def rollback(self): pass

def hole_datenbank_verbindung(max_retries: int = 3, backoff_seconds: int = 1, timeout: int = 10):
    return MockVerbindung()

def initialisiere_beispieldaten():
    pass

def hole_anlagen_daten():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "anlagebezeichnung": ["Demo-Aufzug 01", "Demo-Lüftung 02", "Demo-Kälteanlage 03"],
        "anlagenr": ["17501", "17502", "17503"],
        "standort_text": ["NP", "FG", "MUC"],
        "zustand": ["Betriebsbereit", "Wartung anstehend", "Betriebsbereit"]
    })

def hole_wartungsvertraege_daten():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "vertragsname": ["Demo-Wartung Aufzug", "Demo-Wartung Klima", "Demo-Wartung Kälte"],
        "kosten_bestand_pa": [2400.0, 1800.0, 3200.0],
        "benchmark_ais_pa": [2100.0, 1500.0, 2900.0],
        "naechste_wartung": [pd.Timestamp.now() + pd.Timedelta(days=10), pd.Timestamp.now() + pd.Timedelta(days=20), pd.Timestamp.now() + pd.Timedelta(days=5)],
        "zyklus_monate": [6, 12, 12]
    })

def hole_firmen_daten():
    return pd.DataFrame({
        "id": [1, 2],
        "firmenname": ["Demo-Partner GmbH", "Service AG"]
    })

def hole_wartungsuebersicht_daten():
    return pd.DataFrame({
        "id": [1, 2, 3],
        "anlagebezeichnung": ["Demo-Aufzug 01", "Demo-Lüftung 02", "Demo-Kälteanlage 03"],
        "vertragsname": ["Demo-Wartung Aufzug", "Demo-Wartung Klima", "Demo-Wartung Kälte"],
        "standort": ["NP", "FG", "MUC"],
        "naechste_wartung": [pd.Timestamp.now() + pd.Timedelta(days=10), pd.Timestamp.now() + pd.Timedelta(days=20), pd.Timestamp.now() + pd.Timedelta(days=5)],
        "intervall_monate": [6, 12, 12]
    })

def hole_untergewerk_daten():
    return pd.DataFrame({
        "unter_nr": ["4610", "4310", "4400"],
        "unter_txt": ["Aufzugsanlagen", "Lüftungsanlagen", "Kälteanlagen"]
    })
