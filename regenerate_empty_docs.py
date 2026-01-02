#!/usr/bin/env python3
"""
Script pour supprimer les dossiers vides et régénérer les documents avec genmp3.py.
Tous les documents seront générés au niveau A2.

Usage:
    python regenerate_empty_docs.py
"""

import os
import shutil
import subprocess
import sys

# Configuration des documents à régénérer
DOCS_TO_REGENERATE = [
    {
        "folder": "celebrer_un_annivers_20251216_1850",
        "lang": "fr",
        "prompt": "Célébrer un anniversaire"
    },
    {
        "folder": "describe_how_a_frien_20251221_1226",
        "lang": "eng",
        "prompt": "Describe how a friend or family member is important to you"
    },
    {
        "folder": "preparer_un_repas_de_20251216_1851",
        "lang": "fr",
        "prompt": "Préparer un repas de fête"
    },
    {
        "folder": "presente_la_vie_quot_20251217_1138",
        "lang": "fr",
        "prompt": "Présente la vie quotidienne"
    },
    {
        "folder": "un_collegien_espagno_20251218_1057",
        "lang": "esp",
        "prompt": "Un colegien español describe su día en la escuela"
    },
    {
        "folder": "un_repas_au_restaura_20251215_1651",
        "lang": "fr",
        "prompt": "Un repas au restaurant"
    },
    {
        "folder": "viaggiare_in_italia_20251215_1757",
        "lang": "it",
        "prompt": "Viaggiare in Italia"
    }
]

def main():
    docs_dir = './docs'
    
    if not os.path.exists(docs_dir):
        print(f"Erreur: {docs_dir} non trouvé")
        return
    
    print("🗑️  Suppression des dossiers vides...")
    print("=" * 80)
    
    for doc_info in DOCS_TO_REGENERATE:
        folder_path = os.path.join(docs_dir, doc_info["folder"])
        if os.path.exists(folder_path) and not os.listdir(folder_path):
            shutil.rmtree(folder_path)
            print(f"✓ Supprimé: {doc_info['folder']}")
    
    print("\n🔄 Régénération des documents en niveau A2...")
    print("=" * 80)
    
    success_count = 0
    error_count = 0
    
    for i, doc_info in enumerate(DOCS_TO_REGENERATE, 1):
        lang = doc_info["lang"]
        prompt = doc_info["prompt"]
        
        print(f"\n[{i}/{len(DOCS_TO_REGENERATE)}] Génération: {prompt[:50]}...")
        print(f"    Langue: {lang}, Niveau: A2")
        
        try:
            # Appeler genmp3.py
            cmd = [
                ".venv312/bin/python",
                "genmp3.py",
                "-l", lang,
                "-p", prompt,
                "--niveau", "A2"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"    ✓ Succès")
                success_count += 1
            else:
                print(f"    ✗ Erreur (exit code {result.returncode})")
                if result.stderr:
                    print(f"    {result.stderr[:200]}")
                error_count += 1
        except subprocess.TimeoutExpired:
            print(f"    ✗ Timeout")
            error_count += 1
        except Exception as e:
            print(f"    ✗ Exception: {str(e)}")
            error_count += 1
    
    print("\n" + "=" * 80)
    print(f"✓ Réussis: {success_count}/{len(DOCS_TO_REGENERATE)}")
    print(f"✗ Erreurs: {error_count}/{len(DOCS_TO_REGENERATE)}")

if __name__ == "__main__":
    main()
