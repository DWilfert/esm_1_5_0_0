import streamlit as st
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung, hole_anlagen_daten
from logik.ui import render_page_header, render_section_header

@st.dialog("Anlage bearbeiten (Demo-Modus)")
def anlage_bearbeiten_dialog(sel_id, row_det, txt):
    with st.form(f"form_edit_anl_modal_{sel_id}"):
        f_aname = st.text_input(txt["lbl_aname"], value=str(row_det.get('anlagebezeichnung', '')))
        f_atyp = st.text_input(txt["lbl_atyp"], value=str(row_det.get('anlagetyp', '')))
        f_herst = st.text_input(txt["lbl_herst"], value=str(row_det.get('hersteller', '')))
        f_zustand = st.text_input(txt["lbl_zustand"], value=str(row_det.get('zustand', '')))
        f_beschr = st.text_area(txt["lbl_beschr"], value=str(row_det.get('beschreibung', '')))

        st.write("")
        if st.form_submit_button(txt["btn_save"], type="primary"):
            st.success("✅ [Demo-Modus] Änderungen erfolgreich simuliert gespeichert!")
            st.rerun()

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
    
    txt = {
        "de": {
            "titel": "Anlagenstruktur (Demo-Modus)",
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
            "success_upd": "Änderungen simuliert gespeichert!",
            "btn_back": "Zurück zur Vertragsanalyse",
            "new_titel": "Neue Anlage erfassen (Demo)",
            "sec1": "1. Basisdaten & Klassifizierung",
            "sec2": "2. Technische Daten & Lifecycle",
            "sec3": "3. Räumliche Zuordnung & Standort",
            "sec4": "4. Beschreibung & Kennzeichnung",
            "lbl_std": "Standort *",
            "lbl_aid": "Anlagen-Nummer *",
            "lbl_aname": "Anlagenbezeichnung *",
            "lbl_atyp": "Anlagentyp",
            "lbl_herst": "Hersteller",
            "lbl_zustand": "Zustand",
            "lbl_beschr": "Beschreibung",
            "btn_reg": "Anlage speichern",
            "success_reg": "Anlage erfolgreich im Demo-Modus gespeichert!",
            "bitte_waehlen": "--- Bitte wählen ---",
            "keine_hist": "Keine Historie vorhanden.",
            "err_req": "Bitte füllen Sie mindestens die Pflichtfelder aus."
        },
        "en": {
            "titel": "Asset Structure (Demo)",
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
            "success_upd": "Changes saved!",
            "btn_back": "Back to Contract Analysis",
            "new_titel": "Register New Asset (Demo)",
            "sec1": "1. Basic Data & Classification",
            "sec2": "2. Technical Data & Lifecycle",
            "sec3": "3. Spatial Allocation & Location",
            "sec4": "4. Description & Identification",
            "lbl_std": "Location *",
            "lbl_aid": "Asset Number *",
            "lbl_aname": "Asset Name *",
            "lbl_atyp": "Asset Type",
            "lbl_herst": "Manufacturer",
            "lbl_zustand": "Condition",
            "lbl_beschr": "Description",
            "btn_reg": "Save Asset",
            "success_reg": "Asset successfully saved in demo mode!",
            "bitte_waehlen": "--- Please select ---",
            "keine_hist": "No history available.",
            "err_req": "Please fill out required fields."
        }
    }[lang]

    render_page_header(txt['titel'])
    
    df_anlagen = hole_anlagen_daten()
    if "standort" not in df_anlagen.columns:
        df_anlagen["standort"] = "NP"
        
    if "showendlos" not in st.session_state:
        st.session_state.showendlos = False
        
    if st.button(txt["btn_toggle"], key="anl_toggle_btn_main"):
        st.session_state.showendlos = not st.session_state.showendlos
        st.rerun()

    if st.session_state.showendlos and not df_anlagen.empty:
        df_anlagen_work = df_anlagen.copy()
        df_anlagen_work["zustand"] = df_anlagen_work["zustand"].fillna("").astype(str)

        standorte = sorted(df_anlagen_work['standort'].dropna().astype(str).unique().tolist())
        selected_standorte = st.multiselect(
            txt['filter_location'],
            standorte,
            default=standorte,
            key='anlagen_standort_filter'
        )
        if selected_standorte:
            df_anlagen_work = df_anlagen_work[df_anlagen_work['standort'].astype(str).isin(selected_standorte)].copy()

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
        col_filt, col_src = st.columns([4.0, 6.0])
        with col_filt: 
            anl_filter = st.radio(txt["filter_std"], [txt["beide"], "NP", "FG"], horizontal=True, key="anl_std_filter_v7")
        with col_src: 
            anl_suche = st.text_input(txt["suche"], autocomplete="off", key="anl_src_input_v7")

        df_endlos = df_anlagen_work.copy()
        if anl_filter != txt["beide"]: 
            df_endlos = df_endlos[df_endlos["standort"] == anl_filter]
        if anl_suche:
            s_l = anl_suche.lower()
            df_endlos = df_endlos[df_endlos["anlagebezeichnung"].str.lower().str.contains(s_l, na=False)]
        
        verfuegbare_spalten = [col for col in ["standort", "anlagenr", "anlagebezeichnung", "hersteller", "typ", "zustand"] if col in df_endlos.columns]
        st.dataframe(df_endlos[verfuegbare_spalten], use_container_width=True, hide_index=True)

        anlagen_mapping = {
            row["id"]: f"{row['anlagebezeichnung']} (Nr: {row['anlagenr']})" if pd.notna(row['anlagenr']) else str(row['anlagebezeichnung'])
            for _, row in df_endlos.iterrows()
        }
        id_liste = [None] + list(anlagen_mapping.keys())

        col_sel_box, col_edit_btn = st.columns([5.0, 5.0])
        with col_sel_box:
            sel_id = st.selectbox(
                txt["sel_anlage"], 
                options=id_liste, 
                format_func=lambda x: txt["bitte_waehlen"] if x is None else anlagen_mapping[x],
                key="anl_sel_id_dropdown_v7"
            )
        
        if sel_id is not None:
            df_target = df_endlos[df_endlos["id"] == sel_id]
            if not df_target.empty:
                row_det = df_target.iloc[0].to_dict()
                
                with col_edit_btn:
                    st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)
                    if st.button(txt["btn_edit"], key=f"btn_open_edit_anl_{sel_id}"):
                        anlage_bearbeiten_dialog(sel_id, row_det, txt)

                zustand_str = str(row_det.get('zustand', '')).lower()
                d_class = "dot-green" if "betriebsbereit" in zustand_str else "dot-red"
                
                st.markdown(f"<div style='display:flex; align-items:center; margin-bottom: 15px;'><b>{txt['zustandampel']}</b> <span class='micro-dot {d_class}' style='margin-left:8px; margin-right:8px;'></span> {row_det.get('zustand', '-')}</div>", unsafe_allow_html=True)
                
                t1, t2, t3, t4 = st.tabs(txt["tabs"])
                with t1:
                    st.write(f"**{txt['basis']['art']}:** {row_det.get('anlagetyp', '-')}")
                    st.write(f"**{txt['basis']['beschr']}:** {row_det.get('beschreibung', '-')}")
                with t2:
                    st.write(f"**{txt['technik']['herst']}:** {row_det.get('hersteller', '-')}")
                with t3:
                    st.write(f"**Standort:** {row_det.get('standort', '-')}")
                with t4:
                    st.info(txt["keine_hist"])
    else:
        st.markdown(f"<div style='font-size: 20px; font-weight: 300; margin-bottom: 15px;'>{txt['new_titel']}</div>", unsafe_allow_html=True)
        with st.form("anl_form_n_demo", clear_on_submit=True):
            f_aid = st.text_input(txt["lbl_aid"], placeholder="z. B. 17501")
            f_aname = st.text_input(txt["lbl_aname"], placeholder="z. B. Personenaufzug A")
            if st.form_submit_button(txt["btn_reg"], type="primary"):
                st.success(txt["success_reg"])