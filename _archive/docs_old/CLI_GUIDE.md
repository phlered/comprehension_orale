# Guide d'utilisation du nouveau script CLI

## 📋 Résumé des changements

Le script `app.py` a été **complètement refondu** en **interface en ligne de commande** (CLI). L'ancienne version avec interface graphique tkinter a été sauvegardée sous `app_tkinter.py`.

## 🚀 Utilisation

### Commande basique

```bash
python3 app.py -l all -p "Les animaux domestiques" --niveau B1
```

### Paramètres obligatoires

- **`-l, --langue`** : Code de la langue (requis)
  - `eng` = Anglais (UK)
  - `us` = Anglais (US)
  - `all` = Allemand
  - `esp` = Espagnol (Espagne)
  - `hisp` = Espagnol (Amérique du Sud)
  - `nl` = Néerlandais
  - `cor` = Coréen

- **`-p, --prompt`** : Thème du texte à générer (requis)
  - Exemple: `"Les animaux domestiques"`, `"Climate change"`, `"La familia"`

### Paramètres optionnels

- **`--longueur`** (défaut: 150) : Nombre de mots à générer
  - Exemple: `--longueur 200`

- **`--niveau`** (défaut: B1) : Niveau de langue CECRL
  - Choix: `A1, A2, B1, B2, C1, C2`
  - Exemple: `--niveau B2`

- **`--voix`** (défaut: femme) : Genre de la voix
  - Choix: `femme, homme`
  - Exemple: `--voix homme`

- **`--niveau-scolaire`** (optionnel) : Niveau scolaire français
  - Choix: `2` (Seconde), `1` (Première), `T` (Terminale)
  - Exemple: `--niveau-scolaire 2`

- **`--axe`** (optionnel) : Axe du curriculum
  - Choix: `axe1, axe2, axe3, axe4`
  - Exemple: `--axe axe1`

## 📁 Structure de sortie

Le script crée un **dossier dans `docs/`** avec le format suivant:

```
docs/
└── theme_YYYYMMdd_HHMM/
    ├── README.md      # Contenu + métadonnées YAML
    └── audio.mp3      # Fichier audio
```

### Contenu du fichier README.md

```yaml
---
langue: Allemand
prompt: Les animaux domestiques
longueur: 150
niveau: B1
voix: femme
date_generation: 2025-12-10 15:30:00
---

## Text

[Texte généré par OpenAI]

## Wortschatz

- **der Hund** → le chien
- **die Katze** → le chat
- ...
```

## 📝 Exemples complets

### Exemple 1 : Allemand B1 (150 mots, voix femme)
```bash
python3 app.py -l all -p "Les animaux domestiques" --niveau B1
```

### Exemple 2 : Anglais US B2 (200 mots, voix homme)
```bash
python3 app.py -l us -p "Climate change" --longueur 200 --niveau B2 --voix homme
```

### Exemple 3 : Espagnol A2 (Seconde, Axe 1)
```bash
python3 app.py -l esp -p "La familia" --niveau A2 --niveau-scolaire 2 --axe axe1
```

### Exemple 4 : Néerlandais B1
```bash
python3 app.py -l nl -p "Koken en recepten" --niveau B1
```

## 🔧 Configuration requise

### Variables d'environnement

Créez un fichier `.env` à la racine du projet:

```env
OPENAI_API_KEY=sk-xxx...
```

### Dépendances Python

```bash
pip install openai gtts python-dotenv
```

**Note** : Le script utilise maintenant **gTTS (Google Text-to-Speech)** au lieu de edge-tts, car edge-tts ne fonctionnait pas de manière fiable.

## 📊 Fonctionnalités

✅ **7 langues supportées** (anglais UK/US, allemand, espagnol, néerlandais, coréen)

✅ **6 niveaux de langue** (A1 à C2, recommandé B1)

✅ **Génération d'audio** en temps réel avec edge-tts

✅ **Extraction vocabulaire** automatique (10% du nombre de mots)

✅ **Métadonnées YAML** dans le markdown

✅ **Titres traduits** selon la langue (Text, Texto, Tekst, etc.)

✅ **Articles définis** pour l'allemand (der/die/das)

✅ **Verbes en anglais** avec "to"

## 🐛 Dépannage

### Erreur "Clé API manquante"
→ Vérifiez que `OPENAI_API_KEY` est définie dans `.env`

### Erreur "ModuleNotFoundError"
→ Installez les dépendances: `pip install openai edge-tts python-dotenv`

### Erreur lors de la génération
→ Vérifiez votre connexion internet et que votre clé API est valide

## 📦 Fichiers importants

| Fichier | Description |
|---------|-------------|
| `app.py` | 🆕 Nouveau script CLI |
| `app_tkinter.py` | Ancienne version avec interface graphique |
| `.env` | Configuration (clé API OpenAI) |
| `docs/` | Dossier de sortie des générations |

## 🔄 Migration depuis l'ancienne version

L'ancienne version tkinter reste disponible sous `app_tkinter.py` pour compatibilité. Pour l'utiliser:

```bash
python3 app_tkinter.py
```

## 💡 Conseils

- **Pour débuter** : utilisez le niveau B1 (défaut)
- **Pour contenu long** : augmentez `--longueur` (200-300 mots)
- **Pour Seconde** : combinez `--niveau A2` + `--niveau-scolaire 2`
- **Pour les axes** : consultez la Réforme du bac pour les valeurs appropriées

---

**Version** : 2.0 (CLI)  
**Date** : 2025-12-10  
**Auteur** : Philippe
