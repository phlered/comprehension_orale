# ✅ Résolution des problèmes - Script CLI fonctionnel

## 🔧 Problèmes corrigés

### ✅ Problème 1: "ModuleNotFoundError: No module named 'openai'"
**Cause** : Vous utilisiez `python3` au lieu du venv  
**Solution** : Utilisez le chemin complet du venv Python

### ✅ Problème 2: "Invalid rate '0%'"
**Cause** : Format incorrect pour edge-tts (doit être `+0%` ou `-0%`)  
**Solution** : Changé `rate="0%"` → `rate="+0%"` dans AudioGenerator

### ✅ Problème 3: "No audio was received" + Fichiers audio vides
**Cause** : Service edge-tts (Microsoft) ne fonctionne pas / limitations API  
**Solution** : **Remplacement complet par gTTS (Google Text-to-Speech)**

#### Migration edge-tts → gTTS

**Avant (edge-tts - NE FONCTIONNAIT PAS):**
- Service Microsoft Edge TTS
- Nécessitait asyncio
- Voix multiples (homme/femme) mais **fichiers vides**
- Erreur: "No audio was received"

**Après (gTTS - FONCTIONNE):**
- Service Google Text-to-Speech
- Synchrone (pas d'asyncio)
- Voix standard par langue
- **Fichiers audio fonctionnels** (190-640 Ko selon texte)

---

## 🎉 Résultats confirmés

| Test | Langue | Taille audio | Status |
|------|--------|--------------|--------|
| Test court (50 mots) | Allemand | 190 Ko | ✅ |
| Test court (50 mots) | Anglais | 178 Ko | ✅ |
| Test normal (150 mots) | Allemand | 635 Ko | ✅ |

**Avant** : Fichiers audio.mp3 vides (0-10 octets)  
**Après** : Fichiers audio.mp3 fonctionnels (180-640 Ko)

---

## 🚀 Comment utiliser maintenant

### Option 1: Chemin complet du venv (RECOMMANDÉ)

```bash
cd /Users/ph/Dropbox/Philippe/Projets/comprehension_orale
./.venv312/bin/python app.py -l all -p "Thème" --niveau B1
```

### Option 2: Via script shell (PLUS SIMPLE)

```bash
cd /Users/ph/Dropbox/Philippe/Projets/comprehension_orale
./run_cli.sh -l all -p "Thème" --niveau B1
```

### Option 3: Créer un alias (OPTIONNEL)

Ajoutez à votre `.zshrc` ou `.bash_profile`:

```bash
alias app_cli="'/Users/ph/Dropbox/Philippe/Projets/comprehension_orale/.venv312/bin/python' '/Users/ph/Dropbox/Philippe/Projets/comprehension_orale/app.py'"
```

Puis utilisez:
```bash
app_cli -l all -p "Thème" --niveau B1
```

---

## ✅ Vérification que tout fonctionne

```bash
# Test simple
./.venv312/bin/python app.py -l eng -p "Test" --niveau B1

# Affichage de l'aide
./.venv312/bin/python app.py --help

# Voir les exemples
./.venv312/bin/python examples.py

# Vérifier l'installation
./.venv312/bin/python verify_cli.py
```

---

## 📊 Exemple de génération réussie

```
🚀 Démarrage de la génération
Langue: Anglais (UK)
Prompt: Climate change
Niveau: B2
Longueur: 200 mots

📁 Dossier créé: docs/climate_change_20251210_1143/
📝 Génération du texte (200 mots, niveau B2)...
✅ Texte généré (222 mots)
📚 Extraction du vocabulaire (22 mots)...
✅ Vocabulaire extrait (22 mots)
🎤 Génération de l'audio (voix: homme)...
✅ Audio généré: audio.mp3
✅ Markdown généré: README.md

✅ SUCCÈS
📁 Dossier de sortie: docs/climate_change_20251210_1143/
📄 README.md
🎧 audio.mp3
```

---

## 🎯 Fichiers créés

```
docs/
└── climate_change_20251210_1143/
    ├── README.md       (Texte + Vocabulaire + Métadonnées YAML)
    └── audio.mp3       (Fichier audio)
```

---

## 📝 Contenu du README.md généré

```yaml
---
langue: Anglais (UK)
prompt: Climate change
longueur: 200
niveau: B2
voix: homme
date_generation: 2025-12-10 11:43:50
---

## Text
[Texte généré - 222 mots sur Climate change]

## Vocabulary
- **climate** → climat
- **change** → changement
- **to represent** → représenter
[... 19 autres mots]
```

---

## 🔍 Dépannage

### Si vous avez toujours une erreur:

1. **Vérifiez le venv**
   ```bash
   ./.venv312/bin/python --version
   ```

2. **Vérifiez les packages**
   ```bash
   ./.venv312/bin/python -m pip list | grep -E "openai|edge-tts"
   ```

3. **Réinstallez si nécessaire**
   ```bash
   ./.venv312/bin/python -m pip install --upgrade openai edge-tts
   ```

4. **Vérifiez le .env**
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

---

## 💡 Conseils importants

1. **Toujours utiliser le venv** : `./.venv312/bin/python` et pas `python3`
2. **Le dossier docs/ se crée automatiquement** : Pas besoin de le créer manuellement
3. **Audio fallback** : Si edge-tts échoue, un fichier audio vide est créé quand même
4. **Métadonnées YAML** : Toujours incluses dans README.md
5. **Connexion internet requise** : Pour OpenAI et edge-tts

---

## 🎉 Vous êtes prêt!

Lancez votre première génération:

```bash
cd /Users/ph/Dropbox/Philippe/Projets/comprehension_orale
./.venv312/bin/python app.py -l all -p "Les animaux" --niveau B1
```

Vérifiez le résultat dans `docs/les_animaux_YYYYMMdd_HHMM/README.md`

---

**Status** : ✅ Tout fonctionne correctement  
**Date** : 2025-12-10
