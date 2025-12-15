# 🎧 Générateur de Compréhension Orale - Allemand

Application interactive pour créer automatiquement des exercices de compréhension orale en allemand avec génération de vocabulaire et audio MP3.

## ✨ Fonctionnalités

- 🤖 **Génération automatique de vocabulaire** : L'IA génère 15 mots en allemand sur le thème de votre choix
- ✅ **Sélection interactive** : Cases à cocher pour choisir les mots à utiliser
- ➕ **Ajout de mots personnalisés** : Possibilité d'ajouter vos propres mots
- 📝 **Génération de texte** : Création d'un texte cohérent en allemand utilisant le vocabulaire sélectionné
- 🎤 **Audio haute qualité** : Génération automatique d'un fichier MP3 avec voix allemande naturelle (Microsoft Edge TTS)
- 📊 **Contrôle de la longueur** : Choisissez le nombre de mots du texte (±10%)

## 🚀 Installation

### 1. Créer un environnement virtuel (si ce n'est pas déjà fait)

```bash
python3 -m venv .venv
source .venv/bin/activate  # Sur macOS/Linux
```

### 2. Installer les dépendances

```bash
pip3 install --user openai edge-tts python-dotenv
```

### 3. Configurer la clé API

1. Créez un compte sur [OpenAI Platform](https://platform.openai.com/)
2. Obtenez votre clé API sur https://platform.openai.com/api-keys
3. Éditez le fichier `.env` :

```bash
nano .env
```

4. Remplacez `sk-votre_clé_openai_ici` par votre vraie clé API :

```
OPENAI_API_KEY=sk-proj-votre_vraie_clé_ici
```

## 📖 Utilisation

### Lancer l'application

```bash
python app_comprehension_orale.py
```

### Workflow

1. **Étape 1** : Entrez un thème (ex: "les droits de la femme", "l'environnement", "la technologie")
2. **Étape 2** : Cliquez sur "🤖 Générer le vocabulaire (IA)"
3. **Étape 3** : Sélectionnez/désélectionnez les mots avec les cases à cocher
4. **Étape 4** : Ajoutez des mots personnalisés si souhaité avec "➕ Ajouter un mot personnalisé"
5. **Étape 5** : Choisissez le nombre de mots du texte (par défaut : 300)
6. **Étape 6** : Cliquez sur "🚀 Générer le texte et l'audio MP3"
7. **Résultat** : L'application crée automatiquement :
   - Un fichier `.txt` avec le texte allemand
   - Un fichier `.md` avec le vocabulaire et le texte
   - Un fichier `.mp3` avec l'audio

## 📁 Fichiers générés

Les fichiers sont nommés automatiquement avec le format :
- `texte_[theme]_[date_heure].txt`
- `texte_[theme]_[date_heure].md`
- `audio_[theme]_[date_heure].mp3`

Exemple :
- `texte_droits_femme_20251021_143022.txt`
- `texte_droits_femme_20251021_143022.md`
- `audio_droits_femme_20251021_143022.mp3`

## 🎨 Mode Manuel

Si vous n'avez pas de clé API ou préférez travailler sans IA :
1. Cliquez sur "✏️ Mode manuel"
2. Ajoutez vos mots manuellement avec "➕ Ajouter un mot personnalisé"
3. Note : La génération de texte nécessite quand même l'API IA

## 🔧 Configuration avancée

### Changer la voix allemande

Dans `app_comprehension_orale.py`, ligne ~480, modifiez :

```python
voice="de-DE-KatjaNeural",  # Voix féminine
```

Autres voix disponibles :
- `de-DE-ConradNeural` - Voix masculine allemande
- `de-AT-IngridNeural` - Voix autrichienne féminine
- `de-CH-LeniNeural` - Voix suisse féminine

### Ajuster la vitesse de lecture

Modifiez le paramètre `rate` :

```python
rate="-5%"   # 5% plus lent
rate="0%"    # Vitesse normale
rate="+10%"  # 10% plus rapide
```

## 🐛 Dépannage

### Erreur "OPENAI_API_KEY non trouvée"
- Vérifiez que le fichier `.env` existe
- Vérifiez que la clé API est correcte (commence par `sk-proj-` ou `sk-`)
- Pas d'espaces autour du `=`
- Relancez l'application

### Erreur lors de la génération audio
- Vérifiez votre connexion internet (edge-tts nécessite internet)
- Essayez de relancer la génération

### Interface ne s'affiche pas
- Vérifiez que tkinter est installé (inclus par défaut sur macOS)
- Sur Linux : `sudo apt-get install python3-tk`

## 📚 Exemples de thèmes

- Les droits de la femme
- L'environnement et le climat
- La technologie et l'intelligence artificielle
- Les voyages et le tourisme
- La santé et l'alimentation
- L'éducation
- Le sport
- La culture allemande
- Les médias sociaux
- L'économie

## 🤝 Contribution

N'hésitez pas à améliorer l'application et à partager vos suggestions !

## 📄 Licence

Libre d'utilisation pour un usage éducatif.
