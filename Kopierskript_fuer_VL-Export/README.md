# Kopierskript für VL-Export



Dieses Skript ist ein automatisiertes Werkzeug, das den Prozess der Zusammenstellung der finalen Lieferpakete für den VL-Export (Verbund-Lagerung) standardisiert. Es sammelt gezielt alle relevanten Ergebnisse aus den verschiedenen Phasen des Archivierungsworkflows und kopiert sie in einen dedizierten Export-Ordner.



Das Skript ist als finaler Schritt im lokalen Verarbeitungsprozess konzipiert. Es wird, wie die anderen Skripte im Workflow, über eine `start.bat` mit dynamischen Pfaden gesteuert, um Konsistenz und Nachvollziehbarkeit zu gewährleisten.



## Kernfunktionalität



Das Skript führt eine Reihe von gezielten Kopieroperationen durch, um das finale Lieferpaket zu erstellen. Es sammelt die folgenden Artefakte:



1.  **Abbildungen des physischen Datenträgers**

&nbsp;   *   **Quelle:** Ordner `0_[ID]_picture-carrier`

&nbsp;   *   **Dateien:** Alle `.tif`-Dateien (z.B. Scans oder Fotos des Original-Datenträgers).



2.  **Statistische Berichte:**

&nbsp;   *   **Quelle:** Ordner `2_[ID]_extracted-files`

&nbsp;   *   **Dateien:**

&nbsp;       *   Die `.content`-Datei (XML-Zusammenfassung der Brunnhilde-Analyse).

&nbsp;       *   Die `...Tree.txt`-Datei (Verzeichnisbaum der extrahierten Dateien).



3.  **Detaillierte Metadaten:**

&nbsp;   *   **Quelle:** Ordner `3_[ID]_for-transfer`

&nbsp;   *   **Datei:** Die `.index`-Datei (umfassende Metadaten-XML für jede einzelne Datei).



4.  **Die finalen Dateien:**

&nbsp;   *   **Quelle:** Ordner `3_[ID]_for-transfer/Files`

&nbsp;   *   **Inhalt:** Der gesamte `Files`-Ordner, der die originalen und die konvertierten, archivsicheren Dateien enthält.



Das Skript ist so konzipiert, dass es keine existierenden Dateien oder Ordner im Zielverzeichnis überschreibt, um versehentlichen Datenverlust zu verhindern.



---



## Technische Voraussetzungen



*   **Python:** Version 3.6 oder neuer.

*   **Bibliotheken:** `colorama` für eine farbige Konsolenausgabe.

&nbsp;   

&nbsp;   pip install colorama

&nbsp;   


## Erwartete Ordnerstruktur



Das Skript ist von einer präzisen Ordnerstruktur abhängig, die durch die vorherigen Schritte im Workflow erzeugt wurde. Alle Pfade werden dynamisch basierend auf einer `AC-Nummer` und einer `Datenträger-ID` generiert.


Die erwartete Struktur innerhalb des `Documents\\Datentraeger\_sichern\\\[AC-Nummer]\\\[Datenträger-ID]`-Verzeichnisses ist:




*   **`\[AC-Nummer]`**: Die Haupt-Archivierungsnummer des Projekts.

*   **`\[Datenträger-ID]`\*\*: Die eindeutige ID des zu verarbeitenden Datenträgers.

.

├── 0_[ID]_picture-carrier/         <-- QUELL-ORDNER 1

├── 2_[ID]_extracted-files/         <-- QUELL-ORDNER 2

├── 3_[ID]_for-transfer/            <-- QUELL-ORDNER 3

│   └── Files/                      <-- QUELL-ORDNER 4

│

└── 4_[ID]_VL/                      <-- ZIEL-ORDNER



## Ausführung


Das Skript ist für den Start über eine Wrapper-Datei (z.B. eine `start.bat`) konzipiert, welche die `AC-Nummer` und `Datenträger-ID` als Argumente übergibt.


**Beispielhafter Aufruf in einer `start.bat`:**

@echo off

set AC\_NUMBER=AC\_0001

set DISK\_ID=CD\_01

python vl\_export\_skript.py %AC\_NUMBER% %DISK\_ID%

pause


### Ablauf der Ausführung


1.  **Validierung:** Das Skript prüft die übergebenen Argumente und verifiziert, dass alle benötigten Quell- und Zielverzeichnisse vorhanden sind.

2.  **Iteratives Kopieren:** Das Skript führt die fünf oben beschriebenen Kopiervorgänge nacheinander aus.

3.  **Status-Feedback Für jede Aktion wird eine klare Erfolgs- oder Warnmeldung in der Konsole ausgegeben (z.B. `"Kopiert"`, `"Datei existiert bereits"`, `"Ordner nicht gefunden"`).

4.  **Abschluss:** Nach Abschluss aller Kopiervorgänge fragt das Skript, ob der Zielordner (`4_[ID]_VL`) im Datei-Explorer geöffnet werden soll.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT
