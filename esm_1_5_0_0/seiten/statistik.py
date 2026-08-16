import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datenbank.befehle import hole_datenbank_verbindung


def zeige_statistik():
    st.markdown("""
        <style>
        .ent-subheader { font-size: 11px; font-weight: 500; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 25px; padding-bottom: 10px; border-bottom: 1px solid rgba(148, 163, 184, 0.2); }
        .custom-huge-title {
            font-size: 2.8rem !important;
            font-weight: 500 !important;
            letter-spacing: -0.5px !important;
            margin-bottom: 0px !important;
            line-height: 1.1 !important;
            white-space: nowrap !important;
        }
        .stat-card {
            background: rgba(148, 163, 184, 0.02);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        /* Automatischer Toner-Spar-Modus beim Drucken (Weißer Hintergrund, schwarzer Text) */
        @media print {
            [data-testid="stSidebar"], header, .stButton, iframe {
                display: none !important;
            }
            .stApp, body, html {
                background-color: #ffffff !important;
                color: #000000 !important;
            }
            .custom-huge-title {
                color: #000000 !important;
            }
            .block-container {
                padding: 0 !important;
                max-width: 100% !important;
                background-color: #ffffff !important;
                color: #000000 !important;
            }
        }
        </style>
    """, unsafe_allow_html=True)

    lang = st.session_state.get("language", "de")
    is_de = lang == "de"

    TXT_S = {
        "title": "Grafische Statistik & Analysen" if is_de else "Graphical Statistics & Analytics",
        "desc": "Visuelle Auswertungen der Standort-Kosten, Vertragsarten und Einsparpotenziale" if is_de else "Visual evaluations of location costs, contract types and savings potentials",
        "chart1": "📈 Kostenverteilung nach Standorten (Ist vs. Benchmark)" if is_de else "📈 Cost Distribution by Locations (Actual vs. Benchmark)",
        "chart2": "� Bestand nach Firmen" if is_de else "🏢 Portfolio by Companies",
        "chart3": "📊 Einsparpotenzial nach Firmen" if is_de else "📊 Savings Potential by Companies",
        "no_data": "Keine Daten für die grafische Statistik vorhanden." if is_de else "No data available for graphical statistics.",
        "btn_print": "🖨️ Ansicht drucken / PDF" if is_de else "🖨️ Print View / PDF",
        "filter_location": "Standort filtern:" if is_de else "Filter locations:",
        "kpi_total": "Gesamtbestand" if is_de else "Total portfolio",
        "kpi_benchmark": "Benchmark" if is_de else "Benchmark",
        "kpi_savings": "Einsparpotenzial" if is_de else "Savings potential",
        "kpi_locations": "Standorte" if is_de else "Locations",
        "summary_title": "Executive Summary" if is_de else "Executive Summary",
        "risk_title": "Risikostratifizierung nach Standort" if is_de else "Risk segmentation by location",
        "risk_col_loc": "Standort" if is_de else "Location",
        "risk_col_cost": "Bestand" if is_de else "Portfolio",
        "risk_col_bench": "Benchmark" if is_de else "Benchmark",
        "risk_col_gap": "Differenz" if is_de else "Gap",
        "risk_col_level": "Risikostufe" if is_de else "Risk level"
    }

    conn = hole_datenbank_verbindung()
    df_stat = pd.DataFrame()
    if conn is not None:
        try:
            q = """
                SELECT 
                    v.vertragsname, v.vertragsart, v.standort_text, 
                    v.kosten_bestand_pa, v.benchmark_ais_pa, f.firmenname AS firma
                FROM vertragsanalyse v
                LEFT JOIN firmeninfo f ON v.firma_id = f.id
            """
            df_stat = pd.read_sql(q, conn)
        except Exception:
            try:
                df_stat = pd.read_sql("SELECT * FROM vertragsanalyse", conn)
            except:
                pass
        finally:
            try:
                conn.close()
            except:
                pass

    col_t1, col_t2 = st.columns([7.0, 3.0])
    with col_t1:
        st.markdown(f"<div class='custom-huge-title'>{TXT_S['title']}</div>", unsafe_allow_html=True)
    with col_t2:
        st.write("")
        if not df_stat.empty:
            print_html = f"""
            <div style="text-align: right;">
                <button onclick="parent.window.print();" style="background-color: #0ea5e9; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 13px; width: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.2); font-family: sans-serif;">
                    {TXT_S['btn_print']}
                </button>
            </div>
            """
            components.html(print_html, height=45)

    st.markdown(f"<div style='font-size: 13px; color: var(--text-color); opacity: 0.7; margin-top: 6px; margin-bottom: 25px;'>{TXT_S['desc']}</div>", unsafe_allow_html=True)

    if not df_stat.empty:
        df_stat['kosten_bestand_pa'] = pd.to_numeric(df_stat['kosten_bestand_pa']).fillna(0.0)
        df_stat['benchmark_ais_pa'] = pd.to_numeric(df_stat['benchmark_ais_pa']).fillna(0.0)
        df_stat['einspar_potenzial'] = df_stat['kosten_bestand_pa'] - df_stat['benchmark_ais_pa']

        standorte = sorted(df_stat['standort_text'].dropna().astype(str).unique().tolist())
        if standorte:
            selected_standorte = st.multiselect(
                TXT_S['filter_location'],
                standorte,
                default=standorte,
                key='statistik_standort_filter'
            )
            df_filtered = df_stat[df_stat['standort_text'].astype(str).isin(selected_standorte)].copy() if selected_standorte else df_stat.copy()
        else:
            df_filtered = df_stat.copy()

        gesamt_bestand = df_filtered['kosten_bestand_pa'].sum()
        gesamt_benchmark = df_filtered['benchmark_ais_pa'].sum()
        gesamt_savings = gesamt_bestand - gesamt_benchmark
        gesamt_standorte = df_filtered['standort_text'].nunique()

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric(TXT_S['kpi_total'], f"{gesamt_bestand:,.2f} €")
        with kpi2:
            st.metric(TXT_S['kpi_benchmark'], f"{gesamt_benchmark:,.2f} €")
        with kpi3:
            st.metric(TXT_S['kpi_savings'], f"{gesamt_savings:,.2f} €")
        with kpi4:
            st.metric(TXT_S['kpi_locations'], f"{gesamt_standorte}")

        st.write("")

        risk_df = df_filtered.groupby('standort_text', as_index=False).agg(
            bestand=('kosten_bestand_pa', 'sum'),
            benchmark=('benchmark_ais_pa', 'sum'),
            differenz=('einspar_potenzial', 'sum')
        )
        risk_df['risiko_stufe'] = risk_df['differenz'].apply(lambda value: 'Hoch' if value > 0 else 'Niedrig')
        risk_df = risk_df.sort_values('differenz', ascending=False)

        st.markdown(f"#### {TXT_S['summary_title']}")
        st.dataframe(
            risk_df.head(10).rename(columns={
                'standort_text': TXT_S['risk_col_loc'],
                'bestand': TXT_S['risk_col_cost'],
                'benchmark': TXT_S['risk_col_bench'],
                'differenz': TXT_S['risk_col_gap'],
                'risiko_stufe': TXT_S['risk_col_level']
            }).style.format({
                TXT_S['risk_col_cost']: '{:,.2f} €',
                TXT_S['risk_col_bench']: '{:,.2f} €',
                TXT_S['risk_col_gap']: '{:,.2f} €'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.write("")
        st.markdown(f"##### {TXT_S['chart1']}")
        std_df = df_filtered.groupby('standort_text')[['kosten_bestand_pa', 'benchmark_ais_pa']].sum()
        std_df = std_df.rename(columns={'kosten_bestand_pa': 'Bestandskosten (€)', 'benchmark_ais_pa': 'Benchmark (€)'})
        st.bar_chart(std_df, use_container_width=True)

        st.write("")
        col_s1, col_s2 = st.columns(2)

        with col_s1:
            st.markdown(f"##### {TXT_S['chart2']}")
            if 'firma' in df_filtered.columns:
                firma_bestand_df = df_filtered.groupby('firma', dropna=False)['kosten_bestand_pa'].sum().sort_values(ascending=False).head(10)
                st.bar_chart(firma_bestand_df, use_container_width=True)
            else:
                st.info("Keine Firmen-Daten verfügbar.")

        with col_s2:
            st.markdown(f"##### {TXT_S['chart3']}")
            if 'firma' in df_filtered.columns:
                firma_einspar_df = (
                    df_filtered.groupby('firma', dropna=False)
                    .apply(lambda group: (group['kosten_bestand_pa'].sum() - group['benchmark_ais_pa'].sum()))
                    .sort_values(ascending=False)
                    .head(10)
                )
                st.bar_chart(firma_einspar_df, use_container_width=True)
            else:
                st.info("Keine Firmen-Daten verfügbar.")
    else:
        st.info(TXT_S["no_data"])