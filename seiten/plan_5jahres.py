import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from datenbank.befehle import hole_datenbank_verbindung

@st.dialog("Strategischer 5-Jahres-Wartungsplan (Vollbild-Ansicht)", width="large")
def zeige_matrix_modal(termine_liste, wahl_jahr):
    monate_Namen = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
    
    st.markdown(f"<div style='font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px;'>Projektions-Jahr: {wahl_jahr} | Gesamteinträge: {len(termine_liste)}</div>", unsafe_allow_html=True)
    
    matrix_html = "<div class='timeline-matrix-container' style='max-height: 70vh; overflow-y: auto;'>"
    matrix_html += "<div class='matrix-header'><div>Anlage / Standort</div>" + "".join([f"<div>{m}</div>" for m in monate_Namen]) + "</div>"
    
    anlagen_gruppen = {}
    for t in termine_liste:
        key = (t["Anlage"], t["ID"], t["Standort"])
        if key not in anlagen_gruppen:
            anlagen_gruppen[key] = []
        anlagen_gruppen[key].append(t)
    
    for (anl_name, anl_id, anl_std), g_termine in anlagen_gruppen.items():
        matrix_html += f"<div class='matrix-row'><div style='font-weight: 500;'>{anl_name}<br><span style='font-size: 10px; opacity: 0.6;'>Standort: {anl_std}</span></div>"
        
        for m_idx in range(1, 13):
            matrix_html += "<div class='matrix-cell'>"
            passende_termine = [t for t in g_termine if t["Monat"] == m_idx]
            if passende_termine:
                pt = passende_termine[0]
                tooltip_text = f"{pt['Anlage']} | Termin: {pt['DatumFmt']} | Status: {pt['Status']} | Partner: {pt['Firma']}"
                matrix_html += f"<span class='micro-dot-matrix {pt['Dot']}' title='{tooltip_text}'></span>"
            matrix_html += "</div>"
        matrix_html += "</div>"
        
    matrix_html += "</div>"
    st.markdown(matrix_html, unsafe_allow_html=True)

def zeige_5jahresplan():
    st.markdown("""
        <style>
        .ent-subheader { font-size: 11px; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid rgba(148, 163, 184, 0.2); }
        
        .timeline-matrix-container {
            background: rgba(148, 163, 184, 0.02);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 8px;
            padding: 20px;
            overflow-x: auto;
        }
        .matrix-header {
            display: grid;
            grid-template-columns: 220px repeat(12, 1fr);
            gap: 4px;
            padding-bottom: 12px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            font-size: 11px;
            font-weight: 600;
            color: #94a3b8;
            text-transform: uppercase;
            text-align: center;
        }
        .matrix-row {
            display: grid;
            grid-template-columns: 220px repeat(12, 1fr);
            gap: 4px;
            padding: 12px 0;
            border-bottom: 1px solid rgba(148, 163, 184, 0.1);
            align-items: center;
            font-size: 12px;
        }
        .matrix-row:hover {
            background-color: rgba(14, 165, 233, 0.03);
        }
        .matrix-cell {
            text-align: center;
            position: relative;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-left: 1px dashed rgba(148, 163, 184, 0.1);
        }
        
        .micro-dot-matrix {
            height: 10px;
            width: 10px;
            border-radius: 50%;
            display: inline-block;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .micro-dot-matrix:hover {
            transform: scale(1.6);
        }
        .dot-red { background-color: #ef4444; box-shadow: 0 0 6px rgba(239, 68, 68, 0.6); }
        .dot-yellow { background-color: #f59e0b; box-shadow: 0 0 6px rgba(245, 158, 11, 0.6); }
        .dot-green { background-color: #10b981; box-shadow: 0 0 6px rgba(16, 185, 129, 0.6); }
        
        .proj-label {
            font-size: 11px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        
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

    lang = st.session_state.get("language", "de")
    is_de = lang == "de"
    
    TXT_PLAN = {
        "title": "Strategischer 5-Jahres-Wartungsplan" if is_de else "Strategic 5-Year Maintenance Plan",
        "desc": "Interaktive Monats-Matrix, Gitterstruktur & Micro-Dot Fristen-Controlling" if is_de else "Interactive monthly matrix, grid structure & micro-dot deadline controlling",
        "proj_lbl": "Projektions-Filter" if is_de else "Projection Filter",
        "standort_lbl": "Standort-Auswahl" if is_de else "Location Selection",
        "opt_alle": "Alle Standorte" if is_de else "All Locations",
        "chk_np": "Neuperlach (NP)",
        "chk_fg": "Fasangarten (FG)",
        "chk_rot": "Fällig / Überfällig" if is_de else "Overdue",
        "chk_gelb": "Warnung (Anstehend)" if is_de else "Warning (Upcoming)",
        "chk_gruen": "Planmäßig (Aktiv)" if is_de else "Active (Planned)",
        "no_dates": "Keine Wartungstermine für das Jahr {jahr} mit den gewählten Filtern gefunden." if is_de else "No maintenance dates found for the year {jahr} with the selected filters.",
        "no_data": "Keine Vertrags- oder Wartungsdaten in der MySQL-Datenbank gefunden." if is_de else "No contract or maintenance data found in MySQL database."
    }

    st.markdown(f"<div class='custom-huge-title'>{TXT_PLAN['title']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size: 13px; color: var(--text-color); opacity: 0.7; margin-top: 6px; margin-bottom: 25px;'>{TXT_PLAN['desc']}</div>", unsafe_allow_html=True)
    
    conn = hole_datenbank_verbindung()
    df_verträge = pd.DataFrame()
    if conn is not None:
        try:
            df_verträge = pd.read_sql("SELECT * FROM wartungsuebersicht", conn)
            if not df_verträge.empty and "naechste_wartung" in df_verträge.columns:
                if "anlagenname" in df_verträge.columns:
                    df_verträge["anlagebezeichnung"] = df_verträge["anlagenname"]
                if "standort" in df_verträge.columns:
                    df_verträge["standort_text"] = df_verträge["standort"]
                if "intervall_monate" in df_verträge.columns:
                    df_verträge["zyklus_monate"] = df_verträge["intervall_monate"]
            else:
                raise Exception("Fallback auf vertragsanalyse")
        except Exception:
            try:
                q = """
                    SELECT 
                        v.id, v.anlage_id, v.anlagebezeichnung, v.standort_text, 
                        v.vertragsname, v.wartungsgrundlage, v.naechste_wartung, 
                        v.zyklus_monate, f.firmenname AS firma
                    FROM vertragsanalyse v
                    LEFT JOIN firmeninfo f ON v.firma_id = f.id
                """
                df_verträge = pd.read_sql(q, conn)
            except Exception:
                try:
                    df_verträge = pd.read_sql("SELECT * FROM vertragsanalyse", conn)
                except:
                    pass
        finally:
            try:
                conn.close()
            except:
                pass

    if not df_verträge.empty:
        col_links, col_rechts = st.columns([7.8, 2.2])
        
        with col_rechts:
            with st.container(border=True):
                st.markdown(f"<div class='proj-label'>{TXT_PLAN['proj_lbl']}</div>", unsafe_allow_html=True)
                
                standort_wahl = st.radio(
                    TXT_PLAN["standort_lbl"],
                    options=[TXT_PLAN["opt_alle"], TXT_PLAN["chk_np"], TXT_PLAN["chk_fg"]],
                    index=0,
                    key="rad_standort_v17"
                )
                
                std_filter = []
                if standort_wahl == TXT_PLAN["chk_np"]:
                    std_filter = ["NP"]
                elif standort_wahl == TXT_PLAN["chk_fg"]:
                    std_filter = ["FG"]
                else:
                    std_filter = ["NP", "FG"]
                
                st.markdown("---")
                aktuelles_jahr = datetime.now().year
                jahre_optionen = [aktuelles_jahr + i for i in range(5)]
                wahl_jahr = st.radio("Projektions-Jahr", options=jahre_optionen, index=0, key="rad_year_v17")
                
                st.markdown("---")
                show_rot = st.checkbox(TXT_PLAN["chk_rot"], value=True, key="chk_rot_v17")
                show_gelb = st.checkbox(TXT_PLAN["chk_gelb"], value=True, key="chk_rot_v17_warn")
                show_gruen = st.checkbox(TXT_PLAN["chk_gruen"], value=True, key="chk_gruen_v17")
                
                status_kategorien = []
                if show_rot: status_kategorien.append("Fällig")
                if show_gelb: status_kategorien.append("Warnung")
                if show_gruen: status_kategorien.append("Planmäßig")
            
        with col_links:
            heute_dt = pd.Timestamp(datetime.now().date())
            termine_liste = []
            
            for _, r in df_verträge.iterrows():
                n_w_val = r.get("naechste_wartung")
                if pd.isnull(n_w_val):
                    continue
                    
                n_w_dt = pd.to_datetime(n_w_val, errors='coerce')
                if pd.isnull(n_w_dt):
                    continue
                
                try:
                    zyklus_m = int(r["zyklus_monate"]) if pd.notnull(r.get("zyklus_monate")) and int(r.get("zyklus_monate")) > 0 else 12
                except:
                    zyklus_m = 12
                
                for j in range(6):
                    verschiebung_tage = j * (zyklus_m * 30.44)
                    projizierter_termin = n_w_dt + timedelta(days=verschiebung_tage)
                    proj_jahr = projizierter_termin.year
                    
                    if proj_jahr == wahl_jahr:
                        std_val = str(r.get("standort_text", r.get("standort", "NP")))
                        if std_filter and std_val not in std_filter and std_val != "nan":
                            continue
                        
                        if projizierter_termin < heute_dt:
                            p_status, status_kat, dot_cls = "Überfällig", "Fällig", "dot-red"
                        elif heute_dt <= projizierter_termin <= (heute_dt + timedelta(days=30)):
                            p_status, status_kat, dot_cls = "Anstehend", "Warnung", "dot-yellow"
                        else: 
                            p_status, status_kat, dot_cls = "Planmäßig", "Planmäßig", "dot-green"
                            
                        if status_kat in status_kategorien:
                            termine_liste.append({
                                "Anlage": r.get("anlagebezeichnung", r.get("anlagenname", "Unbekannte Anlage")),
                                "ID": r.get("id", "-"),
                                "Standort": std_val if std_val != "nan" else "NP",
                                "Monat": projizierter_termin.month,
                                "DatumFmt": projizierter_termin.strftime('%d.%m.%Y'),
                                "Status": p_status,
                                "Dot": dot_cls,
                                "Firma": r.get("firma", r.get("firma", "-")) if pd.notnull(r.get("firma", None)) else "Extern",
                                "Vertrag": r.get("vertragsname", r.get("wartungsgrundlage", "-"))
                            })
            
            if termine_liste:
                monate_Namen = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]
                
                col_head_txt, col_head_btn = st.columns([6.5, 3.5])
                with col_head_txt:
                    st.markdown(f"##### Fristen-Matrix & Gitter — Jahr {wahl_jahr} ({len(termine_liste)} Termine)")
                with col_head_btn:
                    if st.button("⛶ Vollbild / Modal öffnen", use_container_width=True, key="btn_open_matrix_modal"):
                        zeige_matrix_modal(termine_liste, wahl_jahr)
                
                st.write("")
                
                matrix_html = "<div class='timeline-matrix-container'>"
                matrix_html += "<div class='matrix-header'><div>Anlage / Standort</div>" + "".join([f"<div>{m}</div>" for m in monate_Namen]) + "</div>"
                
                anlagen_gruppen = {}
                for t in termine_liste:
                    key = (t["Anlage"], t["ID"], t["Standort"])
                    if key not in anlagen_gruppen:
                        anlagen_gruppen[key] = []
                    anlagen_gruppen[key].append(t)
                
                for (anl_name, anl_id, anl_std), g_termine in anlagen_gruppen.items():
                    matrix_html += f"<div class='matrix-row'><div style='font-weight: 500;'>{anl_name}<br><span style='font-size: 10px; opacity: 0.6;'>Standort: {anl_std}</span></div>"
                    
                    for m_idx in range(1, 13):
                        matrix_html += "<div class='matrix-cell'>"
                        passende_termine = [t for t in g_termine if t["Monat"] == m_idx]
                        if passende_termine:
                            pt = passende_termine[0]
                            tooltip_text = f"{pt['Anlage']} | Termin: {pt['DatumFmt']} | Status: {pt['Status']} | Partner: {pt['Firma']}"
                            matrix_html += f"<span class='micro-dot-matrix {pt['Dot']}' title='{tooltip_text}'></span>"
                        matrix_html += "</div>"
                    matrix_html += "</div>"
                    
                matrix_html += "</div>"
                st.markdown(matrix_html, unsafe_allow_html=True)
                
                st.write("")
                st.markdown("<div style='font-size: 11px; opacity: 0.6; text-align: right;'>Tipp: Bewegen Sie den Mauszeiger über einen Micro-Dot, um die detaillierten Wartungsinformationen anzuzeigen.</div>", unsafe_allow_html=True)
            else:
                st.info(TXT_PLAN["no_dates"].format(jahr=wahl_jahr))
    else:
       st.info(TXT_PLAN["no_data"])