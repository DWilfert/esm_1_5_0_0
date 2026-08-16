import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import render_page_header

def format_currency(val):
    if pd.isnull(val):
        return "0,00 €"
    return "{:,.2f} €".format(val).replace(",", "X").replace(".", ",").replace("X", ".")

def zeige_buchhaltung():
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
        .buchhalter-card {
            background: rgba(148, 163, 184, 0.02);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(128, 128, 128, 0.25) !important;
            border-radius: 0.5rem;
            padding: 4px;
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

    TXT_B = {
        "title": "Buchhaltung & Finanz-Controlling" if is_de else "Bookkeeping & Financial Controlling",
        "desc": "Klassische BWA-Auswertung, Standort-Kostenstellen und vertragliche Liquiditätsvorschau" if is_de else "Classic BWA evaluation, location cost centers and contractual liquidity forecast",
        "tab1": "Kostenstellen & BWA" if is_de else "Cost Centers & BWA",
        "tab2": "Liquiditäts- & Fälligkeitsvorschau" if is_de else "Liquidity & Due Date Forecast",
        "tab3": "Kassen- & Belegübersicht" if is_de else "Cash & Receipt Overview",
        "sec_standort": "📊 Auswertung nach Standorten (Kostenstellen)" if is_de else "📊 Evaluation by Locations (Cost Centers)",
        "sec_cash": "📅 Monatliche Budget- & Zahlungsbelastung" if is_de else "📅 Monthly Budget & Payment Load",
        "no_data": "Keine kaufmännischen Vertragsdaten in der Datenbank gefunden." if is_de else "No commercial contract data found in database.",
        "btn_print": "🖨️ BWA drucken / PDF" if is_de else "🖨️ Print BWA / PDF",
        "kpi_total": "Gesamt Kosten" if is_de else "Total costs",
        "kpi_benchmark": "Benchmark" if is_de else "Benchmark",
        "kpi_saving": "Einsparung" if is_de else "Savings",
        "kpi_sites": "Standorte" if is_de else "Locations",
        "summary_title": "Executive Financial Summary" if is_de else "Executive Financial Summary",
        "summary_loc": "Kostenstelle" if is_de else "Cost center",
        "summary_cost": "Kosten" if is_de else "Costs",
        "summary_bench": "Benchmark" if is_de else "Benchmark",
        "summary_gap": "Differenz" if is_de else "Gap"
    }

    conn = hole_datenbank_verbindung()
    df_finanzen = pd.DataFrame()
    if conn is not None:
        try:
            q = """
                SELECT 
                    v.id, v.vertragsname, v.vertragsart, v.standort_text, 
                    v.kosten_bestand_pa, v.benchmark_ais_pa, v.naechste_wartung, 
                    v.zyklus_monate, f.firmenname AS firma
                FROM vertragsanalyse v
                LEFT JOIN firmeninfo f ON v.firma_id = f.id
            """
            df_finanzen = pd.read_sql(q, conn)
        except Exception:
            try:
                df_finanzen = pd.read_sql("SELECT * FROM vertragsanalyse", conn)
            except:
                pass
        finally:
            try:
                conn.close()
            except:
                pass

    col_b1, col_b2 = st.columns([7.0, 3.0])
    with col_b1:
        render_page_header(TXT_B['title'], TXT_B['desc'])
    with col_b2:
        st.write("")
        if not df_finanzen.empty:
            print_html_b = f"""
            <div style="text-align: right;">
                <button onclick="parent.window.print();" style="background-color: #0ea5e9; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 13px; width: 100%; box-shadow: 0 2px 5px rgba(0,0,0,0.2); font-family: sans-serif;">
                    {TXT_B['btn_print']}
                </button>
            </div>
            """
            components.html(print_html_b, height=45)

    if not df_finanzen.empty:
        df_finanzen['kosten_bestand_pa'] = pd.to_numeric(df_finanzen['kosten_bestand_pa']).fillna(0.0)
        df_finanzen['benchmark_ais_pa'] = pd.to_numeric(df_finanzen['benchmark_ais_pa']).fillna(0.0)
        df_finanzen['einsparung'] = df_finanzen['kosten_bestand_pa'] - df_finanzen['benchmark_ais_pa']

        t_bwa1, t_bwa2, t_bwa3 = st.tabs([TXT_B["tab1"], TXT_B["tab2"], TXT_B["tab3"]])

        with t_bwa1:
            st.markdown(f"##### {TXT_B['sec_standort']}")
            st.write("")

            std_gruppe = df_finanzen.groupby('standort_text').agg(
                Anzahl_Vertraege=('vertragsname', 'count'),
                Gesamtkosten_Bestand=('kosten_bestand_pa', 'sum'),
                Gesamtkosten_Benchmark=('benchmark_ais_pa', 'sum'),
                Potenzielle_Einsparung=('einsparung', 'sum')
            ).reset_index()

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            with kpi1:
                st.metric(label=TXT_B['kpi_total'], value=format_currency(std_gruppe['Gesamtkosten_Bestand'].sum()))
            with kpi2:
                st.metric(label=TXT_B['kpi_benchmark'], value=format_currency(std_gruppe['Gesamtkosten_Benchmark'].sum()))
            with kpi3:
                st.metric(label=TXT_B['kpi_saving'], value=format_currency(std_gruppe['Potenzielle_Einsparung'].sum()))
            with kpi4:
                st.metric(label=TXT_B['kpi_sites'], value=str(std_gruppe['standort_text'].nunique()))

            st.write("")
            st.markdown(f"#### {TXT_B['summary_title']}")
            st.dataframe(
                std_gruppe.rename(columns={
                    'standort_text': TXT_B['summary_loc'],
                    'Gesamtkosten_Bestand': TXT_B['summary_cost'],
                    'Gesamtkosten_Benchmark': TXT_B['summary_bench'],
                    'Potenzielle_Einsparung': TXT_B['summary_gap']
                }).style.format({
                    TXT_B['summary_cost']: '{:,.2f} €',
                    TXT_B['summary_bench']: '{:,.2f} €',
                    TXT_B['summary_gap']: '{:,.2f} €'
                }),
                use_container_width=True,
                hide_index=True
            )

            std_gruppe['Gesamtkosten_Bestand_Fmt'] = std_gruppe['Gesamtkosten_Bestand'].apply(format_currency)
            std_gruppe['Gesamtkosten_Benchmark_Fmt'] = std_gruppe['Gesamtkosten_Benchmark'].apply(format_currency)
            std_gruppe['Potenzielle_Einsparung_Fmt'] = std_gruppe['Potenzielle_Einsparung'].apply(format_currency)

            anzeige_bwa = std_gruppe[['standort_text', 'Anzahl_Vertraege', 'Gesamtkosten_Bestand_Fmt', 'Gesamtkosten_Benchmark_Fmt', 'Potenzielle_Einsparung_Fmt']].rename(columns={
                'standort_text': 'Standort / Kostenstelle',
                'Anzahl_Vertraege': 'Aktive Verträge',
                'Gesamtkosten_Bestand_Fmt': 'Jahreskosten (Ist)',
                'Gesamtkosten_Benchmark_Fmt': 'Jahreskosten (Benchmark)',
                'Potenzielle_Einsparung_Fmt': 'Einsparpotenzial p.a.'
            })

            st.dataframe(anzeige_bwa, use_container_width=True, hide_index=True)

            st.write("")
            col_k1, col_k2, col_k3 = st.columns(3)
            ges_ist = df_finanzen['kosten_bestand_pa'].sum()
            ges_bench = df_finanzen['benchmark_ais_pa'].sum()
            ges_einsp = ges_ist - ges_bench

            with col_k1:
                st.metric("Summe Jahreskosten (Ist)", format_currency(ges_ist))
            with col_k2:
                st.metric("Summe Benchmark (Soll)", format_currency(ges_bench))
            with col_k3:
                st.metric("Gesamteinsparung", format_currency(ges_einsp), delta=f"{(ges_einsp/ges_ist*100):.1f}%" if ges_ist > 0 else "0%")

        with t_bwa2:
            st.markdown(f"##### {TXT_B['sec_cash']}")
            st.write("")

            df_finanzen['naechste_wartung'] = pd.to_datetime(df_finanzen['naechste_wartung'], errors='coerce')
            aktuelles_jahr = datetime.now().year
            
            monats_Namen = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]
            monats_last = {m: 0.0 for m in monats_Namen}

            for _, row in df_finanzen.iterrows():
                dt = row['naechste_wartung']
                kosten = row['kosten_bestand_pa']
                zyklus = int(row['zyklus_monate']) if pd.notnull(row['zyklus_monate']) and int(row['zyklus_monate']) > 0 else 12

                if pd.notnull(dt):
                    akt_dt = dt
                    while akt_dt.year <= aktuelles_jahr:
                        if akt_dt.year == aktuelles_jahr:
                            m_idx = akt_dt.month - 1
                            monats_last[monats_Namen[m_idx]] += kosten / (12 / zyklus if zyklus <= 12 else 1)
                        akt_dt += pd.Timedelta(days=zyklus * 30.44)

            cash_df = pd.DataFrame([
                {"Monat": m, "Erwartete Belastung": format_currency(val)} 
                for m, val in monats_last.items()
            ])

            st.dataframe(cash_df, use_container_width=True, hide_index=True)
            st.info("💡 Diese Liquiditätsvorschau basiert auf den vertraglichen Wartungszyklen und den hinterlegten Jahreskosten (Ideal für den Kassensturz des Buchhalters).")

        with t_bwa3:
            st.markdown("##### 📋 Vollständiges Konten- und Vertragsjournal")
            st.write("")
            
            Journal_df = df_finanzen[['vertragsname', 'vertragsart', 'firma', 'standort_text', 'kosten_bestand_pa']].copy()
            Journal_df['kosten_bestand_pa'] = Journal_df['kosten_bestand_pa'].apply(format_currency)
            Journal_df = Journal_df.rename(columns={
                'vertragsname': 'Vertragsbezeichnung',
                'vertragsart': 'Art',
                'firma': 'Dienstleister / Kreditor',
                'standort_text': 'Kostenstelle',
                'kosten_bestand_pa': 'Betrag p.a.'
            })
            st.dataframe(Journal_df, use_container_width=True, hide_index=True)
    else:
       st.info(TXT_B["no_data"])