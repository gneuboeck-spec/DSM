# Intelligenter Dateinamen-Wiederhersteller

Dieses Verzeichnis enthält ein Python-Skript, um Dateiendungen für Dateien wiederherzustellen, die diese verloren haben (z.B. durch Kopiervorgänge von klassischen Mac-Systemen). Es nutzt die professionellen Kommandozeilen-Tools **Siegfried** und **FFprobe**, um den wahren Dateityp anhand des Inhalts zu erkennen und die korrekte Endung intelligent anzuhängen.

## Zweck des Skripts

Beim Transfer von alten Dateien gehen oft die Metadaten verloren, die den Dateityp definieren. Das Ergebnis sind "nackte" Dateien ohne Endung, die von modernen Betriebssystemen falsch interpretiert werden. Dieses Skript löst dieses Problem durch eine mehrstufige, automatisierte Analyse.

**Der Prozess im Überblick:**

1.  **Dateisuche:** Das Skript durchsucht rekursiv einen angegebenen Ordner nach allen Dateien, die **keine Dateiendung** besitzen.
2.  **Inhaltsanalyse mit Siegfried:** Jede endungslose Datei wird mit Siegfried analysiert. Siegfried liest die "Magic Numbers" (die ersten Bytes einer Datei), um den exakten Dateityp aus der PRONOM-Datenbank zu ermitteln und liefert Formatname, PRONOM-ID und MIME-Typ.
3.  **Intelligente Umbenennung:** Das Skript verwendet eine Prioritäten-Kaskade, um die korrekteste Dateiendung zu bestimmen:
    *   **Priorität 1 (Manuelle PRONOM-Regeln):** Zuerst prüft es, ob für die gefundene PRONOM-ID eine Regel in der `pronom_to_ext_map` existiert. Dies dient als präzises "Override" für mehrdeutige Fälle.
    *   **Priorität 2 (Tiefenanalyse mit FFprobe):** Für generische Containerformate wie MPEG-4 (`fmt/199`) wird **FFprobe** aufgerufen, um zu prüfen, ob die Datei eine Videospur enthält. Basierend darauf wird intelligent zwischen `.mp4` (mit Video) und `.m4a` (nur Audio) unterschieden.
    *   **Priorität 3 (Automatische MIME-Typ-Erkennung):** Wenn die oberen Regeln nicht greifen, versucht das Skript, aus dem von Siegfried gelieferten MIME-Typ automatisch die Standard-Dateiendung abzuleiten. Dies deckt die meisten gängigen Formate ab.
    *   **Priorität 4 (Manuelle Formatnamen-Regeln):** Als letzter Fallback dient die `format_name_to_ext_map`.
4.  **Sicherheitsmodus (`DRY_RUN`):** Standardmäßig läuft das Skript in einem Simulationsmodus. Es zeigt nur an, welche Dateien es umbenennen *würde*, ohne tatsächlich Änderungen vorzunehmen.

---

## Technische Voraussetzungen

### 1. Python
*   **Version:** 3.8 oder neuer (wegen `shutil.which`).
*   **Bibliotheken:** Keine externen Python-Bibliotheken erforderlich.

### 2. Externe Kommandozeilen-Tools
Alle der folgenden Programme müssen installiert und systemweit verfügbar sein (d.h. ihre Verzeichnisse müssen zur **Systemumgebungsvariable `PATH`** hinzugefügt werden).

| Werkzeug | Zweck | Installationshinweis |
| :--- | :--- | :--- |
| **Siegfried** | Primäre Dateiidentifikation | **macOS:** `brew install siegfried` / **Windows:** `sf.exe` von der Webseite |
| **FFmpeg** | Tiefenanalyse von Mediendateien (`ffprobe`) | **macOS:** `brew install ffmpeg` / **Windows:** Von [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) laden |

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts angepasst werden:

*   `base_path`: Der absolute Pfad zum Hauptordner, in dem die Suche nach Dateien ohne Endung beginnen soll.
*   `ffprobe_path_config`: Der exakte Pfad zur `ffprobe`-Executable. Wenn FFprobe im System-`PATH` ist, kann der Standardwert (`"ffprobe"`) meist beibehalten werden.
*   `pronom_to_ext_map`: Das wichtigste "Wörterbuch". Hier tragen Sie Regeln für Formate ein, die entweder keinen klaren MIME-Typ haben (z.B. ClarisWorks) oder bei denen Sie die automatische MIME-Erkennung übersteuern möchten.
*   `DRY_RUN`: Setzen Sie diesen Wert auf `False`, um die Dateien tatsächlich umzubenennen, nachdem Sie die Simulationsausgabe überprüft haben.

---

## Anpassung für neue Dateitypen

Das Skript ist so konzipiert, dass es die meisten Standardformate automatisch erkennt. Wenn Sie im Simulationsmodus eine Zeile wie diese sehen:

`❓ Nicht zugeordnet: 'MeineAlteDatei' (Erkannt als: Some Obscure Format)`

... können Sie dem Skript den neuen Dateityp am besten über die **PRONOM-ID** beibringen, die in der erweiterten Debug-Ausgabe angezeigt wird.

1.  **Informationen sammeln:**
    *   PRONOM ID (aus der Ausgabe): `fmt/123`
    *   Korrekte Endung (recherchiert): `.obscure`

2.  **Skript anpassen:** Öffnen Sie das Skript und fügen Sie einen neuen Eintrag zur **`pronom_to_ext_map`**-Liste hinzu:

    ```python
    pronom_to_ext_map = {
        # ... andere Einträge ...
        "fmt/123": ".obscure"  # <-- NEUER EINTRAG
    }
    ```

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Passen Sie den `base_path` und ggf. den `ffprobe_path_config` im Skript an.
3.  Führen Sie das Skript aus (standardmäßig im sicheren `DRY_RUN`-Modus).
    ```bash
    python3 dateityp_erkennen_dateiendung_anhaengen.py
    ```
4.  Überprüfen Sie die Ausgabe. Passen Sie bei Bedarf die `pronom_to_ext_map` an und wiederholen Sie Schritt 3.
5.  Wenn Sie mit dem Ergebnis zufrieden sind, setzen Sie `DRY_RUN = False` im Skript und führen Sie es erneut aus, um die Dateien umzubenennen.```