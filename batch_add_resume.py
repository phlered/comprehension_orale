#!/usr/bin/env python3
"""
Script batch pour ajouter le champ 'resume' à tous les documents existants
qui n'en ont pas encore.
"""

import os
import re
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def extract_frontmatter(file_path):
    """Extrait le frontmatter YAML et le corps du document"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier s'il y a un frontmatter
    if not content.startswith('---'):
        return None, content
    
    # Extraire le frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        return None, content
    
    frontmatter = parts[1].strip()
    body = parts[2].strip()
    
    return frontmatter, body


def parse_yaml_simple(yaml_text):
    """Parse simple du YAML (ligne par ligne)"""
    data = {}
    for line in yaml_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            data[key.strip()] = value.strip()
    return data


def generate_resume(client, prompt):
    """Génère un résumé court du prompt"""
    resume_prompt = f"""Extrait le sujet principal de ce prompt d'apprentissage en 3 à 10 mots maximum (sans guillemets, sans ponctuation finale).
Le résumé doit être le thème concret, pas les instructions pédagogiques. Garde les articles si nécessaire pour la clarté.

Exemples:
- "Utilise un style journalistique pour parler des mutations génétiques au niveau seconde" → "Les mutations génétiques"
- "Écris un dialogue entre deux jeunes Allemands décrivant leur école" → "L'école en Allemagne"
- "Rédige un texte sur les traditions de Noël en Espagne" → "Les traditions de Noël en Espagne"
- "Comment fonctionne le système de vélo aux Pays-Bas ?" → "Le système de vélo aux Pays-Bas"
- "Génère un texte sur la crise de Suez" → "La crise de Suez"
- "Les animaux domestiques" → "Les animaux domestiques"

Prompt à résumer: {prompt}

Résumé (3-10 mots):"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": resume_prompt}],
        max_tokens=50,
        temperature=0.3
    )
    resume = response.choices[0].message.content.strip()
    resume = resume.strip('"\'.,;:!? ')
    return resume


def add_resume_to_file(file_path, client):
    """Ajoute le champ resume au fichier si absent"""
    frontmatter, body = extract_frontmatter(file_path)
    
    if frontmatter is None:
        print(f"  ⚠️  Pas de frontmatter")
        return False
    
    # Vérifier si resume existe déjà
    if 'resume:' in frontmatter:
        print(f"  ✓ Résumé déjà présent")
        return False
    
    # Parser le YAML pour extraire le prompt
    yaml_data = parse_yaml_simple(frontmatter)
    prompt = yaml_data.get('prompt', '')
    
    if not prompt:
        print(f"  ⚠️  Pas de prompt trouvé")
        return False
    
    # Générer le résumé
    print(f"  📝 Prompt: {prompt[:60]}...")
    resume = generate_resume(client, prompt)
    print(f"  ✅ Résumé: {resume}")
    
    # Insérer le resume après le prompt dans le frontmatter
    lines = frontmatter.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if line.startswith('prompt:'):
            new_lines.append(f'resume: {resume}')
    
    new_frontmatter = '\n'.join(new_lines)
    
    # Reconstruire le fichier
    new_content = f"---\n{new_frontmatter}\n---\n\n{body}"
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def main():
    print("🚀 Batch: Ajout de résumés aux documents existants\n")
    
    # Initialiser OpenAI
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Clé API OpenAI manquante")
        return
    
    client = OpenAI(api_key=api_key)
    
    # Parcourir tous les dossiers dans docs/
    docs_dir = Path(__file__).parent / "docs"
    
    if not docs_dir.exists():
        print(f"❌ Dossier docs/ introuvable")
        return
    
    folders = [f for f in docs_dir.iterdir() if f.is_dir() and not f.name.startswith('.')]
    total = len(folders)
    processed = 0
    skipped = 0
    
    print(f"📂 {total} dossiers trouvés\n")
    
    for i, folder in enumerate(folders, 1):
        text_file = folder / "text.md"
        
        if not text_file.exists():
            print(f"[{i}/{total}] {folder.name}: ⚠️  Pas de text.md")
            skipped += 1
            continue
        
        print(f"[{i}/{total}] {folder.name}:")
        
        if add_resume_to_file(text_file, client):
            processed += 1
        else:
            skipped += 1
        
        print()
    
    print("=" * 60)
    print(f"✅ Terminé!")
    print(f"   📝 Résumés ajoutés: {processed}")
    print(f"   ⏭️  Ignorés (déjà présents ou erreur): {skipped}")
    print(f"   📊 Total: {total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
