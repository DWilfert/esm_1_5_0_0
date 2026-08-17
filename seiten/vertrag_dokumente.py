import streamlit as st
import os
from datenbank.befehle import hole_datenbank_verbindung
from logik.ui import render_page_header
import base64
import subprocess

def zeige_vertragsdokumente():
    st.markdown("""
        <style>
        input, select, textarea, div[data-baseweb="select"] span, label {
            font-size: 0.82rem !important;
        }
        div[data-testid="InputInstructions"] { display: none !important; }
        .doc-container {
            max-height: 520px;
            overflow-y: auto;
            padding-right: 5px;
        }
        .doc-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: rgba(148, 163, 184, 0.03);
            border: 1px solid rgba(148, 163, 184, 0.15);
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 8px;
        }
        .doc-name {
            font-size: 13px;
            font-weight: 500;
            color: inherit;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 240px;
        }
        </style>
    """, unsafe_allow_html=True)

    lang = st.session_state.get("language", "de")

    if lang == "de":
        TXT_DOC = {
            "title": "📂 Vertragsdokumente & Dateimanager",
            "desc": "Zentrale Ablage und Verwaltung aller PDF-Verträge, Wartungsprotokolle und Anhänge.",
            "sec_upload": "📤 Dokument hochladen",
            "sec_list": "📋 Verfügbare Dokumente im System",
            "sec_viewer": "👁️ Live PDF-Vorschau",
            "lbl_file": "PDF-Datei auswählen:",
            "btn_upload": "Dokument auf Server speichern",
            "success_up": "Dokument erfolgreich hochgeladen und gespeichert!",
            "empty": "Aktuell sind keine Dokumente im Verzeichnis hinterlegt.",
            "empty_view": "Bitte wählen Sie links ein Dokument aus, um die Vorschau anzuzeigen.",
            "download": "📥 Herunterladen",
            "open_external": "🖨️ Extern öffnen & Drucken",
            "delete": "🗑️ Löschen",
            "view": "👁️ Ansehen"
        }
    else:
        TXT_DOC = {
            "title": "📂 Contract Documents & File Manager",
            "desc": "Central repository and management of all PDF contracts, maintenance reports, and attachments.",
            "sec_upload": "📤 Upload Document",
            "sec_list": "📋 Available Documents in System",
            "sec_viewer": "👁️ Live PDF Preview",
            "lbl_file": "Select PDF file:",
            "btn_upload": "Save Document to Server",
            "success_up": "Document successfully uploaded and saved!",
            "empty": "Currently no documents are stored in the directory.",
            "empty_view": "Please select a document on the left to display the preview.",
            "download": "📥 Download",
            "open_external": "🖨️ Open Externally & Print",
            "delete": "🗑️ Delete",
            "view": "👁️ View"
        }

    render_page_header(TXT_DOC['title'], TXT_DOC['desc'])

    upload_verzeichnis = r"C:\esm_dokumente".replace("\\esm_", "\\esm_")
    conn_cfg = hole_datenbank_verbindung()
    if conn_cfg:
        cursor_cfg = None
        try:
            cursor_cfg = conn_cfg.cursor(dictionary=True)
            cursor_cfg.execute("SELECT wert FROM einstellungen WHERE schluessel = ?", ("dokumenten_pfad",))
            res = cursor_cfg.fetchone()
            if res and res.get('wert'):
                db_pfad = res['wert'].strip()
                if db_pfad != "":
                    upload_verzeichnis = db_pfad
        except Exception:
            pass
        finally:
            if cursor_cfg:
                cursor_cfg.close()
            if conn_cfg.is_connected():
                conn_cfg.close()

    if not os.path.exists(upload_verzeichnis):
        try:
            os.makedirs(upload_verzeichnis, exist_ok=True)
        except Exception:
            pass

    col1, col2 = st.columns([4.5, 5.5], gap="medium")

    with col1:
        with st.container(border=True):
            st.markdown(f"**{TXT_DOC['sec_upload']}**")
            st.markdown("<hr style='border: none; height: 1px; background-color: rgba(128, 128, 128, 0.3); margin: 10px 0;'>", unsafe_allow_html=True)
            
            uploaded_pdf = st.file_uploader(TXT_DOC["lbl_file"], type=["pdf", "png", "jpg"], key="vertrag_pdf_uploader")
            
            if uploaded_pdf is not None:
                if st.button(TXT_DOC["btn_upload"], type="primary", use_container_width=True):
                    sicherer_name = os.path.basename(uploaded_pdf.name)
                    datei_pfad = os.path.join(upload_verzeichnis, sicherer_name)
                    with open(datei_pfad, "wb") as f:
                        f.write(uploaded_pdf.getbuffer())
                    st.success(TXT_DOC["success_up"])
                    st.rerun()

        st.write("")
        with st.container(border=True):
            st.markdown(f"**{TXT_DOC['sec_list']}**")
            st.markdown(f"<div style='font-size: 11px; color: #64748b; margin-bottom: 8px;'>Pfad: <code>{upload_verzeichnis}</code></div>", unsafe_allow_html=True)
            st.markdown("<hr style='border: none; height: 1px; background-color: rgba(128, 128, 128, 0.3); margin: 10px 0;'>", unsafe_allow_html=True)
            
            vorhandene_dateien = []
            if os.path.exists(upload_verzeichnis):
                try:
                    vorhandene_dateien = sorted(os.listdir(upload_verzeichnis))
                except Exception:
                    vorhandene_dateien = []
            
            if vorhandene_dateien:
                selected_doc = st.session_state.get("selected_doc_viewer", None)
                st.markdown("<div class='doc-container'>", unsafe_allow_html=True)
                for datei in vorhandene_dateien:
                    f_pfad = os.path.join(upload_verzeichnis, datei)
                    if os.path.isfile(f_pfad):
                        c_name, c_vw, c_del = st.columns([4.2, 2.9, 2.9])
                        with c_name:
                            st.markdown(f"<div class='doc-name' title='{datei}'>📄 {datei}</div>", unsafe_allow_html=True)
                        with c_vw:
                            if st.button(TXT_DOC["view"], key=f"vw_doc_{datei}", use_container_width=True):
                                st.session_state.selected_doc_viewer = datei
                                st.rerun()
                        with c_del:
                            if st.button(TXT_DOC["delete"], key=f"del_doc_{datei}", use_container_width=True):
                                if selected_doc == datei:
                                    st.session_state.selected_doc_viewer = None
                                os.remove(f_pfad)
                                st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.info(TXT_DOC["empty"])

    with col2:
        with st.container(border=True):
            st.markdown(f"**{TXT_DOC['sec_viewer']}**")
            st.markdown("<hr style='border: none; height: 1px; background-color: rgba(128, 128, 128, 0.3); margin: 10px 0;'>", unsafe_allow_html=True)
            
            active_doc = st.session_state.get("selected_doc_viewer", None)
            if active_doc:
                target_path = os.path.join(upload_verzeichnis, active_doc)
                if os.path.exists(target_path):
                    col_info, col_dl, col_pr = st.columns([4.0, 3.0, 3.0])
                    with col_info:
                        st.markdown(f"<div style='font-size: 11px; font-weight: 600; color: #0ea5e9; padding-top: 6px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;' title='{active_doc}'>Datei: {active_doc}</div>", unsafe_allow_html=True)
                    with col_dl:
                        with open(target_path, "rb") as f_dl:
                            st.download_button(TXT_DOC["download"], f_dl.read(), file_name=active_doc, key="dl_active_pdf_viewer", use_container_width=True)
                    with col_pr:
                        if st.button(TXT_DOC["open_external"], key="btn_open_external_pdf", use_container_width=True):
                            try:
                                os.startfile(target_path)
                            except Exception:
                                try:
                                    subprocess.run(['xdg-open', target_path])
                                except Exception:
                                    try:
                                        subprocess.run(['open', target_path])
                                    except Exception:
                                        pass
                    
                    st.write("")
                    try:
                        with open(target_path, "rb") as pdf_file:
                            base64_pdf = base64.b64encode(pdf_file.read()).decode('utf-8')
                        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=1" width="100%" height="600px" type="application/pdf"></iframe>'
                        st.markdown(pdf_display, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Fehler beim Laden der PDF-Vorschau: {e}")
                else:
                    st.warning("Die ausgewählte Datei wurde im Verzeichnis nicht gefunden.")
                    st.session_state.selected_doc_viewer = None
            else:
                st.info(TXT_DOC["empty_view"])