import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
from datenbank.befehle import hole_datenbank_verbindung
from logik.design import lade_design_farben
from logik.ui import prepare_display_dataframe, render_page_header, render_section_header


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
    conn = hole_datenbank_verbindung()
    if conn is None:
        return []

    try:
        c = conn.cursor(dictionary=True)
        c.execute(
            "SELECT DISTINCT TRIM(vertragsart) AS vertragsart FROM vertragsanalyse "
            "WHERE vertragsart IS NOT NULL AND TRIM(vertragsart) <> '' "
            "ORDER BY TRIM(vertragsart)"
        )
        return [
            str(row['vertragsart']).strip()
            for row in c.fetchall()
            if str(row['vertragsart']).strip()
        ]
    except Exception:
        return []
    finally:
        try:
            conn.close()
        except Exception:
            pass


def _wert_oder_fallback(*werte):
    for wert in werte:
        if wert is None:
            continue
        if isinstance(wert, str):
            wert = wert.strip()
            if not wert:
                continue
        return wert
    return ""


def lade_anlagen_optionen():
    conn = hole_datenbank_verbindung()
    if conn is None:
        return {}

    try:
        c = conn.cursor(dictionary=True)
        try:
            c.execute("SELECT * FROM anlagen ORDER BY id")
            rows = c.fetchall()
        except Exception:
            rows = []

        optionen = {}
        for row in rows:
            if not row:
                continue

            anlage_id = row.get("id")
            if anlage_id is None:
                continue

            bezeichnung = _wert_oder_fallback(row.get("anlagebezeichnung"), row.get("bezeichnung"), row.get("name"))
            standort = _wert_oder_fallback(row.get("standort_text"), row.get("standort"), row.get("ort_kurz"), row.get("ort"))
            kg_nr = _wert_oder_fallback(row.get("kg_nr"), row.get("kostengruppe_nr"))
            kg_txt = _wert_oder_fallback(row.get("kg_txt"), row.get("kostengruppe_txt"), row.get("kostengruppe"))
            ugew_nr = _wert_oder_fallback(row.get("unter_nr"), row.get("ugewerk_nr"))
            ugew_txt = _wert_oder_fallback(row.get("unter_txt"), row.get("ugewerk_txt"), row.get("untergewerk"))

            optionen[int(anlage_id)] = {
                "anzeige": f"{bezeichnung} ({standort})" if bezeichnung and standort else (bezeichnung or "Unbekannte Anlage"),
                "bezeichnung": bezeichnung or "-",
                "standort": standort or "-",
                "kg_nr": kg_nr or "-",
                "kg_txt": kg_txt or "-",
                "ugew_nr": ugew_nr or "-",
                "ugew_txt": ugew_txt or "-",
            }

        return optionen
    finally:
        try:
            conn.close()
        except Exception:
            pass


def berechne_naechste_wartung(letzte_wartung, monate):
    if not letzte_wartung or monate <= 0:
        return None
    
    total_monate = letzte_wartung.month - 1 + monate
    neues_jahr = letzte_wartung.year + (total_monate // 12)
    neuer_monat = (total_monate % 12) + 1
    
    tage_im_monat = [31, 29 if neues_jahr % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    neuer_tag = min(letzte_wartung.day, tage_im_monat[neuer_monat - 1])
    
    return date(neues_jahr, neues_monat, neuer_tag)

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
        "title": "Vertragsanalyse & Fristen-Controlling" if is_de else "Contract Analysis & Deadline Controlling",
        "sub": "Durchsucht den gesamten produktiven Datenbestand in Echtzeit aus der MySQL-Datenbank." if is_de else "Searching the entire productive data asset in real time from the MySQL database.",
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
        "btn_delete": "Vertrag aus MySQL löschen" if is_de else "Delete contract from MySQL",
        "del_confirm": "Sicherheitsabfrage: Vertrag unwiderruflich löschen?" if is_de else "Security check: Delete contract irrevocably?",
        "btn_save": "Vertrag in MySQL speichern" if is_de else "Save Contract to MySQL",
        "btn_update": "Änderungen in MySQL speichern" if is_de else "Save Changes to MySQL",
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
        conn = hole_datenbank_verbindung()
        df = pd.DataFrame()
        opt_std_filter = {}
        if conn:
            try:
                c_f = conn.cursor(dictionary=True)
                c_f.execute("SELECT ort_kurz, ort FROM standort")
                for r in c_f.fetchall():
                    opt_std_filter[r['ort_kurz']] = f"{r['ort_kurz']} - {r['ort']}"
                    
                q = """
                    SELECT 
                        v.*, a.anlagebezeichnung AS anlage_name, 
                        f.firmenname AS firma_name
                    FROM vertragsanalyse v
                    LEFT JOIN anlagen a ON v.anlage_id = a.id
                    LEFT JOIN firmeninfo f ON v.firma_id = f.id
                    ORDER BY v.naechste_wartung ASC
                """
                df = pd.read_sql(q, conn)
            except:
                pass
            finally:
                try:
                    conn.close()
                except:
                    pass

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
            st.dataframe(prepare_display_dataframe(risk_summary), use_container_width=True, hide_index=True)

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
                
                st.dataframe(prepare_display_dataframe(display_df).style.map(color_status, subset=[TXT["col_status"]]), use_container_width=True, hide_index=True)
                
                st.write("")
                c_act1, c_act2 = st.columns([0.4, 0.6])
                
                contract_mapping = {
                    row['id']: f"{row['vertragsname']} ({row['anlage_name']})"
                    for _, row in df_show.iterrows()
                }
                
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
                            conn_d = hole_datenbank_verbindung()
                            if conn_d:
                                try:
                                    c_d = conn_d.cursor()
                                    c_d.execute("DELETE FROM vertragsanalyse WHERE id = %s", (e_id,))
                                    conn_d.commit()
                                    st.success("Vertrag erfolgreich gelöscht!")
                                    st.rerun()
                                except:
                                    pass
                                finally:
                                    try:
                                        conn_d.close()
                                    except:
                                        pass
        else:
            st.info(TXT["no_data"])

    with tab_neu:
        opt_anlagen = lade_anlagen_optionen()
        opt_firmen = {}
        conn_dd = hole_datenbank_verbindung()
        if conn_dd:
            try:
                c_dd = conn_dd.cursor(dictionary=True)
                c_dd.execute("SELECT id, firmenname FROM firmeninfo")
                for row in c_dd.fetchall():
                    opt_firmen[row['id']] = f"{row['firmenname']}"
            except:
                pass
            finally:
                try:
                    conn_dd.close()
                except:
                    pass

        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px;'>Stammdaten & Verknüpfung</div>", unsafe_allow_html=True)
        
        c_f1, c_f2 = st.columns(2)
        
        with c_f1:
            anlagen_options = [None] + list(opt_anlagen.keys())
            v_anl_id = st.selectbox(
                "Anlage auswählen *", 
                options=anlagen_options, 
                format_func=lambda x: opt_anlagen[x]["anzeige"] if x else TXT["bitte_waehlen"]
            )
            
            anl_bez = "-"
            anl_std = "-"
            anl_kg = "-"
            anl_ugew = "-"
            
            if v_anl_id:
                sel_data = opt_anlagen[v_anl_id]
                anl_bez = sel_data['bezeichnung'] or "-"
                anl_std = sel_data['standort'] or "-"
                anl_kg = f"{sel_data['kg_nr']} - {sel_data['kg_txt']}" if sel_data['kg_nr'] else "-"
                anl_ugew = f"{sel_data['ugew_nr']} - {sel_data['ugew_txt']}" if sel_data['ugew_nr'] else "-"

            st.markdown(f"""
                <div class="readonly-label">Anlagenbezeichnung</div>
                <div class="readonly-box">{anl_bez}</div>
                <div class="readonly-label">Standort</div>
                <div class="readonly-box">{anl_std}</div>
                <div class="readonly-label">Kostengruppe (DIN 276)</div>
                <div class="readonly-box">{anl_kg}</div>
                <div class="readonly-label">Untergewerk</div>
                <div class="readonly-box">{anl_ugew}</div>
            """, unsafe_allow_html=True)
            
        with c_f2:
            firmen_options = [None] + list(opt_firmen.keys())
            v_firma = st.selectbox(
                "Firma / Auftragnehmer *", 
                options=firmen_options, 
                format_func=lambda x: opt_firmen[x] if x else TXT["bitte_waehlen"]
            )
            
            v_name = st.text_input("Vertragsname", key="neu_v_name")
            reale_vertragsarten = hole_reale_vertragsarten()
            if reale_vertragsarten:
                v_art = st.selectbox("Vertragsart", options=reale_vertragsarten, index=0, key="neu_v_art")
            else:
                st.warning("Es liegen noch keine realen Vertragsarten aus der MySQL-Datenbank vor. Bitte zuerst echte Werte in MySQL ergänzen.")
                v_art = ""
            
            col_clust_lbl, col_clust_info = st.columns([8.5, 1.5])
            with col_clust_lbl:
                v_clustering = st.text_input("Clustering", key="neu_v_clust")
            with col_clust_info:
                st.write("")
                with st.popover("ℹ️ Info", help="Clustering-Definitionen anzeigen"):
                    st.markdown("""
                        <div style='font-size: 0.8rem; line-height: 1.4;'>
                            <b>Clustering:</b><br><br>
                            <b>A:</b> Abweichungen zwischen Anlagenbestand, Verträgen und Wartungsprotokollen<br>
                            <b>B:</b> Unvollständige oder fehlende Wartungs- und Prüfprotokolle<br>
                            <b>C:</b> Abweichungen bei Wartungs- und Prüfintervallen<br>
                            <b>D:</b> Unklare Zuordnung von Anlagen zu Wartungsverträgen<br>
                            <b>E:</b> Mängel und technische Auffälligkeiten aus der Anlagenerfassung und Wartungsprotokollen
                        </div>
                    """, unsafe_allow_html=True)

            v_opt = st.text_input("Vertragsoptionen", key="neu_v_opt")

        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #0ea5e9; margin-top: 15px; margin-bottom: 15px;'>Kaufmännisch & Zyklen</div>", unsafe_allow_html=True)
        c_f3, c_f4 = st.columns(2)
        
        with c_f3:
            v_anzahl = st.number_input("Anzahl", min_value=1, step=1, value=1, key="neu_v_anz")
            v_kosten = st.number_input("Kosten Bestand p.a. (€)", min_value=0.0, step=100.0, key="neu_v_kost")
            v_bench_ep = st.number_input("Benchmark AIS EP (€)", min_value=0.0, step=100.0, key="neu_v_bench")
            v_zyklus_jahre = st.number_input("Zyklus (Jahre)", min_value=1, step=1, value=1, key="neu_v_zyk")
            v_zyklus_herst = st.text_input("Zyklus Herstellerempfehlung", key="neu_v_herst")
            v_grundlage = st.text_input("Wartungsgrundlage", key="neu_v_grund")
            
        with c_f4:
            v_letzte = st.date_input("Letzte Wartung", value=None, key="neu_v_letzte")
            v_naechste_pruef = st.date_input("Nächste Prüfung", value=date.today() + timedelta(days=365), key="neu_v_pruef")
            v_ende = st.date_input("Vertragsende", value=date.today() + timedelta(days=730), key="neu_v_ende")
            v_frist = st.text_input("Kündigungsfrist", key="neu_v_frist")
            st.write("")
            v_protokoll = st.checkbox("Protokoll vorhanden", key="neu_v_prot")

        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #0ea5e9; margin-top: 15px; margin-bottom: 15px;'>Dokumentation & Notizen</div>", unsafe_allow_html=True)
        v_hinweise = st.text_area("Hinweise", key="neu_v_hinw")
        v_anmerkung = st.text_area("Anmerkung", key="neu_v_anm")
        v_maengel = st.text_area("Mängelverfolgung", key="neu_v_maeng")

        st.write("")
        if st.button(TXT["btn_save"], type="primary"):
            if not v_anl_id or not v_firma:
                st.error("Bitte Anlage und Firma auswählen.")
            else:
                reale_vertragsarten = hole_reale_vertragsarten()
                validierte_v_art = validiere_vertragsart(v_art, reale_vertragsarten)
                if not reale_vertragsarten or validierte_v_art is None:
                    st.error("Nur reale Vertragsarten aus der MySQL-Datenbank sind erlaubt. Bitte einen vorhandenen Wert aus MySQL wählen.")
                else:
                    try:
                        sel_data = opt_anlagen[v_anl_id]
                        v_kg_nr = sel_data['kg_nr']
                        v_kg_bez = sel_data['kg_txt']
                        v_unter_nr = sel_data['ugew_nr']
                        v_unter_txt = sel_data['ugew_txt']
                        v_anl_bez_db = sel_data['bezeichnung']
                        v_std_db = sel_data['standort']
                        
                        berechnete_monate = int(v_zyklus_jahre * 12)
                        n_wart = berechne_naechste_wartung(v_letzte, berechnete_monate) if v_letzte else None
                        berechneter_bench_pa = v_anzahl * v_bench_ep
                        
                        protokoll_db_val = "ja" if v_protokoll else "nein"
                        
                        conn_i = hole_datenbank_verbindung()
                        if conn_i:
                            c_i = conn_i.cursor()
                            sql = """INSERT INTO vertragsanalyse 
                                     (anlage_id, kostengruppe_nr, kostengruppen_bez, ugewerk_nr, ugewerk_bez, anlagebezeichnung, standort_text, 
                                     anzahl, firma_id, vertragsname, vertragsart, vertragsende, kuendigungsfrist, 
                                     vertragsoptionen, kosten_bestand_pa, benchmark_ais_pa, wartungsgrundlage, 
                                     zyklus_jahre, zyklus_monate, zyklus_herstellerempfehlung, hinweise, 
                                     protokoll_vorhanden, letzte_wartung, naechste_wartung, naechste_pruefung, 
                                     anmerkung, maengelverfolgung, clustering) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                            c_i.execute(sql, (
                                v_anl_id, v_kg_nr, v_kg_bez, v_unter_nr, v_unter_txt, v_anl_bez_db, v_std_db, 
                                v_anzahl, v_firma, v_name, validierte_v_art, v_ende, v_frist, 
                                v_opt, v_kosten, berechneter_bench_pa, v_grundlage, 
                                v_zyklus_jahre, berechnete_monate, v_zyklus_herst, v_hinweise, 
                                protokoll_db_val, v_letzte, n_wart, v_naechste_pruef, 
                                v_anmerkung, v_maengel, v_clustering
                            ))
                            conn_i.commit()
                            st.success(TXT["msg_save_ok"])
                    except Exception as e:
                        st.error(f"System-Fehler beim Speichern: {e}")
                    finally:
                        if 'conn_i' in locals() and conn_i:
                            try:
                                conn_i.close()
                            except:
                                pass

    with tab_bearbeiten:
        conn_ed = hole_datenbank_verbindung()
        df_edit_opt = pd.DataFrame()
        opt_firmen_edit = {}
        if conn_ed:
            try:
                c_ed = conn_ed.cursor(dictionary=True)
                c_ed.execute("SELECT id, firmenname FROM firmeninfo")
                for r in c_ed.fetchall():
                    opt_firmen_edit[r['id']] = r['firmenname']
                    
                df_edit_opt = pd.read_sql("SELECT v.id, v.vertragsname, a.anlagebezeichnung FROM vertragsanalyse v LEFT JOIN anlagen a ON v.anlage_id = a.id", conn_ed)
            except:
                pass
            finally:
                try:
                    conn_ed.close()
                except:
                    pass

        if not df_edit_opt.empty:
            edit_mapping = {
                row['id']: f"{row['vertragsname']} ({row['anlagebezeichnung']})"
                for _, row in df_edit_opt.iterrows()
            }
            
            sel_edit_id = st.selectbox(
                TXT["action_title"],
                options=[None] + list(edit_mapping.keys()),
                format_func=lambda x: TXT["bitte_waehlen"] if x is None else edit_mapping[x],
                key="edit_vertrag_selectbox"
            )
            
            if sel_edit_id is not None:
                conn_det = hole_datenbank_verbindung()
                vertrag_dat = {}
                if conn_det:
                    try:
                        c_det = conn_det.cursor(dictionary=True)
                        c_det.execute("SELECT * FROM vertragsanalyse WHERE id = %s", (sel_edit_id,))
                        vertrag_dat = c_det.fetchone() or {}
                    except:
                        pass
                    finally:
                        try:
                            conn_det.close()
                        except:
                            pass
                
                if vertrag_dat:
                    st.write("")
                    with st.form(f"form_edit_vertrag_{sel_edit_id}"):
                        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px;'>Vertragsdaten bearbeiten</div>", unsafe_allow_html=True)
                        
                        ce1, ce2 = st.columns(2)
                        with ce1:
                            up_v_name = st.text_input("Vertragsname", value=str(vertrag_dat.get('vertragsname', '')))
                            reale_vertragsarten_edit = hole_reale_vertragsarten()
                            if reale_vertragsarten_edit:
                                current_vertragsart = validiere_vertragsart(vertrag_dat.get('vertragsart'), reale_vertragsarten_edit) or reale_vertragsarten_edit[0]
                                up_v_art = st.selectbox(
                                    "Vertragsart",
                                    options=reale_vertragsarten_edit,
                                    index=reale_vertragsarten_edit.index(current_vertragsart),
                                    key="edit_v_art"
                                )
                            else:
                                st.warning("Es liegen noch keine realen Vertragsarten aus der MySQL-Datenbank vor.")
                                up_v_art = ""
                            up_v_clust = st.text_input("Clustering", value=str(vertrag_dat.get('clustering', '')))
                            up_v_opt = st.text_input("Vertragsoptionen", value=str(vertrag_dat.get('vertragsoptionen', '')))
                            up_v_kosten = st.number_input("Kosten Bestand p.a. (€)", min_value=0.0, step=100.0, value=float(vertrag_dat.get('kosten_bestand_pa') or 0.0))
                            up_v_bench_ep = st.number_input("Benchmark AIS EP (€)", min_value=0.0, step=100.0, value=float(vertrag_dat.get('benchmark_ais_pa') or 0.0))
                        with ce2:
                            up_v_anz = st.number_input("Anzahl", min_value=1, step=1, value=int(vertrag_dat.get('anzahl') or 1))
                            up_v_zyk = st.number_input("Zyklus (Jahre)", min_value=1, step=1, value=int(vertrag_dat.get('zyklus_jahre') or 1))
                            up_v_grund = st.text_input("Wartungsgrundlage", value=str(vertrag_dat.get('wartungsgrundlage', '')))
                            up_v_frist = st.text_input("Kündigungsfrist", value=str(vertrag_dat.get('kuendigungsfrist', '')))
                            
                            alt_letzte = vertrag_dat.get('letzte_wartung')
                            val_letzte = alt_letzte if isinstance(alt_letzte, date) else None
                            up_v_letzte = st.date_input("Letzte Wartung", value=val_letzte)

                        st.write("")
                        if st.form_submit_button(TXT["btn_update"], type="primary"):
                            reale_vertragsarten_edit = hole_reale_vertragsarten()
                            validierte_up_v_art = validiere_vertragsart(up_v_art, reale_vertragsarten_edit)
                            if not reale_vertragsarten_edit or validierte_up_v_art is None:
                                st.error("Nur reale Vertragsarten aus der MySQL-Datenbank sind erlaubt. Bitte einen vorhandenen Wert aus MySQL wählen.")
                            else:
                                try:
                                    ber_monate = int(up_v_zyk * 12)
                                    neue_n_wart = berechne_naechste_wartung(up_v_letzte, ber_monate) if up_v_letzte else vertrag_dat.get('naechste_wartung')
                                    ber_bench_pa = up_v_anz * up_v_bench_ep
                                   
                                    conn_updt = hole_datenbank_verbindung()
                                    if conn_updt:
                                        cur_u = conn_updt.cursor()
                                        sql_u = """UPDATE vertragsanalyse SET 
                                                  vertragsname = %s, vertragsart = %s, clustering = %s, vertragsoptionen = %s, 
                                                  kosten_bestand_pa = %s, benchmark_ais_pa = %s, anzahl = %s, zyklus_jahre = %s, 
                                                  zyklus_monate = %s, wartungsgrundlage = %s, kuendigungsfrist = %s, 
                                                  letzte_wartung = %s, naechste_wartung = %s WHERE id = %s"""
                                        cur_u.execute(sql_u, (
                                            up_v_name, validierte_up_v_art, up_v_clust, up_v_opt, up_v_kosten, ber_bench_pa, 
                                            up_v_anz, up_v_zyk, ber_monate, up_v_grund, up_v_frist, 
                                            up_v_letzte, neue_n_wart, sel_edit_id
                                        ))
                                        conn_updt.commit()
                                        st.success(TXT["msg_update_ok"])
                                        st.rerun()
                                except Exception as e:
                                    st.error(f"Fehler beim Aktualisieren: {e}")
        else:
            st.info(TXT["no_data"])