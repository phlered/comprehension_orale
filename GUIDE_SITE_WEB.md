# 🌍 Site Web d'Apprentissage des Langues - Guide Complet

## 📋 Vue d'ensemble

Votre site web pour l'apprentissage des langues est prêt ! Il permet de consulter facilement vos ressources audio (textes + vocabulaire + fichiers MP3) depuis n'importe quel smartphone ou ordinateur.

### ✨ Fonctionnalités

- **5 langues** : 🇬🇧 Anglais, 🇩🇪 Allemand, 🇪🇸 Espagnol, 🇳🇱 Néerlandais, 🇰🇷 Coréen
- **Recherche avancée** : par mots-clés, niveau (A1-C2), classe, axe
- **Lecteur audio intégré** : lecture/pause, contrôle du volume
- **Affichage texte/vocabulaire** : boutons pour afficher/masquer
- **Design responsive** : optimisé pour smartphone
- **Navigation intuitive** : retour facile vers la recherche

### 📊 Ressources actuelles

- **30 ressources** au total (~13 MB)
- **Néerlandais** : 20 ressources (A1 principalement)
- **Allemand** : 7 ressources (A1-B2)
- **Anglais** : 1 ressource
- **Français** : 1 ressource
- **Coréen** : 1 ressource

## 🚀 Utilisation rapide

### Option 1 : Script utilitaire (recommandé)

```bash
# Afficher l'aide
./site.sh help

# Générer/régénérer le site
./site.sh build

# Tester localement
./site.sh serve
# Puis ouvrir http://localhost:8000

# Afficher les statistiques
./site.sh stats

# Préparer le déploiement
./site.sh deploy
```

### Option 2 : Commandes Python

```bash
# Générer le site
python build_site.py

# Tester localement
cd site_langues
python -m http.server 8000
```

## 📁 Structure du projet

```
comprehension_orale/
├── site_langues/              # Site web (à déployer sur GitHub Pages)
│   ├── index.html             # Page d'accueil avec drapeaux
│   ├── search.html            # Page de recherche avec filtres
│   ├── player.html            # Lecteur audio
│   ├── metadata.json          # Index des ressources (généré)
│   ├── resources/             # Ressources audio et texte (générées)
│   │   └── [resource_id]/
│   │       ├── audio.mp3
│   │       └── text.md
│   └── README.md
│
├── docs/                      # Ressources sources (générées par genmp3.py)
│   └── [resource_folders]/
│       ├── audio.mp3
│       └── text.md
│
├── build_site.py              # Script de génération du site
├── site.sh                    # Script utilitaire
├── genmp3.py                  # Générateur de ressources
├── md2mp3.py                  # Convertisseur Markdown → MP3
│
└── DEPLOIEMENT_GITHUB_PAGES.md  # Guide de déploiement détaillé
```

## 🔄 Workflow complet

### 1. Créer de nouvelles ressources

```bash
# Exemple : créer une ressource en néerlandais
genmp3 -l nl -p "Les transports aux Pays-Bas" --niveau A2 --longueur 150 --vitesse 0.7

# Exemple : batch de 5 ressources
for prompt in "prompt1" "prompt2" "prompt3" "prompt4" "prompt5"; do
  genmp3 -l all -p "$prompt" --niveau B1
done
```

Les ressources sont créées dans `docs/[resource_id]/`

### 2. Générer le site web

```bash
# Option A : avec le script
./site.sh build

# Option B : directement
python build_site.py
```

Cela crée/met à jour :
- `site_langues/metadata.json` (index pour la recherche)
- `site_langues/resources/` (copie des audio + textes)

### 3. Tester localement

```bash
# Lancer le serveur
./site.sh serve

# Ou manuellement
cd site_langues
python -m http.server 8000
```

Ouvrir http://localhost:8000 dans un navigateur et tester :
- ✅ Page d'accueil : sélection de langue
- ✅ Page de recherche : filtres, liste des ressources
- ✅ Page de lecture : audio, texte, vocabulaire
- ✅ Navigation : retours, liens
- ✅ Responsive : tester sur mobile (dev tools)

### 4. Déployer sur GitHub Pages

```bash
# Préparer le déploiement (build + vérifications)
./site.sh deploy

# Puis suivre les instructions affichées :
git add site_langues/
git commit -m "Mise à jour des ressources"
git push origin main
```

Voir **DEPLOIEMENT_GITHUB_PAGES.md** pour les détails complets.

## 🎯 Cas d'usage courants

### Ajouter une nouvelle langue

Actuellement supporté dans le code mais sans ressources :
- Espagnol (esp)

Pour ajouter des ressources en espagnol :

```bash
genmp3 -l esp -p "La vida en España" --niveau A1 --longueur 150
```

Puis régénérer le site : `./site.sh build`

### Ajouter des métadonnées (classe, axe)

Pour le moment, `genmp3.py` ne génère pas automatiquement `classe` et `axe`.

**Option 1** : Modifier manuellement le front matter dans `docs/[resource]/text.md` :

```yaml
---
langue: Allemand
prompt: Die Umwelt
niveau: B1
classe: 1        # ← Ajouter
axe: Environnement  # ← Ajouter
date_generation: 2025-12-10 20:00:00
---
```

Puis régénérer : `./site.sh build`

**Option 2** : Modifier `genmp3.py` pour ajouter ces paramètres automatiquement.

### Supprimer des ressources obsolètes

```bash
# 1. Supprimer le dossier dans docs/
rm -rf docs/[resource_id]

# 2. Régénérer le site
./site.sh build
```

### Changer l'ordre d'affichage

Par défaut, les ressources sont affichées dans l'ordre de `metadata.json`.

Pour trier par date (plus récentes en premier), modifier `search.html` :

```javascript
// Dans la fonction filterAndDisplayResources()
filteredResources.sort((a, b) => {
    return new Date(b.date) - new Date(a.date);
});
```

## 🛠️ Personnalisation

### Changer les couleurs

Dans `index.html`, `search.html`, `player.html`, modifier les valeurs CSS :

```css
/* Gradient de fond */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
/* Changer vers : */
background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);

/* Couleur primaire */
background: #667eea;
/* Changer vers : */
background: #ff6b6b;
```

### Ajouter un logo

Dans `index.html`, remplacer le titre :

```html
<h1>🌍 Apprentissage des Langues</h1>
<!-- Par : -->
<img src="logo.png" alt="Logo" style="max-width: 200px;">
<h1>Apprentissage des Langues</h1>
```

### Modifier les drapeaux

Dans `index.html` et les fichiers config JavaScript :

```javascript
const LANGUAGE_CONFIG = {
    'eng': { name: 'Anglais', flag: '🇬🇧' },  // ou '🇺🇸' pour USA
    'all': { name: 'Allemand', flag: '🇩🇪' },
    // ...
};
```

### Ajouter Google Analytics

Dans chaque page HTML, avant `</head>` :

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

## 📱 Test sur smartphone

### Méthode 1 : Serveur local + réseau local

```bash
# Trouver votre IP locale
ifconfig | grep "inet "
# Exemple : 192.168.1.100

# Lancer le serveur
./site.sh serve

# Sur smartphone (même réseau WiFi)
# Ouvrir : http://192.168.1.100:8000
```

### Méthode 2 : GitHub Pages (production)

Une fois déployé sur GitHub Pages, le site est directement accessible depuis n'importe quel appareil.

### Méthode 3 : Outils de dev

Chrome DevTools > Device Mode (Cmd+Shift+M / Ctrl+Shift+M) pour simuler un smartphone.

## ⚠️ Limitations et solutions

### Taille du repository

GitHub Pages limite à 1 GB. Actuellement : 13 MB de ressources → largement dans les limites.

Si vous dépassez 1 GB :
- Héberger les MP3 ailleurs (Dropbox, Google Drive, etc.)
- Modifier `metadata.json` pour pointer vers les URLs externes
- Ne pousser que les métadonnées sur GitHub

### Fichiers MP3 volumineux

Pour réduire la taille :
- Utiliser `--vitesse 0.9` ou `1.0` (fichiers plus petits)
- Réduire `--longueur` (moins de mots = fichier plus court)
- Compresser les MP3 après génération (ffmpeg)

### Performance

Si le site devient lent avec beaucoup de ressources :
- Paginer les résultats (afficher 20 par page)
- Lazy loading des audios (charger à la demande)
- Compresser `metadata.json` (minifier)

## 🐛 Dépannage

### Le site ne trouve pas les ressources

```bash
# Vérifier que metadata.json existe et est à jour
ls -lh site_langues/metadata.json
cat site_langues/metadata.json | head -20

# Régénérer
./site.sh build
```

### Les fichiers audio ne se chargent pas

```bash
# Vérifier que resources/ existe
ls site_langues/resources/

# Vérifier les permissions
chmod -R 755 site_langues/resources/
```

### Erreur lors de la génération

```bash
# Vérifier l'environnement Python
which python
python --version

# Utiliser explicitement le bon Python
.venv312/bin/python build_site.py
```

### Le serveur ne démarre pas

```bash
# Port 8000 déjà utilisé ? Essayer un autre port
cd site_langues
python -m http.server 8080
```

## 📚 Documentation complète

- **DEPLOIEMENT_GITHUB_PAGES.md** : Guide détaillé de déploiement
- **site_langues/README.md** : Documentation du site web
- **GUIDE_UTILISATION.md** : Guide d'utilisation de genmp3.py
- **README.md** : Documentation générale du projet

## 🎉 Prochaines étapes

1. **Tester localement** : `./site.sh serve` et ouvrir http://localhost:8000
2. **Créer un repository GitHub** : https://github.com/new
3. **Déployer** : Suivre **DEPLOIEMENT_GITHUB_PAGES.md**
4. **Partager** : Envoyer l'URL à vos utilisateurs !

## ✨ Améliorations futures possibles

- [ ] Mode hors ligne (PWA avec Service Worker)
- [ ] Favoris et historique (localStorage)
- [ ] Quiz de compréhension après chaque texte
- [ ] Sous-titres synchronisés avec l'audio
- [ ] Export PDF des textes + vocabulaire
- [ ] Statistiques de progression
- [ ] Mode sombre
- [ ] Traduction du vocabulaire dans d'autres langues
- [ ] Recherche vocale

---

**Besoin d'aide ?**
- Consulter les fichiers de documentation
- Exécuter `./site.sh help`
- Vérifier les logs d'erreur
