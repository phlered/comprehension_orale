# Configuration d'Azure Text-to-Speech (TTS)

## 📋 Étapes pour créer un compte Azure et accéder à TTS

### 1. Créer un compte Azure (gratuit)

1. Allez sur [portal.azure.com](https://portal.azure.com)
2. Cliquez sur **Créer un compte** (Sign up for free)
3. Entrez votre email Microsoft (Outlook/Hotmail) ou créez un nouveau compte
4. Complétez vos informations personnelles
5. Ajoutez une carte de crédit (pour vérifier votre identité, sans frais)
6. Acceptez les conditions et cliquez **Commencer**

**Important** : Azure donne 12 mois gratuits + 200$ de crédit. Les services TTS utilisent peu de crédit (environ 0,001$ pour 1000 caractères).

### 2. Créer une ressource Speech

1. Dans le portail Azure, cliquez sur **+ Créer une ressource**
2. Recherchez **Speech**
3. Cliquez sur **Speech** (par Microsoft)
4. Cliquez sur **Créer**

Remplissez le formulaire :
- **Abonnement** : Sélectionnez votre abonnement
- **Groupe de ressources** : Créez un nouveau groupe ou en sélectionnez un
  - Nom : `comprehension-orale-rg`
- **Région** : Sélectionnez la région la plus proche
  - `France Central` (Paris) ou `West Europe` (Pays-Bas)
- **Nom** : `comprehension-orale-speech`
- **Niveau tarifaire** : **Free F0** (gratuit, recommandé pour commencer)

Cliquez sur **Vérifier + créer**, puis **Créer**

### 3. Récupérer les clés API

1. Une fois la ressource créée, cliquez sur **Aller à la ressource**
2. Dans le menu à gauche, cliquez sur **Clés et point de terminaison**
3. Copiez :
   - **Clé 1** (ou Clé 2)
   - **Region**

### 4. Configurer le fichier `.env`

Ajoutez les variables dans votre `.env` :

```env
AZURE_SPEECH_KEY=votre_clé_ici
AZURE_SPEECH_REGION=francecentral
```

**Exemple complet** :
```env
# OpenAI
OPENAI_API_KEY=sk-proj-...

# Azure Speech TTS
AZURE_SPEECH_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
AZURE_SPEECH_REGION=francecentral
```

### 5. Installer les dépendances Python

```bash
# Avec le venv312 (recommandé)
.venv312/bin/pip install -r requirements.txt
```

Cela installera :
- `azure-cognitiveservices-speech` → Azure TTS
- `openai` → OpenAI GPT-4o
- `gtts` → Google TTS (fallback)
- `edge-tts` → Microsoft Edge TTS (alternative)
- `requests` → HTTP requests
- `python-dotenv` → Gestion des variables d'environnement

**⚠️ Important** : Utilisez `.venv312/bin/pip` et non `pip` directement, car `pip` seul peut ne pas être disponible.

### 6. Installer ffmpeg (pour la conversion MP3 - optionnel)

`ffmpeg` est utilisé pour convertir les fichiers WAV en MP3 (réduction de taille ~10x).

**macOS** :
```bash
brew install ffmpeg
```

**Linux (Ubuntu/Debian)** :
```bash
sudo apt-get install ffmpeg
```

**Windows** :
Téléchargez depuis [ffmpeg.org](https://ffmpeg.org/download.html)

**⚠️ Important** : Si ffmpeg ne fonctionne pas sur votre système (problème de sécurité macOS), utilisez `--format wav` :
```bash
# Génération en WAV (fonctionne toujours)
.venv312/bin/python md2mp3.py dialogue.md -l fr --format wav

# Tentative MP3 (fallback automatique vers WAV si ffmpeg échoue)
.venv312/bin/python md2mp3.py dialogue.md -l fr
```

Les fichiers WAV peuvent ensuite être convertis en MP3 avec un service en ligne gratuit comme [CloudConvert](https://cloudconvert.com/wav-to-mp3).

## 🔄 Quotas et limitations (Plan Free F0)

| Limite | Valeur |
|--------|--------|
| Requêtes/mois | 500,000 caractères |
| Requêtes/seconde | 20 |
| Durée max/demande | 10 minutes |

**Exemple** : Avec 500k caractères par mois, vous pouvez générer environ :
- 50 textes de 10,000 caractères
- 1667 textes de 300 caractères
- 2500 textes de 200 caractères

## 🧪 Tester l'installation

```bash
# Test simple
.venv312/bin/python md2mp3.py docs/mon_fichier/text.md -l fr

# Test avec voix forcée
.venv312/bin/python md2mp3.py docs/mon_fichier/text.md -l all --voix femme
```

## 🎤 Voix disponibles par langue

### Français (fr)
- **Féminin** : Denise, Eloïse, Vivienne, Brigitte, Celeste, Coralie, Jacqueline, Josephine, Yvette, Ariane (CH), Charline (BE)
- **Masculin** : Henri, Alain, Claude, Jerome, Maurice, Yves, Fabrice (CH), Gerard (BE)

### Anglais UK (eng)
- **Féminin** : Libby, Maisie, Sonia, Bella, Hollie, Olivia
- **Masculin** : Ryan, Thomas, Alfie, Elliot, Ethan, Noah, Oliver

### Anglais US (us)
- **Féminin** : Aria, Ava, Emma, Jenny, Michelle, Monica, Amber, Ana, Ashley, Cora, Elizabeth, Sara
- **Masculin** : Guy, Brian, Christopher, Eric, Jacob, Jason, Tony, Davis

### Espagnol (esp)
- **Féminin** : Elvira, Estrella, Verónica, Abril, Irene, Laia, Lia, Trisa
- **Masculin** : Alvaro, Arnau, Dario, Elias, Nil, Saul, Teo

### Hispanique (hisp)
- **Féminin** : Elena (AR), Marta (MX), Salome (CO), Beatriz, Carlota, Candela, Larissa, Marina, Nuria, Renata
- **Masculin** : Tomas (AR), Jorge (MX), Gonzalo (CO), Cecilio, Gerardo, Liberto, Luciano, Pelayo, Yago

### Néerlandais (nl)
- **Féminin** : Fenna, Colette, Dena (BE)
- **Masculin** : Maarten, Coen, Arnaud (BE)

### Coréen (co)
- **Féminin** : SunHi, YuJin, Hyunju, SoonBok, JiMin
- **Masculin** : InJoon, BongJin, GookMin, Hyunsu

## 💡 Astuces

1. **Pas de compte Microsoft** ? Créez-en un gratuitement sur [outlook.com](https://outlook.com)

2. **Erreur "Invalid API key"** ? Vérifiez que vous avez bien copié la clé complète

3. **Erreur "Invalid region"** ? Utilisez le format exact : `francecentral`, `westeurope`, etc.

4. **Tester la clé en ligne** :
   ```bash
   curl -X POST "https://francecentral.tts.speech.microsoft.com/cognitiveservices/v1" \
     -H "Ocp-Apim-Subscription-Key: votre_clé" \
     -H "Content-Type: application/ssml+xml" \
     -d '<speak version="1.0" xml:lang="fr-FR"><voice name="fr-FR-DeniseNeural">Bonjour</voice></speak>' \
     --output test.wav
   ```

## 🆘 Support

- **Problèmes Azure** : [Docs Azure Speech](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/)
- **Issues du script** : Vérifiez le fichier `.env` et les dépendances

## 📊 Coûts estimés

Plan **Free F0** : Gratuit jusqu'à 500k caractères/mois

Plan **Payant** (si vous dépassez) : ~$4 par 1M de caractères

**Conseil** : Restez sur le plan Free tant que possible (500k caractères = beaucoup de contenu!)
