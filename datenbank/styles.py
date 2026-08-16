import streamlit as st


def lade_app_design():
    farben = {
        "bg_app": "radial-gradient(circle at top left, #020817 0%, #0b1220 26%, #111827 100%)",
        "solid_bg": "#0a1220",
        "border_color": "rgba(125, 211, 252, 0.42)",
        "card_bg": "rgba(15, 23, 42, 0.96)",
        "table_bg": "rgba(15, 23, 42, 0.96)",
        "text_main": "#e2e8f0",
        "text_muted": "#93c5fd",
        "accent_color": "#7dd3fc",
        "input_bg": "rgba(15, 23, 42, 0.94)",
        "dropdown_hover": "rgba(125, 211, 252, 0.2)",
        "hr_color": "rgba(125, 211, 252, 0.24)"
    }

    bg_sidebar = farben["solid_bg"]
    st.markdown(f"""
        <style>
        :root, [data-testid="stAppViewContainer"] {{
            --primary-color: {farben['accent_color']};
            --background-color: {farben['solid_bg']};
            --secondary-background-color: {farben['input_bg']};
            --text-color: {farben['text_main']};
            --body-text-color: {farben['text_main']};
            --widget-background-color: {farben['input_bg']};
            --widget-text-color: {farben['text_main']};
            --panel-bg: {farben['card_bg']};
            --panel-border: {farben['border_color']};
            --panel-shadow: rgba(15, 23, 42, 0.38);
            --sidebar-bg: {bg_sidebar};
        }}

        [data-testid="stHeader"] {{ background: transparent !important; }}
        [data-testid="stDecoration"] {{ display: none !important; }}
        .block-container {{
            padding-top: 1.4rem !important;
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
            padding-bottom: 1.5rem !important;
        }}

        .stApp {{
            background:
                linear-gradient(to right, rgba(148, 163, 184, 0.045) 1px, transparent 1px) 0 0 / 140px 100%,
                linear-gradient(to bottom, rgba(148, 163, 184, 0.03) 1px, transparent 1px) 0 0 / 100% 42px,
                radial-gradient(circle at top left, rgba(148, 163, 184, 0.06), transparent 38%),
                {farben['bg_app']} !important;
            font-family: 'Segoe UI', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif !important;
            border-top: 1px solid rgba(148, 163, 184, 0.14) !important;
        }}

        section[data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"] {{
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.96) 0%, rgba(15, 23, 42, 0.84) 100%) !important;
            background-color: var(--sidebar-bg) !important;
            border-right: 1px solid {farben['border_color']} !important;
            box-shadow: 8px 0 28px rgba(2, 6, 23, 0.26) !important;
        }}

        [data-testid="stSidebar"] > div:first-child {{
            padding: 1rem 0.85rem 1.2rem 0.85rem !important;
        }}

        [data-testid="stSidebar"] div[role="radiogroup"] {{
            display: flex !important;
            flex-direction: column !important;
            gap: 0.18rem !important;
            margin-top: 0.35rem !important;
        }}

        [data-testid="stSidebar"] div[role="radio"] {{
            min-height: 2.7rem !important;
            padding: 0.58rem 0.8rem !important;
            border-radius: 12px !important;
            margin: 0 !important;
            border: 1px solid rgba(125, 211, 252, 0.14) !important;
            background: linear-gradient(90deg, rgba(15, 23, 42, 0.9), rgba(15, 23, 42, 0.62)) !important;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02) !important;
        }}

        [data-testid="stSidebar"] div[role="radiogroup"] label,
        [data-testid="stSidebar"] div[role="radio"] span,
        [data-testid="stSidebar"] div[role="radio"] p {{
            color: {farben['text_main']} !important;
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            line-height: 1.25 !important;
        }}

        [data-testid="stSidebar"] div[role="radio"][aria-checked="true"] {{
            background: linear-gradient(90deg, rgba(125, 211, 252, 0.18) 0%, rgba(30, 41, 59, 0.9) 32%, rgba(15, 23, 42, 0.95) 100%) !important;
            border-color: rgba(125, 211, 252, 0.65) !important;
            box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04), 0 0 0 1px rgba(125, 211, 252, 0.12) !important;
        }}

        [data-testid="stSidebar"] div[role="radio"]:hover {{
            background: linear-gradient(90deg, rgba(125, 211, 252, 0.12) 0%, rgba(30, 41, 59, 0.85) 36%, rgba(15, 23, 42, 0.94) 100%) !important;
            border-color: rgba(125, 211, 252, 0.5) !important;
            transform: translateX(2px);
            transition: all 0.2s ease;
        }}

        h1, h2, h3, h4, h5, h6, p, span, label {{
            color: {farben['text_main']} !important;
        }}

        h1 {{
            letter-spacing: -0.05em !important;
            font-weight: 700 !important;
            line-height: 1.08 !important;
            margin-bottom: 0.5rem !important;
            padding-bottom: 0.5rem !important;
            border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
            position: relative !important;
        }}

        h1::after, h2::after, h3::after, h4::after, h5::after, h6::after {{
            content: "" !important;
            display: block !important;
            width: 72px !important;
            height: 1px !important;
            background: linear-gradient(90deg, rgba(143, 179, 255, 0.9), rgba(148, 163, 184, 0.18)) !important;
            margin-top: 0.55rem !important;
        }}

        h2, h3, h4, h5, h6 {{
            letter-spacing: -0.03em !important;
            font-weight: 600 !important;
            border-bottom: 1px solid rgba(148, 163, 184, 0.12) !important;
            padding-bottom: 0.35rem !important;
        }}

        div[data-testid="stMetric"] {{
            position: relative !important;
            min-height: 118px !important;
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.78) 0%, rgba(15, 23, 42, 0.58) 100%) !important;
            border: 1px solid {farben['border_color']} !important;
            border-radius: 14px !important;
            box-shadow: 0 12px 30px rgba(2, 6, 23, 0.22) !important;
            padding: 1rem 1.1rem !important;
            overflow: hidden !important;
        }}

        div[data-testid="stMetric"]::before {{
            content: "" !important;
            position: absolute !important;
            left: 0 !important;
            right: 0 !important;
            top: 0 !important;
            height: 2px !important;
            background: linear-gradient(90deg, rgba(143, 179, 255, 0.9), rgba(148, 163, 184, 0.22), transparent) !important;
        }}

        div[data-testid="stMetric"]::after {{
            content: "" !important;
            position: absolute !important;
            top: 16px !important;
            right: 16px !important;
            width: 56px !important;
            height: 1px !important;
            background: rgba(148, 163, 184, 0.14) !important;
        }}

        [data-testid="stMetricLabel"] {{
            color: {farben['text_muted']} !important;
            text-transform: uppercase !important;
            letter-spacing: 0.08em !important;
            font-size: 0.68rem !important;
            font-weight: 600 !important;
        }}

        [data-testid="stMetricValue"] {{
            font-size: clamp(1.5rem, 2vw, 2.2rem) !important;
            font-weight: 700 !important;
            line-height: 1.15 !important;
            color: {farben['text_main']} !important;
        }}

        [data-testid="stMetricDelta"] {{
            font-weight: 600 !important;
            color: {farben['accent_color']} !important;
        }}

        div[data-testid="stButton"] button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stDownloadButton"] button {{
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.96) 0%, rgba(15, 23, 42, 0.98) 100%) !important;
            color: {farben['text_main']} !important;
            border: 1px solid rgba(148, 163, 184, 0.45) !important;
            border-radius: 10px !important;
            box-shadow: 0 8px 20px rgba(2, 6, 23, 0.18) !important;
            font-weight: 600 !important;
            letter-spacing: 0.02em !important;
            min-height: 2.6rem !important;
            padding: 0.55rem 0.9rem !important;
        }}

        div[data-testid="stButton"] button:hover,
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover {{
            border-color: rgba(203, 213, 225, 0.8) !important;
            color: {farben['text_main']} !important;
            background: linear-gradient(180deg, rgba(51, 65, 85, 0.97) 0%, rgba(15, 23, 42, 0.99) 100%) !important;
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.24) !important;
            transform: translateY(-1px);
        }}

        label, .stCheckbox label, .stRadio label, .stSelectbox label, .stTextInput label, .stTextArea label {{
            color: {farben['text_muted']} !important;
            font-weight: 600 !important;
            letter-spacing: 0.06em !important;
            text-transform: uppercase !important;
            font-size: 0.7rem !important;
            margin: 0 0 0.38rem 0 !important;
        }}

        input, textarea, select, [data-baseweb="select"], [data-baseweb="base-input"] {{
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.86) 0%, rgba(15, 23, 42, 0.66) 100%) !important;
            color: {farben['text_main']} !important;
            border-color: {farben['border_color']} !important;
            border-radius: 10px !important;
        }}

        hr {{
            border: none !important;
            height: 1px !important;
            background-color: {farben['hr_color']} !important;
            margin: 1rem 0 !important;
        }}

        [data-testid="stSidebarCollapseButton"] {{
            display: inline-flex !important;
            visibility: visible !important;
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.94) 0%, rgba(15, 23, 42, 0.7) 100%) !important;
            border: 1px solid rgba(143, 179, 255, 0.48) !important;
            border-radius: 12px !important;
            z-index: 999999 !important;
            box-shadow: 0 12px 30px rgba(2, 6, 23, 0.32) !important;
        }}

        [data-testid="stSidebarCollapseButton"] svg {{
            fill: {farben['accent_color']} !important;
            color: {farben['accent_color']} !important;
        }}

        [data-testid="stVerticalBlock"] > div {{
            gap: 1.1rem !important;
        }}

        .element-container, .stDataFrame, [data-testid="stMetric"], [data-testid="stButton"] button, [data-testid="stFormSubmitButton"] button, div[data-testid="stFileUploader"] section {{
            border-radius: 16px !important;
        }}

        div[data-testid="stButton"] button,
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stDownloadButton"] button {{
            transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease !important;
        }}

        div[data-testid="stButton"] button:hover,
        div[data-testid="stFormSubmitButton"] button:hover,
        div[data-testid="stDownloadButton"] button:hover {{
            transform: translateY(-1px) !important;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.2) !important;
        }}

        [data-testid="stMainBlockContainer"] > div > div > div {{
            padding-left: 0.15rem !important;
            padding-right: 0.15rem !important;
        }}
        </style>
    """, unsafe_allow_html=True)