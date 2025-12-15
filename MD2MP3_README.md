# md2mp3.py - Convertir Markdown en Audio MP3

## 🎯 Objectif

Convertir automatiquement des fichiers Markdown en audio MP3 avec :
- **Nettoyage automatique** du Markdown (suppression de #, *, $équations$, etc.)
- **Gestion des dialogues** avec voix différentes par personnage
- **Voix variées** (Azure TTS) dans 7 langues
- **Paramètres flexibles** : langue, genre, fichiers

## 🚀 Utilisation rapide

### Installation des dépendances

```bash
# Installer azure-cognitiveservices-speech et pydub
pip install azure-cognitiveservices-speech pydub ffmpeg-python

# Ou utiliser requirements.txt
pip install -r requirements.txt
```

### Exemples basiques

```bash
# Convertir un texte en français
python md2mp3.py docs/article/text.md -l fr

# Convertir en allemand avec voix féminine
python md2mp3.py docs/texte/text.md -l all --voix femme

# Convertir en anglais US avec voix aléatoire
python md2mp3.py document.md -l us

# Convertir un dialogue (détecte automatiquement)
python md2mp3.py dialogue.md -l fr
```

## 📋 Paramètres

```
usage: md2mp3.py [-h] -l {fr,eng,us,esp,hisp,nl,co} [-g {femme,homme}] [-v VOIX] [--format {mp3,wav}] fichier

positional arguments:
  fichier                Fichier Markdown à convertir

optional arguments:
  -l, --langue {fr,eng,us,esp,hisp,nl,co}
                        Langue (fr=français, eng=anglais UK, us=anglais US,
                        esp=espagnol, hisp=hispanique, nl=néerlandais, co=coréen)
  -g, --genre {femme,homme}
                        Genre de voix (défaut: aléatoire). Ignoré si --voix est spécifié.
  -v, --voix VOIX       Nom spécifique de voix (ex: 'denise', 'henri', 'aria').
                        Prioritaire sur --genre.
  --format {mp3,wav}    Format de sortie (défaut: mp3)
```

### Exemples d'utilisation

```bash
# Voix aléatoire (défaut)
python md2mp3.py texte.md -l fr

# Genre spécifique (voix féminine aléatoire)
python md2mp3.py texte.md -l fr -g femme

# Voix spécifique par prénom
python md2mp3.py texte.md -l fr -v denise
python md2mp3.py texte.md -l us -v aria
python md2mp3.py texte.md -l esp -v alvaro

# La voix spécifique est prioritaire sur le genre
python md2mp3.py texte.md -l fr -g homme -v denise
# → Utilise Denise (voix féminine) car --voix est prioritaire
```

## 🎤 Voix disponibles

Le script propose **95 voix Neural de haute qualité** réparties sur 7 langues.

### Français (19 voix : 11 féminines + 8 masculines)

| Genre | Prénoms disponibles | Exemple d'utilisation |
|-------|---------------------|----------------------|
| **Féminin** | denise, eloise, vivienne, brigitte, celeste, coralie, jacqueline, josephine, yvette, ariane, charline | `python md2mp3.py texte.md -l fr -v denise` |
| **Masculin** | henri, alain, claude, jerome, maurice, yves, fabrice, gerard | `python md2mp3.py texte.md -l fr -v henri` |

### Anglais UK (13 voix : 6 féminines + 7 masculines)

| Genre | Prénoms disponibles | Exemple d'utilisation |
|-------|---------------------|----------------------|
| **Féminin** | libby, maisie, sonia, bella, hollie, olivia | `python md2mp3.py texte.md -l eng -v libby` |
| **Masculin** | ryan, thomas, alfie, elliot, ethan, noah, oliver | `python md2mp3.py texte.md -l eng -v ryan` |

### Anglais US (20 voix : 12 féminines + 8 masculines)

| Genre | Prénoms disponibles | Exemple d'utilisation |
|-------|---------------------|----------------------|
| **Féminin** | aria, ava, emma, jenny, michelle, monica, amber, ana, ashley, cora, elizabeth, sara | `python md2mp3.py texte.md -l us -v aria` |
| **Masculin** | guy, brian, christopher, eric, jacob, jason, tony, davis | `python md2mp3.py texte.md -l us -v guy` |

### Espagnol Espagne (15 voix : 8 féminines + 7 masculines)

| Genre | Prénoms disponibles | Exemple d'utilisation |
|-------|---------------------|----------------------|
| **Féminin** | elvira, estrella, veronica, abril, irene, laia, lia, trisa | `python md2mp3.py texte.md -l esp -v elvira` |
| **Masculin** | alvaro, arnau, dario, elias, nil, saul, teo | `python md2mp3.py texte.md -l esp -v alvaro` |

### Espagnol Amérique latine (19 voix : 10 féminines + 9 masculines)

| Genre | Prénoms disponibles | Exemple d'utilisation |
|-------|---------------------|----------------------|
| **Féminin** | elena, marta, salome, beatriz, carlota, candela, larissa, marina, nuria, renata | `python md2mp3.py texte.md -l hisp -v marta` |
| **Masculin** | tomas, jorge, gonzalo, cecilio, gerardo, liberto, luciano, pelayo, yago | `python md2mp3.py texte.md -l hisp -v jorge` |

### Néerlandais (6 voix : 3 féminines + 3 masculines)

| Genre | Prénoms disponibles | Exemple d'utilisation |
|-------|---------------------|----------------------|
| **Féminin** | fenna, colette, dena | `python md2mp3.py texte.md -l nl -v fenna` |
| **Masculin** | maarten, coen, arnaud | `python md2mp3.py texte.md -l nl -v maarten` |

### Coréen (9 voix : 5 féminines + 4 masculines)

| Genre | Prénoms disponibles | Exemple d'utilisation |
|-------|---------------------|----------------------|
| **Féminin** | sunhi, yujin, hyunju, soonbok, jimin | `python md2mp3.py texte.md -l co -v sunhi` |
| **Masculin** | injoon, bongjin, gookmin, hyunsu | `python md2mp3.py texte.md -l co -v injoon` |

**Note** : Les prénoms ne sont **pas sensibles à la casse** (`Denise`, `denise`, `DENISE` fonctionnent tous).


## 🎭 Fonctionnalités avancées

### Nettoyage Markdown

Le script supprime automatiquement :
- **Titres** : `# Titre` → Titre
- **Gras/Italique** : `**texte**` ou `_texte_` → texte
- **Liens** : `[texte](url)` → texte
- **Listes** : `- item` → item
- **Code** : `` `code` `` ou ` ```code``` ` → code
- **Balises HTML** : `<tag>` → supprimé
- **YAML frontmatter** : `---...---` → supprimé

### Conversion d'équations mathématiques

Les équations sont converties en texte lisible :

| Équation | Résultat audio |
|----------|---|
| `$x^2+3=\sqrt{x}$` | "x au carré plus 3 égal racine de x" |
| `$\frac{a}{b}$` | "a divisé par b" |
| `$2^3$` | "2 au cube" |

### Détection et gestion des dialogues

Le script détecte automatiquement les dialogues au format :

```markdown
Marie: Bonjour comment allez-vous?
Pierre: Je vais très bien, merci!
```

**Ou** :

```markdown
**Marie**: Bonjour comment allez-vous?
**Pierre**: Je vais très bien, merci!
```

**Ou** :

```markdown
— Bonjour comment allez-vous?
— Je vais très bien, merci!
```

Pour chaque locuteur :
1. Le script assigne un genre selon le nom (bases de données internes)
2. Sélectionne une voix aléatoire correspondant à ce genre
3. Génère un audio séparé pour chaque ligne
4. Combine les audios avec des pauses naturelles

## 🔊 Variété des voix

Le script **ne choisit jamais la même voix deux fois** pour des personnages différents :

```
Marie → fr-FR-VivienneNeural
Pierre → fr-FR-AlainNeural
Jacques → fr-FR-BriceNeural
Sophie → fr-FR-EloiseNeural
```

Chaque langue possède 4-5 voix féminines et 4-5 voix masculines pour une bonne variété.

## 📁 Fichiers d'entrée/sortie

### Entrée
- **Format** : Markdown (`.md`)
- **Location** : N'importe où dans le système
- **Exemple** : `docs/mon_texte/text.md`

### Sortie
- **Format** : MP3 (`.mp3`)
- **Location** : Même dossier que l'entrée
- **Nom** : Même nom que l'entrée avec extension `.mp3`
- **Exemple** : `docs/mon_texte/text.mp3`

## ⚙️ Configuration requise

### Variables d'environnement (`.env`)

```env
# Clé API Azure Speech
AZURE_SPEECH_KEY=votre_clé_ici
AZURE_SPEECH_REGION=francecentral
```

Voir [AZURE_SETUP.md](AZURE_SETUP.md) pour créer un compte Azure.

### Dépendances système

- **Python 3.8+**
- **ffmpeg** : Pour la conversion audio
  - macOS : `brew install ffmpeg`
  - Linux : `sudo apt-get install ffmpeg`
  - Windows : Télécharger depuis [ffmpeg.org](https://ffmpeg.org)

## 🆘 Dépannage

### Erreur : "ModuleNotFoundError: No module named 'azure'"

```bash
pip install azure-cognitiveservices-speech
```

### Erreur : "AZURE_SPEECH_KEY not found in .env"

Vérifiez que vous avez :
1. Créé un compte Azure
2. Créé une ressource Speech
3. Copié la clé dans `.env`
4. Défini `AZURE_SPEECH_REGION`

### Erreur : "pydub not found or ffmpeg missing"

```bash
pip install pydub
brew install ffmpeg  # macOS
# ou
sudo apt-get install ffmpeg  # Linux
```

### Erreur : "No audio was received"

- Vérifiez votre connexion Internet
- Vérifiez que votre clé API est valide
- Vérifiez la région (exemple : `francecentral`, pas `France Central`)

## 📊 Cas d'usage

### 1. Générer l'audio d'un article

```bash
python md2mp3.py docs/article_climat/text.md -l fr
# Crée : docs/article_climat/text.mp3
```

### 2. Convertir des dialogues d'exercices

```bash
python md2mp3.py docs/dialogue_cafe/text.md -l fr
# Détecte automatiquement les personnages et assigne des voix
# Marie (femme) : voix féminine
# Pierre (homme) : voix masculine
```

### 3. Générer du contenu bilingue

```bash
python md2mp3.py chapitre1.md -l fr
python md2mp3.py chapter1.md -l eng
# Crée : chapitre1.mp3 et chapter1.mp3
```

### 4. Créer des ressources éducatives

```bash
# Pour chaque exercice dans docs/
for file in docs/*/text.md; do
    python md2mp3.py "$file" -l fr
done
```

## 🔮 Améliorations futures

- [ ] Support du multilangage dans un même fichier
- [ ] Contrôle de la vitesse de lecture (`--vitesse`)
- [ ] Ajustement du ton/inflexion
- [ ] Support d'autres services TTS (Google Cloud, Amazon Polly)
- [ ] Mode batch pour convertir plusieurs fichiers
- [ ] Gestion du stress/intonation dans les dialogues

## 📝 Exemple complet

**Fichier d'entrée** : `dialogue.md`

```markdown
---
titre: Conversation au café
niveau: B1
---

## Dialogue

Marie: Bonjour Pierre! Comment ça va?
Pierre: Salut! Ça va très bien, merci. Et toi?
Marie: Moi aussi! Je prendrais un café s'il te plaît.
Pierre: Bonne idée. Moi aussi je vais en prendre un.
```

**Commande** :
```bash
python md2mp3.py dialogue.md -l fr
```

**Résultat** :
- `dialogue.mp3` généré avec :
  - Marie = voix féminine française aléatoire
  - Pierre = voix masculine française aléatoire (différente)
  - Pauses naturelles entre les répliques
  - YAML frontmatter supprimé (pas lu)
  - Texte nettoyé

**Durée estimée** : 10-15 secondes d'audio

## 📄 Licence

Script créé pour le projet comprehension_orale - Usage éducatif libre
