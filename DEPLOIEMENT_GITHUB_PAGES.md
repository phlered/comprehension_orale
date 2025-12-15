# Déploiement sur GitHub Pages

## 📋 Préparation

### 1. Structure du projet

Le site web est dans le répertoire `site_langues/` :

```
site_langues/
├── index.html              # Page d'accueil
├── search.html             # Page de recherche
├── player.html             # Page de lecture
├── metadata.json           # Index des ressources
├── resources/              # Fichiers audio et texte
│   └── [resource_id]/
│       ├── audio.mp3
│       └── text.md
└── README.md
```

### 2. Générer le site

Avant de déployer, assurez-vous que le site est à jour :

```bash
# Activer l'environnement virtuel (si nécessaire)
source .venv312/bin/activate

# Générer le site
python build_site.py
```

### 3. Vérification locale

Pour tester localement avant le déploiement :

```bash
# Se placer dans le répertoire du site
cd site_langues

# Lancer un serveur HTTP simple (Python 3)
python -m http.server 8000

# Ou avec Python 2
python -m SimpleHTTPServer 8000
```

Puis ouvrir dans un navigateur : http://localhost:8000

## 🚀 Déploiement

### Option A : Déployer tout le repository

Si vous voulez pousser tout le projet (scripts + site) :

1. **Initialiser git** (si pas déjà fait)
```bash
git init
git add .
git commit -m "Initial commit: site langues"
```

2. **Créer un repository sur GitHub**
   - Aller sur https://github.com/new
   - Nom : `comprehension-orale-langues` (par exemple)
   - Public ou Private selon vos besoins
   - Ne pas initialiser avec README (vous en avez déjà un)

3. **Pousser le code**
```bash
git remote add origin https://github.com/[USERNAME]/comprehension-orale-langues.git
git branch -M main
git push -u origin main
```

4. **Configurer GitHub Pages**
   - Aller dans **Settings** > **Pages**
   - Source : **Deploy from a branch**
   - Branch : `main`
   - Folder : `/site_langues` ⚠️ Important !
   - Cliquer sur **Save**

5. **Attendre le déploiement** (1-2 minutes)
   - Le site sera accessible à : `https://[USERNAME].github.io/comprehension-orale-langues/`

### Option B : Déployer uniquement le site (recommandé)

Si vous voulez un repository séparé pour le site uniquement :

1. **Créer un nouveau repository sur GitHub**
   - Nom : `[USERNAME].github.io` (pour un site principal)
   - Ou : `langues` (pour un sous-projet)
   - Public

2. **Initialiser git dans site_langues**
```bash
cd site_langues
git init
git add .
git commit -m "Initial deploy"
```

3. **Pousser vers GitHub**
```bash
git remote add origin https://github.com/[USERNAME]/[REPO-NAME].git
git branch -M main
git push -u origin main
```

4. **Configurer GitHub Pages**
   - Settings > Pages
   - Source : **Deploy from a branch**
   - Branch : `main`
   - Folder : **/ (root)** ⚠️ Car on pousse directement le contenu
   - Save

5. **URL du site**
   - Site principal : `https://[USERNAME].github.io/`
   - Sous-projet : `https://[USERNAME].github.io/[REPO-NAME]/`

## 🔄 Mises à jour

### Workflow de mise à jour

Quand vous ajoutez de nouvelles ressources :

```bash
# 1. Générer les nouvelles ressources
genmp3 -l nl -p "Nouveau sujet" --niveau A2

# 2. Régénérer le site
python build_site.py

# 3. Vérifier localement (optionnel)
cd site_langues
python -m http.server 8000
# Tester sur http://localhost:8000

# 4. Commiter et pousser
git add site_langues/
git commit -m "Ajout de nouvelles ressources néerlandaises"
git push origin main
```

GitHub Pages se mettra à jour automatiquement en quelques minutes.

### Vérifier le statut du déploiement

- Aller dans l'onglet **Actions** de votre repository
- Vous verrez l'état de chaque déploiement (✅ succès, ⚠️ en cours, ❌ erreur)

## 🔧 Configuration avancée

### Domaine personnalisé

Si vous avez un domaine personnalisé :

1. Dans **Settings** > **Pages** > **Custom domain**
2. Entrer votre domaine : `langues.votredomaine.com`
3. Configurer les DNS chez votre registrar :
   ```
   Type: CNAME
   Name: langues
   Value: [USERNAME].github.io
   ```

### Forcer HTTPS

Dans **Settings** > **Pages** :
- ✅ Cocher **Enforce HTTPS**

### Actions automatiques (optionnel)

Pour automatiser le build à chaque push, créer `.github/workflows/build.yml` :

```yaml
name: Build and Deploy

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.x'
    
    - name: Build site
      run: python build_site.py
    
    - name: Deploy
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./site_langues
```

## ⚠️ Limitations GitHub Pages

- Taille max du site : **1 GB**
- Bande passante : **100 GB/mois**
- Builds : **10 par heure**
- Pas d'exécution serveur (site statique uniquement)

Pour votre usage (30 ressources × ~100KB MP3 = ~3MB), largement dans les limites !

## 🐛 Résolution de problèmes

### Le site ne s'affiche pas

1. Vérifier que le déploiement est terminé (onglet Actions)
2. Vider le cache du navigateur (Cmd+Shift+R / Ctrl+Shift+R)
3. Vérifier la configuration : Settings > Pages
4. Attendre 5-10 minutes (propagation DNS)

### Les fichiers audio ne se chargent pas

1. Vérifier que `resources/` est bien poussé :
   ```bash
   git add site_langues/resources/
   git commit -m "Ajout des ressources audio"
   git push
   ```

2. Vérifier les chemins dans `metadata.json` (relatifs, pas absolus)

### Les changements n'apparaissent pas

1. Vérifier que `metadata.json` a été régénéré :
   ```bash
   ls -lh site_langues/metadata.json
   ```

2. Forcer le rechargement :
   - Chrome/Edge : Cmd/Ctrl + Shift + R
   - Safari : Cmd + Option + R

### Erreur 404 sur les ressources

Si les chemins ne fonctionnent pas, vérifier la configuration :
- Root folder vs sous-dossier
- Chemins relatifs vs absolus dans le code HTML/JS

## 📊 Monitoring

### Analytics (optionnel)

Pour suivre l'utilisation, ajouter Google Analytics dans `index.html` :

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

### Statistiques GitHub

GitHub fournit des statistiques basiques :
- **Insights** > **Traffic** : visiteurs, vues de page
- **Insights** > **Popular content** : pages les plus consultées

## ✅ Checklist avant déploiement

- [ ] Site généré avec `python build_site.py`
- [ ] Test local effectué (`python -m http.server 8000`)
- [ ] Toutes les ressources sont présentes
- [ ] `metadata.json` est à jour
- [ ] Les chemins sont relatifs (pas absolus)
- [ ] Repository GitHub créé
- [ ] Code poussé sur GitHub
- [ ] GitHub Pages configuré
- [ ] URL du site testée dans un navigateur
- [ ] Test sur smartphone (responsive)

## 🎉 C'est prêt !

Une fois déployé, partagez l'URL avec vos utilisateurs :

```
🌍 Site d'apprentissage des langues
🔗 https://[USERNAME].github.io/[REPO-NAME]/

📱 Compatible smartphone
🎧 Ressources audio avec texte et vocabulaire
🌐 5 langues disponibles
```
