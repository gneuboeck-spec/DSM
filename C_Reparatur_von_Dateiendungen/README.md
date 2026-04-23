# Skript zur Reparatur von Dateiendungen (Stage 2 zu Stage 3)

Dieses Skript ist ein spezialisiertes Werkzeug zur Wiederherstellung von Dateiendungen. Es analysiert den Inhalt jeder endungslosen Datei, um den korrekten Typ zu ermitteln, und benennt die Dateien entsprechend um. Ein besonderes Merkmal ist der automatisierte Workflow, der Daten von der Extraktionsstufe (Stage 2) in die Transferstufe (Stage 3) überführt.

Das Skript wird über Kommandozeilenargumente gesteuert, die typischerweise von einer Start-Datei (start.bat) übergeben werden.

---

## Hauptfunktionen

*   Automatischer Datentransfer: Wenn das Zielverzeichnis in Stufe 3 noch nicht existiert, kopiert das Skript automatisch alle Daten von Stufe 2 (extracted-files) nach Stufe 3 (for-transfer).
*   Siegfried-Integration: Nutzt Siegfried (sf.exe) unter dem fest hinterlegten Pfad C:\Program Files\Siegfried\sf.exe zur Identifizierung von Dateiformaten.
*   Multimedia-Unterscheidung: Verwendet FFprobe, um bei MPEG-4-Dateien (fmt/199) zwischen Video (.mp4) und reinem Audio (.m4a) zu unterscheiden.
*   Erweiterte Fallback-Logik:
    *   ZIP-Analyse: Erkennt OpenDocument-Formate (.odt, .ods) in ZIP-Containern.
    *   XML-Prüfung: Identifiziert "Flat XML" Dokumente.
    *   Tabellen-Erkennung: Erkennt CSV-Strukturen und SYLK-Dateien (.slk) anhand von Delimitern und Signaturen.
    *   Text-Validierung: Klassifiziert unbekannte Dateien als .txt, wenn sie überwiegend aus druckbaren Zeichen bestehen.
*   Protokollierung: Erstellt ein detailliertes Log im Zielordner zur Nachvollziehbarkeit aller Änderungen.

---

## TREE-Struktur & Dateipfade

Das Skript bildet die Brücke zwischen der Extraktion und der aktiven Bearbeitung:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 2_[ID]_extracted-files/
│   └── files/                              <-- QUELLE (Eingabe)
└── 3_[ID]_for-transfer/                    <-- ZIEL (Arbeitsbereich)
    ├── files/                              <-- Hier werden Endungen repariert
    └── 3_[ID]_for-transfer_repair-file-extension.log <-- ZIEL (Ablaufprotokoll)

---

## Technische Voraussetzungen

1.  Python: Version 3.10 oder neuer empfohlen.
2.  Siegfried: Muss unter C:\Program Files\Siegfried\sf.exe installiert sein.
3.  FFmpeg: Die ffprobe.exe muss im System-PATH verfügbar sein.

---

## Analyse-Methoden

1. Stufe: Siegfried (PRONOM & MIME)
Das Skript gleicht Siegfried-Ergebnisse mit einer Mapping-Tabelle ab. MIME-Typen werden zur Bestimmung der Endung herangezogen, sofern sie nicht generisch (octet-stream) sind.

2. Stufe: Fallback-Routinen
Sollte Siegfried kein Ergebnis liefern, werden die Datei-Header auf ZIP- oder XML-Signaturen geprüft. Textdateien werden auf Tabellen-Strukturen (Trennzeichen-Häufigkeit) untersucht.

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python repair_extensions.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Vorbereitung: Falls der Ordner in Stufe 3 fehlt, wird der Inhalt von Stufe 2 komplett dorthin kopiert.
2. Validierung: Prüfung der Pfade zu Siegfried und FFprobe.
3. Suche: Rekursive Suche nach Dateien ohne Suffix im Ordner Stage 3/files.
4. Analyse & Rename: Durchführung der Identifizierung und Umbenennung. Bereits existierende Zieldateien führen zur automatischen Nummerierung (z.B. datei_1.jpg).
5. Logging: Jede Aktion wird mit Zeitstempel und Identifikationsquelle (z.B. "via PRONOM") protokolliert.
6. Abschluss: Zusammenfassung der erfolgreichen und nicht zugeordneten Dateien.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT