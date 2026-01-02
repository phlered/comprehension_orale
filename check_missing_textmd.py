#!/usr/bin/env python3
"""
Script pour identifier et lister les documents sans fichier text.md.

Usage:
    python check_missing_textmd.py
"""

import os
from pathlib import Path

def main():
    docs_dir = './docs'
    
    if not os.path.exists(docs_dir):
        print(f"Erreur: {docs_dir} non trouvé")
        return
    
    folders = sorted([d for d in os.listdir(docs_dir) if os.path.isdir(os.path.join(docs_dir, d))])
    
    print(f"🔍 Vérification des documents...")
    print("=" * 80)
    
    missing_textmd = []
    valid = 0
    
    for folder_name in folders:
        folder_path = os.path.join(docs_dir, folder_name)
        text_file = os.path.join(folder_path, 'text.md')
        
        if not os.path.exists(text_file):
            missing_textmd.append(folder_path)
        else:
            valid += 1
    
    print(f"✓ Documents valides (avec text.md): {valid}")
    print(f"✗ Documents manquants (sans text.md): {len(missing_textmd)}")
    print("=" * 80)
    
    if missing_textmd:
        print("\n📋 Documents sans text.md :\n")
        for path in missing_textmd:
            folder_name = os.path.basename(path)
            # Lister ce qui existe dans le dossier
            contents = os.listdir(path)
            print(f"  {folder_name}")
            print(f"    Contenu: {', '.join(contents) if contents else '(vide)'}")
    else:
        print("\n✓ Tous les documents ont un fichier text.md !")

if __name__ == "__main__":
    main()
