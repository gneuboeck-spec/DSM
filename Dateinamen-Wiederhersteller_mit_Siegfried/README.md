# Skript zur Reparatur von Dateiendungen

Dieses Skript ist ein spezialisiertes Werkzeug zur Wiederherstellung von Dateien, denen eine Dateiendung fehlt. Es analysiert den Inhalt jeder endungslosen Datei, um ihren wahren Typ zu ermitteln und benennt sie entsprechend um.

Das Skript ist für die Integration in einen standardisierten Archivierungsworkflow konzipiert. Es wird über Kommandozeilenargumente gesteuert, die typischerweise von einer Start-Datei (`start.bat`) übergeben werden, und erwartet eine spezifische Ordnerstruktur.

## Hauptfunktionen

*   **Intelligente Dateianalyse:** Verwendet eine mehrstufige Logik, um den korrekten Dateityp zu bestimmen.
*   **Siegfried-Integration:** Nutzt Siegfried (`sf.exe`) als primäres Werkzeug zur Identifizierung von Dateiformaten anhand von Signaturen.
*   **Erweiterte Fallback-Logik:** Wenn Siegfried keine eindeutige Antwort liefert, kommen spezialisierte Routinen zum Einsatz, um z.B. verschiedene Tabellenformate (CSV, SYLK) oder OpenDocument-Typen zu erkennen.
*   **Multimedia-Prüfung:** Verwendet FFprobe (`ffprobe.exe`), um bei MPEG-4-Containern zwischen Videodateien (`.mp4`) und reinen Audiodateien (`.m4a`) zu unterscheiden.
*   **Sicherheitsmechanismen:** Beinhaltet einen `DRY_RUN`-Modus (Testlauf), um Umbenennungen zu simulieren, ohne Dateien tatsächlich zu verändern.
*   **Detaillierte Protokollierung:** Jede Aktion – ob erfolgreich, fehlgeschlagen oder simuliert – wird in einer Log-Datei festgehalten.
*   **Dynamische Pfad-Konfiguration:** Alle Arbeitsverzeichnisse werden automatisch basierend auf einer `AC-Nummer` und einer `Datenträger-ID` abgeleitet.

---

## Analyse-Methoden

Das Skript findet alle Dateien ohne Endung und analysiert sie in einem mehrstufigen Prozess:

1.  **Stufe 1: Siegfried-Analyse**
    *   Jede Datei wird zuerst mit Siegfried (`sf.exe`) gescannt.
    *   Das Ergebnis (PRONOM-ID, MIME-Typ) wird mit einer internen Mapping-Tabelle (`pronom_to_ext_map`) abgeglichen, um eine Endung zuzuweisen.
    *   Ein generisches `text/plain`-Ergebnis von Siegfried wird bewusst ignoriert, um die genauere Fallback-Analyse für Textdateien zu erzwingen.

2.  **Stufe 2: Fallback-Analyse (wenn Stufe 1 fehlschlägt)**
    *   **ZIP-Archiv-Prüfung:** Das Skript prüft, ob es sich um eine ZIP-Datei handelt. Wenn ja, sucht es nach einer `mimetype`-Datei im Inneren, was typisch für OpenDocument-Formate (`.odt`, `.ods`, `.odp`) ist.
    *   **XML-Inhaltsprüfung:** Es wird nach spezifischen XML-Tags in Textdateien gesucht, die auf "flache" OpenDocument-Formate hinweisen.
    *   **Text-Tabellen-Analyse:** Eine spezielle Funktion prüft den Dateiinhalt auf Signaturen (z.B. `ID;` für SYLK `.slk`-Dateien) oder auf eine konsistente Struktur mit Trennzeichen (`;`, `,`, `\t`), um CSV-Dateien zu identifizieren.
    *   **Allgemeine Textdatei-Prüfung:** Als letzte Instanz wird geprüft, ob die Datei überwiegend aus druckbaren Textzeichen besteht und dann als `.txt` klassifiziert.

---

## Technische Voraussetzungen

Die folgenden Programme müssen installiert und über den System-`PATH` global aufrufbar sein:

1.  **Python:** Version 3.6 oder neuer.
2.  **Siegfried:** Die `sf.exe` muss im `PATH` verfügbar sein.
3.  **FFmpeg:** Die `ffprobe.exe` muss für die Multimedia-Analyse im `PATH` verfügbar sein.

---

## Konfiguration

*   **`DRY_RUN` (Testlauf):** Im Skript kann die globale Variable `DRY_RUN = True` gesetzt werden. In diesem Modus werden alle Aktionen nur simuliert und protokolliert, ohne dass Dateien tatsächlich umbenannt werden.
*   **`pronom_to_ext_map`:** Wenn das Skript unbekannte Dateitypen findet, aber eine PRONOM-ID im Log anzeigt, kann diese ID manuell zur Mapping-Tabelle im Skript hinzugefügt werden, um die Erkennung zukünftig zu verbessern.

---

## Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:
Documents
└── Datentraeger_sichern
    └── [AC-Nummer]
        └── [Datenträger-ID]
            └── 3_[Datenträger-ID]_for-transfer
                ├── Files  <-- IN DIESEM ORDNER WIRD GESUCHT
                └── (Hier wird die Log-Datei erstellt)

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

---

## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python repair_extensions_skript.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die übergebenen Argumente, die Ordnerstruktur und die Verfügbarkeit von `sf.exe` und `ffprobe.exe`.
2.  **Suche:** Das `Files`-Verzeichnis wird rekursiv nach Dateien ohne Dateiendung durchsucht.
3.  **Analyse & Umbenennung:** Jede gefundene Datei durchläuft den oben beschriebenen, mehrstufigen Analyseprozess. Bei erfolgreicher Identifizierung wird sie umbenannt.
4.  **Protokollierung:** Jede Aktion (Simulation, Umbenennung, Fehler, nicht identifizierte Datei) wird in die Log-Datei `3_[Datenträger-ID]_repair_file_extension.log` geschrieben.
5.  **Zusammenfassung:** Am Ende wird eine Übersicht über die Anzahl der umbenannten und nicht zugeordneten Dateien ausgegeben.
6.  **Abschluss:** Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.