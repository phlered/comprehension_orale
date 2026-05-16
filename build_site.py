#!/usr/bin/env python3
"""
Script pour générer le site web statique à partir des ressources générées dans docs/
Crée metadata.json et copie les fichiers nécessaires vers site_langues/
"""

import os
import json
import re
import shutil
import unicodedata
from pathlib import Path
from datetime import datetime

# Configuration des chemins
SCRIPT_DIR = Path(__file__).parent
DOCS_DIR = SCRIPT_DIR / "docs"
SITE_DIR = SCRIPT_DIR / "site_langues"
RESOURCES_DIR = SITE_DIR / "resources"

# Mapping des langues
LANGUAGE_MAP = {
    "Français": "fr",
    "Allemand": "all",
    "Allemand (Autriche)": "all",
    "Anglais": "eng",
    "Anglais (US)": "eng",
    "Anglais (UK)": "eng",
    "Espagnol": "esp",
    "Espagnol (Espagne)": "esp",
    "Espagnol (Amérique latine)": "esp",
    "Espagnol (Amérique du Sud)": "esp",
    "Néerlandais": "nl",
    "Coréen": "cor",
    "Italien": "it"
}

LANGUAGE_NAMES = {
    "fr": "Français",
    "all": "Allemand",
    "eng": "Anglais",
    "esp": "Espagnol",
    "nl": "Néerlandais",
    "cor": "Coréen",
    "it": "Italien"
}


def slugify(value):
    """Normalise en ASCII sûr pour les URLs/dossiers (accents supprimés)."""
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "resource"


def extract_frontmatter(text_file):
    """Extrait les métadonnées du front matter YAML d'un fichier text.md"""
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire le front matter (entre --- et ---)
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', content, re.DOTALL)
    if not match:
        return None, None
    
    frontmatter_text = match.group(1)
    body = match.group(2)
    
    # Parser le front matter
    metadata = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()
    
    return metadata, body


def extract_text_and_vocab(body):
    """Extrait le texte et le vocabulaire depuis le corps du markdown"""
    # Extraire le texte (section ## Tekst, ## Text, ## Texto, ## Texte, ## 텍스트, ## Testo)
    text_match = re.search(r'##\s+(Tekst|Text|Texto|Texte|텍스트|Testo)\s*\n\n(.*?)(?=\n##|$)', body, re.DOTALL)
    text_content = text_match.group(2).strip() if text_match else ""
    
    # Extraire le vocabulaire (section ## Woordenschat, ## Wortschatz, ## Vocabulario, etc.)
    vocab_match = re.search(r'##\s+(Woordenschat|Wortschatz|Vocabulario|Vocabulaire|Vocabulary|어휘|Vocabolario)\s*\n\n(.*?)$', body, re.DOTALL)
    vocab_content = vocab_match.group(2).strip() if vocab_match else ""
    
    return text_content, vocab_content


def scan_docs_directory():
    """Scanne le répertoire docs/ et génère les métadonnées"""
    resources = []
    
    for folder in DOCS_DIR.iterdir():
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        
        text_file = folder / "text.md"
        audio_file = folder / "audio.mp3"
        
        if not text_file.exists() or not audio_file.exists():
            print(f"⚠️  Dossier incomplet ignoré : {folder.name}")
            continue
        
        # Extraire métadonnées
        metadata, body = extract_frontmatter(text_file)
        if not metadata:
            print(f"⚠️  Pas de front matter dans : {folder.name}")
            continue
        
        # Extraire texte et vocabulaire
        text_content, vocab_content = extract_text_and_vocab(body)
        
        # Convertir la langue
        langue_full = metadata.get('langue', '')
        langue_code = LANGUAGE_MAP.get(langue_full, '')
        
        if not langue_code:
            print(f"⚠️  Langue inconnue '{langue_full}' dans : {folder.name}")
            continue
        
        slug = slugify(folder.name)

        # Créer l'objet ressource (id = slug pour stabilité côté site)
        resource = {
            "id": slug,
            "langue": langue_code,
            "prompt": metadata.get('prompt', ''),
            "resume": metadata.get('resume', metadata.get('prompt', '')),  # Fallback sur prompt si pas de résumé
            "niveau": metadata.get('niveau', ''),
            "classe": metadata.get('classe', ''),  # Si disponible
            "axe": metadata.get('axe', ''),  # Si disponible
            "genre": metadata.get('voix', metadata.get('genre', '')),  # Prioriser voix sur genre
            "drapeau": metadata.get('drapeau', ''),  # Nouveau: drapeau
            "voix_variant": metadata.get('voix_variant', ''),  # Nouveau: variante de voix
            "date": metadata.get('date_generation', ''),
            "longueur": int(metadata.get('longueur', 0)),
            "text_preview": text_content[:200] + "..." if len(text_content) > 200 else text_content,
            "vocab_count": len(re.findall(r'^\s*[-*]\s+\*\*', vocab_content, re.MULTILINE)),
            "audio_path": f"resources/{slug}/audio.mp3",
            "text_path": f"resources/{slug}/text.md"
        }
        
        resources.append(resource)
        print(f"✅ {folder.name} -> {slug} - {langue_full} - {resource['prompt'][:50]} {resource.get('drapeau', '')}")
    
    return resources


def copy_resources():
    """Copie les ressources (audio + text.md) vers site_langues/resources/, en nettoyant d'abord."""
    if RESOURCES_DIR.exists():
        shutil.rmtree(RESOURCES_DIR)
    RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    
    for folder in DOCS_DIR.iterdir():
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        
        text_file = folder / "text.md"
        audio_file = folder / "audio.mp3"
        
        if not text_file.exists() or not audio_file.exists():
            continue
        
        slug = slugify(folder.name)
        dest_folder = RESOURCES_DIR / slug
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(audio_file, dest_folder / "audio.mp3")
        shutil.copy2(text_file, dest_folder / "text.md")


def generate_metadata_json(resources):
    """Génère le fichier metadata.json"""
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "total_resources": len(resources),
        "languages": list(set(r['langue'] for r in resources)),
        "resources": resources
    }
    
    output_file = SITE_DIR / "metadata.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ metadata.json généré avec {len(resources)} ressources")
    
    # Statistiques
    by_language = {}
    for r in resources:
        lang = r['langue']
        by_language[lang] = by_language.get(lang, 0) + 1
    
    print("\n📊 Statistiques par langue :")
    for lang, count in sorted(by_language.items()):
        print(f"   {LANGUAGE_NAMES.get(lang, lang)}: {count} ressources")


def main():
    print("🔨 Génération du site web...")
    print(f"📂 Dossier docs: {DOCS_DIR}")
    print(f"📂 Dossier site: {SITE_DIR}\n")
    
    # Scanner et extraire métadonnées
    print("📖 Scan des ressources...\n")
    resources = scan_docs_directory()
    
    if not resources:
        print("❌ Aucune ressource trouvée !")
        return
    
    # Copier les ressources
    print("\n📋 Copie des ressources...")
    copy_resources()
    
    # Générer metadata.json
    print("\n📝 Génération de metadata.json...")
    generate_metadata_json(resources)
    
    print("\n✨ Site généré avec succès !")
    print(f"👉 Répertoire: {SITE_DIR}")


if __name__ == "__main__":
    main()
