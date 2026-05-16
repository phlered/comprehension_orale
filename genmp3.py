#!/usr/bin/env python3
"""
Script de génération de ressources pour l'apprentissage des langues.
Crée un dossier avec texte, audio MP3 (Azure TTS) et vocabulaire en markdown.

Usage:
    python genmp3.py -l all -p "Les animaux domestiques" --niveau B1
    python genmp3.py -l eng -p "Climate change" --longueur 200 --niveau B2 -g homme
    python genmp3.py -l fr -p "La météo" --niveau A2 --vitesse 0.7
"""

import argparse
import os
import subprocess
import random
import re
import sys
import time
from datetime import datetime
import unicodedata
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from voices_config import FlagMapping, VoiceVariantConfig, SpeakerAgeDetector, GenderDetector, VoiceSelector

load_dotenv()


class LanguageConfig:
    """Configuration pour chaque langue supportée"""
    LANGUAGES = {
        "fr": {
            "code": "fr",
            "display": "Français",
            "label_text": "Texte",
            "label_vocab": "Vocabulaire",
            "md2mp3_code": "fr",
            "description": "en français"
        },
        "eng": {
            "code": "eng",
            "display": "Anglais (UK)",
            "label_text": "Text",
            "label_vocab": "Vocabulary",
            "md2mp3_code": "eng",
            "description": "en anglais"
        },
        "us": {
            "code": "us",
            "display": "Anglais (US)",
            "label_text": "Text",
            "label_vocab": "Vocabulary",
            "md2mp3_code": "us",
            "description": "en anglais américain"
        },
        "all": {
            "code": "all",
            "display": "Allemand",
            "label_text": "Text",
            "label_vocab": "Wortschatz",
            "md2mp3_code": "all",
            "description": "en allemand"
        },
        "at": {
            "code": "at",
            "display": "Allemand (Autriche)",
            "label_text": "Text",
            "label_vocab": "Wortschatz",
            "md2mp3_code": "at",
            "description": "en allemand autrichien"
        },
        "esp": {
            "code": "esp",
            "display": "Espagnol (Espagne)",
            "label_text": "Texto",
            "label_vocab": "Vocabulario",
            "md2mp3_code": "esp",
            "description": "en espagnol d'Espagne"
        },
        "hisp": {
            "code": "hisp",
            "display": "Espagnol (Amérique du Sud)",
            "label_text": "Texto",
            "label_vocab": "Vocabulario",
            "md2mp3_code": "hisp",
            "description": "en espagnol sud-américain"
        },
        "nl": {
            "code": "nl",
            "display": "Néerlandais",
            "label_text": "Tekst",
            "label_vocab": "Woordenschat",
            "md2mp3_code": "nl",
            "description": "en néerlandais"
        },
        "cor": {
            "code": "cor",
            "display": "Coréen",
            "label_text": "텍스트",
            "label_vocab": "어휘",
            "md2mp3_code": "co",
            "description": "en coréen"
        },
        "it": {
            "code": "it",
            "display": "Italien",
            "label_text": "Testo",
            "label_vocab": "Vocabolario",
            "md2mp3_code": "it",
            "description": "en italien"
        }
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
    """Configuration pour les niveaux et axes du curriculum"""
    LEVELS = {
        "A1": "très simple avec phrases courtes et vocabulaire basique",
        "A2": "simple avec phrases simples et vocabulaire courant",
        "B1": "intermédiaire avec phrases variées et vocabulaire standard",
        "B2": "avancé avec phrases complexes et vocabulaire riche",
        "C1": "très avancé avec structures sophistiquées et vocabulaire étendu",
        "C2": "niveau natif avec nuances linguistiques et expressions idiomatiques"
    }

    SCHOOL_LEVELS = {
        "2": "Seconde",
        "1": "Première",
        "T": "Terminale"
    }

    AXES = {
        "axe1": "Axe 1. Représentation de soi et rapport à autrui",
        "axe2": "Axe 2. Vivre entre générations",
        "axe3": "Axe 3. Le passé dans le présent",
        "axe4": "Axe 4. Défis et transitions",
        "axe5": "Axe 5. Créer et recréer",
        "axe6": "Axe 6. Les pays germanophones au carrefour de l'Europe",
    }

    @classmethod
    def normalize_axe(cls, axe_input):
        """Convertit un texte d'axe complet en clé (axe1, axe2, etc.)"""
        if not axe_input:
            return None
        
        # Si c'est déjà une clé (axe1, axe2, etc.), la retourner
        if axe_input.lower() in cls.AXES:
            return axe_input.lower()
        
        # Sinon, chercher dans les valeurs (texte complet)
        for key, value in cls.AXES.items():
            if value.lower() == axe_input.lower():
                return key
        
        # Si rien trouvé, retourner None
        return None


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

        # Consignes générales
        prompt_text = f"""Écris un texte {lang_config['description']} de niveau {niveau} ({level_desc}) d'environ {longueur} mots sur le thème : {prompt}

Le texte doit être naturel, intéressant et adapté au niveau {niveau}."""

        # Consignes spécifiques: Français C2 orienté "informatif" (journalistique/chercheur)
        if langue_code == "fr" and niveau == "C2":
            style_label = (style or "sobre").lower()
            # Normaliser quelques styles attendus
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
        """Génère un résumé court du prompt (3-10 mots clés)"""
        resume_prompt = f"""Extrait le sujet principal de ce prompt d'apprentissage en 3 à 10 mots maximum (sans guillemets, sans ponctuation finale).
Le résumé doit être le thème concret, pas les instructions pédagogiques. Garde les articles si nécessaire pour la clarté.

Exemples:
- "Utilise un style journalistique pour parler des mutations génétiques au niveau seconde" → "Les mutations génétiques"
- "Écris un dialogue entre deux jeunes Allemands décrivant leur école" → "L'école en Allemagne"
- "Rédige un texte sur les traditions de Noël en Espagne" → "Les traditions de Noël en Espagne"
- "Comment fonctionne le système de vélo aux Pays-Bas ?" → "Le système de vélo aux Pays-Bas"
- "Génère un texte sur la crise de Suez" → "La crise de Suez"
- "Les animaux domestiques" → "Les animaux domestiques"
- "Quelles sont les différences culturelles entre les Néerlandais et les Belges ?" → "Différences culturelles Pays-Bas et Belgique"

Prompt à résumer: {prompt}

Résumé (3-10 mots):"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # Modèle plus léger pour une tâche simple
            messages=[{"role": "user", "content": resume_prompt}],
            max_tokens=50,
            temperature=0.3  # Basse température pour plus de cohérence
        )
        resume = response.choices[0].message.content.strip()
        # Nettoyer les guillemets/ponctuation superflus
        resume = resume.strip('"\'.,;:!? ')
        return resume

    def generate_vocabulary(self, langue_code, text, prompt, niveau):
        """Extrait le vocabulaire du texte"""
        lang_config = LanguageConfig.get_config(langue_code)
        words = len(text.split())
        # Règle de quantité de vocabulaire : nombre fixe de 35 mots quel que soit le niveau
        vocab_count = 35

        vocab_prompt = f"""Analyse ce texte {lang_config['description']} et extrais les {vocab_count} mots les plus importants et utiles pour un apprenant.

Pour chaque mot :
- Choisis des mots clés représentatifs du contenu sur le thème "{prompt}"
- Privilégie les noms, verbes et adjectifs importants
"""

        # Consignes spécifiques par langue
        if langue_code == "all":
            vocab_prompt += "- Pour les noms allemands, INDIQUE TOUJOURS l'article défini (der/die/das) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_allemand | traduction_française\n\nExemple:\nder Frau | la femme\n"
        elif langue_code in ["eng", "us"]:
            vocab_prompt += "- Pour les verbes anglais, indique 'to' avant le verbe\n"
            vocab_prompt += "- NE PAS mettre d'article devant les noms anglais\n"
            vocab_prompt += "- IMPORTANT: Donne une VRAIE traduction en français, pas un cognate. Par exemple: 'dynamics' → 'dynamique' ❌ NON! → 'dynamique' ✓ OUI!\n"
            vocab_prompt += "- Évite les traductions qui sont quasiment identiques au mot anglais (cognates). Cherche le vrai sens en français.\n"
            vocab_prompt += "Format strict (un mot par ligne) :\nmot_anglais | traduction_française\n\nExemples ✓ CORRECTS:\nto see | voir\nhouse | maison\nto challenge | défier\neficiency | rendement\nto spark | susciter\n"
        elif langue_code in ["esp", "hisp"]:
            vocab_prompt += "- Pour les noms espagnols, INDIQUE TOUJOURS l'article défini (el/la/los/las) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_espagnol | traduction_française\n\nExemple:\nla casa | la maison\nel perro | le chien\n"
        elif langue_code == "nl":
            vocab_prompt += "- Pour les noms néerlandais, INDIQUE TOUJOURS l'article défini (de/het) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_néerlandais | traduction_française\n\nExemple:\nde hond | le chien\nhet huis | la maison\n"
        elif langue_code == "fr":
            vocab_prompt += "- Pour les noms français, INDIQUE TOUJOURS l'article défini (le/la/les) devant le mot\n"
            vocab_prompt += "- La TRADUCTION doit être en NÉERLANDAIS (pas en français)\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_français | traduction_néerlandaise\n\nExemples:\nla maison | huis\nle chat | kat\n"
        elif langue_code == "cor":
            vocab_prompt += "- Pour chaque mot coréen, donne d'abord la romanisation (phonétique), puis la traduction en français\n"
            vocab_prompt += "Format strict (un mot par ligne) :\nmot_coréen → romanisation (traduction_française)\n\nExemple:\n김치 → kimchi (chou fermenté épicé)\n불고기 → bulgogi (viande marinée grillée)\n"
        elif langue_code == "it":
            vocab_prompt += "- Pour les noms italiens, INDIQUE TOUJOURS l'article défini (il/la/lo/gli/le) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_italien | traduction_française\n\nExemple:\nla casa | la maison\nil gatto | le chat\n"
        else:
            vocab_prompt += "- Pour les noms, INDIQUE l'article défini devant le mot si la langue l'utilise\n"
            vocab_prompt += "Format strict (un mot par ligne) :\nmot_langue | traduction_française\n\nExemple:\nword | traduction\n"

        vocab_prompt += f"\nTEXTE :\n{text}\n\nDonne uniquement la liste des {vocab_count} mots au format demandé, sans numérotation, sans commentaire."

        print(f"📚 Extraction du vocabulaire ({vocab_count} mots)...")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": vocab_prompt}],
            max_tokens=1024
        )

        vocabulary = []
        for line in response.choices[0].message.content.strip().split('\n'):
            # Support both | and → as separators (Korean uses →)
            separator = '→' if '→' in line else '|'
            if separator in line:
                parts = line.split(separator)
                if len(parts) >= 2:
                    word = parts[0].strip().strip('*').strip('-').strip()
                    translation = parts[1].strip().strip('*').strip('-').strip()
                    if word and translation:
                        vocabulary.append((word, translation))

        # Trier par ordre alphabétique (en ignorant les articles)
        def sort_key(item):
            word = item[0]
            # Pour l'allemand, ignorer l'article (der/die/das)
            if langue_code == "all":
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['der', 'die', 'das']:
                    return parts[1].lower()
            # Pour l'anglais, ignorer 'to' pour les verbes
            elif langue_code in ["eng", "us"]:
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() == 'to':
                    return parts[1].lower()
            # Pour l'espagnol, ignorer les articles (el/la/los/las/un/una)
            elif langue_code in ["esp", "hisp"]:
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['la', 'el', 'los', 'las', 'un', 'una', 'uno', 'unos', 'unas']:
                    return parts[1].lower()
            # Pour le néerlandais, ignorer les articles (de/het)
            elif langue_code == "nl":
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['de', 'het']:
                    return parts[1].lower()
            # Pour le français, ignorer les articles (le/la/les/l')
            elif langue_code == "fr":
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['le', 'la', 'les', "l'"]:
                    return parts[1].lower()
                # Gérer le cas de l'apostrophe collée : l'arbre
                if word.startswith("l'") or word.startswith("L'"):
                    return word[2:].lower()
            # Pour l'italien, ignorer les articles (il/la/lo/gli/le)
            elif langue_code == "it":
                parts = word.split()
                if len(parts) > 1 and parts[0].lower() in ['il', 'la', 'lo', 'gli', 'le', 'i', 'un', 'una', 'uno']:
                    return parts[1].lower()
            return word.lower()
        
        vocabulary.sort(key=sort_key)

        return vocabulary


class AudioGeneratorMD2MP3:
    """Génère l'audio avec md2mp3.py (Azure TTS)"""

    @staticmethod
    def extract_text_only(markdown_file, label_text):
        """Extrait seulement la section de texte (sans vocabulaire)"""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trouver la section Text et extraire jusqu'à la section suivante
        pattern = rf'## {re.escape(label_text)}\s*\n\n(.*?)(?=\n## |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        else:
            # Fallback : tout le contenu après le YAML
            yaml_end = content.find('---', 3)
            if yaml_end != -1:
                return content[yaml_end+3:].strip()
            return content.strip()

    @staticmethod
    def generate(markdown_file, langue_code, genre, dossier_sortie, vitesse=0.8, voix=None, voix_variant=None, ssml=False):
        """Génère le fichier audio MP3 avec md2mp3.py
        
        Args:
            markdown_file: Chemin du fichier .md
            langue_code: Code langue original (eng, us, esp, hisp, etc.)
            genre: Genre de voix (femme/homme)
            dossier_sortie: Dossier de sortie
            vitesse: Vitesse de lecture
            voix: Voix spécifique (optionnel)
            voix_variant: Variante sélectionnée (eng/us, esp/hisp) - utilise celle-ci au lieu de langue_code
        """
        lang_config = LanguageConfig.get_config(langue_code)
        # Utiliser la variante si fournie, sinon utiliser la langue originale
        effective_lang = voix_variant if voix_variant else langue_code
        md2mp3_lang = LanguageConfig.get_config(effective_lang)['md2mp3_code']
        
        # Créer un fichier temporaire avec seulement le texte
        text_only = AudioGeneratorMD2MP3.extract_text_only(markdown_file, lang_config['label_text'])
        temp_md = os.path.join(dossier_sortie, "_temp_text.md")
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(text_only)
        
        # Fichier de sortie
        fichier_mp3 = os.path.join(dossier_sortie, "audio.mp3")
        
        # Obtenir le chemin absolu du script md2mp3.py (dans le même dossier que app.py)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        md2mp3_path = os.path.join(script_dir, "md2mp3.py")
        venv_python = os.path.join(script_dir, ".venv312", "bin", "python")
        
        # Commande md2mp3.py avec voix variée (pas de nom spécifique, juste genre)
        cmd = [
            venv_python,
            md2mp3_path,
            os.path.abspath(temp_md),
            "-l", md2mp3_lang,
            "-g", genre,
            "--vitesse", str(vitesse)
        ]
        
        # Activer SSML si demandé
        if ssml:
            cmd.append("--ssml")
        
        # Ajouter la voix spécifique si fournie
        if voix:
            cmd.extend(["--voix", voix])
        
        print(f"🎤 Génération de l'audio avec md2mp3.py (langue: {md2mp3_lang}, genre: {genre}, vitesse: {vitesse}x)...")
        sys.stdout.flush()
        
        # Retry minimal ici : md2mp3.py gère déjà 2 tentatives avec 30s de pause
        max_retries = 1  # aucune relance ici; on laisse md2mp3 gérer ses retries
        for attempt in range(max_retries):
            try:
                # Streamer la sortie au lieu de la capturer
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                # Lire et afficher la sortie ligne par ligne
                for line in iter(process.stdout.readline, ''):
                    if line:
                        print(line, end='', flush=True)
                
                returncode = process.wait()
                
                if returncode == 0:
                    # Renommer le fichier généré
                    temp_mp3 = temp_md.replace('.md', '.mp3')
                    if os.path.exists(temp_mp3):
                        os.rename(temp_mp3, fichier_mp3)
                    
                    # Nettoyer le fichier temporaire
                    if os.path.exists(temp_md):
                        os.remove(temp_md)
                    
                    # Vérifier la taille
                    if os.path.exists(fichier_mp3):
                        size = os.path.getsize(fichier_mp3)
                        print(f"✅ Audio généré ({size} octets)")
                        sys.stdout.flush()
                    else:
                        print(f"⚠️ Fichier audio non trouvé")
                        sys.stdout.flush()
                    
                    break  # Succès, sortir de la boucle retry
                else:
                    raise subprocess.CalledProcessError(returncode, cmd)
                        
            except subprocess.CalledProcessError as e:
                print(f"❌ Erreur md2mp3.py après {max_retries} tentative(s) (code {e.returncode})")
                sys.stdout.flush()
                raise
            except Exception as e:
                print(f"❌ Erreur inattendue: {e}")
                raise


class OutputGenerator:
    """Génère les fichiers de sortie"""

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
        genre,
        voix=None,
        niveau_scolaire=None,
        axe=None
    ):
        """Crée le fichier markdown avec en-tête YAML et contenu
        
        Retourne: (fichier_md, voix_variant, voix_specifique) - le fichier, la variante de langue, et la voix Azure spécifique
        """
        lang_config = LanguageConfig.get_config(langue_code)

        # Déterminer la variante de voix (eng/us, esp/hisp) basée sur le contexte du texte
        voix_variant = langue_code  # Par défaut, utiliser la langue directement
        drapeau = FlagMapping.get_flag(voix_variant)
        
        # Pour l'anglais et l'espagnol, sélectionner la variante en fonction du contexte
        if langue_code in ["eng", "us"]:
            voix_variant = FlagMapping.select_voice_with_context(texte, langue_code)
            drapeau = FlagMapping.get_flag(voix_variant)
            print(f"🌐 Anglais: Variante sélectionnée {voix_variant} {drapeau}")
        elif langue_code in ["esp", "hisp"]:
            voix_variant = FlagMapping.select_voice_with_context(texte, langue_code)
            drapeau = FlagMapping.get_flag(voix_variant)
            print(f"🌐 Espagnol: Variante sélectionnée {voix_variant} {drapeau}")

        # Détécter le groupe d'âge du locuteur et choisir une voix appropriée
        age_group = SpeakerAgeDetector.detect_speaker_age_group(texte)
        voix_specifique = voix  # Utiliser la voix forcée si fournie
        
        if not voix_specifique:
            # Construire la locale Azure (ex: "en-US" ou "es-ES")
            locale_map = {
                "eng": "en-GB",
                "us": "en-US",
                "esp": "es-ES",
                "hisp": "es-MX",  # Par défaut Mexique pour hisp
                "fr": "fr-FR",
                "all": "de-DE",
                "nl": "nl-NL",
                "it": "it-IT",
                "cor": "ko-KR"
            }
            locale = locale_map.get(voix_variant, locale_map.get(langue_code))
            
            # Détecter le genre du locuteur (si non forcé)
            gender_detected = GenderDetector.detect_speaker_gender(texte)
            if gender_detected:
                genre_final = gender_detected
                print(f"👤 Genre détecté: {gender_detected}")
            else:
                genre_final = genre
            
            # Chercher une voix adaptée selon âge et genre
            voix_candidate = VoiceSelector.select_voice_by_age_and_gender(locale, genre_final, age_group)
            if voix_candidate:
                voix_specifique = voix_candidate
                if age_group:
                    print(f"🎤 Âge détecté: {age_group} → voix: {voix_specifique}")
                else:
                    print(f"🎤 Adulte (défaut) → voix: {voix_specifique}")

        # En-tête YAML
        yaml_header = f"""---
langue: {lang_config['display']}
prompt: {prompt}
resume: {resume}
longueur: {longueur}
niveau: {niveau}
genre: {genre_final if 'genre_final' in locals() else genre}
drapeau: {drapeau}
voix_variant: {voix_variant}
"""
        if voix:
            yaml_header += f"voix: {voix}\n"
        if niveau_scolaire:
            yaml_header += f"niveau_scolaire: {GeneratorConfig.SCHOOL_LEVELS.get(niveau_scolaire, niveau_scolaire)}\n"
        if axe:
            yaml_header += f"axe: {GeneratorConfig.AXES.get(axe, axe)}\n"

        yaml_header += f"date_generation: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        yaml_header += "---\n\n"

        # Contenu
        contenu = yaml_header
        contenu += f"## {lang_config['label_text']}\n\n"
        contenu += texte + "\n\n"
        contenu += f"## {lang_config['label_vocab']}\n\n"

        for word, translation in vocabulaire:
            contenu += f"- **{word}** → {translation}\n"

        # Sauvegarder
        fichier_md = os.path.join(dossier_sortie, "text.md")
        with open(fichier_md, 'w', encoding='utf-8') as f:
            f.write(contenu)

        return fichier_md, voix_variant, voix_specifique, genre_final if 'genre_final' in locals() else genre


class CompressionOralApp:
    """Application principale"""

    def __init__(self):
        self.text_gen = TextGenerator()
        self.output_gen = OutputGenerator()

    def run(self, args):
        """Exécute la génération complète"""
        print(f"\n🚀 Démarrage de la génération")
        print(f"Langue: {LanguageConfig.get_config(args.langue)['display']}")
        print(f"Prompt: {args.prompt}")
        print(f"Niveau: {args.niveau}")
        print(f"Longueur: {args.longueur} mots\n")

        # Créer le dossier de sortie dans le répertoire du script (pas le répertoire courant)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        theme_safe = self.slugify(args.prompt)
        dossier_nom = f"{theme_safe}_{timestamp}"
        dossier_sortie = os.path.join(script_dir, "docs", dossier_nom)

        Path(dossier_sortie).mkdir(parents=True, exist_ok=True)
        print(f"📁 Dossier créé: {dossier_sortie}/\n")

        try:
            # Normaliser l'axe si fourni
            axe_normalized = GeneratorConfig.normalize_axe(args.axe) if args.axe else None
            
            # Générer le texte
            texte = self.text_gen.generate(
                args.langue,
                args.prompt,
                args.longueur,
                args.niveau,
                style=args.style
            )
            print(f"✅ Texte généré ({len(texte.split())} mots)\n")

            # Générer le vocabulaire
            vocabulaire = self.text_gen.generate_vocabulary(
                args.langue,
                texte,
                args.prompt,
                args.niveau
            )
            print(f"✅ Vocabulaire extrait ({len(vocabulaire)} mots)\n")

            # Générer le résumé du prompt
            resume = self.text_gen.generate_resume(args.prompt)
            print(f"✅ Résumé généré: \"{resume}\"\n")

            # Générer le markdown AVANT l'audio (md2mp3 a besoin du fichier)
            fichier_md, voix_variant, voix_specifique, genre_final = self.output_gen.create_markdown(
                dossier_sortie,
                texte,
                vocabulaire,
                args.langue,
                args.prompt,
                resume,
                args.longueur,
                args.niveau,
                args.genre,
                args.voix,
                args.niveau_scolaire,
                axe_normalized
            )
            print(f"✅ Markdown généré: text.md\n")

            # Choisir la vitesse par défaut selon le niveau si non fournie
            # Progression linéaire: A1:0.75 → C2:1.0 (paliers de 0.05)
            default_speeds = {
                "A1": 0.7,
                "A2": 0.75,
                "B1": 0.8,
                "B2": 0.85,
                "C1": 0.90,
                "C2": 0.95
            }
            vitesse_effective = args.vitesse if args.vitesse is not None else default_speeds.get(args.niveau, 0.80)

            # Générer l'audio avec md2mp3.py (passer la variante de voix et la voix spécifique détectée)
            AudioGeneratorMD2MP3.generate(fichier_md, args.langue, genre_final, dossier_sortie, vitesse=vitesse_effective, voix=voix_specifique, voix_variant=voix_variant, ssml=args.ssml)
            print(f"✅ Audio généré: audio.mp3\n")

            print(f"{'=' * 60}")
            print(f"✅ SUCCÈS")
            print(f"{'=' * 60}")
            print(f"📁 Dossier de sortie: {dossier_sortie}/")
            print(f"📄 text.md")
            print(f"🎧 audio.mp3")
            print(f"{'=' * 60}\n")

        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            return 1

        return 0

    @staticmethod
    def slugify(text, max_length=60):
        """Slug sûr : conserve les lettres (accents → base), retire le reste."""
        text = unicodedata.normalize("NFKD", text)
        text = text.encode("ascii", "ignore").decode("ascii")
        text = re.sub(r"[^A-Za-z0-9]+", "_", text.lower())
        text = re.sub(r"_+", "_", text).strip("_")
        if max_length:
            text = text[:max_length].rstrip("_")
        return text or "resource"

def main():
    parser = argparse.ArgumentParser(
        description="Génère des ressources pour l'apprentissage des langues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python genmp3.py -l all -p "Les animaux domestiques" --niveau B1
  python genmp3.py --langue eng --prompt "Climate change" --longueur 200 --niveau B2 -g homme
  python genmp3.py -l esp -p "La familia" --niveau A2 --niveau-scolaire 2 --axe axe1 --vitesse 0.7
        """
    )

    # Paramètres obligatoires
    parser.add_argument(
        '-l', '--langue',
        required=True,
        choices=['fr', 'eng', 'us', 'all', 'at', 'esp', 'hisp', 'nl', 'cor', 'it'],
        help=f"Langue cible. Options: {LanguageConfig.list_languages()}"
    )

    parser.add_argument(
        '-p', '--prompt',
        required=True,
        help="Thème/sujet du texte à générer"
    )

    # Paramètres optionnels avec défauts
    # Longueur auto par niveau si non fournie
    DEFAULT_LENGTHS = {
        "A1": 150,
        "A2": 200,
        "B1": 250,
        "B2": 300,
        "C1": 350,
        "C2": 400,
    }

    parser.add_argument(
        '--longueur',
        type=int,
        default=None,
        help="Longueur du texte en mots (défaut auto par niveau: A1=150, A2=200, B1=250, B2=300, C1=350, C2=400)"
    )

    parser.add_argument(
        '--niveau',
        default='B1',
        choices=['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
        help="Niveau de langue CECRL (défaut: B1)"
    )

    parser.add_argument(
        '--style',
        choices=['sobre', 'journalistique', 'scientifique'],
        help="Style de rédaction (surtout utile pour C2 FR): 'sobre' (défaut), 'journalistique' ou 'scientifique'"
    )

    parser.add_argument(
        '-g', '--genre',
        default='femme',
        choices=['femme', 'homme'],
        help="Genre de la voix (défaut: femme)"
    )

    parser.add_argument(
        '--voix',
        type=str,
        help="Nom de la voix spécifique (ex: elsa, diego, denise, etc.)"
    )

    parser.add_argument(
        '--vitesse',
        type=float,
        default=None,
        help="Vitesse de lecture de 0.6 à 1.0 (défaut auto: A1=0.75, A2=0.80, B1=0.85, B2=0.90, C1=0.95, C2=1.0)"
    )

    # Paramètres optionnels supplémentaires
    parser.add_argument(
        '--niveau-scolaire',
        choices=['2', '1', 'T'],
        help="Niveau scolaire (optionnel): 2=Seconde, 1=Première, T=Terminale"
    )

    parser.add_argument(
        '--axe',
        type=str,
        help="Axe du programme (optionnel). Accepte: axe1-axe6 ou texte complet (ex: 'Axe 1. Représentation de soi et rapport à autrui')"
    )

    # Option pour activer le SSML dans md2mp3 (conversion Markdown→SSML)
    parser.add_argument(
        '--ssml',
        action='store_true',
        help="Activer SSML pour emphases (*, **) et pauses ([p], [p:ms]) lors de la synthèse audio"
    )

    args = parser.parse_args()

    # Appliquer la longueur par défaut en fonction du niveau si non fournie
    if args.longueur is None:
        args.longueur = DEFAULT_LENGTHS.get(args.niveau, 150)

    # Exécuter l'application
    app = CompressionOralApp()
    return app.run(args)


if __name__ == "__main__":
    exit(main())
