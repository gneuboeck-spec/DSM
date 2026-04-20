# Workflow-Launcher (start.bat)

Diese Batch-Datei ist der zentrale Einstiegspunkt für die gesamte digitale Archivierungsumgebung. Sie dient dazu, die notwendigen Projektparameter abzufragen, die Python-Laufzeitumgebung (Virtual Environment) zu initialisieren und das interaktive Hauptmenü zu starten.

Die Datei automatisiert die Konfiguration der Windows-Eingabeaufforderung, sodass keine manuellen Pfadangaben oder Aktivierungsbefehle durch den Benutzer erforderlich sind.

---

## Hauptfunktionen

*   Interaktive Parameterabfrage: Fragt beim Start einmalig die AC-Nummer und die Datenträger-ID ab, die für alle nachfolgenden Skripte als globale Variablen dienen.
*   Automatisierte Umgebungseinrichtung:
    *   Wechselt automatisch in das Arbeitsverzeichnis der Skripte.
    *   Aktiviert die spezifische virtuelle Python-Umgebung (.venv), um sicherzustellen, dass alle Bibliotheken (lxml, requests, bagit etc.) zur Verfügung stehen.
*   Prozess-Isolierung: Öffnet ein neues, sauberes Konsolenfenster für die Arbeitsumgebung, während das ursprüngliche Fenster geschlossen werden kann.
*   Sicherheits-Check: Enthält einen manuellen Kontrollpunkt (Pause), an dem der Benutzer verifizieren kann, dass die virtuelle Umgebung erfolgreich aktiviert wurde, bevor das Menü lädt.
*   Parameter-Übergabe: Reicht die eingegebenen IDs ("%ac_number%" "%disk_id%") sicher an das zentrale Python-Menü (menu.py) weiter.

---

## Technische Voraussetzungen & Konfiguration

Die Batch-Datei enthält hardcodierte Pfade, die auf die spezifische Systemumgebung angepasst sind. Vor der Nutzung auf einem anderen System müssen folgende Zeilen im Editor angepasst werden:

1.  Arbeitsverzeichnis:
    `cd /d "C:\Users\digit\Desktop\Skripte"`
2.  Pfad zur virtuellen Umgebung:
    `C:\Users\digit\.venv\Scripts\activate`

---

## Benutzung

1.  Führen Sie die `start.bat` per Doppelklick aus.
2.  Geben Sie die AC-Nummer des aktuellen Projekts ein (z.B. AC12345678).
3.  Geben Sie die eindeutige Datenträger-ID ein (z.B. ID_001).
4.  Ein neues Fenster öffnet sich. Bestätigen Sie den Kontrollpunkt mit einer beliebigen Taste.
5.  Das Hauptmenü (`menu.py`) erscheint und zeigt die eingegebenen Nummern zur Kontrolle an.

---

## Workflow-Kontext

Die `start.bat` bildet die Brücke zwischen dem Dateisystem und der Programmlogik. Ohne diesen Launcher müssten Benutzer die virtuelle Umgebung manuell aktivieren und Skripte mit komplexen Argumenten über die Konsole aufrufen. Die Datei stellt sicher, dass der Workflow immer mit der korrekten Python-Konfiguration startet.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT