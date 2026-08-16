import streamlit as st
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import render_page_header, render_section_header

def zeige_adminbereich():
    admin_passwort = "esm"
    
    st.markdown("""
        <style>
        .ent-subheader { font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px; margin-top: 10px; }
        .custom-huge-title {
            font-size: 2.8rem !important;
            font-weight: 500 !important;
            letter-spacing: -0.5px !important;
            margin-bottom: 0px !important;
            line-height: 1.1 !important;
            white-space: nowrap !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    col_p1, col_p2, col_p3 = st.columns([3.0, 4.0, 3.0])
    with col_p1:
        eingabe_passwort = st.text_input(
            "Bitte Admin-Passwort eingeben (Demo: 'esm'):" if st.session_state.get("language", "de") == "de" else "Please enter Admin password:",
            type="password"
        )
    
    if eingabe_passwort != admin_passwort:
        if eingabe_passwort != "":
            st.error("Falsches Passwort! (Tipp: esm)" if st.session_state.get("language", "de") == "de" else "Incorrect password!")
        st.stop()
    
    lang = st.session_state.get("language", "de")
    
    txt = {
        "de": {
            "titel": "Admin-Bereich & Systemkonfiguration (Demo)",
            "untertitel": "Zentrale Steuerung im Demo-Modus aktiv.",
            "tab1": "System- & Serverparameter",
            "tab2": "Datenbank-Status",
            "sekt_titel": "Technische Umgebungsparameter",
            "host_label": "MySQL Server-Host (Simuliert):",
            "user_label": "Datenbank-Benutzername:",
            "schema_label": "Datenbank-Schema:",
            "pass_label": "MySQL-Passwort:",
            "port_label": "Port:",
            "pfad_label": "Zentraler Ablagepfad:",
            "btn_speichern": "Konfiguration speichern",
            "success_msg": "Konfiguration im Demo-Modus gespeichert!",
            "db_status_titel": "Datenbank-Integritätsprüfung (Demo-Modus)",
            "db_check_btn": "Demo-Tabellen-Status abrufen",
            "tabelle": "Tabelle",
            "status": "Status",
            "eintraege": "Anzahl Datensätze"
        },
        "en": {
            "titel": "Admin Area & System Configuration (Demo)",
            "untertitel": "Central control active in Demo mode.",
            "tab1": "System & Server Parameters",
            "tab2": "Database Status",
            "sekt_titel": "Technical Environment Parameters",
            "host_label": "MySQL Server Host (Simulated):",
            "user_label": "Database Username:",
            "schema_label": "Database Schema:",
            "pass_label": "MySQL Password:",
            "port_label": "Port:",
            "pfad_label": "Central Storage Path:",
            "btn_speichern": "Save Configuration",
            "success_msg": "Configuration saved in Demo mode!",
            "db_status_titel": "Database Integrity Check (Demo Mode)",
            "db_check_btn": "Fetch Demo Table Status",
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
            st.text_input(txt["host_label"], value="localhost (Demo)")
            st.text_input(txt["user_label"], value="root")
        with col2:
            st.text_input(txt["schema_label"], value="demo_db")
            st.text_input(txt["pass_label"], type="password", value="***")
        with col3:
            st.text_input(txt["port_label"], value="3306")

        st.text_input(txt["pfad_label"], value="C:/esm_dokumente")
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button(txt["btn_speichern"], type="primary"):
            st.success(txt["success_msg"])

    with tab_db:
        render_section_header(txt['db_status_titel'])
        
        if st.button(txt["db_check_btn"]):
            tabellen_liste = ["anlagen", "vertragsanalyse", "service", "auffaelligkeiten", "firmeninfo", "standort"]
            ergebnis_daten = []
            
            for tab in tabellen_liste:
                ergebnis_daten.append({
                    txt["tabelle"]: tab,
                    txt["status"]: "Online (Demo-Aktiv)",
                    txt["eintraege"]: 3
                })
            
            df_status = pd.DataFrame(ergebnis_daten)
            st.dataframe(df_status, use_container_width=True, hide_index=True)
        else:
            st.info("Klicken Sie auf den Button, um den Status der Demo-Tabellen abzurufen." if lang == "de" else "Click the button to fetch demo table status.")

        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            render_section_header("Gefahrenbereich: Bereinigung (Demo)")
            st.markdown(
                "<span style='color: #ef4444; font-weight: bold;'>Hinweis:</span> "
                "Im Demo-Modus werden hierbei lediglich die temporären In-Memory-Testdaten zurückgesetzt.", 
                unsafe_allow_html=True
            )
            if st.button("Demo-Daten zurücksetzen", type="primary"):
                st.success("✅ Demo-Daten erfolgreich auf Werkszustand zurückgesetzt!")
                st.rerun()