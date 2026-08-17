import streamlit as st
import pandas as pd
from datetime import datetime
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import prepare_display_dataframe, render_page_header, render_section_header

def zeige_wartungsanalyse():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label, .stRadio div {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        .kpi-box {
            background-color: rgba(128, 128, 128, 0.02);
            border: 1px solid rgba(128, 128, 128, 0.1);
            border-radius: 4px;
            padding: 15px;
            text-align: center;
        }
        .micro-dot {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 6px;
        }
        .dot-red { background-color: #ef4444; }
        .dot-yellow { background-color: #f59e0b; }
        .dot-green { background-color: #10b981; }
        
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

    if 'language' not in st.session_state:
        st.session_state.language = "de"

    lang = st.session_state.language

    if lang == "de":
        TXT_WA = {
            "title": "Wartungsübersicht & Fristen-Monitoring",
            "desc": "Auswertung anstehender und überfälliger Wartungstermine",
            "tab1": "Überfällige Wartungen",
            "tab2": "Anstehende Wartungen (30 Tage)",
            "tab3": "In Ordnung",
            "empty": "Keine Wartungsverträge gefunden.",
            "ueb_header": "Überfällige Verträge – 1-Wochen-Schritte",
            "ueb_hint": "Hinweis: Jeder Klick auf den +1W Button verschiebt den Termin um exakt 7 Tage.",
            "location_lbl": "Standort:",
            "term_lbl": "Termin:",
            "btn_1w_help": "Termin um 1 Woche verlängern",
            "succ_moved": "um 1 Woche verschoben!",
            "err_msg": "Fehler:",
            "succ_none": "Keine überfälligen Wartungen.",
            "info_ans": "Keine anstehenden Wartungen.",
            "info_ok": "Keine Einträge in dieser Kategorie."
        }
    else:
        TXT_WA = {
            "title": "Maintenance Overview & Deadline Monitoring",
            "desc": "Evaluation of pending and overdue maintenance dates",
            "tab1": "Overdue Maintenance",
            "tab2": "Upcoming Maintenance (30 Days)",
            "tab3": "Up to Date",
            "empty": "No maintenance contracts found.",
            "ueb_header": "Overdue Contracts – 1-Week Steps",
            "ueb_hint": "Note: Each click on +1W shifts the date by exactly 7 days.",
            "location_lbl": "Location:",
            "term_lbl": "Date:",
            "btn_1w_help": "Extend appointment by 1 week",
            "succ_moved": "shifted by 1 week!",
            "err_msg": "Error:",
            "succ_none": "No overdue maintenance.",
            "info_ans": "No upcoming maintenance.",
            "info_ok": "No entries in this category."
        }

    render_page_header(TXT_WA['title'], TXT_WA['desc'])

    conn = hole_datenbank_verbindung()
    df_wartung = pd.DataFrame()
    if conn is not None:
        try:
            df_wartung = pd.read_sql("SELECT * FROM wartungsuebersicht", conn)
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except:
                pass

    if not df_wartung.empty:
        df_wartung = df_wartung.loc[:, ~df_wartung.columns.duplicated()].copy()

        if 'naechste_wartung' not in df_wartung.columns:
            if 'laufzeit_bis' in df_wartung.columns:
                df_wartung['naechste_wartung'] = df_wartung['laufzeit_bis']
            elif 'datum' in df_wartung.columns:
                df_wartung['naechste_wartung'] = df_wartung['datum']
            else:
                df_wartung['naechste_wartung'] = pd.NaT
        if 'standort' not in df_wartung.columns and 'standort_text' in df_wartung.columns:
            df_wartung['standort'] = df_wartung['standort_text']
        if 'anlagebezeichnung' not in df_wartung.columns and 'anlage' in df_wartung.columns:
            df_wartung['anlagebezeichnung'] = df_wartung['anlage']

        df_wartung['naechste_wartung'] = pd.to_datetime(df_wartung['naechste_wartung'], errors='coerce')
        df_wartung = df_wartung.dropna(subset=['naechste_wartung'])

        heute = pd.Timestamp(datetime.now().date())
        
        df_ueb = df_wartung[df_wartung['naechste_wartung'] < heute].copy()
        df_ans = df_wartung[(df_wartung['naechste_wartung'] >= heute) & (df_wartung['naechste_wartung'] <= heute + pd.Timedelta(days=30))].copy()
        df_ok = df_wartung[df_wartung['naechste_wartung'] > heute + pd.Timedelta(days=30)].copy()

        for df in [df_ueb, df_ans, df_ok]:
            df['anzeige_termin'] = df['naechste_wartung'].dt.strftime('%d.%m.%Y')

        t1, t2, t3 = st.tabs([
            f"{TXT_WA['tab1']} ({len(df_ueb)})",
            f"{TXT_WA['tab2']} ({len(df_ans)})",
            f"{TXT_WA['tab3']} ({len(df_ok)})"
        ])

        with t1:
            if not df_ueb.empty:
                render_section_header(f"<span class='micro-dot dot-red'></span>{TXT_WA['ueb_header']}")
                st.markdown(f"<div style='font-size: 11px; opacity: 0.6; margin-bottom: 12px;'>{TXT_WA['ueb_hint']}</div>", unsafe_allow_html=True)
                
                for _, row in df_ueb.iterrows():
                    v_id = row["id"]
                    firma = row.get("firma", "-")
                    bezeichnung = row.get("anlagebezeichnung", row.get("anlagenname", "-"))
                    vertrag = row.get("vertragsname", "-")
                    standort = row.get("standort", "-")
                    anzeige_termin = row["anzeige_termin"]
                    
                    with st.container(border=True):
                        col_details, col_btn = st.columns([5, 1])
                        with col_details:
                            st.markdown(
                                f"<div style='font-size: 11.5px; line-height: 1.4;'>"
                                f"<b>{firma}</b> &nbsp;|&nbsp; <b>{vertrag}</b> &nbsp;|&nbsp; {bezeichnung} "
                                f"&nbsp;|&nbsp; <span style='opacity: 0.7;'>{TXT_WA['location_lbl']}</span> <b>{standort}</b> "
                                f"&nbsp;|&nbsp; <span style='color: #ef4444;'><b>{TXT_WA['term_lbl']} {anzeige_termin}</b></span>"
                                f"</div>",
                                unsafe_allow_html=True
                            )
                        with col_btn:
                            if st.button("➕ 1W", key=f"btn_plus_1w_{v_id}", use_container_width=True, help=TXT_WA["btn_1w_help"]):
                                c_up = hole_datenbank_verbindung()
                                if c_up is not None:
                                    try:
                                        neues_datum = row["naechste_wartung"] + pd.Timedelta(days=7)
                                        cur = c_up.cursor()
                                        cur.execute(
                                            "UPDATE vertragsanalyse SET naechste_wartung = %s WHERE id = %s",
                                            (neues_datum.date(), v_id)
                                        )
                                        c_up.commit()
                                        cur.close()
                                        c_up.close()
                                        st.success(f"Vertrag '{vertrag}' {TXT_WA['succ_moved']}")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"{TXT_WA['err_msg']} {e}")
            else:
                st.success(TXT_WA["succ_none"])

        with t2:
            if not df_ans.empty:
                st.markdown("<span class='micro-dot dot-yellow'></span>", unsafe_allow_html=True)
                anzeige_df = df_ans.drop(columns=["naechste_wartung", "id", "anlage_id", "anlagen_nr"], errors="ignore").rename(columns={"anzeige_termin": "Nächste Wartung"})
                st.dataframe(prepare_display_dataframe(anzeige_df), use_container_width=True, hide_index=True)
            else:
                st.info(TXT_WA["info_ans"])

        with t3:
            if not df_ok.empty:
                st.markdown("<span class='micro-dot dot-green'></span>", unsafe_allow_html=True)
                anzeige_df = df_ok.drop(columns=["naechste_wartung", "id", "anlage_id", "anlagen_nr"], errors="ignore").rename(columns={"anzeige_termin": "Nächste Wartung"})
                st.dataframe(prepare_display_dataframe(anzeige_df), use_container_width=True, hide_index=True)
            else:
                st.info(TXT_WA["info_ok"])
    else:
        st.info(TXT_WA["empty"])