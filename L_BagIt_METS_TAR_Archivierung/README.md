# Skript L: Final Archiving (BagIt, METS & TAR-Versiegelung)

Dieses Skript bildet den krönenden Abschluss des digitalen Archivierungsworkflows. Es transformiert den vorbereiteten Staging-Ordner (Stufe 5) in ein normgerechtes Archival Information Package (AIP). Dabei wird ein BagIt-Container erstellt, eine METS-Steuerungsdatei generiert und alles in ein finales TAR-Archiv versiegelt. 

Nach erfolgreicher Archivierung führt das Skript eine umfassende Bereinigung durch: Es löscht die temporären Arbeitsstufen 0, 1, 2, 3 und 5, während die perfekt kuratierte VL-Stufe (Stufe 4) als aktives Repository erhalten bleibt.

---

## Hauptfunktionen

*   **BagIt-Containerisierung:** Verwandelt die LZA-Stufe in einen BagIt-Bag. Alle Nutzdaten und Logs wandern in das Unterverzeichnis data/, während kryptografische Manifeste die Integrität jeder einzelnen Datei garantieren.
*   **Tag-File Placement:** Positioniert den finalen Master-Index (.index) außerhalb des Datenverzeichnisses auf der Root-Ebene des Bags, um einen schnellen Zugriff auf das Inventar zu ermöglichen.
*   **METS-Generierung:** Erstellt eine mets.xml im Bag-Root. Diese Datei verknüpft den beschreibenden Master-Index (DMD) und die erhaltungsspezifischen PREMIS-Metadaten (AMD) logisch miteinander.
*   **TAR-Versiegelung:** Verpackt den gesamten Container in ein flaches, unkomprimiertes TAR-Archiv. Der Dateiname ist eindeutig durch AC-Nummer, Datenträger-ID und Zeitstempel definiert.
*   **Große Workflow-Bereinigung:**
    *   Löscht die leeren Arbeits-Hüllen der Stufen 0, 1, 2 und 3.
    *   Entfernt den temporären Bag-Staging-Ordner (Stufe 5) nach erfolgreicher TAR-Erstellung.
*   **Duales Output-Prinzip:** Die Stufe 4 (VL) bleibt als gebrauchsfertiges Resultat (Active Repository) für den direkten Import in das Bestandsführungssystem auf der Festplatte erhalten.

---

## TREE-Struktur & Das "Duale Ergebnis"

Nach Abschluss von Skript L sieht die Projektstruktur wie folgt aus (Ordner 0, 1, 2, 3 und 5 wurden gelöscht):

```text
Documents/data/[AC-Nummer]/[Datenträger-ID]/

├── 4_[ID]_VL/                                     <-- ERGEBNIS 1: AKTIVES REPOSITORY
│   ├── files/                                     <-- Bereinigte Nutzdaten & Derivate
│   ├── 2_[ID]_extracted-files.content             <-- Inhaltsbericht (XML)
│   ├── 2_[ID]_extracted-files_tree.txt            <-- Strukturbericht (Text)
│   ├── 3_[ID]_for-transfer.index                  <-- Technisches Inventar (Vorstufe)
│   └── 3_[ID]_for-transfer_integrity.log          <-- Fixity-Nachweis (Phase 3)

└── [AC]_[ID]_[ZEITSTEMPEL].tar                    <-- ERGEBNIS 2: DER TRESOR (AIP)
    └── (Interner Aufbau des Bags)
        ├── data/                                  <-- Archivierte Nutzdaten & Logs
        │   ├── 3_files/                           <-- Alle extrahierten Originale & Derivate
        │   └── logfiles/
        │       ├── *.tif                          <-- Originalfotos der Hardware
        │       ├── 1_[ID]_image-log.csv           <-- Imaging Metadaten (SHA-512)
        │       ├── 01_[ID]_image-log.txt          <-- Imaging Text-Log (KryoFlux/GW)
        │       ├── 2_[ID]_extracted-files.content <-- XML Summary (Archiv-Kopie)
        │       ├── 2_[ID]_extracted-files_tree.txt <-- Text Tree (Archiv-Kopie)
        │       ├── 2_[ID]_extracted-files_brunnhilde-summary.json <-- Forensik-Zusammenfassung
        │       ├── 2_[ID]_extracted-files_brunnhilde/ <-- Ordner mit Detailberichten
        │       ├── 3_[ID]_for-transfer.index      <-- Technischer Vor-Index
        │       ├── 3_[ID]_for-transfer_all-conversions.log <-- Normalisierungs-Protokoll
        │       ├── 3_[ID]_for-transfer_repair-file-extension.log <-- Reparatur-Protokoll
        │       ├── 3_[ID]_for-transfer_integrity.log <-- Fixity-Beweis (Phase 3)
        │       ├── 5_[ID]_LZA_premis.xml          <-- Erhaltungsmetadaten (PREMIS)
        │       └── 5_[ID]_LZA_integrity.log       <-- Finaler Fixity-Beweis (Phase 4)
        ├── 5_[ID]_LZA.index                       <-- Master-Index (Tag-File)
        ├── mets.xml                               <-- METS-Steuerdatei (Tag-File)
        ├── bagit.txt                              <-- BagIt-Deklaration
        ├── bag-info.txt                           <-- Metadaten zum Bag
        └── manifest-sha256.txt                    <-- Digitale Versiegelung
```
---

## Technische Voraussetzungen

*   Python: Version 3.10 oder neuer empfohlen.
*   Bibliotheken: Benötigt bagit für die Containerisierung und colorama für die Statusanzeige.
    pip install bagit colorama

---

## Ausführung

Das Skript erwartet die AC-Nummer und die Datenträger-ID als Argumente.

Beispielhafter Aufruf in einer start.bat:
    python Skript_L_Final_Archiving.py AC_0001 ID_001

### Ablauf der Finalisierung

1. Sicherheitsabfrage: Der Benutzer muss den Start bestätigen.
2. Bagging: Der Ordner Stufe 5 wird in einen Bag verwandelt (Umzug der Daten nach data/).
3. Index-Fix: Der Master-Index wird aus dem Datenordner auf die oberste Bag-Ebene verschoben.
4. METS-Erstellung: Die mets.xml wird generiert und referenziert den Index und die PREMIS-Datei.
5. Manifest-Update: Der Bag berechnet seine Prüfsummen neu, um die Tag-Files (Index & METS) einzuschließen.
6. Archivierung: Das gesamte Paket wird in eine TAR-Datei geschrieben.
7. Bereinigung: Nach erfolgreichem Schreibvorgang werden alle redundanten Ordner (0, 1, 2, 3, 5) gelöscht.

---

## Detaillierte Hinweise zum Skriptverhalten

### Erwartete Ordnerstruktur vor Ausführung

```text
C:\Users\digit\Documents\data\[AC_number]\[disk_archive_ID]/
├── 4_[disk_archive_ID]_VL/                      <-- bleibt erhalten
└── 5_[disk_archive_ID]_LZA/                     <-- wird zu BagIt konvertiert
    ├── 3_files/                                 <-- Nutzdaten
    ├── logfiles/                                <-- alle Logs und Metadaten
    ├── 5_[ID]_LZA.index                         <-- Master-Index (optional, wird in data/ erwartet)
    ├── 5_[ID]_LZA_premis.xml                    <-- PREMIS (optional, wird in data/logfiles/ erwartet)
    └── [andere Dateien aus Stufe 1-3]           <-- werden ebenfalls in data/ verschoben
```
**Wichtiger Hinweis zum Pfad:** Das Skript verwendet einen fest codierten Basispfad:

base_root = Path(r"C:\Users\digit\Documents\data")

Dies muss bei Bedarf an die lokale Umgebung angepasst werden.

### SCHRITT 1: BagIt-Erstellung

bag = bagit.make_bag(str(f5_lza), metadata, checksums=['sha256'])

**Was passiert:**
- Der gesamte Inhalt von `5_[ID]_LZA/` wird in ein Unterverzeichnis `data/` verschoben
- Es werden folgende BagIt-Dateien erstellt: `bagit.txt`, `bag-info.txt`, `manifest-sha256.txt`
- **Nicht** erstellt wird `tagmanifest-sha256.txt` (da `checksums` nur auf Manifeste angewendet wird, nicht auf Tag-Dateien)

**Metadaten im bag-info.txt:**

Contact-Name: Datenrettung Digit
ZPH-ID: [disk_id]
External-Identifier: [ac_number]


### SCHRITT 2: Master-Index als Tag-File positionieren

Das Skript sucht im neu erstellten `data/`-Unterordner rekursiv nach der Datei `5_[ID]_LZA.index`. Sobald gefunden, wird sie **nach `f5_lza / master_index_name`** (also auf Bag-Root-Ebene) verschoben.

**Wichtig:** Der Index muss sich nach diesem Schritt also **außerhalb** des `data/`-Verzeichnisses befinden, damit er als Tag-File im Bag-Container fungiert.

### SCHRITT 3: METS-Datei generieren

Die `mets.xml` wird mit folgendem festen Aufbau erstellt:

| Element | Inhalt |
|---------|--------|
| `OBJID` | `[ac_number]_[disk_id]` |
| `dmdSec/mdRef` | `MDTYPE="OTHER" OTHERMDTYPE="MASTER-INDEX"` → verweist auf `5_[ID]_LZA.index` |
| `amdSec/techMD/mdRef` | `MDTYPE="PREMIS"` → verweist auf `data/logfiles/5_[ID]_LZA_premis.xml` |
| `fileSec/fileGrp/file/FLocat` | `xlink:href="data/"` |
| `structMap` | Physische Struktur: AIP → VOLUME → fptr zu FILEID="BAG_0001" |

**Wichtige Einschränkung:** Die METS-Datei wird **nicht** bei späteren `bag.save()`-Aufrufen automatisch in das Manifest aufgenommen, da sie erst nach der ersten `make_bag` erstellt wird.

### SCHRITT 4: BagIt-Manifeste aktualisieren

bag.save(manifests=True)

Dadurch werden:
- Die bestehenden Manifest-Dateien (`manifest-sha256.txt`) neu berechnet
- **Achtung:** `tagmanifest-sha256.txt` wird standardmäßig nicht erstellt (wird nur bei `save(manifests=True, tag_manifests=True)` generiert)

### SCHRITT 5: TAR-Archiv erstellen

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
tar_name = f"{ac_number}_{disk_id}_{timestamp}.tar"
tar_full_path = disk_path / tar_name

with tarfile.open(tar_full_path, "w") as tar:
    for item in os.listdir(f5_lza):
        tar.add(f5_lza / item, arcname=item)

**Besonderheiten:**
- Unkomprimiertes TAR (Modus `"w"`, nicht `"w:gz"`)
- Alle Inhalte von `f5_lza` werden auf oberster Ebene im TAR abgelegt (kein zusätzliches Wurzelverzeichnis)
- Der Zeitstempel im Dateinamen verhindert Überschreiben

### SCHRITT 6: Bereinigung des temporären Bag-Ordners

shutil.rmtree(f5_lza)

Löscht den gesamten `5_[ID]_LZA`-Ordner nach erfolgreicher TAR-Erstellung.

### SCHRITT 7: Löschen der alten Stufen 0-3

Gelöscht werden folgende Ordner (unabhängig davon, ob sie existieren):

stages_to_delete = [
    f"0_{disk_id}_picture-carrier",
    f"1_{disk_id}_image-LZA",
    f"2_{disk_id}_extracted-files",
    f"3_{disk_id}_for-transfer"
]

**VL-Stufe (4) bleibt erhalten** als aktives Repository.

### Sicherheitsabfrage

Vor der Ausführung erscheint:

[!] HINWEIS: Explorer-Fenster von 5_[ID]_LZA schliessen.
 Bagging und Archivierung jetzt starten? (j/n):

Nur bei Eingabe `j` wird fortgefahren.

### Fehlerbehandlung

| Fehlerfall | Verhalten |
|------------|-----------|
| `f5_lza` existiert nicht | rote Fehlermeldung + `return` (kein Abbruch mit `sys.exit`) |
| Master-Index nicht in `data/` gefunden | rote Meldung, Skript fährt fort |
| Einzelner Ordner kann nicht gelöscht werden | gelbe Warnung, andere Ordner werden weiter gelöscht |
| Allgemeiner Fehler während der Verarbeitung | rote Meldung + Traceback wird ausgegeben |

### Endgültige Projektstruktur nach Skriptende

```Text
C:\Users\digit\Documents\data\[AC_number]\[disk_archive_ID]/
├── 4_[disk_archive_ID]_VL/                      <-- ERGEBNIS 1 (Active Repository)
│   ├── files/
│   ├── 2_[ID]_extracted-files.content
│   ├── 2_[ID]_extracted-files_tree.txt
│   ├── 3_[ID]_for-transfer.index
│   └── 3_[ID]_for-transfer_integrity.log
└── [AC_number]_[disk_archive_ID]_[YYYYMMDD_HHMMSS].tar   <-- ERGEBNIS 2 (AIP)
```
### Abhängigkeiten

**Erforderliche Python-Pakete:**
- `bagit` (für BagIt-Containerisierung)
- `colorama` (für farbige Terminal-Ausgabe; Fallback bei Importfehler)

**Standardbibliothek:** `os`, `sys`, `shutil`, `time`, `tarfile`, `glob`, `datetime`, `pathlib`

### Wichtige Einschränkungen und Hinweise

- Der Basispfad ist **fest codiert** auf `C:\Users\digit\Documents\data`
- `tagmanifest-sha256.txt` wird **nicht** erstellt (nur `manifest-sha256.txt`)
- Die METS-Datei wird **nicht** von BagIt manifestiert (da sie nach dem letzten `save` erstellt wird)
- Das TAR-Archiv ist **unkomprimiert** (nur Verpackung, keine Kompression)
- Die VL-Stufe (4) bleibt **unverändert** erhalten – nur die Stufen 0,1,2,3,5 werden gelöscht
- Es gibt **keine Prüfung**, ob das TAR-Archiv bereits existiert (Zeitstempel verhindert Überschreiben nur im selben Sekundenbruchteil)

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck
SPDX-License-Identifier: MIT