# Office-Konvertierungsskript (ODF & PDF/A Normalisierung)

Dieses Skript automatisiert die Normalisierung von Office-Dokumenten, Tabellen und Präsentationen für die Langzeitarchivierung. Es überführt proprietäre Formate (wie Microsoft Office oder Apple Pages) in offene Archivierungsstandards. Ziel ist es, für jede Quelldatei zwei Derivate zu erstellen: eine Bearbeitungskopie im OpenDocument-Format (ODF) und eine visuelle Repräsentation im PDF/A-Format (ISO-Standard).

Das Skript nutzt LibreOffice im "Headless"-Modus (ohne grafische Oberfläche) als leistungsstarke Konvertierungs-Engine.

---

## Hauptfunktionen

*   Duale Archivierungs-Strategie:
    *   Schritt 1: Konvertierung in das entsprechende ODF-Format (.odt, .ods, .odp).
    *   Schritt 2: Export der ODF-Datei in das PDF/A-Format (Level 2b) für die langfristige visuelle Erhaltung.
*   PDF-Aufwertung: Bestehende Standard-PDFs werden automatisch in das PDF/A-Format überführt.
*   Umfassende Format-Unterstützung: Verarbeitet moderne (.docx, .xlsx) ebenso wie obsolete Formate (.doc, .xls, .rtf, .wpd, Apple Pages, StarOffice etc.).
*   Namenskonvention: Erzeugte Dateien folgen dem Schema "Originalname.Originalendung.Zielendung" (z.B. bericht.doc.pdf), um die Provenienz eindeutig zu dokumentieren.
*   Intelligente Dubletten-Vermeidung: Das Skript erkennt bereits erzeugte Derivate und überspringt diese, um unnötige Rechenzeit zu sparen.
*   Fortschrittsanzeige: Eine grafische Fortschrittsleiste zeigt den Status der Stapelverarbeitung und den aktuell verarbeiteten Dateinamen an.
*   Fehlertoleranz: Fehlerhafte Einzeldateien führen nicht zum Abbruch des Skripts, sondern werden im Log dokumentiert.

---

## Technische Voraussetzungen

Um dieses Skript auszuführen, müssen folgende Programme installiert sein:

1.  Python 3.10+
2.  LibreOffice: Das Skript erwartet die soffice.exe standardmäßig unter:
    C:/Program Files/LibreOffice/program/soffice.exe

---

## Unterstützte Formate (Auszug)

*   Text: .doc, .docx, .rtf, .odt, .wpd, .wps, .pages, .txt, .html, .cwk
*   Tabellen: .xls, .xlsx, .ods, .sxc, .fods
*   Präsentationen: .ppt, .pptx, .odp, .key, .pps
*   Container: .pdf (Normalisierung zu PDF/A)

---

## Erwartete Ordnerstruktur

Das Skript operiert innerhalb der Transfer-Stufe (Stufe 3) des Workflows:

    Documents/
    └── data/
        └── [AC-Nummer]/
            └── [Datenträger-ID]/
                └── 3_[Datenträger-ID]_for-transfer/
                    ├── files/                      <-- QUELLORDNER
                    └── 3_[ID]_text-conversion.log <-- ZIEL DES LOGS

---

## Ausführung

Das Skript wird über die Kommandozeile mit der AC-Nummer und der Datenträger-ID gestartet.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_112233
    set DISK_ID=DISK_OFFICE_01
    python office_converter.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Systemprüfung: Das Skript validiert die Pfade und stellt sicher, dass LibreOffice erreichbar ist.
2. Indexierung: Rekursiver Scan des files-Ordners. Quelldateien werden identifiziert; Derivate werden ausgeschlossen.
3. ODF-Phase: LibreOffice erzeugt die ODF-Zwischendatei.
4. PDF/A-Phase: Ein spezieller Export-Filter erzwingt die Erstellung einer PDF/A-konformen Datei.
5. Logging: Jeder Schritt (Erfolg oder Fehler) wird mit Zeitstempel in der Datei ..._text-conversion.log protokolliert.
6. Abschluss: Das Skript bietet an, den Ordner mit den Ergebnissen im Explorer zu öffnen.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT