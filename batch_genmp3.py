#!/usr/bin/env python3
"""
Script de génération batch de ressources à partir d'une liste de prompts.

Lit un fichier contenant une liste numérotée de prompts et génère automatiquement
des ressources pour chaque prompt dans les langues spécifiées.

Usage:
    ./batch.sh -f prompts/prompt.md -l nl,eng -n A1 --longueur 150
    ./batch.sh --prompts prompts/prompts_hollandais.md --langues nl --niveau B1 --dry-run
    ./batch.sh -f prompts/prompt.md -l eng,esp,all -n A2 -g homme
"""

import argparse
import re
import random
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Tuple


class PromptParser:
    """Parse les prompts depuis un fichier markdown"""
    
    @staticmethod
    def extract_prompts(filepath: str) -> List[str]:
        """
        Extrait les prompts d'un fichier markdown.
        Supporte les formats:
        - 1. Premier prompt
        - 2. Deuxième prompt
        """
        prompts = []
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern pour lignes numérotées: "1. ", "2. ", etc.
        # \s* étendu pour couvrir les caractères invisibles Unicode (U+2060 WORD JOINER, etc.)
        pattern = r'^\s*\d+[\.\s\u2060\u200b\u200c\u200d\ufeff]*\s*(.+)$'
        
        for line in content.split('\n'):
            # Nettoyer les caractères invisibles Unicode fréquents (copier-coller mobile)
            clean_line = line.replace('\u2060', '').replace('\u200b', '').replace('\u200c', '').replace('\u200d', '').replace('\ufeff', '')
            match = re.match(r'^\s*\d+\.\s*(.+)$', clean_line)
            if match:
                prompt_text = match.group(1).strip()
                if prompt_text:  # Ignorer les lignes vides
                    prompts.append(prompt_text)
        
        return prompts


class BatchGenerator:
    """Gère la génération batch de ressources"""
    
    def __init__(self, niveau: str, longueur: int, vitesse: float = None, 
                 genre: str = None, dry_run: bool = False, delai_entre_generations: float = 3.0, ssml: bool = False):
        self.niveau = niveau
        self.longueur = longueur if longueur is not None else self._default_length_for_level(niveau)
        self.vitesse = vitesse
        self.genre = genre
        self.dry_run = dry_run
        self.delai_entre_generations = delai_entre_generations
        self.ssml = ssml
        self.python_exe = ".venv312/bin/python"

    @staticmethod
    def _default_length_for_level(niveau: str) -> int:
        """Retourne la longueur par défaut en fonction du niveau CECRL"""
        defaults = {
            "A1": 150,
            "A2": 200,
            "B1": 250,
            "B2": 300,
            "C1": 350,
            "C2": 400,
        }
        return defaults.get(niveau, 150)
        
    def generate_for_prompt(self, prompt: str, langue: str, index: int, total: int) -> bool:
        """
        Génère une ressource pour un prompt et une langue donnés.
        
        Args:
            prompt: Le texte du prompt
            langue: Code de langue (nl, eng, all, etc.)
            index: Numéro du prompt actuel (pour affichage)
            total: Nombre total de prompts (pour affichage)
            
        Returns:
            True si la génération a réussi, False sinon
        """
        # Choisir aléatoirement homme/femme si genre non spécifié
        genre_effectif = self.genre if self.genre else random.choice(['homme', 'femme'])
        
        # Construire la commande
        cmd = [
            self.python_exe,
            "genmp3.py",
            "-l", langue,
            "-p", prompt,
            "--niveau", self.niveau,
            "--longueur", str(self.longueur),
            "-g", genre_effectif
        ]
        
        # Ajouter la vitesse si spécifiée
        if self.vitesse is not None:
            cmd.extend(["--vitesse", str(self.vitesse)])
        
        # Ajouter --ssml si activé
        if self.ssml:
            cmd.append("--ssml")
        
        print(f"\n{'='*80}")
        print(f"📝 [{index}/{total}] Langue: {langue.upper()} | Genre: {genre_effectif}")
        print(f"💬 Prompt: {prompt}")
        print(f"{'='*80}")
        sys.stdout.flush()
        
        if self.dry_run:
            print(f"🔍 [DRY-RUN] Commande: {' '.join(cmd)}")
            sys.stdout.flush()
            return True
        
        try:
            # Streamer la sortie en temps réel
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1  # Line buffered
            )
            
            # Lire et afficher la sortie ligne par ligne
            for line in iter(process.stdout.readline, ''):
                if line:
                    print(line, end='', flush=True)
            
            returncode = process.wait()
            
            if returncode == 0:
                print(f"✅ Génération réussie !")
                sys.stdout.flush()
                return True
            else:
                print(f"❌ Erreur lors de la génération (code {returncode}):")
                sys.stdout.flush()
                return False
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            sys.stdout.flush()
            return False
    
    def generate_batch(self, prompts: List[str], langues: List[str]) -> Tuple[int, int]:
        """
        Génère toutes les ressources pour tous les prompts et langues.
        
        Args:
            prompts: Liste des prompts à traiter
            langues: Liste des codes de langues
            
        Returns:
            Tuple (nombre de succès, nombre d'échecs)
        """
        total_resources = len(prompts) * len(langues)
        success_count = 0
        fail_count = 0
        current = 0
        
        print(f"\n🚀 Début de la génération batch")
        print(f"📊 {len(prompts)} prompts × {len(langues)} langue(s) = {total_resources} ressources à générer")
        print(f"⚙️  Paramètres: niveau={self.niveau}, longueur={self.longueur}", end="")
        if self.vitesse:
            print(f", vitesse={self.vitesse}", end="")
        if self.genre:
            print(f", genre={self.genre} (fixe)", end="")
        else:
            print(f", genre=aléatoire", end="")
        print()
        sys.stdout.flush()
        
        for i, prompt in enumerate(prompts, 1):
            for langue in langues:
                current += 1
                success = self.generate_for_prompt(prompt, langue, current, total_resources)
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    # Demander si on continue en cas d'erreur
                    if not self.dry_run:
                        response = input("\n⚠️  Continuer malgré l'erreur ? [O/n]: ").strip().lower()
                        if response == 'n':
                            print("🛑 Arrêt de la génération batch")
                            sys.stdout.flush()
                            return success_count, fail_count
                
                # Ajouter un délai entre les générations (sauf après la dernière)
                if current < total_resources and self.delai_entre_generations > 0:
                    print(f"⏳ Pause de {self.delai_entre_generations}s avant la prochaine génération...")
                    sys.stdout.flush()
                    time.sleep(self.delai_entre_generations)
        
        return success_count, fail_count


def main():
    parser = argparse.ArgumentParser(
        description="Génération batch de ressources à partir d'une liste de prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Générer en néerlandais, niveau A1, 150 mots
  ./batch.sh -f prompts/prompt.md -l nl -n A1 --longueur 150
  
  # Générer en anglais ET espagnol
  ./batch.sh -f prompts/prompts_hollandais.md -l eng,esp -n B1
  
  # Mode dry-run pour voir ce qui serait généré
  ./batch.sh -f prompts/prompt.md -l nl,eng,all -n A2 --dry-run
  
  # Forcer le genre pour tous les prompts
  ./batch.sh -f prompts/prompt.md -l nl -n A1 -g femme
  
  # Avec vitesse personnalisée
  ./batch.sh -f prompts/prompt.md -l eng -n C1 --vitesse 0.95
        """
    )
    
    parser.add_argument(
        '-f', '--prompts',
        required=True,
        help="Fichier contenant la liste de prompts (format: liste numérotée)"
    )
    
    parser.add_argument(
        '-l', '--langues',
        required=True,
        help="Langues séparées par virgule (ex: nl,eng,all,esp,fr)"
    )
    
    parser.add_argument(
        '-n', '--niveau',
        required=True,
        choices=['A1', 'A2', 'B1', 'B2', 'C1', 'C2'],
        help="Niveau CECRL"
    )
    
    parser.add_argument(
        '--longueur',
        type=int,
        default=None,
        help="Nombre de mots approximatif (défaut auto par niveau: A1=150, A2=200, B1=250, B2=300, C1=350, C2=400)"
    )
    
    parser.add_argument(
        '--vitesse',
        type=float,
        default=None,
        help="Vitesse de lecture (0.6-1.0). Si non spécifié, auto selon niveau"
    )
    
    parser.add_argument(
        '-g', '--genre',
        choices=['homme', 'femme'],
        default=None,
        help="Genre de la voix. Si non spécifié, choix aléatoire pour chaque ressource"
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Afficher les commandes sans les exécuter"
    )
    
    parser.add_argument(
        '--delai',
        type=float,
        default=40.0,
        help="Délai entre chaque génération en secondes (défaut: 40s pour éviter rate limiting Azure)"
    )
    
    parser.add_argument(
        '--ssml',
        action='store_true',
        help="Activer SSML pour emphases (*, **) et pauses ([p], [p:ms]) lors de la synthèse audio"
    )
    
    args = parser.parse_args()
    
    # Vérifier que le fichier de prompts existe
    prompts_file = Path(args.prompts)
    if not prompts_file.exists():
        print(f"❌ Erreur: Le fichier {args.prompts} n'existe pas")
        sys.exit(1)
    
    # Parser les prompts
    print(f"📖 Lecture des prompts depuis {args.prompts}...")
    prompts = PromptParser.extract_prompts(args.prompts)
    
    if not prompts:
        print(f"❌ Aucun prompt trouvé dans {args.prompts}")
        print("💡 Format attendu: lignes numérotées (1. Premier prompt, 2. Deuxième prompt, etc.)")
        sys.exit(1)
    
    print(f"✅ {len(prompts)} prompt(s) trouvé(s)")
    
    # Parser les langues
    langues = [l.strip() for l in args.langues.split(',')]
    
    # Valider les codes de langues
    valid_langs = ['fr', 'eng', 'us', 'esp', 'hisp', 'nl', 'all', 'at', 'co', 'cor', 'it']
    invalid_langs = [l for l in langues if l not in valid_langs]
    if invalid_langs:
        print(f"❌ Erreur: Code(s) de langue invalide(s): {', '.join(invalid_langs)}")
        print(f"   Codes valides: {', '.join(valid_langs)}")
        print(f"\n   fr    = Français ✅")
        print(f"   nl    = Néerlandais ✅")
        print(f"   eng   = Anglais UK ✅")
        print(f"   us    = Anglais US ✅")
        print(f"   esp   = Espagnol Espagne ✅")
        print(f"   hisp  = Espagnol Amérique ⚠️  (voix limitées)")
        print(f"   all   = Allemand ❓ (non testé)")
        print(f"   at    = Allemand Autrichien ✅ (voix de Vienne)")
        print(f"   co/cor= Coréen ✅")
        print(f"   it    = Italien ✅")
        sys.exit(1)
    
    # Normaliser 'co' -> 'cor' (genmp3.py utilise 'cor')
    langues = ['cor' if l == 'co' else l for l in langues]
    
    # Créer le générateur batch
    generator = BatchGenerator(
        niveau=args.niveau,
        longueur=args.longueur,
        vitesse=args.vitesse,
        genre=args.genre,
        dry_run=args.dry_run,
        delai_entre_generations=args.delai,
        ssml=args.ssml
    )
    
    # Générer toutes les ressources
    success, fail = generator.generate_batch(prompts, langues)
    
    # Résumé final
    print(f"\n{'='*80}")
    print(f"📊 RÉSUMÉ")
    print(f"{'='*80}")
    print(f"✅ Succès: {success}")
    print(f"❌ Échecs: {fail}")
    print(f"📦 Total: {success + fail}")
    
    if not args.dry_run and success > 0:
        print(f"\n� Régénération du site...")
        try:
            site_build = subprocess.run(["./site.sh", "build"], check=False)
            if site_build.returncode == 0:
                print(f"✅ Site régénéré avec succès!")                
                # Push automatique sur GitHub
                print(f"\n📤 Push sur GitHub...")
                try:
                    # Git add
                    subprocess.run(["git", "add", "."], check=True)
                    
                    # Git commit
                    commit_msg = f"Batch: {success} nouvelles ressources ({', '.join(langues)}, {args.niveau})"
                    subprocess.run(["git", "commit", "-m", commit_msg], check=True)
                    
                    # Git push
                    subprocess.run(["git", "push"], check=True)
                    
                    print(f"✅ Modifications poussées sur GitHub!")
                except subprocess.CalledProcessError as e:
                    print(f"⚠️  Erreur Git (code {e.returncode})")
                    print(f"   Vous pouvez pousser manuellement avec: git push")
                except Exception as e:
                    print(f"⚠️  Erreur lors du push: {e}")
            else:
                print(f"⚠️  Le script site.sh a retourné un code d'erreur")
        except Exception as e:
            print(f"⚠️  Erreur lors de la régénération du site: {e}")
    
    sys.exit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
