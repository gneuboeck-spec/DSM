# Selektiver PDF-Lösch-Assistent

Ein Python-Skript zur automatischen Bereinigung von Verzeichnissen. Es löscht gezielt PDF-Dateien, die bestimmte Kriterien in Bezug auf Namenskonvention und Erstellungsdatum erfüllen.

## Zweck

Das Skript durchsucht einen Ordner und dessen Unterordner rekursiv nach PDF-Dateien. Eine PDF-Datei wird gelöscht, wenn **alle** der folgenden Bedingungen zutreffen:

1.  **Dateityp:** Die Datei ist eine PDF (`.pdf`).
2.  **Namenskonvention:** Die Datei folgt **nicht** dem Muster `Dateiname.alteEndung.pdf`.
    -   **Löschkandidat:** `Rechnung.pdf`, `Dokumentation.pdf`
    -   **Wird ignoriert:** `Scan.tif.pdf`, `Brief.docx.pdf`
3.  **Erstellungsdatum:** Die Datei wurde im konfigurierten Schwellenjahr oder später erstellt.

## Features

-   **Rekursive Suche:** Durchsucht den gesamten Verzeichnisbaum ab dem Startordner.
-   **Sicherheitsmodus:** Standardmäßig ist ein `DRY_RUN` (Simulationsmodus) aktiv, der nur anzeigt, welche Dateien gelöscht würden.
-   **Plattformunabhängig:** Dank `pathlib` unter Windows, macOS und Linux lauffähig.
-   **Klare Berichte:** Gibt eine übersichtliche Zusammenfassung der durchgeführten Aktionen aus.
-   **Einfache Konfiguration:** Alle wichtigen Parameter sind am Anfang des Skripts zentral gebündelt.

## Voraussetzungen

-   Python 3.x
-   Keine externen Bibliotheken notwendig.

## Anwendung

### 1. Skript konfigurieren

Öffnen Sie die Skript-Datei und passen Sie die Variablen im `KONFIGURATION`-Abschnitt an.

```python
# ==============================================================================
# 🔧 KONFIGURATION
# ==============================================================================

# 1. Pfad zum Arbeitsordner (bitte anpassen)
base_path = Path(r"C:\Users\IhrName\Desktop\Dokumente")

# 2. Schwellenjahr für die Löschung (inklusive dieses Jahres)
min_year = 2025

# 3. SICHERHEITSMODUS:
# True  = Zeigt nur an, was gelöscht werden würde (Simulation).
# False = LÖSCHT DIE DATEIEN WIRKLICH.
DRY_RUN = True