# Umfassender Metadaten-Extraktor (Filetrove XML)

Dieses Skript ist ein hochentwickeltes Werkzeug zur tiefgehenden Analyse und Metadaten-Extraktion für eine Vielzahl von Dateiformaten. Es aggregiert Informationen aus einer Reihe von spezialisierten Kommandozeilen-Tools, vereinheitlicht die gesammelten Daten in ein konsistentes Schema und erstellt eine detaillierte, maschinenlesbare XML-Indexdatei (`.index`) für einen gesamten Datenträger.

Das Skript ist das Herzstück des Archivierungsworkflows und darauf ausgelegt, eine möglichst vollständige technische und deskriptive Dokumentation für jede einzelne Datei zu generieren. Es wird, wie die anderen Skripte im Workflow, über eine `start.bat` mit dynamischen Pfaden gesteuert.

## Hauptfunktionen

*   **Umfassende Metadaten-Extraktion:** Integriert eine Vielzahl von Werkzeugen, um ein breites Spektrum an Metadaten abzudecken:
    *   **ExifTool:** Für EXIF-, IPTC-, XMP- und herstellerspezifische Metadaten.
    *   **FFprobe:** Für technische Details von Audio- und Videodateien (Codecs, Bitrate, Dauer etc.).
    *   **Siegfried:** Zur robusten Dateiformat-Identifikation via PRONOM-Signaturen.
    *   **Mutagen:** Für Audio-Tags in Formaten wie MP3, FLAC, WAV etc.
    *   **Pillow (PIL):** Für technische Bildinformationen (Dimensionen, Farbmodus, ICC-Profile).
    *   **PyPDF2:** Zum Auslesen von PDF-spezifischen Metadaten (Seitenzahl, Erstellungsdatum).
    *   **YARA:** Zum Scannen von Dateien auf Basis von benutzerdefinierten Regeln (z.B. zur PII-Erkennung oder zur Identifikation spezifischer textbasierter Formate).
    *   **Brunnhilde:** Führt eine initiale, übergreifende Analyse des gesamten Verzeichnisses durch, um globale Statistiken, Warnungen und nicht identifizierte Dateien zu erfassen.

*   **Intelligente Metadaten-Vereinheitlichung:** Das Herzstück des Skripts. Eine komplexe Logik führt die Rohdaten aller Tools zusammen, entfernt Duplikate, priorisiert die verlässlichsten Quellen und mappt tausende verschiedene Metadaten-Tags auf ein sauberes, konsistentes Set von XML-Tags.

*   **Integrierte Validierungs-Checks:** Führt grundlegende Integritätsprüfungen für gängige Formate durch (z.B. PDF-Lesbarkeit, ZIP-Archiv-Integrität, Bild-Verifizierung), um den Zustand der Dateien zu bewerten.

*   **Strukturierte XML-Ausgabe:** Erzeugt eine einzige, gut formatierte `.index`-XML-Datei, die für jede Datei einen `<file>`-Eintrag mit allen extrahierten und vereinheitlichten Metadaten enthält.

---

## Technische Voraussetzungen

Die folgenden Programme und Python-Bibliotheken **MÜSSEN** auf dem System installiert und korrekt konfiguriert sein, damit das Skript funktioniert.

### Python-Bibliotheken
Diese müssen über `pip` installiert werden:
```bash
pip install yara-python mutagen pypdf2 pillow chardet
### Externe Kommandozeilen-Tools

Die Pfade zu diesen Programmen müssen am Anfang des Skripts korrekt eingetragen werden.

1.  **YARA:** Das Regel-Kompilierungswerkzeug. Benötigt wird eine `.yar`-Regeldatei.
2.  **ExifTool:** Das Standardwerkzeug für eingebettete Metadaten.
3.  **FFmpeg:** Benötigt wird die `ffprobe.exe` zur Analyse von Mediendateien.
4.  **Hachoir:** Ein weiteres Metadaten-Extraktionstool (`hachoir-metadata.exe`).
5.  **Siegfried:** Das primäre Werkzeug zur Dateiformat-Identifikation (`sf.exe`).

---

## Konfiguration im Skript

Vor der ersten Ausführung müssen die Pfade zu **allen** externen Werkzeugen am Anfang des Skripts überprüft und an die lokale Systemumgebung angepasst werden.
# --- 1. System-Pfade und Listen (manuell anpassen, falls nötig) ---
YARA_RULES_FILE = "C:\\Users\\digit\\Desktop\\Skripte\\rules.yar"
EXIFTOOL_PATH = "C:\\Program Files\\ExifTool\\exiftool.exe"
FFPROBE_PATH = "C:\\Program Files\\ffmpeg\\ffprobe.exe"
HACHOIR_METADATA_PATH = "C:\\Users\\digit\\.venv\\Scripts\\hachoir-metadata.exe"
SIEGFRIED_PATH = "C:\\Program Files\\Siegfried\\sf.exe"

### Erwartete Ordnerstruktur

Das Skript benötigt die folgende Verzeichnisstruktur im `Documents`-Ordner des Benutzers:
Documents
└── Datentraeger_sichern
    └── [AC-Nummer]
        └── [Datenträger-ID]
            └── 3_[Datenträger-ID]_for-transfer
                ├── Files  <-- AUS DIESEM ORDNER WERDEN DATEIEN ANALYSIERT
                └── (Hier wird die .index XML-Datei erstellt)

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

## Ausführung

Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python metadata_extractor_skript.py %AC_NUMBER% %DISK_ID%
pause

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die übergebenen Argumente, die Ordnerstruktur und die Existenz aller konfigurierten externen Tools.
2.  **Globale Analyse:** Zuerst wird **Brunnhilde** auf das gesamte `Files`-Verzeichnis angewendet, um eine Übersicht (Formatstatistiken, Warnungen, etc.) zu erstellen.
3.  **Iterative Verarbeitung:** Das Skript durchläuft nun jede einzelne Datei im `Files`-Verzeichnis.
4.  **Metadaten-Extraktion (pro Datei):** Für jede Datei wird eine Kaskade von Extraktions-Tools (Siegfried, ExifTool, FFprobe, etc.) ausgeführt. Alle Roh-Metadaten werden gesammelt.
5.  **Metadaten-Vereinheitlichung:** Die gesammelten Roh-Metadaten werden durch die `unify_metadata_keys`-Funktion verarbeitet, um ein sauberes, standardisiertes Set von Schlüssel-Wert-Paaren zu erzeugen.
6.  **Validierung (pro Datei):** Es werden grundlegende Integritätsprüfungen durchgeführt.
7.  **XML-Generierung:** Die vereinheitlichten Metadaten werden als XML-Tags unter einem `<file>`-Element zusammengefasst und dem Haupt-XML-Baum hinzugefügt.
8.  **Finalisierung:** Nachdem alle Dateien verarbeitet wurden, wird der vollständige XML-Baum in die finale `.index`-Datei geschrieben.
9.  **Abschluss:** Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.