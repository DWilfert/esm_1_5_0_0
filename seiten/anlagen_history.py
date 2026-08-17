import streamlit as st
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import render_page_header

def zeige_anlagen_history():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
        div.stSelectbox {
            max-width: 50% !important;
        }
        div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
            background-color: var(--secondary-background-color) !important;
        }
        div[data-baseweb="popover"] ul li, 
        ul[data-baseweb="menu"] li,
        li[role="option"] {
            background-color: var(--secondary-background-color) !important;
            color: var(--text-color) !important;
            font-size: 0.85rem !important;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.25) !important;
            border-radius: 0.5rem;
            padding: 4px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px; background-color: transparent; border-bottom: 1px solid rgba(148, 163, 184, 0.2); padding-bottom: 0; margin-bottom: 25px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px; white-space: break-spaces; background-color: transparent; border-radius: 0; color: #64748b; font-size: 13px;
            font-weight: 500; text-transform: uppercase; letter-spacing: 1px; border: none !important; border-bottom: 2px solid transparent !important;
        }
        .stTabs [aria-selected="true"] { color: #0ea5e9 !important; border-bottom: 2px solid #0ea5e9 !important; }
        
        </style>
    """, unsafe_allow_html=True)

    lang = st.session_state.get("language", "de")
    
    txt = {
        "de": {
            "titel": "360° Anlagen-Ansicht",
            "untertitel": "Chronologische Ansicht: Alle Stammdaten, Verträge, Historien und Prüfberichte im Überblick.",
            "label_dropdown": "Anlage auswählen (Alphabetisch):",
            "tab1": "Stammdaten",
            "tab2": "Verträge",
            "tab3": "Historie",
            "tab4": "Prüfberichte",
            "info_text": "Bitte wähle oben eine Anlage aus, um die vollständige 360°-Chronik anzuzeigen.",
            "geladen": "Ausgewählte Anlage geladen: **{anlage}**",
            "db_fehler": "Fehler beim Laden der Anlagendaten aus der Datenbank.",
            "bitte_waehlen": "--- Bitte wählen ---",
            "keine_details": "Keine Details gefunden.",
            "fehler_stammdaten": "Fehler beim Laden der Stammdaten.",
            "keine_vertraege": "Keine Verträge zu dieser Anlage hinterlegt.",
            "keine_historie": "Keine Historie vorhanden.",
            "keine_pruef": "Keine Prüfberichte vorhanden."
        },
        "en": {
            "titel": "360° Asset View",
            "untertitel": "Chronological view: All master data, contracts, histories, and inspection reports at a glance.",
            "label_dropdown": "Select Asset (Alphabetical):",
            "tab1": "Master Data",
            "tab2": "Contracts",
            "tab3": "History",
            "tab4": "Inspection Reports",
            "info_text": "Please select an asset above to display the complete 360° chronicle.",
            "geladen": "Selected asset loaded: **{anlage}**",
            "db_fehler": "Error loading asset data from the database.",
            "bitte_waehlen": "--- Please select ---",
            "keine_details": "No details found.",
            "fehler_stammdaten": "Error loading master data.",
            "keine_vertraege": "No contracts found for this asset.",
            "keine_historie": "No history available.",
            "keine_pruef": "No inspection reports available."
        }
    }[lang]

    render_page_header(txt['titel'], txt['untertitel'])

    conn = hole_datenbank_verbindung()
    df_history_anlagen = pd.DataFrame()
    if conn is not None:
        try:
            df_history_anlagen = pd.read_sql("SELECT id, anlagebezeichnung, anlagenr FROM anlagen ORDER BY anlagebezeichnung ASC", conn)
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except:
                pass

    if df_history_anlagen.empty:
        st.warning(txt["db_fehler"])
        return

    anlagen_mapping = {
        row["id"]: f"{row['anlagebezeichnung']} (Nr: {row['anlagenr']})" if pd.notna(row['anlagenr']) else str(row['anlagebezeichnung'])
        for _, row in df_history_anlagen.iterrows()
    }
    
    ausgewaehlte_id = st.selectbox(
        txt["label_dropdown"],
        options=[None] + list(anlagen_mapping.keys()),
        format_func=lambda x: txt["bitte_waehlen"] if x is None else anlagen_mapping[x],
        key="hist_anl_dropdown"
    )

    if ausgewaehlte_id is not None:
        st.markdown("---")
        st.success(txt["geladen"].format(anlage=anlagen_mapping[ausgewaehlte_id]))
        
        t_stammdaten, t_vertraege, t_historie, t_pruefungen = st.tabs([
            txt["tab1"], txt["tab2"], txt["tab3"], txt["tab4"]
        ])
        
        with t_stammdaten:
            conn_det = hole_datenbank_verbindung()
            if conn_det:
                try:
                    df_det = pd.read_sql(
                        "SELECT anlagenr AS 'Anlagen-Nr', anlagebezeichnung AS 'Bezeichnung', anlagetyp AS 'Typ', hersteller AS 'Hersteller', typ AS 'Modell', seriennummer AS 'Seriennummer', zustand AS 'Zustand', standort_text AS 'Standort', beschreibung AS 'Beschreibung' FROM anlagen WHERE id = ?",
                        conn_det,
                        params=(ausgewaehlte_id,),
                    )
                    if not df_det.empty:
                        st.dataframe(df_det.T, use_container_width=True)
                    else:
                        st.info(txt["keine_details"])
                except Exception:
                    st.info(txt["fehler_stammdaten"])
                finally:
                    try:
                        conn_det.close()
                    except:
                        pass
                    
        with t_vertraege:
            conn_v = hole_datenbank_verbindung()
            if conn_v:
                try:
                    df_v = pd.read_sql(
                        "SELECT vertragsname AS 'Vertragsname', vertragsart AS 'Art', firmenname AS 'Firma', laufzeit_bis AS 'Laufzeit bis', kosten_bestand_pa AS 'Kosten p.a.', naechste_wartung AS 'Nächste Wartung' FROM vertragsanalyse WHERE anlage_id = ? ORDER BY naechste_wartung ASC",
                        conn_v,
                        params=(ausgewaehlte_id,),
                    )
                    if not df_v.empty:
                        st.dataframe(df_v, use_container_width=True, hide_index=True)
                    else:
                        st.info(txt["keine_vertraege"])
                except Exception:
                    st.info(txt["keine_vertraege"])
                finally:
                    try:
                        conn_v.close()
                    except:
                        pass
                        
        with t_historie:
            conn_h = hole_datenbank_verbindung()
            if conn_h:
                try:
                    df_h = pd.read_sql(
                        "SELECT vertrag AS 'Vertrag', standort_text AS 'Standort', kommentar AS 'Kommentar' FROM auffaelligkeiten WHERE anlage_id = ? ORDER BY id ASC",
                        conn_h,
                        params=(ausgewaehlte_id,),
                    )
                    if not df_h.empty:
                        st.dataframe(df_h, use_container_width=True, hide_index=True)
                    else:
                        st.info(txt["keine_historie"])
                except Exception:
                    st.info(txt["keine_historie"])
                finally:
                    try:
                        conn_h.close()
                    except:
                        pass
                        
        with t_pruefungen:
            conn_p = hole_datenbank_verbindung()
            if conn_p:
                try:
                    df_p = pd.read_sql(
                        "SELECT anlagenklasse AS 'Anlagenklasse', kurzfassung AS 'Kurzfassung', intervall AS 'Intervall', qualifikation AS 'Qualifikation' FROM service WHERE anlage_id = ? ORDER BY id ASC",
                        conn_p,
                        params=(ausgewaehlte_id,),
                    )
                    if not df_p.empty:
                        st.dataframe(df_p, use_container_width=True, hide_index=True)
                    else:
                        st.info(txt["keine_pruef"])
                except Exception:
                    st.info(txt["keine_pruef"])
                finally:
                    try:
                        conn_p.close()
                    except:
                        pass
    else:
        st.info(txt["info_text"])