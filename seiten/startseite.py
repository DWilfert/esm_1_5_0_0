import streamlit as str_lit
import pandas as pd
from datetime import datetime
import warnings
from datenbank.befehle import hole_datenbank_verbindung
from logik.design import lade_design_farben
from logik.ui import render_kpi_card, render_page_header

warnings.filterwarnings("ignore", category=UserWarning)

def zeige_startseite():
    palette = lade_design_farben()
    css = """
        <style>
        :root {
            --theme-bg: __BG_APP__;
            --theme-sidebar: __BG_SIDEBAR__;
            --theme-card: __CARD_BG__;
            --theme-border: __BORDER_COLOR__;
            --theme-text: __TEXT_MAIN__;
            --theme-muted: __TEXT_MUTED__;
            --theme-accent: __ACCENT_COLOR__;
            --theme-input: __INPUT_BG__;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }
        div[data-testid="InputInstructions"] + div, .stTextInput small, .stTextArea small {
            display: none !important;
        }
        @keyframes slideUpFade {
            0% { opacity: 0; transform: translateY(10px); }
            100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes pulseGreen {
            0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
            70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
            100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
        }
        @keyframes pulseRed {
            0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
            70% { box-shadow: 0 0 0 6px rgba(239, 68, 68, 0); }
            100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
        }
        .ent-kpi-card {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(15, 23, 42, 0.82) 100%);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(125, 211, 252, 0.28);
            border-radius: 14px;
            padding: 15px 18px;
            display: flex;
            flex-direction: column;
            align-items: center !important;
            text-align: center !important;
            margin-bottom: 12px;
            box-shadow: 0 14px 28px rgba(2, 6, 23, 0.22), inset 0 1px 0 rgba(255,255,255,0.04);
            transition: all 0.3s ease;
            animation: slideUpFade 0.6s ease forwards;
            opacity: 0;
            position: relative;
            overflow: hidden;
        }
        .ent-kpi-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 18px 36px rgba(2, 6, 23, 0.28), inset 0 1px 0 rgba(255,255,255,0.05);
            border-color: rgba(125, 211, 252, 0.6);
        }
        .delay-1 { animation-delay: 0.05s; }
        .delay-2 { animation-delay: 0.15s; }
        .delay-3 { animation-delay: 0.25s; }
        .delay-4 { animation-delay: 0.35s; }

        .ent-kpi-title {
            font-size: 10px;
            color: var(--theme-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
            font-weight: 700;
            text-align: center !important;
            width: 100%;
        }
        .ent-kpi-value {
            font-size: 24px;
            font-weight: 600;
            color: var(--theme-text);
            display: flex;
            align-items: center;
            justify-content: center !important;
            letter-spacing: -0.2px;
            text-align: center !important;
            width: 100%;
        }
        .micro-dot {
            height: 6px;
            width: 6px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            margin-left: 8px;
        }
        .micro-dot-green-pulse {
            animation: pulseGreen 2.5s infinite;
        }
        .micro-dot-red {
            height: 6px;
            width: 6px;
            background-color: #ef4444;
            border-radius: 50%;
            display: inline-block;
            margin-left: 8px;
        }
        .micro-dot-red-pulse {
            animation: pulseRed 2.5s infinite;
        }
        .micro-dot-yellow {
            height: 6px;
            width: 6px;
            background-color: #f59e0b;
            border-radius: 50%;
            display: inline-block;
            margin-left: 8px;
        }

        .ent-section-title {
            font-size: 11px;
            color: var(--theme-muted);
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-top: 25px;
            margin-bottom: 15px;
            font-weight: 600;
            border-bottom: 1px solid var(--theme-border);
            padding-bottom: 6px;
        }

        .timeline-container {
            border-left: 1px solid var(--theme-border);
            margin-left: 6px;
            padding-left: 20px;
            position: relative;
        }
        .timeline-item {
            position: relative;
            margin-bottom: 20px;
            animation: slideUpFade 0.6s ease forwards;
            opacity: 0;
        }
        .timeline-dot-wrapper {
            position: absolute;
            left: -24.5px;
            top: 4px;
            background: transparent;
            padding: 2px 0;
        }
        .timeline-date {
            font-size: 10px;
            color: var(--theme-muted);
            margin-bottom: 2px;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        .timeline-text {
            font-size: 13px;
            color: var(--theme-text);
            font-weight: 400;
        }
        .timeline-subtext {
            font-size: 11px;
            color: var(--theme-muted);
            font-weight: 300;
        }

        .loc-row {
            display: flex;
            justify-content: flex-start;
            align-items: center;
            gap: 30px;
            padding: 12px 0;
            border-bottom: 1px solid var(--theme-border);
            animation: slideUpFade 0.6s ease forwards;
            opacity: 0;
        }
        .loc-name {
            font-size: 13px;
            color: var(--theme-text);
            font-weight: 500;
            width: 130px;
        }
        .loc-stats {
            display: flex;
            gap: 20px;
            font-size: 11.5px;
            color: var(--theme-muted);
        }
        .loc-stat-item {
            display: flex;
            align-items: center;
        }

        .custom-huge-title {
            font-size: 2.8rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.05em !important;
            margin-bottom: 0px !important;
            line-height: 1.1 !important;
            white-space: nowrap !important;
            color: var(--theme-text) !important;
        }
        </style>
    """
    css = css.replace("__BG_APP__", palette["bg_app"]) \
             .replace("__BG_SIDEBAR__", palette["bg_sidebar"]) \
             .replace("__CARD_BG__", palette["card_bg"]) \
             .replace("__BORDER_COLOR__", palette["border_color"]) \
             .replace("__TEXT_MAIN__", palette["text_main"]) \
             .replace("__TEXT_MUTED__", palette["text_muted"]) \
             .replace("__ACCENT_COLOR__", palette["accent_color"]) \
             .replace("__INPUT_BG__", palette["input_bg"])
    str_lit.markdown(css, unsafe_allow_html=True)

    if "language" not in str_lit.session_state:
        str_lit.session_state.language = "de"

    if str_lit.session_state.language == "de":
        TXT_HOME = {
            "titel_home": "Vertrags- & Wartungsmanagement",
            "subtitel_home": "EXECUTIVE DASHBOARD & SYSTEM-CONTROLLING V1.5.0.0",
            "kpi_1": "Gesamtverträge",
            "kpi_2": "Fristen-Alarm",
            "kpi_3": "Jahresvolumen (Bestand)",
            "kpi_4": "Optimierte Einsparung",
            "timeline_title": "KRITISCHE & ANSTEHENDE FRISTEN (NÄCHSTE 30 TAGE)",
            "location_title": "STANDORT STATUS-MATRIX & HEALTH SCORE",
            "loc_contracts": "Verträge",
            "loc_alarms": "Alarme",
            "no_critical": "Keine kritischen oder anstehenden Fristen im gewählten Zeitraum.",
            "quick_title": "⚡ Schnellzugriff & Aktionen",
            "btn_v": "Zur Vertragsanalyse",
            "btn_w": "Zur Wartungsübersicht",
            "btn_s": "Service-Berichte aufrufen",
            "summary_title": "Portfolio-Übersicht",
            "summary_loc": "Standort",
            "summary_contracts": "Verträge",
            "summary_alarms": "Alarme"
        }
    else:
        TXT_HOME = {
            "titel_home": "Contract & Maintenance Management",
            "subtitel_home": "EXECUTIVE DASHBOARD & SYSTEM CONTROLLING V1.5.0.0",
            "kpi_1": "Total Contracts",
            "kpi_2": "Deadline Alarms",
            "kpi_3": "Total Volume (Actual)",
            "kpi_4": "Optimized Savings",
            "timeline_title": "CRITICAL & UPCOMING DEADLINES (NEXT 30 DAYS)",
            "location_title": "LOCATION HEALTH MATRIX & SCORE",
            "loc_contracts": "Contracts",
            "loc_alarms": "Alarms",
            "no_critical": "No critical or upcoming deadlines found.",
            "quick_title": "⚡ Quick Actions",
            "btn_v": "Open Contract Analysis",
            "btn_w": "Open Maintenance Overview",
            "btn_s": "Open Service Reports",
            "summary_title": "Portfolio Overview",
            "summary_loc": "Location",
            "summary_contracts": "Contracts",
            "summary_alarms": "Alarms"
        }

    col_titel, col_steuerung = str_lit.columns([0.85, 0.15])
    with col_titel:
        render_page_header(TXT_HOME['titel_home'], eyebrow=TXT_HOME['subtitel_home'])

    with col_steuerung:
        btn_cols = str_lit.columns(2)
        with btn_cols[0]:
            if str_lit.button(
                "DE",
                key="lang_toggle_de",
                type="primary" if str_lit.session_state.language == "de" else "secondary",
                width="content"
            ):
                str_lit.session_state.language = "de"
                try:
                    str_lit.query_params["lang"] = "de"
                except Exception:
                    pass
                str_lit.rerun()

        with btn_cols[1]:
            if str_lit.button(
                "EN",
                key="lang_toggle_en",
                type="primary" if str_lit.session_state.language == "en" else "secondary",
                width="content"
            ):
                str_lit.session_state.language = "en"
                try:
                    str_lit.query_params["lang"] = "en"
                except Exception:
                    pass
                str_lit.rerun()
    
    total_vertraege = 0
    c_rot = 0
    sum_kosten = 0.0
    sum_einsparung = 0.0
    timeline_data = []
    location_data = []
    
    conn = hole_datenbank_verbindung()
    if conn is not None:
        try:
            df_all = pd.read_sql("SELECT anlagebezeichnung, vertragsname, naechste_wartung, standort_text, kosten_bestand_pa, benchmark_ais_pa FROM vertragsanalyse", conn)
            
            if not df_all.empty:
                total_vertraege = len(df_all)
                df_all['kosten_bestand_pa'] = pd.to_numeric(df_all['kosten_bestand_pa']).fillna(0.0)
                df_all['benchmark_ais_pa'] = pd.to_numeric(df_all['benchmark_ais_pa']).fillna(0.0)
                
                sum_kosten = df_all['kosten_bestand_pa'].sum()
                sum_einsparung = sum_kosten - df_all['benchmark_ais_pa'].sum()
                
                df_all['naechste_wartung'] = pd.to_datetime(df_all['naechste_wartung'], errors='coerce')
                heute = pd.Timestamp(datetime.now().date())
                
                df_valid_dates = df_all.dropna(subset=['naechste_wartung'])
                c_rot = len(df_valid_dates[df_valid_dates['naechste_wartung'] < heute])
                
                df_critical = df_valid_dates[df_valid_dates['naechste_wartung'] <= (heute + pd.Timedelta(days=30))]
                df_sorted = df_critical.sort_values(by='naechste_wartung').head(5)
                
                for i, r in enumerate(df_sorted.itertuples()):
                    d_obj = r.naechste_wartung
                    if d_obj < heute:
                        dot_class = "micro-dot-red micro-dot-red-pulse"
                    else:
                        dot_class = "micro-dot-yellow"
                        
                    timeline_data.append({
                        "anlage": r.anlagebezeichnung,
                        "vertrag": r.vertragsname,
                        "datum": d_obj.strftime("%d.%m.%Y"),
                        "dot": dot_class,
                        "delay": f"animation-delay: {0.1 + (i*0.1)}s;"
                    })
                
                df_loc = df_all.copy()
                df_loc['is_alarm'] = (df_loc['naechste_wartung'] < heute).astype(int)
                
                loc_grouped = df_loc.groupby('standort_text').agg(
                    contracts=('anlagebezeichnung', 'count'),
                    alarms=('is_alarm', 'sum')
                ).reset_index()
                
                for i, r in enumerate(loc_grouped.itertuples()):
                    st_name = r.standort_text if pd.notnull(r.standort_text) else "Unbekannt"
                    location_data.append({
                        "name": st_name,
                        "contracts": int(r.contracts),
                        "alarms": int(r.alarms),
                        "delay": f"animation-delay: {0.1 + (i*0.1)}s;"
                    })
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except:
                pass

    # Formatierte Strings für die KPIs vorab erstellen
    formatted_kosten = f"{sum_kosten:,.0f} €".replace(',', '.')
    formatted_einsparung = f"+{sum_einsparung:,.0f} €".replace(',', '.')

    # 4 professionelle KPI-Cards für den ersten Blick
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = str_lit.columns(4)
    
    with col_kpi1:
        str_lit.markdown(render_kpi_card(TXT_HOME['kpi_1'], f"{total_vertraege} <span class='micro-dot micro-dot-green-pulse'></span>"), unsafe_allow_html=True)

    with col_kpi2:
        status_text = f"{c_rot} Überfällig" if c_rot > 0 else "Alles im Plan"
        dot_class = "micro-dot-red micro-dot-red-pulse" if c_rot > 0 else "micro-dot"
        val_color = "#ef4444" if c_rot > 0 else "var(--text-color)"
        str_lit.markdown(render_kpi_card(TXT_HOME['kpi_2'], f"{status_text} <span class='{dot_class}'></span>", val_color), unsafe_allow_html=True)

    with col_kpi3:
        str_lit.markdown(render_kpi_card(TXT_HOME['kpi_3'], formatted_kosten), unsafe_allow_html=True)

    with col_kpi4:
        str_lit.markdown(render_kpi_card(TXT_HOME['kpi_4'], formatted_einsparung, "#10b981"), unsafe_allow_html=True)

    str_lit.write("")
    
    # Zweispaltiges Layout: Links die Timeline, Rechts die Standort-Matrix & Quick Actions
    col_timeline, spacer, col_right = str_lit.columns([0.55, 0.05, 0.4])
    
    with col_timeline:
        str_lit.markdown(f"<div class='ent-section-title'>{TXT_HOME['timeline_title']}</div>", unsafe_allow_html=True)
        
        if not timeline_data:
            str_lit.markdown(f"<div class='timeline-text' style='opacity: 0.6;'>{TXT_HOME['no_critical']}</div>", unsafe_allow_html=True)
        else:
            tl_html = "<div class='timeline-container'>"
            for item in timeline_data:
                tl_html += f"<div class='timeline-item' style='{item['delay']}'><div class='timeline-dot-wrapper'><span class='{item['dot']}' style='margin-left:0;'></span></div><div class='timeline-date'>{item['datum']}</div><div class='timeline-text'>{item['anlage']}</div><div class='timeline-subtext'>{item['vertrag']}</div></div>"
            tl_html += "</div>"
            str_lit.markdown(tl_html, unsafe_allow_html=True)

        if location_data:
            summary_df = pd.DataFrame(location_data)
            summary_df = summary_df.rename(columns={
                'name': TXT_HOME['summary_loc'],
                'contracts': TXT_HOME['summary_contracts'],
                'alarms': TXT_HOME['summary_alarms']
            })
            str_lit.markdown(f"<div class='ent-section-title' style='margin-top: 30px;'>{TXT_HOME['summary_title']}</div>", unsafe_allow_html=True)
            str_lit.dataframe(summary_df[[TXT_HOME['summary_loc'], TXT_HOME['summary_contracts'], TXT_HOME['summary_alarms']]], use_container_width=True, hide_index=True)

    with col_right:
        str_lit.markdown(f"<div class='ent-section-title'>{TXT_HOME['location_title']}</div>", unsafe_allow_html=True)
        
        if not location_data:
            str_lit.markdown(f"<div class='timeline-text' style='opacity: 0.5;'>Keine Standortdaten verfügbar</div>", unsafe_allow_html=True)
        else:
            for item in location_data:
                alarm_dot = "micro-dot-red" if item["alarms"] > 0 else "micro-dot"
                alarm_color = "#ef4444" if item["alarms"] > 0 else "#64748b"
                loc_html = f"<div class='loc-row' style='{item['delay']}'><div class='loc-name'>{item['name']}</div><div class='loc-stats'><div class='loc-stat-item'>{item['contracts']} {TXT_HOME['loc_contracts']}</div><div class='loc-stat-item' style='color:{alarm_color};'>{item['alarms']} {TXT_HOME['loc_alarms']} <span class='{alarm_dot}'></span></div></div></div>"
                str_lit.markdown(loc_html, unsafe_allow_html=True)

        str_lit.markdown(f"<div class='ent-section-title' style='margin-top: 30px;'>{TXT_HOME['quick_title']}</div>", unsafe_allow_html=True)
        
        qc1, qc2, qc3 = str_lit.columns(3)
        with qc1:
            if str_lit.button("📊 Verträge", use_container_width=True):
                str_lit.session_state.app_ziel_seite = "Vertragsanalyse" if str_lit.session_state.language == "de" else "Contract Analysis"
                str_lit.session_state.app_seite_wechseln = True
                str_lit.rerun()
        with qc2:
            if str_lit.button("⏱️ Fristen", use_container_width=True):
                str_lit.session_state.app_ziel_seite = "Wartungsübersicht" if str_lit.session_state.language == "de" else "Maintenance Overview"
                str_lit.session_state.app_seite_wechseln = True
                str_lit.rerun()
        with qc3:
            if str_lit.button("🔧 Service", use_container_width=True):
                str_lit.session_state.app_ziel_seite = "Service" if str_lit.session_state.language == "de" else "Service"
                str_lit.session_state.app_seite_wechseln = True
                str_lit.rerun()