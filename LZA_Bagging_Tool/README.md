# LZA Bagging Tool

Dieses Python-Skript automatisiert die Zusammenführung von Datenrettungs-Ergebnissen und erstellt daraus einen standardisierten **BagIt-Container** für die Langzeitarchivierung (LZA).

## Funktionen

1. **Konsolidierung:** Sammelt Dateien aus den Arbeitsordnern 0, 1, 2 und 3 im Zielordner 5.
2. **Robustes Verschieben:** Prüft auf Existenz der Quelldateien und bereinigt etwaige Altlasten im Zielverzeichnis.
3. **BagIt-Erstellung:** Wandelt den Zielordner (Ordner 5) in einen BagIt-Container um.
    - Berechnet Checksummen (Standard: **SHA-256**).
    - Fügt Metadaten wie `Contact-Name` und `External-Identifier` hinzu.
4. **Validierung:** Überprüft den neu erstellten Bag sofort auf Integrität.

## Voraussetzungen

Das Skript benötigt das Modul `bagit`. Installation via pip:

    pip install bagit

## Verwendung

Das Skript wird über die Kommandozeile aufgerufen und benötigt die **AC-Nummer** und die **Disk-ID** als Argumente:

    python skriptname.py <AC-Nummer> <Disk-ID>

**Beispiel:**
    python skriptname.py AC15993802 ZPH1705-120_04-12-03-01

## Konfiguration im Skript

- **base_root:** Definiert den Basispfad zu den Daten (Standard: `C:\Users\digit\Documents\data`).
- **metadata:** Hier können die Informationen für die `bag-info.txt` angepasst werden.
- **time.sleep(3):** Eine eingebaute Pause von 3 Sekunden verhindert "Permission Errors" unter Windows, falls Dateizugriffe noch nicht vollständig vom System freigegeben wurden.

## Ordnerstruktur

Das Skript erwartet folgende Struktur:
- `0_..._picture-carrier` (wird komplett verschoben)
- `1_..._image-LZA` (wird komplett verschoben)
- `2_..._extracted-files` (spezifische Berichte werden verschoben)
- `3_..._for-transfer` (Logs werden verschoben)
- `5_..._LZA` (**Zielordner**, muss existieren)

## Fehlerbehebung

- **Permission Error:** Stellen Sie sicher, dass der Zielordner nicht im Windows Explorer geöffnet ist und keine Datei daraus in einem anderen Programm (Editor, Browser etc.) verwendet wird.
- **Fehlender Zielordner:** Das Skript bricht ab, wenn der Ordner `5_..._LZA` nicht bereits existiert.

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT