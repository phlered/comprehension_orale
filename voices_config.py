#!/usr/bin/env python3
"""
Module centralisé pour gérer les voix, drapeaux et détection de pays.
Gère:
1. Mapping voix Azure → drapeaux
2. Sélection aléatoire des variantes (60% eng/40% us, 80% esp/20% hisp)
3. Détection de pays pour adapter la voix au contexte
4. Détection du groupe d'âge du locuteur (enfant, adolescent, adulte, senior)
5. Sélection de voix appropriée selon âge et genre
"""

import random
import re


class SpeakerAgeDetector:
    """Détecte l'âge apparent du locuteur dans le texte pour choisir une voix adaptée."""
    
    # Patterns pour détecter adolescents et jeunes adultes (13-30 ans)
    ADOLESCENT_PATTERNS = [
        r'\b(I am|je suis|tengo|ho)\s+([1-2][0-9])\b',  # "I am 15", "je suis 20", "tengo 25" (13-29 ans)
        r'\b(I am|je suis|tengo|ho)\s+(thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|vingt|veintiuno|treize|quatorze|quinze|seize|dix-sept|dix-huit|dix-neuf)\b',
        r'\bstudent\b|\bestudiant\b|\bschoolgirl\b|\bscholary\b|\btélécolière\b|\bestudiant(e)?\b|\badolescent\b|\bjeune adulte\b',
        r'\bteen\b|\btéen\b|\btín\b|\byoung\b|\bjoven\b',
        r'\b(age|âge|años|years|ans)\s+([1-2][0-9])\b',  # "age 20", "âge 25", "años 22"
        r'\bmy name is\b.*\b(I am|je suis|tengo).*\b([1-2][0-9])\b',  # "my name is X and I am 20"
    ]
    
    # Patterns pour détecter enfants (5-12 ans)
    CHILD_PATTERNS = [
        r'\b(I am|je suis|tengo|ho)\s+[5-9]\b',  # "I am 7", "je suis 8"
        r'\b(I am|je suis|tengo|ho)\s+(five|six|seven|eight|nine|ten|eleven|twelve|cinq|six|sept|huit|neuf|dix|onze|douze)\b',
        r'\bkindergarten\b|\bprimary school\b|\bécole maternelle\b|\bécole primaire\b',
        r'\bchild\b|\bchildren\b|\benfants?\b|\bnene\b|\bnena\b',
    ]
    
    # Patterns pour détecter seniors (60+)
    SENIOR_PATTERNS = [
        r'\b(I am|je suis|tengo|ho)\s+([6-9][0-9]|100)\b',  # "I am 65", "je suis 72"
        r'\bgrandfather\b|\bgrandmother\b|\bgrands-parents\b|\babuelo\b|\babuela\b',
        r'\bretired\b|\bretraité\b|\bjubilado\b',
        r'\bsenior\b|\bpensioner\b|\bpensionné\b',
    ]
    
    @staticmethod
    def detect_speaker_age_group(text):
        """
        Analyse le texte pour détecter la tranche d'âge du locuteur.
        Retourne: 'adolescent', 'child', 'senior', ou None (par défaut adulte)
        """
        text_lower = text.lower()
        
        # Chercher patterns dans l'ordre de spécificité
        for pattern in SpeakerAgeDetector.SENIOR_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return 'senior'
        
        for pattern in SpeakerAgeDetector.CHILD_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return 'child'
        
        for pattern in SpeakerAgeDetector.ADOLESCENT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return 'adolescent'
        
        return None  # Adulte par défaut


class GenderDetector:
    """Détecte le genre du locuteur basé sur les prénoms et pronoms."""
    
    # Prénoms féminins courants (EN, FR, ES)
    FEMININE_NAMES = {
        'emily', 'alice', 'sarah', 'jessica', 'anna', 'maria', 'sophia', 'olivia', 'charlotte', 'amelia',
        'isabella', 'mia', 'evelyn', 'harper', 'lily', 'luna', 'grace', 'chloe', 'zoe', 'ella',
        'emma', 'jennifer', 'patricia', 'margaret', 'linda', 'barbara', 'susan', 'jessica', 'pamela', 'nancy',
        'catherine', 'christine', 'melissa', 'deborah', 'karen', 'nancy', 'sandra', 'ashley', 'dorothy', 'margaret',
        'marie', 'jeanne', 'francoise', 'isabelle', 'christine', 'martine', 'sylvie', 'dominique', 'valerie', 'veronique',
        'sophie', 'claire', 'nathalie', 'catherine', 'nicole', 'francoise', 'diane', 'christine', 'danielle', 'christine',
        'rosa', 'carmen', 'teresa', 'josefina', 'mariana', 'gabriela', 'alejandra', 'monica', 'diego', 'victoria',
        'sandra', 'patricia', 'gloria', 'rosa', 'elena', 'ana', 'laura', 'linda', 'karen', 'nancy',
        # Diminutifs et variantes courantes
        'liz', 'beth', 'kate', 'meg', 'sue', 'ann', 'lisa', 'jane', 'rose', 'ruby',
        'amy', 'amy', 'jen', 'nancy', 'diane', 'angela', 'sandra', 'ashley', 'julie', 'holly',
        'cathy', 'maggie', 'sammie', 'danny', 'jackie', 'casey', 'sam', 'alex', 'avery', 'riley',
    }
    
    # Prénoms masculins courants (EN, FR, ES)
    MASCULINE_NAMES = {
        'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph', 'thomas', 'charles', 'christopher',
        'daniel', 'matthew', 'anthony', 'mark', 'donald', 'steven', 'paul', 'andrew', 'joshua', 'kenneth',
        'kevin', 'brian', 'george', 'edward', 'ronald', 'timothy', 'jason', 'jeffrey', 'ryan', 'jacob',
        'gary', 'nicholas', 'eric', 'jonathan', 'stephen', 'larry', 'justin', 'scott', 'brandon', 'benjamin',
        'samuel', 'frank', 'gregory', 'raymond', 'patrick', 'jack', 'dennis', 'jerry', 'tyler', 'aaron',
        'pierre', 'jean', 'jacques', 'francois', 'marc', 'philippe', 'andre', 'paul', 'christophe', 'xavier',
        'luc', 'serge', 'bernard', 'gerald', 'claude', 'olivier', 'stephane', 'laurent', 'vincent', 'bruno',
        'carlos', 'juan', 'jose', 'miguel', 'luis', 'diego', 'francisco', 'rafael', 'antonio', 'pedro',
        'ramon', 'marcos', 'ricardo', 'manuel', 'sergio', 'daniel', 'manuel', 'javier', 'angel',
        # Diminutifs et variantes courantes
        'tom', 'tom', 'max', 'alex', 'ben', 'chris', 'greg', 'alex', 'steve', 'nick',
        'pete', 'joe', 'sam', 'dan', 'matt', 'luke', 'james', 'nick', 'leo', 'ethan',
        'noah', 'oliver', 'liam', 'elias', 'lucas', 'gabriel', 'henry', 'alexander', 'oscar', 'jack',
    }
    
    # Pronoms féminins
    FEMININE_PRONOUNS = {
        'she', 'her', 'hers', 'herself',  # Anglais
        'elle', 'la', 'les', 'lui', 'son', 'sa', 'ses',  # Français
        'ella', 'las', 'le', 'su', 'sus', 'suya',  # Espagnol
    }
    
    # Pronoms masculins
    MASCULINE_PRONOUNS = {
        'he', 'him', 'his', 'himself',  # Anglais
        'il', 'le', 'les', 'lui', 'son', 'sa', 'ses',  # Français
        'él', 'los', 'le', 'su', 'sus', 'suyo',  # Espagnol
    }
    
    @staticmethod
    def detect_speaker_gender(text):
        """
        Détecte le genre du locuteur basé sur les prénoms et pronoms.
        Retourne: 'femme', 'homme', ou None (indéterminé)
        """
        text_lower = text.lower()
        
        # Compter les occurrences de pronoms féminins vs masculins
        feminine_count = sum(1 for pronoun in GenderDetector.FEMININE_PRONOUNS if pronoun in text_lower)
        masculine_count = sum(1 for pronoun in GenderDetector.MASCULINE_PRONOUNS if pronoun in text_lower)
        
        # Extraire et analyser les prénoms (après "name is" ou "my name")
        name_patterns = [
            r'my name is (\w+)',
            r"i'm (\w+)",
            r'name is (\w+)',
            r'm\'appelle (\w+)',
            r'me llamo (\w+)',
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                name = match.strip().lower()
                # Enlever les caractères spéciaux
                name = re.sub(r'[^\w]', '', name)
                
                if name in GenderDetector.FEMININE_NAMES:
                    feminine_count += 3  # Pondération plus forte pour les prénoms
                elif name in GenderDetector.MASCULINE_NAMES:
                    masculine_count += 3
        
        # Décider basé sur le score
        if feminine_count > masculine_count:
            return 'femme'
        elif masculine_count > feminine_count:
            return 'homme'
        
        return None  # Indéterminé


class VoiceSelector:
    """Sélectionne une voix Azure optimale selon genre et âge détecté."""
    
    # Voix juvéniles/adolescentes/jeunes adultes (13-30 ans perçus)
    YOUNG_VOICES = {
        "en-US": {
            "female": ["en-US-AriaNeural", "en-US-AvaNeural", "en-US-EmmaNeural"],
            "male": ["en-US-BrianNeural", "en-US-EricNeural"]
        },
        "en-GB": {
            "female": ["en-GB-SoniaNeural", "en-GB-OliviaNeural"],
            "male": ["en-GB-RyanNeural", "en-GB-ElliotNeural"]
        },
        "es-ES": {
            "female": ["es-ES-EstrellaNeural", "es-ES-VerónicaNeural"],
            "male": ["es-ES-AlvaroNeural", "es-ES-ArnauNeural"]
        },
        "es-MX": {
            "female": ["es-MX-BeatrizNeural", "es-MX-CarlotaNeural"],
            "male": ["es-MX-JorgeNeural", "es-MX-GerardoNeural"]
        },
        "es-AR": {
            "female": ["es-AR-ElenaNeural"],
            "male": ["es-AR-TomasNeural"]
        },
        "fr-FR": {
            "female": ["fr-FR-DeniseNeural", "fr-FR-EloiseNeural", "fr-FR-VivienneNeural"],
            "male": ["fr-FR-HenriNeural", "fr-FR-AlainNeural", "fr-FR-ClaudeNeural"]
        },
        "de-DE": {
            "female": ["de-DE-KatjaNeural", "de-DE-AmalaNeural"],
            "male": ["de-DE-ConradNeural", "de-DE-BerndNeural"]
        },
        "nl-NL": {
            "female": ["nl-NL-FennaNeural", "nl-NL-ColetteNeural"],
            "male": ["nl-NL-MaartenNeural", "nl-NL-CoenNeural"]
        },
        "it-IT": {
            "female": ["it-IT-ElsaNeural", "it-IT-IsabellaNeural"],
            "male": ["it-IT-DiegoNeural", "it-IT-GiuseppeNeural"]
        }
    }
    
    # Voix neutres/adultes générales (défaut) - retiré les voix enfant comme BellaNeural
    ADULT_VOICES = {
        "en-US": {
            "female": ["en-US-AriaNeural", "en-US-EmmaNeural", "en-US-MichelleNeural"],
            "male": ["en-US-GuyNeural", "en-US-JasonNeural"]
        },
        "en-GB": {
            "female": ["en-GB-SoniaNeural", "en-GB-OliviaNeural"],
            "male": ["en-GB-ThomasNeural", "en-GB-RyanNeural"]
        },
        "es-ES": {
            "female": ["es-ES-ElviraNeural", "es-ES-EstrellaNeural", "es-ES-VerónicaNeural"],
            "male": ["es-ES-AlvaroNeural", "es-ES-ArnauNeural", "es-ES-TeoNeural"]
        },
        "es-MX": {
            "female": ["es-MX-MartaNeural", "es-MX-BeatrizNeural", "es-MX-CarlotaNeural"],
            "male": ["es-MX-JorgeNeural", "es-MX-GerardoNeural", "es-MX-LucianoNeural"]
        },
        "es-AR": {
            "female": ["es-AR-ElenaNeural"],
            "male": ["es-AR-TomasNeural"]
        },
        "fr-FR": {
            "female": ["fr-FR-DeniseNeural", "fr-FR-EloiseNeural", "fr-FR-VivienneNeural", "fr-FR-BrigitteNeural"],
            "male": ["fr-FR-HenriNeural", "fr-FR-AlainNeural", "fr-FR-ClaudeNeural", "fr-FR-JeromeNeural"]
        },
        "de-DE": {
            "female": ["de-DE-KatjaNeural", "de-DE-AmalaNeural", "de-DE-ElkeNeural"],
            "male": ["de-DE-ConradNeural", "de-DE-BerndNeural", "de-DE-ChristophNeural"]
        },
        "nl-NL": {
            "female": ["nl-NL-FennaNeural", "nl-NL-ColetteNeural"],
            "male": ["nl-NL-MaartenNeural", "nl-NL-CoenNeural"]
        },
        "it-IT": {
            "female": ["it-IT-ElsaNeural", "it-IT-IsabellaNeural"],
            "male": ["it-IT-DiegoNeural", "it-IT-GiuseppeNeural"]
        }
    }
    
    # Voix d'enfants (5-12 ans)
    CHILD_VOICES = {
        "en-US": {"female": ["en-US-AvaNeural"], "male": ["en-US-BrianNeural"]},
        "en-GB": {"female": ["en-GB-BellaNeural"], "male": ["en-GB-ElliotNeural"]},
    }
    
    # Voix graves/matures (35-55 ans perçus)
    MATURE_VOICES = {
        "en-US": {
            "female": ["en-US-MichelleNeural", "en-US-MonicaNeural"],
            "male": ["en-US-GuyNeural", "en-US-JasonNeural"]
        },
        "en-GB": {
            "female": ["en-GB-SoniaNeural"],
            "male": ["en-GB-ThomasNeural"]
        },
    }
    
    # Voix adultes neutres (fallback pour tous les cas non spécifiés)
    ADULT_VOICES = {
        "en-US": {
            "female": ["en-US-EmmaNeural", "en-US-JennyNeural"],
            "male": ["en-US-ChristopherNeural", "en-US-EricNeural"]
        },
        "en-GB": {
            "female": ["en-GB-OliviaNeural", "en-GB-SoniaNeural"],
            "male": ["en-GB-ThomasNeural", "en-GB-RyanNeural"]
        },
        "es-ES": {
            "female": ["es-ES-VerónicaNeural", "es-ES-IreneNeural"],
            "male": ["es-ES-AlvaroNeural", "es-ES-EliasNeural"]
        },
        "es-MX": {
            "female": ["es-MX-BeatrizNeural", "es-MX-MarinaNeural"],
            "male": ["es-MX-JorgeNeural", "es-MX-LibertoNeural"]
        },
        "es-AR": {
            "female": ["es-AR-ElenaNeural"],
            "male": ["es-AR-TomasNeural"]
        },
        "fr-FR": {
            "female": ["fr-FR-VivienneNeural", "fr-FR-BrigitteNeural", "fr-FR-CelesteNeural"],
            "male": ["fr-FR-ClaudeNeural", "fr-FR-JeromeNeural", "fr-FR-YvesNeural"]
        },
        "de-DE": {
            "female": ["de-DE-ElkeNeural", "de-DE-TanjaNeural"],
            "male": ["de-DE-ChristophNeural", "de-DE-KlausNeural"]
        },
        "nl-NL": {
            "female": ["nl-NL-ColetteNeural"],
            "male": ["nl-NL-MaartenNeural"]
        },
        "it-IT": {
            "female": ["it-IT-IsabellaNeural"],
            "male": ["it-IT-DiegoNeural"]
        },
        "ko-KR": {
            "female": ["ko-KR-SunHiNeural", "ko-KR-YuJinNeural"],
            "male": ["ko-KR-InJoonNeural", "ko-KR-SoonBokNeural"]
        }
    }
    
    @staticmethod
    def azure_to_shortname(azure_voice_id):
        """Convertit un ID Azure complet en shortname. Ex: 'en-GB-BellaNeural' → 'bella'"""
        if not azure_voice_id:
            return None
        # Extraire la partie après le tiret final, avant "Neural"
        # Pattern: "locale-FirstNameNeural" → "firstname"
        parts = azure_voice_id.split('-')
        if len(parts) >= 2:
            # Prendre la dernière partie et enlever "Neural"
            name_part = parts[-1].replace("Neural", "").lower()
            return name_part
        return None
    
    @staticmethod
    def select_voice_by_age_and_gender(locale, gender, age_group):
        """
        Sélectionne une voix Azure selon la locale, le genre et le groupe d'âge détecté.
        
        Args:
            locale: ex "en-US", "es-ES", "fr-FR"
            gender: "femme" ou "homme"
            age_group: "adolescent", "child", "senior", ou None (adulte)
        
        Returns:
            Shortname de la voix (ex: "bella") pour md2mp3.py, ou une voix adulte par défaut
        """
        gen = "female" if gender.lower() == "femme" else "male"
        
        # Child: chercher voix enfant si disponible
        if age_group == "child" and locale in VoiceSelector.CHILD_VOICES:
            voices = VoiceSelector.CHILD_VOICES[locale].get(gen, [])
            if voices:
                azure_id = random.choice(voices)
                return VoiceSelector.azure_to_shortname(azure_id)
        
        # Adolescent/Young: chercher voix juvénile
        if age_group == "adolescent" and locale in VoiceSelector.YOUNG_VOICES:
            voices = VoiceSelector.YOUNG_VOICES[locale].get(gen, [])
            if voices:
                azure_id = random.choice(voices)
                return VoiceSelector.azure_to_shortname(azure_id)
        
        # Senior/Mature: chercher voix grave
        if age_group == "senior" and locale in VoiceSelector.MATURE_VOICES:
            voices = VoiceSelector.MATURE_VOICES[locale].get(gen, [])
            if voices:
                azure_id = random.choice(voices)
                return VoiceSelector.azure_to_shortname(azure_id)
        
        # Fallback adulte neutre: utiliser ADULT_VOICES pour la locale (défaut sûr)
        if locale in VoiceSelector.ADULT_VOICES:
            voices = VoiceSelector.ADULT_VOICES[locale].get(gen, [])
            if voices:
                azure_id = random.choice(voices)
                return VoiceSelector.azure_to_shortname(azure_id)
        
        # Dernier recours: aucune voix trouvée
        return None


class VoiceVariantConfig:
    """Gère les variantes de voix (eng/us, esp/hisp) avec probabilités."""
    
    # Probabilités de sélection
    ENGLISH_PROBABILITIES = {"eng": 0.60, "us": 0.40}
    SPANISH_PROBABILITIES = {"esp": 0.80, "hisp": 0.20}
    
    @staticmethod
    def select_english_variant():
        """Retourne 'eng' ou 'us' avec probabilités 60%/40%."""
        return random.choices(
            ["eng", "us"],
            weights=[0.60, 0.40],
            k=1
        )[0]
    
    @staticmethod
    def select_spanish_variant():
        """Retourne 'esp' ou 'hisp' avec probabilités 80%/20%."""
        return random.choices(
            ["esp", "hisp"],
            weights=[0.80, 0.20],
            k=1
        )[0]


class FlagMapping:
    """Mappe les variantes de voix aux drapeaux des pays."""
    
    # Drapeaux par variante de langue
    FLAGS = {
        "eng": "🇬🇧",      # Royaume-Uni
        "us": "🇺🇸",       # États-Unis
        "esp": "🇪🇸",      # Espagne
        "hisp": "🇦🇷",     # Argentine (représentant l'Amérique latine)
        "fr": "🇫🇷",       # France
        "all": "🇩🇪",      # Allemagne
        "nl": "🇳🇱",       # Pays-Bas
        "cor": "🇰🇷",      # Corée
        "it": "🇮🇹",       # Italie
    }
    
    # Variantes possibles par pays mentionné dans le texte
    # Clés: patterns à rechercher (case-insensitive)
    # Ordonnées par spécificité (plus spécifique en premier)
    COUNTRY_VOICE_MAPPING = {
        # États-Unis - mots-clés
        "american": "us",
        "américain": "us",
        "américaine": "us",
        "united states": "us",
        "united states of america": "us",
        "états-unis": "us",
        "etats-unis": "us",
        "estados unidos": "us",
        "usa": "us",
        "american democracy": "us",
        "american election": "us",
        "american culture": "us",
        "american football": "us",
        "wall street": "us",
        "broadway": "us",
        "hollywood": "us",
        "las vegas": "us",
        "disneyland": "us",
        
        # Villes US principales
        "new york": "us",
        "los angeles": "us",
        "chicago": "us",
        "washington": "us",
        "boston": "us",
        "san francisco": "us",
        "seattle": "us",
        "miami": "us",
        "denver": "us",
        
        # États US
        "california": "us",
        "texas": "us",
        "florida": "us",
        "new york state": "us",
        
        # Personnages/Politique US
        "trump": "us",
        "biden": "us",
        "donald trump": "us",
        "joe biden": "us",
        
        # Royaume-Uni - mots-clés
        "british": "eng",
        "britannique": "eng",
        "britain": "eng",
        "great britain": "eng",
        "united kingdom": "eng",
        "england": "eng",
        "royaume-uni": "eng",
        "angleterre": "eng",
        "reino unido": "eng",
        "inglaterra": "eng",
        "english": "eng",
        "british culture": "eng",
        "big ben": "eng",
        "buckingham palace": "eng",
        "parliament": "eng",
        "westminster": "eng",
        
        # Villes UK
        "london": "eng",
        "londres": "eng",
        "manchester": "eng",
        "oxford": "eng",
        "cambridge": "eng",
        "edinburgh": "eng",
        "liverpool": "eng",
        "birmingham": "eng",
        "bristol": "eng",
        "york": "eng",
        "edinburgh": "eng",
        
        # Autres UK
        "thames": "eng",
        "scotland": "eng",
        "wales": "eng",
        "irish": "eng",
        "crown": "eng",
        
        # Argentine - mots-clés
        "argentina": "hisp",
        "argentine": "hisp",
        "argentina (es)": "hisp",
        "buenos aires": "hisp",
        "gaucho": "hisp",
        "tango": "hisp",
        "pampas": "hisp",
        "río de la plata": "hisp",
        "córdoba": "hisp",
        "mendoza": "hisp",
        "asado": "hisp",
        
        # Mexique - mots-clés
        "mexico": "hisp",
        "méxico": "hisp",
        "mexican": "hisp",
        "mexicain": "hisp",
        "mexicaine": "hisp",
        "mexico city": "hisp",
        "guadalajara": "hisp",
        "cancun": "hisp",
        "cancún": "hisp",
        "aztec": "hisp",
        "maya": "hisp",
        "yucatan": "hisp",
        "día de muertos": "hisp",
        "mariachi": "hisp",
        
        # Colombie - mots-clés
        "colombia": "hisp",
        "colombie": "hisp",
        "colombian": "hisp",
        "colombien": "hisp",
        "colombienne": "hisp",
        "bogota": "hisp",
        "bogotá": "hisp",
        "cartagena": "hisp",
        "medellín": "hisp",
        
        # Pérou - mots-clés
        "peru": "hisp",
        "pérou": "hisp",
        "peruvian": "hisp",
        "péruvien": "hisp",
        "lima": "hisp",
        "machu picchu": "hisp",
        "inca": "hisp",
        "cusco": "hisp",
        "quechua": "hisp",
        
        # Chili - mots-clés
        "chile": "hisp",
        "chili": "hisp",
        "chilean": "hisp",
        "chilien": "hisp",
        "santiago": "hisp",
        "atacama": "hisp",
        "atacama desert": "hisp",
        "patagonia": "hisp",
        
        # Espagne - mots-clés
        "spain": "esp",
        "espagne": "esp",
        "españa": "esp",
        "spanish": "esp",
        "espagnol": "esp",
        "español": "esp",
        "madrid": "esp",
        "barcelona": "esp",
        "seville": "esp",
        "sevilla": "esp",
        "valencia": "esp",
        "bilbao": "esp",
        "granada": "esp",
        "alhambra": "esp",
        "flamenco": "esp",
        "paella": "esp",
        "spanish culture": "esp",
        "castilian": "esp",
        "iberia": "esp",
        "basque": "esp",
        "catalonia": "esp",
        "cataluña": "esp",
        "cervantes": "esp",
        "don quixote": "esp",
        "gaudí": "esp",
        "sagrada familia": "esp",
    }
    
    @staticmethod
    def get_flag(variant_code):
        """Retourne le drapeau pour une variante donnée."""
        return FlagMapping.FLAGS.get(variant_code, "❓")
    
    @staticmethod
    def detect_country_voice(text):
        """
        Analyse le texte pour détecter si un pays spécifique y est mentionné.
        Retourne 'eng', 'us', 'esp' ou 'hisp' si un pays est détecté, sinon None.
        """
        text_lower = text.lower()
        
        # Chercher les patterns de pays mentionnés
        for country_pattern, voice_variant in FlagMapping.COUNTRY_VOICE_MAPPING.items():
            # Utiliser des limites de mots pour éviter les faux positifs
            pattern = r'\b' + re.escape(country_pattern) + r'\b'
            if re.search(pattern, text_lower):
                return voice_variant
        
        return None
    
    @staticmethod
    def select_voice_with_context(text, language_code):
        """
        Sélectionne une variante de voix selon:
        1. Le contexte du texte (détection de pays)
        2. Les probabilités de base sinon
        
        Args:
            text: Le texte généré
            language_code: La langue ('eng', 'us', 'esp', 'hisp', etc.)
        
        Returns:
            La variante sélectionnée (ex: 'eng' ou 'us')
        """
        # Pour les langues autres que l'anglais/espagnol, retourner directement
        if language_code not in ["eng", "us", "esp", "hisp"]:
            return language_code

        # Essayer de détecter un pays dans le texte (indicatif seulement)
        detected_voice = FlagMapping.detect_country_voice(text)

        # Cas Anglais: on ne choisit qu'entre eng/us
        if language_code in ["eng", "us"]:
            if detected_voice in ["eng", "us"]:
                return detected_voice
            # Détection d'un pays non anglophone: ignorer, rester dans la famille anglaise
            return VoiceVariantConfig.select_english_variant()

        # Cas Espagnol: on ne choisit qu'entre esp/hisp
        if language_code in ["esp", "hisp"]:
            if detected_voice in ["esp", "hisp"]:
                return detected_voice
            # Détection d'un pays non hispanophone (ex: USA/UK): ignorer, rester en esp/hisp
            return VoiceVariantConfig.select_spanish_variant()

        return language_code


# Exemple d'utilisation
if __name__ == "__main__":
    # Test sélection aléatoire
    print("Test sélection aléatoire (10x):")
    for _ in range(10):
        eng = VoiceVariantConfig.select_english_variant()
        esp = VoiceVariantConfig.select_spanish_variant()
        print(f"  Anglais: {eng} {FlagMapping.get_flag(eng)}, Espagnol: {esp} {FlagMapping.get_flag(esp)}")
    
    # Test détection de pays
    print("\nTest détection de pays:")
    texts = [
        "Les vaches en Argentine sont élevées dans les pampas.",
        "La démocratie américaine aux États-Unis est un système complexe.",
        "Le système de transport à Londres utilise le métro.",
        "La paella est un plat traditionnel de l'Espagne.",
    ]
    
    for text in texts:
        detected = FlagMapping.detect_country_voice(text)
        selected = FlagMapping.select_voice_with_context(text, "esp")
        print(f"  Texte: {text[:50]}...")
        print(f"    → Détecté: {detected}, Sélectionné: {selected} {FlagMapping.get_flag(selected)}\n")
