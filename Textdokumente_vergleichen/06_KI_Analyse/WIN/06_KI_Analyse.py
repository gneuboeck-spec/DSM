# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
import csv
import re
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

# ==============================================================================
# 🔧 FARB-INITIALISIERUNG (Konsistenz mit allen anderen Skripten)
# ==============================================================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

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
MODEL_NAME = 'paraphrase-multilingual-mpnet-base-v2'
SEMANTIC_THRESHOLD_DEFAULT = 0.55
MIN_TEXT_LENGTH_DEFAULT = 100
MAX_TEXT_LENGTH_DEFAULT = 5000
MAX_CHARS_FOR_AI = 3000
TRIGGER_WORDS = ['abstract', 'zusammenfassung', 'summary', 'review', 'rezension',
                 'einleitung', 'aufsatz', 'essay', 'beitrag', 'article']

# Fester, zentraler Cache-Pfad für das KI-Modell (unabhängig vom Skript-Standort)
KI_MODEL_CACHE = Path.home() / ".ki_model_cache"


# ==============================================================================
# === HILFSFUNKTIONEN ==========================================================
# ==============================================================================
def get_ai_text_sample(text, max_chars=3000):
    text = text.strip()
    if len(text) <= max_chars:
        return text
    half = max_chars // 2
    return text[:half] + "\n\n[...]\n\n" + text[-half:]


def extract_text_simple(file_path: Path, cache_dir: Path = None) -> str:
    ext = file_path.suffix.lower()
    try:
        if ext == '.txt':
            return file_path.read_text(encoding='utf-8', errors='ignore')
        elif ext == '.docx':
            import docx
            return "\n".join([p.text for p in docx.Document(file_path).paragraphs])
        elif ext == '.doc':
            if cache_dir: 
                return ""
            return ""
        elif ext == '.pdf':
            import pymupdf
            doc = pymupdf.open(file_path)
            return "\n".join([page.get_text() for page in doc])
        elif ext in ['.odt', '.ods', '.odf']:
            import zipfile
            try:
                with zipfile.ZipFile(file_path, 'r') as z:
                    if 'content.xml' in z.namelist():
                        xml = z.read('content.xml').decode('utf-8', errors='ignore')
                        return re.sub(r'<[^>]+>', ' ', xml).strip()
            except Exception:
                return ""
    except Exception as e:
        print(f"      {Fore.RED}⚠️ Lesefehler bei {file_path.name}: {e}{Style.RESET_ALL}")
        return ""
    return ""


def get_ki_settings_from_user(default_thresh, default_min, default_max):
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    dialog = tk.Toplevel(root)
    dialog.title("KI-Einstellungen")
    dialog.geometry("550x420")
    dialog.resizable(False, False)
    dialog.grab_set()
    
    dialog.update_idletasks()
    x = (dialog.winfo_screenwidth() // 2) - (550 // 2)
    y = (dialog.winfo_screenheight() // 2) - (420 // 2)
    dialog.geometry(f"+{x}+{y}")
    
    result = {'threshold': default_thresh, 'min_len': default_min, 'max_len': default_max}
    
    def on_apply():
        try:
            val_thresh = float(entry_thresh.get()) if entry_thresh.get() else default_thresh
            val_min = int(entry_min.get()) if entry_min.get() else default_min
            val_max = int(entry_max.get()) if entry_max.get() else default_max
            
            if not (0.0 <= val_thresh <= 1.0):
                messagebox.showerror("Fehler", "Threshold muss zwischen 0.0 und 1.0 liegen!", parent=dialog)
                return
            if val_min < 0 or val_max <= val_min:
                messagebox.showerror("Fehler", "Mindestlänge muss >= 0 und kleiner als Maximallänge sein!", parent=dialog)
                return
            
            result['threshold'] = val_thresh
            result['min_len'] = val_min
            result['max_len'] = val_max
            dialog.destroy()
        except ValueError:
            messagebox.showerror("Fehler", "Bitte nur gültige Zahlen eingeben!", parent=dialog)

    def on_skip():
        dialog.destroy()

    tk.Label(dialog, text="KI-Semantische Analyse Einstellungen", font=("Arial", 11, "bold")).pack(pady=10)
    
    frame = tk.Frame(dialog)
    frame.pack(padx=20, fill="x")
    
    tk.Label(frame, text=f"Semantischer Threshold (0.0-1.0)\nStandard: {default_thresh}", anchor="w", justify="left").grid(row=0, column=0, sticky="w", pady=5)
    entry_thresh = tk.Entry(frame, width=10)
    entry_thresh.insert(0, str(default_thresh))
    entry_thresh.grid(row=0, column=1, padx=10)
    
    tk.Label(frame, text=f"Mindestlänge (Zeichen)\nStandard: {default_min}", anchor="w", justify="left").grid(row=1, column=0, sticky="w", pady=5)
    entry_min = tk.Entry(frame, width=10)
    entry_min.insert(0, str(default_min))
    entry_min.grid(row=1, column=1, padx=10)
    
    tk.Label(frame, text=f"Maximallänge (Zeichen)\nStandard: {default_max}", anchor="w", justify="left").grid(row=2, column=0, sticky="w", pady=5)
    entry_max = tk.Entry(frame, width=10)
    entry_max.insert(0, str(default_max))
    entry_max.grid(row=2, column=1, padx=10)
    
    btn_frame = tk.Frame(dialog)
    btn_frame.pack(pady=15)
    
    tk.Button(btn_frame, text="Übernehmen", command=on_apply, width=12, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Abbrechen", command=on_skip, width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="📖 Ablauf", command=lambda: show_ki_process(dialog), width=10, bg="#FF9800", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="❓ Hilfe", command=lambda: show_ki_help(dialog), width=10, bg="#2196F3", fg="white", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
    
    dialog.protocol("WM_DELETE_WINDOW", on_skip)
    root.wait_window(dialog)
    return result


def show_ki_help(parent_dialog):
    help_root = tk.Toplevel(parent_dialog)
    help_root.title("Hilfe: KI-Parameter-Erklärungen")
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
    
    insert_text("KI-PARAMETER-ERKLÄRUNGEN")
    insert_text("Detaillierte Informationen zu den Einstellungen der semantischen Analyse\n")
    
    insert_section("SEMANTIC_THRESHOLD = 0.55 (55%) - Semantischer Schwellenwert")
    insert_content("Mindestens 55% semantische (inhaltliche) Ähnlichkeit, damit ein nicht-gruppiertes")
    insert_content("Dokument einer bestehenden Gruppe aus Schritt 1 zugeordnet wird.")
    insert_subsection("Wann anpassen:")
    insert_content("ERHÖHEN (z.B. 0.70): Strengere Zuordnung, weniger Falsch-Positiv-Ergebnisse.")
    insert_content("SENKEN (z.B. 0.40): Findet mehr Abstracts/Zusammenfassungen, aber evtl. ungenauer.")
    
    insert_section("MIN_TEXT_LENGTH = 100 (Zeichen) - Mindestlänge für KI-Prüfung")
    insert_content("Dokumente mit weniger als 100 Zeichen werden von der KI ignoriert.")
    insert_subsection("Grund:")
    insert_content("Sehr kurze Texte (z.B. reine Metadaten, leere Dateien oder Extrakt-Fehler)")
    insert_content("liefern keine aussagekräftigen KI-Embeddings und würden das Ergebnis verfälschen.")
    
    insert_section("MAX_TEXT_LENGTH = 5.000 (Zeichen) - Maximallänge für KI-Prüfung")
    insert_content("Dokumente mit mehr als 5.000 Zeichen werden von der KI ignoriert.")
    insert_subsection("Grund:")
    insert_content("Die KI soll primär Kurztexte (Abstracts, Zusammenfassungen) finden. Lange")
    insert_content("Hauptdokumente wurden bereits in Schritt 1 (syntaktisch) umfassend gruppiert.")
    insert_content("Dieser Filter spart enorm viel Rechenzeit und RAM.")
    
    insert_section("TRIGGER_WORDS - Auslöser-Wörter im Dateinamen")
    insert_content("abstract, zusammenfassung, summary, review, rezension, einleitung, aufsatz, essay, beitrag, article")
    insert_subsection("Funktion:")
    insert_content("Wenn eines dieser Wörter im Dateinamen vorkommt, wird das Dokument von der KI")
    insert_content("geprüft, SELBST WENN es länger als die Maximallänge ist. Dies stellt sicher,")
    insert_content("dass wichtige Zusammenfassungen nicht übersehen werden.")
    
    btn_frame = tk.Frame(help_root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Fenster schließen", command=help_root.destroy, 
              width=20, font=("Arial", 11, "bold")).pack()


def show_ki_process(parent_dialog):
    help_root = tk.Toplevel(parent_dialog)
    help_root.title("Ablauf der KI-Analyse - Schritt für Schritt")
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
    
    insert_text("ABLAUF DER KI-SEMANTISCHEN ANALYSE")
    insert_text("Wie das Skript Kurztexte den bestehenden Gruppen zuordnet\n")
    
    insert_content("Das Skript durchläuft 6 Hauptphasen, um inhaltlich ähnliche Kurztexte zu finden.")
    
    insert_section("PHASE 1: LADEN DES KI-MODELLS")
    insert_content("Das Skript lädt das vortrainierte Sprachmodell 'paraphrase-multilingual-mpnet-base-v2'")
    insert_content("in den Arbeitsspeicher. Beim ersten Start wird es aus dem Internet heruntergeladen")
    insert_content("und im zentralen Cache-Ordner (~/.ki_model_cache) gespeichert.")
    insert_example("Dieser Schritt dauert beim ersten Mal ca. 10-30 Sekunden, danach nur Millisekunden.")
    
    insert_section("PHASE 2: EXTRAKTION DER BASIS-TEXTE")
    insert_content("Das Skript liest die Ergebnisse aus Schritt 1 (CSV) ein und identifiziert die")
    insert_content("bereits gebildeten Dokumentengruppen. Für jede Gruppe wird das als '(Basis)'")
    insert_content("markierte Hauptdokument ausgewählt und dessen Text extrahiert.")
    insert_example("Gruppe 1: Basis ist 'roman_v1.docx' (gekürzt auf max. 3.000 Zeichen für die KI).")
    insert_example("Gruppe 2: Basis ist 'bericht_final.pdf' (gekürzt auf max. 3.000 Zeichen).")
    
    insert_section("PHASE 3: ERSTELLEN DER EMBEDDINGS (VEKTOREN)")
    insert_content("Die extrahierten Basis-Texte werden durch das KI-Modell in hochdimensionale")
    insert_content("Zahlenvektoren (Embeddings) umgewandelt. Diese Vektoren erfassen die semantische")
    insert_content("Bedeutung des Textes, nicht nur die exakten Wörter.")
    insert_example("'Der Hund läuft schnell' und 'Der canine rennt rasch' erhalten sehr ähnliche Vektoren,")
    insert_example("obwohl sie kaum gemeinsame Wörter haben.")
    
    insert_section("PHASE 4: FILTERUNG DER KANDIDATEN")
    insert_content("Nicht jedes Dokument im Ordner wird an die KI geschickt. Ein schneller Filter")
    insert_content("prüft jedes nicht-gruppierte Dokument auf zwei Kriterien:")
    insert_content("  1. Enthält der Dateiname ein Trigger-Wort (z.B. 'zusammenfassung')?")
    insert_content("  2. Liegt die Textlänge zwischen der Mindest- und Maximallänge (z.B. 100 - 5.000 Zeichen)?")
    insert_content("Nur wenn mindestens EINES dieser Kriterien zutrifft, geht das Dokument in Phase 5.")
    insert_example("Eine 50 MB große PDF ohne Trigger-Wort wird sofort mit 'Nicht geprüft' übersprungen.")
    insert_example("Eine 200-Zeichen 'abstract.txt' wird zur Prüfung zugelassen.")
    
    insert_section("PHASE 5: KOSINUS-ÄHNLICHKEITSBERECHNUNG")
    insert_content("Für die zugelassenen Kandidaten wird ebenfalls ein KI-Embedding erstellt.")
    insert_content("Anschließend wird die Kosinus-Ähnlichkeit (Cosine Similarity) zwischen dem")
    insert_content("Kandidaten und allen Basis-Embeddings berechnet.")
    insert_content("Das Ergebnis ist ein Wert zwischen 0.0 (völlig unterschiedlich) und 1.0 (identisch).")
    insert_example("Kandidat 'abstract.txt' vs. Basis 'roman_v1.docx': Ähnlichkeit = 0.78 (78%)")
    insert_example("Kandidat 'abstract.txt' vs. Basis 'bericht_final.pdf': Ähnlichkeit = 0.12 (12%)")
    
    insert_section("PHASE 6: ZUORDNUNG UND EXPORT")
    insert_content("Das Skript wählt die Gruppe mit der höchsten Ähnlichkeit aus.")
    insert_content("Wenn dieser höchste Wert den eingestellten Threshold (z.B. 55%) erreicht oder")
    insert_content("überschreitet, wird das Dokument als 'Kurztext' dieser Gruppe zugeordnet.")
    insert_content("Andernfalls erhält es das Ergebnis 'Keine passende Gruppe'.")
    insert_content("Am Ende werden die angereicherten Daten in eine neue CSV und eine farbig")
    insert_content("formatierte Excel-Datei exportiert.")
    
    insert_section("ZUSAMMENFASSUNG")
    insert_content("Dieser mehrstufige Prozess stellt sicher, dass die rechenintensive KI nur dort")
    insert_content("eingesetzt wird, wo sie sinnvoll ist (bei potenziellen Kurztexten), und dass")
    insert_content("die Zuordnungen auf echter inhaltlicher Bedeutung basieren, nicht nur auf")
    insert_content("zufällig gleichen Wörtern.")
    
    btn_frame = tk.Frame(help_root)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="Fenster schließen", command=help_root.destroy, 
              width=20, font=("Arial", 11, "bold")).pack()


# ==============================================================================
# === SCHRITT 2: KI-ANALYSE ====================================================
# ==============================================================================
def run_ki_analysis(root_path, rows, threshold, min_len, max_len):
    print(f"\n{Fore.CYAN}🧠 Lade KI-Modell (beim 1. Mal dauert es etwas)...{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}📁 Cache-Ordner: {KI_MODEL_CACHE}{Style.RESET_ALL}")
    try:
        from sentence_transformers import SentenceTransformer, util
        KI_MODEL_CACHE.mkdir(exist_ok=True)
        model = SentenceTransformer(MODEL_NAME, cache_folder=str(KI_MODEL_CACHE))
        print(f"   {Fore.GREEN}✅ Modell geladen!{Style.RESET_ALL}\n")
    except Exception as e:
        print(f"{Fore.RED}❌ FEHLER beim Laden des KI-Modells: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Tipp: Installiere es mit 'pip install sentence-transformers'{Style.RESET_ALL}")
        return rows
    
    cache_dir = root_path / ".ki_conversion_cache"
    
    grouped_docs = {}
    for row in rows:
        if row['Versions_Gruppe']:
            grp = row['Versions_Gruppe']
            if grp not in grouped_docs:
                grouped_docs[grp] = []
            grouped_docs[grp].append(row)
    
    print(f"   {Fore.CYAN}Extrahiere Referenztexte der bestehenden Gruppen...{Style.RESET_ALL}")
    group_bases = {}
    for grp, docs in grouped_docs.items():
        base_row = next((d for d in docs if '(Basis)' in d.get('Basisdokument', '')), None)
        if base_row:
            base_path = root_path / base_row['Relativer_Pfad']
            if base_path.exists():
                full_txt = extract_text_simple(base_path, cache_dir)
                group_bases[grp] = get_ai_text_sample(full_txt, MAX_CHARS_FOR_AI)
    
    if not group_bases:
        print(f"{Fore.YELLOW}⚠️ Keine Basis-Dokumente gefunden.{Style.RESET_ALL}")
        return rows
    
    print(f"{Fore.CYAN}🔬 Führe semantische Analyse durch...{Style.RESET_ALL}")
    base_texts = list(group_bases.values())
    base_names = list(group_bases.keys())
    base_embeddings = model.encode(base_texts, convert_to_tensor=True)
    
    updated_count = 0
    for row in rows:
        if not row['Versions_Gruppe']:
            doc_path = root_path / row['Relativer_Pfad']
            if not doc_path.exists():
                row['KI_Ergebnis'] = "⚠️ Datei nicht gefunden"
                continue
            
            # Log-Dateien und Analyse-Ausgaben von der KI-Analyse ausschließen
            if (doc_path.name.startswith('log_') or 
                'versionen_analyse' in doc_path.name):
                row['KI_Ergebnis'] = "⏭️ Übersprungen (Analyse-Ausgabedatei)"
                continue
                
            is_trigger = any(word in row['Dateiname'].lower() for word in TRIGGER_WORDS)
            text = extract_text_simple(doc_path, cache_dir)
            
            # HIER: Verwendung der dynamischen Längenwerte statt fest codierter 100 und 5000
            is_short = min_len < len(text) < max_len
            
            if is_trigger or is_short:
                if not text.strip():
                    row['KI_Ergebnis'] = "⚠️ Kein Text extrahierbar"
                    continue
                    
                sample_text = get_ai_text_sample(text, MAX_CHARS_FOR_AI)
                doc_embedding = model.encode(sample_text, convert_to_tensor=True)
                cos_scores = util.cos_sim(doc_embedding, base_embeddings)[0]
                
                best_score_idx = cos_scores.argmax().item()
                best_score = cos_scores[best_score_idx].item()
                best_group = base_names[best_score_idx]
                
                row['KI_Semantische_Aehnlichkeit'] = f"{best_score:.2%}"
                
                if best_score >= threshold:
                    row['Dokumententyp'] = "Kurztext"
                    row['KI_Gefundene_Gruppe'] = best_group
                    row['KI_Ergebnis'] = f"✅ Kurztext-Zuordnung: {best_group}"
                    updated_count += 1
                else:
                    row['KI_Ergebnis'] = f"❌ Keine passende Gruppe ({best_score:.1%})"
            else:
                row['KI_Ergebnis'] = f"⚠️ Nicht geprüft (kein Trigger/außerhalb {min_len}-{max_len} Zeichen)"
    
    print(f"\n{Fore.GREEN}🎉 Fertig! {updated_count} Kurztexte wurden durch die KI Gruppen zugeordnet.{Style.RESET_ALL}")
    return rows


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
    print(f"\n{Fore.GREEN}💾 CSV gespeichert: {output_file}{Style.RESET_ALL}")


# === NUR HIER WURDE EINE MINIMALE ÄNDERUNG VORGENOMMEN (base_dir Parameter + Hyperlink-Logik) ===
def save_as_excel(rows, output_file, base_dir: Path):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        print(f"{Fore.RED}⚠️ openpyxl nicht installiert. Bitte: pip install openpyxl{Style.RESET_ALL}")
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
            cell_value = row_data.get(field, '')
            cell = ws.cell(row=row_num, column=col_num, value=cell_value)
            cell.font = cell_font
            cell.fill = row_fill
            cell.alignment = cell_alignment
            cell.border = thin_border
            
            # NEU: Hyperlink für Relativer_Pfad hinzufügen
            if field == "Relativer_Pfad" and cell_value:
                abs_path = str((base_dir / cell_value).resolve())
                cell.hyperlink = abs_path
                cell.style = 'Hyperlink'
            
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
    print(f"{Fore.GREEN}📊 Excel-Datei mit Farben und klickbaren Hyperlinks gespeichert: {output_file}{Style.RESET_ALL}")


# ==============================================================================
# === MAIN =====================================================================
# ==============================================================================
def main():
    if len(sys.argv) < 3:
        print(f"{Fore.RED}❌ Fehler: Eingabe- und Ausgabe-Pfad fehlen.{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Verwendung: python 06_KI_Analyse.py <eingabe_pfad> <ausgabe_pfad>{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Drücke Enter zum Beenden...{Style.RESET_ALL}")
        return

    eingabe_pfad = Path(sys.argv[1])
    ausgabe_pfad = Path(sys.argv[2])

    # ==============================================================================
    # === LOGGING EINRICHTEN (Tee-Klasse für Konsole + Datei) =====================
    # ==============================================================================
    log_filename = ausgabe_pfad / f"log_ki_analyse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    log_file = open(log_filename, 'w', encoding='utf-8')
    sys.stdout = Tee(sys.__stdout__, log_file)
    sys.stderr = Tee(sys.__stderr__, log_file)
    print(f"{Fore.GREEN}📝 Log-Datei erstellt: {log_filename}{Style.RESET_ALL}")

    csv_file = ausgabe_pfad / "versionen_analyse.csv"
    if not csv_file.exists():
        print(f"{Fore.RED}❌ Datei nicht gefunden: {csv_file}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Bitte zuerst Skript 1 (Dokumentenvergleich) ausführen.{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Drücke Enter zum Beenden...{Style.RESET_ALL}")
        return

    print(f"\n{Fore.CYAN}🚀 KI-Analyse gestartet{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Eingabe (CSV): {csv_file}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Ausgabe:       {ausgabe_pfad}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}KI-Modell-Cache: {KI_MODEL_CACHE}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f, delimiter=';'))

    # NEU: Alle drei Einstellungen vom Benutzer abfragen
    settings = get_ki_settings_from_user(SEMANTIC_THRESHOLD_DEFAULT, MIN_TEXT_LENGTH_DEFAULT, MAX_TEXT_LENGTH_DEFAULT)
    threshold = settings['threshold']
    min_len = settings['min_len']
    max_len = settings['max_len']
    
    print(f"\n{Fore.CYAN}⚙️ Aktive KI-Einstellungen:{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}Semantischer Threshold: {threshold}{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}Längenfilter: {min_len} bis {max_len} Zeichen (oder Trigger-Wort im Namen){Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'-' * 60}{Style.RESET_ALL}")

    # NEU: Übergeben der neuen Längenparameter an die Analyse-Funktion
    rows = run_ki_analysis(eingabe_pfad, rows, threshold, min_len, max_len)

    output_csv = ausgabe_pfad / "versionen_analyse_mit_ki.csv"
    save_csv(rows, output_csv)
    
    output_excel = ausgabe_pfad / "versionen_analyse_mit_ki_farbig.xlsx"
    # NEU: eingabe_pfad wird jetzt als dritter Parameter übergeben
    save_as_excel(rows, output_excel, eingabe_pfad)

    print(f"\n{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✅ SCHRITT 2 ABGESCHLOSSEN!{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📄 Ergebnis-CSV: {output_csv}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📊 Ergebnis-Excel: {output_excel}{Style.RESET_ALL}")
    print(f"{Fore.GREEN}📝 Log-Datei: {log_filename}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'=' * 60}{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}Du kannst nun in der menu.py '3 - Visualisierung' auswählen.{Style.RESET_ALL}")
    input(f"\n{Fore.YELLOW}⏹️ Drücke Enter zum Beenden...{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n{Fore.RED}❌ KRITISCHER FEHLER: {e}{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Drücke Enter zum Beenden...{Style.RESET_ALL}")