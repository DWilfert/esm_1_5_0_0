import streamlit as st
import mysql.connector
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import prepare_display_dataframe, render_page_header, render_section_header

def zeige_adminbereich():
    admin_passwort = "esm"
    
    st.markdown("""
        <style>
        .ent-subheader { font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px; margin-top: 10px; }
        
        div[data-baseweb="input"]:has(input[aria-label*="MySQL Server-Host"]),
        div[data-baseweb="input"]:has(input[aria-label*="Datenbank-Benutzername"]) {
            max-width: 60% !important;
        }
        div[data-baseweb="input"]:has(input[aria-label*="Port"]) {
            max-width: 50% !important;
        }
        
        .custom-huge-title {
            font-family: 'Segoe UI', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif !important;
            font-size: 2.8rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.05em !important;
            margin-bottom: 0px !important;
            line-height: 1.1 !important;
            white-space: nowrap !important;
            color: var(--text-color, #e2e8f0) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns([3.0, 4.0, 3.0])
    with col_p1:
        eingabe_passwort = st.text_input(
            "Bitte Admin-Passwort eingeben:" if st.session_state.get("language", "de") == "de" else "Please enter Admin password:",
            type="password"
        )
    
    if eingabe_passwort != admin_passwort:
        if eingabe_passwort != "":
            st.error("Falsches Passwort!" if st.session_state.get("language", "de") == "de" else "Incorrect password!")
        st.stop()
    
    lang = st.session_state.get("language", "de")
    
    txt = {
        "de": {
            "titel": "Admin-Bereich & Systemkonfiguration",
            "untertitel": "Zentrale Steuerung der Umgebungsparameter, Datenbankverbindungen und System-Integrität.",
            "tab1": "System- & Serverparameter",
            "tab2": "Datenbank-Status",
            "sekt_titel": "Technische Umgebungsparameter",
            "host_label": "MySQL Server-Host (IP / FQDN):",
            "user_label": "Datenbank-Benutzername:",
            "schema_label": "Datenbank-Schema:",
            "pass_label": "MySQL-Passwort:",
            "port_label": "Port:",
            "pfad_label": "Zentraler Ablagepfad (Dokumenten-Root / Netzlaufwerk):",
            "btn_speichern": "Konfiguration speichern & Verbindung prüfen",
            "success_msg": "Verbindung erfolgreich hergestellt!",
            "error_msg": "Verbindung fehlgeschlagen.",
            "db_status_titel": "Datenbank-Integritätsprüfung (Echte Tabellen-Abfrage)",
            "db_check_btn": "Echten Tabellen-Status abrufen",
            "tabelle": "Tabelle",
            "status": "Status",
            "eintraege": "Anzahl Datensätze"
        },
        "en": {
            "titel": "Admin Area & System Configuration",
            "untertitel": "Central control of environment parameters, database connections, and system integrity.",
            "tab1": "System & Server Parameters",
            "tab2": "Database Status",
            "sekt_titel": "Technical Environment Parameters",
            "host_label": "MySQL Server Host (IP / FQDN):",
            "user_label": "Database Username:",
            "schema_label": "Database Schema:",
            "pass_label": "MySQL Password:",
            "port_label": "Port:",
            "pfad_label": "Central Storage Path (Document Root / Network Share):",
            "btn_speichern": "Save Configuration & Test Connection",
            "success_msg": "Connection established successfully!",
            "error_msg": "Connection failed.",
            "db_status_titel": "Database Integrity Check (Real Table Query)",
            "db_check_btn": "Fetch Real Table Status",
            "tabelle": "Table",
            "status": "Status",
            "eintraege": "Record Count"
        }
    }[lang]

    render_page_header(txt['titel'], txt['untertitel'])

    tab_sys, tab_db = st.tabs([txt["tab1"], txt["tab2"]])

    with tab_sys:
        render_section_header(txt['sekt_titel'])
        
        col1, col2, col3 = st.columns([3, 3, 4])
        with col1:
            host_val = st.text_input(txt["host_label"], value="localhost")
            user_val = st.text_input(txt["user_label"], value="root")
        with col2:
            schema_val = st.text_input(txt["schema_label"], value="wartungs_vertragsanalyse_db")
            pass_val = st.text_input(txt["pass_label"], type="password", value="esm")
        with col3:
            port_val = st.text_input(txt["port_label"], value="3306")

        col_pfad1, col_pfad2 = st.columns([6.0, 4.0])
        with col_pfad1:
            pfad_val = st.text_input(txt["pfad_label"], value="C:/esm_dokumente")
        
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(txt["btn_speichern"], type="primary"):
            conn = hole_datenbank_verbindung()
            if conn is not None:
                cursor = None
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS einstellungen (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            schluessel TEXT UNIQUE,
                            wert TEXT
                        )
                    """)
                    cursor.execute(
                        """
                        INSERT INTO einstellungen (schluessel, wert)
                        VALUES (?, ?)
                        ON CONFLICT(schluessel) DO UPDATE SET wert = excluded.wert
                        """,
                        ("dokumenten_pfad", pfad_val),
                    )
                    conn.commit()
                    st.success(txt["success_msg"] + " (Dokumenten-Pfad erfolgreich gespeichert)")
                except Exception as e:
                    st.error(f"Fehler beim Speichern der Einstellungen: {e}")
                finally:
                    if cursor:
                        cursor.close()
                    conn.close()
            else:
                st.error(txt["error_msg"])

    with tab_db:
        render_section_header(txt['db_status_titel'])
        
        if st.button(txt["db_check_btn"]):
            conn = hole_datenbank_verbindung()
            if conn is not None:
                cursor = None
                try:
                    cursor = conn.cursor()
                    tabellen_liste = ["anlagen", "vertragsanalyse", "service", "auffaelligkeiten", "firmeninfo", "standort"]
                    ergebnis_daten = []
                    
                    for tab in tabellen_liste:
                        try:
                            cursor.execute(f"SELECT COUNT(*) FROM `{tab}`")
                            anzahl = cursor.fetchone()[0]
                        except:
                            anzahl = 0
                        ergebnis_daten.append({
                            txt["tabelle"]: tab,
                            txt["status"]: "Online (Aktiv)",
                            txt["eintraege"]: anzahl
                        })
                    
                    df_status = pd.DataFrame(ergebnis_daten)
                    display_status = prepare_display_dataframe(df_status.rename(columns={
                        txt["tabelle"]: "Tabelle",
                        txt["status"]: "Status",
                        txt["eintraege"]: "Datensätze",
                    }))
                    st.dataframe(display_status, use_container_width=True, hide_index=True)
                except Exception as e:
                    st.error(f"Fehler beim Abrufen der Tabellen-Integrität: {e}")
                finally:
                    if cursor:
                        try:
                            cursor.close()
                        except:
                            pass
                    if conn and conn.is_connected():
                        conn.close()
            else:
                st.error("Keine Verbindung zur Datenbank möglich.")
        else:
            st.info("Klicken Sie auf den Button, um den echten Status und die Datensatzanzahl direkt aus MySQL auszulesen." if lang == "de" else "Click the button to fetch the real status and record count directly from MySQL.")

        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            render_section_header("Gefahrenbereich: Datenbank Bereinigung")
            st.markdown(
                "<span style='color: #ef4444; font-weight: bold;'>Achtung:</span> "
                "Diese Aktion löscht unwiderruflich sämtliche Daten in allen Haupttabellen (Anlagen, Verträge, Historie, Einsätze etc.). "
                "Das System wird komplett auf Werkszustand zurückgesetzt.", 
                unsafe_allow_html=True
            )
            
            confirm_checkbox = st.checkbox(
                "Ich bin mir sicher und möchte alle Datenbank-Tabellen vollständig leeren." if lang == "de" else "I am sure and want to empty all database tables completely."
            )
            
            confirm_pass = st.text_input(
                "Zur Bestätigung Admin-Passwort erneut eingeben:" if lang == "de" else "Re-enter Admin password to confirm:",
                type="password",
                key="reset_db_password_input"
            )
            
            if st.button("Alle Daten unwiderruflich löschen", type="primary"):
                if not confirm_checkbox:
                    st.error("Bitte bestätigen Sie die Sicherheits-Checkbox darüber." if lang == "de" else "Please check the confirmation box.")
                elif confirm_pass != admin_passwort:
                    st.error("Falsches Passwort zur Bestätigung." if lang == "de" else "Incorrect confirmation password.")
                else:
                    conn_reset = hole_datenbank_verbindung()
                    if conn_reset is not None:
                        cursor_reset = None
                        try:
                            cursor_reset = conn_reset.cursor()
                            cursor_reset.execute("SET FOREIGN_KEY_CHECKS = 0;")
                            
                            tabellen_zum_leeren = ["vertragsanalyse", "service", "auffaelligkeiten", "anlagen", "firmeninfo", "standort"]
                            for tab in tabellen_zum_leeren:
                                try:
                                    cursor_reset.execute(f"TRUNCATE TABLE `{tab}`")
                                except Exception:
                                    cursor_reset.execute(f"DELETE FROM `{tab}`")
                            
                            cursor_reset.execute("SET FOREIGN_KEY_CHECKS = 1;")
                            conn_reset.commit()
                            st.success("Erfolgreich: Alle Tabellen wurden vollständig geleert!" if lang == "de" else "Success: All tables have been cleared!")
                            st.rerun()
                        except Exception as reset_err:
                            st.error(f"Fehler beim Zurücksetzen der Datenbank: {reset_err}")
                        finally:
                            if cursor_reset:
                                cursor_reset.close()
                            if conn_reset.is_connected():
                                conn_reset.close()
                    else:
                        st.error("Keine Verbindung zur Datenbank für den Reset möglich.")