# XML-Zusammenfassungs-Generator (.content)

Dieses Skript ist ein spezialisiertes Werkzeug zur Automatisierung der Berichterstellung innerhalb eines digitalen Archivierungsworkflows. Es sammelt Informationen aus zwei unterschiedlichen Quellen – einer manuell erstellten XML-Beschreibung des physischen Datenträgers und einem automatisch generierten HTML-Analysebericht von Brunnhilde – und führt sie zu einer einzigen, strukturierten XML-Zusammenfassungsdatei (.content) zusammen.

Diese .content-Datei dient als zentrale Übersicht über den Inhalt und die technischen Eigenschaften eines archivierten Datenträgers.

---

## Hauptfunktionen

1. **Einlesen der Datenträger-Beschreibung:**
   * Quelle: Eine XML-Datei (0_[ID]_carrier-description.xml), die manuell erstellte Metadaten über den physischen Datenträger enthält (Typ, Beschriftung, Zustand).
   * Aktion: Das Skript integriert diese deskriptiven Daten in die finale Zusammenfassung.

2. **Einlesen des Analyse-Berichts:**
   * Quelle: Ein HTML-Bericht (report.html), der zuvor vom Analyse-Tool Brunnhilde erstellt wurde.
   * Aktion: Das Skript parst diesen Bericht mit BeautifulSoup 4, um statistische Daten zu extrahieren (Dateianzahl, Gesamtgröße, Zeitspanne, Dateiformate nach PRONOM).

3. **Erstellung der XML-Zusammenfassung:**
   * Ziel: Eine neue XML-Datei mit der Endung .content im Stufe-2-Verzeichnis.
   * Aktion: Erstellt eine saubere, maschinenlesbare Übersicht. Ein Überschreiben existierender Dateien wird vom Skript verhindert.

---

## TREE-Struktur & Dateipfade

Das Skript verknüpft Daten aus verschiedenen Verarbeitungsstufen. Die Existenz des Transfer-Ordners (Stufe 3) wird ebenfalls validiert:

[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/
│   └── 0_[ID]_carrier-description.xml          <-- QUELLE 1 (Manuelle Beschreibung)
├── 2_[ID]_extracted-files/
│   ├── 2_[ID]_extracted-files_brunnhilde/
│   │   └── files_collection_report/
│   │       └── report.html                     <-- QUELLE 2 (Brunnhilde-Analyse)
│   └── 2_[ID]_extracted-files.content          <-- ZIEL (Zusammenfassungsbericht)
└── 3_[ID]_for-transfer/                        <-- VALIDIERUNG (Muss existieren)

---

## Technische Voraussetzungen

* Python: Version 3.10 oder neuer empfohlen.
* Bibliotheken: Beautiful Soup 4 muss installiert sein:
    pip install beautifulsoup4

---

## Ausführung

Das Skript kann flexibel gestartet werden:

1. **Automatisiert (via Kommandozeile):** Übergabe der AC-Nummer und Datenträger-ID als Argumente (z.B. durch eine start.bat oder das Hauptmenü).
2. **Manuell:** Falls keine Argumente übergeben werden, fragt das Skript die benötigten Daten interaktiv ab.

Beispielhafter Aufruf:
    python content_generator.py AC_12345 ID_001

### Ablauf der Ausführung

1. **Validierung:** Prüfung der Argumente sowie Verifizierung aller Quellpfade und des Transfer-Ordners.
2. **XML-Parsing:** Einlesen der physischen Carrier-Metadaten.
3. **HTML-Parsing:** Extraktion der statistischen Daten und Format-Listen aus dem Brunnhilde-Bericht.
4. **XML-Generierung:** Erstellung der .content-Datei mit strukturierter Einrückung.
5. **Abschluss:** Optionale Abfrage, ob der Zielordner im Explorer geöffnet werden soll.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT