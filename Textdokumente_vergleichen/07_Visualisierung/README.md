SPDX-License-Identifier: MIT
Copyright (c) 2025 Gregor Neuboeck g.neuboeck@gmail.com



# 📊 06_Visualisierung.py

Macht die komplexen Ergebnisse der vorangegangenen Skripte für Bewerter:innen und Archivar:innen intuitiv begreifbar. Es generiert interaktive Diagramme auf Basis der in Schritt 4 und 5 erstellten Excel-Datei.

## ⚙️ Funktionsweise
Das Skript bietet ein Hauptmenü mit zwei Ansichtsmodi:

### 1. Gesamtübersicht
- **Dokumente pro Gruppe**: Balkendiagramm der Gruppengrößen.
- **Verteilung Dokumententypen**: Kreisdiagramm (Versionen vs. Kurztexte vs. Unklassifiziert).
- **Durchschnittliche Dateigröße**: Vergleich der Gruppen.
- **KI-Ähnlichkeit**: Übersicht aller erkannten Kurztexte und ihrer semantischen Nähe zum Threshold.

### 2. Detailansicht pro Gruppe
Wählt man eine spezifische Gruppe aus, öffnet sich ein Auswahlmenü für vier detaillierte Diagramme:
- **📅 Zeitstrahl**: Chronologische Entwicklung der Dokumente. *Intelligentes Feature*: Erkennt das Skript, dass alle Dateien innerhalb von Sekunden/Minuten kopiert wurden (kein echtes Entstehungsdatum), wechselt es automatisch zu einer chronologischen Sortierung nach Dateiname, um Irreführung zu vermeiden.
- **💾 Dateigrößen-Vergleich**: Horizontales Balkendiagramm aller Dokumente der Gruppe.
- **📈 Text-Änderung gegen Basis**: Zeigt die prozentuale Zunahme/Abnahme von Zeichen und Wörtern im Vergleich zum Basisdokument.
- **🧠 KI-Ähnlichkeit**: Detaillierte Ansicht der Kurztext-Zuordnungen innerhalb dieser spezifischen Gruppe.

## 🔧 Besonderheiten
- **Dynamische Layouts**: Schriftgrößen und Achsenbeschriftungen passen sich automatisch an die Anzahl der Dokumente an, um Überlappungen zu verhindern.
- **Persistente Fenster**: Einzelne Diagramme können gleichzeitig geöffnet bleiben, um sie bequem miteinander zu vergleichen.