#!/usr/bin/env python3
"""
Script pour convertir des fichiers Markdown en MP3.
Utilise Azure Text-to-Speech pour une meilleure qualité audio.
Gère les dialogues avec plusieurs locuteurs et voix variées.

Usage:
    python md2mp3.py texte.md -l fr
    python md2mp3.py texte.md -l all --voix femme
    python md2mp3.py dialogue.md -l fr --voix homme (pour forcer)
"""

import argparse
import os
import re
import random
import time
from pathlib import Path
from dotenv import load_dotenv
import asyncio

try:
    import azure.cognitiveservices.speech as speechsdk
    HAS_AZURE = True
except ImportError:
    HAS_AZURE = False
    print("⚠️  Azure Speech SDK non installé. Installez avec: pip install azure-cognitiveservices-speech")

load_dotenv()


class VoiceConfig:
    """Configuration des voix pour chaque langue"""
    
    VOICES = {
        "fr": {
            "female": [
                "fr-FR-DeniseNeural",
                "fr-FR-EloiseNeural",
                "fr-FR-VivienneNeural",
                "fr-FR-BrigitteNeural",
                "fr-FR-CelesteNeural",
                "fr-FR-CoralieNeural",
                "fr-FR-JacquelineNeural",
                "fr-FR-JosephineNeural",
                "fr-FR-YvetteNeural",
                "fr-CH-ArianeNeural",
                "fr-BE-CharlineNeural",
            ],
            "male": [
                "fr-FR-HenriNeural",
                "fr-FR-AlainNeural",
                "fr-FR-ClaudeNeural",
                "fr-FR-JeromeNeural",
                "fr-FR-MauriceNeural",
                "fr-FR-YvesNeural",
                "fr-CH-FabriceNeural",
                "fr-BE-GerardNeural",
            ]
        },
        "all": {
            "female": [
                "de-DE-KatjaNeural",
                "de-DE-AmalaNeural",
                "de-DE-ElkeNeural",
                "de-DE-KlarissaNeural",
                "de-DE-LouisaNeural",
                "de-DE-MajaNeural",
                "de-DE-TanjaNeural",
                "de-CH-LeniNeural",
                "de-AT-IngridNeural",
            ],
            "male": [
                "de-DE-ConradNeural",
                "de-DE-BerndNeural",
                "de-DE-ChristophNeural",
                "de-DE-KasperNeural",
                "de-DE-KillianNeural",
                "de-DE-KlausNeural",
                "de-CH-JanNeural",
                "de-AT-JonasNeural",
            ]
        },
        "at": {
            "female": [
                "de-AT-IngridNeural",
            ],
            "male": [
                "de-AT-JonasNeural",
            ]
        },
        "eng": {
            "female": [
                "en-GB-LibbyNeural",
                "en-GB-SoniaNeural",
                "en-GB-BellaNeural",
                "en-GB-HollieNeural",
                "en-GB-OliviaNeural",
            ],
            "male": [
                "en-GB-RyanNeural",
                "en-GB-ThomasNeural",
                "en-GB-ElliotNeural",
                "en-GB-EthanNeural",
                "en-GB-OliverNeural",
            ]
        },
        "us": {
            "female": [
                "en-US-AriaNeural",
                "en-US-AvaNeural",
                "en-US-EmmaNeural",
                "en-US-JennyNeural",
                "en-US-MichelleNeural",
                "en-US-MonicaNeural",
                "en-US-AmberNeural",
                "en-US-AnaNeural",
                "en-US-AshleyNeural",
                "en-US-CoraNeural",
                "en-US-ElizabethNeural",
                "en-US-SaraNeural",
            ],
            "male": [
                "en-US-GuyNeural",
                "en-US-BrianNeural",
                "en-US-ChristopherNeural",
                "en-US-EricNeural",
                "en-US-JacobNeural",
                "en-US-JasonNeural",
                "en-US-TonyNeural",
                "en-US-DavisNeural",
            ]
        },
        "esp": {
            "female": [
                "es-ES-ElviraNeural",
                "es-ES-EstrellaNeural",
                "es-ES-VerónicaNeural",
                "es-ES-AbrilNeural",
                "es-ES-IreneNeural",
                "es-ES-LaiaNeural",
                "es-ES-LiaNeural",
                "es-ES-TrisaNeural",
            ],
            "male": [
                "es-ES-AlvaroNeural",
                "es-ES-ArnauNeural",
                "es-ES-DarioNeural",
                "es-ES-EliasNeural",
                "es-ES-SaulNeural",
                "es-ES-TeoNeural",
            ]
        },
        "hisp": {
            "female": [
                "es-AR-ElenaNeural",
                "es-CO-SalomeNeural",
                "es-MX-BeatrizNeural",
                "es-MX-CarlotaNeural",
                "es-MX-CandelaNeural",
                "es-MX-LarissaNeural",
                "es-MX-MarinaNeural",
                "es-MX-NuriaNeural",
                "es-MX-RenataNeural",
            ],
            "male": [
                "es-AR-TomasNeural",
                "es-MX-JorgeNeural",
                "es-CO-GonzaloNeural",
                "es-MX-CecilioNeural",
                "es-MX-GerardoNeural",
                "es-MX-LibertoNeural",
                "es-MX-LucianoNeural",
                "es-MX-PelayoNeural",
                "es-MX-YagoNeural",
            ]
        },
        "nl": {
            "female": [
                "nl-NL-FennaNeural",
                "nl-NL-ColetteNeural",
                "nl-BE-DenaNeural",
            ],
            "male": [
                "nl-NL-MaartenNeural",
                "nl-NL-CoenNeural",
                "nl-BE-ArnaudNeural",
            ]
        },
        "co": {
            "female": [
                "ko-KR-SunHiNeural",
                "ko-KR-YuJinNeural",
                "ko-KR-SoonBokNeural",
                "ko-KR-JiMinNeural",
            ],
            "male": [
                "ko-KR-InJoonNeural",
                "ko-KR-BongJinNeural",
                "ko-KR-GookMinNeural",
                "ko-KR-HyunsuNeural",
            ]
        },
        "it": {
            "female": [
                "it-IT-ElsaNeural",
                "it-IT-IsabellaNeural",
            ],
            "male": [
                "it-IT-DiegoNeural",
                "it-IT-GiuseppeNeural",
                "it-IT-FabioNeural",
            ]
        }
    }

    # Mapping des prénoms vers les IDs Azure complets (tous les langues)
    VOICE_NAMES = {
        # Français
        "denise": "fr-FR-DeniseNeural",
        "eloise": "fr-FR-EloiseNeural",
        "vivienne": "fr-FR-VivienneNeural",
        "brigitte": "fr-FR-BrigitteNeural",
        "celeste": "fr-FR-CelesteNeural",
        "coralie": "fr-FR-CoralieNeural",
        "jacqueline": "fr-FR-JacquelineNeural",
        "josephine": "fr-FR-JosephineNeural",
        "yvette": "fr-FR-YvetteNeural",
        "ariane": "fr-CH-ArianeNeural",
        "charline": "fr-BE-CharlineNeural",
        "henri": "fr-FR-HenriNeural",
        "alain": "fr-FR-AlainNeural",
        "claude": "fr-FR-ClaudeNeural",
        "jerome": "fr-FR-JeromeNeural",
        "maurice": "fr-FR-MauriceNeural",
        "yves": "fr-FR-YvesNeural",
        "fabrice": "fr-CH-FabriceNeural",
        "gerard": "fr-BE-GerardNeural",
        
        # Allemand
        "katja": "de-DE-KatjaNeural",
        "amala": "de-DE-AmalaNeural",
        "elke": "de-DE-ElkeNeural",
        "klarissa": "de-DE-KlarissaNeural",
        "louisa": "de-DE-LouisaNeural",
        "maja": "de-DE-MajaNeural",
        "tanja": "de-DE-TanjaNeural",
        "leni": "de-CH-LeniNeural",
        "ingrid": "de-AT-IngridNeural",
        "conrad": "de-DE-ConradNeural",
        "bernd": "de-DE-BerndNeural",
        "christoph": "de-DE-ChristophNeural",
        "kasper": "de-DE-KasperNeural",
        "killian": "de-DE-KillianNeural",
        "klaus": "de-DE-KlausNeural",
        "jan": "de-CH-JanNeural",
        "jonas": "de-AT-JonasNeural",
        
        # Anglais UK
        "libby": "en-GB-LibbyNeural",
        "maisie": "en-GB-MaisieNeural",
        "sonia": "en-GB-SoniaNeural",
        "bella": "en-GB-BellaNeural",
        "hollie": "en-GB-HollieNeural",
        "olivia": "en-GB-OliviaNeural",
        "ryan": "en-GB-RyanNeural",
        "thomas": "en-GB-ThomasNeural",
        "alfie": "en-GB-AlfieNeural",
        "elliot": "en-GB-ElliotNeural",
        "ethan": "en-GB-EthanNeural",
        "noah": "en-GB-NoahNeural",
        "oliver": "en-GB-OliverNeural",
        
        # Anglais US
        "aria": "en-US-AriaNeural",
        "ava": "en-US-AvaNeural",
        "emma": "en-US-EmmaNeural",
        "jenny": "en-US-JennyNeural",
        "michelle": "en-US-MichelleNeural",
        "monica": "en-US-MonicaNeural",
        "amber": "en-US-AmberNeural",
        "ana": "en-US-AnaNeural",
        "ashley": "en-US-AshleyNeural",
        "cora": "en-US-CoraNeural",
        "elizabeth": "en-US-ElizabethNeural",
        "sara": "en-US-SaraNeural",
        "guy": "en-US-GuyNeural",
        "brian": "en-US-BrianNeural",
        "christopher": "en-US-ChristopherNeural",
        "eric": "en-US-EricNeural",
        "jacob": "en-US-JacobNeural",
        "jason": "en-US-JasonNeural",
        "tony": "en-US-TonyNeural",
        "davis": "en-US-DavisNeural",
        
        # Espagnol Espagne
        "elvira": "es-ES-ElviraNeural",
        "estrella": "es-ES-EstrellaNeural",
        "veronica": "es-ES-VerónicaNeural",
        "abril": "es-ES-AbrilNeural",
        "irene": "es-ES-IreneNeural",
        "laia": "es-ES-LaiaNeural",
        "lia": "es-ES-LiaNeural",
        "trisa": "es-ES-TrisaNeural",
        "alvaro": "es-ES-AlvaroNeural",
        "arnau": "es-ES-ArnauNeural",
        "dario": "es-ES-DarioNeural",
        "elias": "es-ES-EliasNeural",
        "nil": "es-ES-NilNeural",
        "saul": "es-ES-SaulNeural",
        "teo": "es-ES-TeoNeural",
        
        # Espagnol Amérique latine
        "elena": "es-AR-ElenaNeural",
        "marta": "es-MX-MartaNeural",
        "salome": "es-CO-SalomeNeural",
        "beatriz": "es-MX-BeatrizNeural",
        "carlota": "es-MX-CarlotaNeural",
        "candela": "es-MX-CandelaNeural",
        "larissa": "es-MX-LarissaNeural",
        "marina": "es-MX-MarinaNeural",
        "nuria": "es-MX-NuriaNeural",
        "renata": "es-MX-RenataNeural",
        "tomas": "es-AR-TomasNeural",
        "jorge": "es-MX-JorgeNeural",
        "gonzalo": "es-CO-GonzaloNeural",
        "cecilio": "es-MX-CecilioNeural",
        "gerardo": "es-MX-GerardoNeural",
        "liberto": "es-MX-LibertoNeural",
        "luciano": "es-MX-LucianoNeural",
        "pelayo": "es-MX-PelayoNeural",
        "yago": "es-MX-YagoNeural",
        
        # Néerlandais
        "fenna": "nl-NL-FennaNeural",
        "colette": "nl-NL-ColetteNeural",
        "dena": "nl-BE-DenaNeural",
        "maarten": "nl-NL-MaartenNeural",
        "coen": "nl-NL-CoenNeural",
        "arnaud": "nl-BE-ArnaudNeural",
        
        # Coréen
        "sunhi": "ko-KR-SunHiNeural",
        "yujin": "ko-KR-YuJinNeural",
        "hyunju": "ko-KR-HyunjuNeural",
        "soonbok": "ko-KR-SoonBokNeural",
        "jimin": "ko-KR-JiMinNeural",
        "injoon": "ko-KR-InJoonNeural",
        "bongjin": "ko-KR-BongJinNeural",
        "gookmin": "ko-KR-GookMinNeural",
        "hyunsu": "ko-KR-HyunsuNeural",
        
        # Italien
        "elsa": "it-IT-ElsaNeural",
        "isabella": "it-IT-IsabellaNeural",
        "diego": "it-IT-DiegoNeural",
        "giuseppe": "it-IT-GiuseppeNeural",
        "lucio": "it-IT-LucioNeural",
        "fabio": "it-IT-FabioNeural",
    }

    @classmethod
    def get_voice_by_name(cls, voice_name):
        """Retourne l'ID Azure complet à partir d'un prénom"""
        voice_name_lower = voice_name.lower()
        if voice_name_lower in cls.VOICE_NAMES:
            return cls.VOICE_NAMES[voice_name_lower]
        raise ValueError(f"Voix non trouvée: {voice_name}. Utilisez --help pour voir les voix disponibles.")

    @classmethod
    def get_random_voice(cls, langue, gender=None):
        """Retourne une voix aléatoire pour une langue et genre donnés"""
        if langue not in cls.VOICES:
            raise ValueError(f"Langue non supportée: {langue}")
        
        if gender is None:
            gender = random.choice(["female", "male"])
        
        if gender not in cls.VOICES[langue]:
            gender = list(cls.VOICES[langue].keys())[0]
        
        voices = cls.VOICES[langue][gender]
        return random.choice(voices)

    @classmethod
    def get_voice(cls, langue, gender=None, voice_name=None):
        """Retourne une voix pour une langue et genre donnés, ou une voix spécifique par nom"""
        # Priorité au nom de voix spécifique
        if voice_name:
            return cls.get_voice_by_name(voice_name)
        # Sinon, sélection par genre
        if gender:
            return cls.get_random_voice(langue, gender)
        # Par défaut, aléatoire
        return cls.get_random_voice(langue)


class MarkdownCleaner:
    """Nettoie le texte Markdown pour la lecture TTS"""
    
    # Traductions des éléments mathématiques par langue
    MATH_TRANSLATIONS = {
        "fr": {
            "^2": " au carré",
            "^3": " au cube",
            "^": " exposant ",
            "\\sqrt": "racine",
            "=": " égal ",
            "+": " plus ",
            "-": " moins ",
            "*": " fois ",
            "/": " divisé par ",
        },
        "eng": {
            "^2": " squared",
            "^3": " cubed",
            "^": " to the power of ",
            "\\sqrt": "square root",
            "=": " equals ",
            "+": " plus ",
            "-": " minus ",
            "*": " times ",
            "/": " divided by ",
        },
        "us": {
            "^2": " squared",
            "^3": " cubed",
            "^": " to the power of ",
            "\\sqrt": "square root",
            "=": " equals ",
            "+": " plus ",
            "-": " minus ",
            "*": " times ",
            "/": " divided by ",
        },
        "all": {  # Allemand
            "^2": " zum Quadrat",
            "^3": " zum Kubik",
            "^": " hoch ",
            "\\sqrt": "Quadratwurzel",
            "=": " gleich ",
            "+": " plus ",
            "-": " minus ",
            "*": " mal ",
            "/": " geteilt durch ",
        },
        "esp": {  # Espagnol
            "^2": " al cuadrado",
            "^3": " al cubo",
            "^": " a la potencia ",
            "\\sqrt": "raíz cuadrada",
            "=": " igual ",
            "+": " más ",
            "-": " menos ",
            "*": " por ",
            "/": " dividido por ",
        },
        "hisp": {  # Hispanique (même que esp)
            "^2": " al cuadrado",
            "^3": " al cubo",
            "^": " a la potencia ",
            "\\sqrt": "raíz cuadrada",
            "=": " igual ",
            "+": " más ",
            "-": " menos ",
            "*": " por ",
            "/": " dividido por ",
        },
        "nl": {  # Néerlandais
            "^2": " kwadraat",
            "^3": " kubiek",
            "^": " tot de macht ",
            "\\sqrt": "vierkantswortel",
            "=": " gelijk ",
            "+": " plus ",
            "-": " min ",
            "*": " keer ",
            "/": " gedeeld door ",
        },
        "co": {  # Coréen
            "^2": " 제곱",
            "^3": " 세제곱",
            "^": " 의 거듭제곱 ",
            "\\sqrt": "제곱근",
            "=": " 같음 ",
            "+": " 더하기 ",
            "-": " 빼기 ",
            "*": " 곱하기 ",
            "/": " 나누기 ",
        }
    }

    @staticmethod
    def markdown_to_ssml(text):
        """
        Convertit les marqueurs Markdown en balises SSML.
        - *mot* → <emphasis> + <prosody pitch="+10%"> (emphasis modérée visible)
        - **mot** → <emphasis> + <prosody pitch="+20%" rate="slow"> (emphasis forte très marquée)
        - [p] → <break time="250ms"/>
        - [p:300] → <break time="300ms"/>
        
        Note: Combinaison emphasis + prosody pour forcer Azure à appliquer l'emphasis
        """
        # Convertir **mot** en emphasis forte TRÈS marquée
        # Combiner emphasis, pitch élevé, ralentissement, et volume fort
        text = re.sub(
            r'\*\*([^*]+)\*\*',
            r'<emphasis level="strong"><prosody pitch="+20%" rate="slow" volume="x-loud">\1</prosody></emphasis>',
            text
        )
        
        # Convertir *mot* en emphasis modérée marquée
        text = re.sub(
            r'\*([^*]+)\*',
            r'<emphasis level="moderate"><prosody pitch="+10%" volume="loud">\1</prosody></emphasis>',
            text
        )
        
        # Convertir [p:XXX] avec durée custom
        text = re.sub(r'\[p:(\d+)\]', r'<break time="\1ms"/>', text)
        
        # Convertir [p] en pause par défaut (250ms)
        text = re.sub(r'\[p\]', '<break time="250ms"/>', text)
        
        return text
    
    @staticmethod
    def clean_text(text, langue="fr", enable_ssml=False):
        """Supprime la syntaxe Markdown et les éléments non lus
        
        Args:
            text: Texte Markdown à nettoyer
            langue: Langue pour la conversion d'équations
            enable_ssml: Si True, convertit *mot* et [p] en SSML; si False, supprime ces marqueurs
        """
        
        # Supprimer le frontmatter YAML
        text = re.sub(r'^---.*?---\n', '', text, flags=re.DOTALL)

        # Supprimer le bloc vocabulaire complet (garde uniquement le texte principal)
        text = MarkdownCleaner._remove_vocabulary_section(text)

        # Supprimer un éventuel titre "Text"/"Texte"/"Texto" isolé en tête de fichier
        text = re.sub(r'^\s*(?:#{1,6}\s*)?(?:text|texte|texto|tekst)\s*\n+', '', text, flags=re.IGNORECASE)
        
        # Supprimer les titres Markdown
        text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
        
        # Par défaut (SSML désactivé), supprimer les marqueurs [p], [p:XXX] et les emphasis * **
        if not enable_ssml:
            text = re.sub(r'\[p(?::\d+)?\]', '', text)
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
            text = re.sub(r'\*([^*]+)\*', r'\1', text)
        else:
            # SSML activé: convertir les marqueurs markdown vers SSML
            text = MarkdownCleaner.markdown_to_ssml(text)
        
        # Supprimer les liens Markdown (mais garder le texte)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        
        # Supprimer le gras et l'italique des underscores (__ et _)
        text = re.sub(r'__([^_]+)__', r'\1', text)
        text = re.sub(r'_([^_]+)_', r'\1', text)
        
        # Supprimer les listes Markdown
        text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Convertir les équations mathématiques en texte lisible
        text = MarkdownCleaner._convert_equations(text, langue)
        
        # Supprimer les blocs de code
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`([^`]+)`', r'\1', text)
        
        # Supprimer les balises HTML en fonction du mode SSML
        if enable_ssml:
            # SSML activé: ne pas supprimer les balises pour éviter de casser la
            # structure des balises SSML insérées (emphasis/prosody/break).
            # Les autres nettoyages en amont ont déjà retiré le Markdown.
            pass
        else:
            # SSML désactivé: supprimer toutes les balises
            text = re.sub(r'<[^>]+>', '', text)
        
        # Nettoyer les espaces superflus
        text = re.sub(r'\n\n+', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        return text.strip()

    @staticmethod
    def _remove_vocabulary_section(text):
        """Supprime la section vocabulaire (quel que soit le heading)"""
        vocab_headings = [
            "vocabulaire", "vocabulary", "vocabulario", "wortschatz", "glossary", "vocabulário", "vocabolario"
        ]
        pattern = r'^\s*(?:#{1,6}\s*)?(?:' + '|'.join(vocab_headings) + r')\s*$'
        match = re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
        if match:
            return text[:match.start()].rstrip()
        return text

    @staticmethod
    def _convert_equations(text, langue="fr"):
        """Convertit les équations mathématiques en texte lisible selon la langue"""
        
        # Sélectionner la traduction appropriée
        translations = MarkdownCleaner.MATH_TRANSLATIONS.get(langue, MarkdownCleaner.MATH_TRANSLATIONS["fr"])
        
        # Équations inline avec $...$
        def convert_inline_eq(match):
            eq = match.group(1)
            
            # Appliquer les traductions dans l'ordre approprié
            # D'abord les puissances spéciales (^2, ^3) avant la puissance générale (^)
            eq = eq.replace('^2', translations["^2"])
            eq = eq.replace('^3', translations["^3"])
            eq = eq.replace('^', translations["^"])
            
            # Puis les autres éléments
            eq = eq.replace('\\sqrt', translations["\\sqrt"])
            eq = eq.replace('\\', '')
            eq = eq.replace('{', '(')
            eq = eq.replace('}', ')')
            eq = eq.replace('=', translations["="])
            eq = eq.replace('+', translations["+"])
            eq = eq.replace('-', translations["-"])
            eq = eq.replace('*', translations["*"])
            eq = eq.replace('/', translations["/"])
            
            return f" {eq} "
        
        text = re.sub(r'\$([^$]+)\$', convert_inline_eq, text)
        
        # Équations bloc avec $$...$$
        text = re.sub(r'\$\$([^$]+)\$\$', convert_inline_eq, text, flags=re.DOTALL)
        
        return text

    @staticmethod
    def detect_dialogue(text):
        """Détecte si le texte contient un dialogue et retourne les locuteurs"""
        
        # Motifs courants pour les dialogues
        patterns = [
            r'^[A-Z][^:]+:\s+(.+)$',  # Nom: texte
            r'^—\s+(.+)$',             # — texte
            r'^\*\*[A-Z][^*]+\*\*:\s+(.+)$',  # **Nom**: texte
        ]
        
        dialogue_lines = []
        for line in text.split('\n'):
            for pattern in patterns:
                if re.match(pattern, line):
                    dialogue_lines.append(line)
                    break
        
        # Si plus de 30% du texte est du dialogue, c'est un dialogue
        return len(dialogue_lines) > len(text.split('\n')) * 0.3, dialogue_lines

    @staticmethod
    def parse_dialogue_line(line):
        """Extrait le locuteur et le texte d'une ligne de dialogue"""
        
        # Motif: Nom: texte
        match = re.match(r'^([A-Z][^:]+):\s+(.+)$', line)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        # Motif: — texte
        match = re.match(r'^—\s+(.+)$', line)
        if match:
            return "Narrateur", match.group(1).strip()
        
        # Motif: **Nom**: texte
        match = re.match(r'^\*\*([^*]+)\*\*:\s+(.+)$', line)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        
        return None, line


class DialogueVoiceAssigner:
    """Assigne des voix différentes aux personnages d'un dialogue"""

    def __init__(self, langue, forced_gender=None):
        self.langue = langue
        self.forced_gender = forced_gender
        self.speaker_voices = {}
        self.used_voices = set()
        self.genders = {}

    def assign_gender_to_speaker(self, speaker_name):
        """Assigne un genre au locuteur selon son nom"""
        if speaker_name in self.genders:
            return self.genders[speaker_name]
        
        # Noms français féminins communs
        female_names_fr = ['Marie', 'Sophie', 'Emma', 'Anne', 'Claire', 'Élise', 'Jeanne', 'Isabelle', 'Catherine']
        male_names_fr = ['Jean', 'Pierre', 'Paul', 'Marc', 'André', 'François', 'Philippe', 'Michel', 'Joseph']
        
        # Noms allemands féminins communs
        female_names_de = ['Maria', 'Anna', 'Greta', 'Gisela', 'Petra', 'Claudia', 'Eva', 'Monika', 'Renate']
        male_names_de = ['Hans', 'Klaus', 'Werner', 'Franz', 'Josef', 'Friedrich', 'Wilhelm', 'Johann', 'Heinrich']
        
        all_female = female_names_fr + female_names_de
        all_male = male_names_fr + male_names_de
        
        if speaker_name in all_female:
            gender = "female"
        elif speaker_name in all_male:
            gender = "male"
        else:
            # Choix aléatoire si nom inconnu
            gender = random.choice(["female", "male"])
        
        self.genders[speaker_name] = gender
        return gender

    def get_voice_for_speaker(self, speaker_name):
        """Retourne une voix unique pour ce locuteur"""
        
        if speaker_name in self.speaker_voices:
            return self.speaker_voices[speaker_name]
        
        # Déterminer le genre du locuteur
        if self.forced_gender:
            gender = self.forced_gender
        else:
            gender = self.assign_gender_to_speaker(speaker_name)
        
        # Obtenir une voix unique (pas encore utilisée)
        voices = VoiceConfig.VOICES[self.langue][gender]
        available_voices = [v for v in voices if v not in self.used_voices]
        
        if not available_voices:
            # Réinitialiser si plus de voix disponibles
            self.used_voices.clear()
            available_voices = voices
        
        voice = random.choice(available_voices)
        self.used_voices.add(voice)
        self.speaker_voices[speaker_name] = voice
        
        return voice


class EdgeTTSGenerator:
    """Génère l'audio avec Edge TTS (génère MP3 directement, sans ffmpeg)"""
    
    # Mapping des langues vers les voix Edge TTS
    EDGE_VOICES = {
        "fr": {
            "female": "fr-FR-DeniseNeural",
            "male": "fr-FR-HenriNeural"
        },
        "eng": {
            "female": "en-GB-LibbyNeural",
            "male": "en-GB-RyanNeural"
        },
        "us": {
            "female": "en-US-AriaNeural",
            "male": "en-US-GuyNeural"
        },
        "esp": {
            "female": "es-ES-ElviraNeural",
            "male": "es-ES-AlvaroNeural"
        },
        "hisp": {
            "female": "es-MX-MartaNeural",
            "male": "es-MX-JorgeNeural"
        },
        "nl": {
            "female": "nl-NL-FennaNeural",
            "male": "nl-NL-CoenNeural"
        },
        "co": {
            "female": "ko-KR-SunHiNeural",
            "male": "ko-KR-InJoonNeural"
        }
    }
    
    def __init__(self, langue="fr", gender=None):
        self.langue = langue
        # Convertir gender de français vers anglais
        if gender == "femme":
            self.gender = "female"
        elif gender == "homme":
            self.gender = "male"
        else:
            self.gender = gender
    
    async def generate_audio_from_text_async(self, text, output_file, voice=None):
        """Génère un fichier MP3 à partir du texte (async)"""
        try:
            import edge_tts
        except ImportError:
            return False, "❌ edge-tts non installé"
        
        # Valider le texte
        if not text or not text.strip():
            return False, "❌ Texte vide"
        
        if voice is None:
            # Choisir une voix par défaut
            gender = self.gender or "female"
            voice = self.EDGE_VOICES.get(self.langue, {}).get(gender, "fr-FR-DeniseNeural")
        
        try:
            # Limiter la longueur du texte (Edge TTS a des limites)
            max_length = 10000
            if len(text) > max_length:
                text = text[:max_length]
                print(f"⚠️  Texte tronqué à {max_length} caractères pour Edge TTS")
            
            comm = edge_tts.Communicate(text=text, voice=voice)
            await asyncio.wait_for(comm.save(output_file), timeout=30.0)
            
            # Vérifier que le fichier a été créé et n'est pas vide
            from pathlib import Path
            if not Path(output_file).exists() or Path(output_file).stat().st_size == 0:
                return False, f"❌ Edge TTS n'a pas généré de fichier audio valide"
            
            return True, f"✅ Audio généré (Edge TTS): {voice}"
        except asyncio.TimeoutError:
            return False, f"❌ Timeout Edge TTS (30s dépassé)"
        except Exception as e:
            error_msg = str(e)
            if "No audio" in error_msg:
                return False, f"❌ Edge TTS ne peut pas synthétiser ce texte. Vérifiez la langue '{self.langue}' et la voix '{voice}'"
            return False, f"❌ Erreur Edge TTS: {error_msg}"
    
    def generate_audio_from_text(self, text, output_file, voice=None):
        """Génère un fichier MP3 à partir du texte (wrapper sync)"""
        try:
            # Si le texte est très long, le diviser en chunks
            if len(text) > 2000:
                return self._generate_audio_chunked(text, output_file, voice)
            
            return asyncio.run(self.generate_audio_from_text_async(text, output_file, voice))
        except Exception as e:
            return False, f"❌ Erreur lors de l'exécution async Edge TTS: {str(e)}"
    
    def _generate_audio_chunked(self, text, output_file, voice=None):
        """Génère l'audio Edge TTS en divisant le texte en chunks"""
        from pathlib import Path
        
        print(f"📦 Texte long ({len(text)} chars), division en chunks...")
        
        # Diviser par paragraphes
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunk_files = []
        temp_dir = Path(output_file).parent
        
        for i, paragraph in enumerate(paragraphs):
            chunk_file = temp_dir / f"_edge_chunk_{i}.mp3"
            chunk_files.append(chunk_file)
            
            print(f"📝 Chunk {i+1}/{len(paragraphs)}: {len(paragraph)} chars...")
            
            # Générer le chunk
            success, msg = asyncio.run(self.generate_audio_from_text_async(paragraph, str(chunk_file), voice))
            if not success:
                # Nettoyer les chunks partiels
                for f in chunk_files:
                    f.unlink(missing_ok=True)
                return False, msg
        
        # Combiner les fichiers MP3 avec ffmpeg
        try:
            import subprocess
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for chunk in chunk_files:
                    f.write(f"file '{chunk.absolute()}'\n")
            
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file.absolute()),
                '-c', 'copy', '-y', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Nettoyer les fichiers temporaires
            concat_file.unlink(missing_ok=True)
            for chunk in chunk_files:
                chunk.unlink(missing_ok=True)
            
            if result.returncode == 0:
                return True, f"✅ Audio généré (en chunks): {voice or 'Edge TTS'}"
            else:
                return False, f"❌ Erreur ffmpeg: {result.stderr}"
        
        except FileNotFoundError:
            # ffmpeg non disponible, retourner simplement le premier chunk
            print("⚠️  ffmpeg non disponible, utilisation du premier chunk")
            try:
                chunk_files[0].rename(output_file)
                for chunk in chunk_files[1:]:
                    chunk.unlink(missing_ok=True)
                return True, f"✅ Audio généré (chunk 1): {voice or 'Edge TTS'}"
            except Exception as e:
                return False, f"❌ Erreur: {str(e)}"
        except Exception as e:
            # Nettoyer en cas d'erreur
            for chunk in chunk_files:
                chunk.unlink(missing_ok=True)
            return False, f"❌ Erreur lors de la combinaison: {str(e)}"
    
    async def generate_dialogue_audio_async(self, dialogue_segments, output_file):
        """Génère un MP3 à partir de segments de dialogue (async)"""
        try:
            import edge_tts
        except ImportError:
            return False, "❌ edge-tts non installé"
        
        if not dialogue_segments:
            return False, "❌ Aucun segment de dialogue"
        
        # Choisir des voix aléatoires pour chaque locuteur
        speakers_voices = {}
        available_voices = list(self.EDGE_VOICES.get(self.langue, {"female": "fr-FR-DeniseNeural", "male": "fr-FR-HenriNeural"}).values())
        
        # Générer un fichier MP3 pour chaque segment
        segment_files = []
        
        for i, (speaker, text) in enumerate(dialogue_segments):
            if not text or not text.strip():
                continue
                
            # Obtenir ou assigner une voix pour ce locuteur
            if speaker not in speakers_voices:
                speakers_voices[speaker] = random.choice(available_voices)
            
            edge_voice = speakers_voices[speaker]
            
            # Générer l'audio pour cette partie
            segment_file = f"/tmp/segment_{i}_{len(dialogue_segments)}.mp3"
            
            try:
                comm = edge_tts.Communicate(text=text, voice=edge_voice)
                await asyncio.wait_for(comm.save(segment_file), timeout=30.0)
                
                # Vérifier que le fichier a été créé
                from pathlib import Path
                if Path(segment_file).exists() and Path(segment_file).stat().st_size > 0:
                    segment_files.append(segment_file)
                else:
                    return False, f"❌ Segment {i} n'a pas généré de fichier valide"
                    
            except asyncio.TimeoutError:
                return False, f"❌ Timeout Edge TTS sur le segment {i}"
            except Exception as e:
                error_msg = str(e)
                if "No audio" in error_msg:
                    return False, f"❌ Edge TTS ne peut pas synthétiser le segment {i}"
                return False, f"❌ Erreur sur le segment {i}: {error_msg}"
        
        # Fusionner les MP3 (simple concaténation)
        if segment_files:
            try:
                # Concaténation simple des MP3
                with open(output_file, 'wb') as outfile:
                    for seg_file in segment_files:
                        with open(seg_file, 'rb') as infile:
                            outfile.write(infile.read())
                
                # Nettoyer les segments temporaires
                import os
                for seg_file in segment_files:
                    try:
                        os.remove(seg_file)
                    except:
                        pass
                
                return True, f"✅ Dialogue MP3 généré (Edge TTS): {output_file}"
            except Exception as e:
                return False, f"❌ Erreur lors de la fusion: {str(e)}"
        
        return False, "❌ Aucun segment généré"
    
    def generate_dialogue_audio(self, dialogue_segments, output_file, output_format='mp3'):
        """Génère un MP3 à partir de segments de dialogue (wrapper sync)"""
        try:
            return asyncio.run(self.generate_dialogue_audio_async(dialogue_segments, output_file))
        except Exception as e:
            return False, f"❌ Erreur lors de l'exécution async dialogue Edge TTS: {str(e)}"


class AzureTTSGenerator:
    """Génère l'audio avec Azure Text-to-Speech"""

    def __init__(self, langue="fr", gender=None, voice_name=None, speed=1.0):
        if not HAS_AZURE:
            raise RuntimeError("Azure Speech SDK non installé")
        
        self.langue = langue
        
        # Convertir gender de français vers anglais (femme → female, homme → male)
        if gender == "femme":
            self.gender = "female"
        elif gender == "homme":
            self.gender = "male"
        else:
            self.gender = gender
        
        self.voice_name = voice_name  # Nom spécifique de voix (prioritaire sur gender)
        self.speed = speed  # Vitesse de lecture (0.6 à 1.0)
        self.api_key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION", "eastus")
        
        if not self.api_key:
            raise ValueError("Variable AZURE_SPEECH_KEY non trouvée dans .env")
        
        # Initialiser le client Azure
        self.speech_config = speechsdk.SpeechConfig(
            subscription=self.api_key,
            region=self.region
        )
        
        # Configurer le format de sortie en MP3 directement
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

    def generate_audio_from_text(self, text, output_file, voice=None):
        """Génère un fichier MP3 à partir du texte"""
        
        if voice is None:
            # Utiliser voice_name si spécifié, sinon gender, sinon aléatoire
            voice = VoiceConfig.get_voice(self.langue, self.gender, self.voice_name)
        
        self.speech_config.speech_synthesis_voice_name = voice
        
        # Configurer les timeouts pour Azure (en millisecondes)
        # Augmenter pour les textes longs ou connexions lentes
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_InitialSilenceTimeoutMs,
            "120000"  # 120 secondes pour l'attente initiale
        )
        self.speech_config.set_property(
            speechsdk.PropertyId.SpeechServiceConnection_EndSilenceTimeoutMs,
            "120000"  # 120 secondes pour la fin du silence
        )
        
        # Si le texte est très long (>2000 chars), le diviser en chunks
        if len(text) > 2000:
            return self._generate_audio_chunked(text, output_file, voice)
        else:
            return self._synthesize_to_file(text, output_file, voice)
    
    def _synthesize_to_file(self, text, output_file, voice):
        """Synthétise le texte en fichier MP3 (sans chunking)"""
        # Configurer la sortie audio
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        
        # Créer le synthétiseur
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=self.speech_config,
            audio_config=audio_config
        )
        
        # Créer le SSML avec contrôle de vitesse
        # Convertir speed (0.6-1.0) en pourcentage pour SSML (-40% à 0%)
        speed_percent = int((self.speed - 1.0) * 100)
        speed_str = f"{speed_percent:+d}%" if speed_percent != 0 else "0%"
        
        # Si le texte contient déjà des balises SSML (prosody, break, etc.),
        # on l'insère directement sans wrapper prosody rate pour éviter les conflits
        # Sinon, on wrappe avec prosody rate pour contrôler la vitesse
        if '<prosody' in text or '<break' in text or '<emphasis' in text:
            # Texte avec SSML: on applique le rate globalement AUTOUR des balises existantes
            # Note: on garde le rate dans le wrapper principal, les balises internes ont priorité
            ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{voice[:5]}">
                <voice name="{voice}">
                    <prosody rate="{speed_str}">
                        {text}
                    </prosody>
                </voice>
            </speak>'''
        else:
            # Texte sans SSML: wrapper standard
            ssml = f'''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="{voice[:5]}">
                <voice name="{voice}">
                    <prosody rate="{speed_str}">
                        {text}
                    </prosody>
                </voice>
            </speak>'''
        
        # Générer l'audio avec SSML - 2 tentatives avec pause très longue pour laisser retomber les 429
        max_retries = 2
        retry_delay = 60  # 1 minute entre tentatives si 429/timeout
        for attempt in range(max_retries):
            try:
                result = synthesizer.speak_ssml_async(ssml).get()
                
                if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                    return True, f"✅ Audio généré: {voice}"
                elif result.reason == speechsdk.ResultReason.Canceled:
                    cancellation = result.cancellation_details
                    error_msg = f"Annulé: {cancellation.reason}"
                    if cancellation.error_details:
                        error_msg += f" - {cancellation.error_details}"
                    
                    # Retry pour 429 ou timeout - pause longue
                    if ("Timeout" in error_msg or "429" in error_msg or "Too many requests" in error_msg) and attempt < max_retries - 1:
                        error_type = 'Rate limit' if ('429' in error_msg or 'Too many' in error_msg) else 'Timeout'
                        print(f"⏱️  {error_type} Azure, pause {retry_delay}s avant nouvelle tentative...")
                        time.sleep(retry_delay)
                        continue
                    
                    return False, f"❌ Erreur TTS: {error_msg}"
                else:
                    return False, f"❌ Erreur TTS: Raison inconnue - {result.reason}"
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⏱️  Exception, pause {retry_delay}s avant nouvelle tentative: {str(e)[:100]}")
                    time.sleep(retry_delay)
                    continue
                return False, f"❌ Erreur TTS: {str(e)}"
        
        return False, "❌ Erreur TTS: Max retries atteint"
    
    def _generate_audio_chunked(self, text, output_file, voice):
        """Génère l'audio en divisant le texte en chunks
        
        Divise par paragraphes et génère les audios séparément,
        puis les combine en un seul fichier.
        """
        import subprocess
        from pathlib import Path
        
        print(f"📦 Texte long ({len(text)} chars), division en chunks...")
        
        # Diviser par paragraphes
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunk_files = []
        temp_dir = Path(output_file).parent
        
        for i, paragraph in enumerate(paragraphs):
            chunk_file = temp_dir / f"_chunk_{i}.mp3"
            chunk_files.append(chunk_file)
            
            print(f"📝 Chunk {i+1}/{len(paragraphs)}: {len(paragraph)} chars...")
            
            # Générer le chunk
            success, msg = self._synthesize_to_file(paragraph, str(chunk_file), voice)
            if not success:
                # Nettoyer les chunks partiels
                for f in chunk_files:
                    f.unlink(missing_ok=True)
                return False, msg
        
        # Combiner les fichiers MP3 avec ffmpeg (ou alternative pydub)
        try:
            concat_file = temp_dir / "concat.txt"
            with open(concat_file, 'w') as f:
                for chunk in chunk_files:
                    f.write(f"file '{chunk.absolute()}'\n")
            
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', str(concat_file.absolute()),
                '-c', 'copy', '-y', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            # Nettoyer le fichier concat
            concat_file.unlink(missing_ok=True)
            
            # Vérifier le résultat
            if result.returncode == 0:
                # Succès: nettoyer les chunks
                for chunk in chunk_files:
                    chunk.unlink(missing_ok=True)
                return True, f"✅ Audio généré (en chunks): {voice}"
            elif result.returncode < 0:
                # ffmpeg a été tué (signal), essayer pydub
                print(f"⚠️  ffmpeg crash detected (signal {-result.returncode}), essai avec pydub...")
                return self._combine_with_pydub(chunk_files, output_file, voice)
            else:
                print(f"⚠️  ffmpeg error (code {result.returncode}), essai avec pydub...")
                return self._combine_with_pydub(chunk_files, output_file, voice)
        
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            # ffmpeg non disponible ou timeout, essayer pydub
            print(f"⚠️  ffmpeg indisponible ({type(e).__name__}), essai avec pydub...")
            return self._combine_with_pydub(chunk_files, output_file, voice)
        except Exception as e:
            print(f"⚠️  Erreur inattendue ({str(e)}), essai avec pydub...")
            return self._combine_with_pydub(chunk_files, output_file, voice)
    
    def _combine_with_pydub(self, chunk_files, output_file, voice):
        """Combine les chunks avec pydub (alternative à ffmpeg) ou concaténation binaire"""
        try:
            from pydub import AudioSegment
            
            # Combiner tous les chunks
            combined = AudioSegment.empty()
            for i, chunk_file in enumerate(chunk_files):
                print(f"   Ajout chunk {i+1}/{len(chunk_files)}...")
                segment = AudioSegment.from_mp3(str(chunk_file))
                combined += segment
            
            # Exporter le résultat
            combined.export(output_file, format="mp3")
            
            # Nettoyer les chunks
            for chunk in chunk_files:
                chunk.unlink(missing_ok=True)
            
            return True, f"✅ Audio généré (chunks combinés avec pydub): {voice}"
        except (ImportError, ModuleNotFoundError):
            # pydub non disponible, essayer la concaténation binaire
            print("⚠️  pydub non disponible (Python 3.13+), essai de concaténation binaire...")
            try:
                # Concaténation binaire simple des MP3
                with open(output_file, 'wb') as outfile:
                    for i, chunk_file in enumerate(chunk_files):
                        print(f"   Ajout chunk {i+1}/{len(chunk_files)}...")
                        with open(chunk_file, 'rb') as infile:
                            outfile.write(infile.read())
                
                # Nettoyer les chunks
                for chunk in chunk_files:
                    chunk.unlink(missing_ok=True)
                
                return True, f"✅ Audio généré (concaténation binaire de {len(chunk_files)} chunks): {voice}"
            except Exception as e2:
                print(f"⚠️  Erreur concaténation ({str(e2)}), fallback sur premier chunk")
                return self._fallback_first_chunk(chunk_files, output_file, voice)
        except Exception as e:
            print(f"⚠️  Erreur pydub ({str(e)}), fallback sur premier chunk")
            return self._fallback_first_chunk(chunk_files, output_file, voice)
    
    def _fallback_first_chunk(self, chunk_files, output_file, voice):
        """Fallback: utiliser seulement le premier chunk si ffmpeg échoue"""
        try:
            chunk_files[0].rename(output_file)
            for chunk in chunk_files[1:]:
                chunk.unlink(missing_ok=True)
            return True, f"✅ Audio généré (chunk 1 seulement, ffmpeg indisponible): {voice}"
        except Exception as e:
            return False, f"❌ Erreur lors du fallback: {str(e)}"

    def generate_dialogue_audio(self, dialogue_segments, output_file, output_format='mp3'):
        """Génère un fichier audio à partir de segments de dialogue
        
        Args:
            dialogue_segments: Liste de tuples (locuteur, texte)
            output_file: Chemin du fichier de sortie
            output_format: 'mp3' ou 'wav' (défaut: 'mp3')
        
        Note: Azure génère directement en MP3 ou WAV selon output_format
        Les segments sont concaténés en un seul fichier
        Pour les dialogues, --voix spécifique est ignoré (plusieurs voix nécessaires)
        """
        
        # Pour les dialogues, on utilise gender mais on ignore voice_name (plusieurs voix nécessaires)
        voice_assigner = DialogueVoiceAssigner(self.langue, self.gender)
        
        # Générer un fichier MP3/WAV pour chaque segment
        segment_files = []
        extension = '.mp3' if output_format == 'mp3' else '.wav'
        
        for i, (speaker, text) in enumerate(dialogue_segments):
            # Obtenir une voix pour ce locuteur
            voice = voice_assigner.get_voice_for_speaker(speaker)
            
            # Générer l'audio pour cette partie
            segment_file = f"/tmp/segment_{i}_{len(dialogue_segments)}{extension}"
            success, msg = self.generate_audio_from_text(text, segment_file, voice)
            
            if success:
                segment_files.append(segment_file)
            else:
                print(f"  📍 Segment {i}: {msg}")
                return False, f"❌ Erreur lors de la génération du segment {i}: {msg}"
        
        # Fusionner les fichiers audio
        if segment_files:
            try:
                import os
                
                # Simple concaténation binaire (fonctionne pour MP3 et WAV)
                with open(output_file, 'wb') as outfile:
                    for seg_file in segment_files:
                        with open(seg_file, 'rb') as infile:
                            outfile.write(infile.read())
                
                # Nettoyer les segments temporaires
                for seg_file in segment_files:
                    try:
                        os.remove(seg_file)
                    except:
                        pass
                
                return True, f"✅ Dialogue {output_format.upper()} généré: {output_file}"
            
            except Exception as e:
                return False, f"❌ Erreur: {str(e)}"
        
        return False, "❌ Aucun segment généré"


def main():
    parser = argparse.ArgumentParser(
        description="Convertit un fichier Markdown en MP3 avec Azure TTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python md2mp3.py texte.md -l fr
  python md2mp3.py texte.md -l all --voix femme
  python md2mp3.py dialogue.md -l fr (voix aléatoires pour chaque personnage)
  python md2mp3.py article.md -l us --voix homme
        """
    )

    parser.add_argument(
        "fichier",
        help="Fichier Markdown à convertir"
    )

    parser.add_argument(
        "-l", "--langue",
        required=True,
        choices=['fr', 'all', 'eng', 'us', 'esp', 'hisp', 'nl', 'at', 'co', 'it'],
        help="Langue (fr=français, all=allemand, at=allemand autrichien, eng=anglais UK, us=anglais US, esp=espagnol, hisp=hispanique, nl=néerlandais, co=coréen)"
    )

    parser.add_argument(
        "-g", "--genre",
        choices=['femme', 'homme'],
        default=None,
        help="Genre de voix (défaut: aléatoire). Ignoré si --voix est spécifié."
    )

    parser.add_argument(
        "-v", "--voix",
        default=None,
        help="Nom spécifique de voix (ex: 'denise', 'henri', 'aria'). Prioritaire sur --genre. Utilisez --help pour voir toutes les voix disponibles."
    )

    parser.add_argument(
        "--vitesse",
        type=float,
        default=1.0,
        help="Vitesse de lecture de 0.6 (très ralenti) à 1.0 (vitesse normale). Défaut: 1.0"
    )

    parser.add_argument(
        "--format",
        choices=['mp3', 'wav'],
        default='mp3',
        help="Format de sortie (défaut: mp3, utiliser wav si ffmpeg ne fonctionne pas)"
    )

    # Option pour activer la conversion Markdown→SSML (emphases et pauses)
    parser.add_argument(
        "--ssml",
        action='store_true',
        help="Activer la conversion Markdown→SSML: *mot*, **mot**, [p], [p:ms]"
    )

    args = parser.parse_args()

    # Throttle global pour éviter les 429 si plusieurs appels rapprochés
    MIN_GAP = float(os.getenv("MD2MP3_MIN_GAP", "70"))  # secondes entre deux synthèses
    THROTTLE_FILE = "/tmp/md2mp3_last_call"
    try:
        last_ts = None
        if os.path.exists(THROTTLE_FILE):
            with open(THROTTLE_FILE, "r") as f:
                last_ts = float(f.read().strip())
        now = time.time()
        if last_ts:
            gap = now - last_ts
            if gap < MIN_GAP:
                wait = MIN_GAP - gap
                print(f"⏳ Throttle global: pause {wait:.1f}s pour éviter 429 (MIN_GAP={MIN_GAP}s)")
                time.sleep(wait)
        # Mettre à jour le timestamp dès le démarrage de cette synthèse
        with open(THROTTLE_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        # En cas d'erreur de throttle, continuer sans bloquer la génération
        pass

    # Valider la vitesse
    if args.vitesse < 0.6 or args.vitesse > 1.0:
        print(f"❌ Erreur: La vitesse doit être entre 0.6 et 1.0 (valeur fournie: {args.vitesse})")
        return 1

    # Vérifier que le fichier existe
    if not os.path.exists(args.fichier):
        print(f"❌ Erreur: Fichier '{args.fichier}' non trouvé")
        return 1

    # Lire le fichier Markdown
    with open(args.fichier, 'r', encoding='utf-8') as f:
        content = f.read()

    # Déterminer le fichier de sortie
    if args.format == 'wav':
        output_file = args.fichier.replace('.md', '.wav')
    else:
        output_file = args.fichier.replace('.md', '.mp3')

    print(f"📄 Lecture: {args.fichier}")
    print(f"🌍 Langue: {args.langue}")
    
    # Afficher la voix choisie
    if args.voix:
        print(f"🎤 Voix: {args.voix}")
    elif args.genre:
        print(f"🎤 Genre: {args.genre}")
    else:
        print(f"🎤 Voix: aléatoire")
    
    print(f"⏱️  Vitesse: {args.vitesse}x" + (" (ralenti)" if args.vitesse < 1.0 else ""))
    print(f"📦 Format: {args.format}")
    print()

    try:
        # Nettoyer le texte avec la langue appropriée
        cleaned_text = MarkdownCleaner.clean_text(content, args.langue, enable_ssml=args.ssml)
        
        # Détecter si c'est un dialogue
        is_dialogue, dialogue_lines = MarkdownCleaner.detect_dialogue(cleaned_text)
        
        if is_dialogue:
            print("🎭 Dialogue détecté")
            
            # Parser les lignes de dialogue
            dialogue_segments = []
            for line in dialogue_lines:
                speaker, text = MarkdownCleaner.parse_dialogue_line(line)
                if speaker:
                    dialogue_segments.append((speaker, text))
            
            # Générer l'audio du dialogue (Azure TTS uniquement)
            try:
                tts = AzureTTSGenerator(args.langue, args.genre, args.voix, args.vitesse)
                success, msg = tts.generate_dialogue_audio(dialogue_segments, output_file, args.format)
            except Exception as e:
                success = False
                msg = f"❌ Azure TTS indisponible: {str(e)}\n💡 Vérifiez AZURE_SPEECH_KEY et AZURE_SPEECH_REGION dans .env"
        else:
            print("📖 Texte standard")
            
            # Générer l'audio du texte (Azure TTS uniquement)
            try:
                tts = AzureTTSGenerator(args.langue, args.genre, args.voix, args.vitesse)
                success, msg = tts.generate_audio_from_text(cleaned_text, output_file)
            except Exception as e:
                success = False
                msg = f"❌ Azure TTS indisponible: {str(e)}\n💡 Vérifiez AZURE_SPEECH_KEY et AZURE_SPEECH_REGION dans .env"
        
        if success:
            print(msg)
            print(f"✅ Succès: {output_file}")
            return 0
        else:
            print(msg)
            return 1

    except Exception as e:
        print(f"❌ Erreur: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
