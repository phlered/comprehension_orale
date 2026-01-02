#!/usr/bin/env python3
"""
Normalise tous les fichiers text.md ayant un vocabulaire au mauvais format.
Convertit: "mot | traduction" → "- **mot** → traduction"
"""
from pathlib import Path
import re

def normalize_vocabulary_section(content):
    """Normalise la section vocabulaire au format correct."""
    # Trouver la section vocabulaire (dernière section ## ...)
    m = re.match(r'^(.*)(## \w+.*?)$', content, re.DOTALL)
    if not m:
        return content
    
    prefix = m.group(1)
    vocab_section = m.group(2)
    
    # Séparer header et contenu
    lines = vocab_section.split('\n')
    header = lines[0]  # "## Vocabulaire" etc.
    vocab_lines = lines[1:]
    
    normalized = [header, '']
    
    for line in vocab_lines:
        if not line.strip():
            normalized.append('')
            continue
        
        # Déjà au bon format?
        if line.startswith('- **') and ('→' in line or '|' in line):
            # Convertir | en → si nécessaire
            if '|' in line and '→' not in line:
                line = line.replace(' | ', ' → ')
            normalized.append(line)
            continue
        
        # Mauvais format: "mot | traduction"
        if '|' in line and not line.startswith('-'):
            parts = line.split('|')
            if len(parts) >= 2:
                word = parts[0].strip()
                translation = '|'.join(parts[1:]).strip()  # Rejoindre si plusieurs |
                normalized.append(f"- **{word}** → {translation}")
            else:
                normalized.append(line)
            continue
        
        # Format inconnu: laisser tel quel
        normalized.append(line)
    
    return prefix + '\n'.join(normalized)


def main():
    docs = Path('docs')
    fixed = []
    skipped = []
    
    for folder in sorted(docs.iterdir()):
        if not folder.is_dir() or folder.name.startswith('.'):
            continue
        
        text_file = folder / 'text.md'
        if not text_file.exists():
            continue
        
        content = text_file.read_text(encoding='utf-8')
        normalized = normalize_vocabulary_section(content)
        
        if content == normalized:
            skipped.append(folder.name)
        else:
            text_file.write_text(normalized, encoding='utf-8')
            fixed.append(folder.name)
    
    print(f"✅ Normalisés: {len(fixed)}")
    if fixed[:5]:
        for name in fixed[:5]:
            print(f"  - {name}")
    if len(fixed) > 5:
        print(f"  ... et {len(fixed)-5} autres")
    
    print(f"\n⏭️  Inchangés: {len(skipped)}")

if __name__ == '__main__':
    main()
