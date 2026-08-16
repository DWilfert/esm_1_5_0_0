import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from datenbank.befehle import hole_datenbank_verbindung, hole_wartungsvertraege_daten, hole_anlagen_daten, hole_firmen_daten
from logik.design import lade_design_farben
from logik.ui import render_page_header, render_section_header


def normalisiere_vertragsart(value):
    if value is None:
        return ""
    return str(value).strip()


def validiere_vertragsart(value, erlaubte_werte=None):
    text = normalisiere_vertragsart(value)
    if not text:
        return None

    if erlaubte_werte is None:
        return text

    erlaubte_werte_norm = {
        normalisiere_vertragsart(item).casefold()
        for item in erlaubte_werte
        if normalisiere_vertragsart(item)
    }

    for item in erlaubte_werte:
        if normalisiere_vertragsart(item).casefold() == text.casefold():
            return normalisiere_vertragsart(item)

    if text.casefold() in erlaubte_werte_norm:
        return text

    return None


def hole_reale_vertragsarten():
    return ["Vollwartung", "Wartungsvertrag", "Inspektion", "Basis-Wartung"]


def berechne_naechste_wartung(letzte_wartung, monate):
    if not letzte_wartung or monate <= 0:
        return None
    
    total_monate = letzte_wartung.month - 1 + monate
    neues_jahr = letzte_wartung.year + (total_monate // 12)
    neuer_monat = (total_monate % 12) + 1
    
    tage_im_monat = [31, 29 if neues_jahr % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    neuer_tag = min(letzte_wartung.day, tage_im_monat[neuer_monat - 1])
    
    return date(neues_jahr, neuer_monat, neuer_tag)

def zeige_vertragsanalyse(v_id_auswahl=""):
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
        .block-container { padding-top: 1.5rem !important; max-width: 1400px !important; }
        div[data-testid="InputInstructions"] { display: none !important; }
        .stTabs [data-baseweb="tab-list"] {
            gap: 20px; background-color: transparent; border-bottom: 1px solid var(--theme-border); padding-bottom: 0; margin-bottom: 25px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 45px; white-space: break-spaces; background-color: transparent; border-radius: 0; color: var(--theme-muted); font-size: 13px;
            font-weight: 500; text-transform: uppercase; letter-spacing: 1px; border: none !important; border-bottom: 2px solid transparent !important;
        }
        .stTabs [aria-selected="true"] { color: var(--theme-accent) !important; border-bottom: 2px solid var(--theme-accent) !important; }
        input, select, textarea, div[data-baseweb="select"] span {
            font-size: 13px !important; border-radius: 6px !important; border: 1px solid var(--theme-border) !important;
            background-color: var(--theme-input) !important; color: var(--theme-text) !important;
        }
        input:focus, div[data-baseweb="select"]:focus-within, textarea:focus { border-color: var(--theme-accent) !important; box-shadow: 0 0 0 1px var(--theme-accent) !important; }
        label { font-size: 11px !important; text-transform: uppercase; letter-spacing: 0.5px; color: var(--theme-muted) !important; font-weight: 600 !important; margin-bottom: 4px !important; }
        .stDataFrame { border: 1px solid var(--theme-border); border-radius: 6px; overflow: hidden; }
        div.stButton > button:first-child {
            background: linear-gradient(180deg, rgba(255,255,255,0.08) 0%, rgba(255,255,255,0.02) 100%); color: var(--theme-text); border: 1px solid var(--theme-border); border-radius: 8px; padding: 10px 24px; font-size: 13px; font-weight: 600;
            letter-spacing: 0.5px; text-transform: uppercase; transition: all 0.3s ease; box-shadow: 0 8px 20px rgba(2, 6, 23, 0.12);
        }
        div.stButton > button:first-child:hover { background: linear-gradient(180deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.04) 100%); border-color: var(--theme-accent); transform: translateY(-1px); }
        div.stButton > button[kind="secondary"] { background-color: transparent; color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); box-shadow: none; }
        div.stButton > button[kind="secondary"]:hover { background-color: rgba(239, 68, 68, 0.1); border-color: #ef4444; }
        .ent-subheader { font-size: 11px; font-weight: 500; color: var(--theme-muted); text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 30px; padding-bottom: 10px; border-bottom: 1px solid var(--theme-border); }
        .details-card { background: var(--theme-card); border: 1px solid var(--theme-border); border-radius: 10px; padding: 20px; margin-top: 15px; }
        .details-title { font-size: 14px; font-weight: 600; color: var(--theme-accent); margin-bottom: 15px; display: flex; align-items: center; }

        [data-testid="stMetricValue"] { font-size: 20px !important; font-weight: 300 !important; color: var(--theme-text) !important; }
        [data-testid="stMetricLabel"] { font-size: 11px !important; color: var(--theme-muted) !important; text-transform: uppercase; letter-spacing: 1px; }
        [data-testid="stMetricDelta"] { font-size: 12px !important; color: var(--theme-accent) !important; }

        .micro-dot {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .dot-red { background-color: #ef4444; }
        .dot-yellow { background-color: #f59e0b; }
        .dot-green { background-color: #10b981; }
        .readonly-box {
            background-color: rgba(148, 163, 184, 0.1);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 15px;
        }
        .readonly-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #94a3b8;
            font-weight: 600;
            margin-bottom: 4px;
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
    """
    css = css.replace("__BG_APP__", palette["bg_app"]) \
             .replace("__BG_SIDEBAR__", palette["bg_sidebar"]) \
             .replace("__CARD_BG__", palette["card_bg"]) \
             .replace("__BORDER_COLOR__", palette["border_color"]) \
             .replace("__TEXT_MAIN__", palette["text_main"]) \
             .replace("__TEXT_MUTED__", palette["text_muted"]) \
             .replace("__ACCENT_COLOR__", palette["accent_color"]) \
             .replace("__INPUT_BG__", palette["input_bg"])
    st.markdown(css, unsafe_allow_html=True)

    lang = st.session_state.get("language", "de")
    is_de = lang == "de"

    TXT = {
        "title": "Vertragsanalyse & Fristen-Controlling (Demo-Modus)" if is_de else "Contract Analysis & Deadline Controlling (Demo)",
        "sub": "Durchsucht den Demo-Datenbestand in Echtzeit." if is_de else "Searching the demo data asset in real time.",
        "tab_1": "Vertragsübersicht" if is_de else "Contract Overview",
        "tab_2": "Neuen Vertrag erfassen" if is_de else "Register New Contract",
        "tab_3": "Vertrag bearbeiten" if is_de else "Edit Contract",
        "search": "Schnell-Suche:" if is_de else "Quick Search:",
        "loc_filter": "Standort filtern:" if is_de else "Filter Location:",
        "no_data": "Keine Verträge gefunden." if is_de else "No contracts found.",
        "col_anl": "Anlage", "col_name": "Vertragsname", "col_firma": "Firma", "col_std": "Standort", 
        "col_kosten": "Kosten p.a.", "col_bench": "Bench p.a.", "col_einsp": "Einsparung",
        "col_naechste": "Nächste Wartung", "col_status": "Status",
        "status_ok": "Aktiv" if is_de else "Active", "status_warn": "Fällig" if is_de else "Due", "status_err": "Überfällig" if is_de else "Overdue",
        "action_title": "Vertrag wählen für Aktionen:" if is_de else "Select contract for actions:",
        "btn_delete": "Vertrag aus Demo-Daten löschen" if is_de else "Delete contract from demo data",
        "del_confirm": "Sicherheitsabfrage: Vertrag unwiderruflich löschen?" if is_de else "Security check: Delete contract irrevocably?",
        "btn_save": "Vertrag in Demo speichern" if is_de else "Save Contract to Demo",
        "btn_update": "Änderungen speichern" if is_de else "Save Changes",
        "msg_save_ok": "Neuer Vertrag erfolgreich registriert!" if is_de else "New contract successfully registered!",
        "msg_update_ok": "Vertrag erfolgreich aktualisiert!" if is_de else "Contract successfully updated!",
        "bitte_waehlen": "--- Bitte wählen ---" if is_de else "--- Please select ---",
        "kpi_total": "Gesamtbestand" if is_de else "Portfolio total",
        "kpi_benchmark": "Benchmark" if is_de else "Benchmark",
        "kpi_savings": "Einsparung" if is_de else "Savings",
        "kpi_contracts": "Verträge" if is_de else "Contracts",
        "summary_title": "Executive Contract Summary" if is_de else "Executive Contract Summary",
        "risk_loc": "Standort" if is_de else "Location",
        "risk_total": "Verträge" if is_de else "Contracts",
        "risk_status": "Status" if is_de else "Status"
    }

    render_page_header(TXT['title'], TXT['sub'])

    tab_bestand, tab_neu, tab_bearbeiten = st.tabs([TXT["tab_1"], TXT["tab_2"], TXT["tab_3"]])

    with tab_bestand:
        df = hole_wartungsvertraege_daten()
        if "anlage_name" not in df.columns:
            df["anlage_name"] = "Personenaufzug Hauptgebäude"
        if "firma_name" not in df.columns:
            df["firma_name"] = "Otis GmbH & Co. OHG"
        if "standort_text" not in df.columns:
            df["standort_text"] = "NP"

        opt_std_filter = {"NP": "NP - Neuperlach", "FG": "FG - Fasangarten"}

        if not df.empty:
            df['kosten_bestand_pa'] = pd.to_numeric(df['kosten_bestand_pa']).fillna(0.0)
            df['benchmark_ais_pa'] = pd.to_numeric(df['benchmark_ais_pa']).fillna(0.0)
            df['einsparung_eur'] = df['kosten_bestand_pa'] - df['benchmark_ais_pa']
            df['einsparung_pct'] = df.apply(lambda row: (row['einsparung_eur'] / row['kosten_bestand_pa'] * 100) if row['kosten_bestand_pa'] > 0 else 0.0, axis=1)

            t_bestand = df['kosten_bestand_pa'].sum()
            t_bench = df['benchmark_ais_pa'].sum()
            t_einsparung = t_bestand - t_bench
            t_einsparung_pct = (t_einsparung / t_bestand * 100) if t_bestand > 0 else 0.0

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.metric(label=TXT['kpi_total'], value=f"{t_bestand:,.2f} €".replace(',', '.'))
            with kpi2:
                st.metric(label=TXT['kpi_benchmark'], value=f"{t_bench:,.2f} €".replace(',', '.'))
            with kpi3:
                st.metric(
                    label=TXT['kpi_savings'], 
                    value=f"{t_einsparung:,.2f} €".replace(',', '.'), 
                    delta=f"{t_einsparung_pct:.2f} %",
                    delta_color="normal" if t_einsparung >= 0 else "inverse"
                )
            with kpi4:
                st.metric(label=TXT['kpi_contracts'], value=str(len(df)))

            st.write("")
            risk_df = df.copy()
            risk_df['naechste_wartung'] = pd.to_datetime(risk_df['naechste_wartung'], errors='coerce')
            risk_df['status'] = risk_df['naechste_wartung'].apply(lambda val: 'Überfällig' if pd.isna(val) or val < pd.Timestamp(datetime.now().date()) else ('Fällig' if val <= pd.Timestamp(datetime.now().date()) + pd.Timedelta(days=30) else 'Aktiv'))
            risk_summary = risk_df.groupby('standort_text', as_index=False).agg(
                vertrag_count=('id', 'count'),
                status=('status', lambda s: (s == 'Überfällig').sum())
            )
            risk_summary = risk_summary.rename(columns={
                'standort_text': TXT['risk_loc'],
                'vertrag_count': TXT['risk_total'],
                'status': TXT['risk_status']
            })
            st.markdown(f"#### {TXT['summary_title']}")
            st.dataframe(risk_summary, use_container_width=True, hide_index=True)

            st.write("---")

            c1, c2 = st.columns([0.7, 0.3])
            with c1:
                search_term = st.text_input(TXT["search"], key="v_search")
            with c2:
                f_opts = ["Beide"] + list(opt_std_filter.keys())
                loc_filter = st.selectbox(TXT["loc_filter"], f_opts, key="v_loc", format_func=lambda x: opt_std_filter.get(x, x))

            df_show = df.copy()
            if loc_filter != "Beide":
                df_show = df_show[df_show['standort_text'] == loc_filter]
            if search_term:
                st_l = search_term.lower()
                df_show = df_show[df_show.astype(str).apply(lambda x: x.str.lower().str.contains(st_l)).any(axis=1)]

            display_df = pd.DataFrame()
            if not df_show.empty:
                heute = pd.Timestamp(datetime.now().date())
                df_show['naechste_wartung'] = pd.to_datetime(df_show['naechste_wartung'], errors='coerce')
                
                def ermittle_status(val):
                    if pd.isna(val):
                        return TXT['status_ok']
                    if val < heute:
                        return TXT['status_err']
                    if val <= heute + pd.Timedelta(days=30):
                        return TXT['status_warn']
                    return TXT['status_ok']

                display_df[TXT["col_status"]] = df_show['naechste_wartung'].apply(ermittle_status)
                display_df[TXT["col_anl"]] = df_show['anlage_name']
                display_df[TXT["col_name"]] = df_show['vertragsname']
                display_df[TXT["col_firma"]] = df_show['firma_name']
                display_df[TXT["col_kosten"]] = df_show['kosten_bestand_pa'].map("{:,.2f} €".format).str.replace(',', '.')
                display_df[TXT["col_bench"]] = df_show['benchmark_ais_pa'].map("{:,.2f} €".format).str.replace(',', '.')
                display_df[TXT["col_einsp"]] = df_show['einsparung_eur'].map("{:,.2f} €".format).str.replace(',', '.')
                display_df[TXT["col_naechste"]] = df_show['naechste_wartung'].dt.strftime('%d.%m.%Y')
                
                def color_status(val):
                    if val == TXT['status_err']: return 'color: #ef4444; font-weight: bold;'
                    if val == TXT['status_warn']: return 'color: #f59e0b; font-weight: bold;'
                    if val == TXT['status_ok']: return 'color: #10b981;'
                    return ''
                
                styled_df = display_df.style.map(color_status, subset=[TXT["col_status"]])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
                
                st.write("")
                contract_mapping = {
                    row['id']: f"{row['vertragsname']} ({row['anlage_name']})"
                    for _, row in df_show.iterrows()
                }
                
                c_act1, _ = st.columns([0.4, 0.6])
                with c_act1:
                    e_id = st.selectbox(
                        TXT["action_title"],
                        options=[None] + list(contract_mapping.keys()),
                        format_func=lambda x: TXT["bitte_waehlen"] if x is None else contract_mapping[x]
                    )
                
                if e_id is not None:
                    row_data = df_show[df_show['id'] == e_id].iloc[0]
                    stat_val = ermittle_status(row_data['naechste_wartung'])
                    d_class = "dot-green"
                    if stat_val == TXT['status_err']: d_class = "dot-red"
                    elif stat_val == TXT['status_warn']: d_class = "dot-yellow"
                    
                    st.markdown(f"""
                    <div class="details-card">
                        <div class="details-title"><span class="micro-dot {d_class}"></span> Details zu Vertrag: {row_data['vertragsname']}</div>
                        <div style="font-size: 13px; color: #94a3b8; display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;">
                            <div><b>Firma:</b> {row_data['firma_name']}</div>
                            <div><b>Anlage:</b> {row_data['anlage_name']}</div>
                            <div><b>Standort:</b> {row_data['standort_text']}</div>
                            <div><b>Jahreskosten:</b> {row_data['kosten_bestand_pa']} €</div>
                            <div><b>Benchmark p.a.:</b> {row_data['benchmark_ais_pa']} €</div>
                            <div><b>Einsparung:</b> {row_data['einsparung_eur']} € ({row_data['einsparung_pct']:.2f}%)</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("")
                    if st.checkbox(TXT["del_confirm"]):
                        if st.button(TXT["btn_delete"], type="secondary"):
                            st.success("✅ [Demo-Modus] Vertrag erfolgreich simuliert gelöscht!")
                            st.rerun()
        else:
            st.info(TXT["no_data"])

    with tab_neu:
        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px;'>Neuen Vertrag erfassen (Demo-Modus)</div>", unsafe_allow_html=True)
        with st.form("neu_vertrag_form"):
            v_name = st.text_input("Vertragsname", key="neu_v_name")
            v_kosten = st.number_input("Kosten Bestand p.a. (€)", min_value=0.0, step=100.0, key="neu_v_kost")
            if st.form_submit_button(TXT["btn_save"], type="primary"):
                st.success(TXT["msg_save_ok"])

    with tab_bearbeiten:
        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px;'>Vertrag bearbeiten (Demo-Modus)</div>", unsafe_allow_html=True)
        with st.form("edit_vertrag_form"):
            st.text_input("Vertragsname anpassen", value="Demo-Wartung Aufzug")
            if st.form_submit_button(TXT["btn_update"], type="primary"):
                st.success(TXT["msg_update_ok"])