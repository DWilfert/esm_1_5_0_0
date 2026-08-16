import streamlit as st

DESIGN_TOKENS = {
    "bg_app": "radial-gradient(circle at top left, #020817 0%, #0b1220 26%, #111827 100%)",
    "bg_sidebar": "#0a1220",
    "border_color": "rgba(125, 211, 252, 0.42)",
    "card_bg": "rgba(15, 23, 42, 0.95)",
    "table_bg": "rgba(15, 23, 42, 0.95)",
    "text_main": "#e2e8f0",
    "text_muted": "#93c5fd",
    "input_bg": "rgba(15, 23, 42, 0.94)",
    "accent_color": "#7dd3fc",
    "dropdown_hover": "rgba(125, 211, 252, 0.2)",
    "hr_color": "rgba(125, 211, 252, 0.24)",
    "radius_sm": "10px",
    "radius_md": "14px",
    "radius_lg": "18px",
    "space_xs": "6px",
    "space_sm": "10px",
    "space_md": "16px",
    "space_lg": "24px",
    "shadow_soft": "0 12px 30px rgba(2, 6, 23, 0.22)",
    "font_family": "'Segoe UI', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif"
}

ENTERPRISE_STYLE = DESIGN_TOKENS.copy()


def lade_design_farben():
    return ENTERPRISE_STYLE

def korrigiere_menue_button():
    css_code = """
    <style>
        [data-testid="stSidebarCollapseButton"] {
            top: 20px !important;
        }
    </style>
    """
    st.markdown(css_code, unsafe_allow_html=True)


def wende_design_an():
    farben = lade_design_farben()
    
    css = f"""
    <style>
        .stApp {{
            background: {farben["bg_app"]};
            color: {farben["text_main"]};
        }}
        
        [data-testid="stSidebar"] {{
            background-color: {farben["bg_sidebar"]} !important;
            border-right: 1px solid {farben["border_color"]};
        }}
        
        [data-testid="stSidebar"] .streamlit-expanderHeader {{
            background-color: {farben["card_bg"]} !important;
            color: {farben["text_main"]} !important;
            border: 1px solid {farben["border_color"]};
            border-radius: 8px;
        }}
        [data-testid="stSidebar"] .streamlit-expanderContent {{
            background-color: {farben["bg_sidebar"]} !important;
            color: {farben["text_main"]} !important;
            border: 1px solid {farben["border_color"]};
            border-top: none;
        }}
        
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] svg {{
            color: {farben["text_main"]} !important;
            fill: {farben["text_main"]} !important;
        }}
        
        [data-testid="stSidebar"] div[data-baseweb="input"],
        [data-testid="stSidebar"] div[data-baseweb="select"] {{
            background-color: {farben["input_bg"]} !important;
            border: 1px solid {farben["border_color"]};
            color: {farben["text_main"]} !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    korrigiere_menue_button()