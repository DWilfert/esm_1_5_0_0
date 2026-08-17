import streamlit as st
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import prepare_display_dataframe, standort_code_from_display, standort_display_name, render_page_header, render_section_header
@st.dialog("Anlage bearbeiten")
def anlage_bearbeiten_dialog(sel_id, row_det, txt):
    conn_opt = hole_datenbank_verbindung()
    opt_std, opt_kg, opt_ugew = {}, {}, {}
    if conn_opt:
        try:
            c_opt = conn_opt.cursor(dictionary=True)
            c_opt.execute("SELECT id, ort_kurz, ort FROM standort")
            for r in c_opt.fetchall():
                opt_std[r['id']] = f"{r['ort_kurz']} - {r['ort']}"
            
            c_opt.execute("SELECT kg_nr, kg_txt FROM kostengruppen")
            for r in c_opt.fetchall():
                opt_kg[r['kg_nr']] = f"{r['kg_nr']} - {r['kg_txt']}"

            c_opt.execute("SELECT unter_nr, unter_txt FROM untergewerk")
            for r in c_opt.fetchall():
                opt_ugew[r['unter_nr']] = f"{r['unter_nr']} - {r['unter_txt']}"
        except:
            pass
        finally:
            conn_opt.close()

    with st.form(f"form_edit_anl_modal_{sel_id}"):
        f_aname = st.text_input(txt["lbl_aname"], value=str(row_det.get('anlagebezeichnung', '')))
        f_atyp = st.text_input(txt["lbl_atyp"], value=str(row_det.get('anlagetyp', '')))
        f_herst = st.text_input(txt["lbl_herst"], value=str(row_det.get('hersteller', '')))
        f_typ = st.text_input(txt["lbl_typ"], value=str(row_det.get('typ', '')))
        f_sn = st.text_input(txt["lbl_sn"], value=str(row_det.get('seriennummer', '')))
        f_zustand = st.text_input(txt["lbl_zustand"], value=str(row_det.get('zustand', '')))
        f_beschr = st.text_area(txt["lbl_beschr"], value=str(row_det.get('beschreibung', '')))

        st.write("")
        if st.form_submit_button(txt["btn_save"], type="primary"):
            conn_up = hole_datenbank_verbindung()
            if conn_up:
                cur = None
                try:
                    cur = conn_up.cursor()
                    sql = """UPDATE anlagen SET anlagebezeichnung = %s, anlagetyp = %s, hersteller = %s, 
                             typ = %s, seriennummer = %s, zustand = %s, beschreibung = %s WHERE id = %s"""
                    cur.execute(sql, (f_aname, f_atyp, f_herst, f_typ, f_sn, f_zustand, f_beschr, sel_id))
                    conn_up.commit()
                    st.success(txt["success_upd"])
                    st.rerun()
                except Exception as e:
                    st.error(f"Fehler beim Speichern in MySQL: {e}")
                finally:
                    if cur:
                        try:
                            cur.close()
                        except:
                            pass
                    if conn_up:
                        try:
                            conn_up.close()
                        except:
                            pass

def zeige_anlagenstruktur():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] {
            display: none !important;
        }
        input::placeholder, textarea::placeholder {
            color: #94a3b8 !important;
            font-style: italic !important;
            opacity: 1 !important;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.25) !important;
            border-radius: 0.5rem;
            padding: 4px;
        }
        .micro-dot {
            height: 8px;
            width: 8px;
            border-radius: 50%;
            display: inline-block;
        }
        .dot-red { background-color: #ef4444; }
        .dot-yellow { background-color: #f59e0b; }
        .dot-green { background-color: #10b981; }
        .ent-subheader { font-size: 14px; font-weight: 600; color: #0ea5e9; margin-bottom: 15px; margin-top: 15px; }
        
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

    lang = st.session_state.get("language", "de")
    
    txt = {
        "de": {
            "titel": "Anlagenstruktur",
            "btn_toggle": "Endlosliste & Neuerfassung umschalten",
            "filter_std": "Standort filtern:",
            "beide": "Beide",
            "suche": "Echtzeit-Suche:",
            "sel_anlage": "Anlage wählen für Details:",
            "btn_edit": "✏️ Anlage bearbeiten",
            "zustandampel": "Zustandsampel:",
            "kpi_total": "Gesamtanlagen",
            "kpi_health": "Assets fit",
            "kpi_risk": "Kritische Anlagen",
            "kpi_locations": "Standorte",
            "summary_title": "Executive Asset Summary",
            "risk_loc": "Standort",
            "risk_count": "Anlagen",
            "risk_status": "Status",
            "filter_location": "Standort filtern:",
            "tabs": ["Basis", "Technik", "Ort", "Historie"],
            "basis": {"art": "Anlagenart", "bauteil": "Bauteil-Anlage", "untergewerk": "Untergewerk", "aks": "AKS-Bezeichnung", "din": "DIN 276", "beschr": "Beschreibung"},
            "technik": {"herst": "Hersteller", "typ": "Modell / Typ", "sn": "Seriennummer", "bj": "Baujahr", "ld": "Lebensdauer / -ende"},
            "ort": {"gteil": "Gebäudeteil", "etage": "Etage", "raum": "Raum / -bez."},
            "edit_bez": "Bezeichnung",
            "edit_zustand": "Zustand",
            "btn_save": "Änderungen speichern",
            "success_upd": "Änderungen direkt in MySQL gespeichert!",
            "btn_back": "Zurück zur kaufmännischen Vertragsanalyse",
            "new_titel": "Neue Anlage erfassen",
            "sec1": "1. Basisdaten & Klassifizierung",
            "sec2": "2. Technische Daten & Lifecycle",
            "sec3": "3. Räumliche Zuordnung & Standort",
            "sec4": "4. Beschreibung & Kennzeichnung",
            "lbl_std": "Standort *",
            "lbl_aid": "Anlagen-Nummer (Anlagen-ID) *",
            "lbl_aname": "Anlagenbezeichnung *",
            "lbl_atyp": "Anlagentyp",
            "lbl_bauteil": "Bauteil-Anlage",
            "lbl_ugew": "Untergewerk",
            "lbl_aks": "AKS-Bezeichnung",
            "lbl_din": "Kostengruppe (DIN 276)",
            "lbl_anz": "Anzahl",
            "lbl_herst": "Hersteller",
            "lbl_typ": "Typ / Modell",
            "lbl_sn": "Seriennummer",
            "lbl_bj": "Baujahr",
            "lbl_ld": "Lebensdauer",
            "lbl_le": "Lebensende",
            "lbl_zustand": "Zustand",
            "lbl_gteil": "Gebäudeteil",
            "lbl_etage": "Etage",
            "lbl_raum": "Raum",
            "lbl_rbez": "Raumbezeichnung",
            "lbl_beschr": "Beschreibung der Anlage",
            "btn_reg": "Anlage in MySQL speichern",
            "success_reg": "Anlage erfolgreich in der MySQL-Datenbank gespeichert!",
            "bitte_waehlen": "--- Bitte wählen ---",
            "keine_hist": "Keine Historie in MySQL gefunden.",
            "err_hist": "Fehler beim Laden der Historie.",
            "err_req": "Bitte füllen Sie mindestens Standort, Anlagen-Nummer und Anlagenbezeichnung aus."
        },
        "en": {
            "titel": "Asset Structure",
            "btn_toggle": "Toggle List & Registration",
            "filter_std": "Filter Location:",
            "beide": "Both",
            "suche": "Real-time Search:",
            "sel_anlage": "Select Asset for Details:",
            "btn_edit": "✏️ Edit Asset",
            "zustandampel": "Condition Traffic Light:",
            "kpi_total": "Total assets",
            "kpi_health": "Healthy assets",
            "kpi_risk": "Critical assets",
            "kpi_locations": "Locations",
            "summary_title": "Executive Asset Summary",
            "risk_loc": "Location",
            "risk_count": "Assets",
            "risk_status": "Status",
            "filter_location": "Filter location:",
            "tabs": ["Basic", "Tech", "Location", "History"],
            "basis": {"art": "Asset Type", "bauteil": "Component Asset", "untergewerk": "Sub-Trade", "aks": "AKS Designation", "din": "DIN 276", "beschr": "Description"},
            "technik": {"herst": "Manufacturer", "typ": "Model / Type", "sn": "Serial Number", "bj": "Year of Construction", "ld": "Lifespan / End"},
            "ort": {"gteil": "Building Section", "etage": "Floor", "raum": "Room / Descr."},
            "edit_bez": "Designation",
            "edit_zustand": "Condition",
            "btn_save": "Save Changes",
            "success_upd": "Changes saved directly to MySQL!",
            "btn_back": "Back to Commercial Contract Analysis",
            "new_titel": "Register New Asset",
            "sec1": "1. Basic Data & Classification",
            "sec2": "2. Technical Data & Lifecycle",
            "sec3": "3. Spatial Allocation & Location",
            "sec4": "4. Description & Identification",
            "lbl_std": "Location *",
            "lbl_aid": "Asset Number *",
            "lbl_aname": "Asset Name *",
            "lbl_atyp": "Asset Type",
            "lbl_bauteil": "Component",
            "lbl_ugew": "Sub-Trade",
            "lbl_aks": "AKS Designation",
            "lbl_din": "Cost Group (DIN 276)",
            "lbl_anz": "Quantity",
            "lbl_herst": "Manufacturer",
            "lbl_typ": "Model / Type",
            "lbl_sn": "Serial Number",
            "lbl_bj": "Year of Construction",
            "lbl_ld": "Lifespan",
            "lbl_le": "End of Life",
            "lbl_zustand": "Condition",
            "lbl_gteil": "Building Section",
            "lbl_etage": "Floor",
            "lbl_raum": "Room",
            "lbl_rbez": "Room Designation",
            "lbl_beschr": "Asset Description",
            "btn_reg": "Save Asset in MySQL",
            "success_reg": "Asset successfully saved in the MySQL database!",
            "bitte_waehlen": "--- Please select ---",
            "keine_hist": "No history found in MySQL.",
            "err_hist": "Error loading history.",
            "err_req": "Please fill out at least Location, Asset Number and Asset Name."
        }
    }[lang]

    render_page_header(txt['titel'])
    if "ziel_vertrags_id" in st.session_state and st.session_state.ziel_vertrags_id is not None:
        st.session_state.showendlos = True

    conn = hole_datenbank_verbindung()
    df_anlagen = pd.DataFrame()
    if conn is not None:
        try:
            df_anlagen = pd.read_sql("""
                SELECT a.*, s.ort_kurz AS standort 
                FROM anlagen a 
                LEFT JOIN standort s ON a.standort_id = s.id
            """, conn)
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except:
                pass
        
    if "showendlos" not in st.session_state:
        st.session_state.showendlos = False
        
    if st.button(txt["btn_toggle"], key="anl_toggle_btn_main"):
        st.session_state.showendlos = not st.session_state.showendlos
        if "ziel_vertrags_id" in st.session_state:
            st.session_state.ziel_vertrags_id = None
        st.rerun()

    if st.session_state.showendlos and not df_anlagen.empty:
        df_anlagen_work = df_anlagen.copy()
        df_anlagen_work["zustand"] = df_anlagen_work["zustand"].fillna("").astype(str)

        standorte = sorted(df_anlagen_work['standort'].dropna().astype(str).unique().tolist())
        standort_options = [standort_display_name(s) for s in standorte]
        selected_standorte_labels = st.multiselect(
            txt['filter_location'],
            standort_options,
            default=standort_options,
            key='anlagen_standort_filter'
        )
        if selected_standorte_labels:
            selected_standorte_codes = [standort_code_from_display(v) for v in selected_standorte_labels]
            df_anlagen_work = df_anlagen_work[df_anlagen_work['standort'].astype(str).str.upper().isin(selected_standorte_codes)].copy()

        total_assets = len(df_anlagen_work)
        healthy_assets = (df_anlagen_work['zustand'].str.lower().str.contains('betriebsbereit|bereit|ok', regex=True, na=False)).sum()
        critical_assets = (df_anlagen_work['zustand'].str.lower().str.contains('defekt|fehler|ausfall|kritisch', regex=True, na=False)).sum()
        locations = df_anlagen_work['standort'].nunique()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric(txt['kpi_total'], total_assets)
        with kpi2:
            st.metric(txt['kpi_health'], healthy_assets)
        with kpi3:
            st.metric(txt['kpi_risk'], critical_assets)
        with kpi4:
            st.metric(txt['kpi_locations'], locations)

        st.write("")
        risco_df = df_anlagen_work.groupby('standort', as_index=False).agg(
            anlagen=('id', 'count'),
            status=('zustand', lambda s: (s.str.lower().str.contains('defekt|fehler|ausfall|kritisch', regex=True, na=False)).sum())
        )
        risco_df = risco_df.rename(columns={
            'standort': txt['risk_loc'],
            'anlagen': txt['risk_count'],
            'status': txt['risk_status']
        })
        st.markdown(f"#### {txt['summary_title']}")
        st.dataframe(prepare_display_dataframe(risco_df), use_container_width=True, hide_index=True)

        st.write("")
        col_filt, col_src = st.columns([4.0, 6.0])
        with col_filt: 
            anl_filter_label = st.radio(txt["filter_std"], [txt["beide"], "Neuperlach (NP)", "Fasangarten (FG)"], horizontal=True, key="anl_std_filter_v7")
        with col_src: 
            anl_suche = st.text_input(txt["suche"], autocomplete="off", key="anl_src_input_v7")

        df_endlos = df_anlagen_work.copy()
        if anl_filter_label != txt["beide"]: 
            anl_filter = standort_code_from_display(anl_filter_label)
            df_endlos = df_endlos[df_endlos["standort"].astype(str).str.upper() == anl_filter]
        if anl_suche:
            s_l = anl_suche.lower()
            df_endlos = df_endlos[df_endlos["anlagebezeichnung"].str.lower().str.contains(s_l, na=False)]
        
        verfuegbare_spalten = [col for col in ["standort", "anlagenr", "anlagebezeichnung", "hersteller", "typ", "zustand"] if col in df_endlos.columns]
        st.dataframe(prepare_display_dataframe(df_endlos[verfuegbare_spalten]), use_container_width=True, hide_index=True)

        anlagen_mapping = {
            row["id"]: f"{row['anlagebezeichnung']} (Nr: {row['anlagenr']})" if pd.notna(row['anlagenr']) else str(row['anlagebezeichnung'])
            for _, row in df_endlos.iterrows()
        }
        id_liste = [None] + list(anlagen_mapping.keys())
        vorauswahl_index = 0
        
        if "ziel_vertrags_id" in st.session_state and st.session_state.ziel_vertrags_id is not None:
            gesuchte_id = st.session_state.ziel_vertrags_id
            if gesuchte_id in id_liste:
                vorauswahl_index = id_liste.index(gesuchte_id)

        col_sel_box, col_edit_btn = st.columns([5.0, 5.0])
        with col_sel_box:
            sel_id = st.selectbox(
                txt["sel_anlage"], 
                options=id_liste, 
                index=vorauswahl_index, 
                format_func=lambda x: txt["bitte_waehlen"] if x is None else anlagen_mapping[x],
                key="anl_sel_id_dropdown_v7"
            )
        
        if sel_id is not None:
            df_target = df_endlos[df_endlos["id"] == sel_id]
            if not df_target.empty:
                row_det = df_target.iloc[0].to_dict()
                
                with col_edit_btn:
                    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)
                    if st.button(txt["btn_edit"], key=f"btn_open_edit_anl_{sel_id}", help="Ausgewählte Anlage bearbeiten"):
                        anlage_bearbeiten_dialog(sel_id, row_det, txt)

                zustand_str = str(row_det.get('zustand', '')).lower()
                d_class = "dot-green" if "betriebsbereit" in zustand_str else "dot-red"
                
                st.markdown(f"<div style='display:flex; align-items:center; margin-bottom: 15px;'><b>{txt['zustandampel']}</b> <span class='micro-dot {d_class}' style='margin-left:8px; margin-right:8px;'></span> {row_det.get('zustand', '-')}</div>", unsafe_allow_html=True)
                
                t1, t2, t3, t4 = st.tabs(txt["tabs"])
                with t1:
                    st.write(f"**{txt['basis']['art']}:** {row_det.get('anlagetyp', '-')}")
                    st.write(f"**{txt['basis']['bauteil']}:** {row_det.get('anlagebauteil', '-')}")
                    st.write(f"**{txt['basis']['untergewerk']}:** {row_det.get('ugewerk_bez', '-')}")
                    st.write(f"**{txt['basis']['aks']}:** {row_det.get('aks_Bez.', '-')}")
                    st.write(f"**DIN 276:** {row_det.get('kostengruppe_nr', '-')}")
                    st.write(f"**{txt['basis']['beschr']}:** {row_det.get('beschreibung', '-')}")
                with t2:
                    st.write(f"**{txt['technik']['herst']}:** {row_det.get('hersteller', '-')}")
                    st.write(f"**{txt['technik']['typ']}:** {row_det.get('typ', '-')}")
                    st.write(f"**{txt['technik']['sn']}:** {row_det.get('seriennummer', '-')}")
                    st.write(f"**{txt['technik']['bj']}:** {row_det.get('baujahr', '-')}")
                    st.write(f"**{txt['technik']['ld']}:** {row_det.get('lebensdauer', '-')} / {row_det.get('lebensende', '-')}")
                with t3:
                    st.write(f"**{txt['ort']['gteil']}:** {row_det.get('gebaudeteil', '-')}")
                    st.write(f"**{txt['ort']['etage']}:** {row_det.get('etage', '-')}")
                    st.write(f"**{txt['ort']['raum']}:** {row_det.get('raum', '-')} ({row_det.get('raumbezeichnung', '-')})")
                with t4:
                    conn_h = hole_datenbank_verbindung()
                    if conn_h:
                        try:
                            df_hist = pd.read_sql("SELECT vertrag AS 'Vertrag', kommentar AS 'Kommentar', protokolldatei AS 'Hinweis' FROM auffaelligkeiten WHERE anlage_id = ?", conn_h, params=(sel_id,))
                            if not df_hist.empty:
                                st.dataframe(prepare_display_dataframe(df_hist), use_container_width=True, hide_index=True)
                            else:
                                st.info(txt["keine_hist"])
                        except Exception:
                            st.info(txt["err_hist"])
                        finally:
                            try:
                                conn_h.close()
                            except:
                                pass
                
                st.markdown("---")
                col_back, _ = st.columns([4.0, 6.0])
                with col_back:
                    if st.button(txt["btn_back"], key="anl_btn_back_to_va", use_container_width=True):
                        st.session_state.app_ziel_seite = "Vertragsanalyse" if lang == "de" else "Contract Analysis"
                        st.session_state.app_seite_wechseln = True
                        st.rerun()
                st.write("---")
                
        if "ziel_vertrags_id" in st.session_state and st.session_state.ziel_vertrags_id is not None:
            st.session_state.ziel_vertrags_id = None

    else:
        st.markdown(f"<div style='font-size: 20px; font-weight: 300; margin-bottom: 15px;'>{txt['new_titel']}</div>", unsafe_allow_html=True)
        
        opt_std, opt_kg, opt_ugew = {}, {}, {}
        conn_opt = hole_datenbank_verbindung()
        if conn_opt:
            try:
                c_opt = conn_opt.cursor(dictionary=True)
                c_opt.execute("SELECT id, ort_kurz, ort FROM standort")
                for r in c_opt.fetchall():
                    opt_std[r['id']] = f"{r['ort_kurz']} - {r['ort']}"
                
                c_opt.execute("SELECT kg_nr, kg_txt FROM kostengruppen")
                for r in c_opt.fetchall():
                    opt_kg[r['kg_nr']] = f"{r['kg_nr']} - {r['kg_txt']}"

                c_opt.execute("SELECT unter_nr, unter_txt FROM untergewerk")
                for r in c_opt.fetchall():
                    opt_ugew[r['unter_nr']] = f"{r['unter_nr']} - {r['unter_txt']}"
            except:
                pass
            finally:
                conn_opt.close()

        with st.form("anl_form_n_vollstaendig_v2", clear_on_submit=True):
            
            st.markdown(f"<div class='ent-subheader'>{txt['sec1']}</div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1: f_std = st.selectbox(txt["lbl_std"], options=[None] + list(opt_std.keys()), format_func=lambda x: opt_std.get(x, "") if x else txt["bitte_waehlen"], key="f_std")
            with c2: f_aid = st.text_input(txt["lbl_aid"], placeholder="z. B. 17501", key="f_aid")
            with c3: f_aname = st.text_input(txt["lbl_aname"], placeholder="z. B. Personenaufzug A", key="f_aname")
            with c4: f_atyp = st.text_input(txt["lbl_atyp"], placeholder="z. B. Fördertechnik", key="f_atyp")

            c5, c6, c7, c8 = st.columns(4)
            with c5: f_bauteil = st.text_input(txt["lbl_bauteil"], placeholder="z. B. 1", key="f_bauteil")
            with c6: f_ugew = st.selectbox(txt["lbl_ugew"], options=[None] + list(opt_ugew.keys()), format_func=lambda x: opt_ugew.get(x, "") if x else txt["bitte_waehlen"], key="f_ugew")
            with c7: f_aks = st.text_input(txt["lbl_aks"], placeholder="z. B. AK-10", key="f_aks")
            with c8: f_din = st.selectbox(txt["lbl_din"], options=[None] + list(opt_kg.keys()), format_func=lambda x: opt_kg.get(x, "") if x else txt["bitte_waehlen"], key="f_din")

            st.markdown(f"<div class='ent-subheader'>{txt['sec2']}</div>", unsafe_allow_html=True)
            col_b1, col_b2, col_b3, col_b4 = st.columns(4)
            with col_b1: f_herst = st.text_input(txt["lbl_herst"], placeholder="z. B. Otis GmbH", key="f_herst")
            with col_b2: f_typ = st.text_input(txt["lbl_typ"], placeholder="z. B. Gen2", key="f_typ")
            with col_b3: f_sn = st.text_input(txt["lbl_sn"], placeholder="SN-12345", key="f_sn")
            with col_b4: f_bj = st.text_input(txt["lbl_bj"], placeholder="z. B. 2020", key="f_bj")

            col_b5, col_b6, col_b7, col_b8 = st.columns(4)
            with col_b5: f_anz = st.text_input(txt["lbl_anz"], placeholder="1", key="f_anz")
            with col_b6: f_ld = st.text_input(txt["lbl_ld"], placeholder="z. B. 20 Jahre", key="f_ld")
            with col_b7: f_le = st.text_input(txt["lbl_le"], placeholder="z. B. 2040", key="f_le")
            with col_b8: f_zustand = st.text_input(txt["lbl_zustand"], placeholder="Betriebsbereit", key="f_zustand")

            st.markdown(f"<div class='ent-subheader'>{txt['sec3']}</div>", unsafe_allow_html=True)
            col_o1, col_o2, col_o3, col_o4 = st.columns(4)
            with col_o1: f_gteil = st.text_input(txt["lbl_gteil"], placeholder="z. B. Hauptgebäude", key="f_gteil")
            with col_o2: f_etage = st.text_input(txt["lbl_etage"], placeholder="z. B. EG", key="f_etage")
            with col_o3: f_raum = st.text_input(txt["lbl_raum"], placeholder="z. B. R-012", key="f_raum")
            with col_o4: f_rbez = st.text_input(txt["lbl_rbez"], placeholder="z. B. Technikraum", key="f_rbez")

            st.markdown(f"<div class='ent-subheader'>{txt['sec4']}</div>", unsafe_allow_html=True)
            f_beschr = st.text_area(txt["lbl_beschr"], placeholder="Detaillierte Funktionsbeschreibung...", height=70, key="f_beschr")

            st.write("")
            if st.form_submit_button(txt["btn_reg"], type="primary"):
                if f_aid and f_aname and f_std:
                    conn_ins = hole_datenbank_verbindung()
                    if conn_ins:
                        cur = None
                        try:
                            cur = conn_ins.cursor()
                            
                            sql = """INSERT INTO anlagen 
                                     (anlagenr, anlagebezeichnung, anlagetyp, anlagebauteil, hersteller, typ, seriennummer, baujahr, 
                                      ugewerk_nr, ugewerk_bez, anzahl, standort_id, gebaudeteil, etage, raum, raumbezeichnung, 
                                      aks_Bez., kostengruppe_nr, kostengruppen_bez, lebensdauer, lebensende, zustand, beschreibung) 
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                            
                            ugew_txt_val = opt_ugew.get(f_ugew, "").split(" - ")[-1] if f_ugew else None
                            kg_txt_val = opt_kg.get(f_din, "").split(" - ")[-1] if f_din else None
                            
                            val = (
                                f_aid, f_aname, f_atyp, 
                                int(f_bauteil) if f_bauteil.isdigit() else None,
                                f_herst, f_typ, f_sn, 
                                int(f_bj) if f_bj.isdigit() else None,
                                f_ugew if f_ugew else None,
                                ugew_txt_val,
                                int(f_anz) if f_anz.isdigit() else 1,
                                f_std, f_gteil, f_etage, f_raum, f_rbez,
                                f_aks,
                                f_din if f_din else None,
                                kg_txt_val,
                                f_ld, f_le, 
                                f_zustand or "Betriebsbereit", 
                                f_beschr
                            )
                            cur.execute(sql, val)
                            conn_ins.commit()
                            st.success(txt["success_reg"])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fehler beim Speichern in der Datenbank: {e}")
                        finally:
                            if cur:
                                try:
                                    cur.close()
                                except:
                                    pass
                            if conn_ins:
                                try:
                                    conn_ins.close()
                                except:
                                    pass
                else:
                    st.error(txt["err_req"])