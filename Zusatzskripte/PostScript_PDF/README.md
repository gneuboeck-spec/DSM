# PostScript zu PDF Konvertierungsskript (Ghostscript Wrapper)

Dieses Skript automatisiert die Konvertierung von PostScript-Dateien (.ps) in das PDF-Format. Es ist speziell für digitale Archivierungsworkflows konzipiert, bei denen PostScript-Dateien als Zwischenformate (z. B. aus Lotus AmiPro) anfallen und in stabile PDF-Dokumente überführt werden müssen.

Das Skript nutzt Ghostscript als Konvertierungs-Engine und bietet eine intelligente Namenslogik für AmiPro-Dateien.

---

## Hauptfunktionen

*   **Vollständige Rekursion:** Durchsucht den angegebenen Quellordner und alle Unterverzeichnisse automatisch nach .ps-Dateien.
*   **Intelligente Namenslogik (SAM-Support):**
    *   Falls neben der `.ps`-Datei eine gleichnamige `.sam`-Datei existiert, wird die Zieldatei als `.sam.pdf` benannt.
    *   Andernfalls erfolgt die Standardkonvertierung nach `.pdf`.
*   **Ghostscript-Integration:** Nutzt professionelle Ghostscript-Parameter (`-sDEVICE=pdfwrite`), um qualitativ hochwertige PDF-Ausgaben zu erzeugen.
*   **Automatisches Überschreiben:** Falls bereits eine Zieldatei existiert, wird diese vor dem neuen Schreibvorgang sicher entfernt, um Konflikte zu vermeiden.
*   **Pfad-Validierung:** Prüft vor dem Start, ob sowohl die Ghostscript-Anwendung als auch das Quellverzeichnis tatsächlich vorhanden sind.

---

## Technische Voraussetzungen

*   **Python:** Version 3.4 oder neuer (nutzt das `pathlib`-Modul).
*   **Ghostscript:** Muss auf dem System installiert sein. Das Skript ist auf die 64-Bit-Version (`gswin64c.exe`) unter Windows vorkonfiguriert.

---

## Konfiguration

Vor der Nutzung müssen zwei Pfade im Skript-Header angepasst werden:

1.  **Arbeitsverzeichnis (`ps_dir`):**
    Geben Sie hier den Pfad zum Ordner an, in dem die PostScript-Dateien liegen.
    `ps_dir = Path(r"C:\Pfad\zu\Ihren\Dateien")`

2.  **Ghostscript-Pfad (`gs_path`):**
    Geben Sie den exakten Pfad zur ausführbaren Ghostscript-Datei an.
    `gs_path = Path(r"C:\Program Files\gs\gs[Version]\bin\gswin64c.exe")`

---

## Ausführung

Starten Sie das Skript über die Konsole:

    python ps_to_pdf_converter.py

### Ablauf der Konvertierung

1.  **System-Check:** Das Skript prüft die Erreichbarkeit von Ghostscript.
2.  **Dateisuche:** Erfassung aller `.ps`-Dateien im Verzeichnisbaum.
3.  **Namensprüfung:** Abgleich mit vorhandenen `.sam`-Dateien zur Bestimmung der Endung.
4.  **Konvertierung:** Ghostscript wandelt jede Datei im Hintergrund ("headless") um.
5.  **Feedback:** Erfolg oder Fehlermeldungen werden für jede Datei direkt im Terminal ausgegeben.

---

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert. Das bedeutet, es darf frei verwendet, kopiert und modifiziert werden, solange der obige Copyright-Hinweis erhalten bleibt.

---
**SPDX-FileCopyrightText:** 2025 Gregor Neuboeck  
**SPDX-License-Identifier:** MIT