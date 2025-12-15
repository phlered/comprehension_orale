#!/usr/bin/env python3
"""
Version alternative de l'application avec style différent pour macOS
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from openai import OpenAI
import edge_tts
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class ComprehensionOraleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Compréhension Orale - Allemand")
        self.root.geometry("900x700")
        
        # Forcer le fond blanc pour TOUT
        self.root.configure(bg='white')
        
        # Style pour macOS
        style = ttk.Style()
        try:
            style.theme_use('aqua')  # Thème natif macOS
        except:
            pass
        
        self.theme = tk.StringVar()
        self.word_count = tk.IntVar(value=300)
        self.vocabulary = []
        self.checkboxes = {}
        self.selected_words = []
        
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        
        self.create_widgets()
    
    def create_widgets(self):
        # Configuration du fond
        self.root.configure(bg='#F0F0F0')
        
        # Titre avec fond clair
        title = tk.Label(
            self.root,
            text="🎓 Générateur de Compréhension Orale en Allemand",
            font=("Arial", 18, "bold"),
            bg="#4CAF50",
            fg="white",
            pady=15
        )
        title.pack(fill=tk.X)
        
        # Frame principale avec fond clair explicite
        main_frame = tk.Frame(self.root, bg='#F0F0F0', padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Étape 1
        step1 = tk.LabelFrame(main_frame, text=" Étape 1 : Choisir le thème ", 
                             font=("Arial", 12, "bold"), bg='#F0F0F0', padx=10, pady=10)
        step1.pack(fill=tk.X, pady=5)
        
        tk.Label(step1, text="Thème en français :", bg='#F0F0F0', font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, padx=5)
        theme_entry = tk.Entry(step1, textvariable=self.theme, width=40, font=("Arial", 11), 
                              bg='white', fg='black', insertbackground='black')
        theme_entry.grid(row=0, column=1, padx=5, pady=5)
        
        btn_gen = tk.Button(step1, text="🤖 Générer vocabulaire", 
                          command=self.generate_vocabulary,
                          bg='#4CAF50', fg='white', font=("Arial", 10, "bold"),
                          padx=10, pady=5)
        btn_gen.grid(row=0, column=2, padx=5)
        
        btn_manual = tk.Button(step1, text="✏️ Mode manuel", 
                             command=self.manual_mode,
                             bg='#2196F3', fg='white', font=("Arial", 10, "bold"),
                             padx=10, pady=5)
        btn_manual.grid(row=0, column=3, padx=5)
        
        # Étape 2 - Vocabulaire
        step2 = tk.LabelFrame(main_frame, text=" Étape 2 : Vocabulaire ", 
                             font=("Arial", 12, "bold"), bg='#F0F0F0', padx=10, pady=10)
        step2.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Canvas pour scroll
        canvas = tk.Canvas(step2, height=150, bg='#F0F0F0')
        scrollbar = tk.Scrollbar(step2, orient="vertical", command=canvas.yview)
        self.words_frame = tk.Frame(canvas, bg='#F0F0F0')
        
        self.words_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.words_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        btn_add = tk.Button(step2, text="➕ Ajouter un mot", 
                          command=self.add_custom_word,
                          bg='#FF9800', fg='white', font=("Arial", 10, "bold"),
                          padx=10, pady=5)
        btn_add.pack(pady=5)
        
        # Étape 3
        step3 = tk.LabelFrame(main_frame, text=" Étape 3 : Longueur du texte ", 
                             font=("Arial", 12, "bold"), bg='#F0F0F0', padx=10, pady=10)
        step3.pack(fill=tk.X, pady=5)
        
        tk.Label(step3, text="Nombre de mots :", bg='#F0F0F0', font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, padx=5)
        
        spinbox = tk.Spinbox(step3, from_=100, to=1000, increment=50, 
                            textvariable=self.word_count, width=10, font=("Arial", 11),
                            bg='white', fg='black', buttonbackground='white')
        spinbox.grid(row=0, column=1, padx=5)
        tk.Label(step3, text="(±10%)", bg='#F0F0F0', font=("Arial", 11)).grid(row=0, column=2, sticky=tk.W)
        
        # Bouton génération
        btn_generate = tk.Button(main_frame, text="🚀 GÉNÉRER TEXTE ET AUDIO MP3",
                               command=self.generate_text_and_audio,
                               bg='#E91E63', fg='white', font=("Arial", 14, "bold"),
                               padx=20, pady=10)
        btn_generate.pack(pady=10)
        
        # Zone de log
        log_frame = tk.Frame(main_frame, bg='#F0F0F0')
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(log_frame, text="📊 Statut :", font=("Arial", 11, "bold"), bg='#F0F0F0').pack(anchor=tk.W)
        
        self.status_text = tk.Text(log_frame, height=6, wrap=tk.WORD, 
                                   font=("Courier", 10), bg='white', fg='black')
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("✨ Application prête ! Commencez par entrer un thème.")
        
        # Forcer le rafraîchissement
        self.root.update_idletasks()
        self.root.update()
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update()
    
    def generate_vocabulary(self):
        theme = self.theme.get().strip()
        if not theme:
            messagebox.showwarning("Thème manquant", "Veuillez entrer un thème.")
            return
        
        if not self.client:
            messagebox.showerror("API non configurée", "La clé API OpenAI n'est pas configurée.")
            return
        
        self.log(f"🤖 Génération du vocabulaire pour : {theme}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"""Génère 15 mots de vocabulaire en allemand sur le thème : {theme}
Format : mot allemand | traduction française
Sans numéros ni explications."""}],
                max_tokens=1024
            )
            
            vocab_text = response.choices[0].message.content.strip()
            self.vocabulary = []
            
            for line in vocab_text.split('\n'):
                line = line.strip()
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        self.vocabulary.append((parts[0].strip(), parts[1].strip()))
            
            self.display_vocabulary()
            self.log("✅ Vocabulaire généré avec succès")
        
        except Exception as e:
            self.log(f"❌ Erreur : {str(e)}")
            messagebox.showerror("Erreur", str(e))
    
    def manual_mode(self):
        self.vocabulary = [
            ("das Wort", "le mot"),
            ("die Sprache", "la langue"),
            ("lernen", "apprendre"),
        ]
        self.display_vocabulary()
        self.log("✏️ Mode manuel - 3 mots d'exemple ajoutés")
    
    def display_vocabulary(self):
        for widget in self.words_frame.winfo_children():
            widget.destroy()
        
        self.checkboxes = {}
        
        for i, (german, french) in enumerate(self.vocabulary):
            var = tk.BooleanVar(value=True)
            self.checkboxes[german] = var
            
            cb = tk.Checkbutton(
                self.words_frame,
                text=f"{german} — {french}",
                variable=var,
                bg='#F0F0F0',
                fg='black',
                font=("Arial", 10),
                selectcolor='white'
            )
            cb.grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
    
    def add_custom_word(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter un mot")
        dialog.geometry("400x150")
        dialog.configure(bg='#F0F0F0')
        
        tk.Label(dialog, text="Mot en allemand :", bg='#F0F0F0').grid(row=0, column=0, padx=10, pady=10)
        german_entry = tk.Entry(dialog, width=30, bg='white', fg='black', insertbackground='black')
        german_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(dialog, text="Traduction française :", bg='#F0F0F0').grid(row=1, column=0, padx=10, pady=10)
        french_entry = tk.Entry(dialog, width=30, bg='white', fg='black', insertbackground='black')
        french_entry.grid(row=1, column=1, padx=10, pady=10)
        
        def save():
            german = german_entry.get().strip()
            french = french_entry.get().strip()
            if german and french:
                self.vocabulary.append((german, french))
                self.display_vocabulary()
                self.log(f"➕ Mot ajouté : {german}")
                dialog.destroy()
        
        tk.Button(dialog, text="Ajouter", command=save).grid(row=2, column=0, columnspan=2, pady=10)
    
    def generate_text_and_audio(self):
        self.selected_words = [german for german, var in self.checkboxes.items() if var.get()]
        
        if len(self.selected_words) < 5:
            messagebox.showwarning("Pas assez de mots", "Sélectionnez au moins 5 mots.")
            return
        
        if not self.client:
            messagebox.showerror("API non configurée", "La clé API OpenAI est requise.")
            return
        
        self.log(f"📝 Génération d'un texte de ~{self.word_count.get()} mots...")
        
        try:
            words_list = ", ".join(self.selected_words)
            target_words = self.word_count.get()
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"""Écris un texte en allemand de {target_words} mots (±10%) sur le thème "{self.theme.get()}".
Utilise TOUS ces mots : {words_list}
Texte de niveau B1-B2, cohérent. UNIQUEMENT le texte en allemand, sans titre."""}],
                max_tokens=4096
            )
            
            german_text = response.choices[0].message.content.strip()
            actual_words = len(german_text.split())
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            theme_slug = self.theme.get().lower().replace(' ', '_')[:20]
            
            txt_filename = f"texte_{theme_slug}_{timestamp}.txt"
            md_filename = f"texte_{theme_slug}_{timestamp}.md"
            mp3_filename = f"audio_{theme_slug}_{timestamp}.mp3"
            
            with open(txt_filename, 'w', encoding='utf-8') as f:
                f.write(german_text)
            
            with open(md_filename, 'w', encoding='utf-8') as f:
                f.write(f"# Compréhension orale : {self.theme.get()}\n\n")
                f.write(f"**Nombre de mots** : {actual_words}\n\n")
                f.write("## Vocabulaire\n\n")
                for german, french in self.vocabulary:
                    if german in self.selected_words:
                        f.write(f"- **{german}** — {french}\n")
                f.write(f"\n## Texte\n\n{german_text}\n")
            
            self.log("🎤 Génération de l'audio...")
            asyncio.run(self.generate_audio(german_text, mp3_filename))
            
            self.log(f"✅ Terminé ! {actual_words} mots")
            self.log(f"📄 {md_filename}")
            self.log(f"🎧 {mp3_filename}")
            
            messagebox.showinfo("Succès !", 
                              f"✅ Génération terminée !\n\n"
                              f"📄 Texte : {md_filename}\n"
                              f"🎧 Audio : {mp3_filename}\n"
                              f"📊 {actual_words} mots")
        
        except Exception as e:
            self.log(f"❌ Erreur : {str(e)}")
            messagebox.showerror("Erreur", str(e))
    
    async def generate_audio(self, text, filename):
        communicate = edge_tts.Communicate(text=text, voice="de-DE-KatjaNeural", rate="-5%")
        await communicate.save(filename)


def main():
    root = tk.Tk()
    
    # Forcer le mode clair (désactiver le mode sombre)
    try:
        root.tk.call("set", "::tk::mac::useCompatibilityMetrics", "0")
        root.tk.call("set", "::tk::mac::CGAntialiasLimit", "2")
    except:
        pass
    
    # Configuration spéciale pour macOS
    root.configure(bg='#F0F0F0')
    root.tk.call('tk', 'scaling', 2.0)
    root.update_idletasks()
    
    app = ComprehensionOraleApp(root)
    
    root.update()
    root.lift()
    root.attributes('-topmost', True)
    root.after(100, lambda: root.attributes('-topmost', False))
    
    root.mainloop()


if __name__ == "__main__":
    main()
