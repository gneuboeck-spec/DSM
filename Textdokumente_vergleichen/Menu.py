# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

# ==============================================================================
# 🔧 FARB-INITIALISIERUNG (Konsistenz mit allen anderen Skripten)
# ==============================================================================
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore: GREEN = RED = YELLOW = CYAN = MAGENTA = WHITE = ""
    class Style: RESET_ALL = ""

# =====================================================
# Grundeinstellungen
# =====================================================

# Die Datei, in der sich dieses Skript befindet
MENU_FILE = Path(__file__).resolve()

# Der Hauptordner, in dem die menu.py liegt
SCRIPT_DIR = MENU_FILE.parent

# Diese Ordner werden nicht nach Python-Skripten durchsucht
EXCLUDED_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".idea",
    ".vscode",
}

# Diese Dateien werden nicht als startbare Skripte angezeigt
IGNORED_FILES = {
    MENU_FILE.name
}

# Verwende denselben Interpreter, mit dem dieses Menü selbst läuft.
# Das ist robust gegen unterschiedliche Installationspfade
# (User-Installation vs. System-Installation usw.).
# Falls das Menü mit pythonw.exe gestartet wurde, bevorzuge python.exe,
# damit Konsolenskripte sichtbar bleiben.
PYTHON_EXECUTABLE = sys.executable
if Path(PYTHON_EXECUTABLE).name.lower() == "pythonw.exe":
    candidate = Path(PYTHON_EXECUTABLE).with_name("python.exe")
    if candidate.exists():
        PYTHON_EXECUTABLE = str(candidate)


# =====================================================
# GUI-Hilfsfunktionen
# =====================================================

def waehle_verzeichnis(titel):
    """Öffnet einen Explorer-Dialog zur Auswahl eines Verzeichnisses."""
    root = tk.Tk()
    root.withdraw()  # Hauptfenster verstecken
    root.attributes('-topmost', True)
    
    pfad = filedialog.askdirectory(title=titel)
    root.destroy()
    
    return pfad


def zeige_fehler(titel, nachricht):
    """Zeigt eine Fehlermeldung an."""
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    messagebox.showerror(titel, nachricht)
    root.destroy()


# =====================================================
# Hilfsfunktionen
# =====================================================

def is_excluded_folder(script_path: Path) -> bool:
    """
    Prüft, ob die Datei in einem ausgeschlossenen Ordner liegt.
    """
    try:
        rel_path = script_path.relative_to(SCRIPT_DIR)
    except ValueError:
        return True

    # Der letzte Teil ist der Dateiname.
    # Wir prüfen nur die darüberliegenden Ordner.
    folders = rel_path.parts[:-1]

    return any(folder in EXCLUDED_DIRS for folder in folders)


def get_scripts():
    """
    Sucht alle Python-Skripte im Hauptordner und in allen Unterordnern.
    Ausgeschlossene Ordner und die menu.py selbst werden ignoriert.
    """
    scripts = []

    for path in SCRIPT_DIR.rglob("*.py"):
        if path.name in IGNORED_FILES:
            continue

        if is_excluded_folder(path):
            continue

        scripts.append(path)

    # Sortierung nach relativem Pfad, unabhängig von Groß-/Kleinschreibung
    return sorted(
        scripts,
        key=lambda p: str(p.relative_to(SCRIPT_DIR)).lower()
    )


# =====================================================
# Skript-Ausführung
# =====================================================

def skript_ausfuehren(script_path, eingabe_pfad, ausgabe_pfad):
    """Führt ein Skript mit den gegebenen Pfaden aus."""
    
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN} Starte: {script_path.name}{Style.RESET_ALL}")
    print(f"{Fore.WHITE} Eingabe-Verzeichnis: {Fore.GREEN}{eingabe_pfad}{Style.RESET_ALL}")
    print(f"{Fore.WHITE} Ausgabe-Verzeichnis: {Fore.GREEN}{ausgabe_pfad}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}\n")
    
    try:
        result = subprocess.run(
            [
                PYTHON_EXECUTABLE,
                str(script_path),
                eingabe_pfad,
                ausgabe_pfad
            ],
            cwd=script_path.parent
        )
        
        if result.returncode == 0:
            print(f"\n{Fore.GREEN}✅ Skript erfolgreich abgeschlossen.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.YELLOW}⚠️ Skript wurde mit Code {result.returncode} beendet.{Style.RESET_ALL}")
        
        return True
        
    except Exception as e:
        zeige_fehler("Fehler bei Skript-Ausführung", f"Das Skript konnte nicht gestartet werden:\n\n{e}")
        return False


# =====================================================
# Hauptprogramm
# =====================================================

def main():
    """Zeigt ein Menü zur Auswahl der Skripte."""
    
    print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}  SKRIPTSAMMLUNG DOKUMENTE VERGLEICHEN{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
    print(f"\n{Fore.WHITE} Bitte wähle die Verzeichnisse...{Style.RESET_ALL}")
    
    # 1. Eingabe-Verzeichnis wählen
    eingabe_pfad = waehle_verzeichnis("Wähle das Eingabe-Verzeichnis (z.B. Dokumente zum Analysieren)")
    
    if not eingabe_pfad:
        print(f"\n{Fore.RED}❌ Abbruch: Kein Eingabe-Verzeichnis ausgewählt.{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Drücke Enter zum Beenden...{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.GREEN}✅ Eingabe-Verzeichnis: {eingabe_pfad}{Style.RESET_ALL}")
    
    # 2. Ausgabe-Verzeichnis wählen
    ausgabe_pfad = waehle_verzeichnis("Wähle das Ausgabe-Verzeichnis (z.B. für Ergebnisse)")
    
    if not ausgabe_pfad:
        print(f"\n{Fore.RED}❌ Abbruch: Kein Ausgabe-Verzeichnis ausgewählt.{Style.RESET_ALL}")
        input(f"\n{Fore.YELLOW}Drücke Enter zum Beenden...{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}✅ Ausgabe-Verzeichnis: {ausgabe_pfad}{Style.RESET_ALL}")
    
    # 3. Hauptschleife des Menüs
    while True:
        print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  PYTHON SKRIPTE DOKUMENTE VERGLEICHEN{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        print(f"\n{Fore.WHITE} Eingabe: {Fore.GREEN}{eingabe_pfad}{Style.RESET_ALL}")
        print(f"{Fore.WHITE} Ausgabe: {Fore.GREEN}{ausgabe_pfad}{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN} Verfügbare Skripte:{Style.RESET_ALL}\n")
        
        scripts = get_scripts()
        
        if not scripts:
            print(f"{Fore.YELLOW}   Keine Python-Skripte gefunden.{Style.RESET_ALL}")
        else:
            for i, script_path in enumerate(scripts, 1):
                # Nur den Dateinamen anzeigen, nicht den Pfad
                print(f"   {Fore.GREEN}{i:3}{Style.RESET_ALL} - {Fore.WHITE}{script_path.name}{Style.RESET_ALL}")
        
        print(f"\n{Fore.MAGENTA}---------------------------------------------------{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}E{Style.RESET_ALL} - {Fore.WHITE}Nur Eingabe-Verzeichnis ändern{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}A{Style.RESET_ALL} - {Fore.WHITE}Nur Ausgabe-Verzeichnis ändern{Style.RESET_ALL}")
        print(f"   {Fore.GREEN}V{Style.RESET_ALL} - {Fore.WHITE}Beide Verzeichnisse neu wählen{Style.RESET_ALL}")
        print(f"   {Fore.RED}Q{Style.RESET_ALL} - {Fore.WHITE}Beenden{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
        
        choice = input(f"\n{Fore.YELLOW}Bitte Nummer des Skripts eingeben (oder E/A/V/Q): {Style.RESET_ALL}").strip().lower()
        
        if choice == "q":
            print(f"\n{Fore.CYAN} Programm wird beendet.{Style.RESET_ALL}")
            break
        
        elif choice == "e":
            # Nur Eingabe-Verzeichnis neu wählen
            neuer_eingabe = waehle_verzeichnis(
                f"Wähle das NEUE Eingabe-Verzeichnis\n(aktuell: {eingabe_pfad})"
            )
            if neuer_eingabe:
                eingabe_pfad = neuer_eingabe
                print(f"\n{Fore.GREEN}✅ Neues Eingabe-Verzeichnis: {eingabe_pfad}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠️ Keine Änderung - altes Eingabe-Verzeichnis bleibt erhalten.{Style.RESET_ALL}")
            continue
        
        elif choice == "a":
            # Nur Ausgabe-Verzeichnis neu wählen
            neuer_ausgabe = waehle_verzeichnis(
                f"Wähle das NEUE Ausgabe-Verzeichnis\n(aktuell: {ausgabe_pfad})"
            )
            if neuer_ausgabe:
                ausgabe_pfad = neuer_ausgabe
                print(f"\n{Fore.GREEN}✅ Neues Ausgabe-Verzeichnis: {ausgabe_pfad}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.YELLOW}⚠️ Keine Änderung - altes Ausgabe-Verzeichnis bleibt erhalten.{Style.RESET_ALL}")
            continue
        
        elif choice == "v":
            # Beide Verzeichnisse neu wählen
            print(f"\n{Fore.CYAN}--- Schritt 1/2: Eingabe-Verzeichnis ---{Style.RESET_ALL}")
            neuer_eingabe = waehle_verzeichnis(
                f"Wähle das NEUE Eingabe-Verzeichnis\n(aktuell: {eingabe_pfad})"
            )
            if neuer_eingabe:
                eingabe_pfad = neuer_eingabe
                print(f"{Fore.GREEN}✅ Neues Eingabe-Verzeichnis: {eingabe_pfad}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ Eingabe-Verzeichnis unverändert.{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}--- Schritt 2/2: Ausgabe-Verzeichnis ---{Style.RESET_ALL}")
            neuer_ausgabe = waehle_verzeichnis(
                f"Wähle das NEUE Ausgabe-Verzeichnis\n(aktuell: {ausgabe_pfad})"
            )
            if neuer_ausgabe:
                ausgabe_pfad = neuer_ausgabe
                print(f"{Fore.GREEN}✅ Neues Ausgabe-Verzeichnis: {ausgabe_pfad}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ Ausgabe-Verzeichnis unverändert.{Style.RESET_ALL}")
            
            continue
        
        try:
            choice_index = int(choice) - 1
            
            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]
                skript_ausfuehren(script_to_run, eingabe_pfad, ausgabe_pfad)
                
                print(f"\n{Fore.MAGENTA}----------------------------------------------------{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Skript-Ausführung beendet. Drücke Enter, um zum Menü zurückzukehren.{Style.RESET_ALL}")
            
            else:
                print(f"\n{Fore.YELLOW}⚠️ Ungültige Auswahl.{Style.RESET_ALL}")
                input(f"{Fore.YELLOW}Drücke Enter, um fortzufahren.{Style.RESET_ALL}")
        
        except ValueError:
            print(f"\n{Fore.YELLOW}⚠️ Ungültige Eingabe. Bitte eine Nummer, E, A, V oder Q eingeben.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Drücke Enter, um fortzufahren.{Style.RESET_ALL}")
        
        except Exception as e:
            print(f"\n{Fore.RED}Ein unerwarteter Fehler ist aufgetreten: {e}{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Drücke Enter, um fortzufahren.{Style.RESET_ALL}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        zeige_fehler("Kritischer Fehler", f"Ein unerwarteter Fehler ist aufgetreten:\n\n{e}")
        input(f"\n{Fore.YELLOW}Drücke Enter zum Beenden...{Style.RESET_ALL}")