#!/usr/bin/env python3
"""
Script pour régénérer le vocabulaire de tous les documents avec la nouvelle règle (35 mots fixes).
Optimisation: ne regénère que si le nombre de mots actuels est <= 28 (ancienne règle en %).
Ne modifie que la section vocabulaire, ne regénère pas les textes.

Usage:
    python regenerate_vocabulary.py
"""

import os
import re
import yaml
from pathlib import Path
from genmp3 import TextGenerator, LanguageConfig

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
    # Compter les lignes contenant | ou →
    count = 0
    for line in vocab_section.split('\n'):
        if '|' in line or '→' in line:
            count += 1
    
    return count

def format_vocabulary(vocabulary, langue_code):
    """Formate le vocabulaire en markdown"""
    lines = []
    for word, translation in vocabulary:
        lines.append(f"{word} | {translation}")
    return "\n".join(lines)

def regenerate_doc_vocabulary(folder_path):
    """Régénère le vocabulaire pour un document si nécessaire"""
    text_file = os.path.join(folder_path, 'text.md')
    
    if not os.path.exists(text_file):
        return None, "Fichier text.md non trouvé"
    
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire le frontmatter
    frontmatter, body = extract_frontmatter(content)
    
    if not frontmatter:
        return None, "Pas de frontmatter YAML trouvé"
    
    # Vérifier les champs requis
    langue = frontmatter.get('langue')
    niveau = frontmatter.get('niveau')
    prompt = frontmatter.get('prompt')
    
    if not all([langue, niveau, prompt]):
        return None, f"Champs manquants: langue={langue}, niveau={niveau}, prompt={prompt}"
    
    # Chercher le code langue correspondant
    lang_code = None
    for code, config in LanguageConfig.LANGUAGES.items():
        if config['display'] == langue:
            lang_code = code
            break
    
    if not lang_code:
        return None, f"Langue non reconnue: {langue}"
    
    lang_config = LanguageConfig.get_config(lang_code)
    
    # Compter le vocabulaire actuel
    current_vocab_count = count_current_vocabulary(body, lang_config)
    
    # Si vocabulaire >= 29, pas besoin de regénérer (déjà à 35 ou plus)
    if current_vocab_count >= 29:
        return current_vocab_count, f"Déjà à jour ({current_vocab_count} mots)"
    
    # Extraire le texte
    text_only = extract_text_only(body, lang_config)
    if not text_only:
        return None, "Pas de section de texte trouvée"
    
    # Générer le vocabulaire (35 mots fixes)
    try:
        generator = TextGenerator()
        vocabulary = generator.generate_vocabulary(lang_code, text_only, prompt, niveau)
        
        if not vocabulary:
            return None, "Vocabulaire vide"
        
        # Formater le vocabulaire
        vocab_formatted = format_vocabulary(vocabulary, lang_code)
        
        # Chercher la position de la section vocabulaire dans le contenu
        vocab_label = lang_config['label_vocab']
        vocab_section_pattern = rf'(## {re.escape(vocab_label)}\n\n)(.*?)(\Z)'
        
        # Remplacer la section vocabulaire
        new_body = re.sub(
            vocab_section_pattern,
            rf'\1{vocab_formatted}\3',
            body,
            flags=re.DOTALL
        )
        
        # Reconstituer le fichier avec le frontmatter
        yaml_str = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
        new_content = f"---\n{yaml_str}---\n{new_body}"
        
        # Sauvegarder
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return len(vocabulary), f"✓ Mise à jour {current_vocab_count} → {len(vocabulary)} mots"
        
    except Exception as e:
        return None, f"Erreur: {str(e)}"

def main():
    docs_dir = './docs'
    
    if not os.path.exists(docs_dir):
        print(f"Erreur: {docs_dir} non trouvé")
        return
    
    folders = sorted([d for d in os.listdir(docs_dir) if os.path.isdir(os.path.join(docs_dir, d))])
    
    print(f"🔄 Régénération du vocabulaire pour {len(folders)} documents...")
    print("(Seuls les documents avec <= 28 mots seront regénérés)")
    print("=" * 80)
    
    updated_count = 0
    already_up_to_date = 0
    error_count = 0
    
    for i, folder_name in enumerate(folders, 1):
        folder_path = os.path.join(docs_dir, folder_name)
        vocab_count, message = regenerate_doc_vocabulary(folder_path)
        
        if vocab_count is not None:
            if "Déjà à jour" in message:
                already_up_to_date += 1
                status = "➖"
            else:
                updated_count += 1
                status = "✓"
            print(f"[{i:3d}/{len(folders)}] {folder_name:<50} {status} {message}")
        else:
            error_count += 1
            print(f"[{i:3d}/{len(folders)}] {folder_name:<50} ✗ {message}")
    
    print("=" * 80)
    print(f"✓ Mises à jour: {updated_count}")
    print(f"➖ Déjà à jour: {already_up_to_date}")
    print(f"✗ Erreurs: {error_count}")
    print(f"📊 Total: {len(folders)}")

if __name__ == "__main__":
    main()
