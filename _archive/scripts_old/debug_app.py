#!/usr/bin/env python3
"""
Version de debug pour diagnostiquer le problème
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class DebugApp:
    def __init__(self, root):
        print("1. Initialisation de l'application...")
        self.root = root
        self.root.title("🎧 Test - Générateur de Compréhension Orale")
        self.root.geometry("900x700")
        print("2. Fenêtre configurée")
        
        # Variables
        self.theme = tk.StringVar()
        print("3. Variables créées")
        
        # Configuration OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"4. Clé API: {'✅ Trouvée' if api_key else '❌ Non trouvée'}")
        
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
        
        print("5. Création des widgets...")
        self.create_widgets()
        print("6. Interface créée avec succès !")
    
    def create_widgets(self):
        """Crée l'interface graphique"""
        print("  5.1 Création de l'en-tête...")
        
        # En-tête
        header = tk.Label(
            self.root,
            text="🎓 Générateur de Compréhension Orale en Allemand",
            font=("Helvetica", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            pady=10
        )
        header.pack(fill=tk.X)
        print("  5.2 En-tête créé")
        
        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        print("  5.3 Frame principale créée")
        
        # Étape 1 : Choix du thème
        step1_frame = ttk.LabelFrame(main_frame, text="📝 Étape 1 : Choisir le thème", padding="10")
        step1_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(step1_frame, text="Thème en français :").grid(row=0, column=0, sticky=tk.W, padx=5)
        theme_entry = ttk.Entry(step1_frame, textvariable=self.theme, width=40)
        theme_entry.grid(row=0, column=1, padx=5)
        
        test_btn = ttk.Button(
            step1_frame,
            text="Test",
            command=lambda: print("Bouton cliqué !")
        )
        test_btn.grid(row=0, column=2, padx=5)
        print("  5.4 Étape 1 créée")
        
        # Zone de statut
        self.status_text = scrolledtext.ScrolledText(main_frame, height=8, wrap=tk.WORD)
        self.status_text.pack(fill=tk.BOTH, expand=True, pady=5)
        self.status_text.insert(tk.END, "✨ Application de debug prête !\n")
        self.status_text.insert(tk.END, "Si vous voyez ce texte, l'interface fonctionne.\n")
        print("  5.5 Zone de statut créée")

def main():
    print("="*60)
    print("DEBUG - Lancement de l'application")
    print("="*60)
    root = tk.Tk()
    print("0. Fenêtre Tk créée")
    app = DebugApp(root)
    print("7. Démarrage de la boucle principale...")
    root.mainloop()
    print("8. Application fermée")

if __name__ == "__main__":
    main()
