#!/usr/bin/env python3
"""
Version minimaliste - force mode clair
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
from openai import OpenAI
import edge_tts
import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
import qrcode
from pathlib import Path

load_dotenv()

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Compréhension Orale Allemand")
        
        # FORCE MODE CLAIR
        try:
            self.root.tk.call('tk', 'scaling', 2.0)
        except:
            pass
        
        self.theme = tk.StringVar()
        self.word_count = tk.IntVar(value=300)
        self.speech_rate = tk.IntVar(value=-5)  # Vitesse de -30% à 0%
        self.language_level = tk.StringVar(value="B1")  # Niveau de langue
        self.voice_gender = tk.StringVar(value="femme")  # Voix homme/femme
        self.vocabulary = []
        self.checkboxes = {}
        
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        
        self.create_ui()
    
    def create_ui(self):
        # Frame principal
        main = tk.Frame(self.root, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # ÉTAPE 1
        tk.Label(main, text="ÉTAPE 1 : Entrez un thème", font=("Arial", 14, "bold")).pack(pady=5)
        
        f1 = tk.Frame(main)
        f1.pack(pady=10)
        
        tk.Label(f1, text="Thème :").pack(side=tk.LEFT, padx=5)
        tk.Entry(f1, textvariable=self.theme, width=30, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        tk.Button(f1, text="Générer vocabulaire", command=self.generate_vocab).pack(side=tk.LEFT, padx=5)
        tk.Button(f1, text="Saisie manuelle", command=self.manual_mode).pack(side=tk.LEFT, padx=5)
        tk.Button(f1, text="➕ Ajouter mots", command=self.add_words).pack(side=tk.LEFT, padx=5)
        
        # ÉTAPE 2
        tk.Label(main, text="ÉTAPE 2 : Sélectionnez les mots", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.words_frame = tk.Frame(main, relief=tk.SUNKEN, bd=1)
        self.words_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # ÉTAPE 3
        tk.Label(main, text="ÉTAPE 3 : Générer texte et audio", font=("Arial", 14, "bold")).pack(pady=10)
        
        f3 = tk.Frame(main)
        f3.pack(pady=5)
        
        # Niveau de langue
        tk.Label(f3, text="Niveau :").pack(side=tk.LEFT, padx=5)
        level_menu = tk.OptionMenu(f3, self.language_level, "A1", "A2", "B1", "B2", "C1", "C2")
        level_menu.config(width=4, font=("Arial", 11))
        level_menu.pack(side=tk.LEFT, padx=5)
        
        # Bouton info niveau
        info_btn = tk.Button(f3, text="ℹ️", command=self.show_level_info, 
                            font=("Arial", 10), padx=5, pady=0)
        info_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Label(f3, text="Mots :").pack(side=tk.LEFT, padx=(15, 5))
        tk.Spinbox(f3, from_=100, to=1000, increment=50, textvariable=self.word_count, width=8).pack(side=tk.LEFT, padx=5)
        
        # Choix de la voix
        tk.Label(f3, text="Voix :").pack(side=tk.LEFT, padx=(15, 5))
        voice_menu = tk.OptionMenu(f3, self.voice_gender, "femme", "homme")
        voice_menu.config(width=7, font=("Arial", 11))
        voice_menu.pack(side=tk.LEFT, padx=5)
        
        # Contrôle vitesse audio
        tk.Label(f3, text="Vitesse audio :").pack(side=tk.LEFT, padx=(20, 5))
        speed_frame = tk.Frame(f3)
        speed_frame.pack(side=tk.LEFT, padx=5)
        
        self.speed_label = tk.Label(speed_frame, text=f"{self.speech_rate.get()}%", width=5, font=("Arial", 10, "bold"))
        self.speed_label.pack(side=tk.TOP)
        
        speed_scale = tk.Scale(speed_frame, from_=0, to=-30, variable=self.speech_rate, 
                              orient=tk.HORIZONTAL, length=150, showvalue=0,
                              command=self.update_speed_label)
        speed_scale.pack(side=tk.TOP)
        
        tk.Label(speed_frame, text="(0% = normal, -30% = plus lent)", font=("Arial", 8, "italic")).pack(side=tk.TOP)
        
        tk.Button(main, text="🚀 GÉNÉRER TEXTE ET AUDIO MP3 🚀", 
                 command=self.generate_all, font=("Arial", 14, "bold"),
                 bg="darkgreen", fg="white", padx=20, pady=10).pack(pady=15)
        
        # Log
        tk.Label(main, text="Statut :").pack(pady=5)
        self.log_text = scrolledtext.ScrolledText(main, height=6, font=("Courier", 10))
        self.log_text.pack(fill=tk.X, pady=5)
        
        self.log("✅ Prêt ! Entrez un thème ci-dessus.")
    
    def log(self, msg):
        self.log_text.insert(tk.END, f"{msg}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def update_speed_label(self, value):
        """Met à jour l'affichage de la vitesse"""
        self.speed_label.config(text=f"{int(float(value))}%")
    
    def show_level_info(self):
        """Affiche les informations sur les niveaux de langue"""
        info = """Niveaux du CECRL (Cadre Européen) :

📗 A1 - Débutant
   Phrases très simples, vocabulaire de base

📘 A2 - Élémentaire  
   Phrases simples, situations quotidiennes

📙 B1 - Intermédiaire (recommandé)
   Textes clairs sur sujets familiers

📕 B2 - Intermédiaire avancé
   Textes complexes, idées abstraites

📔 C1 - Avancé
   Textes sophistiqués, nuances subtiles

📓 C2 - Maîtrise
   Niveau natif, expressions idiomatiques"""
        
        messagebox.showinfo("Niveaux de langue", info)
    
    def generate_vocab(self):
        theme = self.theme.get().strip()
        if not theme:
            messagebox.showwarning("Erreur", "Entrez un thème !")
            return
        
        if not self.client:
            messagebox.showerror("Erreur", "Clé API manquante !")
            return
        
        self.log(f"🤖 Génération vocabulaire : {theme}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": f"Génère une liste de 15 mots allemands sur le thème : {theme}\n\nFormat strict (un par ligne):\nmot_allemand | traduction_française"
                }],
                max_tokens=1024
            )
            
            self.vocabulary = []
            for line in response.choices[0].message.content.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        de = parts[0].strip().strip('*').strip('-').strip()
                        fr = parts[1].strip().strip('*').strip('-').strip()
                        if de and fr:
                            self.vocabulary.append((de, fr))
            
            self.display_words()
            self.log(f"✅ {len(self.vocabulary)} mots générés")
        
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", str(e))
    
    def manual_mode(self):
        """Ouvre une fenêtre pour saisir des mots manuellement"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Saisie manuelle de vocabulaire")
        dialog.geometry("500x450")
        
        tk.Label(dialog, text="Entrez vos mots allemands", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(dialog, text="Format: mot_allemand (traduction auto) OU mot_allemand | traduction", 
                font=("Arial", 10, "italic")).pack(pady=5)
        
        tk.Label(dialog, text="Un mot par ligne", 
                font=("Arial", 9, "italic")).pack(pady=2)
        
        # Zone de texte pour saisir les mots
        text_area = tk.Text(dialog, height=15, width=50, font=("Arial", 11))
        text_area.pack(padx=10, pady=10)
        
        # Zone vide - pas d'exemple pré-rempli
        text_area.focus_set()
        
        def save_words():
            content = text_area.get("1.0", tk.END).strip()
            if not content:
                messagebox.showwarning("Erreur", "Entrez au moins un mot !")
                return
            
            dialog.destroy()
            self.log("🔄 Traitement des mots...")
            
            new_vocab = []
            words_to_translate = []
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        de = parts[0].strip()
                        fr = parts[1].strip()
                        if de and fr:
                            new_vocab.append((de, fr))
                else:
                    # Juste le mot allemand, traduction à faire
                    de = line.strip()
                    if de:
                        words_to_translate.append(de)
            
            # Traduire les mots sans traduction
            if words_to_translate and self.client:
                self.log(f"🤖 Traduction de {len(words_to_translate)} mot(s)...")
                try:
                    words_list = "\n".join([f"- {w}" for w in words_to_translate])
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "user",
                            "content": f"Traduis ces mots allemands en français. Format strict (un par ligne): mot_allemand | traduction\n\n{words_list}"
                        }],
                        max_tokens=1024
                    )
                    
                    for line in response.choices[0].message.content.strip().split('\n'):
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 2:
                                de = parts[0].strip().strip('*').strip('-').strip()
                                fr = parts[1].strip().strip('*').strip('-').strip()
                                if de and fr:
                                    new_vocab.append((de, fr))
                
                except Exception as e:
                    self.log(f"❌ Erreur traduction: {e}")
                    # Ajouter quand même les mots sans traduction
                    for w in words_to_translate:
                        new_vocab.append((w, "???"))
            elif words_to_translate:
                # Pas d'API, ajouter sans traduction
                for w in words_to_translate:
                    new_vocab.append((w, "???"))
            
            if new_vocab:
                self.vocabulary = new_vocab
                self.display_words()
                self.log(f"✏️ Mode manuel - {len(new_vocab)} mots ajoutés")
            else:
                messagebox.showwarning("Erreur", "Aucun mot valide trouvé")
        
        tk.Button(dialog, text="Valider et traduire", command=save_words, 
                 font=("Arial", 12, "bold"), bg="green", fg="white", 
                 padx=20, pady=5).pack(pady=10)
        
        tk.Button(dialog, text="Annuler", command=dialog.destroy,
                 font=("Arial", 10), padx=20, pady=5).pack()
    
    def add_words(self):
        """Ajoute des mots à la liste existante sans écraser"""
        if not self.vocabulary:
            messagebox.showinfo("Info", "Aucun vocabulaire existant. Utilisez 'Saisie manuelle' ou 'Générer vocabulaire' d'abord.")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Ajouter des mots")
        dialog.geometry("500x450")
        
        tk.Label(dialog, text="Ajouter des mots supplémentaires", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(dialog, text="Format: mot_allemand (traduction auto) OU mot_allemand | traduction", 
                font=("Arial", 10, "italic")).pack(pady=5)
        
        tk.Label(dialog, text="Un mot par ligne", 
                font=("Arial", 9, "italic")).pack(pady=2)
        
        # Zone de texte
        text_area = tk.Text(dialog, height=15, width=50, font=("Arial", 11))
        text_area.pack(padx=10, pady=10)
        
        def save_additions():
            content = text_area.get("1.0", tk.END).strip()
            if not content:
                dialog.destroy()
                return
            
            dialog.destroy()
            self.log("🔄 Traitement des nouveaux mots...")
            
            new_words = []
            words_to_translate = []
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        de = parts[0].strip()
                        fr = parts[1].strip()
                        if de and fr and not any(word[0] == de for word in self.vocabulary):
                            new_words.append((de, fr))
                else:
                    # Juste le mot allemand
                    de = line.strip()
                    if de and not any(word[0] == de for word in self.vocabulary):
                        words_to_translate.append(de)
            
            # Traduire les mots sans traduction
            if words_to_translate and self.client:
                self.log(f"🤖 Traduction de {len(words_to_translate)} mot(s)...")
                try:
                    words_list = "\n".join([f"- {w}" for w in words_to_translate])
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{
                            "role": "user",
                            "content": f"Traduis ces mots allemands en français. Format strict (un par ligne): mot_allemand | traduction\n\n{words_list}"
                        }],
                        max_tokens=1024
                    )
                    
                    for line in response.choices[0].message.content.strip().split('\n'):
                        if '|' in line:
                            parts = line.split('|')
                            if len(parts) >= 2:
                                de = parts[0].strip().strip('*').strip('-').strip()
                                fr = parts[1].strip().strip('*').strip('-').strip()
                                if de and fr:
                                    new_words.append((de, fr))
                
                except Exception as e:
                    self.log(f"❌ Erreur traduction: {e}")
                    for w in words_to_translate:
                        new_words.append((w, "???"))
            elif words_to_translate:
                for w in words_to_translate:
                    new_words.append((w, "???"))
            
            if new_words:
                self.vocabulary.extend(new_words)
                self.display_words()
                self.log(f"✅ {len(new_words)} mot(s) ajouté(s) (total: {len(self.vocabulary)})")
            else:
                messagebox.showinfo("Info", "Aucun nouveau mot ajouté (doublons ignorés)")
        
        tk.Button(dialog, text="Ajouter et traduire", command=save_additions, 
                 font=("Arial", 12, "bold"), bg="blue", fg="white", 
                 padx=20, pady=5).pack(pady=10)
        
        tk.Button(dialog, text="Annuler", command=dialog.destroy,
                 font=("Arial", 10), padx=20, pady=5).pack()
    
    def display_words(self):
        for w in self.words_frame.winfo_children():
            w.destroy()
        
        self.checkboxes = {}
        
        for i, (de, fr) in enumerate(self.vocabulary):
            var = tk.BooleanVar(value=True)
            self.checkboxes[de] = var
            
            tk.Checkbutton(
                self.words_frame,
                text=f"{de}  →  {fr}",
                variable=var,
                font=("Arial", 11)
            ).grid(row=i, column=0, sticky=tk.W, padx=10, pady=2)
    
    def generate_all(self):
        selected = [de for de, var in self.checkboxes.items() if var.get()]
        
        if len(selected) < 2:
            messagebox.showwarning("Erreur", "Sélectionnez au moins 2 mots !")
            return
        
        if not self.client:
            messagebox.showerror("Erreur", "Clé API manquante !")
            return
        
        self.log(f"📝 Génération texte ({self.word_count.get()} mots)...")
        
        level = self.language_level.get()
        
        # Descriptions des niveaux pour le prompt
        level_descriptions = {
            "A1": "très simple avec phrases courtes et vocabulaire basique",
            "A2": "simple avec phrases simples et vocabulaire courant",
            "B1": "intermédiaire avec phrases variées et vocabulaire standard",
            "B2": "avancé avec phrases complexes et vocabulaire riche",
            "C1": "très avancé avec structures sophistiquées et vocabulaire étendu",
            "C2": "niveau natif avec nuances linguistiques et expressions idiomatiques"
        }
        
        try:
            prompt = f"""Écris un texte en allemand de niveau {level} ({level_descriptions[level]}) d'environ {self.word_count.get()} mots sur le thème : {self.theme.get()}

Utilise ces mots : {', '.join(selected)}

Le texte doit être naturel, intéressant et adapté au niveau {level}."""
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
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
            
            rate_str = f"{self.speech_rate.get()}%"
            voice_label = "👩 Femme" if self.voice_gender.get() == "femme" else "👨 Homme"
            self.log(f"🎤 Génération audio MP3 (voix: {voice_label}, vitesse: {rate_str})...")
            asyncio.run(self.gen_audio(text, mp3_file))
            
            self.log("📄 Génération du PDF...")
            pdf_file = self.generate_pdf(txt_file, mp3_file, level)
            
            self.log(f"✅ TERMINÉ ! {words} mots")
            self.log(f"📄 {txt_file}")
            self.log(f"🎧 {mp3_file} (niveau: {level}, voix: {voice_label}, vitesse: {rate_str})")
            if pdf_file:
                self.log(f"📕 {pdf_file}")
            
            msg = f"Fichiers créés :\n\n📄 {txt_file}\n🎧 {mp3_file}"
            if pdf_file:
                msg += f"\n📕 {pdf_file}"
            msg += f"\n\nNiveau : {level}\nVoix : {voice_label}\nVitesse audio : {rate_str}"
            
            messagebox.showinfo("Succès", msg)
        
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", str(e))
    
    async def gen_audio(self, text, file):
        # Sélection de la voix selon le genre choisi
        voices = {
            "femme": "de-DE-KatjaNeural",      # Voix féminine allemande
            "homme": "de-DE-ConradNeural"      # Voix masculine allemande
        }
        
        voice = voices.get(self.voice_gender.get(), "de-DE-KatjaNeural")
        rate_str = f"{self.speech_rate.get()}%"
        
        comm = edge_tts.Communicate(text=text, voice=voice, rate=rate_str)
        await comm.save(file)
    
    def generate_pdf(self, txt_file, mp3_file, level):
        """Génère un PDF avec vocabulaire, texte et QR code pour l'audio"""
        try:
            # Créer le nom du fichier PDF
            pdf_file = txt_file.replace('.txt', '.pdf')
            
            # Lire le texte
            with open(txt_file, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Créer le QR code pour l'audio sur GitHub
            qr_img_path = mp3_file.replace('.mp3', '_qr.png')
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            # URL publique du MP3 sur GitHub
            github_url = f"https://github.com/phlered/comprehension_orale/raw/master/documents/tornades/{os.path.basename(mp3_file)}"
            qr.add_data(github_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_img_path)
            
            # Créer le PDF
            c = canvas.Canvas(pdf_file, pagesize=A4)
            width, height = A4
            
            # Titre
            c.setFont("Helvetica-Bold", 18)
            c.drawString(2*cm, height - 2*cm, "Compréhension Orale - Allemand")
            
            # Thème et niveau
            c.setFont("Helvetica", 12)
            c.drawString(2*cm, height - 3*cm, f"Thème : {self.theme.get()}")
            c.drawString(2*cm, height - 3.7*cm, f"Niveau : {level}")
            
            # Section Wortschatz
            y = height - 5*cm
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y, "Wortschatz (Vocabulaire)")
            
            # Liste des mots en 2 colonnes
            y -= 0.7*cm
            c.setFont("Helvetica", 10)
            
            for de, var in self.checkboxes.items():
                if not var.get():
                    continue
                
                col1_x = 2*cm
                col2_x = 11*cm
                
                # Trouver la traduction
                translation = next((fr for d, fr in self.vocabulary if d == de), "")
                
                c.drawString(col1_x, y, f"• {de}")
                c.drawString(col2_x, y, f"→ {translation}")
                y -= 0.5*cm
                
                if y < 10*cm:  # Si on arrive en bas, nouvelle page
                    c.showPage()
                    y = height - 2*cm
                    c.setFont("Helvetica", 10)
            
            # Section Texte
            if y < 15*cm:
                c.showPage()
                y = height - 2*cm
            else:
                y -= 1*cm
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, y, "Text (Texte)")
            
            y -= 0.7*cm
            c.setFont("Helvetica", 11)
            
            # Découper le texte en lignes
            max_width = width - 4*cm
            words = text.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                if c.stringWidth(test_line, "Helvetica", 11) < max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            
            # Écrire les lignes
            for line in lines:
                if y < 3*cm:
                    c.showPage()
                    y = height - 2*cm
                    c.setFont("Helvetica", 11)
                c.drawString(2*cm, y, line)
                y -= 0.6*cm
            
            # QR Code sur nouvelle page
            c.showPage()
            c.setFont("Helvetica-Bold", 14)
            c.drawString(2*cm, height - 2*cm, "Audio MP3")
            
            c.setFont("Helvetica", 11)
            c.drawString(2*cm, height - 3*cm, "Scannez le QR code pour accéder à l'audio :")
            
            # Insérer le QR code
            qr_img = ImageReader(qr_img_path)
            c.drawImage(qr_img, 2*cm, height - 12*cm, width=8*cm, height=8*cm)
            
            c.setFont("Helvetica", 9)
            c.drawString(2*cm, height - 13*cm, f"Fichier : {os.path.basename(mp3_file)}")
            
            # Sauvegarder
            c.save()
            
            # Supprimer l'image QR temporaire
            os.remove(qr_img_path)
            
            return pdf_file
            
        except Exception as e:
            self.log(f"❌ Erreur PDF: {e}")
            return None


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
