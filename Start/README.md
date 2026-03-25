# Python Arbeitsumgebung Launcher (Batch-Script)

Diese Batch-Datei (`.bat`) dient als komfortabler Starter für die LZA-Arbeitsumgebung. Sie automatisiert das Abfragen von Metadaten, das Aktivieren der virtuellen Python-Umgebung (venv) und den Start des Hauptmenüs.

## Inhaltsverzeichnis
1. [Funktionsweise](#funktionsweise)
2. [Voraussetzungen](#voraussetzungen)
3. [Konfiguration](#konfiguration)
4. [Verwendung](#verwendung)
5. [Technische Details](#technische-details)
6. [Lizenz](#lizenz)

## Funktionsweise
Das Skript führt folgende Schritte nacheinander aus:
1. **Eingabe**: Abfrage der `AC-Nummer` und der `Datenträger-ID` direkt in der Konsole.
2. **Umgebungsvorbereitung**: Öffnet ein neues Fenster mit dem Titel "Python Arbeitsumgebung".
3. **Pfadwechsel**: Navigiert automatisch in das Skript-Verzeichnis.
4. **Aktivierung**: Aktiviert die vorkonfigurierte virtuelle Python-Umgebung.
5. **Start**: Startet das Python-Skript `menu.py` und übergibt die zuvor eingegebenen Werte als Parameter.

## Voraussetzungen
Damit der Launcher korrekt funktioniert, müssen folgende Komponenten auf dem System vorhanden sein:
- **Betriebssystem**: Windows.
- **Python**: Installiert und mit einer virtuellen Umgebung (venv) unter dem Pfad `C:\Users\digit\.venv`.
- **Skripte**: Das Skript `menu.py` muss sich im Ordner `C:\Users\digit\Desktop\Skripte` befinden.

## Konfiguration
Im Skript sind aktuell folgende festen Pfade hinterlegt. Sollten sich diese ändern, müssen sie in der `.bat`-Datei angepasst werden:

- **Arbeitsverzeichnis**: `C:\Users\digit\Desktop\Skripte`
- **Venv-Pfad**: `C:\Users\digit\.venv\Scripts\activate`

## Verwendung
1. Führe die Batch-Datei per Doppelklick aus.
2. Gib die geforderte **AC-Nummer** ein und drücke Enter.
3. Gib die **Datenträger-ID** ein und drücke Enter.
4. Ein neues Fenster öffnet sich. Drücke dort eine beliebige Taste (beim Kontrollpunkt), um das Python-Menü endgültig zu laden.

## Technische Details
Der Startbefehl nutzt die Übergabe von Variablen an ein neues CMD-Fenster:
`python menu.py "%ac_number%" "%disk_id%"`
Dies stellt sicher, dass die in der Batch-Datei eingegebenen Werte nahtlos an die Python-Logik weitergereicht werden.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT