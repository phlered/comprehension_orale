#!/usr/bin/env python3
"""
Exemples d'utilisation du script CLI app.py

Exécutez ces commandes pour générer du contenu dans différentes langues et niveaux.
"""

EXAMPLES = {
    "allemand_b1_court": {
        "description": "Allemand niveau B1, 150 mots, voix femme (par défaut)",
        "command": 'python3 app.py -l all -p "Les animaux domestiques" --niveau B1'
    },
    "anglais_uk_b2": {
        "description": "Anglais UK niveau B2, 200 mots, voix homme",
        "command": 'python3 app.py -l eng -p "Climate change" --longueur 200 --niveau B2 --voix homme'
    },
    "anglais_us_a1": {
        "description": "Anglais US niveau A1, 100 mots",
        "command": 'python3 app.py -l us -p "Daily routine" --longueur 100 --niveau A1'
    },
    "espagnol_a2": {
        "description": "Espagnol Espagne niveau A2, avec métadonnées scolaires",
        "command": 'python3 app.py -l esp -p "La familia" --niveau A2 --niveau-scolaire 2 --axe axe1'
    },
    "espagnol_hisp_b1": {
        "description": "Espagnol Amérique du Sud niveau B1",
        "command": 'python3 app.py -l hisp -p "La gastronomía latinoamericana" --niveau B1'
    },
    "allemand_b2_long": {
        "description": "Allemand niveau B2, 300 mots, voix homme",
        "command": 'python3 app.py -l all -p "Technologie und Zukunft" --longueur 300 --niveau B2 --voix homme'
    },
    "neerlandais": {
        "description": "Néerlandais niveau B1",
        "command": 'python3 app.py -l nl -p "Koken en recepten" --niveau B1'
    },
    "coreen": {
        "description": "Coréen niveau A2",
        "command": 'python3 app.py -l cor -p "가족 관계" --niveau A2'
    },
    "allemand_seconde": {
        "description": "Allemand A2, Seconde, Axe citoyenneté",
        "command": 'python3 app.py -l all -p "Droits humains" --niveau A2 --niveau-scolaire 2 --axe axe4'
    },
    "anglais_premiere": {
        "description": "Anglais B1, Première, Axe art et culture",
        "command": 'python3 app.py -l eng -p "Shakespeare and British literature" --niveau B1 --niveau-scolaire 1 --axe axe3'
    }
}

if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("EXEMPLES D'UTILISATION DU SCRIPT CLI app.py")
    print("=" * 80)
    print()
    
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        # Mode exécution
        if len(sys.argv) > 2:
            key = sys.argv[2]
            if key in EXAMPLES:
                ex = EXAMPLES[key]
                print(f"🚀 {ex['description']}")
                print(f"📝 {ex['command']}")
                print()
                import subprocess
                result = subprocess.run(ex['command'], shell=True)
                sys.exit(result.returncode)
            else:
                print(f"❌ Exemple '{key}' non trouvé")
                print(f"\nExemples disponibles: {', '.join(EXAMPLES.keys())}")
                sys.exit(1)
    else:
        # Mode affichage
        for idx, (key, ex) in enumerate(EXAMPLES.items(), 1):
            print(f"{idx}. {key.upper()}")
            print(f"   📌 {ex['description']}")
            print(f"   📝 {ex['command']}")
            print()
        
        print("=" * 80)
        print("POUR EXÉCUTER UN EXEMPLE:")
        print("  python3 examples.py run <key>")
        print()
        print("Exemple:")
        print("  python3 examples.py run allemand_b1_court")
        print("=" * 80)
