import sys
import csv
import tkinter as tk
from tkinter import messagebox, ttk
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.unicode_minus'] = False


# ==============================================================================
# === SCHRITT 3: VISUALISIERUNG =================================================
# ==============================================================================
def get_groups_for_visualization(rows):
    groups = defaultdict(list)
    for row in rows:
        grp = row.get('Versions_Gruppe', '').strip()
        if not grp:
            grp = row.get('KI_Gefundene_Gruppe', '').strip()
        
        if grp:
            groups[grp].append(row)
        else:
            if 'Ungrouped' not in groups:
                groups['Ungrouped'] = []
            groups['Ungrouped'].append(row)
    return dict(groups)


def show_overview(rows, groups):
    # ========================================================================
    # HILFSFUNKTIONEN FÜR DIE EINZELNEN DIAGRAMME
    # ========================================================================
    
    def show_group_distribution():
        """Zeigt die Verteilung der Dokumente pro Gruppe."""
        fig = plt.figure(figsize=(14, 8))
        fig.suptitle('📊 Dokumente pro Gruppe - Gesamtübersicht', 
                     fontsize=16, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        group_names = list(groups.keys())
        group_sizes = [len(groups[g]) for g in group_names]
        colors = plt.cm.Set3(range(len(group_names)))
        
        ax.barh(group_names, group_sizes, color=colors)
        ax.set_xlabel('Anzahl Dokumente', fontsize=11)
        ax.set_title(' Dokumente pro Gruppe', fontsize=13, pad=15)
        ax.grid(axis='x', alpha=0.3)
        
        # Werte auf den Balken anzeigen
        for i, v in enumerate(group_sizes):
            ax.text(v + 0.5, i, str(v), va='center', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def show_document_types():
        """Zeigt die Verteilung der Dokumententypen."""
        fig = plt.figure(figsize=(10, 8))
        fig.suptitle('📝 Verteilung der Dokumententypen - Gesamtübersicht', 
                     fontsize=16, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        version_count = sum(1 for r in rows if r.get('Dokumententyp', '').strip() == 'Version')
        kurztext_count = sum(1 for r in rows if r.get('Dokumententyp', '').strip() == 'Kurztext')
        untyped_count = len(rows) - version_count - kurztext_count
        
        labels, sizes = [], []
        colors_list = []
        
        if version_count > 0:
            labels.append(f'Versionen\n({version_count})')
            sizes.append(version_count)
            colors_list.append('#4CAF50')
        if kurztext_count > 0:
            labels.append(f'Kurztexte\n({kurztext_count})')
            sizes.append(kurztext_count)
            colors_list.append('#FF9800')
        if untyped_count > 0:
            labels.append(f'Ohne Typ\n({untyped_count})')
            sizes.append(untyped_count)
            colors_list.append('#9E9E9E')
        
        if sizes:
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                               startangle=90, colors=colors_list,
                                               textprops={'fontsize': 10})
            ax.set_title('📝 Verteilung Dokumententypen', fontsize=13, pad=15)
        else:
            ax.text(0.5, 0.5, 'Keine Dokumente vorhanden', 
                    ha='center', va='center', fontsize=12)
        
        plt.tight_layout()
        plt.show()
    
    def show_avg_file_sizes():
        """Zeigt die durchschnittliche Dateigröße pro Gruppe."""
        fig = plt.figure(figsize=(14, 8))
        fig.suptitle('💾 Durchschnittliche Dateigröße pro Gruppe - Gesamtübersicht', 
                     fontsize=16, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        group_names = list(groups.keys())
        avg_sizes = []
        
        for g in group_names:
            docs = groups[g]
            avg = sum(d['Dateigroesse_Bytes_int'] for d in docs) / len(docs) if docs else 0
            avg_sizes.append(avg / 1024)  # In KB
        
        # Dynamische Schriftgröße
        fontsize = max(7, 9 - len(group_names) * 0.1)
        
        bars = ax.bar(group_names, avg_sizes, color='steelblue')
        ax.set_ylabel('Durchschnittliche Größe (KB)', fontsize=11)
        ax.set_title('💾 Durchschnittliche Dateigröße pro Gruppe', fontsize=13, pad=15)
        ax.tick_params(axis='x', rotation=45, labelsize=fontsize)
        ax.grid(axis='y', alpha=0.3)
        
        # Werte auf den Balken anzeigen
        for bar, val in zip(bars, avg_sizes):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                   f'{val:.0f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def show_ki_similarity_overview():
        """Zeigt die KI-Ähnlichkeit aller Kurztexte."""
        fig = plt.figure(figsize=(14, 8))
        fig.suptitle('🧠 KI-Ähnlichkeit aller Kurztexte - Gesamtübersicht', 
                     fontsize=16, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        kurztexte = [r for r in rows if r.get('Dokumententyp', '').strip() == 'Kurztext' 
                     and r.get('KI_Aehnlichkeit_pct', 0) > 0]
        
        if kurztexte:
            kt_names = [r['Dateiname'] for r in kurztexte]
            kt_scores = [r['KI_Aehnlichkeit_pct'] for r in kurztexte]
            colors_kt = ['#4CAF50' if s >= 70 else '#FF9800' if s >= 55 else '#F44336' for s in kt_scores]
            
            # Dynamische Schriftgröße
            fontsize = max(7, 9 - len(kurztexte) * 0.15)
            
            ax.barh(kt_names, kt_scores, color=colors_kt)
            ax.set_xlim(0, 100)
            ax.set_xlabel('Semantische Ähnlichkeit (%)', fontsize=11)
            ax.set_title('🧠 KI-Ähnlichkeit der Kurztexte', fontsize=13, pad=15)
            ax.tick_params(axis='y', labelsize=fontsize)
            ax.axvline(x=55, color='red', linestyle='--', label='Threshold (55%)', linewidth=1.5)
            ax.legend(fontsize=10)
            ax.grid(axis='x', alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Keine Kurztexte mit KI-Werten vorhanden', 
                    ha='center', va='center', fontsize=12)
            ax.set_title('🧠 KI-Ähnlichkeit der Kurztexte', fontsize=13, pad=15)
        
        plt.tight_layout()
        plt.show()
    
    def show_all_overview():
        """Zeigt alle 4 Diagramme gleichzeitig im 2x2-Grid."""
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle('📊 Gesamtübersicht der Dokumenten-Analyse', 
                     fontsize=18, fontweight='bold', y=0.98)
        
        # Diagramm 1: Dokumente pro Gruppe
        ax1 = fig.add_subplot(2, 2, 1)
        group_names = list(groups.keys())
        group_sizes = [len(groups[g]) for g in group_names]
        colors = plt.cm.Set3(range(len(group_names)))
        
        ax1.barh(group_names, group_sizes, color=colors)
        ax1.set_xlabel('Anzahl Dokumente', fontsize=10)
        ax1.set_title(' Dokumente pro Gruppe', fontsize=12, pad=15)
        ax1.grid(axis='x', alpha=0.3)
        
        # Werte auf den Balken anzeigen
        for i, v in enumerate(group_sizes):
            ax1.text(v + 0.5, i, str(v), va='center', fontsize=8)
        
        # Diagramm 2: Dokumententypen
        ax2 = fig.add_subplot(2, 2, 2)
        version_count = sum(1 for r in rows if r.get('Dokumententyp', '').strip() == 'Version')
        kurztext_count = sum(1 for r in rows if r.get('Dokumententyp', '').strip() == 'Kurztext')
        untyped_count = len(rows) - version_count - kurztext_count
        
        labels, sizes = [], []
        colors_list = []
        
        if version_count > 0:
            labels.append(f'Versionen\n({version_count})')
            sizes.append(version_count)
            colors_list.append('#4CAF50')
        if kurztext_count > 0:
            labels.append(f'Kurztexte\n({kurztext_count})')
            sizes.append(kurztext_count)
            colors_list.append('#FF9800')
        if untyped_count > 0:
            labels.append(f'Ohne Typ\n({untyped_count})')
            sizes.append(untyped_count)
            colors_list.append('#9E9E9E')
        
        if sizes:
            ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                    colors=colors_list, textprops={'fontsize': 9})
        ax2.set_title('📝 Verteilung Dokumententypen', fontsize=12, pad=15)
        
        # Diagramm 3: Durchschnittliche Dateigröße
        ax3 = fig.add_subplot(2, 2, 3)
        avg_sizes = []
        
        for g in group_names:
            docs = groups[g]
            avg = sum(d['Dateigroesse_Bytes_int'] for d in docs) / len(docs) if docs else 0
            avg_sizes.append(avg / 1024)
        
        fontsize = max(6, 8 - len(group_names) * 0.1)
        
        bars = ax3.bar(group_names, avg_sizes, color='steelblue')
        ax3.set_ylabel('Durchschnittliche Größe (KB)', fontsize=10)
        ax3.set_title('💾 Durchschnittliche Dateigröße pro Gruppe', fontsize=12, pad=15)
        ax3.tick_params(axis='x', rotation=45, labelsize=fontsize)
        ax3.grid(axis='y', alpha=0.3)
        
        # Werte auf den Balken anzeigen
        for bar, val in zip(bars, avg_sizes):
            ax3.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'{val:.0f}', ha='center', va='bottom', fontsize=8)
        
        # Diagramm 4: KI-Ähnlichkeit
        ax4 = fig.add_subplot(2, 2, 4)
        kurztexte = [r for r in rows if r.get('Dokumententyp', '').strip() == 'Kurztext' 
                     and r.get('KI_Aehnlichkeit_pct', 0) > 0]
        
        if kurztexte:
            kt_names = [r['Dateiname'] for r in kurztexte]
            kt_scores = [r['KI_Aehnlichkeit_pct'] for r in kurztexte]
            colors_kt = ['#4CAF50' if s >= 70 else '#FF9800' if s >= 55 else '#F44336' for s in kt_scores]
            
            fontsize = max(6, 8 - len(kurztexte) * 0.15)
            
            ax4.barh(kt_names, kt_scores, color=colors_kt)
            ax4.set_xlim(0, 100)
            ax4.set_xlabel('Semantische Ähnlichkeit (%)', fontsize=10)
            ax4.set_title(' KI-Ähnlichkeit der Kurztexte', fontsize=12, pad=15)
            ax4.tick_params(axis='y', labelsize=fontsize)
            ax4.axvline(x=55, color='red', linestyle='--', label='Threshold (55%)', linewidth=1.5)
            ax4.legend(fontsize=9)
            ax4.grid(axis='x', alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'Keine Kurztexte mit KI-Werten vorhanden', 
                     ha='center', va='center', fontsize=11)
            ax4.set_title('🧠 KI-Ähnlichkeit der Kurztexte', fontsize=12, pad=15)
        
        fig.subplots_adjust(top=0.92, hspace=0.45, wspace=0.30, 
                            left=0.10, right=0.95, bottom=0.10)
        
        plt.show()
    
    # ========================================================================
    # AUSWAHLMENÜ FENSTER
    # ========================================================================
    menu_root = tk.Tk()
    menu_root.title("📊 Gesamtübersicht - Visualisierung")
    menu_root.geometry("550x450")
    menu_root.resizable(False, False)
    
    menu_root.update_idletasks()
    x = (menu_root.winfo_screenwidth() // 2) - 275
    y = (menu_root.winfo_screenheight() // 2) - 225
    menu_root.geometry(f"+{x}+{y}")
    
    tk.Label(menu_root, text="📊 Gesamtübersicht der Dokumenten-Analyse", 
             font=("Arial", 14, "bold")).pack(pady=15)
    tk.Label(menu_root, text=f"{len(rows)} Dokumente in {len(groups)} Gruppen", 
             font=("Arial", 10)).pack()
    
    btn_frame = tk.Frame(menu_root)
    btn_frame.pack(pady=20, fill="x", padx=30)
    
    tk.Button(btn_frame, text="📁 Dokumente pro Gruppe", 
              command=show_group_distribution, 
              width=35, height=2, font=("Arial", 11)).pack(pady=5)
    
    tk.Button(btn_frame, text="📝 Verteilung Dokumententypen", 
              command=show_document_types, 
              width=35, height=2, font=("Arial", 11)).pack(pady=5)
    
    tk.Button(btn_frame, text="💾 Durchschnittliche Dateigröße pro Gruppe", 
              command=show_avg_file_sizes, 
              width=35, height=2, font=("Arial", 11)).pack(pady=5)
    
    tk.Button(btn_frame, text="🧠 KI-Ähnlichkeit aller Kurztexte", 
              command=show_ki_similarity_overview, 
              width=35, height=2, font=("Arial", 11)).pack(pady=5)
    
    ttk.Separator(btn_frame, orient='horizontal').pack(fill='x', pady=10)
    
    tk.Button(btn_frame, text="🌐 Alle 4 Diagramme gleichzeitig", 
              command=show_all_overview, 
              width=35, height=2, font=("Arial", 11, "bold"),
              bg="#2196F3", fg="white").pack(pady=5)
    
    tk.Button(menu_root, text="Schließen", command=menu_root.destroy, 
              width=15, font=("Arial", 10)).pack(pady=10)
    
    menu_root.mainloop()


def show_single_group(rows, groups, group_name):
    if group_name not in groups:
        messagebox.showerror("Fehler", f"Gruppe '{group_name}' nicht gefunden!")
        return
    
    group_docs = groups[group_name]
    
    base_doc_name = None
    for d in group_docs:
        if '(Basis)' in d.get('Basisdokument', ''):
            base_doc_name = d['Dateiname']
            break
    
    # ========================================================================
    # HILFSFUNKTIONEN FÜR DIE EINZELNEN DIAGRAMME
    # ========================================================================
    
    def show_timeline():
        """Zeigt den Zeitstrahl mit dynamischer Zeitachse (zeigt Sekunden bei kleinen Abständen)."""
        fig = plt.figure(figsize=(14, 8))
        fig.suptitle(f'📅 Zeitstrahl: {group_name} ({len(group_docs)} Dokumente)', 
                     fontsize=14, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        valid_docs = [d for d in group_docs if d.get('Letzte_Aenderung_dt')]
        
        if valid_docs:
            # Immer chronologisch nach Datum sortieren
            valid_docs = sorted(valid_docs, key=lambda x: x['Letzte_Aenderung_dt'])
            dates = [d['Letzte_Aenderung_dt'] for d in valid_docs]
            names = [d['Dateiname'] for d in valid_docs]
            types = [d.get('Dokumententyp', 'Version').strip() for d in valid_docs]
            colors_ts = ['#4CAF50' if t == 'Version' else '#FF9800' for t in types]
            
            # Zeitspanne berechnen, um die Achse dynamisch anzupassen
            time_span_seconds = (max(dates) - min(dates)).total_seconds()
            
            fontsize = max(7, 9 - len(valid_docs) * 0.2)
            
            y_positions = []
            assigned = {}
            
            for i, date in enumerate(dates):
                nearby = [j for j in range(len(dates)) 
                          if abs((date - dates[j]).total_seconds()) < 86400]
                
                y_pos = 0
                while any(assigned.get(j) == y_pos for j in nearby if j in assigned):
                    y_pos += 1
                
                y_positions.append(y_pos)
                assigned[i] = y_pos
            
            max_y = max(y_positions) if y_positions else 0
            
            ax.scatter(dates, [0]*len(dates), c=colors_ts, s=80, zorder=5, 
                      edgecolors='black', linewidth=0.5)
            
            for i, (date, name, y_pos) in enumerate(zip(dates, names, y_positions)):
                short_name = name[:25] + '...' if len(name) > 25 else name
                
                if y_pos % 2 == 0:
                    y_offset = 20 + (y_pos * 15)
                    va = 'bottom'
                    stem_end = 0.02 + (y_pos * 0.015)
                else:
                    y_offset = -(20 + (y_pos * 15))
                    va = 'top'
                    stem_end = -(0.02 + (y_pos * 0.015))
                
                ax.plot([date, date], [0, stem_end], color='gray', linewidth=0.8, zorder=4)
                
                ax.annotate(short_name, 
                           xy=(date, 0), 
                           xytext=(0, y_offset), 
                           textcoords="offset points",
                           fontsize=fontsize, ha='center', va=va,
                           bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                    edgecolor='gray', alpha=0.7))
            
            y_limit = 0.15 + (max_y * 0.05)
            ax.set_ylim(-y_limit, y_limit)
            ax.set_yticks([])
            ax.set_xlabel('Datum der letzten Änderung', fontsize=10)
            ax.grid(axis='x', alpha=0.3)
            
            # === DYNAMISCHE FORMATIERUNG DER ZEITACHSE ===
            if time_span_seconds < 3600:  # Weniger als 1 Stunde Unterschied
                # Zeige Sekunden, damit man die winzigen Unterschiede sofort sieht
                date_format = '%d.%m. %H:%M:%S'
            else:
                # Normale Anzeige ohne Sekunden (bei großen Zeitabständen)
                date_format = '%d.%m.%Y %H:%M'
            
            ax.xaxis.set_major_formatter(mdates.DateFormatter(date_format))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
            
        else:
            ax.text(0.5, 0.5, 'Keine Datumsinformationen vorhanden', 
                    ha='center', va='center', fontsize=12)
        
        plt.tight_layout()
        plt.show()
    
    def show_file_sizes():
        """Zeigt den Dateigrößen-Vergleich in einem eigenen Fenster."""
        fig = plt.figure(figsize=(12, max(8, len(group_docs) * 0.5)))
        fig.suptitle(f'💾 Dateigrößen-Vergleich: {group_name}', 
                     fontsize=14, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        doc_names = [d['Dateiname'] for d in group_docs]
        doc_sizes_kb = [d['Dateigroesse_Bytes_int'] / 1024 for d in group_docs]
        doc_types = [d.get('Dokumententyp', 'Version').strip() for d in group_docs]
        colors_sizes = ['#4CAF50' if t == 'Version' else '#FF9800' for t in doc_types]
        
        # Dynamische Schriftgröße
        fontsize = max(7, 9 - len(group_docs) * 0.15)
        
        ax.barh(range(len(doc_names)), doc_sizes_kb, color=colors_sizes)
        ax.set_yticks(range(len(doc_names)))
        ax.set_yticklabels(doc_names, fontsize=fontsize)
        ax.set_xlabel('Dateigröße (KB)', fontsize=10)
        ax.grid(axis='x', alpha=0.3)
        
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='#4CAF50', label='Version'),
                          Patch(facecolor='#FF9800', label='Kurztext')]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
        
        plt.tight_layout()
        plt.show()
    
    def show_text_changes():
        """Zeigt die Text-Änderung gegen Basis in einem eigenen Fenster."""
        fig = plt.figure(figsize=(14, 8))
        fig.suptitle(f'📈 Text-Änderung gegen Basis: {group_name}', 
                     fontsize=14, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        version_docs = [d for d in group_docs 
                        if d.get('Dokumententyp', '').strip() == 'Version' 
                        and '(Basis)' not in d.get('Basisdokument', '')]
        
        if version_docs:
            changes = [d['Aenderung_Zeichen_pct'] for d in version_docs]
            v_names = [d['Dateiname'] for d in version_docs]
            
            # Dynamische Schriftgröße
            fontsize = max(6, 8 - len(version_docs) * 0.2)
            
            ax.bar(range(len(v_names)), changes, color='steelblue')
            ax.set_xticks(range(len(v_names)))
            ax.set_xticklabels(v_names, rotation=45, ha='right', fontsize=fontsize)
            ax.set_ylabel('Änderung in % (gegen Basis)', fontsize=10)
            
            if base_doc_name:
                base_short = base_doc_name[:30] + '...' if len(base_doc_name) > 30 else base_doc_name
                ax.set_title(f'Basis-Dokument: "{base_short}"', fontsize=11, pad=10)
            else:
                ax.set_title('Basis-Dokument', fontsize=11, pad=10)
            
            ax.axhline(y=0, color='red', linestyle='-', linewidth=0.5)
            ax.grid(axis='y', alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Keine Versionen außer dem Basis-Dokument vorhanden', 
                    ha='center', va='center', fontsize=11)
        
        plt.tight_layout()
        plt.show()
    
    def show_ki_similarity():
        """Zeigt die KI-Ähnlichkeit in einem eigenen Fenster."""
        fig = plt.figure(figsize=(12, max(8, len(group_docs) * 0.5)))
        fig.suptitle(f'🧠 KI-Ähnlichkeit: {group_name}', 
                     fontsize=14, fontweight='bold')
        
        ax = fig.add_subplot(1, 1, 1)
        kurztexte_grp = [d for d in group_docs if d.get('Dokumententyp', '').strip() == 'Kurztext']
        
        if kurztexte_grp:
            kt_names = [d['Dateiname'] for d in kurztexte_grp]
            kt_scores = [d['KI_Aehnlichkeit_pct'] for d in kurztexte_grp]
            colors_kt = ['#4CAF50' if s >= 70 else '#FF9800' if s >= 55 else '#F44336' for s in kt_scores]
            
            # Dynamische Schriftgröße
            fontsize = max(7, 9 - len(kurztexte_grp) * 0.2)
            
            ax.barh(range(len(kt_names)), kt_scores, color=colors_kt)
            ax.set_yticks(range(len(kt_names)))
            ax.set_yticklabels(kt_names, fontsize=fontsize)
            ax.set_xlim(0, 100)
            ax.set_xlabel('Semantische Ähnlichkeit (%)', fontsize=10)
            ax.axvline(x=55, color='red', linestyle='--', label='Threshold (55%)')
            ax.legend(fontsize=9)
        else:
            ax.text(0.5, 0.5, 'Keine Kurztexte in dieser Gruppe', 
                    ha='center', va='center', fontsize=12)
        
        plt.tight_layout()
        plt.show()
    
    def show_all():
        """Zeigt alle 4 Diagramme gleichzeitig im 2x2-Grid."""
        fig = plt.figure(figsize=(20, 16))
        fig.suptitle(f' Gruppe: {group_name} ({len(group_docs)} Dokumente)', 
                     fontsize=16, fontweight='bold', y=0.98)
        
        # Zeitstrahl
        ax1 = fig.add_subplot(2, 2, 1)
        valid_docs = sorted([d for d in group_docs if d.get('Letzte_Aenderung_dt')], 
                            key=lambda x: x['Letzte_Aenderung_dt'])
        
        if valid_docs:
            dates = [d['Letzte_Aenderung_dt'] for d in valid_docs]
            names = [d['Dateiname'] for d in valid_docs]
            types = [d.get('Dokumententyp', 'Version').strip() for d in valid_docs]
            colors_ts = ['#4CAF50' if t == 'Version' else '#FF9800' for t in types]
            
            fontsize = max(6, 8 - len(valid_docs) * 0.2)
            
            y_positions = []
            assigned = {}
            
            for i, date in enumerate(dates):
                nearby = [j for j in range(len(dates)) 
                          if abs((date - dates[j]).total_seconds()) < 86400]
                
                y_pos = 0
                while any(assigned.get(j) == y_pos for j in nearby if j in assigned):
                    y_pos += 1
                
                y_positions.append(y_pos)
                assigned[i] = y_pos
            
            max_y = max(y_positions) if y_positions else 0
            
            ax1.scatter(dates, [0]*len(dates), c=colors_ts, s=80, zorder=5, 
                       edgecolors='black', linewidth=0.5)
            
            for i, (date, name, y_pos) in enumerate(zip(dates, names, y_positions)):
                short_name = name[:20] + '...' if len(name) > 20 else name
                
                if y_pos % 2 == 0:
                    y_offset = 15 + (y_pos * 12)
                    va = 'bottom'
                    stem_end = 0.02 + (y_pos * 0.012)
                else:
                    y_offset = -(15 + (y_pos * 12))
                    va = 'top'
                    stem_end = -(0.02 + (y_pos * 0.012))
                
                ax1.plot([date, date], [0, stem_end], color='gray', linewidth=0.8, zorder=4)
                
                ax1.annotate(short_name, 
                            xy=(date, 0), 
                            xytext=(0, y_offset), 
                            textcoords="offset points",
                            fontsize=fontsize, ha='center', va=va,
                            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                     edgecolor='gray', alpha=0.7))
            
            y_limit = 0.15 + (max_y * 0.05)
            ax1.set_ylim(-y_limit, y_limit)
            ax1.set_yticks([])
            ax1.set_xlabel('Datum der letzten Änderung', fontsize=9)
            ax1.set_title('📅 Zeitstrahl der Dokumenten-Entwicklung', fontsize=10, pad=10)
            ax1.grid(axis='x', alpha=0.3)
            ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M'))
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=7)
        else:
            ax1.text(0.5, 0.5, 'Keine Datumsinformationen vorhanden', 
                     ha='center', va='center', fontsize=12)
            ax1.set_title('📅 Zeitstrahl', fontsize=10)
        
        # Dateigrößen
        ax2 = fig.add_subplot(2, 2, 2)
        doc_names = [d['Dateiname'] for d in group_docs]
        doc_sizes_kb = [d['Dateigroesse_Bytes_int'] / 1024 for d in group_docs]
        doc_types = [d.get('Dokumententyp', 'Version').strip() for d in group_docs]
        colors_sizes = ['#4CAF50' if t == 'Version' else '#FF9800' for t in doc_types]
        
        fontsize = max(6, 8 - len(group_docs) * 0.15)
        
        ax2.barh(range(len(doc_names)), doc_sizes_kb, color=colors_sizes)
        ax2.set_yticks(range(len(doc_names)))
        ax2.set_yticklabels([n[:22] + '...' if len(n) > 22 else n for n in doc_names], fontsize=fontsize)
        ax2.set_xlabel('Dateigröße (KB)', fontsize=9)
        ax2.set_title('💾 Dateigrößen-Vergleich', fontsize=10, pad=10)
        ax2.grid(axis='x', alpha=0.3)
        
        from matplotlib.patches import Patch
        legend_elements = [Patch(facecolor='#4CAF50', label='Version'),
                          Patch(facecolor='#FF9800', label='Kurztext')]
        ax2.legend(handles=legend_elements, loc='lower right', fontsize=8)
        
        # Text-Änderung
        ax3 = fig.add_subplot(2, 2, 3)
        version_docs = [d for d in group_docs 
                        if d.get('Dokumententyp', '').strip() == 'Version' 
                        and '(Basis)' not in d.get('Basisdokument', '')]
        
        if version_docs:
            changes = [d['Aenderung_Zeichen_pct'] for d in version_docs]
            v_names = [d['Dateiname'] for d in version_docs]
            
            fontsize = max(5, 7 - len(version_docs) * 0.2)
            
            ax3.bar(range(len(v_names)), changes, color='steelblue')
            ax3.set_xticks(range(len(v_names)))
            ax3.set_xticklabels([n[:12] + '...' if len(n) > 12 else n for n in v_names], 
                               rotation=45, ha='right', fontsize=fontsize)
            ax3.set_ylabel('Änderung in % (gegen Basis)', fontsize=9)
            
            if base_doc_name:
                base_short = base_doc_name[:20] + '...' if len(base_doc_name) > 20 else base_doc_name
                ax3.set_title(f' Text-Änderung gegen Basis: "{base_short}"', fontsize=10, pad=10)
            else:
                ax3.set_title(' Text-Änderung gegenüber Basis-Dokument', fontsize=10, pad=10)
            
            ax3.axhline(y=0, color='red', linestyle='-', linewidth=0.5)
            ax3.grid(axis='y', alpha=0.3)
        else:
            ax3.text(0.5, 0.5, 'Keine Versionen außer dem Basis-Dokument vorhanden', 
                     ha='center', va='center', fontsize=11)
            ax3.set_title('📈 Text-Änderung', fontsize=10)
        
        # KI-Ähnlichkeit
        ax4 = fig.add_subplot(2, 2, 4)
        kurztexte_grp = [d for d in group_docs if d.get('Dokumententyp', '').strip() == 'Kurztext']
        
        if kurztexte_grp:
            kt_names = [d['Dateiname'] for d in kurztexte_grp]
            kt_scores = [d['KI_Aehnlichkeit_pct'] for d in kurztexte_grp]
            colors_kt = ['#4CAF50' if s >= 70 else '#FF9800' if s >= 55 else '#F44336' for s in kt_scores]
            
            fontsize = max(6, 8 - len(kurztexte_grp) * 0.2)
            
            ax4.barh(range(len(kt_names)), kt_scores, color=colors_kt)
            ax4.set_yticks(range(len(kt_names)))
            ax4.set_yticklabels([n[:22] + '...' if len(n) > 22 else n for n in kt_names], fontsize=fontsize)
            ax4.set_xlim(0, 100)
            ax4.set_xlabel('Semantische Ähnlichkeit (%)', fontsize=9)
            ax4.set_title('🧠 KI-Ähnlichkeit der Kurztexte', fontsize=10, pad=10)
            ax4.axvline(x=55, color='red', linestyle='--', label='Threshold (55%)')
            ax4.legend(fontsize=8)
        else:
            ax4.text(0.5, 0.5, 'Keine Kurztexte in dieser Gruppe', 
                     ha='center', va='center', fontsize=12)
            ax4.set_title('🧠 KI-Ähnlichkeit', fontsize=10)
        
        fig.subplots_adjust(top=0.92, hspace=0.50, wspace=0.30, 
                            left=0.10, right=0.95, bottom=0.12)
        
        plt.show()
    
    # ========================================================================
    # AUSWAHLMENÜ FENSTER
    # ========================================================================
    menu_root = tk.Tk()
    menu_root.title(f"📊 Visualisierung: {group_name}")
    menu_root.geometry("500x400")
    menu_root.resizable(False, False)
    
    menu_root.update_idletasks()
    x = (menu_root.winfo_screenwidth() // 2) - 250
    y = (menu_root.winfo_screenheight() // 2) - 200
    menu_root.geometry(f"+{x}+{y}")
    
    tk.Label(menu_root, text=f" Gruppe: {group_name}", 
             font=("Arial", 14, "bold")).pack(pady=15)
    tk.Label(menu_root, text=f"{len(group_docs)} Dokumente", 
             font=("Arial", 10)).pack()
    
    btn_frame = tk.Frame(menu_root)
    btn_frame.pack(pady=20, fill="x", padx=30)
    
    tk.Button(btn_frame, text="📅 Zeitstrahl", 
              command=show_timeline, 
              width=30, height=2, font=("Arial", 11)).pack(pady=5)
    
    tk.Button(btn_frame, text=" Dateigrößen-Vergleich", 
              command=show_file_sizes, 
              width=30, height=2, font=("Arial", 11)).pack(pady=5)
    
    tk.Button(btn_frame, text="📈 Text-Änderung gegen Basis", 
              command=show_text_changes, 
              width=30, height=2, font=("Arial", 11)).pack(pady=5)
    
    tk.Button(btn_frame, text="🧠 KI-Ähnlichkeit", 
              command=show_ki_similarity, 
              width=30, height=2, font=("Arial", 11)).pack(pady=5)
    
    ttk.Separator(btn_frame, orient='horizontal').pack(fill='x', pady=10)
    
    tk.Button(btn_frame, text="🌐 Alle 4 Diagramme gleichzeitig", 
              command=show_all, 
              width=30, height=2, font=("Arial", 11, "bold"),
              bg="#4CAF50", fg="white").pack(pady=5)
    
    tk.Button(menu_root, text="Schließen", command=menu_root.destroy, 
              width=15, font=("Arial", 10)).pack(pady=10)
    
    menu_root.mainloop()


def show_visualization_menu(rows):
    groups = get_groups_for_visualization(rows)
    
    root = tk.Tk()
    root.title("📊 Dokumenten-Analyse Visualisierung")
    root.geometry("500x400")
    root.resizable(False, False)
    
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - 250
    y = (root.winfo_screenheight() // 2) - 200
    root.geometry(f"+{x}+{y}")
    
    tk.Label(root, text="📊 Dokumenten-Analyse Visualisierung", 
             font=("Arial", 14, "bold")).pack(pady=20)
    tk.Label(root, text=f"{len(rows)} Dokumente in {len(groups)} Gruppen", 
             font=("Arial", 10)).pack()
    
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20, fill="x", padx=30)
    
    tk.Button(btn_frame, text="🌐 Gesamtübersicht aller Gruppen", 
              command=lambda: show_overview(rows, groups), 
              width=35, height=2, font=("Arial", 10)).pack(pady=5)
    
    ttk.Separator(btn_frame, orient='horizontal').pack(fill='x', pady=10)
    tk.Label(btn_frame, text="Einzelne Gruppe auswählen:", font=("Arial", 10, "bold")).pack()
    
    group_var = tk.StringVar()
    if groups:
        group_var.set(list(groups.keys())[0])
    
    dropdown = ttk.Combobox(btn_frame, textvariable=group_var, values=list(groups.keys()), 
                            state="readonly", width=30, font=("Arial", 10))
    dropdown.pack(pady=5)
    
    tk.Button(btn_frame, text="🔍 Diese Gruppe visualisieren", 
              command=lambda: show_single_group(rows, groups, group_var.get()), 
              width=35, height=2, font=("Arial", 10)).pack(pady=10)
    
    tk.Button(root, text="Beenden", command=root.destroy, width=15).pack(pady=10)
    root.mainloop()


# ==============================================================================
# === MAIN =====================================================================
# ==============================================================================
def main():
    if len(sys.argv) < 3:
        print("❌ Fehler: Eingabe- und Ausgabe-Pfad fehlen.")
        print("Verwendung: python 03_visualisierung.py <eingabe_pfad> <ausgabe_pfad>")
        input("Drücke Enter zum Beenden...")
        return

    ausgabe_pfad = Path(sys.argv[2])

    csv_file = ausgabe_pfad / "versionen_analyse_mit_ki.csv"
    if not csv_file.exists():
        csv_file = ausgabe_pfad / "versionen_analyse.csv"
    
    if not csv_file.exists():
        print(f"❌ Keine CSV gefunden in: {ausgabe_pfad}")
        print("Bitte zuerst Skript 1 (und optional 2) ausführen.")
        input("Drücke Enter zum Beenden...")
        return

    print(f"\n🚀 Visualisierung gestartet")
    print(f"Lade Daten aus: {csv_file}")
    print("=" * 60)

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f, delimiter=';'))

    for row in rows:
        if row.get('Letzte_Aenderung'):
            try:
                row['Letzte_Aenderung_dt'] = datetime.strptime(row['Letzte_Aenderung'].strip(), '%Y-%m-%d %H:%M:%S')
            except:
                row['Letzte_Aenderung_dt'] = None
        else:
            row['Letzte_Aenderung_dt'] = None
        
        try:
            row['Dateigroesse_Bytes_int'] = int(row.get('Dateigroesse_Bytes', 0))
        except:
            row['Dateigroesse_Bytes_int'] = 0
        
        try:
            row['Aenderung_Zeichen_pct'] = float(row.get('Änderung_Zeichen_%', '0').replace('%', '').replace('+', ''))
        except:
            row['Aenderung_Zeichen_pct'] = 0.0
        
        try:
            row['KI_Aehnlichkeit_pct'] = float(row.get('KI_Semantische_Aehnlichkeit', '0').replace('%', ''))
        except:
            row['KI_Aehnlichkeit_pct'] = 0.0

    show_visualization_menu(rows)
    
    print("\n" + "=" * 60)
    print("✅ VISUALISIERUNG ABGESCHLOSSEN!")
    print("=" * 60)
    input("\n⏹️ Drücke Enter zum Beenden...")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        input("Drücke Enter zum Beenden...")