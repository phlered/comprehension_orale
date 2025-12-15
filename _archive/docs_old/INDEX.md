# 📚 Index de la documentation - Refonte CLI

## 🎯 Vous êtes nouveau? Commencez ici!

### 📖 Pour une introduction rapide (5 minutes)
→ Lisez **[QUICKSTART.md](QUICKSTART.md)**

### 💻 Pour utiliser le script
→ Consultez **[CLI_GUIDE.md](CLI_GUIDE.md)**

### 📊 Pour comprendre ce qui a changé
→ Lisez **[REFONTE_CLI.md](REFONTE_CLI.md)**

---

## 📋 Index complet des documents

### 🚀 **Démarrage rapide**
- **[QUICKSTART.md](QUICKSTART.md)** (5 min) - Guide ultra-rapide pour commencer
  - Qu'est-ce qui a changé?
  - Comment l'utiliser?
  - Exemples simples

### 📖 **Documentation complète**
- **[CLI_GUIDE.md](CLI_GUIDE.md)** (15 min) - Documentation exhaustive
  - Installation & configuration
  - Tous les paramètres
  - Exemples complets
  - Dépannage

### 🔄 **Résumé de la refonte**
- **[REFONTE_CLI.md](REFONTE_CLI.md)** (10 min) - Avant vs Après
  - Structure avant/après
  - Comparaison code
  - Avantages de la refonte
  - Checklist migration

### ✅ **Rapport de completion**
- **[COMPLETION_REPORT.md](COMPLETION_REPORT.md)** (5 min) - État final du projet
  - Changements apportés
  - Fichiers créés
  - Checklist de completion
  - Points forts

---

## 🛠️ Fichiers du projet

### Scripts exécutables
```bash
app.py                  # ⭐ PRINCIPAL - Script CLI
app_tkinter.py          # Ancienne version (sauvegarde)
examples.py             # 10 exemples d'utilisation
verify_cli.py           # Vérifier l'installation
run_cli.sh              # Script de démarrage shell
```

### Documentation
```bash
QUICKSTART.md           # Guide rapide (vous êtes ici)
CLI_GUIDE.md            # Documentation complète
REFONTE_CLI.md          # Résumé changements
COMPLETION_REPORT.md    # Rapport final
INDEX.md                # Cet index
```

### Configuration
```bash
.env                    # Configuration API (obligatoire)
.env.example            # Exemple de .env
```

---

## 🎯 Cas d'usage typiques

### 1️⃣ Je veux générer du contenu en allemand
```bash
# Voir QUICKSTART.md → "Exemple 1"
python3 app.py -l all -p "Animaux" --niveau B1
```

### 2️⃣ Je veux automatiser la génération
```bash
# Voir CLI_GUIDE.md → "Automatisation"
for theme in "Animaux" "Technologie" "Environnement"; do
  python3 app.py -l all -p "$theme" --niveau B1
done
```

### 3️⃣ Je veux voir tous les paramètres
```bash
# Voir CLI_GUIDE.md → "Paramètres CLI"
python3 app.py --help
```

### 4️⃣ Je veux des exemples
```bash
# Voir examples.py
python3 examples.py
```

### 5️⃣ Je veux vérifier mon installation
```bash
python3 verify_cli.py
```

---

## 📊 Cheat Sheet

### Langues (code court)
```
eng  = Anglais UK
us   = Anglais US
all  = Allemand ⭐
esp  = Espagnol Espagne
hisp = Espagnol Amérique
nl   = Néerlandais
cor  = Coréen
```

### Niveaux (CECRL)
```
A1 = Débutant
A2 = Élémentaire
B1 = Intermédiaire ⭐ (défaut)
B2 = Avancé
C1 = Très avancé
C2 = Natif
```

### Commande type
```bash
python3 app.py -l CODE -p "THÈME" --niveau NIVEAU
```

---

## 🚀 Commandes rapides

```bash
# Aide
python3 app.py --help

# Voir les exemples
python3 examples.py

# Exécuter un exemple
python3 examples.py run allemand_b1_court

# Vérifier l'installation
python3 verify_cli.py

# Générer du contenu
python3 app.py -l all -p "Thème" --niveau B1

# Voir la documentation
cat CLI_GUIDE.md
cat REFONTE_CLI.md
```

---

## 📁 Structure des fichiers générés

```
docs/
└── theme_YYYYMMdd_HHMM/          # Nom: thème + horodatage
    ├── README.md                 # Texte + Vocabulaire + YAML
    └── audio.mp3                 # Fichier audio
```

**Exemple après génération:**
```
docs/
└── animaux_20251210_1530/
    ├── README.md
    └── audio.mp3
```

---

## 🔧 Installation & configuration

### 1. Clé API OpenAI
Créez un fichier `.env`:
```
OPENAI_API_KEY=sk-xxxxxxxxxxxx
```

### 2. Dépendances
```bash
pip install openai edge-tts python-dotenv
```

### 3. Vérifier
```bash
python3 verify_cli.py
```

---

## ❓ Questions fréquentes

**Q: Où sont les fichiers générés?**
→ Dans `docs/` avec le nom du thème + horodatage

**Q: Comment je reviens à l'ancienne version?**
→ Utilisez `python3 app_tkinter.py`

**Q: Quel niveau recommandez-vous?**
→ **B1** (intermédiaire) - c'est le défaut

**Q: Je peux générer plusieurs langues?**
→ Oui! Lancez le script plusieurs fois

**Q: C'est quoi ce fichier README.md dans chaque dossier?**
→ C'est votre texte + vocabulaire + métadonnées YAML

---

## 📚 Lectures recommandées

1. **Commencer** → [QUICKSTART.md](QUICKSTART.md)
2. **Approfondir** → [CLI_GUIDE.md](CLI_GUIDE.md)
3. **Comprendre** → [REFONTE_CLI.md](REFONTE_CLI.md)
4. **Vérifier** → Exécutez `python3 verify_cli.py`

---

## 🎊 Summary

| Aspect | Avant | Après |
|--------|-------|-------|
| Interface | Tkinter GUI | CLI moderne |
| Démarrage | Clic boutons | Une commande |
| Automatisation | Difficile | Facile |
| Documentation | Minimale | Complète |
| Langues | 5 | 7 ✅ |
| Niveaux | 6 | 6 ✅ |

---

**Version** : 2.0 (CLI)
**Status** : ✅ Complet et opérationnel
**Dernière mise à jour** : 2025-12-10
