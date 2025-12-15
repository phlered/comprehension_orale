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
        self.language = tk.StringVar(value="allemand")  # Choix de la langue
        self.word_count = tk.IntVar(value=300)
        self.speech_rate = tk.IntVar(value=-5)  # Vitesse de -30% à 0%
        self.language_level = tk.StringVar(value="B1")  # Niveau de langue
        self.voice_gender = tk.StringVar(value="femme")  # Voix homme/femme
        self.vocabulary = []
        
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        
        self.create_ui()
    
    def create_ui(self):
        # Frame principal
        main = tk.Frame(self.root, padx=20, pady=20)
        main.pack(fill=tk.BOTH, expand=True)
        
        # ÉTAPE 1
        tk.Label(main, text="ÉTAPE 1 : Choisissez la langue et le thème", font=("Arial", 14, "bold")).pack(pady=5)
        
        f1 = tk.Frame(main)
        f1.pack(pady=10)
        
        tk.Label(f1, text="Langue :").pack(side=tk.LEFT, padx=5)
        lang_menu = tk.OptionMenu(f1, self.language, "anglais", "allemand", "espagnol", "hollandais", "coréen")
        lang_menu.config(width=10, font=("Arial", 11))
        lang_menu.pack(side=tk.LEFT, padx=5)
        
        tk.Label(f1, text="Thème :").pack(side=tk.LEFT, padx=5)
        tk.Entry(f1, textvariable=self.theme, width=30, font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        
        # ÉTAPE 2 (ancienne étape 3)
        tk.Label(main, text="ÉTAPE 2 : Générer texte, vocabulaire et audio", font=("Arial", 14, "bold")).pack(pady=10)
        
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
        
        tk.Button(main, text="🚀 GÉNÉRER TOUT 🚀", 
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
    
    def generate_all(self):
        theme = self.theme.get().strip()
        
        if not theme:
            messagebox.showwarning("Erreur", "Entrez un thème !")
            return
        
        if not self.client:
            messagebox.showerror("Erreur", "Clé API manquante !")
            return
        
        level = self.language_level.get()
        langue = self.language.get()
        # Descriptions des niveaux pour le prompt
        level_descriptions = {
            "A1": "très simple avec phrases courtes et vocabulaire basique",
            "A2": "simple avec phrases simples et vocabulaire courant",
            "B1": "intermédiaire avec phrases variées et vocabulaire standard",
            "B2": "avancé avec phrases complexes et vocabulaire riche",
            "C1": "très avancé avec structures sophistiquées et vocabulaire étendu",
            "C2": "niveau natif avec nuances linguistiques et expressions idiomatiques"
        }
        # Langue cible pour le prompt
        langue_prompt = {
            "allemand": "en allemand",
            "anglais": "en anglais",
            "espagnol": "en espagnol",
            "hollandais": "en néerlandais",
            "coréen": "en coréen"
        }
        self.log(f"📝 Génération texte ({self.word_count.get()} mots) - Niveau {level} - Langue : {langue} ...")
        try:
            # Générer le texte
            prompt = f"""Écris un texte {langue_prompt.get(langue, 'dans la langue choisie')} de niveau {level} ({level_descriptions[level]}) d'environ {self.word_count.get()} mots sur le thème : {theme}

Le texte doit être naturel, intéressant et adapté au niveau {level}."""
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096
            )
            text = response.choices[0].message.content.strip()
            words = len(text.split())
            vocab_count = max(1, int(words * 0.1 + 0.5))
            self.log(f"📚 Extraction du vocabulaire ({vocab_count} mots)...")
            # Prompt vocabulaire adapté à la langue
            vocab_prompt = f"""Analyse ce texte {langue_prompt.get(langue, 'dans la langue choisie')} et extrais les {vocab_count} mots les plus importants et utiles pour un apprenant.

Pour chaque mot :
- Choisis des mots clés représentatifs du contenu sur le thème \"{theme}\"
- Privilégie les noms, verbes et adjectifs importants
"""
            # Ajout consigne pour l'allemand
            if langue == "allemand":
                vocab_prompt += "- Pour les noms allemands, INDIQUE TOUJOURS l'article défini (der/die/das) devant le mot\n"
            vocab_prompt += "\nFormat strict (un mot par ligne) :\n"
            if langue == "allemand":
                vocab_prompt += "article mot_allemand | traduction_française\n\nExemple de format :\nder Frau | la femme\n"
            else:
                vocab_prompt += "mot_langue | traduction_française\n\nExemple de format :\ncat | le chat\n"
            vocab_prompt += f"\nTEXTE :\n{text}\n\nDonne uniquement la liste des {vocab_count} mots au format demandé, sans numérotation, sans commentaire."
            vocab_response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": vocab_prompt}],
                max_tokens=1024
            )
            
            # Parser le vocabulaire
            self.vocabulary = []
            for line in vocab_response.choices[0].message.content.strip().split('\n'):
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        de = parts[0].strip().strip('*').strip('-').strip()
                        fr = parts[1].strip().strip('*').strip('-').strip()
                        if de and fr:
                            self.vocabulary.append((de, fr))
            
            self.log(f"✅ {len(self.vocabulary)} mots de vocabulaire extraits")
            
            # Sauvegarder les fichiers
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            theme_safe = theme.lower().replace(' ', '_')[:15]
            
            txt_file = f"texte_{theme_safe}_{ts}.txt"
            mp3_file = f"audio_{theme_safe}_{ts}.mp3"
            
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(text)
            
            rate_str = f"{self.speech_rate.get()}%"
            voice_label = "👩 Femme" if self.voice_gender.get() == "femme" else "👨 Homme"
            self.log(f"🎤 Génération audio MP3 (voix: {voice_label}, vitesse: {rate_str})...")
            asyncio.run(self.gen_audio(text, mp3_file))
            
            self.log("📄 Génération du PDF...")
            pdf_file = self.generate_pdf(txt_file, mp3_file, level, text)
            
            self.log(f"✅ TERMINÉ ! {words} mots")
            self.log(f"📄 {txt_file}")
            self.log(f"🎧 {mp3_file} (niveau: {level}, voix: {voice_label}, vitesse: {rate_str})")
            if pdf_file:
                self.log(f"📕 {pdf_file}")
            
            msg = f"Fichiers créés :\n\n📄 {txt_file}\n🎧 {mp3_file}"
            if pdf_file:
                msg += f"\n📕 {pdf_file}"
            msg += f"\n\nNiveau : {level}\nVoix : {voice_label}\nVitesse audio : {rate_str}"
            msg += f"\nVocabulaire : {len(self.vocabulary)} mots extraits automatiquement"
            
            messagebox.showinfo("Succès", msg)
        
        except Exception as e:
            self.log(f"❌ Erreur: {e}")
            messagebox.showerror("Erreur", str(e))
    
    async def gen_audio(self, text, file):
        # Sélection de la voix selon la langue et le genre choisi
        langue = self.language.get()
        genre = self.voice_gender.get()
        # Dictionnaire voix edge-tts
        voices = {
            "allemand": {
                "femme": "de-DE-KatjaNeural",
                "homme": "de-DE-ConradNeural"
            },
            "anglais": {
                "femme": "en-GB-LibbyNeural",
                "homme": "en-GB-RyanNeural"
            },
            "espagnol": {
                "femme": "es-ES-ElviraNeural",
                "homme": "es-ES-AlvaroNeural"
            },
            "hollandais": {
                "femme": "nl-NL-FennaNeural",
                "homme": "nl-NL-CoenNeural"
            },
            "coréen": {
                "femme": "ko-KR-SunHiNeural",
                "homme": "ko-KR-InJoonNeural"
            }
        }
        voice = voices.get(langue, {}).get(genre, "de-DE-KatjaNeural")
        rate_str = f"{self.speech_rate.get()}%"
        comm = edge_tts.Communicate(text=text, voice=voice, rate=rate_str)
        await comm.save(file)
    
    def generate_pdf(self, txt_file, mp3_file, level, text):
        """Génère un PDF avec vocabulaire, texte et QR code pour l'audio"""
        try:
            pdf_file = txt_file.replace('.txt', '.pdf')
            qr_img_path = mp3_file.replace('.mp3', '_qr.png')
            qr = qrcode.QRCode(version=1, box_size=10, border=2)
            github_url = f"https://github.com/phlered/comprehension_orale/raw/master/documents/tornades/{os.path.basename(mp3_file)}"
            qr.add_data(github_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_img_path)
            c = canvas.Canvas(pdf_file, pagesize=A4)
            width, height = A4
            langue = self.language.get()
            titres = {
                "allemand": {
                    "titre": "Compréhension Orale - Allemand",
                    "vocab": "Wortschatz (Vocabulaire)",
                    "texte": "Text (Texte)"
                },
                "anglais": {
                    "titre": "Listening Comprehension - English",
                    "vocab": "Vocabulary",
                    "texte": "Text"
                },
                "espagnol": {
                    "titre": "Comprensión Oral - Español",
                    "vocab": "Vocabulario",
                    "texte": "Texto"
                },
                "hollandais": {
                    "titre": "Luistervaardigheid - Nederlands",
                    "vocab": "Woordenschat",
                    "texte": "Tekst"
                },
                "coréen": {
                    "titre": "듣기 이해 - 한국어",
                    "vocab": "어휘",
                    "texte": "텍스트"
                }
            }
            labels = titres.get(langue, titres["allemand"])
            # Police pour le coréen
            if langue == "coréen":
                # Chemin de la police NanumGothic (à placer dans le dossier du script ou préciser le chemin absolu)
                font_path = os.path.join(os.path.dirname(__file__), "NanumGothic.ttf")
                if os.path.exists(font_path):
                    try:
                        pdfmetrics.registerFont(TTFont("NanumGothic", font_path))
                        font_main = "NanumGothic"
                    except Exception as e:
                        self.log(f"Erreur chargement police NanumGothic: {e}")
                        font_main = "Helvetica"
                else:
                    self.log("Police NanumGothic.ttf non trouvée, fallback Helvetica.")
                    font_main = "Helvetica"
            else:
                font_main = "Helvetica"
            # Titre principal
            c.setFont(font_main + "-Bold" if font_main == "Helvetica" else font_main, 18)
            c.drawString(2*cm, height - 2*cm, labels["titre"])
            # Thème et niveau
            c.setFont(font_main, 12)
            c.drawString(2*cm, height - 3*cm, f"Thème : {self.theme.get()}")
            c.drawString(2*cm, height - 3.7*cm, f"Niveau : {level}")
            # Section vocabulaire
            y = height - 5*cm
            c.setFont(font_main + "-Bold" if font_main == "Helvetica" else font_main, 14)
            c.drawString(2*cm, y, labels["vocab"])
            y -= 0.7*cm
            c.setFont(font_main, 10)
            for de, fr in self.vocabulary:
                col1_x = 2*cm
                col2_x = 11*cm
                c.drawString(col1_x, y, f"• {de}")
                c.drawString(col2_x, y, f"→ {fr}")
                y -= 0.5*cm
                if y < 10*cm:
                    c.showPage()
                    y = height - 2*cm
                    c.setFont(font_main, 10)
            # Section texte
            if y < 15*cm:
                c.showPage()
                y = height - 2*cm
            else:
                y -= 1*cm
            c.setFont(font_main + "-Bold" if font_main == "Helvetica" else font_main, 14)
            c.drawString(2*cm, y, labels["texte"])
            y -= 0.7*cm
            c.setFont(font_main, 11)
            max_width = width - 4*cm
            words = text.split()
            lines = []
            current_line = []
            for word in words:
                test_line = ' '.join(current_line + [word])
                if c.stringWidth(test_line, font_main, 11) < max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
            for line in lines:
                if y < 3*cm:
                    c.showPage()
                    y = height - 2*cm
                    c.setFont(font_main, 11)
                c.drawString(2*cm, y, line)
                y -= 0.6*cm
            # QR Code sur nouvelle page
            c.showPage()
            c.setFont(font_main + "-Bold" if font_main == "Helvetica" else font_main, 14)
            c.drawString(2*cm, height - 2*cm, "Audio MP3")
            c.setFont(font_main, 11)
            c.drawString(2*cm, height - 3*cm, "Scannez le QR code pour accéder à l'audio :")
            qr_img = ImageReader(qr_img_path)
            c.drawImage(qr_img, 2*cm, height - 12*cm, width=8*cm, height=8*cm)
            c.setFont(font_main, 9)
            c.drawString(2*cm, height - 13*cm, f"Fichier : {os.path.basename(mp3_file)}")
            c.save()
            os.remove(qr_img_path)
            return pdf_file
        except Exception as e:
            self.log(f"❌ Erreur PDF: {e}")
            return None


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
