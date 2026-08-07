# L - Finale Archivierung (BagIt & Teil-Komprimierung)

Dieses Skript bildet den krönenden Abschluss des digitalen Archivierungsworkflows. Es transformiert den vorbereiteten Staging-Ordner (Stufe 5) in ein normgerechtes Archival Information Package (AIP) im BagIt-Format. 

Besonderes Merkmal dieser Version ist die **gezielte Speicherplatz-Optimierung**: Der große Brunnhilde-Berichtsordner wird vor der BagIt-Erstellung komprimiert. Nach erfolgreicher Archivierung führt das Skript eine umfassende Bereinigung durch: Es löscht die temporären Arbeitsstufen 0, 1, 2 und 3, während die perfekt kuratierte VL-Stufe (Stufe 4) und das finale BagIt-Archiv (Stufe 5) als Endergebnis erhalten bleiben.

---

## Hauptfunktionen

* **Gezielte Speicherplatz-Optimierung (Schritt 0):** Komprimiert den spezifischen, großen Unterordner `2_[ID]_extracted-files_brunnhilde` zu einem `.tar.gz`-Archiv und entfernt das unkomprimierte Original, bevor der Bag erstellt wird.
* **BagIt-Containerisierung:** Verwandelt die LZA-Stufe in einen BagIt-Bag. Alle Nutzdaten, Logs und das neue `.tar.gz`-Archiv wandern in das Unterverzeichnis `data/`, während kryptografische Manifeste die Integrität garantieren.
* **Tag-File Placement:** Positioniert den finalen Master-Index (`.index`) außerhalb des Datenverzeichnisses auf der Root-Ebene des Bags, um einen schnellen Zugriff auf das Inventar zu ermöglichen.
* **METS-Generierung:** Erstellt eine `mets.xml` im Bag-Root. Diese Datei verknüpft den beschreibenden Master-Index (DMD) und die erhaltungsspezifischen PREMIS-Metadaten (AMD) logisch miteinander.
* **Große Workflow-Bereinigung:**
  * Löscht die leeren Arbeits-Hüllen der Stufen 0, 1, 2 und 3.
  * **Behält** den Bag-Staging-Ordner (Stufe 5) als fertiges, durchsuchbares AIP-Verzeichnis bei.
* **Duales Output-Prinzip:** Die Stufe 4 (VL) bleibt als gebrauchsfertiges Resultat (Active Repository) für den direkten Import in das Bestandsführungssystem auf der Festplatte erhalten.

---

## TREE-Struktur & Das "Duale Ergebnis"

Nach Abschluss von Skript L sieht die Projektstruktur wie folgt aus (Ordner 0, 1, 2 und 3 wurden gelöscht):

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/

├── 4_[ID]_VL/                                     <-- ERGEBNIS 1: AKTIVES REPOSITORY
│   ├── files/                                     <-- Bereinigte Nutzdaten & Derivate
│   ├── 2_[ID]_extracted-files.content             <-- Inhaltsbericht (XML)
│   ├── 2_[ID]_extracted-files_tree.txt            <-- Strukturbericht (Text)
│   ├── 3_[ID]_for-transfer.index                  <-- Technisches Inventar (Vorstufe)
│   └── 3_[ID]_for-transfer_integrity.log          <-- Fixity-Nachweis (Phase 3)

└── 5_[ID]_LZA/                                    <-- ERGEBNIS 2: DAS BAGIT-AIP
    ├── data/                                      <-- Archivierte Nutzdaten & Logs
    │   ├── 3_files/                               <-- Alle extrahierten Originale & Derivate
    │   ├── image/                                 <-- Originalfotos der Hardware (unkomprimiert)
    │   └── logfiles/
    │       ├── 1_[ID]_image-log.csv               <-- Imaging Metadaten (SHA-512)
    │       ├── 01_[ID]_image-log.txt              <-- Imaging Text-Log (KryoFlux/GW)
    │       ├── 2_[ID]_extracted-files.content     <-- XML Summary (Archiv-Kopie)
    │       ├── 2_[ID]_extracted-files_tree.txt    <-- Text Tree (Archiv-Kopie)
    │       ├── 2_[ID]_extracted-files_brunnhilde.tar.gz <-- KOMPRESSIERT: Forensik-Detailberichte
    │       ├── 2_[ID]_extracted-files_brunnhilde-summary.json
    │       ├── 3_[ID]_for-transfer.index          <-- Technischer Vor-Index
    │       ├── 3_[ID]_for-transfer_all-conversions.log
    │       ├── 3_[ID]_for-transfer_repair-file-extension.log
    │       ├── 3_[ID]_for-transfer_integrity.log  <-- Fixity-Beweis (Phase 3)
    │       ├── 5_[ID]_LZA_premis.xml              <-- Erhaltungsmetadaten (PREMIS)
    │       └── 5_[ID]_LZA_integrity.log           <-- Finaler Fixity-Beweis (Phase 4)
    ├── 5_[ID]_LZA.index                           <-- Master-Index (Tag-File)
    ├── mets.xml                                   <-- METS-Steuerdatei (Tag-File)
    ├── bagit.txt                                  <-- BagIt-Deklaration
    ├── bag-info.txt                               <-- Metadaten zum Bag
    └── manifest-sha256.txt                        <-- Digitale Versiegelung
```

---

## Technische Voraussetzungen

* **Python:** Version 3.10 oder neuer empfohlen.
* **Bibliotheken:** Benötigt `bagit` für die Containerisierung und `colorama` für die Statusanzeige.
  ```bash
  pip install bagit colorama
  ```

---

## Ausführung

Das Skript wird im normalen Arbeitsablauf über den zentralen **Workflow Launcher** (`Workflow_Launcher_start.bat`) und das darauf folgende **Auswahlmenü** gestartet. Die benötigten Parameter (AC-Nummer und Datenträger-ID) werden dabei automatisch vom Menü an das Skript übergeben.

Für manuelle Tests oder Debugging kann das Skript auch direkt über die Kommandozeile aufgerufen werden. Es erwartet zwei Argumente: die AC-Nummer und die Datenträger-ID.

**Beispiel für einen manuellen Aufruf:**

```bat
@echo off
set AC_NUMBER=AC_0001
set DISK_ID=ID_001
python "L_BagIt_METS_Archivierung.py" %AC_NUMBER% %DISK_ID%
pause
```

### Ablauf der Finalisierung

1. **Sicherheitsabfrage:** Der Benutzer muss den Start bestätigen und offene Explorer-Fenster schließen.
2. **Teil-Komprimierung (Schritt 0):** Der Brunnhilde-Berichtsordner wird zu `.tar.gz` komprimiert und das Original gelöscht.
3. **Bagging (Schritt 1):** Der Ordner Stufe 5 wird in einen Bag verwandelt (Umzug der verbleibenden Daten nach `data/`).
4. **Index-Fix (Schritt 2):** Der Master-Index wird aus dem Datenordner auf die oberste Bag-Ebene verschoben.
5. **METS-Erstellung (Schritt 3):** Die `mets.xml` wird generiert und referenziert den Index und die PREMIS-Datei.
6. **Manifest-Update (Schritt 4):** Der Bag berechnet seine Prüfsummen neu, um die neuen Tag-Files (Index & METS) einzuschließen.
7. **Bereinigung (Schritt 5 & 6):** Nach erfolgreichem Durchlauf werden alle redundanten Ordner (0, 1, 2, 3) gelöscht. Der Ordner 5 bleibt als fertiges AIP bestehen.

---

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur vor Ausführung

```text
C:\Users\digit\Documents\data\[AC-Nummer]\[Datenträger-ID]/
├── 4_[Datenträger-ID]_VL/                      <-- bleibt erhalten
└── 5_[Datenträger-ID]_LZA/                     <-- wird zu BagIt konvertiert
    ├── image/                                  <-- bleibt unkomprimiert
    ├── 3_files/                                <-- Nutzdaten
    ├── logfiles/                               <-- alle Logs und Metadaten
    │   └── 2_[ID]_extracted-files_brunnhilde/  <-- wird zu .tar.gz komprimiert
    ├── 5_[ID]_LZA.index                        <-- Master-Index
    └── 5_[ID]_LZA_premis.xml                   <-- PREMIS
```

**⚠️ Wichtiger Hinweis zum Pfad:** Das Skript verwendet einen fest codierten Basispfad:
```python
base_root = Path(r"C:\Users\digit\Documents\data")
```
Dies muss bei Bedarf an die lokale Umgebung angepasst werden.

### SCHRITT 0: Gezielte Komprimierung

Bevor BagIt läuft, wird ein spezifischer Pfad komprimiert:
* `f5_lza / "logfiles" / f"2_{disk_id}_extracted-files_brunnhilde"` → wird zu `2_{disk_id}_extracted-files_brunnhilde.tar.gz`

Nach erfolgreicher Komprimierung wird der Originalordner mit `shutil.rmtree` gelöscht, um Speicherplatz freizugeben. Der `image`-Ordner bleibt davon unberührt und wird normal in den Bag integriert.

### SCHRITT 1: BagIt-Erstellung

```python
bag = bagit.make_bag(str(f5_lza), metadata, checksums=['sha256'])
```
**Was passiert:**
* Der gesamte Inhalt von `5_[ID]_LZA/` (inklusive der soeben erstellten `.tar.gz`-Datei) wird in ein Unterverzeichnis `data/` verschoben.
* Es werden folgende BagIt-Dateien erstellt: `bagit.txt`, `bag-info.txt`, `manifest-sha256.txt`.
* **Metadaten im `bag-info.txt`:**
  * `Contact-Name`: Datenrettung Digit
  * `ZPH-ID`: [disk_id]
  * `External-Identifier`: [ac_number]

### SCHRITT 2: Master-Index als Tag-File positionieren

Das Skript sucht im neu erstellten `data/`-Unterordner rekursiv nach der Datei `5_[ID]_LZA.index`. Sobald gefunden, wird sie auf die Bag-Root-Ebene (`f5_lza`) verschoben. Der Index fungiert somit als Tag-File.

### SCHRITT 3: METS-Datei generieren

Die `mets.xml` wird mit folgendem festen Aufbau erstellt:
* `OBJID`: `[ac_number]_[disk_id]`
* `dmdSec/mdRef`: Verweist auf `5_[ID]_LZA.index`
* `amdSec/techMD/mdRef`: Verweist auf `data/logfiles/5_[ID]_LZA_premis.xml`
* `fileSec/fileGrp/file/FLocat`: Verweist auf `data/`

### SCHRITT 4: BagIt-Manifeste aktualisieren

```python
bag.save(manifests=True)
```
Dadurch werden die bestehenden Manifest-Dateien (`manifest-sha256.txt`) neu berechnet, um die neu hinzugefügten oder verschobenen Tag-Files (`mets.xml`, `5_[ID]_LZA.index`) in die Prüfsummen aufzunehmen.

### SCHRITT 5 & 6: Bag bleibt erhalten, alte Stufen werden gelöscht

Der Ordner `5_[ID]_LZA` bleibt in seiner BagIt-Struktur als finales, durchsuchbares Archival Information Package (AIP) auf der Festplatte bestehen. 
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
| Master-Index nicht in `data/` gefunden | rote Meldung, Skript fährt fort |
| Einzelner Ordner kann nicht gelöscht werden | gelbe Warnung, andere Ordner werden weiter gelöscht |
| Allgemeiner Fehler während der Verarbeitung | rote Meldung + Traceback wird ausgegeben |

### Abhängigkeiten

**Erforderliche Python-Pakete:**
* `bagit` (für BagIt-Containerisierung)
* `colorama` (für farbige Terminal-Ausgabe; Fallback bei Importfehler)

**Standardbibliothek:** `os`, `sys`, `shutil`, `time`, `tarfile`, `glob`, `datetime`, `pathlib`

### Wichtige Einschränkungen und Hinweise

* Der Basispfad ist **fest codiert** auf `C:\Users\digit\Documents\data`.
* `tagmanifest-sha256.txt` wird standardmäßig nicht erstellt (nur `manifest-sha256.txt`), da `checksums` im Skript nur auf Manifeste, nicht auf Tag-Dateien angewendet wird.
* Die METS-Datei wird erst nach dem initialen `make_bag` erstellt und dann via `bag.save()` in das Manifest aufgenommen.
* Die VL-Stufe (4) bleibt **unverändert** erhalten – nur die Stufen 0, 1, 2, 3 werden gelöscht. Stufe 5 bleibt als BagIt-AIP bestehen.
* Der `image`-Ordner wird **nicht** komprimiert, um einen direkten, schnellen Zugriff auf die Hardware-Fotos im AIP zu gewährleisten.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT