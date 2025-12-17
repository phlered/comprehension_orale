#!/usr/bin/env python3
"""
Module centralisé pour gérer les voix, drapeaux et détection de pays.
Gère:
1. Mapping voix Azure → drapeaux
2. Sélection aléatoire des variantes (60% eng/40% us, 80% esp/20% hisp)
3. Détection de pays pour adapter la voix au contexte
"""

import random
import re


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
