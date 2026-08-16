import streamlit as st  
import pandas as pd  
from datenbank.befehle import hole_datenbank_verbindung  
from logik.ui import render_page_header
  
def zeige_globale_suche():  
    if 'language' not in st.session_state:  
        st.session_state.language = "de"  

    if "selected_detail" not in st.session_state:
        st.session_state.selected_detail = None
  
    if st.session_state.language == "de":  
        TXT_GS = {  
            "title": "Globale 360° Volltextsuche",  
            "desc": "Durchsucht die Datenbank in Echtzeit ( '+' für Mehrfachbegriffe).",  
            "placeholder": "z.B. aufzug + vertrag",  
            "label_suche": "Suchbegriff eingeben",  
            "status_label": "Status",  
            "treffer": "{count} Treffer gefunden",  
            "keine_treffer": "Keine Treffer für: '{term}'",  
            "db_fehler": "Datenbankverbindung fehlgeschlagen."  
        }  
    else:  
        TXT_GS = {  
            "title": "Global 360° Full-Text Search",  
            "desc": "Searches the entire database in real-time ( '+' for multiple terms).",  
            "placeholder": "e.g. elevator + contract",  
            "label_suche": "Enter search term",  
            "status_label": "Status",  
            "treffer": "{count} matches found",  
            "keine_treffer": "No matches for: '{term}'",  
            "db_fehler": "Database connection failed."  
        }  
  
    bg_kachel = "rgba(30, 41, 59, 0.6)"
    border_kachel = "rgba(56, 189, 248, 0.3)"
    shadow_kachel = "0 4px 20px rgba(56, 189, 248, 0.12)"
    color_text = "#f8fafc"
    sub_color = "#94a3b8"
  
    st.markdown(f"""  
    <style>  
    input, select, textarea, div[data-baseweb="select"] span, label, .stRadio div {{  
    font-size: 0.82rem !important;  
    }}  
    div[data-testid="InputInstructions"] {{ display: none !important; }}  

    .search-input-wrapper div[data-baseweb="input"] {{
        max-width: 320px !important;
        width: 320px !important;
    }}
    .search-input-wrapper {{
        max-width: 320px !important;
    }}

    .search-card {{
        background: {bg_kachel};
        border: 1px solid {border_kachel};
        box-shadow: {shadow_kachel};
        border-radius: 6px;
        padding: 10px 12px;
        margin-bottom: 8px;
        color: {color_text};
        font-size: 11.5px;
        line-height: 1.4;
    }}
    
    .stButton > button {{
        padding: 4px 8px !important;
        font-size: 11px !important;
        min-height: 28px !important;
        height: 32px !important;
        background-color: rgba(30, 41, 59, 0.9) !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
        color: #f8fafc !important;
        border-radius: 6px !important;
    }}
    
    .stButton > button:hover {{
        background-color: rgba(14, 165, 233, 0.4) !important;
        border-color: rgba(56, 189, 248, 0.9) !important;
    }}

    .detail-karteikarte {{
        background: {bg_kachel};
        border: 1px solid rgba(56, 189, 248, 0.8);
        border-radius: 12px;
        padding: 25px;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }}
    
    .ent-kv-container {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
        gap: 12px;
        margin-top: 15px;
        margin-bottom: 25px;
    }}
    
    .ent-kv-box {{
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid {border_kachel};
        border-radius: 6px;
        padding: 10px 14px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 15px;
    }}
    
    .ent-kv-label {{
        font-size: 10px;
        color: {sub_color};
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0;
        font-weight: 600;
        white-space: nowrap;
        flex-shrink: 0;
    }}
    
    .ent-kv-value {{
        font-size: 13px;
        color: {color_text};
        font-weight: 500;
        text-align: right;
        word-break: break-word;
    }}
    
    .compact-alert-box {{  
        max-width: 320px;  
        background: rgba(15, 23, 42, 0.85);  
        border: 1px solid rgba(245, 158, 11, 0.4);  
        box-shadow: 0 4px 15px rgba(245, 158, 11, 0.15);  
        border-radius: 8px;  
        padding: 10px 14px;  
        color: #fbbf24;  
        font-size: 12px;  
        margin-top: 5px;  
    }}  
    .micro-dot {{
        height: 8px;
        width: 8px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }}
    .dot-green {{ background-color: #10b981; }}
    .dot-yellow {{ background-color: #f59e0b; }}
    .dot-red {{ background-color: #ef4444; }}
    
    </style>  
    """, unsafe_allow_html=True)  

    render_page_header(TXT_GS['title'], TXT_GS['desc'])
  
    st.markdown('<div class="search-input-wrapper">', unsafe_allow_html=True)
    suchbegriff = st.text_input(  
        TXT_GS["label_suche"],   
        max_chars=70,   
        placeholder=TXT_GS["placeholder"],   
        autocomplete="off",  
        key="globaler_such_input_kompakt"  
    )  
    st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.markdown(f"<div style='height: 1px; background-color: {border_kachel}; opacity: 0.5; margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    if st.session_state.selected_detail:
        sel_tab = st.session_state.selected_detail["tabelle"]
        sel_ds = st.session_state.selected_detail["daten"]
        
        anzeige_ds = {k: v for k, v in sel_ds.items() if str(k).lower() != "id" and not str(k).lower().endswith("_id")}
        
        st.markdown(f"""
        <div class="detail-karteikarte">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style='color: #38bdf8; margin: 0;'>Detail-Ansicht: <span style='color: #fff;'>[{sel_tab.upper()}]</span></h3>
            </div>
        """, unsafe_allow_html=True)
        
        tab_uebersicht, tab_rohdaten, tab_bearbeiten = st.tabs(["Strukturierte Übersicht", "System-Rohdaten", "Bearbeiten"])
        
        with tab_uebersicht:
            html_grid = '<div class="ent-kv-container">'
            for k, v in anzeige_ds.items():
                if v is not None and str(v).strip() != "":
                    clean_label = str(k).replace("_", " ").title()
                    html_grid += f'<div class="ent-kv-box"><div class="ent-kv-label">{clean_label}</div><div class="ent-kv-value">{v}</div></div>'
            html_grid += '</div>'
            st.markdown(html_grid, unsafe_allow_html=True)
            
        with tab_rohdaten:
            st.json(anzeige_ds)

        with tab_bearbeiten:
            st.write("")
            with st.form(f"form_edit_global_{sel_tab}"):
                updated_values = {}
                for k, v in sel_ds.items():
                    if str(k).lower() == "id" or str(k).lower().endswith("_id"):
                        continue
                    clean_label = str(k).replace("_", " ").title()
                    val_str = "" if v is None else str(v)
                    updated_values[k] = st.text_input(clean_label, value=val_str, key=f"edit_field_{sel_tab}_{k}")

                st.write("")
                if st.form_submit_button("Änderungen in MySQL speichern", type="primary"):
                    conn_up = hole_datenbank_verbindung()
                    if conn_up:
                        cur = None
                        try:
                            cur = conn_up.cursor()
                            set_clauses = []
                            vals = []
                            record_id = sel_ds.get("id")
                            
                            for col, new_val in updated_values.items():
                                set_clauses.append(f"`{col}` = %s")
                                vals.append(new_val if new_val != "" else None)
                            
                            if record_id is not None:
                                vals.append(record_id)
                                sql_up = f"UPDATE `{sel_tab}` SET {', '.join(set_clauses)} WHERE id = %s"
                                cur.execute(sql_up, tuple(vals))
                                conn_up.commit()
                                st.success("Datensatz erfolgreich in MySQL aktualisiert!")
                                st.session_state.selected_detail = None
                                st.rerun()
                            else:
                                st.error("Fehler: Primärschlüssel (ID) für den Update-Vorgang nicht gefunden.")
                        except Exception as e:
                            st.error(f"Fehler beim Speichern: {e}")
                        finally:
                            if cur:
                                try:
                                    cur.close()
                                except:
                                    pass
                            try:
                                conn_up.close()
                            except:
                                pass
                
        st.write("")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("Detail-Ansicht schließen", use_container_width=True, type="primary"):
                st.session_state.selected_detail = None
                st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("---")

    if suchbegriff.strip():  
        such_teile = [teil.strip() for teil in suchbegriff.split("+") if teil.strip()]  
        alle_treffer = []  
          
        ziel_tabellen = [  
            "anlagen",   
            "auffaelligkeiten",   
            "firmeninfo",   
            "service",   
            "vertragsanalyse"
        ]  
  
        try:  
            conn = hole_datenbank_verbindung()  
            if conn is not None:  
                cursor = conn.cursor(dictionary=True)  
                  
                for tabellen_name in ziel_tabellen:  
                    try:  
                        cursor.execute(f"SHOW COLUMNS FROM `{tabellen_name}`")  
                        spalten_rows = cursor.fetchall()  
                        text_spalten = []  
                          
                        for sp_row in spalten_rows:  
                            feld_typ = str(sp_row.get("Type", "")).lower()  
                            if "char" in feld_typ or "text" in feld_typ or "int" in feld_typ:  
                                text_spalten.append(sp_row.get("Field"))  
                          
                        if text_spalten:  
                            and_bedingungen = []  
                            query_werte = []  
                              
                            for teil in such_teile:  
                                or_teile = [f"`{sp}` LIKE %s" for sp in text_spalten]  
                                and_bedingungen.append("(" + " OR ".join(or_teile) + ")")  
                                for _ in text_spalten:  
                                    query_werte.append(f"%{teil}%")  
                              
                            sql = f"SELECT * FROM `{tabellen_name}` WHERE " + " AND ".join(and_bedingungen)  
                              
                            cursor.execute(sql, tuple(query_werte))  
                            ergebnisse = cursor.fetchall()  
                            for ds in ergebnisse:  
                                alle_treffer.append({  
                                    "tabelle": tabellen_name,  
                                    "daten": ds  
                                })  
                    except Exception:  
                        pass  
                  
                cursor.close()  
                conn.close()  
            else:  
                st.markdown(f'<div class="compact-alert-box">{TXT_GS["db_fehler"]}</div>', unsafe_allow_html=True)  
                return  
        except Exception as e:  
            st.markdown(f'<div class="compact-alert-box">Fehler: {e}</div>', unsafe_allow_html=True)  
            return  
  
        gesamt = len(alle_treffer)  
  
        if gesamt == 0:  
            st.markdown(f'<div class="compact-alert-box">{TXT_GS["keine_treffer"].format(term=suchbegriff)}</div>', unsafe_allow_html=True)  
        else:  
            st.markdown(f"<div style='font-weight: 700; color: #38bdf8; margin-bottom: 8px; font-size: 12px;'>{TXT_GS['status_label']}:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{TXT_GS['treffer'].format(count=gesamt)}</div>", unsafe_allow_html=True)  
              
            col_links_spalte, col_rechts_spalte = st.columns(2)  
              
            for i, treffer in enumerate(alle_treffer):  
                tab = treffer["tabelle"]  
                ds = treffer["daten"]  
                  
                status_wert = str(ds.get("zustand", ds.get("status", ""))).lower()  
                if any(w in status_wert for w in ["ordnung", "bereit", "in ordnung", "ok", "gut", "betriebsbereit"]):  
                    d_class = "dot-green"
                elif any(w in status_wert for w in ["überfällig", "fehler", "kritisch", "warnung", "anstehend"]):  
                    d_class = "dot-red"
                else:  
                    d_class = "dot-yellow"
                  
                titel_text = "Eintrag"
                unter_text = ""
                
                if tab == "anlagen":
                    titel_text = f"Anlage: {ds.get('anlagebezeichnung', 'Unbenannt')} ({ds.get('standort_ort', '-')})"
                    unter_text = f"Typ: {ds.get('anlagetyp', '-')} | Gewerk: {ds.get('untergewerk', '-')}"
                elif tab == "vertragsanalyse":
                    titel_text = f"Vertrag: {ds.get('vertragsname', 'Unbenannt')}"
                    unter_text = f"Firma: {ds.get('firmenname', '-')} | Nächste Wartung: {ds.get('naechste_wartung', '-')}"
                elif tab == "firmeninfo":
                    titel_text = f"Firma: {ds.get('firmenname', 'Unbenannt')}"
                    unter_text = f"Gewerk: {ds.get('firmebranche', '-')} | Tel: {ds.get('firmentelefon', '-')}"
                elif tab == "service":
                    titel_text = f"Service: {ds.get('anlagebezeichnung', 'Protokoll')}"
                    unter_text = f"Intervall: {ds.get('intervall', '-')} | Info: {str(ds.get('kurzfassung', '-'))[:30]}..."
                elif tab == "auffaelligkeiten":
                    titel_text = f"Auffälligkeit: {ds.get('anlagebezeichnung', 'Unbenannt')}"
                    unter_text = f"Standort: {ds.get('standort_text', '-')} | Vertrag: {ds.get('vertrag', '-')}"
                else:
                    wichtige_felder = [f"<b>{k}:</b> {v}" for k, v in list(ds.items()) if v is not None and str(k).lower() != "id" and not str(k).lower().endswith("_id")][:2]
                    unter_text = " | ".join(wichtige_felder)

                aktive_spalte = col_links_spalte if i % 2 == 0 else col_rechts_spalte

                with aktive_spalte:
                    with st.container():
                        c_text, c_btn = st.columns([0.8, 0.2])
                        
                        with c_text:
                            st.markdown(f"""  
                            <div class="search-card">  
                                <span class="micro-dot {d_class}"></span>
                                <span style='color: #38bdf8; font-weight: 600;'>[{tab.upper()}]</span> <b>{titel_text}</b><br>  
                                <span style='color: {sub_color}; margin-left: 14px;'>{unter_text}</span>  
                            </div>  
                            """, unsafe_allow_html=True)
                            
                        with c_btn:
                            st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                            if st.button("Details", key=f"jump_btn_{tab}_{i}", help="Details anzeigen"):
                                st.session_state.selected_detail = {"tabelle": tab, "daten": ds}
                                st.rerun()