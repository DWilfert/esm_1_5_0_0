import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import render_page_header, render_section_header

def zeige_import_export():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label, .stRadio div {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        .kpi-card {
            background-color: rgba(128, 128, 128, 0.05);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 0.5rem;
            padding: 12px 15px;
            text-align: center;
        }
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

    if 'language' not in st.session_state:
        st.session_state.language = "de"

    if st.session_state.language == "de":
        TXT_IE = {
            "title": "Daten-Schnittstelle (Excel Hub)",
            "desc": "Zentrale Steuerungseinheit für den sicheren Excel-Datentransfer (Demo-Modus aktiv).",
            "direction_lbl": "Schnittstellen-Richtung wählen:",
            "dir_exp": "Daten exportieren (Backup)", 
            "dir_imp": "Daten importieren (Upload)",
            "exp_title": "Tabellenauswahl für den Excel-Export",
            "exp_q": "Welche Tabelle möchtest du exportieren?", 
            "err_conn": "Keine Verbindung zur Datenbank.",
            "exp_success": "Datensätze aus '{}' erfolgreich bereitgestellt.",
            "exp_empty": "Die Tabelle '{}' enthält aktuell keine Daten.", 
            "err_exp": "Fehler beim Exportieren:",
            "kpi_1": "System-Status",
            "status_ok": "Online (Demo-Modus aktiv)",
            "template_title": "Interaktiver Vorlagen-Generator",
            "template_desc": "Wählen Sie eine Tabelle aus, um das exakte Excel-Template herunterzuladen.",
            "template_sel": "Tabellenauswahl:",
            "log_title": "Schnittstellen-Protokoll (Audit-Trail)",
            "dl_tmpl_btn": "Ausgewählte Vorlage herunterladen"
        }
    else:
        TXT_IE = {
            "title": "Data Interface (Excel Hub)",
            "desc": "Central control unit for secure Excel data transfers (Demo mode active).",
            "direction_lbl": "Select Interface Direction:",
            "dir_exp": "Export Data (Backup)", 
            "dir_imp": "Import Data (Upload)",
            "exp_title": "Table Selection for Excel Export",
            "exp_q": "Which table do you want to export?", 
            "err_conn": "No database connection.",
            "exp_success": "Records from '{}' successfully provided.",
            "exp_empty": "The table '{}' currently contains no data.", 
            "err_exp": "Error during export:",
            "kpi_1": "System Status",
            "status_ok": "Online (Demo mode active)",
            "template_title": "Interactive Template Generator",
            "template_desc": "Select a table to download the exact Excel template.",
            "template_sel": "Table Selection:",
            "log_title": "Interface Log (Audit Trail)",
            "dl_tmpl_btn": "Download Selected Template"
        }

    render_page_header(TXT_IE['title'], TXT_IE['desc'])

    col_k1, _ = st.columns([2.0, 8.0])
    with col_k1:
        st.markdown(f"""<div class="kpi-card"><div style="font-size: 11px; opacity: 0.7;">{TXT_IE['kpi_1']}</div><div style="font-size: 14px; font-weight: bold; color: #10b981;">{TXT_IE['status_ok']}</div></div>""", unsafe_allow_html=True)

    st.write("")

    col_dir_lbl, col_dir_val = st.columns([2.5, 7.5])
    with col_dir_lbl:
        st.markdown(f"<div style='font-size: 13px; font-weight: 600; padding-top: 6px;'>{TXT_IE['direction_lbl']}</div>", unsafe_allow_html=True)
    with col_dir_val:
        ie_aktion = st.radio("", [TXT_IE["dir_exp"], TXT_IE["dir_imp"]], horizontal=True, key="ie_haupt_aktion_final_v7", label_visibility="collapsed")

    st.write("")

    tabellen_liste = {
        "Anlagen-Stammdaten": "anlagen",
        "Vertragsanalyse": "vertragsanalyse",
        "Service-Prüfungen": "service",
        "Auffälligkeiten & Mängel": "auffaelligkeiten",
        "Firmen & Dienstleister": "firmeninfo"
    }

    col_main_left, col_main_right = st.columns([6.0, 4.0])
    with col_main_left:
        with st.container(border=True):
            if ie_aktion == TXT_IE["dir_exp"]:
                render_section_header(TXT_IE['exp_title'])
                col_exp_sel, _ = st.columns([6.0, 4.0])
                with col_exp_sel:
                    export_wahl = st.selectbox(TXT_IE["exp_q"], [""] + list(tabellen_liste.keys()), key="export_bereich_wahl_final_v7")
                
                if export_wahl:
                    db_tabelle = tabellen_liste[export_wahl]
                    conn = hole_datenbank_verbindung()
                    if conn is not None:
                        try:
                            # Sichere Abfrage via pandas und Mock-Connection
                            if db_tabelle == "anlagen":
                                from datenbank.befehle import hole_anlagen_daten
                                df_exp = hole_anlagen_daten()
                            elif db_tabelle == "vertragsanalyse":
                                from datenbank.befehle import hole_wartungsvertraege_daten
                                df_exp = hole_wartungsvertraege_daten()
                            elif db_tabelle == "firmeninfo":
                                from datenbank.befehle import hole_firmen_daten
                                df_exp = hole_firmen_daten()
                            else:
                                df_exp = pd.DataFrame({"Hinweis": ["Demo-Daten für " + db_tabelle]})

                            if not df_exp.empty:
                                df_exp_bereinigt = df_exp.drop(columns=["id", "ID"], errors="ignore")
                                st.success(f"{len(df_exp_bereinigt)} {TXT_IE['exp_success'].format(export_wahl)}")
                                output_ie = io.BytesIO()
                                with pd.ExcelWriter(output_ie, engine='xlsxwriter') as writer:
                                    df_exp_bereinigt.to_excel(writer, index=False, sheet_name=export_wahl[:30])
                                excel_ie_data = output_ie.getvalue()
                                dateiname = f"ESM_Backup_{db_tabelle}_{datetime.now().strftime('%Y%m%d')}.xlsx"
                                
                                st.download_button(label=f"'{export_wahl}' als Excel herunterladen", data=excel_ie_data, file_name=dateiname, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key="export_download_btn_final_v7")
                            else: 
                                st.info(TXT_IE["exp_empty"].format(export_wahl))
                        except Exception as e: 
                            st.error(f"{TXT_IE['err_exp']} {str(e)}")
                        finally: 
                            try:
                                conn.close()
                            except:
                                pass
                    else: 
                        st.error(TXT_IE["err_conn"])

            elif ie_aktion == TXT_IE["dir_imp"]:
                TXT_IMP = {
                    "de": {
                        "imp_title": "Excel-Daten einlesen (Demo-Modus)",
                        "imp_q": "Ziel-Tabelle für Import:",
                        "imp_hint": "Hinweis: Im Demo-Modus werden Uploads simuliert.",
                        "imp_file_lbl": "Excel-Datei für '{}' auswählen:"
                    },
                    "en": {
                        "imp_title": "Read Excel Data (Demo Mode)",
                        "imp_q": "Target Table for Import:",
                        "imp_hint": "Note: Uploads are simulated in Demo mode.",
                        "imp_file_lbl": "Select Excel file for '{}':"
                    }
                }[st.session_state.language]
                    
                render_section_header(TXT_IMP['imp_title'])
                col_imp_sel, _ = st.columns([6.0, 4.0])
                with col_imp_sel:
                    import_wahl = st.selectbox(TXT_IMP["imp_q"], [""] + list(tabellen_liste.keys()), key="import_bereich_wahl_final_v7")

                if import_wahl:
                    st.write("")
                    st.info(TXT_IMP["imp_hint"])
                    uploaded_file = st.file_uploader(TXT_IMP["imp_file_lbl"].format(import_wahl), type=["xlsx"], key="excel_uploader_field_v7")
                    
                    if uploaded_file is not None:
                        st.success("✅ [Demo-Modus] Datei erfolgreich eingelesen und simuliert!")

    with col_main_right:
        with st.container(border=True):
            render_section_header(TXT_IE['template_title'])
            st.markdown(f"<p style='font-size: 11px; opacity: 0.7; margin-bottom: 12px;'>{TXT_IE['template_desc']}</p>", unsafe_allow_html=True)
            
            col_t1, col_t2 = st.columns([3.5, 6.5])
            with col_t1:
                st.markdown(f"<div style='font-size: 13px; font-weight: 600; padding-top: 8px;'>{TXT_IE['template_sel']}</div>", unsafe_allow_html=True)
            with col_t2:
                template_wahl = st.selectbox("Template Auswahl", [""] + list(tabellen_liste.keys()), key="interaktives_template_selectbox", label_visibility="collapsed")
            
            if template_wahl:
                t_key = tabellen_liste[template_wahl]
                out_t = io.BytesIO()
                df_dummy = pd.DataFrame({"Spalte1": ["Beispielwert"]})
                with pd.ExcelWriter(out_t, engine='xlsxwriter') as w:
                    df_dummy.to_excel(w, index=False, sheet_name="Vorlage")
                
                st.write("")
                st.download_button(
                    label=TXT_IE["dl_tmpl_btn"],
                    data=out_t.getvalue(),
                    file_name=f"ESM_Vorlage_{t_key}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key=f"dl_hub_tpl_{t_key}_interactive",
                    use_container_width=True
                )

    st.divider()
    render_section_header(TXT_IE['log_title'])
    st.info("Schnittstellen-Protokoll aktiv (Demo-Modus)." if st.session_state.language == "de" else "Audit trail active (Demo mode).")