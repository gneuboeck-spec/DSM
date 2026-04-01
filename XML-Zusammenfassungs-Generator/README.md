# XML-Zusammenfassungs-Generator (.content)



Dieses Skript ist ein spezialisiertes Werkzeug zur Automatisierung der Berichterstellung innerhalb eines digitalen Archivierungsworkflows. Es sammelt Informationen aus zwei unterschiedlichen Quellen – einer manuell erstellten XML-Beschreibung des physischen Datenträgers und einem automatisch generierten HTML-Analysebericht von Brunnhilde – und führt sie zu einer einzigen, strukturierten XML-Zusammenfassungsdatei (`.content`) zusammen.



Diese `.content`-Datei dient als zentrale Übersicht über den Inhalt und die technischen Eigenschaften eines archivierten Datenträgers.



## Kernfunktionalität



Das Skript führt die folgenden Aktionen aus:



1\.  \*\*Einlesen der Datenträger-Beschreibung:\*\*

&nbsp;   \*   \*\*Quelle:\*\* Eine XML-Datei (`0\_\[ID]\_carrier-description.xml`), die manuell erstellte, deskriptive Metadaten über den physischen Datenträger enthält (z.B. Typ, Beschriftung, Zustand).

&nbsp;   \*   \*\*Aktion:\*\* Das Skript liest diese Informationen ein, um sie in die finale Zusammenfassung zu integrieren.



2\.  \*\*Einlesen des Analyse-Berichts:\*\*

&nbsp;   \*   \*\*Quelle:\*\* Ein HTML-Bericht (`report.html`), der zuvor vom Analyse-Tool Brunnhilde erstellt wurde.

&nbsp;   \*   \*\*Aktion:\*\* Das Skript parst diesen HTML-Bericht, um quantitative und statistische Daten zu extrahieren, darunter:

&nbsp;       \*   Gesamtzahl und -größe der Dateien.

&nbsp;       \*   Frühestes und spätestes Datum der Dateien.

&nbsp;       \*   Eine detaillierte Aufschlüsselung der gefundenen Dateiformate (inkl. PRONOM-ID, Version und Anzahl).

&nbsp;       \*   Die Anzahl der nicht identifizierten Dateien.



3\.  \*\*Erstellung der XML-Zusammenfassung:\*\*

&nbsp;   \*   \*\*Ziel:\*\* Eine neue XML-Datei mit der Endung `.content`.

&nbsp;   \*   \*\*Aktion:\*\* Das Skript erstellt eine neue XML-Struktur und befüllt sie mit den aggregierten Daten aus beiden Quellen. Das Ergebnis ist eine saubere, gut formatierte und maschinenlesbare Übersicht.



---



## Technische Voraussetzungen



\*   \*\*Python:\*\* Version 3.6 oder neuer.

\*   \*\*Bibliotheken:\*\* `Beautiful Soup 4` muss über `pip` installiert sein. Diese Bibliothek wird zum Parsen des HTML-Berichts benötigt.

&nbsp;   ```bash

&nbsp;   pip install beautifulsoup4

&nbsp;   ```



---



## Erwartete Ordner- und Dateistruktur



Das Skript ist von einer präzisen Ordner- und Dateistruktur abhängig, die durch die vorherigen Schritte im Workflow erzeugt wurde. Alle Pfade werden dynamisch basierend auf einer `AC-Nummer` und einer `Datenträger-ID` generiert.



Die erwartete Struktur innerhalb des `Documents\\Datentraeger\_sichern\\\[AC-Nummer]\\\[Datenträger-ID]`-Verzeichnisses ist:



```.

├── 0\_\[ID]\_picture-carrier/

│   └── 0\_\[ID]\_carrier-description.xml  <-- QUELLE 1 (Manuelle Beschreibung)

│

└── 2\_\[ID]\_extracted-files/

&nbsp;   ├── Brunnhilde\_\[ID]/

&nbsp;   │   └── Files\_collection\_report/

&nbsp;   │       └── report.html             <-- QUELLE 2 (Brunnhilde-Analyse)

&nbsp;   │

&nbsp;   └── (Hier wird die Zieldatei erstellt)

&nbsp;       └── 2\_\[ID]\_extracted-files.content <-- ZIELDATEI (.content XML)



\*   \*\*`\[AC-Nummer]`\*\*: Die Haupt-Archivierungsnummer des Projekts.

\*   \*\*`\[Datenträger-ID]`\*\*: Die eindeutige ID des zu verarbeitenden Datenträgers.



## Ausführung



Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.



\*\*Beispielhafter Aufruf in einer `start.bat`:\*\*```

@echo off

set AC\_NUMBER=AC\_0001

set DISK\_ID=CD\_01

python content\_generator\_skript.py %AC\_NUMBER% %DISK\_ID%

pause



### Ablauf der Ausführung



1\.  \*\*Validierung:\*\* Das Skript prüft die übergebenen Argumente und verifiziert, dass alle benötigten Quellverzeichnisse und -dateien vorhanden sind.

2\.  \*\*XML-Parsing:\*\* Die manuelle Datenträgerbeschreibung wird aus der XML-Datei extrahiert.

3\.  \*\*HTML-Parsing:\*\* Der Brunnhilde-Bericht wird mit `Beautiful Soup` analysiert und alle relevanten Statistiken werden extrahiert.

4\.  \*\*XML-Generierung:\*\* Eine neue XML-Struktur wird im Speicher aufgebaut und mit den gesammelten Daten befüllt.

5\.  \*\*Schreiben der Datei:\*\* Die fertige XML-Struktur wird in die `.content`-Zieldatei geschrieben. Das Skript überschreibt keine bereits existierende Zieldatei.

6\.  \*\*Abschluss:\*\* Das Skript fragt, ob der Zielordner im Datei-Explorer geöffnet werden soll.


## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT
