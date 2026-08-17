import re

import pandas as pd
import streamlit as st

PAGE_FONT_FAMILY = "'Segoe UI', 'Segoe UI Emoji', 'Segoe UI Symbol', sans-serif"

COMMON_COLUMN_LABELS = {
    "id": "ID",
    "anlage_id": "Anlagen-ID",
    "anlagen_nr": "Anlagen-Nr.",
    "anlagenr": "Anlagen-Nr.",
    "anlagebezeichnung": "Anlagenbezeichnung",
    "anlagenname": "Anlagenname",
    "standort": "Standort",
    "standort_text": "Standort",
    "standortname": "Standortname",
    "vertrag": "Vertrag",
    "vertragsname": "Vertragsname",
    "vertragsart": "Vertragsart",
    "naechste_wartung": "Nächste Wartung",
    "zyklus_monate": "Intervall (Monate)",
    "intervall": "Intervall",
    "kosten_bestand_pa": "Bestandskosten / Jahr",
    "benchmark_ais_pa": "Benchmark / Jahr",
    "einspar_potenzial": "Einsparpotenzial",
    "firma": "Firma",
    "firma_id": "Firmen-ID",
    "firmenname": "Firmenname",
    "firma_name": "Firmenname",
    "status": "Status",
    "datum": "Datum",
    "termin": "Termin",
    "kurzfassung": "Kurzfassung",
    "qualifikation": "Qualifikation",
    "erstabnahme": "Erstabnahme",
    "wiederkehrende_pruefung": "Wiederkehrende Prüfung",
    "baujahr": "Baujahr",
    "anzahl": "Anzahl",
    "merkmal": "Merkmal",
    "merkmalwert": "Merkmalwert",
    "bezeichnung_anlagenklasse": "Klassenbezeichnung",
    "anlagenklasse": "Anlagenklasse",
    "kennz_1": "Kennzeichnung 1",
    "kennz_2": "Kennzeichnung 2",
    "kommentar": "Kommentar",
    "beschreibung": "Beschreibung",
    "hinweis": "Hinweis",
    "protokolldatei": "Protokolldatei",
    "vertrag_datei": "Vertrag / Datei",
    "gesetzl_grundlage": "Gesetzliche Grundlage",
    "textstelle_gesetz": "Relevante Textstelle",
    "entlastung_schadensfall": "Entlastung im Schadensfall",
}

STANDORT_DISPLAY_MAP = {
    "NP": "Neuperlach (NP)",
    "FG": "Fasangarten (FG)",
}


def standort_display_name(value):
    if value is None:
        return ""
    key = str(value).strip()
    raw = key.upper()
    if raw in STANDORT_DISPLAY_MAP:
        return STANDORT_DISPLAY_MAP[raw]
    lower = key.lower()
    for code, label in STANDORT_DISPLAY_MAP.items():
        if lower in {code.lower(), label.lower(), label.split(" (")[0].lower()}:
            return label
    return key


def standort_code_from_display(value):
    if value is None:
        return None
    label = str(value).strip()
    for code, display in STANDORT_DISPLAY_MAP.items():
        if label == display or label.upper() == code or label.lower() == display.lower():
            return code
    return label


PAGE_TYPOGRAPHY_CSS = f"""
<style>
    body, .stApp, .stApp .markdown-text-container, .stApp div, .stApp p, .stApp label,
    .stApp input, .stApp textarea, .stApp select {{
        font-family: {PAGE_FONT_FAMILY} !important;
    }}
    .custom-huge-title, .forced-header-title, h1 {{
        font-family: {PAGE_FONT_FAMILY} !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        letter-spacing: -0.05em !important;
        line-height: 1.1 !important;
        margin-bottom: 0px !important;
        color: var(--text-color, #e2e8f0) !important;
        white-space: nowrap !important;
    }}
    h2 {{
        font-family: {PAGE_FONT_FAMILY} !important;
        font-size: 2.0rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.04em !important;
        line-height: 1.2 !important;
        color: var(--text-color, #e2e8f0) !important;
    }}
    h3 {{
        font-family: {PAGE_FONT_FAMILY} !important;
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        letter-spacing: -0.03em !important;
        line-height: 1.25 !important;
        color: var(--text-color, #e2e8f0) !important;
    }}
</style>
"""


def readable_column_name(column_name):
    key = str(column_name).strip()
    normalized = key.lower().replace("`", "")
    if normalized in COMMON_COLUMN_LABELS:
        return COMMON_COLUMN_LABELS[normalized]

    label = key.replace("_", " ")
    label = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", label)
    label = re.sub(r"\s+", " ", label).strip()
    label = label[0].upper() + label[1:] if label else label
    return label


def prepare_display_dataframe(df, custom_labels=None):
    if df is None or df.empty and len(df.columns) == 0:
        return df

    renamed = df.copy()
    for col in renamed.columns:
        key = str(col)
        if key.lower() in {"standort", "standort_text", "standortname", "ort_kurz", "ort"}:
            renamed[key] = renamed[key].map(lambda value: standort_display_name(value) if pd.notna(value) else value)

    labels = {}
    seen = {}
    for col in renamed.columns:
        key = str(col)
        label = custom_labels.get(key, readable_column_name(key)) if custom_labels else readable_column_name(key)
        if label in seen:
            seen[label] += 1
            label = f"{label} ({seen[label]})"
        else:
            seen[label] = 0
        labels[key] = label
    renamed = renamed.rename(columns=labels)
    return renamed


def apply_page_typography():
    st.markdown(PAGE_TYPOGRAPHY_CSS, unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str = "", eyebrow: str | None = None):
    apply_page_typography()
    st.markdown(
        f"""
        <div class="forced-header-title" style="
            font-family: {PAGE_FONT_FAMILY} !important;
            font-size: 2.8rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.05em !important;
            line-height: 1.1 !important;
            margin-bottom: 0px !important;
            color: var(--text-color, #e2e8f0) !important;
            white-space: nowrap !important;
        ">
            {title}
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if eyebrow:
        st.markdown(
            f"<div style='font-family: \"Segoe UI\", sans-serif; font-size:10px; font-weight:600; color:#64748b; margin-top:6px; letter-spacing:2px;'>{eyebrow}</div>",
            unsafe_allow_html=True,
        )
    if subtitle:
        st.markdown(
            f"<div style='font-family: \"Segoe UI\", sans-serif; font-size: 13px; color: var(--text-color); opacity: 0.7; margin-top: 6px; margin-bottom: 25px;'>{subtitle}</div>",
            unsafe_allow_html=True,
        )
    st.markdown("---")


def render_section_header(title: str):
    st.markdown(f"<div class='ent-subheader'>{title}</div>", unsafe_allow_html=True)


def render_status_chip(label: str, value: str, color: str = "#8fb3ff"):
    return f"""
        <div style="display:inline-flex; align-items:center; gap:8px; background: rgba(148,163,184,0.06); border:1px solid rgba(148,163,184,0.2); border-radius:999px; padding:8px 12px; font-size:11px; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:{color};">
            <span>{label}</span>
            <span style="opacity:0.9; color: var(--text-color);">{value}</span>
        </div>
    """


def render_kpi_card(title: str, value: str, accent: str = "#e2e8f0"):
    return f"""
        <div class="ent-kpi-card">
            <div class="ent-kpi-title">{title}</div>
            <div class="ent-kpi-value" style="color: {accent};">{value}</div>
        </div>
    """