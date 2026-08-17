import streamlit as st
import pandas as pd
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import prepare_display_dataframe, render_page_header

def zeige_firmeninfo():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label, .stRadio div {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        div[data-testid="stDataFrame"] {
            background-color: var(--secondary-background-color) !important;
            border: 1px solid rgba(128, 128, 128, 0.25) !important;
            border-radius: 0.5rem;
            padding: 2px;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'language' not in st.session_state:
        st.session_state.language = "de"

    TXT_FIRMA = {
        "de": {
            "title": "🏢 Firmen- & Dienstleisterverwaltung",
            "desc": "Zentrale Verwaltung der Wartungsfirmen direkt aus der MySQL-Datenbank.",
            "act_lbl": "Aktion wählen:",
            "act_list": "Firmenübersicht",
            "act_add": "Neue Firma anlegen",
            "act_edit": "Firma bearbeiten",
            "sel_del": "Firma auswählen zum Bearbeiten / Löschen / Verträge anzeigen:",
            "sel_edit": "Firma auswählen zum Bearbeiten:",
            "btn_del": "Firma unwiderruflich aus MySQL löschen",
            "succ_del": "Firma erfolgreich gelöscht!",
            "btn_save": "Firma in MySQL speichern",
            "btn_update": "Änderungen in MySQL speichern",
            "succ_save": "Neue Firma erfolgreich angelegt!",
            "succ_update": "Firmendaten erfolgreich aktualisiert!",
            "empty_db": "Keine Firmen in der MySQL-Tabelle 'firmeninfo' vorhanden.",
            "vertrag_title": "📑 Verknüpfte Verträge & Anlagen für",
            "no_contracts": "ℹ️ Keine aktiven Verträge für diese Firma in MySQL hinterlegt.",
            "bitte_waehlen": "--- Bitte wählen ---",
            "sicherheitsabfrage": "Sicherheitsabfrage: Wirklich löschen?",
            "err_name": "Bitte mindestens den Firmennamen angeben!"
        },
        "en": {
            "title": "🏢 Company & Contractor Management",
            "desc": "Central management of maintenance contractors directly from the MySQL database.",
            "act_lbl": "Select action:",
            "act_list": "Company List",
            "act_add": "Add New Company",
            "act_edit": "Edit Company",
            "sel_del": "Select company to edit / delete / view contracts:",
            "sel_edit": "Select company to edit:",
            "btn_del": "Permanently delete company from MySQL",
            "succ_del": "Company deleted successfully!",
            "btn_save": "Save Company to MySQL",
            "btn_update": "Save Changes to MySQL",
            "succ_save": "New company created successfully!",
            "succ_update": "Company details updated successfully!",
            "empty_db": "No companies available in MySQL table 'firmeninfo'.",
            "vertrag_title": "📑 Linked Contracts & Assets for",
            "no_contracts": "ℹ️ No active contracts found for this company in MySQL.",
            "bitte_waehlen": "--- Please select ---",
            "sicherheitsabfrage": "Security check: Really delete?",
            "err_name": "Please provide at least the company name!"
        }
    }[st.session_state.language]

    render_page_header(TXT_FIRMA['title'], TXT_FIRMA['desc'])

    firma_aktion = st.radio(
        TXT_FIRMA["act_lbl"],
        [TXT_FIRMA["act_list"], TXT_FIRMA["act_add"], TXT_FIRMA["act_edit"]],
        horizontal=True,
        key="firmen_haupt_aktion_radio_v1"
    )
    st.write("")

    conn = hole_datenbank_verbindung()
    df_firmen = pd.DataFrame()
    if conn is not None:
        try:
            df_firmen = pd.read_sql("SELECT * FROM firmeninfo", conn)
        except Exception:
            pass
        finally:
            try:
                conn.close()
            except:
                pass

    if firma_aktion == TXT_FIRMA["act_list"]:
        if not df_firmen.empty:
            anzeige_df = df_firmen.drop(columns=["id", "zugewiesen"], errors="ignore")
            st.dataframe(prepare_display_dataframe(anzeige_df), use_container_width=True, hide_index=True)
            
            st.write("---")
            
            firmen_mapping = {
                row["id"]: str(row.get("firmenname", "Unbenannt"))
                for _, row in df_firmen.iterrows()
            }
            id_liste = [None] + list(firmen_mapping.keys())
            
            col_sel, _ = st.columns([3.5, 6.5])
            with col_sel:
                ausgewaehlte_firma_id = st.selectbox(
                    TXT_FIRMA["sel_del"], 
                    options=id_liste,
                    format_func=lambda x: TXT_FIRMA["bitte_waehlen"] if x is None else firmen_mapping[x],
                    key="firmen_del_selectbox_v1"
                )

            if ausgewaehlte_firma_id is not None:
                gefundener_firmenname = firmen_mapping[ausgewaehlte_firma_id]

                st.markdown("<hr style='margin: 25px 0; border: none; border-top: 1px solid rgba(128, 128, 128, 0.3);'>", unsafe_allow_html=True)
                st.markdown(f"##### {TXT_FIRMA['vertrag_title']} **{gefundener_firmenname}**")

                conn_v = hole_datenbank_verbindung()
                df_v_filtered = pd.DataFrame()
                if conn_v:
                    try:
                        query = """
                            SELECT 
                                a.anlagenr AS 'Anlagen-Nr', 
                                a.anlagebezeichnung AS 'Anlagenbezeichnung', 
                                v.standort_text AS 'Standort (Excel)', 
                                v.vertragsname AS 'Vertragsname',
                                v.zyklus_monate AS 'Intervall (Monate)' 
                            FROM vertragsanalyse v
                            JOIN anlagen a ON v.anlage_id = a.id
                            WHERE v.firma_id = ?
                        """
                        df_v_filtered = pd.read_sql(query, conn_v, params=(ausgewaehlte_firma_id,))
                    except Exception:
                        pass
                    finally:
                        try:
                            conn_v.close()
                        except:
                            pass

                if not df_v_filtered.empty:
                    st.dataframe(df_v_filtered, use_container_width=True, hide_index=True)
                else:
                    st.info(TXT_FIRMA["no_contracts"])

                st.write("")
                bestaetigt_del = st.checkbox(
                    TXT_FIRMA["sicherheitsabfrage"],
                    key="firmen_del_checkbox_confirm"
                )
                if bestaetigt_del:
                    if st.button(TXT_FIRMA["btn_del"], key="firmen_del_action_btn"):
                        conn_del = hole_datenbank_verbindung()
                        if conn_del:
                            cur = None
                            try:
                                cur = conn_del.cursor()
                                cur.execute("DELETE FROM firmeninfo WHERE id = %s", (ausgewaehlte_firma_id,))
                                conn_del.commit()
                                st.success(TXT_FIRMA["succ_del"])
                                st.rerun()
                            except Exception as e:
                                st.error(f"Fehler beim Löschen: {e}")
                            finally:
                                if cur:
                                    try:
                                        cur.close()
                                    except:
                                        pass
                                try:
                                    conn_del.close()
                                except:
                                    pass
        else:
            st.info(TXT_FIRMA["empty_db"])

    elif firma_aktion == TXT_FIRMA["act_add"]:
        with st.form("firma_anlegen_form", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                f_name = st.text_input("Firmenname *" if st.session_state.language == "de" else "Company Name *", placeholder="z.b. Lift Service GmbH", key="f_name_inp")
                f_art = st.text_input("Firmenart" if st.session_state.language == "de" else "Company Type", placeholder="z.b. Wartungsdienstleister", key="f_art_inp")
                f_adresse = st.text_input("Firmenadresse" if st.session_state.language == "de" else "Address", placeholder="z.b. Hauptstraße 12", key="f_adr_inp")
                f_telefon = st.text_input("Telefonnummer" if st.session_state.language == "de" else "Phone", placeholder="z.b. +49 89 1234567", key="f_tel_inp")
            with col_f2:
                f_fax = st.text_input("Fax", placeholder="z.b. +49 89 1234568", key="f_fax_inp")
                f_mail = st.text_input("E-Mail Adresse" if st.session_state.language == "de" else "Email", placeholder="z.b. info@liftservice.de", key="f_email_inp")
                f_website = st.text_input("Website", placeholder="z.b. www.liftservice.de", key="f_web_inp")
                f_ansprechpartner = st.text_input("Ansprechpartner" if st.session_state.language == "de" else "Contact Person", placeholder="z.b. Max Mustermann", key="f_ap_inp")

            if st.form_submit_button(TXT_FIRMA["btn_save"]):
                if not f_name:
                    st.error(TXT_FIRMA["err_name"])
                else:
                    conn_ins = hole_datenbank_verbindung()
                    if conn_ins:
                        cur = None
                        try:
                            cur = conn_ins.cursor()
                            sql = """INSERT INTO firmeninfo (firmenname, firmebranche, firmenadresse, firmentelefon, firmenfax, firmenEMail, firmenwebsite, firmenansprechpartner)
                                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                            val = (f_name, f_art, f_adresse, f_telefon, f_fax, f_mail, f_website, f_ansprechpartner)
                            cur.execute(sql, val)
                            conn_ins.commit()
                            st.success(TXT_FIRMA["succ_save"])
                            st.rerun()
                        except Exception as e:
                            st.error(f"Fehler beim Speichern in MySQL: {e}")
                        finally:
                            if cur:
                                try:
                                    cur.close()
                                except:
                                    pass
                            try:
                                conn_ins.close()
                            except:
                                pass

    elif firma_aktion == TXT_FIRMA["act_edit"]:
        if not df_firmen.empty:
            firmen_mapping = {
                row["id"]: str(row.get("firmenname", "Unbenannt"))
                for _, row in df_firmen.iterrows()
            }
            id_liste = [None] + list(firmen_mapping.keys())
            
            col_sel_ed, _ = st.columns([3.5, 6.5])
            with col_sel_ed:
                edit_firma_id = st.selectbox(
                    TXT_FIRMA["sel_edit"],
                    options=id_liste,
                    format_func=lambda x: TXT_FIRMA["bitte_waehlen"] if x is None else firmen_mapping[x],
                    key="firmen_edit_selectbox_v1"
                )

            if edit_firma_id is not None:
                row_firma = df_firmen[df_firmen["id"] == edit_firma_id].iloc[0]
                
                st.write("")
                with st.form("firma_bearbeiten_form"):
                    col_fe1, col_fe2 = st.columns(2)
                    with col_fe1:
                        up_name = st.text_input("Firmenname *" if st.session_state.language == "de" else "Company Name *", value=str(row_firma.get("firmenname", "")), key="up_f_name")
                        up_art = st.text_input("Firmenart" if st.session_state.language == "de" else "Company Type", value=str(row_firma.get("firmebranche", "")), key="up_f_art")
                        up_adresse = st.text_input("Firmenadresse" if st.session_state.language == "de" else "Address", value=str(row_firma.get("firmenadresse", "")), key="up_f_adr")
                        up_telefon = st.text_input("Telefonnummer" if st.session_state.language == "de" else "Phone", value=str(row_firma.get("firmentelefon", "")), key="up_f_tel")
                    with col_fe2:
                        up_fax = st.text_input("Fax", value=str(row_firma.get("firmenfax", "")), key="up_f_fax")
                        up_mail = st.text_input("E-Mail Adresse" if st.session_state.language == "de" else "Email", value=str(row_firma.get("firmenEMail", "")), key="up_f_email")
                        up_website = st.text_input("Website", value=str(row_firma.get("firmenwebsite", "")), key="up_f_web")
                        up_ansprechpartner = st.text_input("Ansprechpartner" if st.session_state.language == "de" else "Contact Person", value=str(row_firma.get("firmenansprechpartner", "")), key="up_f_ap")

                    st.write("")
                    if st.form_submit_button(TXT_FIRMA["btn_update"], type="primary"):
                        if not up_name:
                            st.error(TXT_FIRMA["err_name"])
                        else:
                            conn_up = hole_datenbank_verbindung()
                            if conn_up:
                                cur = None
                                try:
                                    cur = conn_up.cursor()
                                    sql = """UPDATE firmeninfo SET firmenname = %s, firmebranche = %s, firmenadresse = %s, 
                                             firmentelefon = %s, firmenfax = %s, firmenEMail = %s, firmenwebsite = %s, 
                                             firmenansprechpartner = %s WHERE id = %s"""
                                    val = (up_name, up_art, up_adresse, up_telefon, up_fax, up_mail, up_website, up_ansprechpartner, edit_firma_id)
                                    cur.execute(sql, val)
                                    conn_up.commit()
                                    st.success(TXT_FIRMA["succ_update"])
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Fehler beim Aktualisieren: {e}")
                                finally:
                                    if cur:
                                        try:
                                            cur.close()
                                        except:
                                            pass
                                    try:
                                        conn_up.close()
                                    except:
                                        pass
        else:
            st.info(TXT_FIRMA["empty_db"])