#!/usr/bin/env python3
"""
Script de génération de ressources pour l'apprentissage des langues avec Google Cloud TTS.
Version alternative à genmp3.py utilisant Google Cloud Text-to-Speech au lieu d'Azure.

Crée un dossier avec texte, audio MP3 (Google Cloud TTS) et vocabulaire en markdown.

Usage:
    python genmp3_google.py -l all -p "Les animaux domestiques" --niveau B1
    python genmp3_google.py -l eng -p "Climate change" --longueur 200 --niveau B2 -g homme
    python genmp3_google.py -l fr -p "La météo" --niveau A2 --vitesse 0.7

Requirements:
    - GOOGLE_APPLICATION_CREDENTIALS pointant vers le fichier de credentials JSON
    - google-cloud-texttospeech installé
"""

import argparse
import os
import subprocess
import random
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LanguageConfig:
    """Configuration pour chaque langue supportée"""
    LANGUAGES = {
        "fr": {
            "code": "fr",
            "display": "Français",
            "label_text": "Texte",
            "label_vocab": "Vocabulaire",
            "description": "en français"
        },
        "eng": {
            "code": "eng",
            "display": "Anglais (UK)",
            "label_text": "Text",
            "label_vocab": "Vocabulary",
            "description": "en anglais"
        },
        "us": {
            "code": "us",
            "display": "Anglais (US)",
            "label_text": "Text",
            "label_vocab": "Vocabulary",
            "description": "en anglais américain"
        },
        "all": {
            "code": "all",
            "display": "Allemand",
            "label_text": "Text",
            "label_vocab": "Wortschatz",
            "description": "en allemand"
        },
        "esp": {
            "code": "esp",
            "display": "Espagnol (Espagne)",
            "label_text": "Texto",
            "label_vocab": "Vocabulario",
            "description": "en espagnol d'Espagne"
        },
        "hisp": {
            "code": "hisp",
            "display": "Espagnol (Amérique du Sud)",
            "label_text": "Texto",
            "label_vocab": "Vocabulario",
            "description": "en espagnol sud-américain"
        },
        "nl": {
            "code": "nl",
            "display": "Néerlandais",
            "label_text": "Tekst",
            "label_vocab": "Woordenschat",
            "description": "en néerlandais"
        },
        "it": {
            "code": "it",
            "display": "Italien",
            "label_text": "Testo",
            "label_vocab": "Vocabolario",
            "description": "en italien"
        },
    }

    @classmethod
    def get_config(cls, code):
        """Retourne la configuration pour une langue donnée"""
        return cls.LANGUAGES.get(code)

    @classmethod
    def list_languages(cls):
        """Liste toutes les langues supportées"""
        return ", ".join([f"{k} ({v['display']})" for k, v in cls.LANGUAGES.items()])


class GeneratorConfig:
    """Configuration pour les niveaux et axes"""
    LEVELS = {
        "A1": "très simple avec phrases courtes et vocabulaire basique",
        "A2": "simple avec phrases simples et vocabulaire courant",
        "B1": "intermédiaire avec phrases variées et vocabulaire standard",
        "B2": "avancé avec phrases complexes et vocabulaire riche",
        "C1": "très avancé avec structures sophistiquées et vocabulaire étendu",
        "C2": "niveau natif avec nuances linguistiques et expressions idiomatiques"
    }


class TextGenerator:
    """Génère le texte avec OpenAI"""

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Clé API OpenAI manquante. Configurez OPENAI_API_KEY.")
        self.client = OpenAI(api_key=api_key)

    def generate(self, langue_code, prompt, longueur, niveau, style=None):
        """Génère un texte selon les paramètres"""
        lang_config = LanguageConfig.get_config(langue_code)
        level_desc = GeneratorConfig.LEVELS.get(niveau, GeneratorConfig.LEVELS["B1"])

        prompt_text = f"""Écris un texte {lang_config['description']} de niveau {niveau} ({level_desc}) d'environ {longueur} mots sur le thème : {prompt}

Le texte doit être naturel, intéressant et adapté au niveau {niveau}."""

        if langue_code == "fr" and niveau == "C2":
            style_label = (style or "sobre").lower()
            if style_label in ["journalistique", "journalistiq", "journal"]:
                style_label = "journalistique"
            elif style_label in ["scientifique", "chercheur", "research"]:
                style_label = "scientifique"
            else:
                style_label = "sobre"

            prompt_text += f"""

Contraintes de style (C2 FR orienté apprentissage par le contenu):
- Registre neutre, informatif et {style_label} (ton factuel, sans emphase ni métaphores).
- Priorité au contenu: faits, chiffres, dates, acteurs, causalité; pas de verbiage.
- Phrases claires (en moyenne 12 à 22 mots), éviter l'empilement de subordonnées.
- Vocabulaire courant privilégié; n'utiliser des termes techniques que si nécessaire et les définir brièvement à la première occurrence.
- Éviter les superlatifs, adverbes d'intensité et tournures inutilement complexes.
- Structurer en paragraphes courts avec transitions explicites; conclure par 1 à 2 phrases récapitulatives.
"""

        print(f"📝 Génération du texte ({longueur} mots, niveau {niveau})...")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=4096
        )
        text = response.choices[0].message.content.strip()
        return text

    def generate_resume(self, prompt):
        """Génère un résumé court du prompt"""
        resume_prompt = f"""Extrait le sujet principal de ce prompt d'apprentissage en 3 à 10 mots maximum.
Prompt: {prompt}
Résumé (3-10 mots):"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": resume_prompt}],
            max_tokens=50,
            temperature=0.3
        )
        resume = response.choices[0].message.content.strip()
        resume = resume.strip('"\'.,;:!? ')
        return resume

    def generate_vocabulary(self, langue_code, text, prompt, niveau):
        """Extrait le vocabulaire du texte"""
        lang_config = LanguageConfig.get_config(langue_code)
        vocab_count = 35

        vocab_prompt = f"""Analyse ce texte {lang_config['description']} et extrais les {vocab_count} mots les plus importants.

Pour chaque mot:
- Choisis des mots clés représentatifs du thème "{prompt}"
- Privilégie les noms, verbes et adjectifs importants
"""

        # Consignes spécifiques par langue
        if langue_code == "all":
            vocab_prompt += "- Pour les noms allemands, INDIQUE l'article défini (der/die/das)\n"
            vocab_prompt += "Format: article mot_allemand | traduction_française\n\nExemple:\nder Frau | la femme\n"
        elif langue_code in ["eng", "us"]:
            vocab_prompt += "- Pour les verbes, indique 'to' avant le verbe\n"
            vocab_prompt += "Format: mot_anglais | traduction_française\n\nExemples:\nto see | voir\nhouse | maison\n"
        elif langue_code in ["esp", "hisp"]:
            vocab_prompt += "- Pour les noms espagnols, INDIQUE l'article défini (el/la)\n"
            vocab_prompt += "Format: article mot_espagnol | traduction_française\n\nExemple:\nla casa | la maison\n"
        elif langue_code == "nl":
            vocab_prompt += "- Pour les noms néerlandais, INDIQUE l'article défini (de/het)\n"
            vocab_prompt += "Format: article mot_néerlandais | traduction_française\n\nExemple:\nde hond | le chien\n"
        elif langue_code == "it":
            vocab_prompt += "- Pour les noms italiens, INDIQUE l'article défini (il/la)\n"
            vocab_prompt += "Format: article mot_italien | traduction_française\n\nExemple:\nla casa | la maison\n"
        else:
            vocab_prompt += "Format: mot_langue | traduction_française\n"

        vocab_prompt += f"\nTEXTE:\n{text}\n\nDonne uniquement la liste des {vocab_count} mots au format demandé, sans numérotation."

        print(f"📚 Extraction du vocabulaire ({vocab_count} mots)...")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": vocab_prompt}],
            max_tokens=1024
        )

        vocabulary = []
        for line in response.choices[0].message.content.strip().split('\n'):
            separator = '→' if '→' in line else '|'
            if separator in line:
                parts = line.split(separator)
                if len(parts) >= 2:
                    word = parts[0].strip().strip('*').strip()
                    translation = parts[1].strip().strip('*').strip()
                    if word and translation:
                        vocabulary.append((word, translation))

        # Trier alphabétiquement
        def sort_key(item):
            word = item[0]
            if langue_code == "all":
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['der', 'die', 'das']:
                    return parts[1].lower()
            elif langue_code in ["eng", "us"]:
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() == 'to':
                    return parts[1].lower()
            elif langue_code in ["esp", "hisp"]:
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['el', 'la', 'los', 'las']:
                    return parts[1].lower()
            elif langue_code == "nl":
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['de', 'het']:
                    return parts[1].lower()
            elif langue_code == "it":
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['il', 'la', 'lo', 'gli', 'le']:
                    return parts[1].lower()
            return word.lower()
        
        vocabulary.sort(key=sort_key)
        return vocabulary


class AudioGeneratorGoogle:
    """Génère l'audio avec md2mp3_google.py (Google Cloud TTS)"""

    @staticmethod
    def generate(markdown_file, langue_code, genre, dossier_sortie, vitesse=0.8, voix=None):
        """Génère le fichier audio MP3 avec md2mp3_google.py
        
        Args:
            markdown_file: Chemin du fichier .md
            langue_code: Code langue
            genre: Genre de voix (femme/homme)
            dossier_sortie: Dossier de sortie
            vitesse: Vitesse de lecture
            voix: Voix spécifique (optionnel)
        """
        script_dir = os.path.dirname(os.path.abspath(__file__))
        md2mp3_path = os.path.join(script_dir, "md2mp3_google.py")
        
        if not os.path.exists(md2mp3_path):
            raise FileNotFoundError(f"md2mp3_google.py non trouvé à {md2mp3_path}")
        
        fichier_mp3 = os.path.join(dossier_sortie, "audio.mp3")
        
        cmd = [
            sys.executable,
            md2mp3_path,
            os.path.abspath(markdown_file),
            "-l", langue_code,
            "-g", genre,
            "-o", fichier_mp3,
            "--vitesse", str(vitesse)
        ]
        
        if voix:
            cmd.extend(["-v", voix])
        
        print(f"🎤 Génération de l'audio avec Google Cloud TTS (langue: {langue_code}, genre: {genre}, vitesse: {vitesse}x)...")
        sys.stdout.flush()
        
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                for line in iter(process.stdout.readline, ''):
                    if line:
                        print(line, end='', flush=True)
                
                returncode = process.wait()
                
                if returncode == 0:
                    if os.path.exists(fichier_mp3):
                        size = os.path.getsize(fichier_mp3)
                        print(f"✅ Audio généré ({size} octets)")
                        sys.stdout.flush()
                    break
                else:
                    raise subprocess.CalledProcessError(returncode, cmd)
                        
            except subprocess.CalledProcessError as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée, nouvelle tentative dans {retry_delay}s...")
                    sys.stdout.flush()
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Erreur après {max_retries} tentatives")
                    sys.stdout.flush()
                    raise
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ Tentative {attempt + 1}/{max_retries} échouée...")
                    time.sleep(retry_delay)
                else:
                    print(f"❌ Erreur: {e}")
                    raise


class OutputGenerator:
    """Génère les fichiers de sortie"""

    @staticmethod
    def slugify(text):
        """Convertit un texte en slug (minuscules, caractères spéciaux remplacés)"""
        # Remplacer les caractères spéciaux
        text = text.lower()
        text = re.sub(r'[àâä]', 'a', text)
        text = re.sub(r'[èéêë]', 'e', text)
        text = re.sub(r'[ìîï]', 'i', text)
        text = re.sub(r'[òôö]', 'o', text)
        text = re.sub(r'[ùûü]', 'u', text)
        text = re.sub(r'[ñ]', 'n', text)
        text = re.sub(r'[ç]', 'c', text)
        text = re.sub(r'[^a-z0-9_\s-]', '', text)
        text = re.sub(r'[\s_-]+', '_', text)
        return text.strip('_')

    @staticmethod
    def create_markdown(
        dossier_sortie,
        texte,
        vocabulaire,
        langue_code,
        prompt,
        resume,
        longueur,
        niveau,
        genre
    ):
        """Crée le fichier markdown avec frontmatter YAML"""
        lang_config = LanguageConfig.get_config(langue_code)
        
        # Frontmatter YAML
        yaml_header = f"""---
langue: {lang_config['display']}
prompt: {prompt}
resume: {resume}
longueur: {longueur}
niveau: {niveau}
genre: {genre}
date_generation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
tts_engine: Google Cloud Text-to-Speech
---

"""
        
        # Section texte
        texte_section = f"""## {lang_config['label_text']}

{texte}

"""
        
        # Section vocabulaire
        vocab_section = f"""## {lang_config['label_vocab']}

"""
        
        for word, translation in vocabulaire:
            vocab_section += f"{word} | {translation}\n"
        
        # Contenu complet
        contenu = yaml_header + texte_section + vocab_section
        
        # Écrire le fichier
        fichier_md = os.path.join(dossier_sortie, "text.md")
        with open(fichier_md, 'w', encoding='utf-8') as f:
            f.write(contenu)
        
        print(f"✅ Markdown créé")
        return fichier_md


def main():
    parser = argparse.ArgumentParser(
        description="Générer des ressources audio multilingues avec Google Cloud Text-to-Speech",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python genmp3_google.py -l all -p "Aller au supermarché" --niveau A1
  python genmp3_google.py -l eng -p "Climate change" --longueur 200 --niveau B2 -g homme
  python genmp3_google.py -l fr -p "La météo" --niveau A2 --vitesse 0.7

Requirements:
  - GOOGLE_APPLICATION_CREDENTIALS: Variable d'environnement pointant vers le fichier JSON de credentials
  - google-cloud-texttospeech: pip install google-cloud-texttospeech
        """
    )
    
    parser.add_argument(
        "-l", "--langue",
        default="fr",
        choices=list(LanguageConfig.LANGUAGES.keys()),
        help=f"Langue (défaut: fr). Options: {LanguageConfig.list_languages()}"
    )
    parser.add_argument(
        "-p", "--prompt",
        required=True,
        help="Thème/sujet de la ressource"
    )
    parser.add_argument(
        "--longueur",
        type=int,
        default=150,
        help="Nombre approximatif de mots (défaut: 150)"
    )
    parser.add_argument(
        "--niveau",
        default="B1",
        choices=list(GeneratorConfig.LEVELS.keys()),
        help="Niveau de langue (A1-C2, défaut: B1)"
    )
    parser.add_argument(
        "-g", "--genre",
        choices=["homme", "femme"],
        help="Genre de voix (aléatoire si omis)"
    )
    parser.add_argument(
        "-v", "--voix",
        help="Voix spécifique (ex: fr-FR-Neural2-A)"
    )
    parser.add_argument(
        "--vitesse",
        type=float,
        default=0.8,
        help="Vitesse de lecture (0.25-4.0, défaut: 0.8)"
    )
    parser.add_argument(
        "-o", "--output-dir",
        help="Dossier de sortie (défaut: docs/[slug]_[timestamp])"
    )
    
    args = parser.parse_args()
    
    try:
        # Validation
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS non défini")
        
        # Générer le texte
        text_gen = TextGenerator()
        texte = text_gen.generate(args.langue, args.prompt, args.longueur, args.niveau)
        resume = text_gen.generate_resume(args.prompt)
        vocabulaire = text_gen.generate_vocabulary(args.langue, texte, args.prompt, args.niveau)
        
        # Créer le dossier de sortie
        if args.output_dir:
            dossier_sortie = args.output_dir
        else:
            slug = OutputGenerator.slugify(args.prompt)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            dossier_sortie = f"docs/{slug}_{timestamp}"
        
        os.makedirs(dossier_sortie, exist_ok=True)
        print(f"📁 Dossier créé: {dossier_sortie}\n")
        
        # Créer le markdown
        fichier_md = OutputGenerator.create_markdown(
            dossier_sortie,
            texte,
            vocabulaire,
            args.langue,
            args.prompt,
            resume,
            args.longueur,
            args.niveau,
            args.genre or "(aléatoire)"
        )
        
        # Générer l'audio
        genre = args.genre or "homme"
        AudioGeneratorGoogle.generate(
            fichier_md,
            args.langue,
            genre,
            dossier_sortie,
            vitesse=args.vitesse,
            voix=args.voix
        )
        
        print(f"\n✅ Ressource créée avec succès dans {dossier_sortie}")
        print(f"   - text.md (texte + vocabulaire)")
        print(f"   - audio.mp3 (Google Cloud TTS)")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
