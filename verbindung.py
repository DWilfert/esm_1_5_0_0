import os
import re
import sqlite3
import logging

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

try:
    import mysql.connector  # type: ignore
except Exception:  # pragma: no cover - optional dependency in demo mode
    mysql = None


def _sqlite_sql_from_mysql(sql):
    if not isinstance(sql, str):
        return sql
    return re.sub(r"(?<!%)%s", "?", sql)


class DictCursor:
    def __init__(self, cursor):
        self._cursor = cursor

    def execute(self, *args, **kwargs):
        if args and isinstance(args[0], str):
            args = (_sqlite_sql_from_mysql(args[0]), *args[1:])
        return self._cursor.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self._cursor.executemany(*args, **kwargs)

    def fetchone(self):
        row = self._cursor.fetchone()
        if row is None:
            return None
        return {key: row[key] for key in row.keys()}

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [{key: row[key] for key in row.keys()} for row in rows]

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class SQLiteConnectionAdapter:
    def __init__(self, connection):
        self._connection = connection

    def is_connected(self):
        return True

    def cursor(self, dictionary=False, *args, **kwargs):
        cursor = self._connection.cursor(*args, **kwargs)
        if dictionary:
            cursor.row_factory = sqlite3.Row
            return DictCursor(cursor)
        return cursor

    def execute(self, *args, **kwargs):
        if args and isinstance(args[0], str):
            args = (_sqlite_sql_from_mysql(args[0]), *args[1:])
        return self._connection.execute(*args, **kwargs)

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()

    def __getattr__(self, name):
        return getattr(self._connection, name)


DEMO_TABLES = {
    "anlagen": [
        {"id": 1, "anlagebezeichnung": "Hauptwerk - Kesselanlage", "anlagenr": "AN-1001", "anlagetyp": "Technik", "hersteller": "Bosch", "typ": "KSB-200", "seriennummer": "K-1001", "zustand": "gut", "beschreibung": "Zentrale Energieversorgung", "standort_text": "NP", "standort": "NP", "ort_kurz": "NP", "anlage_id": 1},
        {"id": 2, "anlagebezeichnung": "Lagerhalle Nord - Lagerregal", "anlagenr": "AN-1002", "anlagetyp": "Logistik", "hersteller": "SSI Schafer", "typ": "LRS-200", "seriennummer": "L-1002", "zustand": "ok", "beschreibung": "Automatisches Regalzugangssystem", "standort_text": "FG", "standort": "FG", "ort_kurz": "FG", "anlage_id": 2},
        {"id": 3, "anlagebezeichnung": "Serverraum - UPS", "anlagenr": "AN-1003", "anlagetyp": "IT", "hersteller": "APC", "typ": "Smart-UPS 3000", "seriennummer": "U-1003", "zustand": "kritisch", "beschreibung": "Notstromversorgung der IT-Infrastruktur", "standort_text": "NP", "standort": "NP", "ort_kurz": "NP", "anlage_id": 3},
        {"id": 4, "anlagebezeichnung": "Kantine - Küchenanlage", "anlagenr": "AN-1004", "anlagetyp": "Gebaeude", "hersteller": "Miele", "typ": "Kueche-400", "seriennummer": "K-1004", "zustand": "gut", "beschreibung": "Kuechenausstattung und Haustechnik", "standort_text": "FG", "standort": "FG", "ort_kurz": "FG", "anlage_id": 4},
        {"id": 5, "anlagebezeichnung": "Aufzug West - Personenaufzug", "anlagenr": "AN-1005", "anlagetyp": "Mobilitaet", "hersteller": "Otis", "typ": "Gen2", "seriennummer": "P-1005", "zustand": "warnung", "beschreibung": "Personenaufzug West", "standort_text": "NP", "standort": "NP", "ort_kurz": "NP", "anlage_id": 5},
        {"id": 6, "anlagebezeichnung": "Werkstatt - Drehmaschine", "anlagenr": "AN-1006", "anlagetyp": "Produktion", "hersteller": "DMG Mori", "typ": "CMX 1100", "seriennummer": "D-1006", "zustand": "gut", "beschreibung": "CNC Drehmaschine", "standort_text": "FG", "standort": "FG", "ort_kurz": "FG", "anlage_id": 6},
        {"id": 7, "anlagebezeichnung": "Verteiler 1 - Schaltanlage", "anlagenr": "AN-1007", "anlagetyp": "Elektro", "hersteller": "Siemens", "typ": "S7-1200", "seriennummer": "S-1007", "zustand": "ok", "beschreibung": "Zentrale Schaltanlage", "standort_text": "NP", "standort": "NP", "ort_kurz": "NP", "anlage_id": 7},
        {"id": 8, "anlagebezeichnung": "Buerotrakt A - Klimaanlage", "anlagenr": "AN-1008", "anlagetyp": "Gebaeude", "hersteller": "Daikin", "typ": "FTXJ25", "seriennummer": "C-1008", "zustand": "warnung", "beschreibung": "Klimaanlage fuer Buero", "standort_text": "FG", "standort": "FG", "ort_kurz": "FG", "anlage_id": 8},
        {"id": 9, "anlagebezeichnung": "Fertigungshof - Spritzanlage", "anlagenr": "AN-1009", "anlagetyp": "Produktion", "hersteller": "Arburg", "typ": "Allrounder 320", "seriennummer": "A-1009", "zustand": "gut", "beschreibung": "Spritzgussmaschine", "standort_text": "NP", "standort": "NP", "ort_kurz": "NP", "anlage_id": 9},
        {"id": 10, "anlagebezeichnung": "Labor 3 - Reinraum", "anlagenr": "AN-1010", "anlagetyp": "Labor", "hersteller": "M+W", "typ": "CleanLab", "seriennummer": "L-1010", "zustand": "kritisch", "beschreibung": "Reinraum und Prozesssteuerung", "standort_text": "FG", "standort": "FG", "ort_kurz": "FG", "anlage_id": 10},
    ],
    "standort": [
        {"id": 1, "ort_kurz": "NP", "ort": "Neuperlach"},
        {"id": 2, "ort_kurz": "FG", "ort": "Fasangarten"},
    ],
    "kostengruppen": [
        {"kg_nr": 101, "kg_txt": "Heizung / Energie"},
        {"kg_nr": 102, "kg_txt": "Lueftung / Klima"},
        {"kg_nr": 103, "kg_txt": "Elektrotechnik"},
        {"kg_nr": 104, "kg_txt": "Gebaeudeautomation"},
        {"kg_nr": 105, "kg_txt": "Sicherheitsanlagen"},
        {"kg_nr": 106, "kg_txt": "Logistiksysteme"},
        {"kg_nr": 107, "kg_txt": "IT / Netz"},
        {"kg_nr": 108, "kg_txt": "Laboranlagen"},
        {"kg_nr": 109, "kg_txt": "Werkstatt / Produktion"},
        {"kg_nr": 110, "kg_txt": "Transport / Aufzug"},
    ],
    "untergewerk": [
        {"id": 1, "unter_nr": 1, "unter_txt": "Heizung"},
        {"id": 2, "unter_nr": 2, "unter_txt": "Klimaanlage"},
        {"id": 3, "unter_nr": 3, "unter_txt": "Aufzug"},
        {"id": 4, "unter_nr": 4, "unter_txt": "Brandmeldeanlage"},
        {"id": 5, "unter_nr": 5, "unter_txt": "Lichtsteuerung"},
        {"id": 6, "unter_nr": 6, "unter_txt": "PV-Anlage"},
        {"id": 7, "unter_nr": 7, "unter_txt": "Sprinkler"},
        {"id": 8, "unter_nr": 8, "unter_txt": "Netzwerk"},
        {"id": 9, "unter_nr": 9, "unter_txt": "Messtechnik"},
        {"id": 10, "unter_nr": 10, "unter_txt": "Datenzentrum"},
    ],
    "vertragsanalyse": [
        {"id": 1, "vertrag": "V-1001", "vertragsname": "V-1001", "kunde": "Muller GmbH", "firma": "Muller GmbH", "firmenname": "Muller GmbH", "firma_id": 1, "status": "aktiv", "vertragsart": "Service", "volumen": 120000, "standort_text": "NP", "kosten_bestand_pa": 120000.0, "benchmark_ais_pa": 98400.0, "laufzeit_bis": "2028-12-31", "naechste_wartung": "2026-09-12", "zyklus_monate": 12, "anlage_id": 1, "anlagebezeichnung": "Hauptwerk - Kesselanlage"},
        {"id": 2, "vertrag": "V-1002", "vertragsname": "V-1002", "kunde": "Schmidt AG", "firma": "Schmidt AG", "firmenname": "Schmidt AG", "firma_id": 2, "status": "aktiv", "vertragsart": "Wartung", "volumen": 98000, "standort_text": "FG", "kosten_bestand_pa": 98000.0, "benchmark_ais_pa": 80360.0, "laufzeit_bis": "2027-06-30", "naechste_wartung": "2026-08-30", "zyklus_monate": 6, "anlage_id": 2, "anlagebezeichnung": "Lagerhalle Nord - Lagerregal"},
        {"id": 3, "vertrag": "V-1003", "vertragsname": "V-1003", "kunde": "Fischer Logistics", "firma": "Fischer Logistics", "firmenname": "Fischer Logistics", "firma_id": 3, "status": "pruefung", "vertragsart": "Monitoring", "volumen": 154000, "standort_text": "NP", "kosten_bestand_pa": 154000.0, "benchmark_ais_pa": 126280.0, "laufzeit_bis": "2029-03-31", "naechste_wartung": "2026-07-20", "zyklus_monate": 12, "anlage_id": 3, "anlagebezeichnung": "Serverraum - UPS"},
        {"id": 4, "vertrag": "V-1004", "vertragsname": "V-1004", "kunde": "Apex Technik", "firma": "Apex Technik", "firmenname": "Apex Technik", "firma_id": 4, "status": "aktiv", "vertragsart": "Service", "volumen": 87000, "standort_text": "FG", "kosten_bestand_pa": 87000.0, "benchmark_ais_pa": 71340.0, "laufzeit_bis": "2028-08-31", "naechste_wartung": "2026-10-05", "zyklus_monate": 6, "anlage_id": 4, "anlagebezeichnung": "Kantine - Küchenanlage"},
        {"id": 5, "vertrag": "V-1005", "vertragsname": "V-1005", "kunde": "Nordenergie", "firma": "Nordenergie", "firmenname": "Nordenergie", "firma_id": 5, "status": "inaktiv", "vertragsart": "Wartung", "volumen": 64000, "standort_text": "NP", "kosten_bestand_pa": 64000.0, "benchmark_ais_pa": 52480.0, "laufzeit_bis": "2026-12-31", "naechste_wartung": "2026-08-06", "zyklus_monate": 12, "anlage_id": 5, "anlagebezeichnung": "Aufzug West - Personenaufzug"},
        {"id": 6, "vertrag": "V-1006", "vertragsname": "V-1006", "kunde": "Green Plant", "firma": "Green Plant", "firmenname": "Green Plant", "firma_id": 6, "status": "aktiv", "vertragsart": "Service", "volumen": 142500, "standort_text": "FG", "kosten_bestand_pa": 142500.0, "benchmark_ais_pa": 116850.0, "laufzeit_bis": "2029-09-30", "naechste_wartung": "2026-09-15", "zyklus_monate": 12, "anlage_id": 6, "anlagebezeichnung": "Werkstatt - Drehmaschine"},
        {"id": 7, "vertrag": "V-1007", "vertragsname": "V-1007", "kunde": "Control Labs", "firma": "Control Labs", "firmenname": "Control Labs", "firma_id": 7, "status": "aktiv", "vertragsart": "Monitoring", "volumen": 91000, "standort_text": "NP", "kosten_bestand_pa": 91000.0, "benchmark_ais_pa": 74500.0, "laufzeit_bis": "2027-11-30", "naechste_wartung": "2026-11-02", "zyklus_monate": 6, "anlage_id": 7, "anlagebezeichnung": "Verteiler 1 - Schaltanlage"},
        {"id": 8, "vertrag": "V-1008", "vertragsname": "V-1008", "kunde": "Sonnenhaus", "firma": "Sonnenhaus", "firmenname": "Sonnenhaus", "firma_id": 8, "status": "pruefung", "vertragsart": "Wartung", "volumen": 111000, "standort_text": "FG", "kosten_bestand_pa": 111000.0, "benchmark_ais_pa": 90900.0, "laufzeit_bis": "2028-05-31", "naechste_wartung": "2026-06-18", "zyklus_monate": 12, "anlage_id": 8, "anlagebezeichnung": "Buerotrakt A - Klimaanlage"},
        {"id": 9, "vertrag": "V-1009", "vertragsname": "V-1009", "kunde": "Leichtbau GmbH", "firma": "Leichtbau GmbH", "firmenname": "Leichtbau GmbH", "firma_id": 9, "status": "aktiv", "vertragsart": "Service", "volumen": 76000, "standort_text": "NP", "kosten_bestand_pa": 76000.0, "benchmark_ais_pa": 62320.0, "laufzeit_bis": "2026-10-15", "naechste_wartung": "2026-07-12", "zyklus_monate": 6, "anlage_id": 9, "anlagebezeichnung": "Fertigungshof - Spritzanlage"},
        {"id": 10, "vertrag": "V-1010", "vertragsname": "V-1010", "kunde": "MetroService", "firma": "MetroService", "firmenname": "MetroService", "firma_id": 10, "status": "aktiv", "vertragsart": "Monitoring", "volumen": 205000, "standort_text": "FG", "kosten_bestand_pa": 205000.0, "benchmark_ais_pa": 168100.0, "laufzeit_bis": "2030-02-28", "naechste_wartung": "2026-10-20", "zyklus_monate": 12, "anlage_id": 10, "anlagebezeichnung": "Labor 3 - Reinraum"},
    ],
    "firmeninfo": [
        {"id": 1, "firmenname": "Muller GmbH", "firma": "Muller GmbH", "firmebranche": "Facility Management", "firmenadresse": "Musterstr. 1, Hamburg", "firmentelefon": "+49 40 1234 560", "firmenfax": "+49 40 1234 561", "firmenEMail": "info@muller.de", "firmenwebsite": "https://muller.de", "firmenansprechpartner": "Anna Müller", "branche": "Facility & Asset Management", "standort": "Hamburg", "kontakt": "info@muller.de"},
        {"id": 2, "firmenname": "Schmidt AG", "firma": "Schmidt AG", "firmebranche": "Logistik", "firmenadresse": "Industriestr. 22, Berlin", "firmentelefon": "+49 30 2222 101", "firmenfax": "+49 30 2222 102", "firmenEMail": "kontakt@schmidt-ag.de", "firmenwebsite": "https://schmidt-ag.de", "firmenansprechpartner": "M. Schmidt", "branche": "Logistik", "standort": "Berlin", "kontakt": "kontakt@schmidt-ag.de"},
        {"id": 3, "firmenname": "Fischer Logistics", "firma": "Fischer Logistics", "firmebranche": "Transport", "firmenadresse": "Werkstr. 4, Dresden", "firmentelefon": "+49 351 2200 400", "firmenfax": "+49 351 2200 401", "firmenEMail": "info@fischer-logistics.de", "firmenwebsite": "https://fischer-logistics.de", "firmenansprechpartner": "T. Fischer", "branche": "Transport", "standort": "Dresden", "kontakt": "info@fischer-logistics.de"},
        {"id": 4, "firmenname": "Apex Technik", "firma": "Apex Technik", "firmebranche": "Produktion", "firmenadresse": "Tech Park 3, Stuttgart", "firmentelefon": "+49 711 4500 300", "firmenfax": "+49 711 4500 301", "firmenEMail": "service@apex-technik.de", "firmenwebsite": "https://apex-technik.de", "firmenansprechpartner": "J. Klein", "branche": "Produktion", "standort": "Stuttgart", "kontakt": "service@apex-technik.de"},
        {"id": 5, "firmenname": "Nordenergie", "firma": "Nordenergie", "firmebranche": "Energie", "firmenadresse": "Energieweg 12, Hamburg", "firmentelefon": "+49 40 5150 100", "firmenfax": "+49 40 5150 101", "firmenEMail": "support@nordenergie.de", "firmenwebsite": "https://nordenergie.de", "firmenansprechpartner": "K. Nord", "branche": "Energie", "standort": "Hamburg", "kontakt": "support@nordenergie.de"},
        {"id": 6, "firmenname": "Green Plant", "firma": "Green Plant", "firmebranche": "Sustainability", "firmenadresse": "Umweltstr. 8, Leipzig", "firmentelefon": "+49 341 8899 120", "firmenfax": "+49 341 8899 121", "firmenEMail": "hello@greenplant.de", "firmenwebsite": "https://greenplant.de", "firmenansprechpartner": "M. Gruen", "branche": "Sustainability", "standort": "Leipzig", "kontakt": "hello@greenplant.de"},
        {"id": 7, "firmenname": "Control Labs", "firma": "Control Labs", "firmebranche": "Laboranalytik", "firmenadresse": "Labstr. 14, Mannheim", "firmentelefon": "+49 621 6600 710", "firmenfax": "+49 621 6600 711", "firmenEMail": "team@controllabs.de", "firmenwebsite": "https://controllabs.de", "firmenansprechpartner": "E. Sommer", "branche": "Laboranalytik", "standort": "Mannheim", "kontakt": "team@controllabs.de"},
        {"id": 8, "firmenname": "Sonnenhaus", "firma": "Sonnenhaus", "firmebranche": "Gebaeudetechnik", "firmenadresse": "Solarweg 7, Berlin", "firmentelefon": "+49 30 7770 200", "firmenfax": "+49 30 7770 201", "firmenEMail": "kontakt@sonnenhaus.de", "firmenwebsite": "https://sonnenhaus.de", "firmenansprechpartner": "C. Hell", "branche": "Gebaeudetechnik", "standort": "Berlin", "kontakt": "kontakt@sonnenhaus.de"},
        {"id": 9, "firmenname": "Leichtbau GmbH", "firma": "Leichtbau GmbH", "firmebranche": "Werkstoffe", "firmenadresse": "Materialstr. 16, Dortmund", "firmentelefon": "+49 231 7750 230", "firmenfax": "+49 231 7750 231", "firmenEMail": "kontakt@leichtbau.de", "firmenwebsite": "https://leichtbau.de", "firmenansprechpartner": "P. Leicht", "branche": "Werkstoffe", "standort": "Dortmund", "kontakt": "kontakt@leichtbau.de"},
        {"id": 10, "firmenname": "MetroService", "firma": "MetroService", "firmebranche": "Service", "firmenadresse": "Serviceplatz 3, Essen", "firmentelefon": "+49 201 4040 550", "firmenfax": "+49 201 4040 551", "firmenEMail": "office@metroservice.de", "firmenwebsite": "https://metroservice.de", "firmenansprechpartner": "L. Mertens", "branche": "Service", "standort": "Essen", "kontakt": "office@metroservice.de"},
    ],
    "service": [
        {"id": 1, "anlage_id": 1, "standort_text": "NP", "anlagenklasse": "Heizung", "bezeichnung_anlagenklasse": "Heizung", "anlagebezeichnung": "Hauptwerk - Kesselanlage", "kennz_1": "HZ-01", "kennz_2": "A", "kurzfassung": "Pruefung und Reinigung des Heizkreises", "intervall": "6 Monate", "hinweis": "Leckpruefung erforderlich", "gesetzl_grundlage": "DIN EN 60204", "textstelle_gesetz": "Abschnitt 5.2", "qualifikation": "Mechatroniker", "entlastung_schadensfall": "Notfallplan aktiv"},
        {"id": 2, "anlage_id": 2, "standort_text": "FG", "anlagenklasse": "Logistik", "bezeichnung_anlagenklasse": "Lagerregal", "anlagebezeichnung": "Lagerhalle Nord - Lagerregal", "kennz_1": "LG-02", "kennz_2": "B", "kurzfassung": "Fahrzeugdiagnose und Riemencheck", "intervall": "3 Monate", "hinweis": "Pruefung der Sicherheitstuer", "gesetzl_grundlage": "DGUV Vorschrift 1", "textstelle_gesetz": "Kapitel 2.3", "qualifikation": "Fachkraft Logistik", "entlastung_schadensfall": "Reservelager aktiv"},
        {"id": 3, "anlage_id": 3, "standort_text": "NP", "anlagenklasse": "IT", "bezeichnung_anlagenklasse": "UPS", "anlagebezeichnung": "Serverraum - UPS", "kennz_1": "IT-03", "kennz_2": "C", "kurzfassung": "Batterie- und Loadtest", "intervall": "12 Monate", "hinweis": "Ausfallrisiko bei Temperaturspitzen", "gesetzl_grundlage": "VDE 0100", "textstelle_gesetz": "Abschnitt 7.4", "qualifikation": "IT-Servicetechniker", "entlastung_schadensfall": "Redundante Versorgung"},
        {"id": 4, "anlage_id": 4, "standort_text": "FG", "anlagenklasse": "Gebaeude", "bezeichnung_anlagenklasse": "Kuechenausstattung", "anlagebezeichnung": "Kantine - Küchenanlage", "kennz_1": "GB-04", "kennz_2": "D", "kurzfassung": "Reinigung und Sicherheitscheck", "intervall": "4 Monate", "hinweis": "Abzugseinrichtung kontrollieren", "gesetzl_grundlage": "TRGS 500", "textstelle_gesetz": "Abschnitt 3.1", "qualifikation": "Facility Technician", "entlastung_schadensfall": "Notbetrieb eingerichtet"},
        {"id": 5, "anlage_id": 5, "standort_text": "NP", "anlagenklasse": "Aufzug", "bezeichnung_anlagenklasse": "Personenaufzug", "anlagebezeichnung": "Aufzug West - Personenaufzug", "kennz_1": "AU-05", "kennz_2": "E", "kurzfassung": "Sicherheitsabnahme und Schachtcheck", "intervall": "6 Monate", "hinweis": "Notruftest erfolgreich", "gesetzl_grundlage": "LBO", "textstelle_gesetz": "Abschnitt 10.2", "qualifikation": "Aufzugmonteur", "entlastung_schadensfall": "Alternativer Zugang freigegeben"},
        {"id": 6, "anlage_id": 6, "standort_text": "FG", "anlagenklasse": "Produktion", "bezeichnung_anlagenklasse": "Drehmaschine", "anlagebezeichnung": "Werkstatt - Drehmaschine", "kennz_1": "PR-06", "kennz_2": "F", "kurzfassung": "Spindel- und Werkzeugkontrolle", "intervall": "4 Monate", "hinweis": "Wertzeugzustand im Grenzbereich", "gesetzl_grundlage": "BGV C1", "textstelle_gesetz": "Kapitel 4.1", "qualifikation": "Maschinenwart", "entlastung_schadensfall": "Reserveanlage bereitgestellt"},
        {"id": 7, "anlage_id": 7, "standort_text": "NP", "anlagenklasse": "Elektro", "bezeichnung_anlagenklasse": "Schaltanlage", "anlagebezeichnung": "Verteiler 1 - Schaltanlage", "kennz_1": "EL-07", "kennz_2": "G", "kurzfassung": "Thermografie und Schutzkontaktcheck", "intervall": "12 Monate", "hinweis": "Kontaktorspannung leicht erhöht", "gesetzl_grundlage": "DIN VDE 0105", "textstelle_gesetz": "Abschnitt 7.1", "qualifikation": "Elektrofachkraft", "entlastung_schadensfall": "Reserveverteiler aktiv"},
        {"id": 8, "anlage_id": 8, "standort_text": "FG", "anlagenklasse": "Gebaeude", "bezeichnung_anlagenklasse": "Klimaanlage", "anlagebezeichnung": "Buerotrakt A - Klimaanlage", "kennz_1": "KL-08", "kennz_2": "H", "kurzfassung": "Filterwechsel und Luftqualitaetsmessung", "intervall": "3 Monate", "hinweis": "Ueberwachung der Luftfeuchtigkeit", "gesetzl_grundlage": "VDI 6022", "textstelle_gesetz": "Abschnitt 6", "qualifikation": "HVAC Technician", "entlastung_schadensfall": "Zweiter Kreislauf vorbereitet"},
        {"id": 9, "anlage_id": 9, "standort_text": "NP", "anlagenklasse": "Produktion", "bezeichnung_anlagenklasse": "Spritzanlage", "anlagebezeichnung": "Fertigungshof - Spritzanlage", "kennz_1": "PR-09", "kennz_2": "I", "kurzfassung": "Dichtung und Druckbereich prüfen", "intervall": "6 Monate", "hinweis": "Dichtung scheint verschlissen", "gesetzl_grundlage": "BGV C1", "textstelle_gesetz": "Kapitel 5.2", "qualifikation": "Maschinenmeister", "entlastung_schadensfall": "Reserveanlage organisiert"},
        {"id": 10, "anlage_id": 10, "standort_text": "FG", "anlagenklasse": "Labor", "bezeichnung_anlagenklasse": "Reinraum", "anlagebezeichnung": "Labor 3 - Reinraum", "kennz_1": "LB-10", "kennz_2": "J", "kurzfassung": "Partikelmessung und Reinraumbewertung", "intervall": "1 Monat", "hinweis": "Stetige Temperaturregelung erforderlich", "gesetzl_grundlage": "ISO 14644", "textstelle_gesetz": "Kapitel 8", "qualifikation": "Reinraumbeauftragter", "entlastung_schadensfall": "Ausweichbereich freigegeben"},
    ],
    "auffaelligkeiten": [
        {"id": 1, "anlage_id": 1, "vertrag": "V-1001", "protokolldatei": "Protokoll-001.pdf", "standort_text": "NP", "kommentar": "Kritischer Defekt: Temperaturabweichung an Kessel 1"},
        {"id": 2, "anlage_id": 2, "vertrag": "V-1002", "protokolldatei": "Protokoll-002.pdf", "standort_text": "FG", "kommentar": "Leichte Verschiebung im Regalbereich; sofort prüfen"},
        {"id": 3, "anlage_id": 3, "vertrag": "V-1003", "protokolldatei": "Protokoll-003.pdf", "standort_text": "NP", "kommentar": "UPS Batterie leicht unter Spannung"},
        {"id": 4, "anlage_id": 4, "vertrag": "V-1004", "protokolldatei": "Protokoll-004.pdf", "standort_text": "FG", "kommentar": "Abzugseinrichtung wurde im Prüfintervall nicht dokumentiert"},
        {"id": 5, "anlage_id": 5, "vertrag": "V-1005", "protokolldatei": "Protokoll-005.pdf", "standort_text": "NP", "kommentar": "Aufzugnotruf verzoegert; Wartung erforderlich"},
        {"id": 6, "anlage_id": 6, "vertrag": "V-1006", "protokolldatei": "Protokoll-006.pdf", "standort_text": "FG", "kommentar": "Spindelvibration erhöht, weitere Messung erforderlich"},
        {"id": 7, "anlage_id": 7, "vertrag": "V-1007", "protokolldatei": "Protokoll-007.pdf", "standort_text": "NP", "kommentar": "Temperaturverlauf im Verteiler zeigt leichte Abweichung"},
        {"id": 8, "anlage_id": 8, "vertrag": "V-1008", "protokolldatei": "Protokoll-008.pdf", "standort_text": "FG", "kommentar": "Luftfeuchtigkeit im Grenzbereich, Filterwechsel empfohlen"},
        {"id": 9, "anlage_id": 9, "vertrag": "V-1009", "protokolldatei": "Protokoll-009.pdf", "standort_text": "NP", "kommentar": "Dichtung verschlissen, weitere Prüfung in 2 Wochen"},
        {"id": 10, "anlage_id": 10, "vertrag": "V-1010", "protokolldatei": "Protokoll-010.pdf", "standort_text": "FG", "kommentar": "Reinraumpartikelwert leicht ueber Grenzwert"},
    ],
    "wartungsuebersicht": [
        {"id": 1, "anlage": "Hauptwerk - Kesselanlage", "typ": "Jahreswartung", "status": "offen", "kosten": 5400},
        {"id": 2, "anlage": "Lagerhalle Nord - Lagerregal", "typ": "Routine", "status": "erledigt", "kosten": 2200},
        {"id": 3, "anlage": "Serverraum - UPS", "typ": "Vollwartung", "status": "offen", "kosten": 6300},
        {"id": 4, "anlage": "Kantine - Küchenanlage", "typ": "Pruefung", "status": "erledigt", "kosten": 1700},
        {"id": 5, "anlage": "Aufzug West - Personenaufzug", "typ": "Sicherheitscheck", "status": "offen", "kosten": 3100},
        {"id": 6, "anlage": "Werkstatt - Drehmaschine", "typ": "Inspektion", "status": "erledigt", "kosten": 2600},
        {"id": 7, "anlage": "Verteiler 1 - Schaltanlage", "typ": "Pruefung", "status": "offen", "kosten": 2800},
        {"id": 8, "anlage": "Buerotrakt A - Klimaanlage", "typ": "Routine", "status": "offen", "kosten": 1800},
        {"id": 9, "anlage": "Fertigungshof - Spritzanlage", "typ": "Vollwartung", "status": "erledigt", "kosten": 4200},
        {"id": 10, "anlage": "Labor 3 - Reinraum", "typ": "Validierung", "status": "offen", "kosten": 4700},
    ],
    "einstellungen": [
        {"id": 1, "schluessel": "dokumenten_pfad", "wert": "C:/esm_dokumente"},
    ],
}


def _demo_mode_enabled():
    value = os.environ.get("ESM_DEMO_MODE", "true").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _normalisiere_demo_daten():
    for table_name, rows in DEMO_TABLES.items():
        if table_name == "vertragsanalyse":
            for row in rows:
                row.setdefault("vertragsname", row.get("vertrag", f"V-{row.get('id', 0):04d}"))
                row.setdefault("vertragsart", "Wartung")
                row.setdefault("standort_text", "NP" if int(row.get("id", 1)) % 2 == 1 else "FG")
                row.setdefault("kosten_bestand_pa", float(row.get("volumen", 0) or 0))
                row.setdefault("benchmark_ais_pa", float(row.get("volumen", 0) or 0) * 0.82)
                row.setdefault("naechste_wartung", row.get("laufzeit_bis", "2026-12-31"))
                row.setdefault("zyklus_monate", 12)
                row.setdefault("firma_id", row.get("id", 1))
                row.setdefault("firma", row.get("kunde", "ESM GmbH"))
                row.setdefault("firmenname", row.get("kunde", "ESM GmbH"))
        elif table_name == "firmeninfo":
            for row in rows:
                row.setdefault("firmenname", row.get("firma", "ESM GmbH"))
                row.setdefault("standort_text", row.get("standort", "Standort"))
        elif table_name == "wartungsuebersicht":
            vertrags_rows = DEMO_TABLES.get("vertragsanalyse", [])
            for idx, row in enumerate(rows):
                source = vertrags_rows[idx] if idx < len(vertrags_rows) else {}
                row.setdefault("vertragsname", source.get("vertragsname", f"V-{idx + 1:04d}"))
                row.setdefault("firma", source.get("firmenname", source.get("kunde", f"Firma {idx + 1}")))
                row.setdefault("standort", source.get("standort_text", "NP"))
                row.setdefault("standort_text", source.get("standort_text", "NP"))
                row.setdefault("anlagebezeichnung", source.get("anlagebezeichnung", row.get("anlage", f"Anlage {idx + 1}")))
                row.setdefault("anlagenname", row.get("anlagebezeichnung", source.get("anlagebezeichnung", f"Anlage {idx + 1}")))
                row.setdefault("naechste_wartung", source.get("naechste_wartung", "2026-12-31"))
                row.setdefault("kosten_bestand_pa", float(row.get("kosten", 0) or 0))
                row.setdefault("benchmark_ais_pa", float(row.get("kosten", 0) or 0) * 0.82)


def _zeige_demo_status_info():
    session_state = getattr(st, "session_state", None)
    if session_state is None:
        return

    if not getattr(session_state, "demo_db_status_message_angezeigt", False):
        st.info("Demoversion,Verbindung zu Mysql wird Simuliert")
        session_state.demo_db_status_message_angezeigt = True


def _baue_demo_sqlite_verbindung():
    _normalisiere_demo_daten()
    conn = sqlite3.connect(":memory:")
    for table_name, rows in DEMO_TABLES.items():
        if not rows:
            continue
        columns = list(rows[0].keys())
        column_defs = ", ".join(
            f"{column} TEXT" if isinstance(rows[0][column], str) else f"{column} REAL" if isinstance(rows[0][column], float) else f"{column} INTEGER"
            for column in columns
        )
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        conn.execute(f"CREATE TABLE {table_name} ({column_defs})")
        placeholders = ", ".join(["?"] * len(columns))
        for row in rows:
            values = [row.get(column) for column in columns]
            conn.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
    conn.commit()
    return SQLiteConnectionAdapter(conn)


def _versuche_mysql_verbindung():
    if mysql is None:
        return None

    secrets = getattr(st, "secrets", None)
    if secrets and "mysql" in secrets:
        cfg = secrets["mysql"]
        host = cfg.get("host")
        user = cfg.get("user")
        password = cfg.get("password")
        database = cfg.get("database")
        port = int(cfg.get("port", 3306))
    else:
        host = os.environ.get("MYSQL_HOST")
        user = os.environ.get("MYSQL_USER")
        password = os.environ.get("MYSQL_PASSWORD")
        database = os.environ.get("MYSQL_DATABASE")
        port = int(os.environ.get("MYSQL_PORT", 3306))

    if not (host and user and database):
        return None

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connection_timeout=10,
        )
        if conn.is_connected():
            return conn
    except Exception as exc:  # pragma: no cover
        logger.warning("MySQL-Verbindung fehlgeschlagen, nutze Demo-Modus: %s", exc)
        return None
    return None


def hole_datenbank_verbindung(max_retries: int = 3, backoff_seconds: int = 1, timeout: int = 10):
    """Verbindung zu einer simulierten MySQL (Demo) oder optional einer echten MySQL.

    Standardmaessig verwendet die App die lokale Demo-Simulation, damit sie ohne echte
    MySQL-Instanz auf GitHub, in Präsentationen und im lokalen Demo-Lauf lauffaehig ist.
    Eine echte MySQL-Verbindung kann nur gezielt via Umgebungsvariable aktiviert werden.
    """
    use_real_db = os.environ.get("ESM_USE_REAL_DB", "0").strip().lower() in {"1", "true", "yes", "on"}

    if use_real_db:
        conn = _versuche_mysql_verbindung()
        if conn is not None:
            return conn
        _zeige_demo_status_info()

    if _demo_mode_enabled():
        return _baue_demo_sqlite_verbindung()

    conn = _versuche_mysql_verbindung()
    if conn is not None:
        return conn

    _zeige_demo_status_info()
    return _baue_demo_sqlite_verbindung()


def initialisiere_beispieldaten():
    return _baue_demo_sqlite_verbindung()


def hole_anlagen_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM anlagen", conn)
        except Exception:
            _zeige_demo_status_info()
            logger.info("Anlagendaten konnten nicht geladen werden. Demo-DB wird verwendet.")
        finally:
            try:
                if hasattr(conn, "is_connected") and conn.is_connected():
                    conn.close()
            except Exception:
                pass
    return pd.DataFrame()


def hole_wartungsvertraege_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM vertragsanalyse", conn)
        except Exception:
            _zeige_demo_status_info()
            logger.info("Vertragsanalyse-Daten konnten nicht geladen werden. Demo-DB wird verwendet.")
        finally:
            try:
                if hasattr(conn, "is_connected") and conn.is_connected():
                    conn.close()
            except Exception:
                pass
    return pd.DataFrame()


def hole_firmen_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM firmeninfo", conn)
        except Exception:
            _zeige_demo_status_info()
            logger.info("Firmeninformationen konnten nicht geladen werden. Demo-DB wird verwendet.")
        finally:
            try:
                if hasattr(conn, "is_connected") and conn.is_connected():
                    conn.close()
            except Exception:
                pass
    return pd.DataFrame()


def hole_wartungsuebersicht_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM wartungsuebersicht", conn)
        except Exception:
            _zeige_demo_status_info()
            logger.info("Wartungsuebersicht konnte nicht geladen werden. Demo-DB wird verwendet.")
        finally:
            try:
                if hasattr(conn, "is_connected") and conn.is_connected():
                    conn.close()
            except Exception:
                pass
    return pd.DataFrame()


def hole_untergewerk_daten():
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            return pd.read_sql("SELECT * FROM untergewerk", conn)
        except Exception:
            _zeige_demo_status_info()
            logger.info("Untergewerk-Daten konnten nicht geladen werden. Demo-DB wird verwendet.")
        finally:
            try:
                if hasattr(conn, "is_connected") and conn.is_connected():
                    conn.close()
            except Exception:
                pass
    return pd.DataFrame()