# YARA-Regelsammlung für Dateiformat-Identifizierung (rules.yar)

Diese Datei enthält eine umfassende Sammlung von YARA-Regeln, die speziell für die Identifizierung und Validierung von Dateiformaten in digitalen Archiven entwickelt wurden. Sie dient als signaturbasierte Wissensdatenbank für Tools wie den "filetrove"-Metadaten-Extraktor, um Dateitypen anhand ihrer binären Struktur (Magic Bytes) und spezifischer Inhaltsmuster sicher zu bestimmen.

Die Regeln ordnen den gefundenen Dateien technische Metadaten wie PRONOM-IDs und beschreibende Notizen zu.

---

## Hauptfunktionen

*   Binäre Identifizierung: Nutzt präzise Hex-Signaturen (Magic Bytes) am Dateianfang für Formate wie PDF, OLE (DOC/XLS), ZIP, JPEG und TIFF.
*   Inhaltsanalyse: Sucht nach spezifischen XML-Namespaces oder Zeichenketten innerhalb von Containern (z.B. zur Unterscheidung zwischen Standard-PDF und archivsicherem PDF/A).
*   Heuristische Erkennung: Enthält intelligente Logiken für schwierige Formate:
    *   CSV: Erkennt tabellarische Strukturen durch Zählen von Trennzeichen in den ersten 2048 Bytes.
    *   SAM/EML: Identifiziert Lotus AmiPro und E-Mail-Dateien anhand ihrer Header-Felder.
*   Ausschluss-Logik (Generic TXT): Eine spezialisierte Fallback-Regel klassifiziert Dateien als "Plain Text", wenn sie keine bekannten binären Signaturen aufweisen, aber lesbare Inhalte enthalten.
*   Archiv-Validierung: Erkennt verschachtelte Strukturen in modernen Office-Formaten (DOCX, PPTX, ODF), die technisch gesehen ZIP-Container sind.

---

## Abgedeckte Format-Kategorien

1.  Dokumente & Texte:
    *   Microsoft Word (DOC, DOCX), RTF, Apple Pages, Lotus AmiPro (SAM), Plain Text (TXT).
2.  E-Mail & Datenbanken:
    *   Outlook Express (DBX), E-Mail Messages (EML), JSON.
3.  Präsentationen & Tabellen:
    *   PowerPoint (PPT, PPTX), OpenDocument (ODP), Apple Keynote (KEY), Corel/Lotus Freelance (PRZ, SHW).
    *   Excel (XLS), CSV (Komma-getrennt).
4.  Multimedia (Audio & Video):
    *   MP3, WAV (RIFF), FLAC.
    *   MP4, AVI, Matroska (MKV).
5.  Bildformate:
    *   JPEG, PNG, TIFF, GIF, BMP.
6.  Markup-Sprachen:
    *   Generic XML, MusicXML (komprimiert/unkomprimiert), HTML, XHTML.

---

## Technische Details & Integration

Die Datei ist im Standard-YARA-Format verfasst und kann von jedem Tool geladen werden, das die `yara-python` Bibliothek oder das YARA-Kommandozeilenwerkzeug unterstützt.

Beispiel für den Aufbau einer Regel:

    rule PDF {
        meta:
            pronom_id = "fmt/18"
            note = "Adobe PDF (kein PDF/A)"
        strings:
            $pdf = {25 50 44 46 2D} // %PDF-
            $pdfaid = "xmlns:pdfaid="
        condition:
            $pdf at 0 and not $pdfaid
    }

### Verwendung im Workflow

Im Archivierungsworkflow wird diese Datei primär vom Metadaten-Skript genutzt:
1. Das Skript lädt `rules.yar`.
2. Jede zu archivierende Datei wird gegen alle Regeln geprüft.
3. Die Treffer (Matches) werden extrahiert und in die finale XML-Indexdatei übernommen, um eine präzise Identifizierung über die Dateiendung hinaus zu ermöglichen.

---

## Lizenz & Urheberrecht

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Diese Regelsammlung ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT