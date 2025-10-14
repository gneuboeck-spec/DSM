# Dateinamen-Wiederhersteller mit Siegfried

Dieses Verzeichnis enthält ein Python-Skript, um Dateiendungen für Dateien wiederherzustellen, die diese durch Kopiervorgänge zwischen verschiedenen Betriebssystemen (insbesondere von klassischem Mac OS) verloren haben. Es nutzt das professionelle Dateiidentifikations-Tool **Siegfried**, um den wahren Dateityp anhand des Inhalts zu erkennen und die korrekte Endung anzuhängen.

## Zweck des Skripts

Beim Transfer von alten Dateien, insbesondere von klassischen Mac-Systemen, gehen oft die Metadaten verloren, die den Dateityp definieren. Das Ergebnis sind "nackte" Dateien ohne Endung, die von modernen Betriebssystemen als "Ausführbare Unix-Datei" oder "Dokument" falsch interpretiert werden.

Dieses Skript löst dieses Problem automatisiert:

1.  **Dateisuche:** Es durchsucht rekursiv einen angegebenen Ordner nach allen Dateien, die entweder **keine Dateiendung** haben oder eine **unbekannte Endung** besitzen.
2.  **Inhaltsanalyse:** Jede dieser Dateien wird mit **Siegfried** analysiert. Siegfried liest die "Magic Numbers" (die ersten Bytes einer Datei), um den exakten Dateityp aus der PRONOM-Datenbank zu ermitteln (z.B. "Microsoft Word for Macintosh Document").
3.  **Intelligente Umbenennung:** Das Skript gleicht das Ergebnis von Siegfried mit einer internen "Übersetzungsliste" (`siegfried_to_ext_map`) ab. Wenn ein bekanntes Format erkannt wird, benennt es die Datei um, indem es die korrekte Endung anhängt (z.B. `MeinBrief` wird zu `MeinBrief.doc`).
4.  **Sicherheitsmodus (`DRY_RUN`):** Standardmäßig läuft das Skript in einem Simulationsmodus. Es zeigt nur an, welche Dateien es umbenennen *würde*, ohne tatsächlich Änderungen vorzunehmen.

---

## Technische Voraussetzungen

### 1. Python
*   **Version:** 3.6 oder neuer.
*   **Bibliotheken:** Keine externen Bibliotheken erforderlich. Das Skript verwendet nur Standardbibliotheken.

### 2. Siegfried
*   **Zweck:** Dies ist das **zentrale Analysewerkzeug**. Das Skript ist auf eine funktionierende Installation von Siegfried angewiesen.
*   **Installation:** Siegfried muss auf Ihrem System installiert und über die Kommandozeile als `sf` erreichbar sein (d.h. im System-`PATH`).
    *   **macOS:** Am einfachsten via [Homebrew](https://brew.sh/): `brew install siegfried`
    *   **Windows:** Laden Sie die `sf.exe` von der [offiziellen Webseite](https://www.itforarchivists.com/siegfried/) herunter und legen Sie sie in ein Verzeichnis, das in Ihrer `PATH`-Umgebungsvariable enthalten ist.

---

## Konfiguration im Skript

Vor der Ausführung müssen die folgenden Variablen am Anfang des Skripts angepasst werden:

*   `base_path`: Der absolute Pfad zum Hauptordner, in dem die Suche nach Dateien ohne Endung beginnen soll.
*   `siegfried_to_ext_map`: Das Python-Dictionary, das die "Übersetzungsregeln" enthält. Hier legen Sie fest, welches Siegfried-Ergebnis zu welcher Dateiendung führt.
*   `DRY_RUN`: Setzen Sie diesen Wert auf `False`, um die Dateien tatsächlich umzubenennen, nachdem Sie die Simulationsausgabe überprüft haben.

---

## Anpassung für neue Dateitypen

Das Skript ist so konzipiert, dass es leicht "lernen" kann, neue Dateitypen zu erkennen. Wenn das Skript im Simulationsmodus läuft und eine Zeile wie diese ausgibt:

`❓ Nicht zugeordnet: 'MeineAlteGrafik' (Erkannt als: MacPaint Image)`

... können Sie dem Skript den neuen Dateityp wie folgt beibringen:

1.  **Informationen sammeln:**
    *   Erkannter Name: `MacPaint Image`
    *   Korrekte Endung (recherchiert): `.pntg`

2.  **Skript anpassen:** Öffnen Sie das Skript und fügen Sie einen neuen Eintrag zur `siegfried_to_ext_map`-Liste hinzu:

    ```python
    siegfried_to_ext_map = {
        "Microsoft Word for Macintosh Document": ".doc",
        "AppleWorks Word Processing": ".cwk",
        # ... andere Einträge ...
        "MacPaint Image": ".pntg"  # <-- NEUER EINTRAG
    }
    ```

3.  **Erneut ausführen:** Wenn Sie das Skript jetzt erneut im Simulationsmodus starten, wird es die Datei korrekt zuordnen:
    `[SIMULATION]: 'MeineAlteGrafik' -> 'MeineAlteGrafik.pntg' (Erkannt als: MacPaint Image)`

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Passen Sie den `base_path` im Skript an.
3.  Führen Sie das Skript aus (standardmäßig im sicheren `DRY_RUN`-Modus).
    ```bash
    python3 add_extensions_with_siegfried.py
    ```
4.  Überprüfen Sie die Ausgabe. Passen Sie bei Bedarf die `siegfried_to_ext_map` an und wiederholen Sie Schritt 3.
5.  Wenn Sie mit dem Ergebnis zufrieden sind, setzen Sie `DRY_RUN = False` im Skript und führen Sie es erneut aus, um die Dateien umzubenennen.