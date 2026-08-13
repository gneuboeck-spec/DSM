# Textdokumente-Versionsanalyse & Auszugserkennung

Dieses Skript ist ein automatisiertes Kontroll- und Gruppierungswerkzeug zur Erkennung von Textversionen, Bearbeitungsstufen und Auszügen in großen Dokumentensammlungen. Es vergleicht Texte auf syntaktischer Ebene (Zeichen für Zeichen) und gruppiert ähnliche Dokumente zu logischen Versionengruppen, während es gleichzeitig abgeleitete Kurztexte (Abstracts, Zusammenfassungen) intelligent erkennt und zuordnet.

---

## Hauptfunktionen

* **Multi-Format-Textextraktion:** 
  * Liest nativ über 15 Dateiformate (DOCX, PDF, ODT, XML, RTF, TXT, MD, u.v.m.).
  * Nutzt eine Fallback-Kette für PDFs (`pymupdf` → `pdfplumber` → `PyPDF2`).
* **Dreistufiges Filter-System:** 
  * **Wort-Overlap:** Schneller thematischer Vorfilter (Jaccard-Index).
  * **Längenverhältnis:** Verhindert den Vergleich völlig unterschiedlich langer Texte.
  * **Sequenz-Ähnlichkeit:** Exakter Zeichenvergleich mittels Ratcliff/Obershelp-Algorithmus.
* **Intelligente Auszugserkennung (Excerpt Detection):** 
  * Erkennt stark gekürzte Texte (z. B. Abstracts), die das normale Längenverhältnis nicht erfüllen, aber eine extrem hohe wörtliche Übereinstimmung mit dem Basisdokument aufweisen.
* **Interaktive GUI:** 
  * Grafisches Einstellungsfenster zur dynamischen Anpassung aller Schwellenwerte vor dem Start.
* **Revisionssicheres Protokoll:** 
  * Detaillierte CSV-Ausgabe mit Metriken (Übereinstimmungsprozente, Änderungsrichtung) und einer Diagnose für nicht-gruppierte Dateien.

---

## Technische Voraussetzungen

Zusätzlich zu Python 3.8+ müssen folgende externe Python-Pakete installiert sein:
* `python-docx`
* `pymupdf`
* `pdfplumber`

Folgende externe Tools müssen im System-Pfad oder an den im Skript konfigurierten festen Pfaden verfügbar sein (optional, aber empfohlen für Vollständigkeit):
1. **LibreOffice** (`soffice.exe` oder `libreoffice`): Wird automatisch zur Konvertierung von problematischen Formaten wie `.doc`, `.pages`, `.wpd`, `.sdw` oder `.wps` herangezogen.

---

## Ausführung

Das Skript ist für die einfache Bedienung per Doppelklick konzipiert.

**Ablauf:**
1. Doppelklick auf `textdokumente_vergleichen.py`.
2. Bestätigungs-Dialog mit "Ja" beantworten.
3. Im grafischen Einstellungsfenster die Schwellenwerte anpassen (Felder leer lassen, um die Standardwerte zu übernehmen).
4. Quell-Ordner mit den zu analysierenden Dokumenten auswählen.
5. Ziel-Ordner für die CSV-Ausgabedatei auswählen.
6. Das Skript führt die Analyse durch und hält am Ende an, damit die Diagnose im Terminal gelesen werden kann.

---

## Detaillierte Hinweise zum Skriptverhalten

### Konfigurierbare Parameter und ihre Berechnung

| Parameter | Standard | Inhaltliche Bedeutung | Technische Berechnung |
|-----------|----------|-----------------------|-----------------------|
| `SIMILARITY_THRESHOLD` | `0.40` | Mindestens 40% des Textes müssen exakt (Zeichen für Zeichen) übereinstimmen. | `difflib.SequenceMatcher.ratio()`: `(2 * gemeinsame Zeichen) / (Gesamtzeichen beider Texte)`. |
| `LENGTH_RATIO_THRESHOLD` | `0.35` | Ein Text darf maximal 65% kürzer sein als der andere. | `min(len_1, len_2) / max(len_1, len_2)`. |
| `WORD_OVERLAP_THRESHOLD` | `0.25` | Texte müssen mind. 25% ihres einzigartigen Wortschatzes teilen (thematischer Vorfilter). | Jaccard-Index: `\|Schnittmenge der Wörter\| / \|Vereinigung der Wörter\|`. |
| `MIN_TEXT_LENGTH` | `200` | Texte unter dieser Zeichenzahl werden komplett ignoriert. | Absoluter Filter: `if len(text) < MIN_TEXT_LENGTH: continue`. |
| `EXCERPT_THRESHOLD` | `0.80` | Wenn ein Text viel kürzer ist, wird er nur als "Auszug" gruppiert, wenn 80% exakt übereinstimmen. | Sonderfall-Threshold: Aktiviert, wenn `LENGTH_RATIO_THRESHOLD` unterschritten wird. |
| `BASE_CRITERION` | `'oldest'` | Bestimmt das Referenzdokument für die prozentuale Änderungsberechnung. | Sortiert Gruppe nach Datum (`'oldest'`, `'newest'`) oder Länge (`'longest'`, `'shortest'`) und wählt Index 0. |

### Ablauf der Analyse

1. **Textextraktion:** Für jede Datei wird der reine Text extrahiert. Problematische Formate werden temporär im Ordner `.conversion_cache` als `.txt` gespeichert.
2. **Vorfilterung:** Dateien unter `MIN_TEXT_LENGTH` oder mit versteckten Namen (`.`) werden übersprungen.
3. **Paarweiser Vergleich (Union-Find):** Für jedes Paar (i, j) wird geprüft:
   * Erfüllt es den `WORD_OVERLAP_THRESHOLD`?
   * Erfüllt es den `LENGTH_RATIO_THRESHOLD`?
     * *Ja:* Prüfe auf `SIMILARITY_THRESHOLD`.
     * *Nein:* Prüfe auf `EXCERPT_THRESHOLD` (Auszugslogik).
   * Bei Erfolg: `union(i, j)` (Dokumente werden derselben Gruppe zugeordnet).
4. **Metriken-Berechnung:** Für jedes Dokument in einer Gruppe werden die übereinstimmenden Zeichen/Wörter und die prozentuale Änderung gegenüber dem `BASE_CRITERION`-Dokument berechnet.
5. **CSV-Export:** Sortierte Ausgabe mit Diagnose für nicht-gruppierte Dateien.

### Unterstützte Dateiformate

* **Direkt lesbar:** `.txt`, `.md`, `.csv`, `.log`, `.tex`, `.rst`, `.docx`, `.pdf`, `.xml`, `.odt`, `.odf`, `.ods`, `.rtf`
* **Über LibreOffice konvertiert:** `.doc`, `.pages`, `.wpd`, `.sdw`, `.wps`

### Ausgabeformat (CSV-Spalten)

| Spalte | Beschreibung |
|--------|--------------|
| `Relativer_Pfad` | Pfad relativ zum gewählten Quell-Ordner. |
| `Dateiname` | Nur der Name der Datei. |
| `Dateityp` | Dateiendung (z. B. `.docx`). |
| `Versions_Gruppe` | Gruppen-ID (z. B. `GRUPPE_001`) oder leer (nicht gruppiert). |
| `Basisdokument` | Referenzdokument der Gruppe oder `(Basis)`. |
| `Übereinstimmung_Zeichen` | Absolute Anzahl übereinstimmender Zeichen. |
| `Übereinstimmung_Wörter` | Absolute Anzahl übereinstimmender Wörter. |
| `Änderung_Zeichen_%` | Prozentuale Änderung der Zeichenlänge gegenüber der Basis. |
| `Änderung_Wörter_%` | Prozentuale Änderung der Wortanzahl gegenüber der Basis. |
| `Letzte_Aenderung` | Zeitstempel der letzten Dateiänderung (mtime). |
| `Dateigroesse_Bytes` | Dateigröße in Bytes. |

---

## Bekannte Grenzen

1. **Semantische Ähnlichkeit:** Das Skript erkennt nur exakte Textübereinstimmungen. Zwei Texte mit gleicher Bedeutung, aber komplett unterschiedlichen Worten, werden nicht gruppiert. (Für semantische Analyse siehe `ki_semantische_analyse.py`).
2. **Sehr kurze Texte:** Texte unter `MIN_TEXT_LENGTH` (Standard: 200 Zeichen) werden ignoriert.
3. **Gescannte PDFs:** PDFs ohne Textebene (nur Bilder) können nicht gelesen werden, da keine OCR-Engine integriert ist.
4. **Performance:** Bei sehr großen Sammlungen (>1000 Dokumente) kann die Analyse mehrere Minuten dauern (quadratische Komplexität O(n²) beim paarweisen Vergleich).
5. **Verschlüsselte Dateien:** Passwortgeschützte DOCX/PDF-Dateien können nicht gelesen werden.

---

## Verwandte Skripte im Ökosystem

* **`ki_semantische_analyse.py`:** KI-basierte semantische Analyse für Abstracts und Zusammenfassungen (nutzt `sentence-transformers` und erweitert die CSV um eine Spalte `Dokumententyp: Kurztext`).
* **`visualisierung.py`:** Grafische Darstellung der Analyse-Ergebnisse mittels `matplotlib` (Gesamtübersicht und Detailansicht pro Gruppe).

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT