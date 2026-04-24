# Skript zur Reparatur von Dateiendungen (Stufe 2 zu Stufe 3)

Dieses Skript ist ein spezialisiertes Werkzeug zur Wiederherstellung von Dateiendungen. Es analysiert den Inhalt jeder endungslosen Datei, um den korrekten Typ zu ermitteln, und benennt die Dateien entsprechend um. Ein besonderes Merkmal ist der automatisierte Workflow, der Daten von der Extraktionsstufe (Stufe 2) in die Transferstufe (Stufe 3) überführt.

---

## Hauptfunktionen

*   **Automatischer Datentransfer:** Wenn das Zielverzeichnis in Stufe 3 noch nicht existiert, kopiert das Skript automatisch alle Daten von Stufe 2 (`2_[ID]_extracted-files/files`) nach Stufe 3 (`3_[ID]_for-transfer/files`).
*   **Siegfried-Integration:** Nutzt Siegfried (`sf.exe`) unter dem fest hinterlegten Pfad `C:\Program Files\Siegfried\sf.exe` zur Identifizierung von Dateiformaten via PRONOM und MIME.
*   **Multimedia-Unterscheidung:** Verwendet `ffprobe.exe`, um bei MPEG-4-Dateien (`fmt/199`) zwischen Video (`.mp4`) und reinem Audio (`.m4a`) zu unterscheiden.
*   **Erweiterte Fallback-Logik:**
    *   **ZIP-Analyse:** Erkennt OpenDocument-Formate (`.odt`, `.ods`) innerhalb von ZIP-Containern.
    *   **XML-Prüfung:** Identifiziert "Flat XML" Dokumente.
    *   **Tabellen-Erkennung:** Erkennt CSV-Strukturen und SYLK-Dateien (`.slk`) anhand von Delimitern und Signaturen.
    *   **Text-Validierung:** Klassifiziert unbekannte Dateien als `.txt`, wenn der Inhalt überwiegend aus druckbaren Zeichen besteht (UTF-8/Latin-1).
*   **Protokollierung:** Erstellt ein detailliertes Log-File direkt im Stufe-3-Ordner zur vollständigen Nachvollziehbarkeit.

---

## TREE-Struktur & Dateipfade

Das Skript bildet die Brücke zwischen der Extraktion und der aktiven Bearbeitung:

```text
[AC-Nummer]/[Datenträger-ID]/
├── 2_[ID]_extracted-files/
│   └── files/                              <-- QUELLE (Daten aus der Extraktion)
└── 3_[ID]_for-transfer/                    <-- ZIEL (Arbeitsbereich für Stufe 3)
    ├── files/                              <-- Hier werden Endungen repariert
    └── 3_[ID]_for-transfer_repair-file-extension.log <-- LOG-DATEI
```
---

## Technische Voraussetzungen

1.  **Python:** Version 3.10 oder neuer empfohlen.
2.  **Siegfried:** Muss zwingend unter `C:\Program Files\Siegfried\sf.exe` installiert sein.
3.  **FFmpeg:** Die `ffprobe.exe` muss im System-PATH verfügbar sein.

---

## Ausführung

Das Skript kann auf zwei Arten gestartet werden:

1.  **Automatisiert (Empfohlen):** Übergabe der AC-Nummer und Datenträger-ID als Argumente via Kommandozeile oder `start.bat`.
    Beispiel: `python repair_extensions.py AC_0001 CD_01`
2.  **Interaktiv:** Falls keine Argumente übergeben werden, fragt das Skript die AC-Nummer und die ID beim Start manuell ab.

### Ablauf der Ausführung

1.  **Vorbereitung:** Falls der Ordner in Stufe 3 fehlt, wird der Inhalt von Stufe 2 komplett dorthin kopiert.
2.  **Validierung:** Prüfung der Pfade zu Siegfried und FFprobe.
3.  **Suche:** Rekursive Suche nach Dateien ohne Suffix im Ordner `Stage 3/files`.
4.  **Analyse & Rename:** Durchführung der Identifizierung. Falls die Zieldatei bereits existiert, erfolgt eine automatische Nummerierung (z.B. `datei_1.jpg`).
5.  **Logging:** Jede Aktion wird mit Zeitstempel und Quelle (z.B. "via PRONOM ID (Manuell)") im Log protokolliert.
6.  **Abschluss:** Ausgabe einer Zusammenfassung und optionale Abfrage zum Öffnen des Zielordners im Explorer.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT