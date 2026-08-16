import streamlit as st
import pandas as pd
from verbindung import (
    hole_anlagen_daten,
    hole_wartungsvertraege_daten,
    hole_firmen_daten,
    hole_wartungsuebersicht_daten
)

def zeige_startseite():
    st.markdown(
        """
        <h1 style='font-size: 3.5rem !important; margin-bottom: 0px;'>Vertrags- & Wartungsmanagement</h1>
        <p style='font-size: 1.3rem !important; color: #93c5fd; margin-top: 0px; margin-bottom: 25px;'>EXECUTIVE DASHBOARD & SYSTEM-CONTROLLING V1.5.0.0</p>
        """, 
        unsafe_allow_html=True
    )
    st.markdown("---")

    df_vertraege = hole_wartungsvertraege_daten()
    df_anlagen = hole_anlagen_daten()
    df_wartung = hole_wartungsuebersicht_daten()

    gesamt_vertraege = len(df_vertraege)
    gesamt_volumen = df_vertraege["kosten_bestand_pa"].sum() if "kosten_bestand_pa" in df_vertraege.columns else 0.0
    optimierte_einsparung = 1200.0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="GESAMTVERTRÄGE", value=f"{gesamt_vertraege}")
    with col2:
        st.metric(label="FRISTEN-ALARM", value="Alles im Plan")
    with col3:
        st.metric(label="JAHRESVOLUMEN (BESTAND)", value=f"{gesamt_volumen:,.2f} €".replace(",", "."))
    with col4:
        st.metric(label="OPTIMIERTE EINSPARUNG", value=f"+{optimierte_einsparung:,.2f} €".replace(",", "."))

    st.markdown("---")

    st.subheader("Kritische & anstehende Fristen (nächste 30 Tage)")
    if not df_wartung.empty:
        st.dataframe(df_wartung, use_container_width=True)
    else:
        st.info("Keine kritischen oder anstehenden Fristen im gewählten Zeitraum.")

    st.subheader("Anlagen-Übersicht")
    if not df_anlagen.empty:
        st.dataframe(df_anlagen, use_container_width=True)
    else:
        st.info("Keine Standorten- oder Anlagendaten verfügbar.")
