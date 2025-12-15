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

    def generate(self, langue_code, prompt, longueur, niveau):
        """Génère un texte selon les paramètres"""
        lang_config = LanguageConfig.get_config(langue_code)
        level_desc = GeneratorConfig.LEVELS.get(niveau, GeneratorConfig.LEVELS["B1"])

        prompt_text = f"""Écris un texte {lang_config['description']} de niveau {niveau} ({level_desc}) d'environ {longueur} mots sur le thème : {prompt}

Le texte doit être naturel, intéressant et adapté au niveau {niveau}."""

        print(f"📝 Génération du texte ({longueur} mots, niveau {niveau})...")
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt_text}],
            max_tokens=4096
        )
        text = response.choices[0].message.content.strip()
        return text

    def generate_vocabulary(self, langue_code, text, prompt):
        """Extrait le vocabulaire du texte"""
        lang_config = LanguageConfig.get_config(langue_code)
        words = len(text.split())
        vocab_count = max(1, int(words * 0.2 + 0.5))  # 20% au lieu de 10%

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
            vocab_prompt += "Format strict (un mot par ligne) :\nmot_anglais | traduction_française\n\nExemple:\nto see | voir\nhouse | maison\n"
        elif langue_code in ["esp", "hisp"]:
            vocab_prompt += "- Pour les noms espagnols, INDIQUE TOUJOURS l'article défini (el/la/los/las) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_espagnol | traduction_française\n\nExemple:\nla casa | la maison\nel perro | le chien\n"
        elif langue_code == "nl":
            vocab_prompt += "- Pour les noms néerlandais, INDIQUE TOUJOURS l'article défini (de/het) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_néerlandais | traduction_française\n\nExemple:\nde hond | le chien\nhet huis | la maison\n"
        elif langue_code == "fr":
            vocab_prompt += "- Pour les noms français, INDIQUE TOUJOURS l'article défini (le/la/les) devant le mot\n"
            vocab_prompt += "Format strict (un mot par ligne) :\narticle mot_français | traduction\n\nExemple:\nla maison | house\nle chat | cat\n"
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
    def generate(markdown_file, langue_code, genre, dossier_sortie, vitesse=0.8, voix=None):
        """Génère le fichier audio MP3 avec md2mp3.py"""
        lang_config = LanguageConfig.get_config(langue_code)
        md2mp3_lang = lang_config['md2mp3_code']
        
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
        
        # Ajouter la voix spécifique si fournie
        if voix:
            cmd.extend(["--voix", voix])
        
        print(f"🎤 Génération de l'audio avec md2mp3.py (langue: {md2mp3_lang}, genre: {genre}, vitesse: {vitesse}x)...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
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
            else:
                print(f"⚠️ Fichier audio non trouvé")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur md2mp3.py: {e}")
            print(f"Sortie: {e.stdout}")
            print(f"Erreur: {e.stderr}")
            raise
        except Exception as e:
            print(f"❌ Erreur: {e}")
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
        longueur,
        niveau,
        genre,
        voix=None,
        niveau_scolaire=None,
        axe=None
    ):
        """Crée le fichier markdown avec en-tête YAML et contenu"""
        lang_config = LanguageConfig.get_config(langue_code)

        # En-tête YAML
        yaml_header = f"""---
langue: {lang_config['display']}
prompt: {prompt}
longueur: {longueur}
niveau: {niveau}
genre: {genre}
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

        return fichier_md


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
        theme_safe = args.prompt.lower().replace(' ', '_').replace('é', 'e').replace('è', 'e')[:20]
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
                args.niveau
            )
            print(f"✅ Texte généré ({len(texte.split())} mots)\n")

            # Générer le vocabulaire
            vocabulaire = self.text_gen.generate_vocabulary(
                args.langue,
                texte,
                args.prompt
            )
            print(f"✅ Vocabulaire extrait ({len(vocabulaire)} mots)\n")

            # Générer le markdown AVANT l'audio (md2mp3 a besoin du fichier)
            fichier_md = self.output_gen.create_markdown(
                dossier_sortie,
                texte,
                vocabulaire,
                args.langue,
                args.prompt,
                args.longueur,
                args.niveau,
                args.genre,
                args.voix,
                args.niveau_scolaire,
                axe_normalized
            )
            print(f"✅ Markdown généré: text.md\n")

            # Générer l'audio avec md2mp3.py
            AudioGeneratorMD2MP3.generate(fichier_md, args.langue, args.genre, dossier_sortie, vitesse=args.vitesse, voix=args.voix)
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
        choices=['fr', 'eng', 'us', 'all', 'esp', 'hisp', 'nl', 'cor', 'it'],
        help=f"Langue cible. Options: {LanguageConfig.list_languages()}"
    )

    parser.add_argument(
        '-p', '--prompt',
        required=True,
        help="Thème/sujet du texte à générer"
    )

    # Paramètres optionnels avec défauts
    parser.add_argument(
        '--longueur',
        type=int,
        default=150,
        help="Longueur du texte en mots (défaut: 150)"
    )

    parser.add_argument(
        '--niveau',
        default='B1',
        choices=['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
        help="Niveau de langue CECRL (défaut: B1)"
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
        default=0.8,
        help="Vitesse de lecture de 0.6 à 1.0 (défaut: 0.8 pour apprentissage)"
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

    args = parser.parse_args()

    # Exécuter l'application
    app = CompressionOralApp()
    return app.run(args)


if __name__ == "__main__":
    exit(main())
