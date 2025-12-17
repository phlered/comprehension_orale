# Copilot Instructions - Comprehension Orale

## Vue d'ensemble

Projet de génération automatisée de ressources audio multilingues pour l'apprentissage des langues. Utilise OpenAI GPT pour générer des textes pédagogiques et Azure Text-to-Speech pour créer des MP3 de haute qualité avec voix neurales variées.

**Pipeline principal**: Prompt → Texte GPT → Audio Azure TTS → Site web statique

## Architecture

### Scripts principaux (exécution séquentielle)

1. **`genmp3.py`** - Point d'entrée pour créer une ressource complète
   - Génère texte via OpenAI (classe `TextGenerator`)
   - Extrait vocabulaire automatiquement (classe `VocabularyExtractor`)
   - Appelle `md2mp3.py` pour l'audio
   - Crée dossier dans `docs/[slug]_[timestamp]/` avec `text.md` et `audio.mp3`

2. **`md2mp3.py`** - Conversion Markdown → MP3
   - Utilise Azure Cognitive Services Speech SDK
   - Gère dialogues multi-locuteurs (détection automatique des lignes de dialogue)
   - 95+ voix neurales disponibles (classe `VoiceConfig`)
   - Nettoie Markdown (#, *, $équations$) avant synthèse vocale

3. **`build_site.py`** - Génération du site web statique
   - Scan `docs/` pour extraire métadonnées (frontmatter YAML)
   - Génère `site_langues/metadata.json` pour moteur de recherche
   - Copie ressources vers `site_langues/resources/`
   - Site déployable sur GitHub Pages

4. **`site.sh`** - Utilitaire de gestion du site
   - `./site.sh build` - Régénère le site
   - `./site.sh serve` - Serveur local (localhost:8000)
   - `./site.sh stats` - Statistiques des ressources

### Structure de données

**Ressource générée** (`docs/[slug]_[timestamp]/`):
```
text.md       # Frontmatter YAML + texte + vocabulaire
audio.mp3     # Synthèse vocale Azure
_temp_text.*  # Fichiers temporaires (ignorables)
```

**Frontmatter YAML** (obligatoire dans `text.md`):
```yaml
---
langue: Néerlandais
prompt: Commander une pizza
resume: Commander une pizza
longueur: 150
niveau: A1
genre: homme
date_generation: 2025-12-16 12:20:19
---
```

## Workflows de développement

### Créer une nouvelle ressource

```bash
# Utiliser genmp3.py avec Python de .venv312
.venv312/bin/python genmp3.py -l nl -p "Aller au supermarché" --niveau A1
```

**Options importantes**:
- `-l` : Langue (`fr`, `all`, `eng`, `us`, `esp`, `hisp`, `nl`, `co`, `it`)
- `-p` : Prompt/thème
- `--niveau` : A1, A2, B1, B2, C1, C2
- `--longueur` : Nombre de mots (~150 par défaut)
- `-g` : Genre (`homme`/`femme`) - voix aléatoire si omis
- `--vitesse` : Vitesse de lecture (0.7-1.0, défaut 0.8)
- `--style` : Pour C2 français (`journalistique`, `scientifique`, `sobre`)

### Régénérer le site après ajout

```bash
./site.sh build
./site.sh serve  # Tester localement
```

### Conventions importantes

1. **Noms de dossiers**: Format `[slug]_[YYYYMMDD_HHMM]/` automatique (fonction `slugify()` supprime accents)
2. **Vocabulaire**: Extraction automatique par regex selon langue (séparateurs `→` ou `|`)
3. **Tri vocabulaire**: Ignore articles selon langue (de/het pour NL, le/la/les pour FR, etc.)
4. **Dialogues**: Détection auto si lignes commencent par guillemets/tirets - alterne voix homme/femme

## Configuration

### Variables d'environnement (.env)

```bash
OPENAI_API_KEY=sk-...           # Obligatoire pour genmp3.py
AZURE_SPEECH_KEY=...            # Obligatoire pour md2mp3.py
AZURE_SPEECH_REGION=westeurope  # Région Azure
```

### Python

- **Environnement**: `.venv312/` (Python 3.12+)
- **Dépendances**: Voir `requirements.txt` (OpenAI, Azure Speech SDK, python-dotenv)

## Patterns spécifiques

### Mapping langues

Cohérence entre codes:
- `genmp3.py`: `nl` (néerlandais), `all` (allemand), `eng` (anglais UK)
- `md2mp3.py`: Idem
- `build_site.py`: Map vers codes internes (`LANGUAGE_MAP`, `LANGUAGE_NAMES`)

### Style C2 Français

Pour `niveau=C2` et `langue=fr`, le système applique un prompt enrichi orienté "contenu informatif":
- Styles: `journalistique`, `scientifique`, `sobre`
- Registre neutre, factuel (phrases 12-22 mots)
- Vocabulaire courant privilégié, termes techniques définis

### Gestion des voix

`md2mp3.py` utilise `VoiceConfig.VOICES` (dict par langue/genre). Exemple:
```python
VoiceConfig.VOICES["nl"]["female"]  # Liste voix féminines NL
```

Voix aléatoire si `-g` spécifié, sinon alternance homme/femme pour dialogues.

## Points d'attention

- **Pas de tests automatisés** - Vérifier manuellement après génération
- **Fichiers temporaires**: `_temp_text.*` créés par `md2mp3.py`, non supprimés automatiquement
- **Erreurs Azure**: Vérifier clés API et région si échec synthèse vocale
- **Déploiement**: GitHub Pages attend `site_langues/` à la racine
- **Prompts existants**: Voir `prompts/` pour inspiration (ex: `prompts_hollandais.md`)

## Fichiers de référence

- Architecture: [build_site.py](build_site.py), [genmp3.py](genmp3.py)
- Voix disponibles: [md2mp3.py](md2mp3.py#L35-L80) (classe `VoiceConfig`)
- Templates site: `site_langues/*.html`
- Documentation: [QUICKSTART.md](QUICKSTART.md), [MD2MP3_README.md](MD2MP3_README.md)
