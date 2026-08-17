import streamlit as st
import streamlit.components.v1 as components
import base64
import os
import warnings

from datenbank.befehle import hole_datenbank_verbindung
from datenbank.styles import lade_app_design
from logik.design import lade_design_farben
from seiten.startseite import zeige_startseite
from seiten.admin import zeige_adminbereich
from seiten.vertragsanalyse import zeige_vertragsanalyse
from seiten.wartungsanalyse import zeige_wartungsanalyse
from seiten.auffaelligkeiten import zeige_auffalligkeiten
from seiten.anlagenstruktur import zeige_anlagenstruktur
from seiten.serviceeinsaetze import zeige_serviceeinsaetze
from seiten.plan_5jahres import zeige_5jahresplan
from seiten.firmeninfo import zeige_firmeninfo
from seiten.import_export import zeige_import_export
from seiten.vertrag_dokumente import zeige_vertragsdokumente
from seiten.anlagen_history import zeige_anlagen_history
from seiten.globale_suche import zeige_globale_suche
from seiten.buchhaltung import zeige_buchhaltung
from seiten.statistik import zeige_statistik

warnings.filterwarnings("ignore", category=UserWarning)

if "language" not in st.session_state:
    st.session_state.language = "de"

try:
    query_lang = st.query_params.get("lang", "de")
    if isinstance(query_lang, list):
        query_lang = query_lang[0] if query_lang else "de"
    if query_lang in ["de", "en"]:
        st.session_state.language = query_lang
except Exception:
    pass

if "speicher_modus" not in st.session_state:
    st.session_state.speicher_modus = "manuell"

TXT_MENU = {
    "de": {
        "hauptmenue": "HAUPTMENÜ",
        "m1": "Startseite",
        "m16": "Globale Suche",
        "m2": "Vertragsanalyse",
        "m4": "Wartungsübersicht",
        "m3": "Vertragsdokumente",
        "m6": "Anlagen",
        "m15": "360° Anlagen",
        "m7": "Service",
        "m5": "Auffälligkeiten",
        "m9": "Firmeninfo",
        "m8": "5-Jahresplan",
        "m10": "Import / Export",
        "m13": "Buchhaltung",
        "m14": "Statistik",
        "m11": "Adminbereich"
    },
    "en": {
        "hauptmenue": "MAIN MENU",
        "m1": "Home",
        "m16": "Global Search",
        "m2": "Contract Analysis",
        "m4": "Maintenance Overview",
        "m3": "Contract Documents",
        "m6": "Asset Structure",
        "m15": "360° Assets",
        "m7": "Service",
        "m5": "Discrepancies",
        "m9": "Company Info",
        "m8": "5-Year Plan",
        "m10": "Import / Export",
        "m13": "Bookkeeping",
        "m14": "Statistics",
        "m11": "Admin Area"
    }
}[st.session_state.language]

def render_page_header(title: str, subtitle: str = ""):
    st.markdown(f"<div class='custom-huge-title'>{title}</div>", unsafe_allow_html=True)
    if subtitle:
        st.markdown(f"<div style='font-size: 13px; color: var(--text-color); opacity: 0.7; margin-top: 6px; margin-bottom: 25px;'>{subtitle}</div>", unsafe_allow_html=True)
    st.markdown("---")

if "app_seite_wechseln" not in st.session_state:
    st.session_state.app_seite_wechseln = False

if "app_ziel_seite" not in st.session_state:
    st.session_state.app_ziel_seite = None

if st.session_state.app_seite_wechseln:
    if st.session_state.app_ziel_seite is not None:
        st.session_state.haupt_navigation_final = st.session_state.app_ziel_seite
    else:
        st.session_state.haupt_navigation_final = TXT_MENU["m1"]  
    st.session_state.app_seite_wechseln = False
    st.session_state.app_ziel_seite = None

st.set_page_config(
    page_title="ESM Vertrags- & Wartungsmanagement V1.5.0.0 Enterprise",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

theme_colors = lade_design_farben()

st.markdown(
    f"""
    <style>
    .stAppDeployButton {{ display: none !important; }}
    #MainMenu {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    header {{ background: transparent !important; }}
    .stApp {{ background: {theme_colors['bg_app']} !important; }}
    [data-testid="stSidebar"] {{
        background: {theme_colors['bg_sidebar']} !important;
        width: 270px !important;
        min-width: 270px !important;
        max-width: 270px !important;
    }}
    [data-testid="stSidebar"] div[role="radiogroup"] label,
    [data-testid="stSidebar"] div[role="radiogroup"] p,
    [data-testid="stSidebar"] div[role="radio"] span,
    [data-testid="stSidebar"] div[role="radio"] p,
    [data-testid="stSidebar"] .sidebar-title {{
        white-space: nowrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
    }}
    .sidebar-title {{ font-size: 0.9rem; font-weight: 800; color: {theme_colors['text_muted']}; text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 14px; margin-top: 8px; white-space: nowrap; }}

    :root {{
        --basis-schrift: 0.84rem;
        --theme-accent: {theme_colors['accent_color']};
        --theme-text: {theme_colors['text_main']};
        --theme-muted: {theme_colors['text_muted']};
        --theme-border: {theme_colors['border_color']};
        --theme-input: {theme_colors['input_bg']};
    }}

    p, label, input, textarea {{
        font-size: var(--basis-schrift) !important;
    }}

    body, .stApp, .stApp div, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp select {{
        font-family: 'Segoe UI', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif !important;
    }}
    .custom-huge-title {{
        font-family: 'Segoe UI', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.05em !important;
        line-height: 1.1 !important;
        margin-bottom: 0px !important;
        color: var(--theme-text) !important;
        white-space: nowrap !important;
    }}
    h1 {{ font-size: 2.8rem !important; font-weight: 700 !important; color: var(--theme-text) !important; }}
    h2 {{ font-size: 2.0rem !important; font-weight: 600 !important; color: var(--theme-text) !important; }}
    h3 {{ font-size: 1.6rem !important; font-weight: 600 !important; color: var(--theme-text) !important; }}
    </style>
    
""",
unsafe_allow_html=True
)

lade_app_design()

logo_pfad = "logo1.png"
try:
    if os.path.exists(logo_pfad):
        with open(logo_pfad, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.sidebar.markdown(
            f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin: 0 auto 14px auto; width: 100%;">'
            f'<div style="width: 100%; display: flex; justify-content: center; align-items: center; padding: 0 8px; box-sizing: border-box;">'
            f'<img src="data:image/png;base64,{encoded_string}" style="max-width: 150px; width: 100%; height: auto; border-radius: 8px; display: block; margin: 0 auto; object-fit: contain;">'
            f'</div>'
            f'<div style="font-size: 0.45rem; color: var(--text-color); opacity: 0.4; margin-top: 4px; letter-spacing: 0.5px;">© D.Wilfert / 2026</div>'
            f'</div>', 
            unsafe_allow_html=True
        )
except Exception:
    pass

st.sidebar.markdown(f"<div class='sidebar-title'>{TXT_MENU['hauptmenue']}</div>", unsafe_allow_html=True)

ausgewaehlter_punkt = st.sidebar.radio(
    "Navigieren zu:" if st.session_state.language == "de" else "Navigate to:",
    [TXT_MENU[k] for k in ["m1", "m16", "m2", "m4", "m3", "m6", "m15", "m7", "m5", "m9", "m8", "m10", "m13", "m14", "m11"]], 
    key="haupt_navigation_final",
    label_visibility="collapsed"
)

if ausgewaehlter_punkt == TXT_MENU["m1"]:
    zeige_startseite()  
elif ausgewaehlter_punkt == TXT_MENU["m16"]:
    zeige_globale_suche()
elif ausgewaehlter_punkt == TXT_MENU["m2"]:
    zeige_vertragsanalyse("")
elif ausgewaehlter_punkt == TXT_MENU["m4"]:
    zeige_wartungsanalyse()
elif ausgewaehlter_punkt == TXT_MENU["m3"]:
    zeige_vertragsdokumente()
elif ausgewaehlter_punkt == TXT_MENU["m6"]:
    zeige_anlagenstruktur()
elif ausgewaehlter_punkt == TXT_MENU["m15"]:
    zeige_anlagen_history()
elif ausgewaehlter_punkt == TXT_MENU["m7"]:
    zeige_serviceeinsaetze()
elif ausgewaehlter_punkt == TXT_MENU["m5"]:
    zeige_auffalligkeiten()
elif ausgewaehlter_punkt == TXT_MENU["m9"]:
    zeige_firmeninfo()
elif ausgewaehlter_punkt == TXT_MENU["m8"]:
    zeige_5jahresplan()
elif ausgewaehlter_punkt == TXT_MENU["m10"]:
    zeige_import_export()
elif ausgewaehlter_punkt == TXT_MENU["m13"]:
    zeige_buchhaltung()
elif ausgewaehlter_punkt == TXT_MENU["m14"]:
    zeige_statistik()
elif ausgewaehlter_punkt == TXT_MENU["m11"]:
    zeige_adminbereich()