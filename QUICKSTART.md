# 🚀 Démarrage Rapide - Site Web Langues

## ⚡ En 30 secondes

```bash
# 1. Tester localement
./site.sh serve
# Ouvrir http://localhost:8000

# 2. Créer un repo GitHub
# https://github.com/new

# 3. Pousser le code
git init
git add .
git commit -m "Site langues initial"
git remote add origin https://github.com/[USERNAME]/[REPO].git
git push -u origin main

# 4. Activer GitHub Pages
# Settings > Pages > Source: main > Folder: /site_langues
```

## 📱 Test smartphone (réseau local)

```bash
# Trouver votre IP
ifconfig | grep "inet " | grep -v 127.0.0.1

# Lancer le serveur
./site.sh serve

# Sur smartphone : http://[VOTRE_IP]:8000
```

## ➕ Ajouter des ressources

```bash
# 1. Créer une ressource
genmp3 -l nl -p "Nouveau thème" --niveau A1

# 2. Régénérer le site
./site.sh build

# 3. Tester
./site.sh serve

# 4. Déployer
git add site_langues/
git commit -m "Ajout ressources"
git push
```

## 📊 Commandes utiles

```bash
./site.sh stats    # Statistiques
./site.sh deploy   # Vérifications avant déploiement
./site.sh help     # Liste des commandes
```

## 📚 Documentation complète

- **RECAP_SITE_WEB.md** - Vue d'ensemble
- **GUIDE_SITE_WEB.md** - Guide complet
- **DEPLOIEMENT_GITHUB_PAGES.md** - Déploiement détaillé

## ✅ Actuellement

- **30 ressources** (~13 MB)
- **5 langues** (Anglais, Allemand, Espagnol, Néerlandais, Coréen)
- **Interface responsive** (smartphone ready)
- **Moteur de recherche** avec filtres
- **Lecteur audio** intégré

---

**🎉 C'est prêt !** Testez maintenant : `./site.sh serve`
