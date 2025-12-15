#!/usr/bin/env python3
"""
Script pour convertir un fichier texte en audio MP3.
Utilise edge-tts pour la synthèse vocale.

Usage:
    python lit.py fichier.txt [OPTIONS]

Options:
    --voix VOIX       : Choix de la voix (homme/femme) [défaut: femme]
    --vitesse VITESSE : Vitesse de lecture en % (-30 à +30) [défaut: -30]
    --langue LANGUE   : Code langue (de/en/en-us/fr/es/nl/ko) [optionnel, détection auto]
                        Note: 'en' = anglais britannique, 'en-us' = anglais américain
    --output FICHIER  : Nom du fichier de sortie [défaut: audio_[timestamp].mp3]

Exemples:
    python lit.py texte.txt                                    # Détection automatique
    python lit.py texte.txt --voix homme --vitesse -10         # Avec paramètres
    python lit.py texte.txt --langue en --output mon_audio.mp3 # Force la langue
"""

import argparse
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import edge_tts
from langdetect import detect, LangDetectException

# Mapping des voix par langue et genre
VOIX_MAPPING = {
    'de': {'femme': 'de-DE-KatjaNeural', 'homme': 'de-DE-ConradNeural'},
    'en': {'femme': 'en-GB-SoniaNeural', 'homme': 'en-GB-RyanNeural'},
    'en-us': {'femme': 'en-US-JennyNeural', 'homme': 'en-US-GuyNeural'},
    'fr': {'femme': 'fr-FR-DeniseNeural', 'homme': 'fr-FR-HenriNeural'},
    'es': {'femme': 'es-ES-ElviraNeural', 'homme': 'es-ES-AlvaroNeural'},
    'nl': {'femme': 'nl-NL-ColetteNeural', 'homme': 'nl-NL-MaartenNeural'},
    'ko': {'femme': 'ko-KR-SunHiNeural', 'homme': 'ko-KR-InJoonNeural'},
}


def detecter_langue(texte: str) -> str:
    """Détecte automatiquement la langue du texte."""
    try:
        code_langue = detect(texte)
        # Mapper les codes de langdetect vers nos codes
        if code_langue in VOIX_MAPPING:
            return code_langue
        # Fallback sur l'allemand si langue non supportée
        print(f"⚠️  Langue détectée ({code_langue}) non supportée, utilisation de l'allemand par défaut.")
        return 'de'
    except LangDetectException:
        print("⚠️  Impossible de détecter la langue, utilisation de l'allemand par défaut.")
        return 'de'


async def text_to_speech(texte: str, voix: str, vitesse: int, output_file: str):
    """Convertit le texte en audio avec edge-tts."""
    rate_str = f"{vitesse:+d}%"
    communicate = edge_tts.Communicate(text=texte, voice=voix, rate=rate_str)
    await communicate.save(output_file)
    print(f"✓ Audio généré : {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Convertit un fichier texte en audio MP3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument('fichier', help="Fichier texte à lire")
    parser.add_argument('--voix', choices=['homme', 'femme'], default='femme',
                        help="Choix de la voix (défaut: femme)")
    parser.add_argument('--vitesse', type=int, default=-30,
                        help="Vitesse de lecture en %% (-30 à +30, défaut: -30)")
    parser.add_argument('--langue', choices=list(VOIX_MAPPING.keys()),
                        help="Code langue (optionnel, détection auto). 'en' = GB, 'en-us' = US")
    parser.add_argument('--output', help="Nom du fichier de sortie")

    args = parser.parse_args()

    # Vérification du fichier d'entrée
    fichier_path = Path(args.fichier)
    if not fichier_path.exists():
        print(f"❌ Erreur : Le fichier '{args.fichier}' n'existe pas.", file=sys.stderr)
        sys.exit(1)

    # Lecture du texte
    try:
        with open(fichier_path, 'r', encoding='utf-8') as f:
            texte = f.read().strip()
    except Exception as e:
        print(f"❌ Erreur lors de la lecture du fichier : {e}", file=sys.stderr)
        sys.exit(1)

    if not texte:
        print(f"❌ Erreur : Le fichier '{args.fichier}' est vide.", file=sys.stderr)
        sys.exit(1)

    # Vérification de la vitesse
    if not -30 <= args.vitesse <= 30:
        print("❌ Erreur : La vitesse doit être entre -30 et +30.", file=sys.stderr)
        sys.exit(1)

    # Détection ou sélection de la langue
    if args.langue:
        langue = args.langue
    else:
        print("🔍 Détection automatique de la langue...")
        langue = detecter_langue(texte)

    # Sélection de la voix
    voix_code = VOIX_MAPPING[langue][args.voix]

    # Nom du fichier de sortie
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"audio_{fichier_path.stem}_{timestamp}.mp3"

    # Génération de l'audio
    print(f"🔊 Génération de l'audio...")
    print(f"   Langue : {langue}")
    print(f"   Voix : {args.voix} ({voix_code})")
    print(f"   Vitesse : {args.vitesse:+d}%")
    
    try:
        asyncio.run(text_to_speech(texte, voix_code, args.vitesse, output_file))
    except Exception as e:
        print(f"❌ Erreur lors de la génération de l'audio : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
