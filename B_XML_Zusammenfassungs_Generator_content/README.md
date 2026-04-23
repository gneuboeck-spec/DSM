# XML-Zusammenfassungs-Generator (.content)

Dieses Skript ist ein spezialisiertes Werkzeug zur Automatisierung der Berichterstellung innerhalb eines digitalen Archivierungsworkflows. Es sammelt Informationen aus zwei unterschiedlichen Quellen – einer manuell erstellten XML-Beschreibung des physischen Datenträgers und einem automatisch generierten HTML-Analysebericht von Brunnhilde – und führt sie zu einer einzigen, strukturierten XML-Zusammenfassungsdatei (.content) zusammen.

Diese .content-Datei dient als zentrale Übersicht über den Inhalt und die technischen Eigenschaften eines archivierten Datenträgers.

---

## Hauptfunktionen

1. Einlesen der Datenträger-Beschreibung:
   * Quelle: Eine XML-Datei (0_[ID]_carrier-description.xml), die manuell erstellte Metadaten über den physischen Datenträger enthält (Typ, Beschriftung, Zustand).
   * Aktion: Das Skript integriert diese deskriptiven Daten in die finale Zusammenfassung.

2. Einlesen des Analyse-Berichts:
   * Quelle: Ein HTML-Bericht (report.html), der zuvor vom Analyse-Tool Brunnhilde erstellt wurde.
   * Aktion: Das Skript parst diesen Bericht mit BeautifulSoup 4, um statistische Daten zu extrahieren (Dateianzahl, Gesamtgröße, Zeitspanne, Dateiformate nach PRONOM).

3. Erstellung der XML-Zusammenfassung:
   * Ziel: Eine neue XML-Datei mit der Endung .content.
   * Aktion: Erstellt eine saubere, maschinenlesbare Übersicht im Zielverzeichnis.

---

## TREE-Struktur & Dateipfade

Das Skript verknüpft Daten aus Stufe 0 und Stufe 2, um den Inhaltsbericht zu generieren:

Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/
│   └── 0_[ID]_carrier-description.xml          <-- QUELLE 1 (Manuelle Beschreibung)
└── 2_[ID]_extracted-files/
    ├── 2_[ID]_extracted-files_brunnhilde/
    │   └── files_collection_report/
    │       └── report.html                     <-- QUELLE 2 (Brunnhilde-Analyse)
    └── 2_[ID]_extracted-files.content          <-- ZIEL (Zusammenfassungsbericht)

---

## Technische Voraussetzungen

* Python: Version 3.10 oder neuer empfohlen.
* Bibliotheken: Beautiful Soup 4 muss installiert sein:
    pip install beautifulsoup4

---

## Ausführung

Das Skript wird idealerweise über eine start.bat gestartet, welche die AC-Nummer und Datenträger-ID übergibt.

Beispielhafter Aufruf in einer start.bat:
    @echo off
    set AC_NUMBER=AC_0001
    set DISK_ID=CD_01
    python content_generator.py %AC_NUMBER% %DISK_ID%
    pause

### Ablauf der Ausführung

1. Validierung: Das Skript prüft die Argumente und verifiziert die Existenz der Quellpfade.
2. XML-Parsing: Die manuelle Datenträgerbeschreibung wird eingelesen.
3. HTML-Parsing: Der Brunnhilde-Bericht wird nach Statistiken und Formaten durchsucht.
4. XML-Generierung: Die aggregierten Daten werden in die .content-Struktur geschrieben.
5. Abschluss: Das Skript bietet an, den Zielordner im Explorer zu öffnen.

---

## Lizenz

Copyright (c) 2025 Florian Lüftner <florian.lueftner@posteo.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
SPDX-FileCopyrightText: 2025 Florian Lüftner
SPDX-License-Identifier: MIT