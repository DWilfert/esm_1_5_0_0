import streamlit as st


def render_page_header(title: str, subtitle: str = "", eyebrow: str | None = None):
    st.markdown(f"<div class='custom-huge-title'>{title}</div>", unsafe_allow_html=True)
    if eyebrow:
        st.markdown(
            f"<div style='font-size:10px; font-weight:600; color:#64748b; margin-top:6px; letter-spacing:2px;'>{eyebrow}</div>",
            unsafe_allow_html=True,
        )
    if subtitle:
        st.markdown(
            f"<div style='font-size: 13px; color: var(--text-color); opacity: 0.7; margin-top: 6px; margin-bottom: 25px;'>{subtitle}</div>",
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
