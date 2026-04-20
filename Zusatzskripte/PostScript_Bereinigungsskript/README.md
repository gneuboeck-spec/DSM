# PostScript-Bereinigungsskript (.ps)

Dieses Skript ist ein einfaches Hilfswerkzeug zur automatisierten Bereinigung von Verzeichnisstrukturen. Es durchsucht ein definiertes Basisverzeichnis rekursiv nach allen Dateien mit der Endung .ps (PostScript) und löscht diese unwiderruflich vom Datenträger.

Es dient dazu, temporäre oder unerwünschte PostScript-Dateien, die beispielsweise bei Konvertierungsprozessen als Zwischenschritte entstanden sind, effizient zu entfernen.

---

## Hauptfunktionen

*   Rekursive Suche: Das Skript durchsucht nicht nur den Hauptordner, sondern auch alle Unterverzeichnisse nach .ps-Dateien.
*   Sichere Löschung: Nutzt die moderne pathlib-Bibliothek zur zuverlässigen Identifizierung und Löschung (unlink) der Dateien.
*   Status-Bericht: Gibt während des Laufs jede gelöschte Datei im Terminal aus und zeigt am Ende eine Zusammenfassung der insgesamt entfernten Dateien an.
*   Fehlerbehandlung: Sollte eine Datei blockiert sein oder fehlen, wird der Fehler abgefangen, protokolliert und das Skript setzt die Bereinigung fort.

---

## Technische Voraussetzungen

*   Python: Version 3.4 oder neuer (da pathlib benötigt wird).
*   Berechtigungen: Das Skript benötigt Schreibrechte im Zielverzeichnis, um Löschvorgänge durchführen zu können.

---

## Konfiguration

Vor der Ausführung muss der Zielpfad im Skript manuell angepasst werden. Suchen Sie die folgende Zeile im oberen Teil der Datei:

    base_path = Path(r"C:\Pfad\zu\Ihrem\Arbeitsordner")

Ersetzen Sie den Pfad in den Anführungszeichen durch das Verzeichnis, das bereinigt werden soll. Das vorangestellte 'r' stellt sicher, dass Windows-Backslashes korrekt interpretiert werden.

---

## Ausführung

Starten Sie das Skript nach der Pfadanpassung über die Konsole oder per Doppelklick:

    python delete_ps_files.py

### Ablauf der Bereinigung

1. Validierung: Das Skript prüft, ob der angegebene Pfad existiert und ein Verzeichnis ist.
2. Indexierung: Alle .ps-Dateien in der Struktur werden erfasst.
3. Löschvorgang: Jede gefundene Datei wird einzeln gelöscht und im Terminal mit einem Papierkorb-Emoji quittiert.
4. Abschluss: Das Skript gibt die Gesamtzahl der gelöschten Elemente aus.

---

## Sicherheitshinweis

⚠️ **Achtung:** Die Löschung erfolgt direkt und dauerhaft. Die Dateien werden nicht in den Papierkorb verschoben. Stellen Sie sicher, dass Sie den korrekten Pfad angegeben haben, bevor Sie das Skript starten.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT