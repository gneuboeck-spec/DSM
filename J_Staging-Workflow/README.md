# Skript J: Staging-Workflow & LZA-Strukturierung

Dieses Skript ist der strategische "Organisator" des Workflows. Es dient der finalen Konsolidierung aller dezentralen Arbeitsergebnisse vor der Archivierung. Es führt die Daten aus den Stufen 0 bis 3 zusammen, vervollständigt die Dokumentation in der VL-Stufe (Stufe 4) und bereitet die LZA-Stufe (Stufe 5) für die abschließende Indexierung und PREMIS-Erstellung vor.

Das Skript automatisiert den Umzug und die standardkonforme Umbenennung von Dateien, um eine saubere Archivstruktur zu gewährleisten und die ursprünglichen Arbeitsordner leerzuräumen.

---

## Hauptfunktionen

*   **Vervollständigung der VL-Stufe (Stage 4):**
    *   Kopiert Hardware-Fotos (.tif) aus Stufe 0 in den VL-Ordner.
    *   Kopiert Inhaltsberichte (.content und _tree.txt) aus Stufe 2 in den VL-Ordner.
*   **Restrukturierung der LZA-Stufe (Stage 5):**
    *   **Zentralisierung der Protokolle:** Sammelt alle Log-Dateien aus den Stufen 0, 1, 2 und 3 und verschiebt sie gesammelt in den Ordner 5_[ID]_LZA/logfiles.
    *   **Integration der Nutzdaten:** Verschiebt den "files"-Ordner aus Stufe 3 in die Archivstufe und benennt ihn zur eindeutigen Identifikation in 3_files um.
    *   **Image-Migration:** Verschiebt forensische Disk-Images aus Stufe 1 direkt in die Wurzel der LZA-Stufe.
    *   **Bereinigung der Arbeitsstufen:** Nach dem erfolgreichen Verschieben (Move-Logik) sind die ursprünglichen Ordner 0, 1, 2 und 3 leergeräumt.
*   **Sicherheitslogik:** Beinhaltet eine interaktive Abfrage vor dem Start und nutzt eine "Safe-Move"-Funktion, die bestehende Zielordner bei Bedarf überschreibt, um einen sauberen Stand zu garantieren.

---

## TREE-Struktur & Datenfluss (Phase 4)

Das Skript transformiert die dezentralen Arbeitsordner in die finale Archivstruktur von Stufe 5:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/

├── 4_[ID]_VL/                                     <-- [SCHRITT 1: KOPIEREN]
│   ├── *.tif (Hardware-Fotos)                     <-- Kopie aus Stufe 0
│   ├── 2_[ID]_extracted-files.content             <-- Kopie aus Stufe 2
│   └── 2_[ID]_extracted-files_tree.txt            <-- Kopie aus Stufe 2
│
└── 5_[ID]_LZA/                                    <-- [SCHRITT 2: ZIELSTRUKTUR]
    ├── 01_[ID].img (oder .001 / .bin)             <-- Umzug aus Stufe 1
    ├── 3_files/                                   <-- Umzug & Umbenennung aus Stufe 3/files
    └── logfiles/                                  <-- Zentraler Dokumentations-Pool
        ├── *.tif (Originalfotos der Hardware)     <-- Umzug aus Stufe 0
        ├── 0_[ID]_carrier-description.xml         <-- Umzug aus Stufe 0
        ├── 1_[ID]_image-log.csv                   <-- Umzug aus Stufe 1
        ├── 01_[ID]_image-log.txt                  <-- Umzug aus Stufe 1
        ├── 2_[ID]_extracted-files.content         <-- Umzug aus Stufe 2
        ├── 2_[ID]_extracted-files_tree.txt        <-- Umzug aus Stufe 2
        ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- Umzug aus Stufe 2
        ├── 2_[ID]_extracted-files_brunnhilde/     <-- Umzug aus Stufe 2
        ├── 3_[ID]_for-transfer_all-conversions.log <-- Umzug aus Stufe 3
        └── 3_[ID]_for-transfer_repair-file-extension.log <-- Umzug aus Stufe 3
```
(Die Ordner 0, 1, 2 und 3 sind nach diesem Schritt leer.)

---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt colorama für die Statusanzeige.
    pip install colorama

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf:
    python Skript_J_Staging.py AC_0001 ID_001

### Ablauf der Ausführung

1.  **Sicherheitsabfrage:** Der Benutzer muss das Staging explizit bestätigen.
2.  **VL-Export (Schritt 1):** Fotos und Inhaltsberichte werden nach Stufe 4 kopiert. Dies stellt sicher, dass das aktive Repository (VL) alle Dokumente für die Verzeichnung enthält, bevor die Quellordner geleert werden.
3.  **LZA-Staging (Schritt 2):** 
    *   Alle Log-Dateien aus 0, 1, 2 und 3 werden im zentralen Ordner `5/logfiles` zusammengeführt.
    *   Forensische Images werden nach 5 migriert.
    *   Die Nutzdaten (der `files`-Ordner) werden als `3_files` in die Archivstufe verschoben.
4.  **Abschluss:** Die Arbeitsordner 0-3 sind nach dem Durchlauf leer, und Stufe 5 enthält die komplette, archivfähige Struktur für den Master-Index (Skript K).

---

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur vor Ausführung

```text
~/Documents/data/[AC_number]/[disk_archive_ID]/
├── 0_[disk_archive_ID]_picture-carrier/
│   ├── *.tif                                    <-- Hardware-Fotos
│   ├── 0_[ID]_carrier-description.xml           <-- Trägerbeschreibung
│   └── logfiles/ (falls vorhanden)              <-- wird migriert
├── 1_[disk_archive_ID]_image-LZA/
│   ├── *.img / *.001 / *.bin / *.dd             <-- Disk-Images
│   ├── *.log / *.csv                            <-- Imaging-Logs
│   └── logfiles/ (falls vorhanden)              <-- wird migriert
├── 2_[disk_archive_ID]_extracted-files/
│   ├── 2_[ID]_extracted-files.content
│   ├── 2_[ID]_extracted-files_tree.txt
│   ├── 2_[ID]_extracted-files_brunnhilde-summary.json
│   ├── 2_[ID]_extracted-files_brunnhilde/       <-- Ordner (wird komplett migriert)
│   └── logfiles/ (falls vorhanden)              <-- wird migriert
├── 3_[disk_archive_ID]_for-transfer/
│   ├── files/                                   <-- Nutzdaten (wird zu 3_files)
│   ├── *.log                                    <-- Konvertierungs-Logs
│   ├── *.index                                  <-- Technischer Index
│   └── logfiles/ (falls vorhanden)              <-- wird migriert
├── 4_[disk_archive_ID]_VL/                      <-- Ziel für Kopien
└── 5_[disk_archive_ID]_LZA/                     <-- Ziel für Migration
```

### `safe_move_item()` Funktion

| Parameter | Beschreibung |
|-----------|--------------|
| `src` | Quell-Path-Objekt |
| `dest_dir` | Ziel-Verzeichnis (Path) |
| `rename_to` | optionaler neuer Name (wenn `None`, bleibt Originalname) |

**Verhalten:**
1. Prüft ob Quelle existiert
2. Erstellt Zielverzeichnis falls nötig (`mkdir(parents=True)`)
3. Wenn Ziel bereits existiert:
   - Bei Ordner: `shutil.rmtree(target)`
   - Bei Datei: `os.remove(target)`
4. Führt `shutil.move(src, target)` aus

### Migrationsdetails im Einzelnen

| Schritt | Aktion | Details |
|---------|--------|---------|
| 2A | Konsolidierung vorhandener `logfiles`-Unterordner | Durchsucht Stufen 0,1,2,3 nach Unterordnern `logfiles`, verschiebt deren gesamten Inhalt nach `5/logfiles`, löscht leeren Unterordner |
| 2B | Bilder aus Stufe 0 | Alle Dateien (nicht nur `.tif`) aus `0_.../` werden nach `5/logfiles/` verschoben |
| 2C | Nutzdaten | `3/files` (sofern vorhanden) wird nach `5/3_files` verschoben und umbenannt |
| 2D | Image-LZA (Stufe 1) | **Kompletter Inhalt** von `1_.../` wird nach `5/` verschoben (nicht nur Images) |
| 2E | Berichte aus Stufe 2 | Bestimmte Dateien/Ordner werden nach `5/logfiles/` verschoben (siehe Tabelle oben) |
| 2F | Verbliebene Dateien aus Stufe 3 | Alle `.log` und `.index` Dateien werden nach `5/logfiles/` verschoben |

### Sicherheitsabfrage

Vor der Ausführung erscheint:

[!] HINWEIS: Dieses Skript strukturiert Stufe 5 für den Master-Index.
 Staging jetzt starten? (j/n):

Nur bei Eingabe `j` wird fortgefahren.

### Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| Zielverzeichnis existiert nicht bei Kopie | `mkdir(parents=True)` wird ausgeführt |
| Ziel existiert bereits bei Move | Wird gelöscht (Datei `os.remove`, Ordner `shutil.rmtree`) |
| Fehler beim Verschieben | Fehlermeldung mit `Fore.RED`, Funktion gibt `False` zurück, Skript läuft weiter |
| `src_files_dir` (Stufe 3/files) nicht gefunden | Schritt 2C wird übersprungen (kein Fehler, nur Warnung) |

### Zustand nach Skriptende

| Stufe | Zustand |
|-------|---------|
| `0_[ID]_picture-carrier` | leer (alle Dateien nach `5/logfiles` verschoben) |
| `1_[ID]_image-LZA` | leer (alle Dateien nach `5/` verschoben) |
| `2_[ID]_extracted-files` | ggf. noch nicht migrierte Restdateien (nur spezifische Dateien wurden verschoben) |
| `3_[ID]_for-transfer` | leer (nach Migration von `files` und `.log`/`.index`) |
| `4_[ID]_VL` | angereichert mit Kopien |
| `5_[ID]_LZA` | vollständige Archivstruktur |

### Farbkodierung (colorama)

| Farbe | Verwendung |
|-------|------------|
| Grün (`Fore.GREEN`) | Erfolgsmeldungen (Move/Kopie erfolgreich) |
| Rot (`Fore.RED`) | Fehlermeldungen |
| Gelb (`Fore.YELLOW`) | Hinweise, Sicherheitsabfrage |
| Cyan (`Fore.CYAN`) | Abschnittsüberschriften (SCHRITT 1, SCHRITT 2) |
| Magenta (`Fore.MAGENTA`) | Kopfzeilen (Trennlinien, Titel) |
| Weiß (`Fore.WHITE`) | normaler Text |

### Abhängigkeiten

**Erforderlich:** `colorama` (muss installiert sein, sonst Fallback mit Dummy-Klassen)

**Standardbibliothek:** `os`, `sys`, `shutil`, `time`, `datetime`, `pathlib`

### Wichtige Einschränkungen

- Die `safe_move_item`-Funktion löscht **ohne Rückfrage** bestehende Ziele (Überschreiben)
- Der technische Index (`3_...for-transfer.index`) wird von Skript J **nicht** kopiert, sondern nur geprüft
- Schritt 2D verschiebt **alle** Dateien aus Stufe 1, nicht nur Images
- `logfiles`-Unterordner in den Stufen 0-3 werden nach Migration ihrer Inhalte gelöscht (`rmdir()` nur wenn leer)

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT