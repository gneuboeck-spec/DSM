# Skript H: VL-Export (Dateien konsolidieren)

Dieses Skript dient der abschließenden Zusammenführung aller relevanten Metadaten-Berichte und Objektaufnahmen in das Verzeichnis der Stufe 4 (VL). Es automatisiert das Kopieren von TIF-Bildern des physischen Datenträgers (aus Stufe 0) sowie der generierten Inhalts-Zusammenfassungen und Verzeichnisstrukturen (aus Stufe 2), um ein vollständiges Paket für die Kuratierung und Archivierung bereitzustellen.

Das Skript ist für den Einsatz innerhalb einer standardisierten Ordnerstruktur konzipiert und nutzt farbliche Rückmeldungen (colorama) zur Statusanzeige.

---

## Hauptfunktionen

*   Automatisierte Konsolidierung: Sammelt dezentrale Dateien aus verschiedenen Vorstufen (0 und 2) und führt sie zentral in Stufe 4 zusammen.
*   Hardware-Dokumentation: Identifiziert und kopiert alle Objektaufnahmen (.tif) des Datenträgers aus Stufe 0.
*   Metadaten-Aggregation: Kopiert die Inhaltszusammenfassung (.content) und den Verzeichnis-Tree (_tree.txt) aus Stufe 2.
*   Sicherheitscheck: Verhindert das versehentliche Überschreiben bereits existierender Dateien im Zielordner.
*   Metadaten-Erhalt: Nutzt shutil.copy2, um die ursprünglichen Zeitstempel der Berichte beim Kopieren beizubehalten.
*   Farbkodierte Konsole: Erfolg (Grün), Warnungen (Gelb) und Fehler (Rot) werden zur besseren Übersicht farblich hervorgehoben.

---

## TREE-Struktur & Dateipfade (Phase 3)

Das Skript fungiert als Sammler für den Stufe-4-Ordner. Es greift auf folgende Pfade zu:

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/
├── 0_[ID]_picture-carrier/
│   └── *.tif                              <-- QUELLE (Hardware-Fotos)
├── 2_[ID]_extracted-files/
│   ├── 2_[ID]_extracted-files.content     <-- QUELLE (Inhaltsbericht)
│   └── 2_[ID]_extracted-files_tree.txt    <-- QUELLE (Ordnerstruktur)
└── 4_[ID]_VL/                             <-- ZIELORDNER (Konsolidierter Export)
    ├── *.tif                              <-- Kopierte Hardware-Fotos
    ├── 2_[ID]_extracted-files.content     <-- Kopierter Inhaltsbericht
    └── 2_[ID]_extracted-files_tree.txt    <-- Kopierter Struktur-Tree
```
---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt das Paket colorama für die farbige Darstellung.
    pip install colorama

---

## Ausführung

Das Skript wird idealerweise über die zentrale start.bat oder das menu.py gestartet, welche die AC-Nummer und Datenträger-ID übergeben.

Beispielhafter Aufruf:
    python Skript_H_VL_Export.py AC_12345 ID_001

### Ablauf der Ausführung

1. Validierung: Das Skript prüft die Existenz der Basisordner und des Zielverzeichnisses (Stufe 4).
2. TIF-Kopiervorgang: Alle Bilddateien aus Stufe 0 werden nach Stufe 4 übertragen.
3. Berichts-Kopiervorgang: Die XML-Zusammenfassung (.content) und die Text-Struktur (_tree.txt) werden aus Stufe 2 übertragen.
4. Dubletten-Check: Falls eine Datei bereits im Zielordner vorhanden ist, wird der Kopiervorgang für diese Datei übersprungen (Warnmeldung).
5. Abschluss: Der Benutzer kann den VL-Zielordner auf Wunsch direkt im Explorer öffnen.

---

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur

```text
~/Documents/data/[AC_number]/[disk_archive_ID]/
├── 0_[disk_archive_ID]_picture-carrier/
│   └── *.tif                                    <-- QUELLE (alle TIF-Dateien)
├── 2_[disk_archive_ID]_extracted-files/
│   ├── 2_[disk_archive_ID]_extracted-files.content  <-- QUELLE
│   └── 2_[disk_archive_ID]_extracted-files_tree.txt <-- QUELLE
└── 4_[disk_archive_ID]_VL/                      <-- ZIEL (muss existieren)
```


### Kopierte Dateien im Detail

| Quelle | Ziel | Bedingung |
|--------|------|------------|
| `0_[ID]_picture-carrier/*.tif` | `4_[ID]_VL/*.tif` | nur wenn Quelldatei existiert und Ziel nicht bereits vorhanden |
| `2_[ID]_extracted-files/2_[ID]_extracted-files.content` | `4_[ID]_VL/2_[ID]_extracted-files.content` | nur wenn Quelldatei existiert und Ziel nicht bereits vorhanden |
| `2_[ID]_extracted-files/2_[ID]_extracted-files_tree.txt` | `4_[ID]_VL/2_[ID]_extracted-files_tree.txt` | nur wenn Quelldatei existiert und Ziel nicht bereits vorhanden |

### Fehlerfälle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| `base_path` (Dokumente/data/[AC]) existiert nicht | rote Meldung + `sys.exit(1)` |
| `main_folder` (Dokumente/data/[AC]/[ID]) existiert nicht | rote Meldung + `sys.exit(1)` |
| `destination_folder` (`4_[ID]_VL`) existiert nicht | rote Meldung + `sys.exit(1)` |
| Quellordner `0_[ID]_picture-carrier` existiert nicht | gelbe Warnung, Kopiervorgang wird übersprungen (kein Abbruch) |
| Quellordner `2_[ID]_extracted-files` existiert nicht | wird nicht separat geprüft; die fehlenden Dateien werden einzeln mit gelber Warnung gemeldet |
| Quelldatei existiert nicht | gelbe Warnung, keine Kopie |
| Zieldatei existiert bereits | gelbe Warnung, Überspringen (kein Überschreiben) |

### Kopiermethode

Das Skript verwendet `shutil.copy2()`, welches die ursprünglichen Metadaten (z. B. Zeitstempel) beibehält.

### TIF-Erkennung

Das Skript sucht mit `source_picture_carrier.glob("*.tif")` nach Dateien mit der Endung `.tif` (Groß-/Kleinschreibung wird nicht explizit behandelt; Windows ist case-insensitiv). Dateien mit Endung `.tiff` werden nicht erkannt.

### Dublettenprüfung

Für jede Datei wird vor dem Kopieren geprüft, ob die Zieldatei bereits existiert (`dest_file.exists()`). Wenn ja, erscheint eine gelbe Warnung und die Datei wird übersprungen.

### Farbkodierung (colorama)

| Farbe | Verwendung |
|-------|------------|
| Grün (`Fore.GREEN`) | Erfolgsmeldungen (Kopie erfolgreich, Pfade vorhanden) |
| Gelb (`Fore.YELLOW`) | Warnungen (Datei existiert bereits, Ordner/Datei nicht gefunden, manuelle Eingabe-Aufforderung) |
| Rot (`Fore.RED`) | Fehler (Pfade existieren nicht, Skriptabbruch) |
| Magenta (`Fore.MAGENTA`) | Kopfzeilen (Trennlinien, Überschriften) |
| Cyan (`Fore.CYAN`) | Abschnittsüberschriften („Pfade definieren“, „Kopiervorgang starten“) |
| Weiß (`Fore.WHITE`) | Pfadausgabe |

### Fallback bei fehlenden Kommandozeilen-Argumenten

Wenn das Skript ohne AC-Nummer und Datenträger-ID gestartet wird, fragt es interaktiv nach den Werten. Die Meldung erscheint in Gelb.

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j`:
- **Windows** → `os.startfile(destination_folder)`
- **macOS** → `subprocess.run(["open", destination_folder])`
- **Linux/andere** → `subprocess.run(["xdg-open", destination_folder])`

### Abhängigkeiten

- **Erforderlich**: `colorama` (muss installiert sein, sonst Abbruch mit Fehlermeldung)
- **Standardbibliothek**: `os`, `sys`, `re`, `shutil`, `subprocess`, `pathlib`

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT