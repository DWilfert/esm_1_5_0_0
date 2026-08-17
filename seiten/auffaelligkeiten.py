import streamlit as st
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import prepare_display_dataframe, render_page_header, render_section_header, standort_code_from_display

def zeige_auffalligkeiten():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        div[data-testid="stDataFrame"] {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid rgba(128, 128, 128, 0.25) !important;
            border-radius: 0.5rem;
            padding: 4px;
        }
        .auffallig-card {
            background-color: var(--secondary-background-color);
            border: 1px solid var(--primary-color);
            border-radius: 8px;
            padding: 18px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            color: var(--text-color);
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

    if 'language' not in st.session_state:
        st.session_state.language = "de"

    if st.session_state.language == "de":
        TXT_AUF = {
            "title": "⚠️ Auffälligkeiten & Mängelmanagement",
            "desc": "Erfassung und Bearbeitung von technischen Mängeln, Fristüberschreitungen und Unstimmigkeiten aus MySQL.",
            "sec_uebersicht": "🔍 1. Aktuelle Auffälligkeiten aus Datenbank",
            "sec_loeschen": "🗑️ 2. Eintrag löschen",
            "lbl_id_loeschen": "Zu löschenden Eintrag wählen:",
            "btn_loeschen": "Aus MySQL löschen",
            "bitte_waehlen": "--- Bitte wählen ---",
            "erfolg_del": "Eintrag erfolgreich aus MySQL gelöscht!",
            "warnung_del": "Bitte wählen Sie zuerst einen gültigen Eintrag aus.",
            "kpi_total": "Gesamtauffälligkeiten",
            "kpi_sites": "Standorte",
            "kpi_critical": "Kritisch",
            "filter_location": "Standort filtern:",
            "opt_all": "Alle",
            "summary_title": "Executive Summary",
            "risk_col_loc": "Standort",
            "risk_col_count": "Anzahl",
            "risk_col_critical": "Kritisch"
        }
    else:
        TXT_AUF = {
            "title": "⚠️ Anomalies & Defect Management",
            "desc": "Recording and processing of technical defects and discrepancies from MySQL.",
            "sec_uebersicht": "🔍 1. Current Anomalies from Database",
            "sec_loeschen": "🗑️ 2. Delete Entry",
            "lbl_id_loeschen": "Select entry to delete:",
            "btn_loeschen": "Delete from MySQL",
            "bitte_waehlen": "--- Please select ---",
            "erfolg_del": "Entry successfully deleted from MySQL!",
            "warnung_del": "Please select a valid entry first.",
            "kpi_total": "Total anomalies",
            "kpi_sites": "Locations",
            "kpi_critical": "Critical",
            "filter_location": "Filter location:",
            "opt_all": "All",
            "summary_title": "Executive Summary",
            "risk_col_loc": "Location",
            "risk_col_count": "Count",
            "risk_col_critical": "Critical"
        }

    render_page_header(TXT_AUF['title'], TXT_AUF['desc'])

    conn = hole_datenbank_verbindung()
    df_auffalligkeiten = pd.DataFrame()
    if conn is not None:
        try:
            query = """
                SELECT 
                    auf.id AS 'ID',
                    anl.anlagenr AS 'Anlagen-Nr',
                    anl.anlagebezeichnung AS 'Anlagenbezeichnung',
                    auf.vertrag AS 'Vertrag / Datei',
                    auf.protokolldatei AS 'Protokolldatei',
                    auf.standort_text AS 'Standort (Excel)',
                    auf.kommentar AS 'Kommentar / Mangel'
                FROM auffaelligkeiten auf
                JOIN anlagen anl ON auf.anlage_id = anl.id
            """
            df_auffalligkeiten = pd.read_sql(query, conn)
        except Exception as e:
            st.error(f"Fehler beim Laden der Auffälligkeiten: {e}")
        finally:
            try:
                conn.close()
            except:
                pass

    if not df_auffalligkeiten.empty:
        df_auffalligkeiten = df_auffalligkeiten.copy()
        df_auffalligkeiten["Kommentar / Mangel"] = df_auffalligkeiten["Kommentar / Mangel"].fillna("")
        df_auffalligkeiten["_prioritaet"] = df_auffalligkeiten["Kommentar / Mangel"].astype(str).str.lower().apply(
            lambda text: "Hoch" if any(keyword in text for keyword in ["kritisch", "fehler", "defekt", "ausfall", "gefährlich", "warning", "critical", "fault", "failure"]) else "Mittel"
        )

        standorte = sorted(df_auffalligkeiten["Standort (Excel)"].dropna().astype(str).unique().tolist())
        if standorte:
            filter_selection_label = st.radio(
                TXT_AUF['filter_location'],
                [TXT_AUF['opt_all'], "Neuperlach (NP)", "Fasangarten (FG)"],
                horizontal=True,
                key='auffaelligkeiten_standort_filter_v7'
            )

            if filter_selection_label != TXT_AUF['opt_all']:
                filter_selection_code = standort_code_from_display(filter_selection_label)
                df_filtered = df_auffalligkeiten[df_auffalligkeiten["Standort (Excel)"].astype(str).str.upper().isin([filter_selection_code])].copy()
            else:
                df_filtered = df_auffalligkeiten.copy()
        else:
            df_filtered = df_auffalligkeiten.copy()

        total_auffaelligkeiten = len(df_filtered)
        total_standorte = df_filtered["Standort (Excel)"].nunique()
        total_kritisch = (df_filtered["_prioritaet"] == "Hoch").sum()

        kpi_total, kpi_sites, kpi_critical = st.columns(3)
        with kpi_total:
            st.metric(TXT_AUF['kpi_total'], total_auffaelligkeiten)
        with kpi_sites:
            st.metric(TXT_AUF['kpi_sites'], total_standorte)
        with kpi_critical:
            st.metric(TXT_AUF['kpi_critical'], total_kritisch)

        st.write("")
        risk_df = df_filtered.groupby('Standort (Excel)', as_index=False).agg(
            anzahl=('ID', 'count'),
            kritisch=('_prioritaet', lambda s: (s == 'Hoch').sum())
        )
        risk_df = risk_df.sort_values(['kritisch', 'anzahl'], ascending=[False, False])

        st.markdown(f"#### {TXT_AUF['summary_title']}")
        st.dataframe(
            prepare_display_dataframe(risk_df.rename(columns={
                'Standort (Excel)': TXT_AUF['risk_col_loc'],
                'anzahl': TXT_AUF['risk_col_count'],
                'kritisch': TXT_AUF['risk_col_critical']
            })),
            use_container_width=True,
            hide_index=True
        )
        st.write("")

    with st.container(border=True):
        render_section_header(TXT_AUF['sec_uebersicht'])
        
        if not df_auffalligkeiten.empty:
            anzeige_df = df_auffalligkeiten.drop(columns=["ID", "_prioritaet"])
            st.dataframe(prepare_display_dataframe(anzeige_df), use_container_width=True, hide_index=True)
        else:
            st.info("Keine Einträge in der Tabelle 'auffaelligkeiten' gefunden." if st.session_state.language == "de" else "No entries found in table 'auffaelligkeiten'.")

    st.write("")

    if not df_auffalligkeiten.empty:
        with st.container(border=True):
            st.markdown(f"**{TXT_AUF['sec_loeschen']}**")
            st.markdown("<hr style='border: none; height: 1px; background-color: rgba(128, 128, 128, 0.3); margin: 10px 0;'>", unsafe_allow_html=True)
            
            col_id_sel, col_btn_del, col_space = st.columns([4.0, 2.5, 3.5])
            
            mapping = {
                row["ID"]: f"{row['Anlagenbezeichnung']} - {str(row['Kommentar / Mangel'])[:40]}..."
                for _, row in df_auffalligkeiten.iterrows()
            }
            id_optionen = [None] + list(mapping.keys())
            
            with col_id_sel:
                ausgewaehlte_id = st.selectbox(
                    TXT_AUF["lbl_id_loeschen"],
                    options=id_optionen,
                    format_func=lambda x: TXT_AUF["bitte_waehlen"] if x is None else mapping[x],
                    key="auffallig_loesch_id"
                )
                
            with col_btn_del:
                st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True) 
                if st.button(TXT_AUF["btn_loeschen"], key="btn_auffallig_loeschen", use_container_width=True):
                    if ausgewaehlte_id:
                        conn_del = hole_datenbank_verbindung()
                        if conn_del:
                            cursor = None
                            try:
                                cursor = conn_del.cursor()
                                cursor.execute("DELETE FROM auffaelligkeiten WHERE id = %s", (int(ausgewaehlte_id),))
                                conn_del.commit()
                                st.success(TXT_AUF["erfolg_del"])
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler beim Löschen: {e}")
                            finally:
                                if cursor:
                                    try:
                                        cursor.close()
                                    except:
                                        pass
                                try:
                                    conn_del.close()
                                except:
                                    pass
                    else:
                        st.warning(TXT_AUF["warnung_del"])