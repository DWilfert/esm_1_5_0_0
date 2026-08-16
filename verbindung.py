import streamlit as st
import pandas as pd
import re
from datetime import datetime, timedelta, date

MOCK_STANDORTE = [
    {"id": 1, "ort_kurz": "NP", "ort": "Neuperlach"},
    {"id": 2, "ort_kurz": "FG", "ort": "Fasangarten"}
]

MOCK_KOSTENGRUPPEN = [
    {"kg_nr": "460", "kg_txt": "Förderanlagen"},
    {"kg_nr": "430", "kg_txt": "Raumlufttechnische Anlagen"},
    {"kg_nr": "420", "kg_txt": "Wärmeversorgungsanlagen"},
    {"kg_nr": "440", "kg_txt": "Kälteversorgungsanlagen"}
]

MOCK_UNTERGEWERKE = [
    {"unter_nr": "4610", "unter_txt": "Aufzugsanlagen Personen / Lasten"},
    {"unter_nr": "4310", "unter_txt": "Lüftungszentralen & Brandschutzklappen"},
    {"unter_nr": "4210", "unter_txt": "Heizkessel & BHKW"},
    {"unter_nr": "4410", "unter_txt": "Kältemaschinen & Rückkühlwerke"}
]

MOCK_FIRMEN = [
    {"id": 1, "firmenname": "Otis GmbH & Co. OHG", "firmebranche": "Aufzugstechnik", "firmenadresse": "Carl-Wery-Straße 22, 81739 München", "firmentelefon": "+49 89 678901", "firmenfax": "+49 89 678902", "firmenEMail": "service@otis.com", "firmenwebsite": "www.otis.com", "firmenansprechpartner": "Markus Weber"},
    {"id": 2, "firmenname": "Carrier Klimatechnik GmbH", "firmebranche": "Klimatechnik", "firmenadresse": "Gutenbergstraße 5, 85748 Garching", "firmentelefon": "+49 89 456789", "firmenfax": "+49 89 456780", "firmenEMail": "kontakt@carrier.de", "firmenwebsite": "www.carrier.de", "firmenansprechpartner": "Stefan Klein"},
    {"id": 3, "firmenname": "Viessmann Werke München", "firmebranche": "Wärmeerzeugung", "firmenadresse": "Industriestraße 12, 85609 Aschheim", "firmentelefon": "+49 89 123000", "firmenfax": "+49 89 123009", "firmenEMail": "service@viessmann.de", "firmenwebsite": "www.viessmann.de", "firmenansprechpartner": "Thomas Bauer"},
    {"id": 4, "firmenname": "Schindler Aufzüge GmbH", "firmebranche": "Fördertechnik", "firmenadresse": "Theresienhöhe 12, 80339 München", "firmentelefon": "+49 89 555123", "firmenfax": "+49 89 555124", "firmenEMail": "info@schindler.de", "firmenwebsite": "www.schindler.de", "firmenansprechpartner": "Anna Schmidt"},
    {"id": 5, "firmenname": "Johnson Controls Germany", "firmebranche": "Gebäudeautomation", "firmenadresse": "Robert-Bosch-Straße 3, 85746 Garching", "firmentelefon": "+49 89 321654", "firmenfax": "+49 89 321655", "firmenEMail": "service@jci.com", "firmenwebsite": "www.jci.com", "firmenansprechpartner": "Michael Horn"}
]

MOCK_ANLAGEN = []
_anl_namen = [
    "Personenaufzug Hauptgebäude", "Lüftungszentrale RLT-01", "Brennwertkessel K1", "Kältemaschine Chill-02",
    "Glastür-Automatik Nord", "Tiefgaragen-Lüftung TG1", "Blockheizkraftwerk BHKW", "Brandmeldezentrale BMZ-Main",
    "Trinkwasser-Druckerhöhung", "Klima Serverraum S1", "Lastenaufzug Logistik", "RLT-Anlage Konferenzbereich",
    "Heizkreisverteiler Haus B", "Rückkühlwerk Dach", "Fassaden-Befahranlage", "Schmutzwasser-Hebeanlage",
    "Sicherheitsstrom-Diesel", "Klimasplitgerät Archiv", "Rauchschürzensteuerung", "Wärmetauscher Fernwärme"
]
for i in range(1, 21):
    MOCK_ANLAGEN.append({
        "id": i,
        "anlagenr": f"175{i:02d}",
        "anlagebezeichnung": _anl_namen[i-1],
        "anlagetyp": "Technische Gebäudeausrüstung",
        "anlagebauteil": (i % 3) + 1,
        "hersteller": MOCK_FIRMEN[(i - 1) % len(MOCK_FIRMEN)]["firmenname"],
        "typ": f"Model-X{i}",
        "seriennummer": f"SN-MOCK-{8000+i}",
        "baujahr": 2015 + (i % 8),
        "ugewerk_nr": "4610" if i % 4 == 0 else ("4310" if i % 4 == 1 else ("4210" if i % 4 == 2 else "4410")),
        "ugewerk_bez": "Anlagengruppe TGA",
        "anzahl": 1,
        "standort_id": (i % 2) + 1,
        "gebaudeteil": f"Bauteil {(i % 3) + 1}",
        "etage": f"{(i % 5) - 1}.OG" if i % 5 != 0 else "UG",
        "raum": f"R-{(100 + i)}",
        "raumbezeichnung": f"Technikraum {(100 + i)}",
        "aks_Bez.": f"AKS-99{i:02d}",
        "kostengruppe_nr": "460" if i % 4 == 0 else "430",
        "kostengruppen_bez": "DIN 276 Gruppe TGA",
        "lebensdauer": "20 Jahre",
        "lebensende": f"{2035 + (i % 8)}",
        "zustand": "Betriebsbereit" if i not in [3, 7, 12] else "Wartung anstehend",
        "beschreibung": f"Detaillierte technische Beschreibung für {_anl_namen[i-1]} im Enterprise-Betrieb."
    })

_heute = date.today()

MOCK_VERTRAGSANALYSE = []
for i in range(1, 21):
    _kosten = 1500.00 + (i * 350.0)
    _bench = _kosten * 0.85
    MOCK_VERTRAGSANALYSE.append({
        "id": i,
        "anlage_id": i,
        "kostengruppe_nr": "430",
        "kostengruppen_bez": "TGA Anlagen",
        "ugewerk_nr": "4310",
        "ugewerk_bez": "Gewerbe TGA",
        "anlagebezeichnung": _anl_namen[i-1],
        "standort_text": "NP" if i % 2 == 0 else "FG",
        "anzahl": 1,
        "firma_id": ((i - 1) % len(MOCK_FIRMEN)) + 1,
        "vertragsname": f"Wartungsvertrag {_anl_namen[i-1]}",
        "vertragsart": "Vollwartung" if i % 3 == 0 else "Inspektion",
        "vertragsende": _heute + timedelta(days=300 + (i * 15)),
        "kuendigungsfrist": "3 Monate zum Jahresende",
        "vertragsoptionen": "24/7 Service-Hotline inklusive",
        "kosten_bestand_pa": _kosten,
        "benchmark_ais_pa": _bench,
        "wartungsgrundlage": "Herstellervorgabe / Gesetzliche Prüfpflicht",
        "zyklus_jahre": 1,
        "zyklus_monate": 6 if i % 2 == 0 else 12,
        "zyklus_herstellerempfehlung": "Halbjährlich / Jährlich",
        "hinweise": "Digitaler Berichtsversand an Facility Management.",
        "protokoll_vorhanden": "ja",
        "letzte_wartung": _heute - timedelta(days=50 + (i * 5)),
        "naechste_wartung": _heute - timedelta(days=10) if i == 1 else (_heute + timedelta(days=i * 12)),
        "naechste_pruefung": _heute + timedelta(days=i * 15),
        "anmerkung": f"Rahmenvertrag Nr. 2026-{i:03d}",
        "maengelverfolgung": "Keine Mängel" if i % 4 != 0 else "Kleinere Abweichungen in Klärung",
        "clustering": "A" if i % 2 == 0 else "B"
    })

MOCK_SERVICE = []
for i in range(1, 21):
    MOCK_SERVICE.append({
        "id": i,
        "anlage_id": i,
        "standort_text": "NP" if i % 2 == 0 else "FG",
        "anlagenklasse": f"4{i}10",
        "bezeichnung_anlagenklasse": "Technische Prüfung",
        "anlagebezeichnung": _anl_namen[i-1],
        "kennz_1": f"Anlage {i}",
        "kennz_2": f"Sektor {(i % 3) + 1}",
        "kurzfassung": f"Reguläre Inspektion und Funktionsprüfung für {_anl_namen[i-1]} erfolgreich beendet.",
        "intervall": "6M",
        "Hinweis": "Keinerlei sicherheitsrelevante Beanstandungen.",
        "gesetzl_grundlage": "BetrSichV / DIN VDE",
        "textstelle_gesetz": "Paragraph 14",
        "qualifikation": "Sachkundiger Prüfer",
        "entlastung_schadensfall": "Vollständig gegeben durch Prüfprotokoll",
        "erstabnahme": "Nein",
        "wiederkehrende_pruefung": "Ja",
        "anzahl": 1,
        "baujahr": 2018,
        "merkmal": "Betriebsdruck",
        "merkmalwert": "Standard"
    })

MOCK_AUFFAELLIGKEITEN = []
for i in range(1, 21):
    MOCK_AUFFAELLIGKEITEN.append({
        "id": i,
        "anlage_id": i,
        "vertrag": f"Wartungsvertrag {_anl_namen[i-1]}",
        "protokolldatei": f"Bericht_Anlage_{i}.pdf",
        "standort_text": "NP" if i % 2 == 0 else "FG",
        "kommentar": f"Hinweis zu {_anl_namen[i-1]}: Verschleißerscheinung im Toleranzbereich dokumentiert (Eintrag {i})."
    })

MOCK_EINSTELLUNGEN = [
    {"id": 1, "schluessel": "dokumenten_pfad", "wert": "C:/esm_dokumente"}
]

def _init_mock_store():
    if "mock_db_initialized" not in st.session_state:
        st.session_state.mock_standort = [dict(x) for x in MOCK_STANDORTE]
        st.session_state.mock_kostengruppen = [dict(x) for x in MOCK_KOSTENGRUPPEN]
        st.session_state.mock_untergewerk = [dict(x) for x in MOCK_UNTERGEWERKE]
        st.session_state.mock_firmeninfo = [dict(x) for x in MOCK_FIRMEN]
        st.session_state.mock_anlagen = [dict(x) for x in MOCK_ANLAGEN]
        st.session_state.mock_vertragsanalyse = [dict(x) for x in MOCK_VERTRAGSANALYSE]
        st.session_state.mock_service = [dict(x) for x in MOCK_SERVICE]
        st.session_state.mock_auffaelligkeiten = [dict(x) for x in MOCK_AUFFAELLIGKEITEN]
        st.session_state.mock_einstellungen = [dict(x) for x in MOCK_EINSTELLUNGEN]
        st.session_state.mock_db_initialized = True

_init_mock_store()

class MockCursor:
    def __init__(self, dictionary=False):
        self.dictionary = dictionary
        self.results = []
        self._row_index = 0
        self.rowcount = 0

    def execute(self, sql, params=None):
        _init_mock_store()
        sql_clean = " ".join(sql.split()).strip()
        sql_lower = sql_clean.lower()
        self.results = []
        self._row_index = 0

        if sql_lower.startswith("select"):
            self._handle_select(sql_clean, params)
        elif sql_lower.startswith("insert"):
            self.rowcount = 1
        elif sql_lower.startswith("update"):
            self.rowcount = 1
        elif sql_lower.startswith("delete"):
            self.rowcount = 1
        else:
            self.rowcount = 0

    def _handle_select(self, sql, params):
        sql_lower = sql.lower()
        if "count(*)" in sql_lower:
            self.results = [{"count": 20}] if self.dictionary else [(20,)]
            return
        if "from vertragsanalyse" in sql_lower:
            self.results = [dict(x) for x in st.session_state.mock_vertragsanalyse]
            if not self.dictionary:
                self.results = [list(x.values()) for x in self.results]
            return
        if "from anlagen" in sql_lower:
            self.results = [dict(x) for x in st.session_state.mock_anlagen]
            if not self.dictionary:
                self.results = [list(x.values()) for x in self.results]
            return
        self.results = []

    def fetchall(self):
        return self.results

    def fetchone(self):
        if self._row_index < len(self.results):
            r = self.results[self._row_index]
            self._row_index += 1
            return r
        return None

    def close(self):
        pass

class MockConnection:
    def cursor(self, dictionary=False, **kwargs):
        return MockCursor(dictionary=dictionary)
    def commit(self): pass
    def rollback(self): pass
    def close(self): pass
    def is_connected(self): return True

def hole_datenbank_verbindung(*args, **kwargs):
    _init_mock_store()
    return MockConnection()

def initialisiere_beispieldaten():
    _init_mock_store()

def hole_anlagen_daten():
    _init_mock_store()
    return pd.DataFrame(st.session_state.mock_anlagen)

def hole_wartungsvertraege_daten():
    _init_mock_store()
    return pd.DataFrame(st.session_state.mock_vertragsanalyse)

def hole_firmen_daten():
    _init_mock_store()
    return pd.DataFrame(st.session_state.mock_firmeninfo)

def hole_wartungsuebersicht_daten():
    _init_mock_store()
    # Hier filtern wir die Daten sauber, damit nur die kompakte Übersicht für die Startseite entsteht!
    df = pd.DataFrame(st.session_state.mock_vertragsanalyse)
    if not df.empty:
        return df[["id", "anlagebezeichnung", "vertragsname", "standort_text", "naechste_wartung", "zyklus_monate"]].rename(
            columns={"standort_text": "standort", "zyklus_monate": "intervall_monate"}
        )
    return pd.DataFrame()

def hole_untergewerk_daten():
    _init_mock_store()
    return pd.DataFrame(st.session_state.mock_untergewerk)
