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

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Verzeichnisstruktur

Die start.bat geht von folgender fester Ordnerstruktur auf dem System aus:

C:\Users\digit\Desktop\Skripte\          <-- Hier liegen alle Python-Skripte (inkl. menu.py)
C:\Users\digit\.venv\Scripts\activate    <-- Hier liegt die virtuelle Umgebung

### Ablauf im Detail

1. Parameterabfrage:
   set /p ac_number="AC-Nummer eingeben: "
   set /p disk_id="Datentraeger-ID eingeben: "

2. Start eines neuen CMD-Fensters:
   start "Python Arbeitsumgebung" cmd /k "..."


Der Befehl im neuen Fenster wird in folgender Reihenfolge ausgefuehrt:

Schritt 1: cd /d "C:\Users\digit\Desktop\Skripte"
          Wechselt ins Skript-Verzeichnis (auch auf andere Laufwerke moeglich)

Schritt 2: C:\Users\digit\.venv\Scripts\activate
          Aktiviert die virtuelle Python-Umgebung

Schritt 3: echo. && echo KONTROLLPUNKT: Die VENV ist aktiv.
          Gibt eine Bestaetigung aus

Schritt 4: pause > nul
          Wartet auf einen Tastendruck (Ausgabe wird unterdrueckt)

Schritt 5: python menu.py "%ac_number%" "%disk_id%"
          Startet das Menue mit den eingegebenen Werten

### Besonderheiten der Batch-Syntax

| Element | Bedeutung |
|---------|-----------|
| start | Oeffnet ein neues Fenster, das alte bleibt erhalten |
| cmd /k | Fuehrt den Befehl aus und laesst das Fenster danach offen |
| cd /d | Wechselt Laufwerk und Verzeichnis in einem Schritt |
| && | Fuehrt den naechsten Befehl nur aus, wenn der vorherige erfolgreich war |
| pause > nul | Unterdrueckt die Ausgabe "Druecken Sie eine beliebige Taste . . ." |
| "%ac_number%" "%disk_id%" | Uebergabe der Variablen mit Anfuerungszeichen (schuetzt vor Leerzeichen) |

### Interaktion mit dem Benutzer

1. Erstes Fenster (die aufgerufene start.bat):
   --- Bitte geben Sie die initialen Werte ein ---
   AC-Nummer eingeben: [Benutzereingabe]
   Datentraeger-ID eingeben: [Benutzereingabe]
   Werte wurden gespeichert. Starte die Arbeitsumgebung...

2. Zweites Fenster (das von "start" geoeffnete Fenster):
   KONTROLLPUNKT: Die VENV ist aktiv. Druecken Sie eine Taste, um das Menue zu starten.
   [Benutzer drueckt eine beliebige Taste]
   (dann erscheint das menu.py)

### Fehlerfaelle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| Skript-Verzeichnis existiert nicht | Das neue Fenster zeigt "Das System kann den angegebenen Pfad nicht finden" |
| .venv existiert nicht oder activate fehlt | Der Befehl schlaegt fehl, das Menue wird nicht gestartet |
| menu.py nicht im Skript-Verzeichnis | "python: can't open file" Fehler im neuen Fenster |
| Benutzer gibt keine Werte ein (nur Enter) | Die Variablen bleiben leer, werden aber trotzdem an menu.py uebergeben |

### Wichtige Einschraenkungen

- Die Pfade sind fest codiert und muessen vor der ersten Nutzung angepasst werden
- Das Skript geht davon aus, dass die virtuelle Umgebung bereits existiert und alle Pakete installiert sind
- Der Kontrollpunkt erfordert manuelle Interaktion (Tastendruck) – keine automatische Fortsetzung
- Beide Fenster bleiben geoeffnet – das urspruengliche Fenster kann manuell geschlossen werden
- Die Variablen werden nur mit Anfuerungszeichen geschuetzt, aber nicht auf gueltige Zeichen geprueft

### Anpassung an andere Systeme

Vor der Nutzung auf einem anderen Rechner muessen folgende Zeilen geaendert werden:

Zeile 13 (Pfad zum Skript-Verzeichnis):
   cd /d "C:\Users\ANDERER_BENUTZER\Desktop\Skripte"

Zeile 14 (Pfad zur virtuellen Umgebung):
   C:\Users\ANDERER_BENUTZER\.venv\Scripts\activate

### Abhaengigkeiten

- Windows-Betriebssystem (start, cmd /k, cd /d, set /p sind Windows-spezifisch)
- Python mit installierter virtueller Umgebung (.venv) im angegebenen Pfad
- menu.py und alle anderen Skripte muessen im Skript-Verzeichnis liegen

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT