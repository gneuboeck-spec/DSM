# Deep Metadata Extraction & Indexing Tool (filetrove + Brunnhilde)

Dieses Skript ist ein hochleistungsfähiges Werkzeug zur technischen Charakterisierung und Inventarisierung digitaler Archive. Es kombiniert die Tiefenanalyse mehrerer Experten-Tools (Siegfried, ExifTool, FFprobe, Hachoir, YARA) mit einem automatisierten Scan durch Brunnhilde (inkl. ClamAV-Virenprüfung). Das Ergebnis ist ein umfassender Master-Index (.index) im XML-Format, der den physischen Zustand, die Integrität und alle verfügbaren Metadaten jeder Datei dokumentiert.

Das Skript ist für den Einsatz in der Transfer-Stufe (Stufe 3) konzipiert und dient als zentrale Dokumentationsinstanz vor der Langzeitarchivierung.

---

## Hauptfunktionen

*   **Vollautomatisierter Analyse-Workflow:**
    *   **Brunnhilde-Integration:** Führt Brunnhilde über das gesamte Quellverzeichnis aus, um Formatstatistiken, Siegfried-Warnungen und nicht identifizierte Dateien zu erfassen.
    *   **Integrierter Virenscan:** Nutzt ClamAV innerhalb von Brunnhilde und extrahiert Funde direkt in den Master-Index.
    *   **Windows-Workaround:** Erzeugt manuell eine `tree.txt` (Verzeichnisstruktur), um bekannte Einschränkungen unter Windows zu umgehen.
*   **Multi-Tool Metadaten-Erfassung:**
    *   **Siegfried:** Dateiformat-Identifizierung nach PRONOM-Standard.
    *   **ExifTool:** Umfassende Metadaten aus Bildern, Dokumenten und Medien.
    *   **FFprobe:** Technische Details zu Audio- und Videostreams.
    *   **Hachoir:** Ergänzende technische Datenextraktion.
    *   **YARA:** Signaturbasierte Inhaltsanalyse zur Validierung von Dateitypen (z. B. SAM, EML, CSV).
*   **Integrität & Validierung:**
    *   **SHA-256 Hashing:** Berechnet für jedes Objekt eine kryptografische Prüfsumme.
    *   **Validitäts-Check:** Prüft aktiv die Funktionalität von Dateien (z. B. PDF-Struktur, ZIP-Integrität, Bild-Verifizierung).
*   **Metadaten-Harmonisierung:**
    *   Überführt hunderte unterschiedliche Tool-Tags in ein kontrolliertes XML-Schema.
    *   Bereinigt Werte von ungültigen XML-Steuerzeichen zur Vermeidung von Fehlern in Folgesystemen.
    *   Filtert redundante oder datenschutzrelevante Tags über eine umfangreiche Blockliste.

---

## Technische Voraussetzungen

Die folgenden Programme müssen installiert und im System-Pfad (PATH) erreichbar sein oder im Skript-Header konfiguriert werden:

1.  **Python 3.10+** (Bibliotheken: mutagen, PyPDF2, Pillow, yara-python, chardet, beautifulsoup4).
2.  **Brunnhilde:** Muss als Python-Modul installiert sein (`pip install brunnhilde`).
3.  **ExifTool:** exiftool.exe.
4.  **Siegfried:** sf.exe.
5.  **FFmpeg/FFprobe:** ffprobe.exe.
6.  **Hachoir:** hachoir-metadata.exe.
7.  **YARA:** Eine gültige YARA-Regeldatei (`rules.yar`).
8.  **ClamAV (Optional):** Für Virenscans innerhalb von Brunnhilde.

---

## Konfiguration im Skript

Passen Sie die Pfade zu den Tools im Abschnitt KONFIGURATION an:

    YARA_RULES_FILE = r"C:\Pfad\zu\rules.yar"
    EXIFTOOL_PATH = r"C:\Program Files\ExifTool\exiftool.exe"
    SIEGFRIED_PATH = r"C:\Program Files\Siegfried\sf.exe"

### Erwartete Ordnerstruktur

Das Skript arbeitet innerhalb der Transfer-Stufe (Stufe 3) des Archivierungsworkflows:

    Documents/data/
    └── [AC-Nummer]/
        └── [Datenträger-ID]/
            └── 3_[ID]_for-transfer/
                ├── files/                      <-- QUELLORDNER (Eingabe)
                ├── 3_[ID]_for-transfer.index   <-- ZIELDATEI (Master-Index)
                └── 3_[ID]_for-transfer_Brunnhilde/ <-- Detailberichte

---

## Ausführung

Das Skript wird über die Kommandozeile mit der AC-Nummer und der Datenträger-ID gestartet.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python metadata_master_index.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. **Vorphase:** Ausführung von Brunnhilde zur Erstellung der Basis-Statistiken und Durchführung des Virenscans.
2. **Scan-Phase:** Rekursive Erfassung aller Dateien im `files/`-Ordner.
3. **Extraktions-Phase:** Jede Datei wird nacheinander von allen konfigurierten Tools analysiert.
4. **Harmonisierung:** Zusammenführung der Metadaten, Korrektur von Namenskonventionen und Konsistenzprüfung (z.B. Videodimensionen).
5. **Validierung:** Prüfung, ob die Datei technisch einwandfrei lesbar ist.
6. **Finalisierung:** Speicherung des Master-Index (.index) im XML-Format.
7. **Abschluss:** Optionale Öffnung des Zielordners im Datei-Explorer.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT