# LZA-Paket-Generator (BagIt & TAR Master)

Dieses Skript bildet den krönenden Abschluss des Archivierungsworkflows. Es führt alle Teilergebnisse eines Projekts zusammen, erstellt einen validen **BagIt-Container** (inkl. SHA-256 Prüfsummen für jede Datei) und verpackt das Ergebnis in ein unkomprimiertes **TAR-Archiv**.

Das resultierende Paket ist ein vollständig dokumentiertes **Archival Information Package (AIP)**, das bereit für die Langzeitarchivierung ist.

---

## Funktionsumfang

*   **Daten-Aggregation:** Sammelt automatisch alle relevanten Daten aus den Prozessstufen 0 (Image), 1 (LZA-Image), 2 (Analyse) und 3 (Konvertierung & Logs).
*   **Fehlertoleranz:** Das Skript bricht nicht ab, wenn einzelne Log-Dateien fehlen, sondern protokolliert dies und fährt mit den vorhandenen Daten fort.
*   **BagIt-Standard:** Erstellt eine offizielle BagIt-Struktur inklusive Metadaten (`Contact-Name`, `ZPH-ID`, etc.) und berechnet Fixity-Werte (SHA-256) für alle Dateien.
*   **TAR-Container:** Verpackt den gesamten Bag unkomprimiert in ein TAR-Archiv. Dies erleichtert den Transfer und schützt die Bag-Struktur.
*   **Sicherheits-Check:** Beinhaltet eine Abfrage zum Schließen von Windows-Explorer-Fenstern, um Zugriffsfehler während der Bag-Erstellung zu vermeiden.
*   **Automatisches Cleanup:** Löscht den temporären Arbeitsordner (`5_..._LZA`) nach der erfolgreichen Erstellung des TAR-Archivs, um Speicherplatz zu sparen.

---

## Technische Details

*   **Container-Format:** Unkomprimiertes TAR (Tape Archive).
*   **Fixity:** SHA-256 (innerhalb des BagIt-Manifests).
*   **Namenskonvention:** `AC-Nummer_ZPH-ID_Zeitstempel.tar`
*   **Zeitstempel-Format:** `YYYYMMDD_HHMMSS`

---

## Erwartete Ordnerstruktur

Das Skript erwartet die Standard-Projektstruktur im `Documents/data`-Verzeichnis:

```text
Documents/data/[AC-Nummer]/[ZPH-ID]/
├── 0_..._picture-carrier/
├── 1_..._image-LZA/
├── 2_..._extracted-files/
├── 3_..._for-transfer/
└── 5_..._LZA/                  <-- Ziel- & Staging-Ordner
```

---

## Ausführung

Starten Sie das Skript über das Hauptmenü oder direkt via Batch-Datei:

```batch
python lza_bagging_skript.py AC12345678 ZPH1705-120
```

### Ablauf

1.  **Sicherheitsabfrage:** Bestätigen Sie, dass alle Explorer-Fenster geschlossen sind.
2.  **Collection:** Alle verfügbaren Dateien aus den Vorstufen werden in den Ordner `5` verschoben.
3.  **Bagging:** Der Ordner `5` wird "gebaggt" (Erstellung von Manifesten und Metadaten-Tags).
4.  **Validation:** Der Bag wird sofort auf Integrität geprüft.
5.  **Archivierung:** Der valide Bag wird in die `.tar`-Datei geschrieben.
6.  **Cleanup:** Der nun redundante Ordner `5` wird entfernt.

---

## Lizenz

**Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>**

Dieses Skript ist unter der **MIT-Lizenz** lizenziert.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT