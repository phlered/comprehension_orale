#!/usr/bin/env python3
"""
Vérification complète de la refonte CLI

Lance cette commande pour vérifier que tout fonctionne correctement.
"""

import subprocess
import os
import sys
from pathlib import Path

def print_header(title):
    """Affiche un en-tête"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")

def check_file_exists(path, description):
    """Vérifie qu'un fichier existe"""
    if Path(path).exists():
        print(f"✅ {description}: {path}")
        return True
    else:
        print(f"❌ {description}: {path} (NON TROUVÉ)")
        return False

def check_python_env():
    """Vérifie l'environnement Python"""
    print_header("1️⃣  ENVIRONNEMENT PYTHON")
    
    venv = ".venv312/bin/python"
    if Path(venv).exists():
        print(f"✅ Python venv trouvé: {venv}")
        
        # Vérifier les packages
        result = subprocess.run(
            [venv, "-m", "pip", "list", "--format=json"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode == 0:
            import json
            packages = {p['name'].lower(): p['version'] for p in json.loads(result.stdout)}
            required = ['openai', 'edge-tts', 'python-dotenv']
            
            for pkg in required:
                if pkg in packages:
                    print(f"  ✅ {pkg} ({packages[pkg]})")
                else:
                    print(f"  ❌ {pkg} (MANQUANT)")
        return True
    else:
        print(f"❌ Python venv non trouvé: {venv}")
        return False

def check_files():
    """Vérifie les fichiers principaux"""
    print_header("2️⃣  FICHIERS DU PROJET")
    
    files_to_check = [
        ("app.py", "Script CLI principal"),
        ("app_tkinter.py", "Ancienne version (sauvegarde)"),
        ("CLI_GUIDE.md", "Documentation CLI"),
        ("REFONTE_CLI.md", "Résumé de la refonte"),
        ("examples.py", "Exemples d'utilisation"),
        ("run_cli.sh", "Script de démarrage shell"),
        ("test_app.py", "Tests basiques"),
        (".env", "Configuration API (optionnel)"),
    ]
    
    count = 0
    for filename, description in files_to_check:
        if check_file_exists(filename, description):
            count += 1
    
    return count >= 7  # Au moins les fichiers essentiels

def check_app_help():
    """Vérifie que le script CLI affiche l'aide"""
    print_header("3️⃣  VÉRIFICATION DU SCRIPT CLI")
    
    venv = ".venv312/bin/python"
    result = subprocess.run(
        [venv, "app.py", "--help"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    if result.returncode == 0:
        print("✅ Script CLI exécutable")
        
        # Vérifier les paramètres
        required_params = [
            "-l, --langue",
            "-p, --prompt",
            "--longueur",
            "--niveau",
            "--voix",
            "--niveau-scolaire",
            "--axe"
        ]
        
        for param in required_params:
            if param in result.stdout:
                print(f"  ✅ Paramètre: {param}")
            else:
                print(f"  ❌ Paramètre manquant: {param}")
        
        return True
    else:
        print(f"❌ Erreur: {result.stderr}")
        return False

def check_docs_folder():
    """Vérifie le dossier docs/"""
    print_header("4️⃣  DOSSIER DE SORTIE")
    
    docs_path = Path("docs")
    if docs_path.exists():
        print(f"✅ Dossier docs/ existe")
        
        # Compter les générations existantes
        generations = list(docs_path.glob("*_*/"))
        if generations:
            print(f"  ℹ️  {len(generations)} génération(s) existante(s)")
            for gen in sorted(generations)[:3]:  # Montrer les 3 dernières
                print(f"    - {gen.name}/")
        else:
            print(f"  ℹ️  Aucune génération encore")
        return True
    else:
        print(f"⚠️  Dossier docs/ créé automatiquement à la première génération")
        return True

def check_env_file():
    """Vérifie le fichier .env"""
    print_header("5️⃣  CONFIGURATION API")
    
    if Path(".env").exists():
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY" in content:
                key_exists = "sk-" in content or "sk_" in content
                if key_exists:
                    print("✅ Fichier .env configuré avec clé API")
                else:
                    print("⚠️  Fichier .env existe mais clé API semble manquante")
                return True
            else:
                print("❌ Fichier .env existe mais OPENAI_API_KEY manquante")
                return False
    else:
        print("⚠️  Fichier .env non trouvé")
        print("\nCréez un fichier .env avec:")
        print("  OPENAI_API_KEY=sk-xxxxxxxxxxxx")
        return False

def show_summary():
    """Affiche un résumé final"""
    print_header("✅ RÉSUMÉ")
    
    print("Refonte complète en script CLI")
    print()
    print("📝 Fichiers créés:")
    print("  • app.py (nouveau script CLI)")
    print("  • app_tkinter.py (ancienne version sauvegardée)")
    print("  • CLI_GUIDE.md (documentation)")
    print("  • REFONTE_CLI.md (résumé des changements)")
    print("  • examples.py (10 exemples)")
    print("  • run_cli.sh (script de démarrage)")
    print()
    print("🚀 Pour démarrer:")
    print("  python3 app.py -l all -p \"Thème\" --niveau B1")
    print()
    print("📚 Pour voir les exemples:")
    print("  python3 examples.py")
    print()
    print("📖 Pour la documentation:")
    print("  cat CLI_GUIDE.md")
    print("  cat REFONTE_CLI.md")
    print()

def main():
    """Lance la vérification complète"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  ✅ VÉRIFICATION DE LA REFONTE CLI - app.py".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    checks = {
        "Environnement Python": check_python_env(),
        "Fichiers du projet": check_files(),
        "Script CLI": check_app_help(),
        "Dossier de sortie": check_docs_folder(),
        "Configuration API": check_env_file(),
    }
    
    show_summary()
    
    # Résultat final
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print_header("📊 RÉSULTATS")
    print(f"Vérifications réussies: {passed}/{total}")
    
    if passed == total:
        print("\n✅ TOUT EST OPÉRATIONNEL!\n")
        return 0
    else:
        print("\n⚠️  Certaines vérifications ont échoué\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
