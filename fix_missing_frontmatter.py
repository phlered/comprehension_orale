#!/usr/bin/env python3
"""
Script pour identifier et réparer les documents sans frontmatter YAML valide.
Ajoute un frontmatter par défaut et regénère le vocabulaire si nécessaire.

Usage:
    python fix_missing_frontmatter.py
"""

import os
import re
import yaml
from pathlib import Path
from genmp3 import TextGenerator, LanguageConfig

def has_valid_frontmatter(content):
    """Vérifie si le fichier a un frontmatter YAML valide"""
    if not content.startswith('---\n'):
        return False
    
    match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return False
    
    try:
        yaml.safe_load(match.group(1))
        return True
    except yaml.YAMLError:
        return False

def extract_frontmatter(content):
    """Extrait le frontmatter YAML et le contenu"""
    match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            body = match.group(2).strip()
            return frontmatter, body
        except yaml.YAMLError:
            return None, content
    return None, content

def extract_text_only(content, lang_config):
    """Extrait seulement la section de texte (sans vocabulaire)"""
    label_text = lang_config['label_text']
    pattern = rf'## {re.escape(label_text)}\s*\n\n(.*?)(?=\n## |\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    return None

def count_current_vocabulary(content, lang_config):
    """Compte le nombre de mots de vocabulaire actuels"""
    label_vocab = lang_config['label_vocab']
    pattern = rf'## {re.escape(label_vocab)}\s*\n\n(.*?)(\Z)'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        return 0
    
    vocab_section = match.group(1).strip()
    count = 0
    for line in vocab_section.split('\n'):
        if '|' in line or '→' in line:
            count += 1
    
    return count

def format_vocabulary(vocabulary):
    """Formate le vocabulaire en markdown"""
    lines = []
    for word, translation in vocabulary:
        lines.append(f"{word} | {translation}")
    return "\n".join(lines)

def guess_language_from_content(content):
    """Essaie de deviner la langue en fonction des sections de titre"""
    # Chercher la première section ## (Text, Texte, Texto, etc.)
    match = re.search(r'## ([^\n]+)\n', content)
    if not match:
        return "fr"  # Par défaut français
    
    first_section = match.group(1).lower()
    
    # Map des mots-clés par langue
    keywords = {
        "fr": ["texte", "vocabulaire"],
        "eng": ["text", "vocabulary"],
        "us": ["text", "vocabulary"],
        "all": ["text", "wortschatz"],
        "esp": ["texto", "vocabulario"],
        "hisp": ["texto", "vocabulario"],
        "nl": ["tekst", "woordenschat"],
        "it": ["testo", "vocabolario"],
    }
    
    for lang_code, words in keywords.items():
        if any(word in first_section for word in words):
            return lang_code
    
    return "fr"  # Par défaut

def create_default_frontmatter(folder_name, lang_code, content):
    """Crée un frontmatter par défaut"""
    # Extraire le titre du dossier (avant le timestamp)
    title = re.sub(r'_\d{8}_\d{4}$', '', folder_name).replace('_', ' ').title()
    
    lang_config = LanguageConfig.get_config(lang_code)
    if not lang_config:
        lang_code = "fr"
        lang_config = LanguageConfig.get_config(lang_code)
    
    # Compter les mots du texte
    text_only = extract_text_only(content, lang_config)
    if text_only:
        word_count = len(text_only.split())
    else:
        word_count = len(content.split())
    
    # Déterminer le niveau par défaut selon la longueur
    if word_count < 170:
        niveau = "A1"
    elif word_count < 225:
        niveau = "A2"
    elif word_count < 275:
        niveau = "B1"
    elif word_count < 325:
        niveau = "B2"
    elif word_count < 375:
        niveau = "C1"
    else:
        niveau = "C2"
    
    from datetime import datetime
    frontmatter = {
        "langue": lang_config['display'],
        "prompt": title,
        "resume": title,
        "longueur": word_count,
        "niveau": niveau,
        "genre": "femme",
        "date_generation": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    return frontmatter

def fix_and_regenerate_vocabulary(folder_path, folder_name):
    """Répare le frontmatter et regénère le vocabulaire si nécessaire"""
    text_file = os.path.join(folder_path, 'text.md')
    
    if not os.path.exists(text_file):
        return None, "Fichier text.md non trouvé"
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier si le frontmatter existe et est valide
    if has_valid_frontmatter(content):
        return None, "Frontmatter déjà valide"
    
    # Extraire le contenu sans frontmatter existant
    body = content
    if content.startswith('---'):
        # Essayer de trouver la fin d'un frontmatter partiel
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if match:
            body = match.group(2)
        else:
            # Frontmatter partiel, le retirer
            match = re.match(r'^---\n.*?\n---\n(.*)$', content, re.DOTALL)
            if match:
                body = match.group(1)
    
    # Deviner la langue
    lang_code = guess_language_from_content(body)
    lang_config = LanguageConfig.get_config(lang_code)
    
    # Créer un frontmatter par défaut
    frontmatter = create_default_frontmatter(folder_name, lang_code, body)
    
    # Compter le vocabulaire actuel
    current_vocab_count = count_current_vocabulary(body, lang_config)
    
    # Regénérer le vocabulaire si <= 28 mots
    if current_vocab_count <= 28:
        try:
            # Extraire le texte
            text_only = extract_text_only(body, lang_config)
            if not text_only:
                # Si pas de section de texte trouvée, utiliser le body
                text_only = body
            
            # Générer le vocabulaire
            generator = TextGenerator()
            vocabulary = generator.generate_vocabulary(lang_code, text_only, frontmatter['prompt'], frontmatter['niveau'])
            
            if vocabulary:
                vocab_formatted = format_vocabulary(vocabulary)
                
                # Chercher la section vocabulaire dans le contenu
                vocab_label = lang_config['label_vocab']
                vocab_section_pattern = rf'(## {re.escape(vocab_label)}\n\n)(.*?)(\Z)'
                
                # Remplacer la section vocabulaire
                new_body = re.sub(
                    vocab_section_pattern,
                    rf'\1{vocab_formatted}\3',
                    body,
                    flags=re.DOTALL
                )
                body = new_body
                vocab_status = f"{current_vocab_count} → {len(vocabulary)} mots"
            else:
                vocab_status = f"{current_vocab_count} mots (pas regénéré)"
        except Exception as e:
            vocab_status = f"{current_vocab_count} mots (erreur: {str(e)})"
    else:
        vocab_status = f"{current_vocab_count} mots (déjà à jour)"
    
    # Reconstituer le fichier avec le frontmatter réparé
    yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
    new_content = f"---\n{yaml_str}---\n{body}"
    
    # Sauvegarder
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, f"✓ Frontmatter créé ({lang_config['display']}, {frontmatter['niveau']}) | Vocab: {vocab_status}"

def main():
    docs_dir = './docs'
    
    if not os.path.exists(docs_dir):
        print(f"Erreur: {docs_dir} non trouvé")
        return
    
    folders = sorted([d for d in os.listdir(docs_dir) if os.path.isdir(os.path.join(docs_dir, d))])
    
    print(f"🔧 Vérification et réparation des documents sans frontmatter...")
    print("=" * 80)
    
    fixed_count = 0
    already_valid = 0
    error_count = 0
    
    for i, folder_name in enumerate(folders, 1):
        folder_path = os.path.join(docs_dir, folder_name)
        result, message = fix_and_regenerate_vocabulary(folder_path, folder_name)
        
        if result is True:
            fixed_count += 1
            print(f"[{i:3d}/{len(folders)}] {folder_name:<45} {message}")
        elif result is None:
            already_valid += 1
        else:
            error_count += 1
            print(f"[{i:3d}/{len(folders)}] {folder_name:<45} ✗ {message}")
    
    print("=" * 80)
    print(f"✓ Réparés: {fixed_count}")
    print(f"✓ Déjà valides: {already_valid}")
    print(f"✗ Erreurs: {error_count}")
    print(f"📊 Total: {len(folders)}")

if __name__ == "__main__":
    main()
