import os
import shutil

titre = input("Titre du document à supprimer (recherche partielle): ").strip()

if not titre:
    print("Aucun titre fourni.")
    exit()

results = []
for folder in os.listdir('docs'):
    filepath = f'docs/{folder}/text.md'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if titre.lower() in content.lower():
                # Extraire le prompt/resume pour affichage
                lines = content.split('\n')
                for line in lines:
                    if 'prompt:' in line.lower() or 'resume:' in line.lower():
                        results.append((folder, line.strip()))
                        break

if not results:
    print(f"Aucun document trouvé contenant '{titre}'.")
    exit()

print(f"\n{len(results)} document(s) trouvé(s):\n")
for i, (folder, meta) in enumerate(sorted(results), 1):
    print(f"  {i}. {folder}")
    print(f"     {meta}\n")

confirm = input("Supprimer ces documents ? (oui/non): ").strip().lower()
if confirm == 'oui':
    for folder, _ in results:
        path = f'docs/{folder}'
        shutil.rmtree(path)
        print(f"✓ Supprimé: {folder}")
    print(f"\n{len(results)} document(s) supprimé(s).")
else:
    print("Annulé.")
