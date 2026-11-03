# SPDX-FileCopyrightText: 2025 Gregor Neuboeck <g.neuboeck@gmail.com>
#
# SPDX-License-Identifier: MIT

import subprocess
import sys
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
MENU_FILE = Path(__file__).resolve()
SCRIPT_DIR = MENU_FILE.parent

# Die drei Hauptkategorien (Unterordner)
SUBMENU_DIRS = {
    "Datenaufbereitung",
    "Textdokumente_vergleichen",
    "Tools"
}

# Shortcuts für die Ordner
FOLDER_SHORTCUTS = {
    "Datenaufbereitung": "D",
    "Textdokumente_vergleichen": "T",
    "Tools": "O"
}

# =====================================================
# Hilfsfunktionen
# =====================================================
def print_header(current_path):
    """Zeigt den farbigen Header an."""
    print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")
    print(f"{Fore.CYAN}       Skriptsammlung WIENBIBLIOTHEK{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")
    print(f"{Fore.WHITE} Aktueller Bereich: {current_path}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}---------------------------------------------------{Style.RESET_ALL}")

def start_submenu(folder_name: str):
    """Startet die start.bat eines Unterordners."""
    submenu_path = SCRIPT_DIR / folder_name
    start_bat = submenu_path / "start.bat"
    
    if not start_bat.exists():
        print(f"\n{Fore.RED}[FEHLER] start.bat nicht gefunden in: {submenu_path}{Style.RESET_ALL}")
        input(f"{Fore.YELLOW}Drücken Sie Enter, um fortzufahren.{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.CYAN}--- Starte Bereich: {folder_name} ---{Style.RESET_ALL}")
    print(f"{Fore.WHITE}Das Fenster bleibt geöffnet und kehrt danach hierher zurück.{Style.RESET_ALL}\n")
    
    # Startet die start.bat des Unterordners
    subprocess.run([str(start_bat)], cwd=str(submenu_path), shell=True)
    
    print(f"\n{Fore.GREEN}--- Bereich '{folder_name}' wurde erfolgreich beendet. ---{Style.RESET_ALL}")
    input(f"{Fore.YELLOW}Drücken Sie Enter, um zum Hauptmenü zurückzukehren.{Style.RESET_ALL}")

# =====================================================
# Hauptprogramm
# =====================================================
def main():
    while True:
        print_header("Hauptmenü")
        
        print(f"\n{Fore.CYAN}   --- Bereiche ---{Style.RESET_ALL}")
        folder_list = sorted(list(SUBMENU_DIRS))
        
        for folder_name in folder_list:
            shortcut = FOLDER_SHORTCUTS.get(folder_name, folder_name[0].upper())
            # Format: [D] - [ORDNER] Datenaufbereitung (mit farbiger Hervorhebung)
            print(f"   {Fore.GREEN}[{shortcut}]{Style.RESET_ALL}   - {Fore.WHITE}[ORDNER] {folder_name}{Style.RESET_ALL}")

        print(f"\n{Fore.MAGENTA}---------------------------------------------------{Style.RESET_ALL}")
        print(f"   {Fore.RED}Q{Style.RESET_ALL} - {Fore.WHITE}Beenden{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}==================================================={Style.RESET_ALL}")

        # Gelbe, klare Eingabeaufforderung
        choice = input(f"\n{Fore.YELLOW}Bitte Buchstaben eingeben: {Style.RESET_ALL}").strip().lower()

        if choice == "q":
            print(f"\n{Fore.CYAN}Menü wird beendet. Auf Wiedersehen!{Style.RESET_ALL}")
            break

        choice_upper = choice.upper()
        matched = False
        
        for folder_name in folder_list:
            if FOLDER_SHORTCUTS.get(folder_name, folder_name[0].upper()) == choice_upper:
                start_submenu(folder_name)
                matched = True
                break
        
        if not matched:
            print(f"\n{Fore.RED}[FEHLER] Ungültige Eingabe. Bitte versuchen Sie es erneut.{Style.RESET_ALL}")
            input(f"{Fore.YELLOW}Drücken Sie Enter, um fortzufahren.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()