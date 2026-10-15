# L - Finale Archivierung (BagIt & Teil-Komprimierung)

Dieses Skript bildet den krönenden Abschluss des digitalen Archivierungsworkflows. Es transformiert den vorbereiteten Staging-Ordner (Stufe 5) in ein normgerechtes Archival Information Package (AIP) im BagIt-Format.

Besonderes Merkmal dieser Version ist die **gezielte Speicherplatz-Optimierung**: Der große Brunnhilde-Berichtsordner wird vor der BagIt-Erstellung komprimiert. Nach erfolgreicher Archivierung führt das Skript eine umfassende Bereinigung durch: Es löscht die temporären Arbeitsstufen 0, 1, 2 und 3, während die perfekt kuratierte VL-Stufe (Stufe 4) und das finale BagIt-Archiv (Stufe 5) als Endergebnis erhalten bleiben.

## Struktur

    L_BagIt_METS_TAR_Archivierung/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- L_BagIt_METS_TAR_Archivierung.py   <-- Ausführbare Python-Datei

## Hauptfunktionen

* **Gezielte Speicherplatz-Optimierung (Schritt 0):** Komprimiert den spezifischen, großen Unterordner `2_[ID]_extracted-files_brunnhilde` zu einem `.tar.gz`-Archiv und entfernt das unkomprimierte Original, bevor der Bag erstellt wird.
* **BagIt-Containerisierung:** Verwandelt die LZA-Stufe in einen BagIt-Bag. Alle Nutzdaten, Logs und das neue `.tar.gz`-Archiv wandern in das Unterverzeichnis `data/`, während kryptografische Manifeste die Integrität garantieren.
* **Master-Index verbleibt in data/logfiles/:** Der finale Master-Index (`.index`) verbleibt in `data/logfiles/` innerhalb des Bags.
* **Ordner-Umbenennung:** Nach erfolgreicher BagIt-Erstellung wird der Ordner `5_[ID]_LZA` in `<disk_id>` umbenannt – das finale AIP-Verzeichnis trägt also nur noch die Datenträger-ID.
* **Große Workflow-Bereinigung:**
  * Löscht die leeren Arbeits-Hüllen der Stufen 0, 1, 2 und 3.
  * **Behält** den Bag-Ordner (nach Umbenennung) als fertiges, durchsuchbares AIP-Verzeichnis bei.
* **Duales Output-Prinzip:** Die Stufe 4 (VL) bleibt als gebrauchsfertiges Resultat (Active Repository) für den direkten Import in das Bestandsführungssystem auf der Festplatte erhalten.

## TREE-Struktur & Das "Duale Ergebnis"

Nach Abschluss von Skript L sieht die Projektstruktur wie folgt aus (Ordner 0, 1, 2 und 3 wurden gelöscht):

    [Projektpfad]/

    |-- 4_[ID]_VL/                                     <-- ERGEBNIS 1: AKTIVES REPOSITORY
    |   |-- files/                                     <-- Bereinigte Nutzdaten & Derivate
    |   |-- 2_[ID]_extracted-files.content             <-- Inhaltsbericht (XML)
    |   |-- 2_[ID]_extracted-files_tree.txt            <-- Strukturbericht (Text)
    |   |-- 3_[ID]_for-transfer.index                  <-- Technisches Inventar (Vorstufe)
    |   `-- 3_[ID]_for-transfer_integrity.log          <-- Fixity-Nachweis (Phase 3)
    |
    `-- [ID]/                                          <-- ERGEBNIS 2: DAS BAGIT-AIP (umbenannt aus 5_[ID]_LZA)
        |-- data/                                      <-- Archivierte Nutzdaten & Logs
        |   |-- 3_files/                               <-- Alle extrahierten Originale & Derivate
        |   |-- image/                                 <-- Originalfotos der Hardware (unkomprimiert)
        |   `-- logfiles/
        |       |-- 1_[ID]_image-log.csv               <-- Imaging Metadaten (SHA-512)
        |       |-- 01_[ID]_image-log.txt              <-- Imaging Text-Log (KryoFlux/GW)
        |       |-- 2_[ID]_extracted-files.content     <-- XML Summary (Archiv-Kopie)
        |       |-- 2_[ID]_extracted-files_tree.txt    <-- Text Tree (Archiv-Kopie)
        |       |-- 2_[ID]_extracted-files_brunnhilde.tar.gz <-- KOMPRESSIERT: Forensik-Detailberichte
        |       |-- 2_[ID]_extracted-files_brunnhilde-summary.json
        |       |-- 3_[ID]_for-transfer.index          <-- Technischer Vor-Index
        |       |-- 3_[ID]_for-transfer_all-conversions.log
        |       |-- 3_[ID]_for-transfer_repair-file-extension.log
        |       |-- 3_[ID]_for-transfer_integrity.log  <-- Fixity-Beweis (Phase 3)
        |       |-- 5_[ID]_LZA.index                   <-- Master-Index (verbleibt in data/logfiles/)
        |       |-- 5_[ID]_LZA_premis.xml              <-- Erhaltungsmetadaten (PREMIS)
        |       `-- 5_[ID]_LZA_integrity.log           <-- Finaler Fixity-Beweis (Phase 4)
        |-- bagit.txt                                  <-- BagIt-Deklaration
        |-- bag-info.txt                               <-- Metadaten zum Bag
        `-- manifest-sha256.txt                        <-- Digitale Versiegelung

## Technische Voraussetzungen

* **Windows 10/11**
* **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
* **Python-Pakete:** `bagit`, `colorama` (in `requirements.txt` enthalten; Installation: `pip install -r requirements.txt`)
* **Standardbibliothek:** `os`, `sys`, `shutil`, `time`, `tarfile`, `glob`, `datetime`, `pathlib`

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

Das Skript wird im normalen Arbeitsablauf über das Hauptmenü gestartet:

1. `Start.bat` im Root doppelklicken → Hauptmenü
2. `D` eingeben (Datenaufbereitung)
3. AC-Nummer und Datenträger-ID über die Menüpunkte `A`, `D` oder `N` wählen
4. Skript `12` (L_BagIt_METS_TAR_Archivierung) auswählen

Die Parameter werden vom Menü automatisch an das Skript übergeben:

- `sys.argv[1]` = AC-Nummer
- `sys.argv[2]` = Datenträger-ID
- `sys.argv[3]` = Datenpfad (optional; alternativ Umgebungsvariable `DATA_PATH`)

Für manuelle Tests oder Debugging kann das Skript direkt über die Kommandozeile aufgerufen werden:

    python "L_BagIt_METS_TAR_Archivierung.py" AC_0001 ID_001 "C:\Pfad\zum\Datenordner"

### Ablauf der Finalisierung

1. **Sicherheitsabfrage:** Der Benutzer muss den Start bestätigen und offene Explorer-Fenster schließen.
2. **Teil-Komprimierung (Schritt 0):** Der Brunnhilde-Berichtsordner wird zu `.tar.gz` komprimiert und das Original gelöscht.
3. **Bagging (Schritt 1):** Der Ordner Stufe 5 wird in einen Bag verwandelt (Umzug der verbleibenden Daten nach `data/`).
4. **Index-Prüfung (Schritt 2):** Es wird geprüft, ob der Master-Index in `data/logfiles/` vorhanden ist.
5. **Manifest-Update (Schritt 3):** Der Bag berechnet seine Prüfsummen neu, um die neue `.tar.gz`-Datei einzuschließen.
6. **Ordner-Umbenennung (Schritt 4):** Der Ordner `5_[ID]_LZA` wird in `<disk_id>` umbenannt.
7. **Bereinigung (Schritt 5):** Nach erfolgreichem Durchlauf werden alle redundanten Ordner (0, 1, 2, 3) gelöscht. Der umbenannte Bag-Ordner bleibt als fertiges AIP bestehen.

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur vor Ausführung

    [Projektpfad]/
    |-- 4_[Datenträger-ID]_VL/                      <-- bleibt erhalten
    `-- 5_[Datenträger-ID]_LZA/                     <-- wird zu BagIt konvertiert
        |-- image/                                  <-- bleibt unkomprimiert
        |-- 3_files/                                <-- Nutzdaten
        |-- logfiles/                               <-- alle Logs und Metadaten
        |   |-- 2_[ID]_extracted-files_brunnhilde/  <-- wird zu .tar.gz komprimiert
        |   |-- 5_[ID]_LZA.index                    <-- Master-Index (verbleibt in logfiles/)
        |   `-- 5_[ID]_LZA_premis.xml               <-- PREMIS
        `-- [weitere Dateien]

### SCHRITT 0: Gezielte Komprimierung

Bevor BagIt läuft, wird ein spezifischer Pfad komprimiert:

* `f5_lza / "logfiles" / f"2_{disk_id}_extracted-files_brunnhilde"` → wird zu `2_{disk_id}_extracted-files_brunnhilde.tar.gz`

Nach erfolgreicher Komprimierung wird der Originalordner mit `shutil.rmtree` gelöscht, um Speicherplatz freizugeben. Der `image`-Ordner bleibt davon unberührt und wird normal in den Bag integriert.

### SCHRITT 1: BagIt-Erstellung

    bag = bagit.make_bag(str(f5_lza), metadata, checksums=['sha256'])

**Was passiert:**

* Der gesamte Inhalt von `5_[ID]_LZA/` (inklusive der soeben erstellten `.tar.gz`-Datei) wird in ein Unterverzeichnis `data/` verschoben.
* Es werden folgende BagIt-Dateien erstellt: `bagit.txt`, `bag-info.txt`, `manifest-sha256.txt`.
* **Metadaten im `bag-info.txt`:**
  * `Contact-Name`: Datenrettung Digit
  * `ZPH-ID`: [disk_id]
  * `External-Identifier`: [ac_number]

### SCHRITT 2: Master-Index bleibt in data/logfiles/

Der Master-Index (`5_[ID]_LZA.index`) verbleibt nach dem Bagging in `data/logfiles/`. Es findet **kein** Verschieben auf die Bag-Root-Ebene statt. Das Skript prüft lediglich, ob die Datei dort vorhanden ist, und gibt eine entsprechende Meldung aus.

### SCHRITT 3: BagIt-Manifeste aktualisieren

    bag.save(manifests=True)

Dadurch werden die bestehenden Manifest-Dateien (`manifest-sha256.txt`) neu berechnet, um die neu hinzugefügte `.tar.gz`-Datei in die Prüfsummen aufzunehmen.

### SCHRITT 4: Ordner-Umbenennung

Nach erfolgreichem Bagging wird der Ordner `5_[ID]_LZA` in `<disk_id>` umbenannt (sofern der Zielordner noch nicht existiert). Das finale AIP-Verzeichnis trägt also nur noch die Datenträger-ID.

Falls der Zielordner bereits existiert, wird die Umbenennung übersprungen und eine Warnung ausgegeben.

### SCHRITT 5: Bag bleibt erhalten, alte Stufen werden gelöscht

Der umbenannte Bag-Ordner bleibt in seiner BagIt-Struktur als finales, durchsuchbares Archival Information Package (AIP) auf der Festplatte bestehen.

Anschließend werden folgende Ordner gelöscht:

* `0_[ID]_picture-carrier`
* `1_[ID]_image-LZA`
* `2_[ID]_extracted-files`
* `3_[ID]_for-transfer`

Die **VL-Stufe (4) bleibt erhalten** als aktives Repository.

### Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| `f5_lza` existiert nicht | rote Fehlermeldung + `return` (kein harter Abbruch) |
| Master-Index nicht in `data/logfiles/` gefunden | gelbe Meldung, Skript fährt fort |
| Einzelner Ordner kann nicht gelöscht werden | gelbe Warnung, andere Ordner werden weiter gelöscht |
| Allgemeiner Fehler während der Verarbeitung | rote Meldung + Traceback wird ausgegeben |

### Wichtige Einschränkungen und Hinweise

* `tagmanifest-sha256.txt` wird standardmäßig nicht erstellt (nur `manifest-sha256.txt`), da `checksums` im Skript nur auf Manifeste, nicht auf Tag-Dateien angewendet wird.
* Die VL-Stufe (4) bleibt **unverändert** erhalten – nur die Stufen 0, 1, 2, 3 werden gelöscht. Der umbenannte Bag-Ordner bleibt als BagIt-AIP bestehen.
* Der `image`-Ordner wird **nicht** komprimiert, um einen direkten, schnellen Zugriff auf die Hardware-Fotos im AIP zu gewährleisten.

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT