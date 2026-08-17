# ESM Vertrags- & Wartungsmanagement

Demo-Version ohne echte MySQL-Verbindung.

## Überblick
Diese Version ist für GitHub-Demonstrationen und lokale Präsentationen vorbereitet. Wenn keine reale MySQL-Instanz konfiguriert ist, nutzt die App automatisch eine in-memory SQLite-Datenbank mit 10 Demo-Datensätzen.

## Schnellstart

1. Installieren:
   ```bash
   pip install -r requirements.txt
   ```
2. Starten:
   ```bash
   streamlit run app.py
   ```

## Demo-Modus
Der Demo-Modus ist standardmäßig aktiv. Die App simuliert eine MySQL-Verbindung mit 10 Demo-Datensätzen und läuft damit ohne echte Datenbank.

Wenn du eine echte MySQL-Verbindung nutzen möchtest, setze:

```bash
set ESM_USE_REAL_DB=1
```

und stelle danach `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE` passend ein oder nutze `st.secrets["mysql"]`.

## Hinweis
Die Datei `.streamlit/secrets.toml` ist in `.gitignore` enthalten und darf nicht für GitHub veröffentlicht werden. Wenn du echte Datenbankzugangsdaten brauchst, lege sie lokal außerhalb des Repositories an.
