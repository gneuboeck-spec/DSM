import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path

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
    
    print(f"\n{'='*60}")
    print(f" Starte: {script_path.relative_to(SCRIPT_DIR)}")
    print(f" Eingabe-Verzeichnis: {eingabe_pfad}")
    print(f" Ausgabe-Verzeichnis: {ausgabe_pfad}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [
                r"C:\Users\digit\AppData\Local\Programs\Python\Python313\python.exe",
                str(script_path),
                eingabe_pfad,
                ausgabe_pfad
            ],
            cwd=script_path.parent
        )
        
        if result.returncode == 0:
            print(f"\n✅ Skript erfolgreich abgeschlossen.")
        else:
            print(f"\n⚠️ Skript wurde mit Code {result.returncode} beendet.")
        
        return True
        
    except Exception as e:
        zeige_fehler("Fehler bei Skript-Ausführung", f"Das Skript konnte nicht gestartet werden:\n\n{e}")
        return False


# =====================================================
# Hauptprogramm
# =====================================================

def main():
    """Zeigt ein Menü zur Auswahl der Skripte."""
    
    print("\n" + "="*60)
    print("  PYTHON SKRIPT STARTER")
    print("="*60)
    print("\n Bitte wähle die Verzeichnisse...")
    
    # 1. Eingabe-Verzeichnis wählen
    eingabe_pfad = waehle_verzeichnis("Wähle das Eingabe-Verzeichnis (z.B. Dokumente zum Analysieren)")
    
    if not eingabe_pfad:
        print("\n❌ Abbruch: Kein Eingabe-Verzeichnis ausgewählt.")
        input("\nDrücke Enter zum Beenden...")
        return
    
    print(f"\n✅ Eingabe-Verzeichnis: {eingabe_pfad}")
    
    # 2. Ausgabe-Verzeichnis wählen
    ausgabe_pfad = waehle_verzeichnis("Wähle das Ausgabe-Verzeichnis (z.B. für Ergebnisse)")
    
    if not ausgabe_pfad:
        print("\n❌ Abbruch: Kein Ausgabe-Verzeichnis ausgewählt.")
        input("\nDrücke Enter zum Beenden...")
        return
    
    print(f"✅ Ausgabe-Verzeichnis: {ausgabe_pfad}")
    
    # 3. Hauptschleife des Menüs
    while True:
        print("\n" + "="*60)
        print("  PYTHON SKRIPT STARTER")
        print("="*60)
        print(f"\n Eingabe: {eingabe_pfad}")
        print(f" Ausgabe: {ausgabe_pfad}")
        print("\n Verfügbare Skripte:\n")
        
        scripts = get_scripts()
        
        if not scripts:
            print("   Keine Python-Skripte gefunden.")
        else:
            for i, script_path in enumerate(scripts, 1):
                rel_path = script_path.relative_to(SCRIPT_DIR)
                print(f"   {i:3} - {rel_path}")
        
        print("\n   V - Verzeichnisse neu wählen")
        print("   Q - Beenden")
        print("="*60)
        
        choice = input("\nBitte Nummer des Skripts eingeben (oder V / Q): ").strip().lower()
        
        if choice == "q":
            print("\n Programm wird beendet.")
            break
        
        elif choice == "v":
            # Verzeichnisse neu wählen
            neuer_eingabe = waehle_verzeichnis("Wähle das NEUE Eingabe-Verzeichnis")
            if neuer_eingabe:
                eingabe_pfad = neuer_eingabe
                print(f"\n✅ Neues Eingabe-Verzeichnis: {eingabe_pfad}")
            
            neuer_ausgabe = waehle_verzeichnis("Wähle das NEUE Ausgabe-Verzeichnis")
            if neuer_ausgabe:
                ausgabe_pfad = neuer_ausgabe
                print(f"✅ Neues Ausgabe-Verzeichnis: {ausgabe_pfad}")
            
            continue
        
        try:
            choice_index = int(choice) - 1
            
            if 0 <= choice_index < len(scripts):
                script_to_run = scripts[choice_index]
                skript_ausfuehren(script_to_run, eingabe_pfad, ausgabe_pfad)
                
                print("\n----------------------------------------------------")
                input("Skript-Ausführung beendet. Drücke Enter, um zum Menü zurückzukehren.")
            
            else:
                print("\n⚠️ Ungültige Auswahl.")
                input("Drücke Enter, um fortzufahren.")
        
        except ValueError:
            print("\n⚠️ Ungültige Eingabe. Bitte eine Nummer, V oder Q eingeben.")
            input("Drücke Enter, um fortzufahren.")
        
        except Exception as e:
            print(f"\nEin unerwarteter Fehler ist aufgetreten: {e}")
            input("Drücke Enter, um fortzufahren.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        zeige_fehler("Kritischer Fehler", f"Ein unerwarteter Fehler ist aufgetreten:\n\n{e}")
        input("\nDrücke Enter zum Beenden...")