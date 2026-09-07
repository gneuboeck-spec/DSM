SPDX-License-Identifier: MIT
Copyright (c) 2025 Gregor Neuboeck g.neuboeck@gmail.com



# 🧠 05_KI_Analyse.py

Ergänzt die syntaktische Analyse um eine semantische Ebene. Dieses Skript nutzt ein vortrainiertes KI-Sprachmodell, um kurze Texte (wie Abstracts, Zusammenfassungen, Rezensionen oder Einleitungen) zu erkennen und den in Schritt 4 gebildeten Hauptdokumentengruppen zuzuordnen.

## ⚙️ Funktionsweise
1. **Modell-Laden**: Lädt `paraphrase-multilingual-mpnet-base-v2` (mehrsprachig, optimiert für semantische Ähnlichkeit) in einen zentralen Cache (`~/.ki_model_cache`).
2. **Basis-Embeddings**: Erstellt Vektorrepräsentationen der Basisdokumente aus Schritt 4.
3. **Intelligente Filterung**: Prüft nur Dokumente, die entweder:
   - Ein Trigger-Wort im Namen haben (z. B. "zusammenfassung", "abstract").
   - Innerhalb einer konfigurierbaren Längengrenze liegen (Standard: 100 bis 5.000 Zeichen).
4. **Kosinus-Ähnlichkeit**: Berechnet die semantische Nähe des Kandidaten zu allen Basis-Embeddings.

## 🔧 Einstellungs-Dialog
- **Semantischer Threshold**: Ab welcher prozentualen Ähnlichkeit eine Zuordnung erfolgt (Standard: 55%).
- **Mindestlänge / Maximallänge**: Fenster für die automatische Erkennung von Kurztexten.

## 📊 Ausgabe
Ergänzt die CSV- und Excel-Dateien aus Schritt 4 um die Spalten:
- `Dokumententyp` (z. B. "Kurztext")
- `KI_Gefundene_Gruppe`
- `KI_Semantische_Aehnlichkeit` (in %)
- `KI_Ergebnis` (Klartext-Beschreibung der Zuordnung)