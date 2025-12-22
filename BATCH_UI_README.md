# Interface Web - Générateur Batch

Interface HTML + serveur Python pour générer facilement plusieurs ressources audio en une seule opération.

## 🚀 Démarrage rapide

### Option 1: Avec le script shell (recommandé sur macOS)

```bash
./batch_server.sh
```

Puis ouvrez http://localhost:5000 dans votre navigateur.

### Option 2: Directement avec Python

```bash
.venv312/bin/python batch_server.py
```

### Options de lancement

```bash
# Port personnalisé
./batch_server.sh --port 8080

# Mode debug (rechargement automatique)
./batch_server.sh --debug

# Avec Python directement
.venv312/bin/python batch_server.py --port 8080 --debug
```

## 📋 Utilisation

1. **Choisir un fichier de prompts** 📁
   - Cliquez sur "Choisir un fichier..."
   - Sélectionnez un fichier `.md` ou `.txt` contenant une liste numérotée de prompts
   - Format attendu:
     ```
     1. Commande une pizza
     2. Aller à la pharmacie
     3. Faire les courses
     ```

2. **Sélectionner les langues** 🌍
   - Cochez les langues souhaitées
   - Utilisez "Tout cocher" / "Tout décocher" pour faciliter
   - Langues disponibles:
     - 🇫🇷 Français
     - 🇳🇱 Néerlandais
     - 🇬🇧 Anglais UK
     - 🇺🇸 Anglais US
     - 🇪🇸 Espagnol
     - 🇨🇴 Espagnol Amérique
     - 🇩🇪 Allemand
     - 🇰🇷 Coréen
     - 🇮🇹 Italien

3. **Choisir le niveau** 📊
   - Sélectionnez un niveau CECRL dans le menu déroulant:
     - A1 (Débutant)
     - A2 (Faux débutant)
     - B1 (Intermédiaire)
     - B2 (Intermédiaire supérieur)
     - C1 (Avancé)
     - C2 (Maîtrise)

4. **Créer les documents** ✨
   - Cliquez sur "Créer les documents et mettre le site à jour"
   - La génération commence et vous voyez la progression en temps réel
   - Une fois terminée, le site est automatiquement mis à jour

## 🔧 Architecture

### Frontend (`batch_ui.html`)
- Interface réactive en HTML/CSS/JavaScript
- Sélection des prompts, langues, et niveau
- Streaming en temps réel de la génération
- Barre de progression et affichage des logs

### Backend (`batch_server.py`)
- Serveur Flask avec streaming NDJSON
- Lance `batch_genmp3.py` en subprocess
- Capture et diffuse la sortie en temps réel
- Mise à jour automatique du site avec `site.sh build`

## 📊 Flux de données

```
HTML Form
    ↓
Flask API (/api/batch-generate)
    ↓
batch_genmp3.py (subprocess)
    ↓
genmp3.py × N (génération par prompt+langue)
    ↓
md2mp3.py (synthèse audio Azure)
    ↓
docs/[slug]_[timestamp]/ (ressources générées)
    ↓
site.sh build (mise à jour du site)
    ↓
site_langues/ (site statique)
```

## 🔍 Dépannage

### "Flask n'est pas installé"
```bash
.venv312/bin/pip install flask
```

### Le serveur ne démarre pas
```bash
# Vérifier que le port n'est pas déjà utilisé
lsof -i :5000

# Utiliser un autre port
./batch_server.sh --port 8080
```

### Erreur lors de la génération
- Vérifiez que les variables d'environnement sont configurées:
  - `OPENAI_API_KEY` (pour genmp3.py)
  - `AZURE_SPEECH_KEY` (pour md2mp3.py)
  - `AZURE_SPEECH_REGION` (pour md2mp3.py)

### Le site ne se met pas à jour
```bash
# Testez site.sh directement
./site.sh build
./site.sh serve  # Vérifier localement
```

## 📝 Formats supportés

### Fichiers de prompts
- `.md` (Markdown) - Format recommandé
- `.txt` (Texte brut)

Format attendu (liste numérotée):
```
1. Premier prompt
2. Deuxième prompt
3. Troisième prompt
```

## 🎨 Interface

### Éléments
- ✅ Sélecteurs de fichier avec drag-and-drop (par navigateur)
- ✅ Checkboxes pour les langues
- ✅ Boutons "Tout cocher" / "Tout décocher"
- ✅ Menu déroulant pour le niveau
- ✅ Affichage en temps réel des logs
- ✅ Barre de progression
- ✅ Indicateurs de statut (info, succès, erreur, warning)

### Responsive
- Design adaptatif pour desktop et tablette
- Fond dégradé moderne
- Animations fluides

## 🚀 Cas d'usage

### Exemple 1: Générer des ressources A1 en français et néerlandais
1. Ouvrir http://localhost:5000
2. Sélectionner `prompts/prompt.md`
3. Cocher: Français, Néerlandais
4. Niveau: A1
5. Cliquer sur "Créer les documents et mettre le site à jour"
6. Attendre la fin de la génération

### Exemple 2: Batch multilingue B1
1. Ouvrir http://localhost:5000
2. Sélectionner `prompts/prompts_hollandais.md`
3. Cocher: Français, Néerlandais, Anglais UK, Espagnol
4. Niveau: B1
5. Cliquer sur "Créer les documents et mettre le site à jour"

## 📦 Dépendances

- Flask (installé automatiquement si absent)
- Python 3.12+ (via `.venv312`)
- batch_genmp3.py (intégration)
- site.sh (pour la mise à jour du site)

## 🔐 Sécurité

- Validation des fichiers uploadés
- Noms de fichiers sécurisés avec `werkzeug.utils.secure_filename`
- Limite de taille: 16 MB
- Fichiers temporaires supprimés après traitement

## 📄 Licences

Voir [LICENSE](LICENSE) pour les détails.

## 🆘 Support

Pour les problèmes:
1. Vérifiez les logs dans la section "Sortie du serveur"
2. Lancez le serveur en mode debug: `./batch_server.sh --debug`
3. Consultez [QUICKSTART.md](QUICKSTART.md) pour la configuration générale
