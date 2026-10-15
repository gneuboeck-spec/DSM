# H - VL-Export (Konsolidierung)

Dieses Skript dient der abschließenden Zusammenführung aller relevanten Metadaten-Berichte und Objektaufnahmen in das Verzeichnis der Stufe 4 (VL). Es automatisiert das Kopieren von TIF-Bildern des physischen Datenträgers (aus Stufe 0) sowie der generierten Inhalts-Zusammenfassungen und Verzeichnisstrukturen (aus Stufe 2 und Stufe 3), um ein vollständiges Paket für die Kuratierung und Archivierung bereitzustellen.

Das Skript ist für den Einsatz innerhalb einer standardisierten Ordnerstruktur konzipiert und nutzt farbliche Rückmeldungen (`colorama`) zur Statusanzeige.

## Struktur

    H_VL_Export/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- H_VL_Export.py                 <-- Ausführbare Python-Datei

## Hauptfunktionen

* **Automatisierte Konsolidierung:** Sammelt dezentrale Dateien aus verschiedenen Vorstufen (0, 2 und 3) und führt sie zentral in Stufe 4 zusammen.
* **Hardware-Dokumentation:** Identifiziert und kopiert alle Objektaufnahmen (`.tif`) des Datenträgers aus Stufe 0.
* **Metadaten-Aggregation:** Kopiert die Inhaltszusammenfassung (`.content`), den Verzeichnis-Tree aus Stufe 2 (`_tree.txt`) sowie den Verzeichnis-Tree aus Stufe 3 (`_for-transfer_tree.txt`).
* **Sicherheitscheck:** Verhindert das versehentliche Überschreiben bereits existierender Dateien im Zielordner.
* **Metadaten-Erhalt:** Nutzt `shutil.copy2`, um die ursprünglichen Zeitstempel der Berichte beim Kopieren beizubehalten.
* **Farbkodierte Konsole:** Erfolg (Grün), Warnungen (Gelb) und Fehler (Rot) werden zur besseren Übersicht farblich hervorgehoben.

## TREE-Struktur & Dateipfade (Phase 3)

Das Skript fungiert als Sammler für den Stufe-4-Ordner. Der Projektpfad wird vom Menü übergeben (`sys.argv[3]` oder Umgebungsvariable `DATA_PATH`):

    [Projektpfad]/
    |-- 0_[ID]_picture-carrier/
    |   `-- *.tif                              <-- QUELLE (Hardware-Fotos)
    |-- 2_[ID]_extracted-files/
    |   |-- 2_[ID]_extracted-files.content     <-- QUELLE (Inhaltsbericht)
    |   `-- 2_[ID]_extracted-files_tree.txt    <-- QUELLE (Ordnerstruktur)
    |-- 3_[ID]_for-transfer/
    |   `-- 3_[ID]_for-transfer_tree.txt       <-- QUELLE (Ordnerstruktur nach Konvertierung)
    `-- 4_[ID]_VL/                             <-- ZIELORDNER (Konsolidierter Export)
        |-- *.tif                              <-- Kopierte Hardware-Fotos
        |-- 2_[ID]_extracted-files.content     <-- Kopierter Inhaltsbericht
        |-- 2_[ID]_extracted-files_tree.txt    <-- Kopierter Struktur-Tree (Stufe 2)
        `-- 3_[ID]_for-transfer_tree.txt       <-- Kopierter Struktur-Tree (Stufe 3)

## Technische Voraussetzungen

* **Windows 10/11**
* **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
* **Python-Paket:** `colorama` (in `requirements.txt` enthalten; Installation: `pip install -r requirements.txt`)
* **Standardbibliothek:** `os`, `sys`, `re`, `shutil`, `subprocess`, `pathlib`

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `8` (H_VL_Export) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript direkt über die Kommandozeile aufgerufen werden:

    python "H_VL_Export.py" AC_12345 ID_001 "C:\Pfad\zum\Datenordner"

Wird das Skript ohne Argumente gestartet (z. B. per Doppelklick), fragt es interaktiv nach AC-Nummer und Datenträger-ID.

### Ablauf der Ausführung

1. **Validierung:** Das Skript prüft die Existenz der Basisordner und des Zielverzeichnisses (Stufe 4).
2. **TIF-Kopiervorgang:** Alle Bilddateien aus Stufe 0 werden nach Stufe 4 übertragen.
3. **content-Kopiervorgang:** Die XML-Zusammenfassung (`.content`) aus Stufe 2 wird übertragen.
4. **Tree-Kopiervorgang (Stufe 2):** Die Text-Struktur `2_[ID]_extracted-files_tree.txt` wird übertragen.
5. **Tree-Kopiervorgang (Stufe 3):** Die Text-Struktur `3_[ID]_for-transfer_tree.txt` wird übertragen.
6. **Dubletten-Check:** Falls eine Datei bereits im Zielordner vorhanden ist, wird der Kopiervorgang für diese Datei übersprungen (Warnmeldung).
7. **Abschluss:** Der Benutzer kann den VL-Zielordner auf Wunsch direkt im Explorer öffnen.

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur

    [Projektpfad]/
    |-- 0_[Datenträger-ID]_picture-carrier/
    |   `-- *.tif                                     <-- QUELLE (alle TIF-Dateien)
    |-- 2_[Datenträger-ID]_extracted-files/
    |   |-- 2_[Datenträger-ID]_extracted-files.content  <-- QUELLE
    |   `-- 2_[Datenträger-ID]_extracted-files_tree.txt <-- QUELLE
    |-- 3_[Datenträger-ID]_for-transfer/
    |   `-- 3_[Datenträger-ID]_for-transfer_tree.txt    <-- QUELLE
    `-- 4_[Datenträger-ID]_VL/                          <-- ZIEL (muss existieren)

### Kopierte Dateien im Detail

| Quelle | Ziel | Bedingung |
|--------|------|------------|
| `0_[ID]_picture-carrier/*.tif` | `4_[ID]_VL/*.tif` | nur wenn Quelldatei existiert und Ziel nicht bereits vorhanden |
| `2_[ID]_extracted-files/2_[ID]_extracted-files.content` | `4_[ID]_VL/2_[ID]_extracted-files.content` | nur wenn Quelldatei existiert und Ziel nicht bereits vorhanden |
| `2_[ID]_extracted-files/2_[ID]_extracted-files_tree.txt` | `4_[ID]_VL/2_[ID]_extracted-files_tree.txt` | nur wenn Quelldatei existiert und Ziel nicht bereits vorhanden |
| `3_[ID]_for-transfer/3_[ID]_for-transfer_tree.txt` | `4_[ID]_VL/3_[ID]_for-transfer_tree.txt` | nur wenn Quelldatei existiert und Ziel nicht bereits vorhanden |

### Fehlerfälle und Abbruchbedingungen

| Fehlerfall | Verhalten |
|------------|-----------|
| `base_path` (`[AC]`-Ordner) existiert nicht | rote Meldung + `sys.exit(1)` |
| `main_folder` (`[AC]/[ID]`) existiert nicht | rote Meldung + `sys.exit(1)` |
| `destination_folder` (`4_[ID]_VL`) existiert nicht | rote Meldung + `sys.exit(1)` |
| Quellordner `0_[ID]_picture-carrier` existiert nicht | gelbe Warnung, Kopiervorgang wird übersprungen (kein Abbruch) |
| Quellordner `2_[ID]_extracted-files` existiert nicht | wird nicht separat geprüft; die fehlenden Dateien werden einzeln mit gelber Warnung gemeldet |
| Quelldatei existiert nicht | gelbe Warnung, keine Kopie |
| Zieldatei existiert bereits | gelbe Warnung, Überspringen (kein Überschreiben) |

### Kopiermethode

Das Skript verwendet `shutil.copy2()`, welches die ursprünglichen Metadaten (z. B. Zeitstempel) beibehält.

### TIF-Erkennung

Das Skript sucht mit `source_picture_carrier.glob("*.tif")` nach Dateien mit der Endung `.tif` (Groß-/Kleinschreibung wird nicht explizit behandelt; Windows ist case-insensitiv). Dateien mit Endung `.tiff` werden nicht erkannt.

### Dublettenprüfung

Für jede Datei wird vor dem Kopieren geprüft, ob die Zieldatei bereits existiert (`dest_file.exists()`). Wenn ja, erscheint eine gelbe Warnung und die Datei wird übersprungen.

### Farbkodierung (`colorama`)

| Farbe | Verwendung |
|-------|------------|
| Grün (`Fore.GREEN`) | Erfolgsmeldungen (Kopie erfolgreich, Pfade vorhanden) |
| Gelb (`Fore.YELLOW`) | Warnungen (Datei existiert bereits, Ordner/Datei nicht gefunden, manuelle Eingabe-Aufforderung) |
| Rot (`Fore.RED`) | Fehler (Pfade existieren nicht, Skriptabbruch) |
| Magenta (`Fore.MAGENTA`) | Kopfzeilen (Trennlinien, Überschriften) |
| Cyan (`Fore.CYAN`) | Abschnittsüberschriften ("Pfade definieren", "Kopiervorgang starten") |
| Weiß (`Fore.WHITE`) | Pfadausgabe |

### Fallback bei fehlenden Kommandozeilen-Argumenten

Wenn das Skript ohne AC-Nummer und Datenträger-ID gestartet wird, fragt es interaktiv nach den Werten. Die Meldung erscheint in Gelb.

### Plattformabhängiges Öffnen des Zielordners

Nach Abschluss fragt das Skript: `Zielordner oeffnen? (j/n):`. Bei `j`:

- **Windows** → `os.startfile(destination_folder)`
- **macOS** → `subprocess.run(["open", destination_folder])`
- **Linux/andere** → `subprocess.run(["xdg-open", destination_folder])`

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT