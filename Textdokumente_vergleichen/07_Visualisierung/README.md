# 07 - Visualisierung

Macht die komplexen Ergebnisse der vorangegangenen Skripte für Bewerter:innen und Archivar:innen intuitiv begreifbar. Es generiert interaktive Diagramme auf Basis der in Schritt 05 und 06 erstellten Excel- bzw. CSV-Datei.

## Struktur

    07_Visualisierung/
    |-- README.md                          <-- Diese Datei
    `-- win/
        `-- 07_Visualisierung.py           <-- Ausführbare Python-Datei

## Funktionsweise

Das Skript bietet ein Hauptmenü mit zwei Ansichtsmodi.

### 1. Gesamtübersicht

Vier Diagramme stehen zur Auswahl (einzeln oder als 2x2-Grid):

- **Dokumente pro Gruppe**: Balkendiagramm der Gruppengrößen.
- **Verteilung Dokumententypen**: Kreisdiagramm (Versionen vs. Kurztexte vs. Unklassifiziert).
- **Durchschnittliche Dateigröße pro Gruppe**: Balkendiagramm.
- **KI-Ähnlichkeit aller Kurztexte**: Horizontales Balkendiagramm mit Farbkodierung (grün ≥ 70%, orange ≥ 55%, rot < 55%) und roter Linie am Standard-Threshold.

### 2. Detailansicht pro Gruppe

Nach Auswahl einer Gruppe öffnet sich ein zweites Menü mit vier Diagrammen:

- **Zeitstrahl**: Chronologische Entwicklung der Dokumente. Bei sehr kleinen Zeitabständen (< 1 Stunde) zeigt die Achse Sekunden an – sonst Datum + Uhrzeit. Die Dokumentennamen werden bei Bedarf versetzt über/unter der Achse platziert, um Überlappungen zu vermeiden.
- **Dateigrößen-Vergleich**: Horizontales Balkendiagramm aller Dokumente der Gruppe.
- **Text-Änderung gegen Basis**: Zeigt die prozentuale Zu-/Abnahme der Zeichenanzahl im Vergleich zum Basisdokument.
- **KI-Ähnlichkeit**: Detaillierte Ansicht der Kurztext-Zuordnungen innerhalb dieser spezifischen Gruppe.

## Datenquelle

Das Skript liest bevorzugt `versionen_analyse_mit_ki.csv` aus dem Ausgabeverzeichnis. Falls diese nicht existiert, wird auf `versionen_analyse.csv` zurückgegriffen.

**Vorbedingung:** Die CSV muss zuvor von `05_Dokumente_vergleichen.py` (und optional `06_KI_Analyse.py`) erzeugt worden sein. Fehlt sie, bricht das Skript mit einer Meldung ab.

## Technische Voraussetzungen

- **Windows 10/11**
- **Python 3.13** oder höher (siehe Hinweis zur Fallback-Kette unten)
- **Python-Pakete:** `matplotlib` (in `requirements.txt` enthalten; Installation: `pip install -r requirements.txt`)
- **`tkinter`** ist Teil der Python-Standardbibliothek (auf Windows normalerweise vorinstalliert).

**Hinweis für Headless-Umgebungen:** Das Skript setzt `matplotlib.use('TkAgg')` als Backend – es benötigt also ein funktionierendes grafisches System. Auf einem reinen Server ohne Display funktioniert die Visualisierung nicht.

## Python-Interpreter

Dieses Skript verwendet dieselbe Python-Fallback-Kette wie das Hauptmenü. Der Interpreter wird von der übergeordneten `Start.bat` bzw. `Menu.py` ermittelt und über `sys.executable` an das Subskript weitergegeben.

## Ausführung

### Über das Menü (empfohlen)

1. `Start.bat` im Root doppelklicken
2. Im Hauptmenü `T` (Textdokumente_vergleichen) eingeben
3. Im Dialog Eingabeverzeichnis (Quelle) und Ausgabeverzeichnis wählen
4. Im Menü das Skript `07_Visualisierung.py` auswählen

### Direkt über die Kommandozeile

    python 07_Visualisierung.py <eingabe_verzeichnis> <ausgabe_verzeichnis>

**Beispiel:**

    python 07_Visualisierung.py "C:\Daten\MeineSammlung" "C:\Daten\Logs"

Tatsächlich verwendet das Skript nur `sys.argv[2]` (das Ausgabeverzeichnis), um die CSV zu suchen. `sys.argv[1]` wird derzeit nicht ausgewertet.

## Ablauf

1. Das Skript lädt die CSV aus dem Ausgabeverzeichnis.
2. Für jeden Eintrag werden Datum, Dateigröße, Änderungsprozent und KI-Ähnlichkeit als numerische Werte aufbereitet (fehlertolerant – fehlende Werte werden durch `None` bzw. `0.0` ersetzt).
3. Das Hauptmenü öffnet sich (tkinter-Fenster).
4. Der Benutzer wählt eine Ansicht; jedes Diagramm öffnet sich in einem eigenen Matplotlib-Fenster (`plt.show()`).
5. Die Menüs bleiben geöffnet, bis der Benutzer sie schließt. Matplotlib-Fenster können parallel geöffnet bleiben.

## Detaillierte Hinweise

### Zeitstrahl-Formatierung

Die Zeitachse passt sich automatisch an die Zeitspanne der Dokumente an:

- **< 1 Stunde Unterschied:** Sekundengenaue Anzeige (`%d.%m. %H:%M:%S`)
- **≥ 1 Stunde Unterschied:** Minuten-genaue Anzeige (`%d.%m.%Y %H:%M`)

Die Dokumentennamen werden in zwei Ebenen über- bzw. unterhalb der Achse platziert (alternierend `y_pos % 2`), um Kollisionen bei vielen Dokumenten zu vermeiden.

### Farbkodierung

- **Gruppen (Gesamtübersicht)**: 20 Pastellfarben aus `plt.cm.Set3`
- **Version vs. Kurztext**: Grün (`#4CAF50`) vs. Orange (`#FF9800`)
- **KI-Ähnlichkeit**: Grün ≥ 70%, Orange ≥ 55%, Rot < 55%
- **Threshold-Linie**: rote gestrichelte Linie bei 55%

### Numerische Aufbereitung

Die eingehenden CSV-Werte werden defensiv geparst:

- `Letzte_Aenderung` → `datetime`-Objekt (oder `None`)
- `Dateigroesse_Bytes` → `int` (oder `0`)
- `Änderung_Zeichen_%` → `float` (Prozentzeichen und `+` werden entfernt)
- `KI_Semantische_Aehnlichkeit` → `float` (Prozentzeichen wird entfernt)

Fehlerhafte Werte führen zu Defaults (0 bzw. `None`), ohne das Skript abzubrechen.

### Fehlerbehandlung

- Fehlende Argumente → Fehlermeldung und Beenden.
- Keine CSV gefunden → Fehlermeldung und Beenden.
- Fehlende Datumswerte werden ignoriert (Diagramme zeigen dann „Keine Datumsinformationen vorhanden").

## Lizenz

Copyright (c) 2025 Gregor Neuboeck <g.neuboeck@gmail.com>

Dieses Skript ist unter der MIT-Lizenz lizenziert.

---
SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
SPDX-License-Identifier: MIT