import subprocess
import sys
from pathlib import Path

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
    """Zeigt den Header an."""
    print("===================================================")
    print("       Skriptsammlung WIENBIBLIOTHEK")
    print("===================================================")
    print(f" Aktueller Bereich: {current_path}")
    print("---------------------------------------------------")

def start_submenu(folder_name: str):
    """Startet die start.bat eines Unterordners."""
    submenu_path = SCRIPT_DIR / folder_name
    start_bat = submenu_path / "start.bat"
    
    if not start_bat.exists():
        print(f"\n[FEHLER] start.bat nicht gefunden in: {submenu_path}")
        input("Drücken Sie Enter, um fortzufahren.")
        return
    
    print(f"\n--- Starte Bereich: {folder_name} ---")
    print(f"Das Fenster bleibt geöffnet und kehrt danach hierher zurück.\n")
    
    # Startet die start.bat des Unterordners
    subprocess.run([str(start_bat)], cwd=str(submenu_path), shell=True)
    
    print(f"\n--- Bereich {folder_name} wurde beendet. ---")
    input("Drücken Sie Enter, um zum Hauptmenü zurückzukehren.")

# =====================================================
# Hauptprogramm
# =====================================================
def main():
    while True:
        print_header("Hauptmenü")
        
        print("\n   --- Bereiche ---")
        folder_list = sorted(list(SUBMENU_DIRS))
        
        for folder_name in folder_list:
            shortcut = FOLDER_SHORTCUTS.get(folder_name, folder_name[0].upper())
            print(f"   {shortcut}   - [ORDNER] {folder_name}")

        print("\n---------------------------------------------------")
        print("   Q - Beenden")
        print("===================================================")

        choice = input("\nBitte Buchstaben eingeben: ").strip().lower()

        if choice == "q":
            break

        choice_upper = choice.upper()
        matched = False
        
        for folder_name in folder_list:
            if FOLDER_SHORTCUTS.get(folder_name, folder_name[0].upper()) == choice_upper:
                start_submenu(folder_name)
                matched = True
                break
        
        if not matched:
            print("\nUngueltige Eingabe.")
            input("Druecken Sie Enter, um fortzufahren.")

if __name__ == "__main__":
    main()