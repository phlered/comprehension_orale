# 🎯 Refonte app.py - Guide de démarrage rapide

## ✅ Qu'est-ce qui a été fait?

Votre script `app.py` a été complètement transformé d'une **interface graphique tkinter** à un **script en ligne de commande moderne**.

### Avant ❌
- Interface tkinter (fenêtres, boutons, menus)
- Interaction souris + clavier
- Nécessite un affichage X11
- Difficile à automatiser

### Après ✅
- Paramètres en ligne de commande
- Exécution en une seule commande
- Pas d'interface graphique
- Parfait pour l'automatisation

---

## 🚀 Comment l'utiliser?

### La commande la plus simple

```bash
python3 app.py -l all -p "Thème" --niveau B1
```

### En français lisible

```bash
python3 app.py \
  --langue all \
  --prompt "Les animaux domestiques" \
  --niveau B1
```

---

## 📚 Voir les exemples

```bash
# Voir tous les exemples disponibles
python3 examples.py

# Exécuter un exemple
python3 examples.py run allemand_b1_court
```

---

## 🌍 Les 7 langues

| Code | Langue |
|------|--------|
| `eng` | Anglais (UK) |
| `us` | Anglais (US) |
| `all` | **Allemand** ⭐ |
| `esp` | Espagnol (Espagne) |
| `hisp` | Espagnol (Amérique) |
| `nl` | Néerlandais |
| `cor` | Coréen |

---

## 📊 Paramètres essentiels

```bash
-l    # Langue (obligatoire)
-p    # Prompt/Thème (obligatoire)
--niveau    # A1, A2, B1 (défaut), B2, C1, C2
--longueur  # Mots à générer (défaut: 150)
--voix      # femme (défaut) ou homme
```

---

## 💡 Exemples pratiques

### Exemple 1: Allemand basique
```bash
python3 app.py -l all -p "Animaux" --niveau B1
```

### Exemple 2: Anglais avancé
```bash
python3 app.py -l eng -p "Climate change" --niveau B2 --voix homme
```

### Exemple 3: Espagnol pour Seconde
```bash
python3 app.py -l esp -p "La familia" --niveau A2 --niveau-scolaire 2
```

### Exemple 4: Texte long
```bash
python3 app.py -l all -p "Technologie" --longueur 300 --niveau B2
```

---

## 📁 Où se trouvent les fichiers?

### Créés à chaque génération

```
docs/
└── theme_YYYYMMdd_HHMM/
    ├── README.md      ← Texte + Vocabulaire + Métadonnées
    └── audio.mp3      ← Fichier audio
```

### Exemples existants

```bash
ls -la docs/
# Voir les dossiers générés
```

---

## 📖 Documentation complète

```bash
# Guide d'utilisation détaillé
cat CLI_GUIDE.md

# Résumé des changements
cat REFONTE_CLI.md

# Rapport de completion
cat COMPLETION_REPORT.md
```

---

## 🆘 Aide rapide

```bash
# Voir tous les paramètres
python3 app.py --help

# Vérifier le setup
python3 verify_cli.py

# Voir les exemples
python3 examples.py
```

---

## 🎯 Points clés à retenir

✅ **Pas de interface graphique** - Tout se fait en CLI  
✅ **Paramètres en ligne de commande** - Plus de clics  
✅ **7 langues supportées** - Choix avec `-l`  
✅ **Automatisable** - Parfait pour les scripts  
✅ **Sortie structurée** - Dossier `docs/`  
✅ **Documentation complète** - 3 guides + exemples  

---

## 🔧 Configuration requise

Assurez-vous que:
1. ✅ Python 3.8+ installé
2. ✅ Dépendances installées (`openai`, `edge-tts`, `python-dotenv`)
3. ✅ Clé API OpenAI dans `.env`

---

## 📝 Structure de sortie

Pour chaque génération:

**README.md**
```yaml
---
langue: Allemand
prompt: Les animaux
niveau: B1
---

## Text
[Votre texte généré]

## Wortschatz
- **der Hund** → le chien
```

**audio.mp3**
- Fichier MP3 avec la lecture du texte

---

## 🎓 Niveaux de difficulté

| Niveau | Description |
|--------|-------------|
| **A1** | Débutant absolu |
| **A2** | Faux débutant |
| **B1** | Intermédiaire ⭐ (défaut) |
| **B2** | Intermédiaire avancé |
| **C1** | Avancé |
| **C2** | Bilingue natif |

---

## ✨ Spécialités par langue

- **Allemand** 🇩🇪 : Articles (der/die/das)
- **Anglais** 🇬🇧 : Verbes avec "to"
- **Coréen** 🇰🇷 : Alphabet hangul supporté
- **Espagnol** 🇪🇸 : UK et Amérique latine

---

## 🚀 Commandes essentielles

```bash
# Voir l'aide
python3 app.py --help

# Exemple rapide
python3 app.py -l all -p "Thème" --niveau B1

# Voir tous les exemples
python3 examples.py

# Exécuter un exemple
python3 examples.py run allemand_b1_court

# Vérifier le setup
python3 verify_cli.py
```

---

## 📊 Fichiers importants

| Fichier | Rôle |
|---------|------|
| `app.py` | **Script principal** (nouveau) |
| `app_tkinter.py` | Ancienne version (sauvegarde) |
| `CLI_GUIDE.md` | Documentation complète |
| `examples.py` | 10 exemples prêts |
| `verify_cli.py` | Vérifier l'installation |

---

## 🎉 Bon à savoir

1. **Ancien code sauvegardé** : `app_tkinter.py` est l'ancienne version
2. **Compatible** : Toutes les fonctionnalités sont conservées
3. **Plus rapide** : Pas d'overhead interface graphique
4. **Automatisable** : Intégrable dans n'importe quel script
5. **Documenté** : 3 guides + 10 exemples + help intégré

---

## 🤔 FAQs rapides

**Q: Comment générer un texte en allemand?**
```bash
python3 app.py -l all -p "Thème" --niveau B1
```

**Q: Je veux un texte plus long**
```bash
python3 app.py -l all -p "Thème" --longueur 300
```

**Q: Comment voir tous les paramètres?**
```bash
python3 app.py --help
```

**Q: Où vont les fichiers générés?**
```bash
# Dans le dossier docs/
ls docs/
```

**Q: Je veux revenir à l'ancienne version?**
```bash
python3 app_tkinter.py
```

---

## 📞 Support

- Consultez `CLI_GUIDE.md` pour la documentation détaillée
- Utilisez `python3 examples.py` pour des exemples
- Exécutez `python3 verify_cli.py` pour vérifier le setup

---

**Version** : 2.0 (CLI)  
**Status** : ✅ Opérationnel  
**Date** : 2025-12-10
