# Guide : Copier-Coller de Prompts dans l'Interface Batch

## Vue d'ensemble

L'interface batch a été modifiée pour permettre le **copier-coller direct** de prompts au format Markdown, au lieu de devoir sélectionner un fichier.

## Format des prompts

Les prompts doivent être au format Markdown avec une **liste numérotée** :

```markdown
1. Premier prompt
2. Deuxième prompt
3. Troisième prompt
4. Quatrième prompt
...
```

## Utilisation

### 1. Lancer le serveur

```bash
python batch_server.py
# ou
./batch_server.sh
```

Le serveur démarre sur http://localhost:5000

### 2. Dans l'interface web

1. **Coller les prompts** dans la zone de texte (zone grise avec police monospace)
   - Format attendu : liste numérotée (1. Prompt, 2. Prompt, etc.)
   - Exemple : copier-coller depuis un fichier comme `prompts/prompt.md`

2. **Sélectionner les langues** souhaitées
   - Cochez une ou plusieurs langues
   - Utilisez les boutons "Tout cocher" / "Tout décocher" pour aller plus vite

3. **Choisir le niveau CECRL** (A1 à C2)

4. **Cliquer sur "Créer les documents et mettre le site à jour"**

### 3. Suivi de la génération

L'interface affiche en temps réel :
- La progression de la génération
- Les logs du processus
- Les erreurs éventuelles
- La mise à jour automatique du site web

## Exemple de fichier source

Vous pouvez copier directement le contenu de fichiers comme :
- `prompts/prompt.md`
- `prompts/prompts_hollandais.md`
- Tout autre fichier contenant une liste numérotée de prompts

## Avantages

✅ **Plus rapide** : pas besoin de naviguer dans les fichiers  
✅ **Plus flexible** : éditer les prompts directement dans l'interface  
✅ **Plus simple** : copier-coller depuis n'importe quelle source  

## Modifications techniques

### Fichiers modifiés

1. **batch_ui.html**
   - Remplacement de `<input type="file">` par `<textarea>`
   - Ajout de styles CSS pour la zone de texte
   - Modification du JavaScript pour envoyer le texte au lieu d'un fichier

2. **batch_server.py**
   - Modification de l'endpoint `/api/batch-generate`
   - Accepte maintenant `promptText` au lieu de `promptFile`
   - Crée automatiquement un fichier temporaire `.md` avec le contenu
   - Nettoyage automatique du fichier temporaire après traitement

### Backend

Le serveur crée automatiquement un fichier temporaire `.md` avec le texte collé, puis le supprime après la génération. Le reste du pipeline (batch_genmp3.py) fonctionne exactement comme avant.

## Format attendu par batch_genmp3.py

Le script `batch_genmp3.py` attend toujours un fichier Markdown avec le format :

```markdown
1. Prompt un
2. Prompt deux
3. Prompt trois
```

L'interface crée simplement ce fichier automatiquement à partir du texte collé.
