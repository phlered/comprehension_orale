# 🎯 Guide Complet - Interface Web Batch

## Vue d'ensemble

L'interface web `batch_ui.html` + `batch_server.py` offre une alternative graphique au script `batch_genmp3.py` en ligne de commande.

### Avantages
✅ Pas de terminal requis  
✅ Interface intuitive avec formulaire graphique  
✅ Sélection visuelle des fichiers, langues, et niveaux  
✅ Streaming en direct des résultats  
✅ Mise à jour automatique du site web  

## Installation

### 1. Vérifier les dépendances

```bash
cd /Users/ph/Dropbox/Philippe/Projets/comprehension_orale

# Flask doit être installé
.venv312/bin/pip install flask
```

### 2. Fichiers nécessaires

```
✅ batch_ui.html       (interface HTML)
✅ batch_server.py     (serveur Flask)
✅ batch_server.sh     (script de lancement)
✅ batch_genmp3.py     (moteur de génération existant)
```

## Démarrage

### Mode 1: Script shell (recommandé)

```bash
./batch_server.sh
```

Puis ouvrez automatiquement ou manuellement:
```
http://localhost:5000
```

### Mode 2: Direct avec Python

```bash
.venv312/bin/python batch_server.py
```

### Mode 3: Port personnalisé

```bash
./batch_server.sh --port 8080
```

Accédez à `http://localhost:8080`

## 📖 Guide utilisateur étape par étape

### Étape 1️⃣ : Charger un fichier de prompts

![File Selection]
```
┌─────────────────────────────────────┐
│ 📝 Fichier de prompts               │
│ ┌─────────────────────────────────┐ │
│ │ Choisir un fichier...           │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

**Action:**
- Cliquez sur la zone grise "Choisir un fichier..."
- Sélectionnez un fichier `.md` ou `.txt`
- Doit contenir une liste numérotée de prompts

**Format attendu:**
```markdown
1. Commande une pizza
2. Aller à la pharmacie
3. Acheter des vêtements
4. Réserver un hôtel
```

**Exemple de fichiers disponibles:**
- `prompts/prompt.md` (général)
- `prompts/prompts_hollandais.md` (néerlandais)
- Vos propres fichiers de prompts

### Étape 2️⃣ : Sélectionner les langues

![Languages Selection]
```
┌─────────────────────────────────────┐
│ 🌍 Langues                          │
│ [Tout cocher] [Tout décocher]       │
│ ┌─ ☑ Français                       │
│ ├─ ☑ Néerlandais                    │
│ ├─ ☐ Anglais UK                     │
│ ├─ ☐ Anglais US                     │
│ ├─ ☑ Espagnol                       │
│ ├─ ☐ Espagnol Amérique              │
│ ├─ ☐ Allemand                       │
│ ├─ ☐ Coréen                         │
│ └─ ☐ Italien                        │
└─────────────────────────────────────┘
```

**Actions disponibles:**
1. Cocher individuellement: ☑ = inclus, ☐ = exclu
2. Bouton "Tout cocher" pour sélectionner toutes les langues
3. Bouton "Tout décocher" pour désélectionner toutes les langues

**Exemple:**
- Pour générer en français et néerlandais: ☑ Français + ☑ Néerlandais

### Étape 3️⃣ : Choisir le niveau CECRL

![Level Selection]
```
┌─────────────────────────────────────┐
│ 📊 Niveau CECRL                     │
│ ┌─────────────────────────────────┐ │
│ │ -- Sélectionner un niveau --  ▼ │ │
│ └─────────────────────────────────┘ │
└─────────────────────────────────────┘

Options:
├─ A1 - Débutant
├─ A2 - Faux débutant
├─ B1 - Intermédiaire
├─ B2 - Intermédiaire supérieur
├─ C1 - Avancé
└─ C2 - Maîtrise
```

**Sélection:**
- Menu déroulant avec 6 niveaux
- A1 = très simple (100-150 mots)
- C2 = très complexe (vocabulaire riche)

### Étape 4️⃣ : Lancer la génération

![Submit Button]
```
┌─────────────────────────────────────┐
│ ✨ Créer les documents et mettre    │
│    le site à jour                   │
│ ↻ Réinitialiser                     │
└─────────────────────────────────────┘
```

**Cliquez sur le bouton "✨ Créer..."**

L'interface:
1. Valide tous les champs
2. Envoie la demande au serveur
3. Affiche la barre de progression
4. Stream les logs en temps réel
5. Met à jour le site automatiquement

### Étape 5️⃣ : Suivi en temps réel

![Progress Section]
```
Barre de progression:
████████████░░░░░░░░░░░░░░░░░░░░░░░░ 35%

Logs:
📝 Démarrage de la génération batch...
✅ 1 / 6 ressources générées
...
```

**Affichage:**
- 📊 Barre de progression (%)
- 📋 Logs en temps réel (scrollable)
- ✅ Indicateurs de succès
- ❌ Messages d'erreur

## 📊 Exemple complet

### Scénario: Générer 4 prompts en 3 langues

**Étapes:**

1. **Fichier de prompts** → `prompts/prompt.md`
   ```
   1. Commande une pizza
   2. Aller à la pharmacie
   3. Acheter des vêtements
   4. Réserver un hôtel
   ```

2. **Langues** → ☑ Français + ☑ Néerlandais + ☑ Anglais UK

3. **Niveau** → B1

4. **Résultat attendu:**
   - 4 prompts × 3 langues = **12 ressources**
   - Chacune = 1 texte `.md` + 1 audio `.mp3`
   - Stockées dans `docs/`
   - Site mis à jour automatiquement

5. **Logs de progression:**
   ```
   🚀 Démarrage de la génération batch...
   📊 4 prompts × 3 langue(s) = 12 ressources à générer
   
   [1/12] Langue: FR | Genre: femme
   💬 Prompt: Commande une pizza
   ✅ Génération réussie !
   
   [2/12] Langue: NL | Genre: homme
   💬 Prompt: Commande une pizza
   ✅ Génération réussie !
   
   ... (10 autres ressources)
   
   📊 RÉSUMÉ
   ✅ Succès: 12
   ❌ Échecs: 0
   
   🔨 Mise à jour du site web...
   ✅ Site web mis à jour avec succès!
   ```

## 🔧 Paramètres avancés

### Personnalisation (non exposée dans l'UI)

Pour des paramètres avancés (longueur, vitesse, genre fixe), modifiez:

**Option 1: Modifier le serveur Python**
```python
# Dans batch_server.py, ligne ~200
# Ajouter dans la commande:
cmd.extend(["--longueur", "200"])  # 200 mots
cmd.extend(["--vitesse", "0.85"])  # Vitesse 0.85
cmd.extend(["-g", "homme"])        # Genre fixe
```

**Option 2: Utiliser le CLI directement**
```bash
./batch.sh -f prompts/prompt.md -l fr,nl,eng -n B1 --longueur 200
```

## ⚠️ Messages d'erreur courants

### "Veuillez sélectionner au moins une langue"
**Cause:** Pas de langue cochée  
**Solution:** Cochez au moins 1 langue

### "Veuillez sélectionner un fichier de prompts"
**Cause:** Aucun fichier sélectionné  
**Solution:** Cliquez sur "Choisir un fichier..."

### "Veuillez sélectionner un niveau"
**Cause:** Niveau non choisi  
**Solution:** Sélectionnez dans le menu déroulant

### "❌ Erreur: OPENAI_API_KEY non définie"
**Cause:** Clé OpenAI manquante  
**Solution:** Vérifier `.env`:
```bash
echo $OPENAI_API_KEY
# Doit être défini
```

### "❌ Erreur: Azure Speech Service échoué"
**Cause:** Clé/région Azure incorrecte  
**Solution:** Vérifier `.env`:
```bash
echo $AZURE_SPEECH_KEY
echo $AZURE_SPEECH_REGION  # westeurope
```

### "⚠️ La mise à jour du site a rencontré une erreur"
**Cause:** `site.sh build` a échoué  
**Solution:** Testez directement:
```bash
./site.sh build
./site.sh serve
```

## 🚀 Cas d'usage pratiques

### Cas 1: Générer des ressources pour un nouveau cours

```
Fichier: prompts/prompt.md (5 prompts)
Langues: Français, Néerlandais
Niveau: A1
Résultat: 10 ressources (5 FR + 5 NL)
Durée: ~5-10 minutes
```

### Cas 2: Expansion multilingue

```
Fichier: prompts/prompts_hollandais.md (10 prompts)
Langues: FR, NL, ENG, ESP
Niveau: B1
Résultat: 40 ressources (10 × 4 langues)
Durée: ~20-30 minutes
```

### Cas 3: Mise à jour progressive

Lancez plusieurs fois avec différents niveaux:
```
Itération 1: Niveau A1 (5 ressources)
Itération 2: Niveau A2 (5 ressources)
Itération 3: Niveau B1 (5 ressources)
Total: 15 ressources progressives
```

## 📈 Performance

### Temps estimé par ressource

| Niveau | Voix | Synthèse | Total |
|--------|------|----------|-------|
| A1     | ~5s  | ~10s     | ~15s  |
| B1     | ~8s  | ~15s     | ~23s  |
| C2     | ~10s | ~20s     | ~30s  |

**Temps total = (nb_prompts × nb_langues × temps_par_ressource)**

Exemple: 5 prompts × 3 langues × 20s = 300s ≈ 5 minutes

## 🛡️ Points de sécurité

✅ Fichiers validés avant upload  
✅ Noms de fichiers sécurisés  
✅ Limite de taille: 16 MB  
✅ Fichiers temporaires supprimés  
✅ Pas d'exécution de code malveillant  

## 📝 Notes techniques

### Architecture
```
Frontend (HTML/JS) 
    ↓ HTTP POST
Backend (Flask)
    ↓ subprocess
batch_genmp3.py
    ↓ multiple calls
genmp3.py (OpenAI)
    ↓ genmp3.py (Azure TTS)
docs/ (ressources)
    ↓ site.sh build
site_langues/ (site statique)
```

### Streaming
- Format NDJSON (newline-delimited JSON)
- Événements: output, progress, status, complete, error
- Frontend met à jour l'UI en temps réel

## 🆘 Dépannage avancé

### Serveur ne démarre pas
```bash
# Vérifier les permissions
ls -la batch_server.py batch_server.sh

# Port déjà utilisé?
lsof -i :5000

# Utiliser un autre port
./batch_server.sh --port 8080
```

### Mode debug
```bash
./batch_server.sh --debug
```

Affiche:
- Rechargement automatique
- Stack traces complets
- Plus de logs

### Vérifier les fichiers générés
```bash
# Voir les dernières ressources
ls -ltr docs/ | tail -5

# Vérifier le site
./site.sh serve
# Ouvrir http://localhost:8000
```

## 📚 Voir aussi

- [QUICKSTART.md](QUICKSTART.md) - Installation générale
- [batch_genmp3.py](batch_genmp3.py) - Script CLI
- [MD2MP3_README.md](MD2MP3_README.md) - Synthèse vocale Azure
