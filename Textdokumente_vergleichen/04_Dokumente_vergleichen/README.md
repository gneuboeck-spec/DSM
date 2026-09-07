SPDX-License-Identifier: MIT
Copyright (c) 2025 Gregor Neuboeck g.neuboeck@gmail.com



---

# 04_Dokumente_vergleichen/README.md

```markdown
# 📐 04_Dokumente_vergleichen.py

Das Kernstück der Pipeline. Dieses Skript führt hochperformante, mathematische Textvergleiche durch, um verschiedene Versionen desselben Dokuments zu identifizieren und zu Gruppen zusammenzufassen. Dies ermöglicht eine realistische Einschätzung des *einzigartigen* Textumfangs.

## ⚙️ Funktionsweise
1. **Textextraktion**: Liest Texte aus `.docx`, `.pdf`, `.odt`, `.txt` etc. (mit Cache-System für Konvertierungen).
2. **Fingerabdruck-Erstellung**: Erstellt Wortmengen (Jaccard-Index) und kürzt sehr lange Texte (Smart-Modus: Anfang + Ende), um RAM zu sparen.
3. **Längen-Bucketing**: Vergleicht nur Dokumente ähnlicher Länge, um die Rechenzeit von O(n²) drastisch zu reduzieren.
4. **Multiprocessing-Vergleich**: Prüft Paare parallel auf:
   - Wort-Overlap (Jaccard-Ähnlichkeit)
   - Längenverhältnis
   - Exakte Zeichen-Übereinstimmung (RapidFuzz / difflib)
5. **Union-Find-Algorithmus**: Bildet aus den Paar-Übereinstimmungen logische Dokumentengruppen und bestimmt ein "Basisdokument" (z. B. das älteste).

## 🔧 Einstellungs-Dialog
Beim Start öffnet sich ein GUI-Fenster zur Anpassung der Schwellenwerte:
- **Similarity Threshold**: Mindestens erforderliche exakte Übereinstimmung (Standard: 40%).
- **Length Ratio**: Maximale erlaubte Längendifferenz (Standard: 35%).
- **Word Overlap**: Mindestens gemeinsamer Wortschatz (Standard: 25%).
- **Sampling-Modus**: "Standard" (nur Anfang) oder "Smart" (Anfang + Ende bei langen Texten).

## 📊 Ausgabe
- `versionen_analyse.csv`: Rohdaten aller Zuordnungen und prozentualen Änderungen zum Basisdokument.
- `versionen_analyse_farbig.xlsx`: Farblich kodierte Excel-Tabelle zur schnellen visuellen Erfassung der Gruppen.