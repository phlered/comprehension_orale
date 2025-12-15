#!/usr/bin/env python3
"""
Version ultra-simple avec contrastes maximum pour mode sombre
"""

import tkinter as tk
from tkinter import messagebox
from openai import OpenAI
import edge_tts
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class SimpleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur Compréhension Orale Allemand")
        self.root.geometry("800x600")
        self.root.configure(bg='white')
        
        self.theme = tk.StringVar()
        self.word_count = tk.IntVar(value=300)
        self.vocabulary = []
        self.checkboxes = {}
        
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        
        self.create_ui()
    
    def create_ui(self):
        # TOUT EN BLANC
        main = tk.Frame(self.root, bg='white', padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # TITRE TRÈS VISIBLE
        tk.Label(main, text="GÉNÉRATEUR DE COMPRÉHENSION ORALE", 
                font=("Arial", 20, "bold"), bg='white', fg='blue').pack(pady=10)
        
        tk.Label(main, text="Allemand - OpenAI", 
                font=("Arial", 14), bg='white', fg='black').pack(pady=5)
        
        # === ÉTAPE 1 ===
        tk.Label(main, text="━" * 60, bg='white', fg='black').pack(pady=5)
        tk.Label(main, text="ÉTAPE 1 : THÈME", 
                font=("Arial", 16, "bold"), bg='white', fg='red').pack(pady=5)
        
        frame1 = tk.Frame(main, bg='white')
        frame1.pack(pady=10)
        
        tk.Label(frame1, text="Entrez un thème :", 
                font=("Arial", 14), bg='white', fg='black').pack(side=tk.LEFT, padx=5)
        
        entry = tk.Entry(frame1, textvariable=self.theme, width=30, 
                        font=("Arial", 14), bg='yellow', fg='black', 
                        insertbackground='black', relief='solid', bd=2)
        entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame1, text="GÉNÉRER VOCABULAIRE", 
                 command=self.generate_vocab,
                 font=("Arial", 12, "bold"), bg='green', fg='white',
                 padx=20, pady=10, relief='raised', bd=3).pack(side=tk.LEFT, padx=5)
        
        tk.Button(frame1, text="MODE MANUEL", 
                 command=self.manual_mode,
                 font=("Arial", 12, "bold"), bg='orange', fg='white',
                 padx=20, pady=10, relief='raised', bd=3).pack(side=tk.LEFT, padx=5)
        
        # === ÉTAPE 2 ===
        tk.Label(main, text="━" * 60, bg='white', fg='black').pack(pady=5)
        tk.Label(main, text="ÉTAPE 2 : VOCABULAIRE", 
                font=("Arial", 16, "bold"), bg='white', fg='red').pack(pady=5)
        
        # Frame pour mots avec scroll
        words_container = tk.Frame(main, bg='white', relief='solid', bd=2)
        words_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        canvas = tk.Canvas(words_container, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(words_container, orient="vertical", command=canvas.yview)
        self.words_frame = tk.Frame(canvas, bg='white')
        
        self.words_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.words_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # === ÉTAPE 3 ===
        tk.Label(main, text="━" * 60, bg='white', fg='black').pack(pady=5)
        tk.Label(main, text="ÉTAPE 3 : GÉNÉRATION", 
                font=("Arial", 16, "bold"), bg='white', fg='red').pack(pady=5)
        
        frame3 = tk.Frame(main, bg='white')
        frame3.pack(pady=10)
        
        tk.Label(frame3, text="Nombre de mots :", 
                font=("Arial", 14), bg='white', fg='black').pack(side=tk.LEFT, padx=5)
        
        tk.Spinbox(frame3, from_=100, to=1000, increment=50, 
                  textvariable=self.word_count, width=8, font=("Arial", 14),
                  bg='yellow', fg='black', buttonbackground='yellow',
                  relief='solid', bd=2).pack(side=tk.LEFT, padx=5)
        
        tk.Button(main, text="🚀 GÉNÉRER TEXTE ET AUDIO MP3 🚀", 
                 command=self.generate_all,
                 font=("Arial", 16, "bold"), bg='red', fg='white',
                 padx=30, pady=15, relief='raised', bd=4).pack(pady=15)
        
        # Zone de log
        tk.Label(main, text="STATUT :", 
                font=("Arial", 14, "bold"), bg='white', fg='black').pack(pady=5)
        
        self.log_text = tk.Text(main, height=5, font=("Courier", 11),
                               bg='lightyellow', fg='black', relief='solid', bd=2)
        self.log_text.pack(fill=tk.X, pady=5)
        
        self.log("✅ Application prête !")
        self.log("👉 Entrez un thème dans le champ JAUNE ci-dessus")
    
    def log(self, msg):
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def generate_vocab(self):
        theme = self.theme.get().strip()
        if not theme:
            messagebox.showwarning("Erreur", "Entrez un thème !")
            return
        
        if not self.client:
            messagebox.showerror("Erreur", "Clé API OpenAI manquante !")
            return
        
        self.log(f"🤖 Génération pour : {theme}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"Génère 15 mots allemands sur: {theme}. Format: mot | traduction"}],
                max_tokens=1024
            )
            
            self.vocabulary = []
            for line in response.choices[0].message.content.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        self.vocabulary.append((parts[0].strip(), parts[1].strip()))
            
            self.display_words()
            self.log(f"✅ {len(self.vocabulary)} mots générés !")
        
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", str(e))
    
    def manual_mode(self):
        self.vocabulary = [
            ("das Wetter", "la météo"),
            ("die Sonne", "le soleil"),
            ("der Regen", "la pluie"),
        ]
        self.display_words()
        self.log("✏️ Mode manuel - 3 exemples ajoutés")
    
    def display_words(self):
        for w in self.words_frame.winfo_children():
            w.destroy()
        
        self.checkboxes = {}
        
        for i, (de, fr) in enumerate(self.vocabulary):
            var = tk.BooleanVar(value=True)
            self.checkboxes[de] = var
            
            tk.Checkbutton(
                self.words_frame,
                text=f"  {de}  →  {fr}",
                variable=var,
                font=("Arial", 12),
                bg='white', fg='black',
                selectcolor='lightgreen',
                activebackground='white',
                activeforeground='black'
            ).grid(row=i, column=0, sticky=tk.W, padx=10, pady=3)
    
    def generate_all(self):
        selected = [de for de, var in self.checkboxes.items() if var.get()]
        
        if len(selected) < 5:
            messagebox.showwarning("Erreur", "Sélectionnez au moins 5 mots !")
            return
        
        if not self.client:
            messagebox.showerror("Erreur", "Clé API manquante !")
            return
        
        self.log(f"📝 Génération texte {self.word_count.get()} mots...")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": f"Texte allemand {self.word_count.get()} mots sur {self.theme.get()}. Utilise: {', '.join(selected)}. Niveau B1-B2."}],
                max_tokens=4096
            )
            
            text = response.choices[0].message.content.strip()
            words = len(text.split())
            
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            theme = self.theme.get().lower().replace(' ', '_')[:15]
            
            txt_file = f"texte_{theme}_{ts}.txt"
            mp3_file = f"audio_{theme}_{ts}.mp3"
            
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            self.log("🎤 Génération audio...")
            asyncio.run(self.gen_audio(text, mp3_file))
            
            self.log(f"✅ TERMINÉ ! {words} mots")
            self.log(f"📄 {txt_file}")
            self.log(f"🎧 {mp3_file}")
            
            messagebox.showinfo("Succès !", f"✅ Fichiers créés !\n\n📄 {txt_file}\n🎧 {mp3_file}")
        
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", str(e))
    
    async def gen_audio(self, text, file):
        comm = edge_tts.Communicate(text=text, voice="de-DE-KatjaNeural", rate="-5%")
        await comm.save(file)


def main():
    root = tk.Tk()
    root.configure(bg='white')
    app = SimpleApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
