# Conversion app.py → CLI

## 📊 Résumé de la refonte

**Date** : 2025-12-10  
**Changement majeur** : Suppression de l'interface graphique tkinter → Script CLI avec argparse  

---

## 🔄 Avant vs Après

### AVANT (tkinter)

```
app.py (435 lignes)
├── Interface graphique tkinter
├── Widgets (Button, Entry, OptionMenu, Scale, etc.)
├── Gestion des événements click/change
└── Fonction mainloop() bloquante
```

**Utilisation** : Clic sur les boutons, menus déroulants, champs texte

**Inconvénients** :
- ❌ Interfère avec les automatisations
- ❌ Nécessite une fenêtre X11
- ❌ Difficulté pour intégrer dans des pipelines
- ❌ Pas de scripting possible

### APRÈS (CLI)

```
app.py (~350 lignes, structure optimisée)
├── Classes modulaires (LanguageConfig, TextGenerator, etc.)
├── Argument parser avec argparse
├── Génération d'output structurée
└── Exécution en une commande
```

**Utilisation** : Commande en ligne avec paramètres

```bash
python3 app.py -l all -p "Thème" --niveau B1
```

**Avantages** :
- ✅ Automation facile
- ✅ Pas besoin d'affichage X11
- ✅ Intégrable dans des scripts/CI
- ✅ Logging structuré
- ✅ Documentation --help intégrée

---

## 📁 Structure de fichiers

### Nouveaux fichiers

| Fichier | Contenu |
|---------|---------|
| `app.py` | Script CLI principal (refonte) |
| `app_tkinter.py` | Ancienne version (sauvegarde) |
| `CLI_GUIDE.md` | Documentation complète |
| `examples.py` | 10 exemples d'utilisation |
| `run_cli.sh` | Script de démarrage shell |
| `test_app.py` | Tests basiques |

---

## 🎯 Paramètres

### Avant (Tkinter)
- Interface : widgets en cascade
- Entrée : clics + texte libre
- Sortie : fichiers dans répertoire courant

### Après (CLI)

#### Obligatoires
```
-l, --langue    : eng, us, all, esp, hisp, nl, cor (7 langues)
-p, --prompt    : Texte libre
```

#### Optionnels
```
--longueur       : 150 (défaut), plage 100-1000
--niveau         : B1 (défaut), choix A1-C2
--voix           : femme (défaut) ou homme
--niveau-scolaire: 2, 1, T (optionnel)
--axe            : axe1-4 (optionnel)
```

---

## 📦 Sortie

### Structure identique

```
docs/
└── theme_YYYYMMdd_HHMM/
    ├── README.md      ✅ Markdown avec YAML
    └── audio.mp3      ✅ Fichier audio
```

### Contenu README.md

```yaml
---
langue: Allemand
prompt: Les animaux domestiques
longueur: 150
niveau: B1
voix: femme
---

## Text
[Texte généré]

## Wortschatz
- **der Hund** → le chien
```

---

## 🔧 Installation

### Ancienne version (tkinter)
```bash
pip install openai edge-tts python-dotenv reportlab qrcode pillow
# Nécessite un affichage X11
python3 app_tkinter.py
```

### Nouvelle version (CLI)
```bash
pip install openai edge-tts python-dotenv
python3 app.py -l all -p "Thème" --niveau B1
```

---

## 📝 Exemples d'utilisation

### Ancien (tkinter)
1. Ouvrir `app.py`
2. Sélectionner langue dans menu
3. Taper thème dans champ texte
4. Cliquer "GÉNÉRER TOUT"
5. Attendre la barre de progression
6. Fichiers créés dans le répertoire courant

### Nouveau (CLI)

```bash
# Simple
python3 app.py -l all -p "Animaux" --niveau B1

# Complet avec options
python3 app.py -l all -p "Droits humains" --niveau A2 \
  --longueur 150 --voix homme --niveau-scolaire 2 --axe axe4

# Via script shell
./run_cli.sh -l eng -p "Climate" --niveau B2

# Voir les exemples
python3 examples.py
```

---

## 🎓 Niveaux de langue CECRL

Identique à la version tkinter :

| Niveau | Description |
|--------|-------------|
| **A1** | Débutant - phrases très simples |
| **A2** | Élémentaire - situations quotidiennes |
| **B1** | Intermédiaire ⭐ (défaut) |
| **B2** | Intermédiaire avancé |
| **C1** | Avancé - textes sophistiqués |
| **C2** | Maîtrise - niveau natif |

---

## 🌍 Langues supportées

| Code | Langue | UK/US | Notes |
|------|--------|-------|-------|
| `eng` | Anglais UK | ✅ | Voix: Libby/Ryan |
| `us` | Anglais US | ✅ | Voix: Aria/Guy |
| `all` | Allemand | - | Articles (der/die/das) |
| `esp` | Espagnol Espagne | ✅ | Voix: Elvira/Alvaro |
| `hisp` | Espagnol Amérique | ✅ | Voix: Elena/Tomas |
| `nl` | Néerlandais | - | Voix: Fenna/Coen |
| `cor` | Coréen | - | Voix: SunHi/InJoon |

---

## 📊 Comparaison de code

### Avant (tkinter - 435 lignes)
```python
# Imports tkinter
import tkinter as tk
from tkinter import messagebox, scrolledtext

class App:
    def __init__(self, root):
        self.root = root
        # Création widgets...
    
    def create_ui(self):
        # tk.Frame, tk.Label, tk.Button...
        # Structures imbriquées complexes
    
    def generate_all(self):
        # Logique mélangée avec UI
        self.log("Génération...")
        # ...
```

### Après (CLI - ~350 lignes, mieux organisé)
```python
# Imports modernes
import argparse
from pathlib import Path

class LanguageConfig:
    """Gestion des langues"""
    LANGUAGES = {...}

class TextGenerator:
    """Génère le texte"""
    def generate(self, langue_code, ...): ...

class AudioGenerator:
    """Génère l'audio"""
    @staticmethod
    async def generate(...): ...

class CompressionOralApp:
    """Application principale"""
    def run(self, args): ...

def main():
    parser = argparse.ArgumentParser()
    # Définition arguments...
    app = CompressionOralApp()
    return app.run(args)
```

**Avantages de la refonte** :
- ✅ Code plus lisible et modulaire
- ✅ Séparation des responsabilités
- ✅ Pas d'accouplage UI/logique
- ✅ Plus facile à tester
- ✅ Plus facile à étendre

---

## ✅ Checklist de migration

- [x] Créer script CLI avec argparse
- [x] Implémenter 7 langues
- [x] Implémenter 6 niveaux CECRL
- [x] Générer texte avec OpenAI
- [x] Extraire vocabulaire automatique
- [x] Générer audio avec edge-tts
- [x] Créer markdown avec YAML
- [x] Sauvegarder ancienne version
- [x] Créer documentation CLI_GUIDE.md
- [x] Créer exemples d'utilisation
- [x] Créer script de démarrage shell
- [x] Tests de base

---

## 🚀 Commandes rapides

```bash
# Voir l'aide
python3 app.py --help

# Voir les exemples
python3 examples.py
python3 examples.py run allemand_b1_court

# Exécution simple
python3 app.py -l all -p "Thème" --niveau B1

# Via script shell
./run_cli.sh -l eng -p "Topic" --niveau B2

# Tests
python3 test_app.py
```

---

## 📌 Notes importantes

1. **Backward compatibility** : L'ancienne version reste disponible comme `app_tkinter.py`

2. **Dossier docs/** : Crée automatiquement les dossiers si nécessaire

3. **Clé API** : Toujours requise via `OPENAI_API_KEY` en `.env`

4. **Sortie** : Structure identique (README.md + audio.mp3)

5. **Métadonnées** : Toujours incluses en YAML dans le markdown

---

**Status** : ✅ Refonte complétée  
**Version** : 2.0 (CLI)  
**Compatible** : Python 3.12+
