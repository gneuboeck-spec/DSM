# Dateinamen-Wiederhersteller mit Siegfried

Dieses Verzeichnis enthält ein Python-Skript, um Dateiendungen für Dateien wiederherzustellen, die diese durch Kopiervorgänge zwischen verschiedenen Betriebssystemen (insbesondere von klassischem Mac OS) verloren haben. Es nutzt das professionelle Dateiidentifikations-Tool **Siegfried**, um den wahren Dateityp anhand des Inhalts zu erkennen und die korrekte Endung automatisch oder über manuelle Regeln anzuhängen.

## Zweck des Skripts

Beim Transfer von alten Dateien, insbesondere von klassischen Mac-Systemen, gehen oft die Metadaten verloren, die den Dateityp definieren. Das Ergebnis sind "nackte" Dateien ohne Endung, die von modernen Betriebssystemen als "Ausführbare Unix-Datei" oder "Dokument" falsch interpretiert werden.

Dieses Skript löst dieses Problem automatisiert:

1.  **Dateisuche:** Es durchsucht rekursiv einen angegebenen Ordner nach allen Dateien, die entweder keine Dateiendung haben oder eine **unbekannte Endung** besitzen (d.h. eine Endung, die nicht in einer vordefinierten Sicherheitsliste steht).
2.  **Inhaltsanalyse:** Jede dieser Dateien wird mit **Siegfried** analysiert. Siegfried liest die "Magic Numbers" (die ersten Bytes einer Datei), um den exakten Dateityp aus der PRONOM-Datenbank zu ermitteln und liefert Formatname, PRONOM-ID und MIME-Typ.
3.  **Intelligente Umbenennung:** Das Skript verwendet eine mehrstufige Logik, um die korrekte Dateiendung zu bestimmen:
    *   **Priorität 1 (PRONOM ID):** Zuerst prüft es, ob für die von Siegfried gefundene PRONOM-ID (z.B. `fmt/846`) eine manuelle Regel in der `pronom_to_ext_map` existiert. Dies ist die präziseste Methode und hat Vorrang.
    *   **Priorität 2 (MIME-Typ):** Wenn keine PRONOM-Regel passt, versucht das Skript, aus dem von Siegfried gelieferten MIME-Typ (z.B. `application/msword`) automatisch die Standard-Dateiendung (`.doc`) abzuleiten. Dies deckt viele gängige Formate ab.
    *   **Priorität 3 (Formatname):** Als letzte Möglichkeit prüft das Skript, ob der von Siegfried erkannte Formatname in der `format_name_to_ext_map` als Fallback definiert ist.
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
*   `pronom_to_ext_map`: Das Python-Dictionary, das die **wichtigsten Übersetzungsregeln** enthält. Hier legen Sie fest, welche PRONOM-ID zu welcher Endung führt. Dies ist ideal für Formate ohne klaren MIME-Typ (z.B. ClarisWorks) oder wenn Sie eine bestimmte Endung erzwingen wollen.
*   `format_name_to_ext_map`: Dient als Fallback für Regeln, die auf dem reinen Formatnamen basieren.
*   `DRY_RUN`: Setzen Sie diesen Wert auf `False`, um die Dateien tatsächlich umzubenennen, nachdem Sie die Simulationsausgabe überprüft haben.

---

## Anpassung für neue Dateitypen

Das Skript ist so konzipiert, dass es viele Dateitypen automatisch über ihren MIME-Typ erkennt. Wenn Sie im Simulationsmodus eine Zeile wie diese sehen, die Sie aber zuordnen möchten:

`❓ Nicht zugeordnet: 'MeineAlteDatei' Some Obscure Format (ID: fmt/123, MIME: application/x-obscure)`

... können Sie dem Skript den neuen Dateityp am besten über die PRONOM-ID beibringen:

1.  **Informationen sammeln:**
    *   PRONOM ID: `fmt/123`
    *   Korrekte Endung (recherchiert): `.obscure`

2.  **Skript anpassen:** Öffnen Sie das Skript und fügen Sie einen neuen Eintrag zur **`pronom_to_ext_map`**-Liste hinzu:

    ```python
    pronom_to_ext_map = {
        "fmt/397": ".mus",
        "fmt/846": ".cwk",
        "fmt/123": ".obscure"  # <-- NEUER EINTRAG
    }
    ```

3.  **Erneut ausführen:** Wenn Sie das Skript jetzt erneut im Simulationsmodus starten, wird es die Datei korrekt zuordnen:
    `[SIMULATION]: 'MeineAlteDatei' -> 'MeineAlteDatei.obscure' [via PRONOM ID]`

---

## Ausführung

1.  Öffnen Sie ein Terminal (macOS) oder eine Eingabeaufforderung/PowerShell (Windows).
2.  Passen Sie den `base_path` im Skript an.
3.  Führen Sie das Skript aus (standardmäßig im sicheren `DRY_RUN`-Modus).
    ```bash
    python3 add_extensions_with_siegfried.py
    ```
4.  Überprüfen Sie die Ausgabe. Passen Sie bei Bedarf die `pronom_to_ext_map` an und wiederholen Sie Schritt 3.
5.  Wenn Sie mit dem Ergebnis zufrieden sind, setzen Sie `DRY_RUN = False` im Skript und führen Sie es erneut aus, um die Dateien umzubenennen.