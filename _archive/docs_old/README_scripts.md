# Scripts de Compréhension Orale

Ce projet contient trois scripts Python modulaires pour créer du contenu d'apprentissage de langues.

## 📋 Scripts disponibles

### 1. `lit.py` - Conversion texte → audio

Convertit un fichier texte en audio MP3 avec synthèse vocale.

**Usage :**
```bash
python lit.py fichier.txt [OPTIONS]
```

**Options :**
- `--voix` : Choix de la voix (homme/femme) [défaut: femme]
- `--vitesse` : Vitesse de lecture en % (-30 à +30) [défaut: -5]
- `--langue` : Code langue (de/en/fr/es/nl/ko) [défaut: de]
- `--output` : Nom du fichier de sortie

**Exemples :**
```bash
# Lecture basique en allemand
python lit.py texte.txt

# Voix masculine plus lente
python lit.py texte.txt --voix homme --vitesse -10

# En anglais avec fichier de sortie personnalisé
python lit.py texte.txt --langue en --voix femme --output mon_audio.mp3
```

---

### 2. `creer.py` - Génération de textes

Génère un texte dans une langue donnée avec des paramètres configurables.

**Usage :**
```bash
python creer.py --theme "VOTRE_THEME" [OPTIONS]
```

**Options :**
- `--langue` : Langue (allemand/anglais/francais/espagnol/hollandais/coreen) [défaut: allemand]
- `--theme` : Thème du texte [**requis**]
- `--longueur` : Longueur en mots (±10%) [défaut: 300]
- `--niveau` : Niveau (A1/A2/B1/B2/C1/C2) [défaut: B1]
- `--output` : Nom du fichier de sortie

**Exemples :**
```bash
# Texte allemand basique
python creer.py --theme "droits de la femme"

# Texte anglais long et avancé
python creer.py --langue anglais --theme "climate change" --longueur 500 --niveau C1

# Texte français pour débutants
python creer.py --langue francais --theme "cuisine française" --niveau A2 --output mon_texte.txt
```

---

### 3. `vocabulaire.py` - Extraction de vocabulaire

Extrait les mots importants d'un texte et les traduit en français. Sortie au format Markdown.

**Usage :**
```bash
python vocabulaire.py fichier.txt [OPTIONS]
```

**Options :**
- `--nombre` : Nombre de mots à extraire [défaut: 15]
- `--theme` : Thème pour orienter l'extraction (optionnel)
- `--langue` : Langue du texte (de/en/fr/es/nl/ko) [défaut: de]
- `--output` : Nom du fichier de sortie
- `--genre` : Inclure le genre des mots (allemand uniquement)

**Exemples :**
```bash
# Vocabulaire allemand basique
python vocabulaire.py texte.txt

# 20 mots sur un thème spécifique avec genre
python vocabulaire.py texte.txt --nombre 20 --theme "droits de la femme" --genre

# Vocabulaire anglais
python vocabulaire.py texte_en.txt --langue en --nombre 25 --output vocab.md
```

---

## 🔧 Installation

1. **Cloner le projet :**
```bash
git clone https://github.com/phlered/comprehension_orale.git
cd comprehension_orale
```

2. **Créer un environnement virtuel :**
```bash
python -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
```

3. **Installer les dépendances :**
```bash
pip install openai edge-tts python-dotenv
```

4. **Configurer la clé API OpenAI :**
Créez un fichier `.env` à la racine du projet :
```
OPENAI_API_KEY=votre_cle_api_openai
```

---

## 🎯 Workflow complet

Exemple de création d'un exercice de compréhension orale complet :

```bash
# 1. Générer un texte allemand
python creer.py --theme "environnement" --niveau B1 --longueur 300

# 2. Extraire le vocabulaire avec genre
python vocabulaire.py texte_de_environnement_*.txt --nombre 15 --genre

# 3. Convertir en audio
python lit.py texte_de_environnement_*.txt --voix femme --vitesse -5
```

---

## 📦 Langues supportées

- 🇩🇪 Allemand (de)
- 🇬🇧 Anglais (en)
- 🇫🇷 Français (fr)
- 🇪🇸 Espagnol (es)
- 🇳🇱 Néerlandais (nl)
- 🇰🇷 Coréen (ko)

---

## 📝 Notes

- Les scripts `creer.py` et `vocabulaire.py` nécessitent une clé API OpenAI
- Le script `lit.py` utilise edge-tts (gratuit, pas d'API requise)
- Les fichiers générés incluent un timestamp pour éviter les écrasements
- Le format Markdown du vocabulaire est facilement convertible en PDF

---

## 🤝 Contribution

Pour toute question ou suggestion, ouvrez une issue sur GitHub.
