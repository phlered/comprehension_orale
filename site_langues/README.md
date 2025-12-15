# Site Web d'Apprentissage des Langues

Site web statique pour consulter les ressources audio d'apprentissage des langues sur smartphone.

## 🌍 Langues disponibles

- 🇬🇧 Anglais
- 🇩🇪 Allemand  
- 🇪🇸 Espagnol
- 🇳🇱 Néerlandais
- 🇰🇷 Coréen

## ✨ Fonctionnalités

### Page d'accueil
- Sélection de la langue par drapeaux
- Interface épurée et intuitive

### Page de recherche
- Moteur de recherche par mots-clés
- Filtres avancés :
  - Niveau (A1, A2, B1, B2, C1, C2)
  - Classe (Seconde, Première, Terminale)
  - Axe du programme
- Liste dynamique des ressources disponibles
- Aperçu du texte et statistiques (nombre de mots, vocabulaire)

### Page de lecture
- Lecteur audio HTML5 (lecture/pause, contrôle du volume)
- Boutons pour afficher/masquer :
  - 📄 Le texte complet
  - 📚 Le vocabulaire avec traductions
- Navigation facile vers la recherche

## 📱 Optimisation mobile

- Design responsive adapté aux smartphones
- Boutons tactiles larges et ergonomiques
- Chargement rapide
- Interface fluide et intuitive

## 🚀 Génération du site

### Prérequis
- Python 3.x
- Environnement virtuel `.venv312` activé

### Commandes

```bash
# Générer le site depuis le répertoire du projet
python build_site.py
```

Le script `build_site.py` effectue automatiquement :
1. Scan du répertoire `docs/` pour identifier toutes les ressources
2. Extraction des métadonnées depuis le front matter des fichiers `text.md`
3. Génération du fichier `metadata.json` pour le moteur de recherche
4. Copie des fichiers audio et texte vers `site_langues/resources/`
5. Affichage des statistiques par langue

### Structure générée

```
site_langues/
├── index.html              # Page d'accueil avec sélection de langue
├── search.html             # Page de recherche avec filtres
├── player.html             # Page de lecture avec lecteur audio
├── metadata.json           # Index des ressources pour la recherche
└── resources/              # Ressources copiées depuis docs/
    └── [resource_id]/
        ├── audio.mp3       # Fichier audio
        └── text.md         # Texte et vocabulaire
```

## 📊 Statistiques actuelles

Après génération :
- **30 ressources** au total
- **Allemand** : 7 ressources
- **Néerlandais** : 20 ressources
- **Anglais** : 1 ressource
- **Français** : 1 ressource
- **Coréen** : 1 ressource

## 🌐 Déploiement sur GitHub Pages

### Configuration

1. Créer un fichier `.gitignore` à la racine pour exclure les fichiers inutiles :

```gitignore
# Python
__pycache__/
*.py[cod]
.venv*/
*.egg-info/

# Système
.DS_Store
Thumbs.db

# Documents sources (on ne pousse que le site généré)
docs/
_archive/
anciens_scripts/
autre_documents/
old_documents/
```

2. Créer un repository GitHub et pousser le code

3. Configurer GitHub Pages :
   - Aller dans **Settings** > **Pages**
   - Sélectionner **Deploy from a branch**
   - Choisir la branche `main` (ou `master`)
   - Sélectionner le dossier `/site_langues` comme source
   - Cliquer sur **Save**

4. Le site sera accessible à : `https://[username].github.io/[repository-name]/`

### Mise à jour du site

Après avoir généré de nouvelles ressources avec `genmp3.py` :

```bash
# 1. Régénérer le site
python build_site.py

# 2. Commiter les changements
git add site_langues/
git commit -m "Mise à jour des ressources"

# 3. Pousser vers GitHub
git push origin main
```

GitHub Pages mettra automatiquement à jour le site en quelques minutes.

## 🛠️ Technologies utilisées

- **HTML5** : Structure sémantique et lecteur audio natif
- **CSS3** : Design responsive avec gradients et animations
- **JavaScript vanilla** : Interactivité sans dépendances
- **JSON** : Métadonnées des ressources pour la recherche
- **Python** : Script de build automatique

## 📝 Notes techniques

### Format des métadonnées

Le fichier `metadata.json` contient :
- `generated_at` : Date de génération
- `total_resources` : Nombre total de ressources
- `languages` : Liste des codes de langues disponibles
- `resources[]` : Tableau des ressources avec :
  - `id` : Identifiant unique (nom du dossier)
  - `langue` : Code langue (eng, all, esp, nl, cor)
  - `prompt` : Description de la ressource
  - `niveau` : Niveau CECRL (A1-C2)
  - `classe` : Classe scolaire (optionnel)
  - `axe` : Axe du programme (optionnel)
  - `genre` : Voix (femme/homme)
  - `date` : Date de génération
  - `longueur` : Nombre de mots du texte
  - `text_preview` : Aperçu du texte (200 caractères)
  - `vocab_count` : Nombre de mots de vocabulaire
  - `audio_path` : Chemin relatif vers le MP3
  - `text_path` : Chemin relatif vers le markdown

### Compatibilité

Le site est compatible avec :
- ✅ Chrome/Edge (desktop et mobile)
- ✅ Safari (iOS et macOS)
- ✅ Firefox (desktop et mobile)
- ✅ Samsung Internet
- ✅ Tous les navigateurs modernes supportant HTML5 audio

## 🎯 Améliorations futures possibles

- [ ] Favoris et historique de lecture (localStorage)
- [ ] Mode sombre
- [ ] Vitesse de lecture ajustable
- [ ] Sous-titres synchronisés avec l'audio
- [ ] Téléchargement des ressources pour usage hors ligne
- [ ] Statistiques de progression
- [ ] Quiz de compréhension
