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

## Detaillierte Hinweise zur YARA-Regelsammlung

### Aufbau einer Regel

Jede Regel folgt diesem Grundmuster:

rule REGELNAME {
    meta:
        pronom_id = "fmt/XXX"
        note = "Beschreibung des Formats"
    strings:
        $variable1 = {HEX BYTES}
        $variable2 = "Textstring"
    condition:
        Bedingung mit $variable1, $variable2
}

### Verwendete Meta-Felder

| Feld | Bedeutung | Beispiel |
|------|-----------|----------|
| pronom_id | PRONOM-Identifikator (falls bekannt) | `fmt/18` für PDF |
| note | Beschreibender Text | `"Adobe PDF (kein PDF/A)"` |

Nicht alle Regeln haben ein `pronom_id`-Feld. Für proprietäre oder weniger verbreitete Formate (z.B. Apple Pages, Lotus AmiPro, Corel Presentations) ist nur `note` vorhanden.

### Wichtige Regeln im Detail

**PDF vs. PDF/A**
- `rule PDF`: Erkennt Standard-PDF (%PDF- am Anfang, aber kein pdfaid-Namespace)
- `rule PDFA`: Erkennt PDF/A (%PDF- am Anfang + Namespace + Teil 1,2 oder 3)

**CSV (heuristisch)**
- Sucht nach 3 Vorkommen des Patterns `(\r\n|\n|\r|^)[^\r\n,]+(,[^\r\n,]+)+` in den ersten 2048 Bytes
- Schliesst bekannte Formate aus (XML, RTF, PDF, HTML), die Kommas enthalten koennten
- Erhoeht die Zuverlässigkeit durch minimale Trefferzahl (3)

**TXT (Fallback-Regel)**
- Trifft zu, wenn KEINE bekannte Binär-Signatur am Anfang gefunden wird
- Prueft auf: ZIP, PDF, OLE, PNG, JPEG, BMP, TIFF, GIF
- Datei muss groesser als 0 Bytes sein
- Diese Regel wird normalerweise zuletzt ausgewertet

**SAM (Lotus AmiPro)**
- Sucht nach den Headern `[ver]`, `[sty]`, `[files]`, `[charset]`, `[revisions]`
- Bedingung: alle fuenf Header muessen in den ersten 512 Bytes vorkommen

**EML (E-Mail)**
- Prueft auf `From:`, `To:`, `Subject:`, `Date:`, `MIME-Version:`
- Alternative 1: `From:` oder `Subject:` oder `Date:` an Position 0
- Alternative 2: mindestens 2 der fuenf Header irgendwo in der Datei

**ZIP_ARCHIVE**
- Prueft auf ZIP-Magic `{50 4B 03 04}` an Position 0
- ODER: `{50 4B 01 02}` (Zentralverzeichnis) und `{50 4B 05 06}` (Ende des Zentralverzeichnisses) beide vorhanden

**MUSICXML vs. XML**
- `rule XML`: Erkennt generisches XML (`<?xml` am Anfang) aber NICHT `<score-partwise>` oder `<score-timewise>`
- `rule MUSICXML`: Erkennt unkomprimiertes MusicXML (`<?xml` am Anfang + Score-Tag)
- `rule MXL`: Erkennt komprimiertes MusicXML (ZIP-Magic + `META-INF/container.xml`)

### Besondere Schreibweisen

| Syntax | Bedeutung |
|--------|-----------|
| `{D0 CF 11 E0 A1 B1 1A E1}` | Hex-Byte-Sequenz (OLE-Header) |
| `"WordDocument"` | Textstring (case-sensitive) |
| `nocase` | Flag fuer case-insensitive Suche |
| `uint16be(0) == 0xFFD8` | 16-Bit Integer im Big-Endian-Format an Position 0 |
| `at 0` | Die Zeichenkette muss an Position 0 beginnen |
| `in (0..512)` | Suchbereich auf die ersten 512 Bytes begrenzt |
| `1 of ($a, $b, $c)` | Mindestens 1 der aufgelisteten Strings muss vorkommen |
| `all of ($a, $b, $c)` | Alle aufgelisteten Strings muessen vorkommen |
| `filesize > 0` | Datei darf nicht leer sein |

### Format-Kategorien (uebersicht)

| Kategorie | Enthaltene Regeln |
|-----------|-------------------|
| Dokumente | DOC, DOCX, RTF, PAGES, SAM, PDF, PDFA |
| E-Mails/Daten | DBX, EML, JSON |
| Praesentationen | PPT, PPTX, ODP, KEY, PRZ, SHW |
| Tabellen | XLS, CSV |
| Audio | MP3, WAV, FLAC |
| Video | MP4, AVI, MKV |
| Bilder | JPEG, PNG, TIFF, GIF, BMP |
| Auszeichnungssprachen | XML, MUSICXML, MXL, HTML, XHTML |
| Text | TXT (Fallback) |
| Archive | ZIP_ARCHIVE |

### Einschraenkungen und bekannte Probleme

- Die CSV-Regel kann bei sehr kleinen Dateien (weniger als 3 Zeilen) fehlschlagen
- Die TXT-Regel ist ein Negativ-Test und kann Dateien faelschlicherweise als Text klassifizieren, wenn sie keine der geprueften Magic Bytes haben (z.B. leere Dateien)
- Die MUSICXML-Regel setzt voraus, dass die XML-Deklaration `<?xml` an Position 0 steht
- Die PRONOM-IDs sind nicht fuer alle Regeln verfuegbar (nur fuer Standard-Formate)
- Die Regel `PS` (PostScript) ist in der Sammlung enthalten, wird aber in der README nicht als Kategorie aufgefuehrt

### Abhaengigkeiten

Die Regeldatei ist unabhaengig von externen Bibliotheken und kann mit jedem YARA-kompatiblen Parser verwendet werden (z.B. `yara-python`, `yara` CLI). Keine zusaetzlichen Python-Pakete erforderlich.

---

## Lizenz & Urheberrecht

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Diese Regelsammlung ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT