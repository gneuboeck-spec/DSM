# Zentraler Python-Skript-Starter (menu.py)

Dieses Skript dient als zentrale Steuereinheit und grafisches Konsolen-Menü für den gesamten digitalen Archivierungsworkflow. Es ermöglicht das komfortable Starten aller spezialisierten Python-Skripte, verwaltet die Projekt-IDs (AC-Nummer und Datenträger-ID) und stellt sicher, dass diese korrekt an die Unterprozesse übergeben werden.

Das Skript ist darauf ausgelegt, innerhalb einer virtuellen Umgebung (.venv) ausgeführt zu werden und wird in der Regel über die zentrale `start.bat` initialisiert.

---

## Hauptfunktionen

*   Dynamische Skript-Erkennung: Scannt automatisch das aktuelle Verzeichnis nach allen verfügbaren Python-Skripten und listet diese alphabetisch sortiert auf.
*   Zentrale Variablenverwaltung: Empfängt die AC-Nummer und die Datenträger-ID beim Start und hält diese für alle weiteren Arbeitsschritte bereit.
*   Interaktive Steuerung: Ermöglicht das Starten von Skripten per Nummerneingabe, ohne dass Dateinamen manuell eingegeben werden müssen.
*   Flexible ID-Anpassung: Über die Option "N" können die Projektnummern während der Laufzeit geändert werden, um schnell zwischen verschiedenen Datenträgern zu wechseln.
*   Prozess-Kapselung: Startet jedes Skript als eigenen Subprozess (`subprocess.run`) und übergibt die aktuellen Projektparameter als Kommandozeilenargumente.
*   Fehlertoleranz: Fängt ungültige Eingaben ab und kehrt nach Beendigung eines Skripts immer zum Hauptmenü zurück.

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Umgebung: Das Skript sollte in einem Ordner liegen, der auch die anderen Workflow-Skripte enthält.
*   Vorbereitung: Idealerweise ist eine virtuelle Umgebung (`.venv`) eingerichtet, in der alle Abhängigkeiten der Unter-Skripte (z.B. colorama, lxml, bagit) installiert sind.

---

## Benutzung

Das Menü wird normalerweise automatisch durch die `start.bat` mit den erforderlichen Argumenten aufgerufen.

Beispielhafter Aufruf (manuell):
    python menu.py AC_12345 ID_001

### Menü-Optionen:
*   [1-N]: Gibt die Nummer des gewünschten Skripts ein, um es zu starten.
*   N: Erlaubt die Eingabe einer neuen AC-Nummer und Datenträger-ID.
*   Q: Beendet den Skript-Starter und kehrt zur Konsole/Batch zurück.

---

## Workflow-Integration

Das `menu.py` fungiert als Bindeglied zwischen der Batch-Ebene (Windows-Umgebung) und der Python-Logik. Es stellt sicher, dass der Benutzer nicht mit Pfaden oder komplexen Befehlszeilen interagieren muss. Nach jedem ausgeführten Skript pausiert das Menü, damit Statusmeldungen oder Fehlerberichte in Ruhe gelesen werden können, bevor man zum nächsten Schritt übergeht.

---

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Verzeichnisstruktur

Das Skript sucht im selben Verzeichnis, in dem es sich selbst befindet (Path(__file__).resolve().parent), nach allen .py-Dateien. Es zeigt alle gefundenen Skripte an, ausser sich selbst (Python_Skript_Starter_menu.py bzw. den tatsächlichen Dateinamen).

[beliebiger Ordner]/
├── menu.py (dieses Skript)
├── Skript_A_*.py
├── Skript_B_*.py
├── ...
└── start.bat (optional)

### Menüanzeige

Das Menue wird wie folgt dargestellt:
```Text
===================================================
 PYTHON SKRIPT STARTER (Umgebung: .venv ist aktiv)
===================================================
 Aktuelle AC-Nummer:     [ac_number]
 Aktuelle Datentraeger-ID: [disk_id]
---------------------------------------------------

 Verfuegbare Skripte:

   1 - Skript_A_Beispiel.py
   2 - Skript_B_Beispiel.py
   3 - Skript_C_Beispiel.py

   N - Neue Nummern eingeben
   Q - Beenden

===================================================
```

Bitte Nummer des Skripts eingeben (oder N / Q):

### Übergabe der Argumente an Unterprozesse

Wenn ein Skript ausgewaehlt wird, startet das Menue es mit:

subprocess.run([sys.executable, str(script_to_run), ac_number, disk_id])

- sys.executable stellt sicher, dass die gleiche Python-Umgebung verwendet wird (z.B. die aktive virtuelle Umgebung)
- Die Argumente werden in der Reihenfolge ac_number (z.B. AC_12345) und disk_id (z.B. ID_001) uebergeben
- Das aufgerufene Skript muss diese Argumente mit sys.argv[1] und sys.argv[2] empfangen koennen

### Option N: Neue Nummern eingeben

Bei Eingabe von n (Gross-/Kleinschreibung egal) erscheint:

--- Bitte neue Werte eingeben ---
Neue AC-Nummer (alt: [alte_AC]):
Neue Datentraeger-ID (alt: [alte_ID]):

Der Benutzer kann eingeben:
- Einen neuen Wert (ueberschreibt den alten)
- Nichts (einfach Enter) → der alte Wert bleibt erhalten

Wichtig: Die Eingaben werden mit .strip() bereinigt (fuehrende/folgende Leerzeichen entfernt).

### Option Q: Beenden

Bei Eingabe von q (Gross-/Kleinschreibung egal) wird die while True-Schleife mit break verlassen und das Menue beendet.

### Fehlerbehandlung

| Benutzereingabe | Verhalten |
|----------------|-----------|
| Nummer ausserhalb des gueltigen Bereichs | "Ungueltige Auswahl." → Enter zum Fortfahren |
| Buchstabe (nicht N/n oder Q/q) | "Ungueltige Eingabe. Bitte eine Nummer, 'N' oder 'Q' eingeben." → Enter zum Fortfahren |
| Leere Eingabe | wird als ValueError abgefangen (da int('') fehlschlaegt) |
| Unterprozess schlaegt fehl | Fehlermeldung wird angezeigt, Menue kehrt zurueck |

### Wichtige Einschraenkungen

- Das Skript zeigt alle .py-Dateien im Verzeichnis an, ausser sich selbst – auch solche, die nicht als eigenstaendige Skripte gedacht sind (z.B. Modul-Dateien)
- Die Sortierung erfolgt alphabetisch nach Dateiname (sorted())
- Es gibt keine Validierung, ob die uebergebenen ac_number und disk_id tatsaechlich gueltige Projektordner existieren
- Nach jedem Skript-Durchlauf muss der Benutzer Enter druecken, um zum Menue zurueckzukehren
- Das Menue setzt voraus, dass alle aufgerufenen Skripte mit zwei Kommandozeilen-Argumenten umgehen koennen

### Aufruf aus start.bat (Beispiel)

@echo off
cd /d "C:\Pfad\zum\Skriptverzeichnis"
call .venv\Scripts\activate
python menu.py %AC_NUMBER% %DISK_ID%
pause

### Abhaengigkeiten

Keine externen Python-Pakete erforderlich. Verwendet nur Module der Standardbibliothek:
- os
- subprocess
- sys
- pathlib

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT