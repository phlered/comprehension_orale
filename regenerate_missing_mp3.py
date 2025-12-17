#!/usr/bin/env python3
"""
Régénère les MP3 manquants pour les docs qui ont text.md mais pas audio.mp3.
Lit le frontmatter pour déterminer la langue et la vitesse.
"""

import os
import re
import subprocess
from pathlib import Path
from datetime import datetime

# Mapping langue frontmatter → code md2mp3
LANG_MAP = {
    "Français": "fr",
    "Néerlandais": "nl",
    "Anglais (UK)": "eng",
    "Anglais (US)": "us",
    "Espagnol (Espagne)": "esp",
    "Espagnol (Amérique du Sud)": "hisp",
    "Allemand": "all",
    "Coréen": "co",
    "Italien": "it",
}

# Vitesse par niveau
SPEED_MAP = {
    "A1": 0.75,
    "A2": 0.80,
    "B1": 0.85,
    "B2": 0.90,
    "C1": 0.95,
    "C2": 1.00,
}

def extract_frontmatter(text_md_path):
    """Extrait langue, niveau et genre du frontmatter"""
    with open(text_md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extraire le frontmatter YAML
    match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    if not match:
        return None, None, None
    
    frontmatter = match.group(1)
    
    # Extraire langue
    langue_match = re.search(r'^langue:\s*(.+)$', frontmatter, re.MULTILINE)
    langue = langue_match.group(1).strip() if langue_match else None
    
    # Extraire niveau
    niveau_match = re.search(r'^niveau:\s*(.+)$', frontmatter, re.MULTILINE)
    niveau = niveau_match.group(1).strip() if niveau_match else None
    
    # Extraire genre
    genre_match = re.search(r'^genre:\s*(.+)$', frontmatter, re.MULTILINE)
    genre = genre_match.group(1).strip() if genre_match else None
    
    return langue, niveau, genre

def generate_mp3(doc_folder, text_md_path, langue_code, vitesse, genre):
    """Génère le MP3 pour un document"""
    
    cmd = [
        ".venv312/bin/python",
        "md2mp3.py",
        str(text_md_path),
        "-l", langue_code,
        "-g", genre if genre else "femme",
        "--vitesse", str(vitesse)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Vérifier que le MP3 a été généré
        temp_mp3 = text_md_path.parent / "_temp_text.mp3"
        audio_mp3 = text_md_path.parent / "audio.mp3"
        
        if temp_mp3.exists() and temp_mp3.stat().st_size > 0:
            # Renommer _temp_text.mp3 → audio.mp3
            temp_mp3.rename(audio_mp3)
            return True, audio_mp3.stat().st_size
        else:
            return False, "MP3 non généré"
    
    except subprocess.CalledProcessError as e:
        # Afficher stderr et stdout pour diagnostiquer
        error_msg = ""
        if e.stderr:
            error_msg += f"STDERR:\n{e.stderr}\n"
        if e.stdout:
            error_msg += f"STDOUT:\n{e.stdout}"
        if not error_msg:
            error_msg = str(e)
        return False, error_msg

def main():
    docs_dir = Path("docs")
    today = datetime.now().strftime("%Y%m%d")
    
    print(f"\n🔍 Recherche des docs créés aujourd'hui ({today})...")
    
    # Trouver tous les dossiers créés aujourd'hui
    folders = [f for f in docs_dir.iterdir() if f.is_dir() and today in f.name]
    
    if not folders:
        print(f"❌ Aucun dossier trouvé pour {today}")
        return
    
    print(f"✅ {len(folders)} dossier(s) trouvé(s)\n")
    
    # Filtrer ceux sans audio.mp3
    missing_audio = []
    for folder in folders:
        text_md = folder / "text.md"
        audio_mp3 = folder / "audio.mp3"
        
        if text_md.exists() and not audio_mp3.exists():
            missing_audio.append(folder)
    
    if not missing_audio:
        print("🎉 Tous les dossiers ont déjà leur audio.mp3 !")
        return
    
    print(f"⚠️  {len(missing_audio)} dossier(s) sans audio.mp3\n")
    print(f"{'='*80}")
    
    success = 0
    fail = 0
    
    for i, folder in enumerate(missing_audio, 1):
        text_md = folder / "text.md"
        
        # Extraire frontmatter
        langue, niveau, genre = extract_frontmatter(text_md)
        
        if not langue or not niveau:
            print(f"❌ [{i}/{len(missing_audio)}] {folder.name}: Frontmatter incomplet")
            fail += 1
            continue
        
        # Mapper langue et niveau
        langue_code = LANG_MAP.get(langue)
        vitesse = SPEED_MAP.get(niveau, 0.80)
        
        if not langue_code:
            print(f"❌ [{i}/{len(missing_audio)}] {folder.name}: Langue non reconnue ({langue})")
            fail += 1
            continue
        
        print(f"\n📝 [{i}/{len(missing_audio)}] {folder.name}")
        print(f"   Langue: {langue} ({langue_code}) | Niveau: {niveau} | Vitesse: {vitesse}x")
        
        # Générer MP3
        ok, result = generate_mp3(folder, text_md, langue_code, vitesse, genre)
        
        if ok:
            print(f"   ✅ MP3 généré ({result} bytes)")
            success += 1
        else:
            print(f"   ❌ Échec:")
            # Afficher l'erreur avec indentation
            for line in str(result).split('\n'):
                if line.strip():
                    print(f"      {line}")
            fail += 1
    
    # Résumé
    print(f"\n{'='*80}")
    print(f"📊 RÉSUMÉ")
    print(f"{'='*80}")
    print(f"✅ Succès: {success}")
    print(f"❌ Échecs: {fail}")
    print(f"📦 Total: {success + fail}")
    
    if success > 0:
        print(f"\n💡 Pensez à régénérer le site: ./site.sh build")

if __name__ == "__main__":
    main()
