# Python LZA-Menü (Zentraler Skript-Starter)

Dieses Python-Skript (`menu.py`) dient als zentrale Steuerzentrale für eine Sammlung von Langzeitarchivierungs-Skripten (LZA). Es ermöglicht das einfache Auswählen und Ausführen von Skripten, ohne Metadaten wie AC-Nummern oder Datenträger-IDs bei jedem Start manuell neu eingeben zu müssen.

## Inhaltsverzeichnis
1. [Funktionsweise](#funktionsweise)
2. [Features](#features)
3. [Voraussetzungen](#voraussetzungen)
4. [Menü-Optionen](#menü-optionen)
5. [Technische Details](#technische-details)
6. [Lizenz](#lizenz)

## Funktionsweise
Das Menü fungiert als "Wrapper". Es nimmt initiale Werte (AC-Nummer und Datenträger-ID) entgegen und reicht diese automatisch an jedes Unter-Skript weiter, das über das Menü gestartet wird. Es scannt dabei dynamisch den Ordner nach verfügbaren `.py`-Dateien.

## Features
- **Dynamische Skript-Erkennung**: Erkennt automatisch alle Python-Dateien im selben Verzeichnis (außer sich selbst).
- **Parameter-Passing**: Übergibt die aktuelle AC-Nummer und Datenträger-ID als Kommandozeilenargumente an die Zielskripte.
- **Kontext-Wechsel**: Ermöglicht das Ändern der AC-Nummer/ID direkt im laufenden Betrieb, ohne das Programm neu zu starten.
- **Benutzerfreundlich**: Übersichtlicher Header und einfache Navigation über Nummern oder Buchstaben.

## Voraussetzungen
- **Python 3.x**
- Die Zielskripte im selben Ordner sollten darauf ausgelegt sein, Argumente via `sys.argv` zu empfangen (z. B. der "LZA Derivation Image Creator").
- Empfohlen: Start über die zugehörige `start.bat`, um die virtuelle Umgebung (`.venv`) und die initialen Werte automatisch zu laden.

## Menü-Optionen
- **[Nummer]**: Startet das entsprechende Skript aus der Liste.
- **N**: Erlaubt die Eingabe einer neuen AC-Nummer und Datenträger-ID für die aktuelle Sitzung.
- **Q**: Beendet das Programm und schließt das Fenster.

## Technische Details

### Parameterübergabe
Wenn ein Skript (z. B. `image_creator.py`) ausgewählt wird, führt das Menü intern folgenden Befehl aus:
`python image_creator.py [AC-Nummer] [Datenträger-ID]`

### Skript-Filterung
Das Menü schließt sich selbst (`menu.py`) automatisch aus der Liste der startbaren Skripte aus, um Endlosschleifen zu verhindern.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT