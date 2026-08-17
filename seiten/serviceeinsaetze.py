import streamlit as st
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import prepare_display_dataframe, render_page_header, standort_code_from_display, standort_display_name

def zeige_serviceeinsaetze():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label, .stRadio div {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        
        .ent-subheader { font-size: 11px; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; padding-bottom: 8px; border-bottom: 1px solid rgba(148, 163, 184, 0.2); }
        
        .service-card {
            background: rgba(148, 163, 184, 0.02);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.2s ease;
        }
        .service-card:hover {
            border-color: #0ea5e9;
            box-shadow: 0 4px 12px rgba(14, 165, 233, 0.08);
        }
        .micro-dot {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-green { background-color: #10b981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.5); }
        
        .meta-label {
            font-size: 10px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 2px;
        }
        .meta-val {
            font-size: 13px;
            font-weight: 500;
            color: var(--text-color);
        }
        
        </style>
    """, unsafe_allow_html=True)

    if 'language' not in st.session_state:
        st.session_state.language = "de"

    if st.session_state.language == "de":
        TXT_SRV = {
            "title": "Service", "act_lbl": "Aktion:", "act_hist": "Historie / Suche", "act_add": "Bericht erfassen",
            "filter_lbl": "Standort filtern:", "opt_all": "Alle", "src_lbl": "Schnell-Suche (Echtzeit):",
            "src_ph": "Gewerk, Kurzbericht...", "empty_table": "Keine Einträge entsprechen deinen Filter-Kriterien.",
            "empty_db": "Keine Serviceberichte in der MySQL-Tabelle 'service' vorhanden.", "sel_id": "Service-Datensatz für Detailansicht wählen:",
            "det_title": "Details zu Serviceeinsatz", "gewerk": "Gewerbeklassifizierung:",
            "kurz": "Kurzfassung / Ergebnis:", "zyklus": "Intervall:", "hinweis": "Hinweis:", "btn_del": "Diesen Bericht aus MySQL löschen", "succ_del": "Bericht erfolgreich gelöscht.",
            "loc_lbl": "Standort", "lbl_anlage_wahl": "Anlage auswählen *", "class_lbl": "Klasse", "asset_type_lbl": "Anlagenart",
            "kenn1_lbl": "Kennzeichnung 1", "kenn2_lbl": "Kennzeichnung 2", "class_desc_lbl": "Bezeichnung Klasse",
            "summary_res_lbl": "Kurzfassung / Ergebnis", "equipment_lbl": "Benötigtes Ersatzequipment",
            "interval_lbl": "Intervall", "note_lbl": "Hinweis", "legal_basis_lbl": "Gesetzliche Grundlage", "legal_text_lbl": "Gesetzliche Textstelle",
            "qual_lbl": "Qualifikation", "initial_insp_lbl": "Erstabnahme", "recurring_lbl": "Wiederkehrend", "relief_lbl": "Entlastung im Schadensfall",
            "btn_save_report": "Servicebericht in MySQL speichern", "err_valid": "Fehler: Bitte wähle einen Standort und eine Anlage aus!",
            "succ_saved": "Servicebericht erfolgreich in MySQL gespeichert!",
            "tab_details": "Prüfdetails", "tab_gesetz": "Gesetzliche Grundlagen", "tab_historie": "Prüfprotokolle",
            "bitte_waehlen": "--- Bitte wählen ---"
        }
    else:
        TXT_SRV = {
            "title": "Service", "act_lbl": "Action:", "act_hist": "History / Search", "act_add": "Log New Report",
            "filter_lbl": "Filter Location:", "opt_all": "All", "src_lbl": "Quick Search (Real-time):",
            "src_ph": "Trade, summary...", "empty_table": "No entries match your filter criteria.",
            "empty_db": "No service reports available in MySQL table 'service'.", "sel_id": "Select service record for details:",
            "det_title": "Details for Service Deployment", "gewerk": "Trade Classification:",
            "kurz": "Summary / Result:", "zyklus": "Interval:", "hinweis": "Note:", "btn_del": "Delete this report from MySQL", "succ_del": "Report successfully deleted.",
            "loc_lbl": "Location", "lbl_anlage_wahl": "Select Asset *", "class_lbl": "Class", "asset_type_lbl": "Asset Type",
            "kenn1_lbl": "Identification 1", "kenn2_lbl": "Identification 2", "class_desc_lbl": "Class Designation",
            "summary_res_lbl": "Summary / Result", "equipment_lbl": "Required Spare Equipment",
            "interval_lbl": "Interval", "note_lbl": "Note", "legal_basis_lbl": "Legal Basis", "legal_text_lbl": "Legal Provision",
            "qual_lbl": "Qualification", "initial_insp_lbl": "Initial Inspection", "recurring_lbl": "Recurring", "relief_lbl": "Relief in Case of Damage",
            "btn_save_report": "Save Service Report to MySQL", "err_valid": "Error: Please select a location and an asset!",
            "succ_saved": "Service report successfully saved in MySQL!",
            "tab_details": "Inspection Details", "tab_gesetz": "Legal Basis", "tab_historie": "Audit Logs",
            "bitte_waehlen": "--- Please select ---"
        }

    render_page_header(TXT_SRV['title'])
    srv_aktion = st.radio(TXT_SRV["act_lbl"], [TXT_SRV["act_hist"], TXT_SRV["act_add"]], horizontal=True, key="srv_haupt_aktion_v7")
    
    conn = hole_datenbank_verbindung()
    df_service = pd.DataFrame()
    if conn is not None:
        try:
            df_service = pd.read_sql("SELECT * FROM service", conn)
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except:
                pass

    if srv_aktion == TXT_SRV["act_hist"]:
        if df_service.empty:
            st.info(TXT_SRV["empty_db"])
        else:
            s_filter_label = st.radio(TXT_SRV["filter_lbl"], [TXT_SRV["opt_all"], "Neuperlach (NP)", "Fasangarten (FG)"], horizontal=True, key="srv_standort_filter_v7")
            s_filter = standort_code_from_display(s_filter_label)
            col_src_srv, _ = st.columns([3.5, 6.5])
            with col_src_srv: 
                s_suche = st.text_input(TXT_SRV["src_lbl"], placeholder=TXT_SRV["src_ph"], autocomplete="off", key="srv_src_inp_v7")

            df_srv_f = df_service.copy()
            if s_filter_label != TXT_SRV["opt_all"] and s_filter:
                if "standort_text" in df_srv_f.columns:
                    df_srv_f = df_srv_f[df_srv_f["standort_text"].astype(str).str.upper() == s_filter]
                elif "standort" in df_srv_f.columns:
                    df_srv_f = df_srv_f[df_srv_f["standort"].astype(str).str.upper() == s_filter]
                
            if s_suche:
                sl = s_suche.lower()
                df_srv_f = df_srv_f[df_srv_f.astype(str).apply(lambda x: x.str.lower().str.contains(sl, na=False)).any(axis=1)]
            
            if not df_srv_f.empty:
                st.write("")
                
                record_mapping = {
                    r['id']: f"{r.get('anlagebezeichnung', 'Unbekannte Anlage')} ({standort_display_name(r.get('standort_text', r.get('standort', 'NP')) )}) - {str(r.get('kurzfassung', ''))[:30]}"
                    for _, r in df_srv_f.iterrows()
                }
                record_options = [None] + list(record_mapping.keys())
                
                srv_sel_record_id = st.selectbox(
                    TXT_SRV["sel_id"], 
                    options=record_options, 
                    format_func=lambda x: TXT_SRV["bitte_waehlen"] if x is None else record_mapping[x],
                    key="srv_sel_id_selectbox_v7"
                )
                
                if srv_sel_record_id is not None:
                    row_data = df_service[df_service["id"] == srv_sel_record_id].iloc[0].to_dict()
                    
                    st.markdown("---")
                    st.markdown(f"""
                        <div class='service-card'>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;'>
                                <div>
                                    <span class='micro-dot dot-green' style='margin-right: 6px;'></span>
                                    <b style='font-size: 16px; font-weight: 500;'>{row_data.get('anlagebezeichnung', '-')}</b>
                                </div>
                                <div style='font-size: 12px; font-weight: 600; color: #0ea5e9; background: rgba(14, 165, 233, 0.1); padding: 4px 10px; border-radius: 4px;'>
                                    Standort: {row_data.get('standort_text', row_data.get('standort', '-'))}
                                </div>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    t_det, t_law, t_hist = st.tabs([TXT_SRV["tab_details"], TXT_SRV["tab_gesetz"], TXT_SRV["tab_historie"]])
                    
                    with t_det:
                        st.write("")
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            st.markdown(f"<div class='meta-label'>Anlagenklasse</div><div class='meta-val'>{row_data.get('anlagenklasse', '-')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='meta-label' style='margin-top:15px;'>Prüfintervall</div><div class='meta-val'>{row_data.get('intervall', '-')}</div>", unsafe_allow_html=True)
                        with c2:
                            st.markdown(f"<div class='meta-label'>Merkmal / Wert</div><div class='meta-val'>{row_data.get('merkmal', '-')} : {row_data.get('merkmalwert', '-')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='meta-label' style='margin-top:15px;'>Qualifikation</div><div class='meta-val'>{row_data.get('qualifikation', '-')}</div>", unsafe_allow_html=True)
                        with c3:
                            st.markdown(f"<div class='meta-label'>Erstabnahme</div><div class='meta-val'>{row_data.get('erstabnahme', '-')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='meta-label' style='margin-top:15px;'>Wiederkehrende Prüfung</div><div class='meta-val'>{row_data.get('wiederkehrende_pruefung', '-')}</div>", unsafe_allow_html=True)
                        with c4:
                            st.markdown(f"<div class='meta-label'>Anzahl</div><div class='meta-val'>{row_data.get('anzahl', '-')}</div>", unsafe_allow_html=True)
                            st.markdown(f"<div class='meta-label' style='margin-top:15px;'>Baujahr</div><div class='meta-val'>{row_data.get('baujahr', '-')}</div>", unsafe_allow_html=True)
                        
                        st.write("")
                        st.markdown(f"<div class='meta-label'>Kurzfassung / Ergebnis</div><div style='font-size: 13px; background: rgba(0,0,0,0.1); padding: 10px; border-radius: 6px; margin-top: 4px;'>{row_data.get('kurzfassung', 'Keine Kurzfassung hinterlegt.')}</div>", unsafe_allow_html=True)
                        
                    with t_law:
                        st.write("")
                        st.markdown(f"<div class='meta-label'>Gesetzliche Grundlage</div><div style='font-size: 13px; font-weight: 500; margin-bottom: 12px;'>{row_data.get('gesetzl_grundlage', 'Keine Angabe')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='meta-label'>Relevante Textstelle / Paragraph</div><div style='font-size: 13px; font-weight: 500; margin-bottom: 12px;'>{row_data.get('textstelle_gesetz', 'Keine Angabe')}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='meta-label'>Entlastung im Schadensfall</div><div style='font-size: 13px; background: rgba(16, 185, 129, 0.05); border-left: 3px solid #10b981; padding: 10px; border-radius: 0 6px 6px 0;'>{row_data.get('entlastung_schadensfall', 'Keine spezifischen Haftungsdetails hinterlegt.')}</div>", unsafe_allow_html=True)
                        
                    with t_hist:
                        st.write("")
                        st.markdown(f"<div class='meta-label'>Prüfhinweise & Protokolle</div><div style='font-size: 13px; background: rgba(0,0,0,0.1); padding: 10px; border-radius: 6px;'>{row_data.get('Hinweis', 'Keine Protokollhinweise vorhanden.')}</div>", unsafe_allow_html=True)
                        
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    st.write("")
                    if st.checkbox("Sicherheitsabfrage: Wirklich löschen?" if st.session_state.language == "de" else "Security check: Really delete?", key="srv_sicherheits_checkbox"):
                        if st.button(TXT_SRV["btn_del"], key="srv_del_btn_action"):
                            conn_del = hole_datenbank_verbindung()
                            if conn_del:
                                cur = None
                                try:
                                    cur = conn_del.cursor()
                                    cur.execute("DELETE FROM service WHERE id = %s", (srv_sel_record_id,))
                                    conn_del.commit()
                                    st.success(TXT_SRV["succ_del"])
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Fehler beim Löschen: {e}")
                                finally:
                                    if cur:
                                        try:
                                            cur.close()
                                        except:
                                            pass
                                    try:
                                        conn_del.close()
                                    except:
                                        pass
                else:
                    st.write("")
                    st.markdown("##### Übersicht aller gefilterten Serviceeinsätze")
                    
                    spalten_mapping = {
                        "standort_text": "Standort",
                        "anlagenklasse": "Anlagenklasse",
                        "bezeichnung_anlagenklasse": "Klassenbezeichnung",
                        "anlagebezeichnung": "Anlagenart",
                        "kennz_1": "Kennzeichnung 1",
                        "kennz_2": "Kennzeichnung 2",
                        "kurzfassung": "Kurzfassung / Ergebnis",
                        "intervall": "Intervall",
                        "qualifikation": "Qualifikation",
                        "erstabnahme": "Erstabnahme",
                        "wiederkehrende_pruefung": "Wiederkehrende Prüfung",
                        "anzahl": "Anzahl",
                        "baujahr": "Baujahr"
                    }
                    
                    anzeige_df = df_srv_f.drop(columns=["id", "anlage_id"], errors="ignore")
                    anzeige_df = anzeige_df.rename(columns=spalten_mapping)
                    st.dataframe(prepare_display_dataframe(anzeige_df), use_container_width=True, hide_index=True)
            else: 
                st.info(TXT_SRV["empty_table"])
    elif srv_aktion == TXT_SRV["act_add"]:
        anlagen_opts = {}
        conn_anl = hole_datenbank_verbindung()
        if conn_anl:
            try:
                df_anl = pd.read_sql("SELECT id, anlagebezeichnung, anlagenr FROM anlagen ORDER BY anlagebezeichnung ASC", conn_anl)
                for _, r in df_anl.iterrows():
                    anlagen_opts[r['id']] = f"{r['anlagebezeichnung']} (Nr: {r['anlagenr']})" if pd.notnull(r['anlagenr']) else str(r['anlagebezeichnung'])
            except:
                pass
            finally:
                try:
                    conn_anl.close()
                except:
                    pass

        with st.form("srv_form_n_einmalig", clear_on_submit=True):
            col_s1, col_s2, col_s3, col_s4 = st.columns([1.5, 2.5, 2.0, 4.0])
            with col_s1: s_standort = st.selectbox(TXT_SRV["loc_lbl"], ["", "Neuperlach (NP)", "Fasangarten (FG)"], format_func=lambda val: "" if val == "" else val, key="srv_standort_sel_v7")
            with col_s2: 
                s_id = st.selectbox(
                    TXT_SRV["lbl_anlage_wahl"], 
                    options=[None] + list(anlagen_opts.keys()), 
                    format_func=lambda x: TXT_SRV["bitte_waehlen"] if x is None else anlagen_opts[x],
                    key="srv_id_input_v7"
                )
            with col_s3: 
                s_kl_raw = st.text_input(TXT_SRV["class_lbl"], max_chars=6, placeholder="4610", autocomplete="off", key="srv_klasse_input_v7")
                s_kl = s_kl_raw
            with col_s4: s_anl_typ = st.text_input(TXT_SRV["asset_type_lbl"], placeholder="z.B. Personenaufzug", autocomplete="off", key="srv_art_input_v7")
            
            col_s5, col_s6, col_s7 = st.columns([2.0, 2.0, 6.0])
            with col_s5: s_k1 = st.text_input(TXT_SRV["kenn1_lbl"], placeholder="z.B. Haupt", autocomplete="off", key="srv_k1_input_v7")
            with col_s6: s_k2 = st.text_input(TXT_SRV["kenn2_lbl"], placeholder="z.B. Bauteil A", autocomplete="off", key="srv_k2_input_v7")
            with col_s7: s_kl_bez = st.text_input(TXT_SRV["class_desc_lbl"], placeholder="z.B. Aufzugstechnik", autocomplete="off", key="srv_klbez_input_v7")
            
            col_s8, col_s9 = st.columns([5.0, 5.0])
            with col_s8: s_kurz = st.text_input(TXT_SRV["summary_res_lbl"], placeholder="z.B. Quartalswartung erfolgreich", autocomplete="off", key="srv_kurz_input_v7")
            with col_s9: s_ersatzequip = st.text_input(TXT_SRV["equipment_lbl"], placeholder="z.B. Schmieröl", autocomplete="off", key="srv_equip_input_v7")

            col_zz5, col_zz6 = st.columns([2.0, 8.0])
            with col_zz5: s_int = st.text_input(TXT_SRV["interval_lbl"], placeholder="z.B. 6M", autocomplete="off", key="srv_int_input_v7")
            with col_zz6: s_hinw = st.text_input(TXT_SRV["note_lbl"], placeholder="z.B. Keine Mängel", autocomplete="off", key="srv_hinw_input_v7")

            col_uu1, col_uu2 = st.columns([5.0, 5.0])
            with col_uu1: s_gg = st.text_input(TXT_SRV["legal_basis_lbl"], placeholder="z.B. BetrSichV", autocomplete="off", key="srv_gg_input_v7")
            with col_uu2: s_gt = st.text_input(TXT_SRV["legal_text_lbl"], placeholder="z.B. Anhang 1", autocomplete="off", key="srv_gt_input_v7")
            
            col_uu3, col_uu4, col_uu5, col_uu6 = st.columns([3.0, 2.0, 2.0, 3.0])
            with col_uu3: s_qual = st.text_input(TXT_SRV["qual_lbl"], placeholder="z.B. Sachkundiger", autocomplete="off", key="srv_qual_input_v7")
            with col_uu4: s_erst = st.selectbox(TXT_SRV["initial_insp_lbl"], ["", "Ja", "Nein"], key="srv_erst_sel_v7")
            with col_uu5: s_wied = st.selectbox(TXT_SRV["recurring_lbl"], ["", "Ja", "Nein"], key="srv_wied_sel_v7")
            with col_uu6: s_entl = st.text_input(TXT_SRV["relief_lbl"], placeholder="z.B. Ja", autocomplete="off", key="srv_entl_input_v7")
            
            if st.form_submit_button(TXT_SRV["btn_save_report"]):
                if not s_standort or s_id is None: 
                    st.error(TXT_SRV["err_valid"])
                else:
                    s_standort_code = standort_code_from_display(s_standort) or s_standort
                    conn_ins = hole_datenbank_verbindung()
                    if conn_ins:
                        cur = None
                        try:
                            cur = conn_ins.cursor()
                            sql = """INSERT INTO service (anlage_id, standort_text, anlagenklasse, bezeichnung_anlagenklasse, anlagebezeichnung, kennz_1, kennz_2, kurzfassung, intervall, Hinweis, gesetzl_grundlage, textstelle_gesetz, qualifikation, entlastung_schadensfall)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                            val = (s_id, s_standort_code, s_kl, s_kl_bez, s_anl_typ, s_k1, s_k2, s_kurz, s_int, s_hinw, s_gg, s_gt, s_qual, s_entl)
                            cur.execute(sql, val)
                            conn_ins.commit()
                            st.success(TXT_SRV["succ_saved"])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fehler beim Speichern in MySQL: {e}")
                        finally:
                            if cur:
                                try:
                                    cur.close()
                                except:
                                    pass
                            try:
                                conn_ins.close()
                            except:
                                pass