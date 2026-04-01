# XML-Zusammenfassungs-Generator (.content)

Dieses Skript ist ein spezialisiertes Werkzeug zur Automatisierung der Berichterstellung innerhalb eines digitalen Archivierungsworkflows. Es sammelt Informationen aus zwei unterschiedlichen Quellen – einer manuell erstellten XML-Beschreibung des physischen Datenträgers und einem automatisch generierten HTML-Analysebericht von Brunnhilde – und führt sie zu einer einzigen, strukturierten XML-Zusammenfassungsdatei (`.content`) zusammen.

Diese `.content`-Datei dient als zentrale Übersicht über den Inhalt und die technischen Eigenschaften eines archivierten Datenträgers.

---

## Kernfunktionalität

Das Skript führt die folgenden Aktionen aus:

1.  **Einlesen der Datenträger-Beschreibung:**
    *   **Quelle:** Eine XML-Datei (`0_[ID]_carrier-description.xml`), die manuell erstellte, deskriptive Metadaten über den physischen Datenträger enthält (z. B. Typ, Beschriftung, Zustand).
    *   **Aktion:** Das Skript liest diese Informationen ein, um sie in die finale Zusammenfassung zu integrieren.

2.  **Einlesen des Analyse-Berichts:**
    *   **Quelle:** Ein HTML-Bericht (`report.html`), der zuvor vom Analyse-Tool Brunnhilde erstellt wurde.
    *   **Aktion:** Das Skript parst diesen HTML-Bericht mit `Beautiful Soup 4`, um quantitative und statistische Daten zu extrahieren:
        *   Gesamtzahl und -größe der Dateien.
        *   Frühestes und spätestes Datum der Dateien.
        *   Detaillierte Aufschlüsselung der gefundenen Dateiformate (inkl. PRONOM-ID, Version und Anzahl).
        *   Anzahl der nicht identifizierten Dateien.

3.  **Erstellung der XML-Zusammenfassung:**
    *   **Ziel:** Eine neue XML-Datei mit der Endung `.content`.
    *   **Aktion:** Das Skript erstellt eine neue XML-Struktur und befüllt sie mit den aggregierten Daten aus beiden Quellen. Das Ergebnis ist eine saubere, gut formatierte und maschinenlesbare Übersicht.

---

## Technische Voraussetzungen

*   **Python:** Version 3.6 oder neuer.
*   **Bibliotheken:** `Beautiful Soup 4` muss installiert sein, um den HTML-Bericht zu parsen.
    ```bash
    pip install beautifulsoup4
    ```

---

## Erwartete Ordner- und Dateistruktur

Das Skript ist von einer präzisen Ordnerstruktur abhängig. Alle Pfade werden dynamisch basierend auf einer `AC-Nummer` und einer `Datenträger-ID` generiert.

Die erwartete Struktur innerhalb des Verzeichnisses `Documents/Datentraeger_sichern/[AC-Nummer]/[Datenträger-ID]/` ist:

```text
.
├── 0_[ID]_picture-carrier/
│   └── 0_[ID]_carrier-description.xml          <-- QUELLE 1 (Manuelle Beschreibung)
│
└── 2_[ID]_extracted-files/
    ├── Brunnhilde_[ID]/
    │   └── Files_collection_report/
    │       └── report.html                     <-- QUELLE 2 (Brunnhilde-Analyse)
    │
    └── 2_[ID]_extracted-files.content          <-- ZIELDATEI (Wird hier erstellt)
```

*   **`[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.
*   **`[Datenträger-ID]`**: Die eindeutige ID des zu verarbeitenden Datenträgers.

---

## Ausführung

Das Skript wird idealerweise über eine Wrapper-Datei (z. B. eine `start.bat`) gestartet, welche die Argumente übergibt.

**Beispielhafter Aufruf in einer `start.bat`:**

```batch
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=CD_01
python content_generator_skript.py %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Ausführung

1.  **Validierung:** Das Skript prüft die Argumente und verifiziert die Existenz der Quell- und Zielpfade.
2.  **XML-Parsing:** Die manuelle Datenträgerbeschreibung wird eingelesen.
3.  **HTML-Parsing:** Der Brunnhilde-Bericht wird analysiert und die Statistiken werden extrahiert.
4.  **XML-Generierung:** Eine neue XML-Struktur wird im Speicher aufgebaut.
5.  **Schreiben der Datei:** Die fertige Struktur wird in die `.content`-Datei geschrieben. Eine bereits existierende Zieldatei wird dabei nicht ohne Weiteres überschrieben (Sicherheitscheck).
6.  **Abschluss:** Das Skript bietet an, den Zielordner im Explorer zu öffnen.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT