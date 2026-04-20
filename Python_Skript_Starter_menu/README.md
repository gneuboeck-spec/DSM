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

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT