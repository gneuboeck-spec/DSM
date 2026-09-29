import os
import sys
import csv
import difflib
import subprocess
import zipfile
import re
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import shutil
import math
from multiprocessing import Pool, cpu_count
from functools import partial
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- RAPIDFUZZ IMPORTS (Schnelle C++ Engine) ---
try:
    from rapidfuzz import fuzz
    HAS_RAPIDFUZZ = True
    if __name__ == "__main__" or os.getpid() == os.getppid():
        print("🚀 RapidFuzz gefunden! C++-Beschleunigung für Großtexte aktiviert.")
except ImportError:
    HAS_RAPIDFUZZ = False
    print("⚠️ RapidFuzz nicht gefunden. Verwende Python difflib (Langsamer bei riesigen Texten).")
    print("👉 Tipp: Installiere rapidfuzz mit 'pip install rapidfuzz' für drastisch mehr Speed!")

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False


# ==============================================================================
# === LOGGING-HILFSKLASSE (Tee) =================================================
# ==============================================================================
class Tee:
    """
    Hilfsklasse, die Ausgaben sowohl in die Konsole (stdout) als auch in eine Datei schreibt.
    Wird verwendet, um alle print()-Ausgaben automatisch in ein Logfile zu duplizieren.
    """
    def __init__(self, *files):
        self.files = files
    
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    
    def flush(self):
        for f in self.files:
            f.flush()


# ==============================================================================
# === KONFIGURATION ============================================================
# ==============================================================================
SIMILARITY_THRESHOLD = 0.40
LENGTH_RATIO_THRESHOLD = 0.35
WORD_OVERLAP_THRESHOLD = 0.25

ALLOWED_TEXT_EXTENSIONS = {
    '.txt', '.md', '.csv', '.log', '.tex', '.rst', '.xml', '.html', '.htm',
    '.doc', '.docx', '.odt', '.odf', '.ods', '.rtf', '.pdf',
    '.pages', '.wpd', '.wps', '.sdw', '.abw', '.wri', '.cwk', '.cws', 
    '.wbk', '.uot', '.fodt', '.sxw', '.stw', '.ott', '.dot'
}

PROBLEMATIC_FORMATS = {
    '.doc', '.dot', '.rtf', '.odt', '.ott', '.sxw', '.stw', '.fodt', '.uot',
    '.wpd', '.wps', '.abw', '.sdw', '.wri', '.html', '.htm', 
    '.pages', '.wbk', '.cwk', '.cws', '.docx'
}

BASE_CRITERION = 'oldest'
MIN_TEXT_LENGTH = 200
EXCERPT_THRESHOLD = 0.80
MAX_COMPARE_LENGTH = 2000000  
USE_SMART_SAMPLING = True

LO_EXECUTABLES = [
    'soffice', 'libreoffice',
    r'C:\Program Files\LibreOffice\program\soffice.exe',
    r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
]


# ==============================================================================
# === GUI-FUNKTIONEN ===========================================================
# ==============================================================================
def get_settings_from_user(default_sim, default_len, default_word, default_base, default_min_len, default_exc_thresh, default_max_compare):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    dialog = tk.Toplevel(root)
    dialog.title("Einstellungen: Syntaktischer Vergleich")
    dialog.geometry("550x900")
    dialog.resizable(False, False)
    dialog.grab_set()
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
    y = (dialog.winfo_screenheight() // 2) - (900 // 2)
    dialog.geometry(f"+{x}+{y}")

    base_options = {
        'oldest': 'Ältestes Dokument (Standard, nach Änderungsdatum)',
        'newest': 'Neuestes Dokument (nach Änderungsdatum)',
        'longest': 'Längster Text (nach Zeichenanzahl)',
        'shortest': 'Kürzester Text (nach Zeichenanzahl)'
    }
    
    result = {
        'sim': default_sim, 'length': default_len, 'word': default_word,
        'base': default_base, 'min_len': default_min_len, 'exc_thresh': default_exc_thresh,
        'max_compare': default_max_compare, 'sampling': 'standard'
    }

    def on_apply():
        try:
            val_sim = float(entry_sim.get()) if entry_sim.get() else default_sim
            val_len = float(entry_len.get()) if entry_len.get() else default_len
            val_word = float(entry_word.get()) if entry_word.get() else default_word
            val_min_len = int(entry_min_len.get()) if entry_min_len.get() else default_min_len
            val_exc_thresh = float(entry_exc_thresh.get()) if entry_exc_thresh.get() else default_exc_thresh
            val_max_compare = int(entry_max_compare.get()) if entry_max_compare.get() else default_max_compare
            
            if not (0.0 <= val_sim <= 1.0 and 0.0 <= val_len <= 1.0 and 0.0 <= val_word <= 1.0 and 0.0 <= val_exc_thresh <= 1.0):
                messagebox.showerror("Fehler", "Prozentwerte müssen zwischen 0.0 und 1.0 liegen!", parent=dialog)
                return
            if val_min_len < 0 or val_max_compare < 1000:
                messagebox.showerror("Fehler", "Mindestlänge muss >= 0 und Max. Vergleich >= 1000 sein!", parent=dialog)
                return
            
            result['sim'] = val_sim
            result['length'] = val_len
            result['word'] = val_word
            result['base'] = base_var.get()
            result['min_len'] = val_min_len
            result['exc_thresh'] = val_exc_thresh
            result['max_compare'] = val_max_compare
            result['sampling'] = sampling_var.get()
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Fehler", "Bitte nur gültige Zahlen eingeben!", parent=dialog)

    def on_skip():
        dialog.destroy()

    tk.Label(dialog, text="Schwellenwerte anpassen\n(Felder leer lassen für Standardwerte)", 
             font=("Arial", 11, "bold")).pack(pady=10)
    
    frame_thresh = tk.Frame(dialog)
    frame_thresh.pack(padx=20, fill="x")

    sim_desc = f"Ähnlichkeit / SIMILARITY_THRESHOLD (0.0-1.0)\nStandard: {default_sim}\n(Mindestens {int(default_sim*100)}% exakte Übereinstimmung.)"
    tk.Label(frame_thresh, text=sim_desc, anchor="w", justify="left").grid(row=0, column=0, sticky="w", pady=5)
    entry_sim = tk.Entry(frame_thresh, width=10)
    entry_sim.grid(row=0, column=1, padx=10)
    
    len_desc = f"Längenverhältnis / LENGTH_RATIO_THRESHOLD (0.0-1.0)\nStandard: {default_len}\n(Ein Text darf max. {int((1-default_len)*100)}% kürzer sein.)"
    tk.Label(frame_thresh, text=len_desc, anchor="w", justify="left").grid(row=1, column=0, sticky="w", pady=5)
    entry_len = tk.Entry(frame_thresh, width=10)
    entry_len.grid(row=1, column=1, padx=10)
    
    word_desc = f"Wort-Overlap / WORD_OVERLAP_THRESHOLD (0.0-1.0)\nStandard: {default_word}\n(Mind. {int(default_word*100)}% gleicher Wortschatz.)"
    tk.Label(frame_thresh, text=word_desc, anchor="w", justify="left").grid(row=2, column=0, sticky="w", pady=5)
    entry_word = tk.Entry(frame_thresh, width=10)
    entry_word.grid(row=2, column=1, padx=10)

    min_len_desc = f"Mindestlänge / MIN_TEXT_LENGTH (Zeichen)\nStandard: {default_min_len}\n(Texte kürzer als dieser Wert werden ignoriert.)"
    tk.Label(frame_thresh, text=min_len_desc, anchor="w", justify="left").grid(row=3, column=0, sticky="w", pady=5)
    entry_min_len = tk.Entry(frame_thresh, width=10)
    entry_min_len.grid(row=3, column=1, padx=10)

    exc_desc = f"Auszug-Ähnlichkeit / EXCERPT_THRESHOLD (0.0-1.0)\nStandard: {default_exc_thresh}\n(Wenn Text kürzer ist, aber {int(default_exc_thresh*100)}% ähnelt -> Auszug.)"
    tk.Label(frame_thresh, text=exc_desc, anchor="w", justify="left").grid(row=4, column=0, sticky="w", pady=5)
    entry_exc_thresh = tk.Entry(frame_thresh, width=10)
    entry_exc_thresh.grid(row=4, column=1, padx=10)

    max_compare_desc = f"Max. Vergleichslänge / MAX_COMPARE_LENGTH (Zeichen)\nStandard: {default_max_compare:,}\n(Max. verarbeitete Zeichenanzahl pro Text.)"
    tk.Label(frame_thresh, text=max_compare_desc, anchor="w", justify="left").grid(row=5, column=0, sticky="w", pady=5)
    entry_max_compare = tk.Entry(frame_thresh, width=10)
    entry_max_compare.grid(row=5, column=1, padx=10)

    tk.Label(dialog, text="Text-Sampling-Modus:", 
             font=("Arial", 11, "bold")).pack(pady=(20, 5))
    
    sampling_var = tk.StringVar(value="standard")
    frame_sampling = tk.Frame(dialog)
    frame_sampling.pack(padx=20, fill="x")
    
    tk.Radiobutton(frame_sampling, text="Standard: Nur Anfang des Textes (schneller)", 
                   variable=sampling_var, value="standard", anchor="w", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=2)
    tk.Radiobutton(frame_sampling, text="Smart: Anfang + Ende (besser für lange Dokumente)", 
                   variable=sampling_var, value="smart", anchor="w", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=2)

    tk.Label(dialog, text="Kriterium für das Basisdokument:", 
             font=("Arial", 11, "bold")).pack(pady=20)
    
    base_var = tk.StringVar(value=default_base)
    frame_base = tk.Frame(dialog)
    frame_base.pack(padx=20, fill="x")
    
    for i, (key, text) in enumerate(base_options.items()):
        tk.Radiobutton(frame_base, text=text, variable=base_var, value=key, anchor="w", font=("Arial", 10)).grid(row=i, column=0, sticky="w", pady=2)

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=15)
    
    tk.Button(btn_frame, text="Einstellungen übernehmen", command=on_apply, width=20, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Standardwerte nutzen", command=on_skip, width=20, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📖 Ablauf", command=lambda: show_process_help(dialog), width=10, bg="#FF9800", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="❓ Hilfe", command=lambda: show_main_help(dialog), width=10, bg="#2196F3", fg="white", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)

    dialog.protocol("WM_DELETE_WINDOW", on_skip)
    root.wait_window(dialog)
    return result

def show_process_help(parent_dialog):
    help_root = tk.Toplevel(parent_dialog)
    help_root.title("Ablauf des Skripts - Schritt für Schritt")
    help_root.geometry("900x700")
    help_root.resizable(True, True)
    
    help_root.update_idletasks()
    x = (help_root.winfo_screenwidth() // 2) - 450
    y = (help_root.winfo_screenheight() // 2) - 350
    help_root.geometry(f"+{x}+{y}")
    help_root.protocol("WM_DELETE_WINDOW", help_root.destroy)
    
    text_frame = tk.Frame(help_root)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 10), 
                          yscrollcommand=scrollbar.set, padx=10, pady=10, state="normal", relief="flat")
    text_widget.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)
    
    def insert_text(text):
        text_widget.configure(state="normal")
        text_widget.insert(tk.END, text + "\n")
        text_widget.configure(state="disabled")
    
    def insert_section(title):
        insert_text("\n" + "=" * 70)
        insert_text(title)
        insert_text("=" * 70 + "\n")
    
    def insert_subsection(title):
        insert_text("\n" + title)
    
    def insert_content(text):
        insert_text(text + "\n")
    
    def insert_example(text):
        insert_text("   💡 " + text + "\n")
    
    # ============================================================================
    # === ÜBERSICHT ===============================================================
    # ============================================================================
    insert_text("ABLAUF DES DOKUMENTEN-VERGLEICHS")
    insert_text("Wie das Skript arbeitet - von der Textextraktion bis zur Ergebnis-Tabelle\n")
    
    insert_content("Das Skript durchläuft insgesamt 6 Hauptphasen. Jede Phase baut auf der vorherigen auf.")
    insert_content("Am Ende erhältst du eine farbig formatierte Excel-Tabelle mit allen Ergebnissen.")
    
    # ============================================================================
    # === PHASE 1: TEXT-EXTRAKTION ===============================================
    # ============================================================================
    insert_section("PHASE 1: TEXT-EXTRAKTION")
    insert_content("Das Skript durchsucht den gewählten Ordner rekursiv nach allen unterstützten Dateitypen")
    insert_content("(.docx, .pdf, .txt, .odt, .rtf, .html, .xml,...).")
    insert_content("")
    insert_content("Für jedes gefundene Dokument wird derTextinhalt extrahiert:")
    insert_content("  • .docx / .doc: Über python-docx oder LibreOffice-Konvertierung")
    insert_content("  • .pdf: Über PyMuPDF (sehr schnell) oder pdfplumber (Fallback)")
    insert_content("  • .odt / .ods: Direktes Auslesen aus dem ZIP-Archiv")
    insert_content("  • .rtf: Regex-basierte Bereinigung der Steuerzeichen")
    insert_content("  • .txt / .md / .csv: Direktes Einlesen")
    insert_content("")
    insert_content("Zusätzlich werden Metadaten erfasst: Dateigröße, letztes Änderungsdatum und relativer Pfad.")
    insert_content("")
    insert_subsection("Cache-System:")
    insert_content("Konvertierte Dokumente (z.B. .doc → .txt) werden in einem versteckten Ordner")
    insert_content("'.conversion_cache' zwischengespeichert. Beim nächsten Lauf werden sie nicht")
    insert_content("erneut konvertiert, sondern direkt aus dem Cache geladen → enorme Zeitersparnis.")
    insert_example("Ein 10 MB .doc wird beim ersten Lauf zu .txt konvertiert (dauert ca. 5 Sek.).")
    insert_example("Beim zweiten Lauf wird die fertige .txt in Millisekunden geladen.")
    
    # ============================================================================
    # === PHASE 2: TEXT-FINGERABDRÜCKE ===========================================
    # ============================================================================
    insert_section("PHASE 2: TEXT-FINGERABDRÜCKE BERECHNEN")
    insert_content("Bevor das Skript Dokumente paarweise vergleicht, erstellt es für jedes Dokument")
    insert_content("einen 'Fingerabdruck' - eine kompakte Zusammenfassung aller relevanten Daten.")
    insert_content("")
    insert_subsection("Ein Fingerabdruck enthält drei Dinge:")
    insert_content("  1. Den (eventuell gekürzten) Text")
    insert_content("  2. Die Textlänge in Zeichen")
    insert_content("  3. Die Menge aller einzigartigen Wörter (in Kleinbuchstaben)")
    insert_content("")
    insert_subsection("Konkretes Beispiel:")
    insert_content("Dokument 'roman.txt' hat 5.242.880 Zeichen (ca. 5 MB).")
    insert_content("")
    insert_content("Schritt 1 - Text kürzen:")
    insert_content("  Da 5.242.880 > 2.000.000 (MAX_COMPARE_LENGTH), wird der Text gekürzt.")
    insert_content("  Im Standard-Modus: Nur die ersten 2.000.000 Zeichen werden behalten.")
    insert_content("  Im Smart-Modus: Erste 1.000.000 + letzte 1.000.000 Zeichen.")
    insert_content("")
    insert_content("Schritt 2 - Länge speichern:")
    insert_content("  Der Fingerabdruck speichert: 'len = 2.000.000' (die gekürzte Länge!)")
    insert_content("  Diese Zahl wird später für das Längen-Bucketing und Längenverhältnis benötigt.")
    insert_content("")
    insert_content("Schritt 3 - Wörter extrahieren:")
    insert_content("  Aus dem gekürzten Text werden alle Wörter extrahiert und in eine Menge umgewandelt.")
    insert_content("  Beispiel: 'Der Hund läuft. Der Hund schläft.'")
    insert_content("  → Wörter-Menge: {'der', 'hund', 'läuft', 'schläft'}")
    insert_content("  (Doppelte Wörter wie 'der' und 'hund' werden automatisch entfernt)")
    insert_content("")
    insert_subsection("Welche Funktion haben diese Fingerabdruck-Wörter?")
    insert_content("Sie dienen als SCHNELLER VORAB-FILTER, bevor der teure Textvergleich startet.")
    insert_content("")
    insert_content("Der dahinterstehende Algorithmus heißt JACCARD-INDEX (Jaccard Similarity).")
    insert_content("Er berechnet, wie viel Prozent des Wortschatzes zwei Dokumente gemeinsam haben:")
    insert_content("")
    insert_content("  Formel: Jaccard = gemeinsame Wörter / alle Wörter zusammen")
    insert_content("")
    insert_content("Beispiel 1 - Völlig verschiedene Texte:")
    insert_content("  A: {'der', 'hund', 'läuft', 'schläft', 'bellt'}        (5 Wörter)")
    insert_content("  B: {'die', 'katze', 'sitzt', 'auf', 'dem', 'dach'}     (6 Wörter)")
    insert_content("  Gemeinsame Wörter: 0")
    insert_content("  Alle Wörter zusammen: 11")
    insert_content("  Jaccard = 0 / 11 = 0%")
    insert_content("")
    insert_content("  → 0% bedeutet: Kein einziges Wort kommt in beiden Texten vor.")
    insert_content("  → Es ist offensichtlich, dass dies keine ähnlichen Texte sein können.")
    insert_content("  → Das Skript bricht SOFORT ab. Kein Zeichenvergleich wird gestartet.")
    insert_content("")
    insert_content("Beispiel 2 - Leicht ähnliche Texte:")
    insert_content("  A: {'der', 'hund', 'läuft', 'schläft', 'bellt'}        (5 Wörter)")
    insert_content("  B: {'der', 'hund', 'rennt', 'spielt', 'frisst'}        (5 Wörter)")
    insert_content("  Gemeinsame Wörter: {'der', 'hund'} = 2")
    insert_content("  Alle Wörter zusammen: 8")
    insert_content("  Jaccard = 2 / 8 = 25%")
    insert_content("")
    insert_content("  → 25% >= 25% (WORD_OVERLAP_THRESHOLD)")
    insert_content("  → Das Skript startet jetzt den echten Zeichen-für-Zeichen-Vergleich!")
    insert_content("")
    insert_content("Beispiel 3 - Sehr ähnliche Texte:")
    insert_content("  A: {'der', 'hund', 'läuft', 'schnell', 'im', 'park'}   (6 Wörter)")
    insert_content("  B: {'der', 'hund', 'läuft', 'schnell', 'im', 'garten'} (6 Wörter)")
    insert_content("  Gemeinsame Wörter: 5")
    insert_content("  Alle Wörter zusammen: 7")
    insert_content("  Jaccard = 5 / 7 = 71%")
    insert_content("")
    insert_content("  → 71% >> 25% → Zeichenvergleich wird gestartet (und wird hoch ausfallen).")
    insert_content("")
    insert_subsection("Die 25%-Schwelle ist konfigurierbar!")
    insert_content("Im Einstellungsdialog findest du das Feld 'Wort-Overlap / WORD_OVERLAP_THRESHOLD'.")
    insert_content("Standardwert ist 0.25 (= 25%). Du kannst ihn anpassen:")
    insert_content("  • ERHÖHEN (z.B. 0.35): Strengerer Filter, weniger Dokumentenpaare werden verglichen")
    insert_content("  • SENKEN (z.B. 0.15): Lockerer Filter, mehr Paare werden verglichen (langsamer)")
    insert_content("")
    insert_subsection("Zusammenfassung des Ablaufs pro Dokumentenpaar:")
    insert_content("  1. Jaccard-Index berechnen (Wort-Overlap)")
    insert_content("     → Unter 25% (oder deinem eingestellten Wert)? SOFORT ABBRECHEN.")
    insert_content("     → 25% oder mehr? Weiter zu Schritt 2.")
    insert_content("  2. Längenverhältnis prüfen")
    insert_content("     → Ein Text mehr als 65% kürzer? Nur als 'Auszug' möglich.")
    insert_content("  3. Zeichen-für-Zeichen-Vergleich (RapidFuzz)")
    insert_content("     → Erst jetzt wird der rechenintensive Vergleich durchgeführt.")
    insert_content("")
    insert_content("Dieser dreistufige Filter spart enorm viel Rechenzeit, da die meisten")
    insert_content("Dokumentenpaare bereits in Schritt 1 (Millisekunden) aussortiert werden.")
    
    # ============================================================================
    # === PHASE 3: LÄNGEN-BUCKETING ==============================================
    # ============================================================================
    insert_section("PHASE 3: LÄNGEN-BUCKETING (INTELLIGENTE PAAR-FILTERUNG)")
    insert_content("Dies ist eine der wichtigsten Performance-Optimierungen des Skripts.")
    insert_content("")
    insert_subsection("Das Problem:")
    insert_content("Bei 1000 Dokumenten gäbe es 499.500 mögliche Paare zum Vergleichen.")
    insert_content("Die meisten davon sind aber völlig unterschiedlich (z.B. ein Gedicht vs. ein Roman).")
    insert_content("Solche Vergleiche sind reine Zeitverschwendung.")
    insert_content("")
    insert_subsection("Die Lösung - logarithmische Längen-Kategorien:")
    insert_content("Alle Dokumente werden nach ihrer Textlänge in 'Eimer' (Buckets) sortiert:")
    insert_content("  • Bucket 7:   128-255 Zeichen")
    insert_content("  • Bucket 8:   256-511 Zeichen")
    insert_content("  • Bucket 9:   512-1023 Zeichen")
    insert_content("  • Bucket 10:  1024-2047 Zeichen")
    insert_content("  • ...usw.")
    insert_content("")
    insert_content("Es werden NUR Dokumente innerhalb desselben Buckets ODER benachbarter Buckets")
    insert_content("miteinander verglichen. Ein 100-Zeichen-Text wird nie mit einem 10.000-Zeichen-Text")
    insert_content("verglichen - das spart extrem viel Rechenzeit.")
    insert_example("Bucket 10 enthält 15 Dokumente → 105 Paare zum Vergleichen")
    insert_example("Bucket 11 enthält 8 Dokumente → 28 Paare zum Vergleichen")
    insert_example("Zusätzlich: 15 × 8 = 120 Paare zwischen den Buckets")
    insert_example("Gesamt: 253 Paare statt 4.950 → 95% weniger Vergleiche!")
    
    # ============================================================================
    # === PHASE 4: PARALLELER VERGLEICH ==========================================
    # ============================================================================
    insert_section("PHASE 4: PARALLELER VERGLEICH (MULTIPROCESSING)")
    insert_content("Die gefilterten Dokumentenpaare werden jetzt auf ALLE CPU-Kerne verteilt.")
    insert_content("")
    insert_subsection("Pro Paar werden 3 Prüfungen durchgeführt:")
    insert_content("  1. Wort-Overlap (Jaccard-Index):")
    insert_content("     Wie viele einzigartige Wörter haben beide Texte gemeinsam?")
    insert_content("     → Schneller Filter: Wenn < 25% gemeinsamer Wortschatz → abbrechen")
    insert_content("")
    insert_content("  2. Längenverhältnis:")
    insert_content("     min(Länge1, Länge2) / max(Länge1, Länge2)")
    insert_content("     → Muss >= 0.35 sein (ein Text darf max. 65% kürzer sein)")
    insert_content("")
    insert_content("  3. Exakte Text-Ähnlichkeit (RapidFuzz / difflib):")
    insert_content("     Zeichen-für-Zeichen-Vergleich mit C++-Beschleunigung")
    insert_content("     → Muss >= 0.40 sein (40% exakte Übereinstimmung)")
    insert_content("")
    insert_content("Erst wenn ALLE 3 Kriterien erfüllt sind, gilt das Paar als 'zusammengehörig'.")
    insert_example("Text A: 'Der Hund läuft schnell.'")
    insert_example("Text B: 'Der Hund läuft sehr schnell.'")
    insert_example("→ Wort-Overlap: 4/5 = 80% ✓")
    insert_example("→ Längenverhältnis: 23/28 = 82% ✓")
    insert_example("→ Text-Ähnlichkeit: 85% ✓")
    insert_example("→ ERGEBNIS: Beide gehören zusammen!")
    
    # ============================================================================
    # === PHASE 5: UNION-FIND (GRUPPENBILDUNG) ===================================
    # ============================================================================
    insert_section("PHASE 5: UNION-FIND ALGORITHMUS (GRUPPENBILDUNG)")
    insert_content("Nach dem Vergleich hat das Skript viele 'A gehört mit B zusammen'-Erkenntnisse.")
    insert_content("Jetzt müssen daraus sinnvolle Gruppen gebildet werden.")
    insert_content("")
    insert_subsection("Beispiel:")
    insert_content("  A ≈ B (A ist ähnlich zu B) → Brücke A-B")
    insert_content("  B ≈ C (B ist ähnlich zu C) → Brücke B-C")
    insert_content("  D ≈ E (D ist ähnlich zu E) → Brücke D-E")
    insert_content("")
    insert_content("Ergebnis:")
    insert_content("  GRUPPE 1: {A, B, C}")
    insert_content("  GRUPPE 2: {D, E}")
    insert_content("  GRUPPE 3: {F}")
    insert_content("")
    insert_content("Dieser Algorithmus ist extrem effizient und kann tausende Dokumente in Sekunden")
    insert_content("in Gruppen einteilen. Er garantiert, dass jedes Dokument in genau einer Gruppe ist.")
    insert_content("")
    insert_subsection("Wichtig:")
    insert_content("Nur Gruppen mit mindestens 2 Dokumenten werden in der Ausgabe berücksichtigt.")
    insert_content("Einzelgänger-Dokumente erscheinen zwar in der Tabelle, aber ohne Gruppenzuordnung.")
    
    # ============================================================================
    # === PHASE 6: METRIK-BERECHNUNG =============================================
    # ============================================================================
    insert_section("PHASE 6: METRIK-BERECHNUNG INNERHALB DER GRUPPEN")
    insert_content("Für jede Gruppe wird jetzt ein 'Basisdokument' bestimmt. Das ist das Referenzdokument,")
    insert_content("gegen das alle anderen Dokumente der Gruppe verglichen werden.")
    insert_content("")
    insert_subsection("Auswahl des Basisdokuments (BASE_CRITERION):")
    insert_content("  • oldest: Das älteste Dokument (Standard)")
    insert_content("  • newest: Das neueste Dokument")
    insert_content("  • longest: Der längste Text")
    insert_content("  • shortest: Der kürzeste Text")
    insert_content("")
    insert_subsection("Berechnung der Metriken:")
    insert_content("Für jedes Dokument in der Gruppe wird berechnet:")
    insert_content("  • Übereinstimmung Zeichen: Absolute Anzahl gleicher Zeichen mit dem Basisdokument")
    insert_content("  • Übereinstimmung Wörter: Absolute Anzahl gleicher Wörter mit dem Basisdokument")
    insert_content("  • Änderung Zeichen %: Wie viel % länger/kürzer ist das Dokument vs. Basis?")
    insert_content("  • Änderung Wörter %: Wie viel % mehr/weniger Wörter vs. Basis?")
    insert_example("Basisdokument: 10.000 Zeichen, 1.500 Wörter")
    insert_example("Version 2:     11.000 Zeichen, 1.600 Wörter")
    insert_example("→ Änderung Zeichen: +10%")
    insert_example("→ Änderung Wörter:  +6,7%")
    insert_content("")
    insert_content("Die Ähnlichkeitswerte zwischen Basis und jedem Dokument werden aus dem Cache")
    insert_content("aus Phase 4 wiederverwendet - keine Neuberechnung nötig!")
    
    # ============================================================================
    # === PHASE 7: EXPORT ========================================================
    # ============================================================================
    insert_section("PHASE 7: EXPORT IN CSV UND EXCEL")
    insert_content("Am Ende werden alle Ergebnisse in zwei Formate exportiert:")
    insert_content("")
    insert_subsection("1. CSV-Datei (versionen_analyse.csv):")
    insert_content("   • Einfache, universelle Tabellenstruktur")
    insert_content("   • Kann von jedem Programm geöffnet werden")
    insert_content("   • UTF-8 mit BOM (für korrekte Darstellung von Umlauten in Excel)")
    insert_content("")
    insert_subsection("2. Excel-Datei (versionen_analyse_farbig.xlsx):")
    insert_content("   • Farbige Hintergrundfarben pro Gruppe")
    insert_content("   • Kurztexte gelb hervorgehoben")
    insert_content("   • Nicht gruppierte Dokumente grau")
    insert_content("   • Auto-Filter aktivierbar")
    insert_content("   • Spaltenbreiten automatisch angepasst")
    insert_content("   • Erste Zeile eingefroren (beim Scrollen immer sichtbar)")
    insert_content("")
    insert_content("Die Dateien werden im Ausgabe-Ordner gespeichert, den du zu Beginn gewählt hast.")
    
    # ============================================================================
    # === ZUSAMMENFASSUNG ========================================================
    # ============================================================================
    insert_section("ZUSAMMENFASSUNG: WIE DIE PHASEN ZUSAMMENHÄNGEN")
    insert_content("")
    insert_content("  ┌─────────────────────────────────────────────────────────┐")
    insert_content("  │ 1. TEXT-EXTRAKTION                                      │")
    insert_content("  │    Alle Dokumente → reiner Text + Metadaten            │")
    insert_content("  └──────────────────┬──────────────────────────────────────┘")
    insert_content("                     ↓")
    insert_content("  ┌─────────────────────────────────────────────────────────┐")
    insert_content("  │ 2. FINGERABDRÜCKE                                       │")
    insert_content("  │    Text kürzen + Wort-Mengen bilden                    │")
    insert_content("  └──────────────────┬──────────────────────────────────────┘")
    insert_content("                     ↓")
    insert_content("  ┌─────────────────────────────────────────────────────────┐")
    insert_content("  │ 3. LÄNGEN-BUCKETING                                     │")
    insert_content("  │    Nur ähnliche Längen → weniger Paare                 │")
    insert_content("  └──────────────────┬──────────────────────────────────────┘")
    insert_content("                     ↓")
    insert_content("  ┌─────────────────────────────────────────────────────────┐")
    insert_content("  │ 4. PARALLELER VERGLEICH                                 │")
    insert_content("  │    Alle CPU-Kerne arbeiten gleichzeitig                │")
    insert_content("  └──────────────────┬──────────────────────────────────────┘")
    insert_content("                     ↓")
    insert_content("  ┌─────────────────────────────────────────────────────────┐")
    insert_content("  │ 5. UNION-FIND                                           │")
    insert_content("  │    Aus 'A≈B' und 'B≈C' wird Gruppe {A,B,C}           │")
    insert_content("  └──────────────────┬──────────────────────────────────────┘")
    insert_content("                     ↓")
    insert_content("  ┌─────────────────────────────────────────────────────────┐")
    insert_content("  │ 6. METRIKEN                                             │")
    insert_content("  │    Basisdokument wählen + Änderungen berechnen         │")
    insert_content("  └──────────────────┬──────────────────────────────────────┘")
    insert_content("                     ↓")
    insert_content("  ┌─────────────────────────────────────────────────────────┐")
    insert_content("  │ 7. EXPORT                                               │")
    insert_content("  │    CSV + farbige Excel-Datei                           │")
    insert_content("  └─────────────────────────────────────────────────────────┘")
    insert_content("")
    insert_content("Die gesamte Verarbeitung ist darauf optimiert, auch bei tausenden Dokumenten")
    insert_content("in akzeptabler Zeit durchzulaufen. Die Kombination aus Bucketing, Multiprocessing")
    insert_content("und dem Union-Find-Algorithmus macht das Skript besonders effizient.")
    
    btn_frame = tk.Frame(help_root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Fenster schließen", command=help_root.destroy, 
              width=20, font=("Arial", 11, "bold")).pack()

def show_main_help(parent_dialog):
    help_root = tk.Toplevel(parent_dialog)
    help_root.title("Hilfe: Parameter-Erklärungen")
    help_root.geometry("850x650")
    help_root.resizable(True, True)
    
    help_root.update_idletasks()
    x = (help_root.winfo_screenwidth() // 2) - 425
    y = (help_root.winfo_screenheight() // 2) - 325
    help_root.geometry(f"+{x}+{y}")
    help_root.protocol("WM_DELETE_WINDOW", help_root.destroy)
    
    text_frame = tk.Frame(help_root)
    text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    text_widget = tk.Text(text_frame, wrap="word", font=("Arial", 10), 
                          yscrollcommand=scrollbar.set, padx=10, pady=10, state="normal", relief="flat")
    text_widget.pack(fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_widget.yview)
    
    def insert_text(text):
        text_widget.configure(state="normal")
        text_widget.insert(tk.END, text + "\n")
        text_widget.configure(state="disabled")
    
    def insert_section(title):
        insert_text("\n" + "=" * 70)
        insert_text(title)
        insert_text("=" * 70 + "\n")
    
    def insert_subsection(title):
        insert_text("\n" + title)
    
    def insert_content(text):
        insert_text(text + "\n")
    
    insert_text("PARAMETER-ERKLÄRUNGEN / PARAMETER EXPLANATIONS")
    insert_text("Detaillierte Informationen zu allen Schwellenwerten\n")
    
    # 1. SIMILARITY_THRESHOLD (wie im Dialog: Feld 1)
    insert_section("SIMILARITY_THRESHOLD = 0.40 (40%) - Ähnlichkeit")
    insert_content("Mindestens 40% des Textes müssen exakt (Zeichen für Zeichen in der richtigen Reihenfolge) übereinstimmen.")
    insert_subsection("Technische Berechnung:")
    insert_content("Verwendet RapidFuzz (C++ beschleunigt) oder difflib SequenceMatcher.")
    insert_subsection("Wann anpassen:")
    insert_content("ERHÖHEN (z.B. 0.60): Wenn zu viele unterschiedliche Texte fälschlich gruppiert werden.")
    insert_content("SENKEN (z.B. 0.25): Wenn offensichtlich zusammengehörige Versionen nicht erkannt werden.")
    
    # 2. LENGTH_RATIO_THRESHOLD (wie im Dialog: Feld 2)
    insert_section("LENGTH_RATIO_THRESHOLD = 0.35 (35%) - Längenverhältnis")
    insert_content("Ein Text darf maximal 65% kürzer sein als der andere.")
    insert_subsection("Technische Berechnung:")
    insert_content("min(len_1, len_2) / max(len_1, len_2).")
    insert_subsection("Wann anpassen:")
    insert_content("ERHÖHEN (z.B. 0.50): Wenn nur wirklich gleich lange Versionen gefunden werden sollen.")
    insert_content("SENKEN (z.B. 0.20): Wenn auch stark gekürzte Fassungen erkannt werden sollen.")
    
    # 3. WORD_OVERLAP_THRESHOLD (wie im Dialog: Feld 3)
    insert_section("WORD_OVERLAP_THRESHOLD = 0.25 (25%) - Wort-Overlap")
    insert_content("Die Texte müssen mindestens 25% ihres einzigartigen Wortschatzes teilen.")
    insert_subsection("Technische Berechnung:")
    insert_content("Jaccard-Index = |Schnittmenge| / |Vereinigung| der Wortmengen.")
    insert_subsection("Wann anpassen:")
    insert_content("ERHÖHEN: Wenn Texte mit ähnlichen Wörtern aber unterschiedlichem Inhalt gruppiert werden.")
    insert_content("SENKEN: Wenn synonymreiche Texte gefunden werden sollen.")
    
    # 4. MIN_TEXT_LENGTH (wie im Dialog: Feld 4)
    insert_section("MIN_TEXT_LENGTH = 200 (Zeichen) - Mindestlänge")
    insert_content("Texte unter 200 Zeichen werden komplett ignoriert.")
    
    # 5. EXCERPT_THRESHOLD (wie im Dialog: Feld 5)
    insert_section("EXCERPT_THRESHOLD = 0.80 (80%) - Auszug-Ähnlichkeit")
    insert_content("Wenn ein Text viel kürzer ist, wird er nur als 'Auszug' gruppiert, wenn 80% der Zeichen exakt übereinstimmen.")
    
    # 6. MAX_COMPARE_LENGTH (wie im Dialog: Feld 6)
    insert_section("MAX_COMPARE_LENGTH = 2.000.000 (Zeichen) - Max. Vergleichslänge")
    insert_content("Die maximale Anzahl an Zeichen, die pro Text für den Vergleich verwendet wird.")
    insert_subsection("Technische Berechnung:")
    insert_content("Texte, die länger als dieser Wert sind, werden vor dem Vergleich gekürzt.")
    insert_subsection("Wann anpassen:")
    insert_content("ERNIEDRIGEN (z.B. 500.000): Deutlich schneller, aber ungenauer bei sehr langen Dokumenten.")
    insert_content("ERHÖHEN (z.B. 5.000.000): Genaue Ergebnisse auch bei sehr langen Texten, aber langsamer und höherer RAM-Verbrauch.")
    insert_subsection("Hinweis:")
    insert_content("Der Standardwert von 2.000.000 Zeichen deckt die meisten Anwendungsfälle optimal ab.")
    
    # 7. TEXT-SAMPLING-MODUS (wie im Dialog: Radio-Buttons darunter)
    insert_section("TEXT-SAMPLING-MODUS - Art der Textkürzung")
    insert_content("Bestimmt, wie ein Text gekürzt wird, wenn er länger als MAX_COMPARE_LENGTH ist.")
    insert_subsection("Standard-Modus (Nur Anfang):")
    insert_content("Es werden nur die ERSTEN MAX_COMPARE_LENGTH Zeichen verwendet.")
    insert_content("Vorteil: Sehr schnell, da nur ein zusammenhängender Textblock verarbeitet wird.")
    insert_content("Nachteil: Änderungen am Ende des Dokuments werden nicht erkannt.")
    insert_subsection("Smart-Modus (Anfang + Ende):")
    insert_content("Es werden die ERSTEN 50% und die LETZTEN 50% von MAX_COMPARE_LENGTH verwendet.")
    insert_content("Beispiel bei 2.000.000: erste 1.000.000 + letzte 1.000.000 Zeichen.")
    insert_content("Vorteil: Erkennt auch Änderungen am Ende von Dokumenten (z.B. Nachträge, neue Kapitel).")
    insert_content("Nachteil: Die Mitte des Textes wird nicht berücksichtigt.")
    insert_subsection("Wann welchen Modus wählen:")
    insert_content("STANDARD: Wenn Dokumente meist komplett neu geschrieben oder nur am Anfang geändert werden.")
    insert_content("SMART: Wenn Dokumente oft am Ende erweitert werden (z.B. angehängte Abschnitte, Bibliographien).")
    
    # 8. BASE_CRITERION (wie im Dialog: Radio-Buttons ganz unten)
    insert_section("BASE_CRITERION = 'oldest' - Basisdokument-Kriterium")
    insert_content("Bestimmt das Referenzdokument für die Änderungsprozente.")
    insert_content("• oldest: Ältestes Dokument (Standard)\n• newest: Neuestes Dokument\n• longest: Längster Text\n• shortest: Kürzester Text")
    
    btn_frame = tk.Frame(help_root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Fenster schließen", command=help_root.destroy, 
              width=20, font=("Arial", 11, "bold")).pack()


# ==============================================================================
# === TEXT-EXTRAKTION ==========================================================
# ==============================================================================
def convert_with_libreoffice(file_path: Path, cache_dir: Path) -> Path:
    import tempfile
    import uuid
    
    cache_dir.mkdir(exist_ok=True)
    target_file = cache_dir / (file_path.stem + "_" + str(file_path.stat().st_mtime)[:10] + ".txt")
    
    if target_file.exists() and target_file.stat().st_size > 0:
        return target_file
        
    print(f"  🔄 Konvertiere {file_path.name} mit LibreOffice zu TXT...")
    
    max_retries = 3
    
    for attempt in range(max_retries):
        unique_profile_name = f"lo_profile_{uuid.uuid4().hex[:8]}"
        temp_profile_dir = Path(tempfile.gettempdir()) / unique_profile_name
        
        try:
            temp_profile_dir.mkdir(parents=True, exist_ok=True)
            profile_url = f"file:///{temp_profile_dir.as_posix()}"
            
            success = False
            for lo_cmd in LO_EXECUTABLES:
                try:
                    if file_path.suffix.lower() == '.sdw':
                        cmd = [
                            lo_cmd, '--headless', '--norestore',
                            f'-env:UserInstallation={profile_url}',
                            '--infilter=StarWriter 5.0',
                            '--convert-to', 'txt:Text',
                            '--outdir', str(cache_dir),
                            str(file_path)
                        ]
                    else:
                        cmd = [
                            lo_cmd, '--headless', '--norestore',
                            f'-env:UserInstallation={profile_url}',
                            '--convert-to', 'txt:Text',
                            '--outdir', str(cache_dir),
                            str(file_path)
                        ]
                    
                    result = subprocess.run(
                        cmd, 
                        check=True, 
                        capture_output=True, 
                        timeout=120
                    )
                    
                    expected_file = cache_dir / (file_path.stem + ".txt")
                    if expected_file.exists() and expected_file.stat().st_size > 0:
                        expected_file.rename(target_file)
                        success = True
                        break
                except subprocess.TimeoutExpired:
                    print(f"     ⏱️ Timeout bei Versuch {attempt + 1}")
                    continue
                except Exception:
                    continue
            
            if success:
                try:
                    shutil.rmtree(temp_profile_dir, ignore_errors=True)
                except:
                    pass
                return target_file
                
        except Exception as e:
            print(f"     ⚠️ Fehler bei Versuch {attempt + 1}: {e}")
        
        try:
            shutil.rmtree(temp_profile_dir, ignore_errors=True)
        except:
            pass
        
        if attempt < max_retries - 1:
            time.sleep(2)
    
    if file_path.suffix.lower() not in ['.doc', '.docx']:
        print(f"  ⚠️ Standard-Konvertierung fehlgeschlagen, versuche .doc Auto-Detection...")
        temp_doc = cache_dir / (file_path.stem + "_temp.doc")
        try:
            shutil.copy2(file_path, temp_doc)
            result = convert_with_libreoffice(temp_doc, cache_dir)
            if temp_doc.exists():
                temp_doc.unlink()
            if result:
                return result
        except Exception:
            if temp_doc.exists():
                temp_doc.unlink()

    print(f"  ❌ Konvertierung von {file_path.name} mit LibreOffice fehlgeschlagen (nach {max_retries} Versuchen).")
    return None


def convert_doc_to_txt(file_path: Path, cache_dir: Path) -> str:
    cache_dir.mkdir(exist_ok=True)
    target_file = cache_dir / (file_path.stem + ".txt")
    if target_file.exists():
        return target_file.read_text(encoding='utf-8', errors='ignore')
    
    for lo_cmd in LO_EXECUTABLES:
        try:
            cmd = [lo_cmd, '--headless', '--convert-to', 'txt:Text', '--outdir', str(cache_dir), str(file_path)]
            subprocess.run(cmd, check=True, capture_output=True, timeout=60)
            if target_file.exists():
                return target_file.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
    return ""


def extract_pdf_text(file_path: Path) -> str:
    full_text = ""
    try:
        import pymupdf
        doc = pymupdf.open(file_path)
        text_parts = [page.get_text() for page in doc]
        full_text = "\n".join(text_parts)
        doc.close()
        if full_text.strip():
            return full_text
    except Exception as e:
        print(f"  ⚠️ pymupdf Fehler bei {file_path.name}: {e}")
    
    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            text_parts = [page.extract_text() for page in pdf.pages if page.extract_text()]
        full_text = "\n".join(text_parts)
        if full_text.strip():
            return full_text
    except Exception as e:
        print(f"  ⚠️ pdfplumber Fehler bei {file_path.name}: {e}")
    
    return full_text


def extract_text(file_path: Path, cache_dir: Path) -> str:
    ext = file_path.suffix.lower()
    full_text = ""
    
    try:
        if ext == '.xml':
            try:
                import xml.etree.ElementTree as ET
                tree = ET.parse(file_path)
                root = tree.getroot()
                full_text = ' '.join(root.itertext())
                if not full_text.strip():
                    full_text = file_path.read_text(encoding='utf-8', errors='ignore')
                    full_text = re.sub(r'<[^>]+>', ' ', full_text)
            except Exception as e:
                print(f"  ⚠️ XML-Fehler bei {file_path.name}: {e}")
                full_text = file_path.read_text(encoding='utf-8', errors='ignore')
                full_text = re.sub(r'<[^>]+>', ' ', full_text)
        
        elif ext in ['.txt', '.md', '.csv', '.log', '.tex', '.rst']:
            full_text = file_path.read_text(encoding='utf-8', errors='ignore')
            
        elif ext == '.pdf':
            full_text = extract_pdf_text(file_path)
            if not full_text.strip():
                print(f"  ⚠️ Kein Text in PDF extrahiert: {file_path.name}")
                
        elif ext == '.docx':
            import docx
            doc = docx.Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            
        elif ext == '.doc':
            try:
                import docx
                doc = docx.Document(file_path)
                full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
                if len(full_text.strip()) > 100:
                    return full_text
            except Exception:
                pass
            print(f"  📄 Konvertiere altes .doc Format: {file_path.name}")
            converted_path = convert_with_libreoffice(file_path, cache_dir)
            if converted_path:
                return extract_text(converted_path, cache_dir)
                
        elif ext in ['.odt', '.odf', '.ods']:
            try:
                with zipfile.ZipFile(file_path, 'r') as z:
                    if 'content.xml' in z.namelist():
                        xml_content = z.read('content.xml').decode('utf-8', errors='ignore')
                        full_text = re.sub(r'<[^>]+>', ' ', xml_content)
                        if len(full_text.strip()) > 100:
                            return full_text
            except Exception:
                pass
            print(f"  📄 Konvertiere OpenDocument Format: {file_path.name}")
            converted_path = convert_with_libreoffice(file_path, cache_dir)
            if converted_path:
                return extract_text(converted_path, cache_dir)
                
        elif ext == '.rtf':
            raw = file_path.read_text(encoding='utf-8', errors='ignore')
            full_text = re.sub(r'\\[a-z]+\d*\s?', '', raw)
            full_text = re.sub(r'[{}]', '', full_text)
            full_text = re.sub(r'\s+', ' ', full_text).strip()
            
        elif ext in PROBLEMATIC_FORMATS:
            print(f"  📄 Konvertiere {ext} Format mit LibreOffice: {file_path.name}")
            converted_path = convert_with_libreoffice(file_path, cache_dir)
            if converted_path:
                return extract_text(converted_path, cache_dir)
                
    except Exception as e:
        print(f"  ⚠️ Fehler beim Lesen von {file_path.name}: {e}")
        
    return full_text


def extract_text_simple(file_path: Path, cache_dir: Path = None) -> str:
    ext = file_path.suffix.lower()
    try:
        if ext == '.txt':
            return file_path.read_text(encoding='utf-8', errors='ignore')
        elif ext == '.docx':
            import docx
            return "\n".join([p.text for p in docx.Document(file_path).paragraphs])
        elif ext == '.doc':
            if cache_dir: return convert_doc_to_txt(file_path, cache_dir)
            return ""
        elif ext == '.pdf':
            return extract_pdf_text(file_path)
        elif ext in ['.odt', '.ods', '.odf']:
            try:
                with zipfile.ZipFile(file_path, 'r') as z:
                    if 'content.xml' in z.namelist():
                        xml = z.read('content.xml').decode('utf-8', errors='ignore')
                        text = re.sub(r'<[^>]+>', ' ', xml)
                        return text.strip()
            except Exception:
                return ""
    except Exception as e:
        print(f"      ⚠️ Lesefehler bei {file_path.name}: {e}")
        return ""
    return ""


# ==============================================================================
# === SCHRITT 1: SYNTAKTISCHE ANALYSE ==========================================
# ==============================================================================
def format_time(seconds):
    seconds = max(0, int(seconds))
    hrs = seconds // 3600
    mins = (seconds % 3600) // 60
    secs = seconds % 60
    if hrs > 0:
        return f"{hrs}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


def get_smart_text_sample(text, max_chars):
    text = text.strip()
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n\n[...MITTE AUSGELASSEN...]\n\n" + text[-half:]


def compare_pair(pair, preprocessed, similarity_threshold, max_compare_length,
                 min_text_length, word_overlap_threshold, length_ratio_threshold,
                 excerpt_threshold):
    i, j = pair
    prep_i = preprocessed[i]
    prep_j = preprocessed[j]
    len_i = prep_i['len']
    len_j = prep_j['len']

    if len_i < min_text_length or len_j < min_text_length:
        return None

    length_ratio = min(len_i, len_j) / max(len_i, len_j)

    words_i = prep_i['words_set']
    words_j = prep_j['words_set']
    intersection = len(words_i.intersection(words_j))
    if intersection == 0:
        return None

    union_len = len(words_i.union(words_j))
    word_overlap = intersection / union_len if union_len > 0 else 0

    if word_overlap < word_overlap_threshold:
        return None

    text_i = prep_i['text']
    text_j = prep_j['text']
    
    if HAS_RAPIDFUZZ:
        sim = fuzz.ratio(text_i, text_j) / 100.0
    else:
        sim = difflib.SequenceMatcher(None, text_i, text_j).ratio()

    if length_ratio >= length_ratio_threshold:
        if sim >= similarity_threshold:
            return (i, j, sim)
    else:
        if sim >= excerpt_threshold:
            return (i, j, sim)

    return None


SIMILARITY_CACHE = {}

def find_version_groups(files_data, similarity_threshold, max_compare_length):
    global SIMILARITY_CACHE
    SIMILARITY_CACHE = {}

    print(f"\n🔍 Suche nach Text-Versionen (Threshold: {similarity_threshold})...")
    print(f"   Max. Vergleichslänge: {max_compare_length:,} Zeichen pro Text")

    n = len(files_data)
    parent = list(range(n))

    def find(i):
        if parent[i] == i:
            return i
        parent[i] = find(parent[i])
        return parent[i]

    def union(i, j):
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j

    print("  ⚡ Berechne Text-Fingerabdrücke im Voraus...")
    preprocessed = []
    word_regex = re.compile(r'\w+')

    for i, data in enumerate(files_data):
        if USE_SMART_SAMPLING:
            text_sub = get_smart_text_sample(data['text'], max_compare_length)
        else:
            text_sub = data['text'][:max_compare_length]

        words_list = word_regex.findall(text_sub.lower())
        preprocessed.append({
            'text': text_sub,
            'len': len(text_sub),
            'words_set': set(words_list)
        })

    buckets = defaultdict(list)
    for i, prep in enumerate(preprocessed):
        length = prep['len']
        if length < MIN_TEXT_LENGTH:
            continue
        bucket_key = int(math.log2(max(length, 1)))
        buckets[bucket_key].append(i)

    pairs_to_compare = []
    bucket_keys = sorted(buckets.keys())
    for idx, key in enumerate(bucket_keys):
        indices = buckets[key]
        for p in range(len(indices)):
            for q in range(p + 1, len(indices)):
                pairs_to_compare.append((indices[p], indices[q]))
        if key + 1 in buckets:
            for i in indices:
                for j in buckets[key + 1]:
                    pairs_to_compare.append((i, j))

    total_pairs = len(pairs_to_compare)
    print(f"   ⚡ Vergleiche {total_pairs} Paare (gefiltert durch Längen-Bucketing) mit {cpu_count()} Kernen...")

    start_time = time.time()

    func = partial(
        compare_pair,
        preprocessed=preprocessed,
        similarity_threshold=similarity_threshold,
        max_compare_length=max_compare_length,
        min_text_length=MIN_TEXT_LENGTH,
        word_overlap_threshold=WORD_OVERLAP_THRESHOLD,
        length_ratio_threshold=LENGTH_RATIO_THRESHOLD,
        excerpt_threshold=EXCERPT_THRESHOLD,
    )

    try:
        from tqdm import tqdm
        with Pool(processes=cpu_count()) as pool:
            results = []
            for result in tqdm(pool.imap_unordered(func, pairs_to_compare), total=total_pairs, desc="  Vergleiche"):
                if result is not None:
                    results.append(result)
    except ImportError:
        print("   (Installiere 'tqdm' für Fortschrittsbalken: pip install tqdm)")
        with Pool(processes=cpu_count()) as pool:
            results = [r for r in pool.imap_unordered(func, pairs_to_compare) if r is not None]

    for i, j, sim in results:
        union(i, j)
        key = (min(i, j), max(i, j))
        SIMILARITY_CACHE[key] = sim

    groups = defaultdict(list)
    for i in range(n):
        groups[find(i)].append(i)

    result = {k: v for k, v in groups.items() if len(v) > 1}

    elapsed = time.time() - start_time
    elapsed_str = format_time(elapsed)
    print(f"\n✅ {len(result)} Versions-Gruppen gefunden in {elapsed_str}.\n")

    return result


def calculate_metrics(files_data, groups, base_criterion, max_compare_length):
    global SIMILARITY_CACHE
    print("📊 Berechne Versions-Metriken innerhalb der Gruppen...")
    version_results = {}

    for group_id, (root_idx, indices) in enumerate(groups.items(), 1):
        if base_criterion == 'newest':
            indices_sorted = sorted(indices, key=lambda x: files_data[x]['mtime'], reverse=True)
        elif base_criterion == 'longest':
            indices_sorted = sorted(indices, key=lambda x: len(files_data[x]['text']), reverse=True)
        elif base_criterion == 'shortest':
            indices_sorted = sorted(indices, key=lambda x: len(files_data[x]['text']))
        else:
            indices_sorted = sorted(indices, key=lambda x: files_data[x]['mtime'])

        base_idx = indices_sorted[0]
        base_data = files_data[base_idx]
        base_text = base_data['text'][:max_compare_length]
        base_words = base_text.split()
        base_words_set = set(base_words)

        for idx in indices_sorted:
            data = files_data[idx]
            curr_text = data['text'][:max_compare_length]
            curr_words = curr_text.split()
            curr_words_set = set(curr_words)

            key = (min(base_idx, idx), max(base_idx, idx))
            if key in SIMILARITY_CACHE:
                sim_ratio = SIMILARITY_CACHE[key]
                matching_chars = int(sim_ratio * max(len(base_text), len(curr_text)))
            else:
                if HAS_RAPIDFUZZ:
                    sim_ratio = fuzz.ratio(base_text, curr_text) / 100.0
                else:
                    sim_ratio = difflib.SequenceMatcher(None, base_text, curr_text).ratio()
                matching_chars = int(sim_ratio * max(len(base_text), len(curr_text)))

            matching_words = len(base_words_set.intersection(curr_words_set))

            change_chars = ((len(curr_text) - len(base_text)) / max(len(base_text), 1)) * 100
            change_words = ((len(curr_words) - len(base_words)) / max(len(base_words), 1)) * 100

            version_results[idx] = {
                'gruppe': f"GRUPPE_{group_id:03d}",
                'basis': base_data['rel_path'] if idx != base_idx else "(Basis)",
                'match_chars': matching_chars,
                'match_words': matching_words,
                'change_chars_pct': f"{change_chars:+.1f}%",
                'change_words_pct': f"{change_words:+.1f}%"
            }
    return version_results


# ==============================================================================
# === CSV & EXCEL EXPORT =======================================================
# ==============================================================================
def save_csv(rows, output_file):
    fieldnames = [
        "Relativer_Pfad", "Dateiname", "Dateityp",
        "Versions_Gruppe", "Basisdokument", 
        "Übereinstimmung_Zeichen", "Übereinstimmung_Wörter", 
        "Änderung_Zeichen_%", "Änderung_Wörter_%", 
        "Letzte_Aenderung", "Dateigroesse_Bytes",
        "Dokumententyp", "KI_Gefundene_Gruppe", "KI_Semantische_Aehnlichkeit", "KI_Ergebnis"
    ]
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n💾 CSV gespeichert: {output_file}")


def save_as_excel(rows, output_file):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        print("⚠️ openpyxl nicht installiert. Bitte: pip install openpyxl")
        return
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Dokumenten-Analyse"
    
    pastel_colors = [
        'BDD7EE', 'C6EFCE', 'FFF2CC', 'FCE4D6', 'E4DFEC',
        'F4B6C2', 'B4E7CE', 'D9E2F3', 'FFF9C4', 'D7CCC8',
        'FFE5B4', 'E0BBE4', '957DAD', 'D291BC', 'FEC8D8',
        'FFDFD3', 'E2F0CB', 'B5EAD7', 'C7CEEA', 'FFDAC1'
    ]
    
    fieldnames = [
        "Relativer_Pfad", "Dateiname", "Dateityp",
        "Versions_Gruppe", "Basisdokument", 
        "Übereinstimmung_Zeichen", "Übereinstimmung_Wörter", 
        "Änderung_Zeichen_%", "Änderung_Wörter_%", 
        "Letzte_Aenderung", "Dateigroesse_Bytes",
        "Dokumententyp", "KI_Gefundene_Gruppe", "KI_Semantische_Aehnlichkeit", "KI_Ergebnis"
    ]
    
    header_font = Font(name='Arial', bold=True, color='FFFFFF', size=11)
    header_fill = PatternFill(start_color='2F5496', end_color='2F5496', fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    for col_num, header in enumerate(fieldnames, 1):
        cell = ws.cell(row=1, column=col_num, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment
        cell.border = thin_border
    
    cell_font = Font(name='Arial', size=10)
    cell_alignment = Alignment(vertical='center', wrap_text=True)
    
    for row_num, row_data in enumerate(rows, 2):
        gruppe = row_data.get('Versions_Gruppe', '').strip()
        ki_gruppe = row_data.get('KI_Gefundene_Gruppe', '').strip()
        dokumententyp = row_data.get('Dokumententyp', '').strip()
        
        if dokumententyp == 'Kurztext':
            bg_color = 'FFEB99'
        elif not gruppe and not ki_gruppe:
            bg_color = 'F2F2F2'
        else:
            active_group = ki_gruppe if ki_gruppe else gruppe
            match = re.search(r'\d+', active_group)
            if match:
                group_num = int(match.group())
                color_index = (group_num - 1) % len(pastel_colors)
                bg_color = pastel_colors[color_index]
            else:
                bg_color = 'D9E2F3'
        
        row_fill = PatternFill(start_color=bg_color, end_color=bg_color, fill_type='solid')
        
        for col_num, field in enumerate(fieldnames, 1):
            cell = ws.cell(row=row_num, column=col_num, value=row_data.get(field, ''))
            cell.font = cell_font
            cell.fill = row_fill
            cell.alignment = cell_alignment
            cell.border = thin_border
            
            if field in ['Änderung_Zeichen_%', 'Änderung_Wörter_%', 'KI_Semantische_Aehnlichkeit']:
                cell.alignment = Alignment(horizontal='right', vertical='center')
            elif field == 'Dateigroesse_Bytes':
                cell.alignment = Alignment(horizontal='right', vertical='center')
                cell.number_format = '#,##0'
    
    for col_num, header in enumerate(fieldnames, 1):
        max_length = len(str(header))
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=col_num, max_col=col_num):
            for cell in row:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
        adjusted_width = min(max(max_length + 2, 12), 50)
        ws.column_dimensions[ws.cell(row=1, column=col_num).column_letter].width = adjusted_width
    
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    
    wb.save(str(output_file))
    print(f"📊 Excel-Datei mit Farben gespeichert: {output_file}")


# ==============================================================================
# === MAIN =====================================================================
# ==============================================================================
def main():
    global SIMILARITY_THRESHOLD, LENGTH_RATIO_THRESHOLD, WORD_OVERLAP_THRESHOLD, BASE_CRITERION, MIN_TEXT_LENGTH, EXCERPT_THRESHOLD, MAX_COMPARE_LENGTH, USE_SMART_SAMPLING

    if len(sys.argv) < 3:
        print("❌ Fehler: Eingabe- und Ausgabe-Pfad fehlen.")
        print("Verwendung: python 01_dokumentenvergleich.py <eingabe_pfad> <ausgabe_pfad>")
        input("Drücke Enter zum Beenden...")
        return

    eingabe_pfad = Path(sys.argv[1])
    ausgabe_pfad = Path(sys.argv[2])

    # ==============================================================================
    # === LOGGING EINRICHTEN (Tee-Klasse für Konsole + Datei) =====================
    # ==============================================================================
    log_filename = ausgabe_pfad / f"log_dokumentenvergleich_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_file = open(log_filename, 'w', encoding='utf-8')
    sys.stdout = Tee(sys.__stdout__, log_file)
    sys.stderr = Tee(sys.__stderr__, log_file)
    print(f"📝 Log-Datei erstellt: {log_filename}")
    print(f"🚀 Textdokumente-Vergleich (High-Performance Engine) gestartet\n")
    
    print("=" * 60)
    print("SCHRITT 1: Einstellungen für syntaktischen Vergleich")
    print("=" * 60)

    settings = get_settings_from_user(SIMILARITY_THRESHOLD, LENGTH_RATIO_THRESHOLD, WORD_OVERLAP_THRESHOLD, BASE_CRITERION, MIN_TEXT_LENGTH, EXCERPT_THRESHOLD, MAX_COMPARE_LENGTH)
    
    SIMILARITY_THRESHOLD = settings['sim']
    LENGTH_RATIO_THRESHOLD = settings['length']
    WORD_OVERLAP_THRESHOLD = settings['word']
    BASE_CRITERION = settings['base']
    MIN_TEXT_LENGTH = settings['min_len']
    EXCERPT_THRESHOLD = settings['exc_thresh']
    MAX_COMPARE_LENGTH = settings['max_compare']
    USE_SMART_SAMPLING = (settings['sampling'] == 'smart')

    print(f"\n⚙️ Aktive Einstellungen:")
    print(f"   Ähnlichkeit: {SIMILARITY_THRESHOLD} | Längenverhältnis: {LENGTH_RATIO_THRESHOLD} | Wort-Overlap: {WORD_OVERLAP_THRESHOLD}")
    print(f"   Mindestlänge: {MIN_TEXT_LENGTH} Zeichen | Auszugs-Schwelle: {EXCERPT_THRESHOLD}")
    print(f"   Max. Vergleichslänge: {MAX_COMPARE_LENGTH:,} Zeichen")
    print(f"   Sampling-Modus: {'Smart (Anfang + Ende)' if USE_SMART_SAMPLING else 'Standard (Nur Anfang)'}")

    print(f"\n✅ Ordner gewählt: {eingabe_pfad}")

    print("\n📂 Lese Dateien...")
    cache_dir = eingabe_pfad / ".conversion_cache"

    file_paths = []
    for file_path in eingabe_pfad.rglob('*'):
        if (file_path.is_file() and
            not file_path.name.startswith('.') and
            '.conversion_cache' not in str(file_path) and
            '.ki_conversion_cache' not in str(file_path) and
            'versionen_analyse' not in file_path.name and
            file_path.suffix.lower() in ALLOWED_TEXT_EXTENSIONS):
            file_paths.append(file_path)

    files_data = []
    for file_path in file_paths:
        try:
            text = extract_text(file_path, cache_dir)
            stat = file_path.stat()
            files_data.append({
                'path': file_path,
                'rel_path': str(file_path.relative_to(eingabe_pfad)),
                'name': file_path.name,
                'text': text,
                'size': stat.st_size,
                'mtime': stat.st_mtime
            })
        except Exception as e:
            print(f"  ⚠️ Fehler bei {file_path.name}: {e}")

    success_count = sum(1 for f in files_data if len(f['text']) > 0)
    empty_count = len(files_data) - success_count
    doc_count = sum(1 for f in files_data if f['path'].suffix.lower() == '.doc')
    docx_count = sum(1 for f in files_data if f['path'].suffix.lower() == '.docx')
    pdf_count = sum(1 for f in files_data if f['path'].suffix.lower() == '.pdf')
    other_count = len(files_data) - doc_count - docx_count - pdf_count

    print(f"\n✅ {len(files_data)} Dateien eingelesen.")
    print(f"   📊 Statistik:")
    print(f"     ✅ {success_count} Dateien mit erfolgreich extrahiertem Text")
    print(f"     ⚠️  {empty_count} Dateien ohne Text (leer oder Lesefehler)")
    print(f"   📄 Dateitypen-Verteilung:")
    print(f"     • {doc_count} alte .doc-Dateien (über LibreOffice konvertiert)")
    print(f"     • {docx_count} moderne .docx-Dateien (direkt gelesen)")
    print(f"     • {pdf_count} PDF-Dateien")
    print(f"     • {other_count} andere Formate (.txt, .odt, .rtf, etc.)")

    if empty_count > 0:
        print(f"   ⚠️  Dateien ohne Text:")
        for f in files_data:
            if len(f['text']) == 0:
                print(f"      - {f['name']} ({f['path'].suffix})")
    print()

    print("=" * 60)
    print("SCHRITT 2: Syntaktischer Vergleich")
    print("=" * 60)

    groups = find_version_groups(files_data, SIMILARITY_THRESHOLD, MAX_COMPARE_LENGTH)
    version_results = calculate_metrics(files_data, groups, BASE_CRITERION, MAX_COMPARE_LENGTH)
    
    print("\n🔍 DIAGNOSE: Analyse nicht-gruppierter Dateien...")
    ungrouped_count = 0
    for i, data in enumerate(files_data):
        ver = version_results.get(i, {})
        if not ver.get('gruppe'):
            ungrouped_count += 1
            text_len = len(data['text'].strip())
            print(f"  ⚠️ {data['name']}: {text_len} Zeichen extrahiert")
            
            if text_len == 0:
                print(f"     -> URSACHE: Datei ist leer oder Lesefehler.")
            elif text_len < MIN_TEXT_LENGTH:
                print(f"     -> URSACHE: Zu wenig Text (< {MIN_TEXT_LENGTH} Zeichen).")
            else:
                preview = data['text'].strip()[:50].replace('\n', ' ')
                print(f"     -> URSACHE: Text vorhanden, aber zu unterschiedlich. (Vorschau: '{preview}...')")
    
    if ungrouped_count == 0:
        print("  ✅ Alle Dateien mit ausreichend Text wurden erfolgreich gruppiert!")

    rows = []
    for i, data in enumerate(files_data):
        ver = version_results.get(i, {})
        dt = datetime.fromtimestamp(data['mtime']).strftime('%Y-%m-%d %H:%M:%S')
        
        row = {
            'Relativer_Pfad': data['rel_path'],
            'Dateiname': data['name'],
            'Dateityp': data['path'].suffix,
            'Versions_Gruppe': ver.get('gruppe', ''),
            'Basisdokument': ver.get('basis', ''),
            'Übereinstimmung_Zeichen': ver.get('match_chars', ''),
            'Übereinstimmung_Wörter': ver.get('match_words', ''),
            'Änderung_Zeichen_%': ver.get('change_chars_pct', ''),
            'Änderung_Wörter_%': ver.get('change_words_pct', ''),
            'Letzte_Aenderung': dt,
            'Dateigroesse_Bytes': data['size'],
            'Dokumententyp': 'Version' if ver.get('gruppe') else '',
            'KI_Gefundene_Gruppe': '',
            'KI_Semantische_Aehnlichkeit': '',
            'KI_Ergebnis': 'Bereits vom Hauptskript gruppiert' if ver.get('gruppe') else ''
        }
        rows.append(row)

    output_csv = ausgabe_pfad / "versionen_analyse.csv"
    save_csv(rows, output_csv)
    
    output_excel = ausgabe_pfad / "versionen_analyse_farbig.xlsx"
    save_as_excel(rows, output_excel)

    print("\n" + "=" * 60)
    print("✅ SCHRITT 1 ABGESCHLOSSEN!")
    print(f"📄 Ergebnis-CSV: {output_csv}")
    print(f"📊 Ergebnis-Excel: {output_excel}")
    print(f"📝 Log-Datei: {log_filename}")
    print("=" * 60)
    print("\nDu kannst nun in der menu.py '2 - KI-Analyse' auswählen.")
    input("\n⏹️ Drücke Enter zum Beenden...")

    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    
    # Log-Datei schließen (optional, wird beim Programmende automatisch geschlossen)
    log_file.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        input("Drücke Enter zum Beenden...")