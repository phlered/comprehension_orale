# Google Cloud Text-to-Speech vs Azure Speech Service

## Vue d'ensemble

Ce projet propose maintenant deux versions parallèles pour générer des ressources audio multilingues :

1. **Version Azure** (originale) - `genmp3.py` → `md2mp3.py`
2. **Version Google Cloud** (nouvelle) - `genmp3_google.py` → `md2mp3_google.py`

Cela permet de **comparer la qualité audio, le coût et les performances** entre les deux services TTS leaders.

---

## Installation

### Dépendances Azure (déjà installées)

```bash
pip install azure-cognitiveservices-speech
```

Environnement: `AZURE_SPEECH_KEY` et `AZURE_SPEECH_REGION`

### Dépendances Google Cloud (nouvelle)

```bash
pip install google-cloud-texttospeech
```

Authentification: `GOOGLE_APPLICATION_CREDENTIALS` pointant vers un fichier JSON de credentials

---

## Configuration

### Azure

```bash
# .env
OPENAI_API_KEY=sk-...
AZURE_SPEECH_KEY=your-key-here
AZURE_SPEECH_REGION=westeurope
```

### Google Cloud

```bash
# .env
OPENAI_API_KEY=sk-...

# Bash
export GOOGLE_APPLICATION_CREDENTIALS=/chemin/vers/credentials.json
```

**Obtenir les credentials Google Cloud:**
1. Créer un projet Google Cloud
2. Activer l'API Text-to-Speech
3. Créer une clé de service (Account)
4. Télécharger le JSON et mettre le chemin dans `GOOGLE_APPLICATION_CREDENTIALS`

---

## Utilisation

### Générer une ressource avec Azure

```bash
python genmp3.py -l fr -p "Commander une pizza" --niveau A1
python genmp3.py -l eng -p "Climate change" --longueur 200 --niveau B2 -g femme
```

### Générer une ressource avec Google Cloud

```bash
# Assurez-vous que GOOGLE_APPLICATION_CREDENTIALS est défini
python genmp3_google.py -l fr -p "Commander une pizza" --niveau A1
python genmp3_google.py -l eng -p "Climate change" --longueur 200 --niveau B2 -g femme
```

### Convertir un Markdown existant

**Avec Azure:**
```bash
python md2mp3.py text.md -l fr --voix femme --vitesse 0.9
```

**Avec Google Cloud:**
```bash
python md2mp3_google.py text.md -l fr --voix femme --vitesse 0.9
```

---

## Comparaison détaillée

### Langues supportées

#### Azure
- ✅ Français (multiples variantes: FR, CH, BE)
- ✅ Anglais (GB, US)
- ✅ Allemand (DE, CH, AT)
- ✅ Espagnol (ES, MX, AR, CO)
- ✅ Néerlandais
- ✅ Italien
- ✅ Coréen
- ✅ Portugais, Polonais, Russe, Arabe, etc. (95+ voix)

#### Google Cloud
- ✅ Français
- ✅ Anglais (GB, US)
- ✅ Allemand
- ✅ Espagnol (ES, MX)
- ✅ Néerlandais
- ✅ Italien
- ✅ Coréen
- ✅ Japonais, Mandarin, Russe, Arabe, etc. (100+ voix)

**Verdict:** Google Cloud a **légèrement plus** de langues, mais Azure couvre tous les besoins du projet.

---

### Qualité vocale

#### Azure
- **Technologie:** Voix neurales (Neural Voices) de haute qualité
- **Variété:** 95+ voix distinctes avec bon contrôle prosodique
- **Naturalité:** Très naturelle, avec bonne émulation de l'accent
- **Variantes régionales:** Excellentes (suisse, belge, mexicain, etc.)
- **Performance prosodique:** Bonne gestion des pauses, intonations, vitesse

#### Google Cloud
- **Technologie:** Neural2 (dernière générations) et Wavenet (plus anciennes)
- **Variété:** 100+ voix disponibles
- **Naturalité:** **Légèrement supérieure** à Azure (plus humaine)
- **Variantes régionales:** Bonnes (Mexique pour l'espagnol)
- **Performance prosodique:** Excellente, très naturelle même à vitesses extrêmes

**Verdict:** **Google Cloud gagne légèrement** en naturalité vocale, particulièrement pour les textes longs.

---

### Vitesse et latence

#### Azure
- **Latence:** ~500ms à 2s par requête (selon la région)
- **Quota:** 20 requêtes/secondes (Standard)
- **Chunking:** Inclus (gère les textes >2000 chars)
- **Temps total pour 150 mots:** ~2-3 secondes

#### Google Cloud
- **Latence:** ~200ms à 1s par requête (plus rapide)
- **Quota:** 5000 caractères/secondes (très généreux)
- **Chunking:** Inclus (gère les textes >3000 chars)
- **Temps total pour 150 mots:** ~1-2 secondes

**Verdict:** **Google Cloud est plus rapide** et offre un quota plus généreux.

---

### Coût

#### Azure (à partir d'octobre 2024)
- **Standard:** €10-15 par 1M caractères (~67k ressources à 150 mots)
- **Neural:** €15-20 par 1M caractères
- **Engagement annuel:** Remise possible

#### Google Cloud
- **Neural2:** $0.000016 par caractère (~$16 par 1M caractères, légèrement plus cher)
- **Wavenet (gratuit):** Ancienne génération, moins bonne qualité
- **Essai gratuit:** $300 de crédits

**Verdict:** **Azure légèrement moins cher**, mais la différence est minime (<50%).

---

### Résilience et disponibilité

#### Azure
- **Uptime:** 99.95%+
- **Retry:** Implémenté avec backoff exponentiel
- **Régions:** Multiple (westeurope, eastus, etc.)
- **Fallback:** Chunking avec ffmpeg ou pydub

#### Google Cloud
- **Uptime:** 99.99%
- **Retry:** Implémenté avec backoff exponentiel
- **Régions:** Multiple (us-central, europe-west1, etc.)
- **Fallback:** Chunking avec ffmpeg

**Verdict:** **Google Cloud légèrement plus fiable** sur le papier, mais les deux sont excellentes en pratique.

---

### Facilité d'intégration

#### Azure
- ✅ SDK Python officiel très mature
- ✅ Configuration simple (clé API + région)
- ✅ Bien documenté
- ⚠️ Gestion des voix un peu complexe (IDs spécifiques)

#### Google Cloud
- ✅ SDK Python officiel (google-cloud-texttospeech)
- ✅ API REST aussi disponible
- ✅ Bien documenté
- ✅ Authentification plus standard (credentials JSON)
- ⚠️ Quotas à surveiller

**Verdict:** Les deux sont faciles, **Google Cloud légèrement plus standard**.

---

## Cas d'usage recommandés

### Utiliser Azure si:
- ✅ Vous avez déjà une clé Azure
- ✅ Vous générez peu de ressources (<10k/mois)
- ✅ Vous avez besoin des variantes régionales (suisse, belge, etc.)
- ✅ Vous préférez une intégration établie

### Utiliser Google Cloud si:
- ✅ Vous produisez beaucoup de contenu (>10k ressources/mois)
- ✅ Vous préférez une qualité vocale naturelle
- ✅ Vous avez besoin de performances rapides
- ✅ Vous voulez bénéficier du crédit gratuit initial
- ✅ Vous préférez une authentification standard (OAuth2)

### Utiliser les DEUX si:
- ✅ Vous voulez **comparer** la qualité audio pour votre audience
- ✅ Vous voulez **garantir la disponibilité** (failover)
- ✅ Vous voulez **optimiser le coût** (utiliser le plus avantageux selon le moment)
- ✅ Vous faites de la **recherche** sur la qualité TTS

---

## Structure des fichiers

### Version Azure
```
genmp3.py          # Génération complète (texte + audio Azure)
md2mp3.py          # Conversion Markdown → MP3 (Azure TTS)
```

### Version Google Cloud
```
genmp3_google.py   # Génération complète (texte + audio Google)
md2mp3_google.py   # Conversion Markdown → MP3 (Google Cloud TTS)
```

### Fichiers partagés
```
requirements.txt              # Dépendances (inclut google-cloud-texttospeech)
voices_config.py              # Configuration des voix (utilisé par Azure)
.env                          # Variables d'environnement
```

---

## Tests et validation

### Tester Azure
```bash
python genmp3.py -l fr -p "Test Azure" --niveau A1
```

### Tester Google Cloud
```bash
python genmp3_google.py -l fr -p "Test Google" --niveau A1
```

### Comparer les deux en parallèle
```bash
# Terminal 1
python genmp3.py -l fr -p "Sujet à tester" --niveau B1

# Terminal 2
python genmp3_google.py -l fr -p "Sujet à tester" --niveau B1

# Puis comparer les fichiers audio.mp3 générés
```

---

## Limitations et workarounds

### Azure
- Les voix spécifiques (prénoms) ne fonctionnent que pour la langue active
- Timeout possible sur textes très longs (>5000 chars) → utilise le chunking

### Google Cloud
- Limite de 32k caractères par appel API → chunking automatique
- Besoin d'authentification via JSON (fichier credentials.json)
- Les voix Neural2 sont plus naturelles que Wavenet

---

## Contribution et amélioration

Vous pouvez:
1. **Améliorer la détection de dialogue** dans `md2mp3_google.py`
2. **Ajouter un benchmark de coût** (script Python pour comparer les prix)
3. **Créer un wrapper unifiée** (`genmp3_auto.py`) qui choisit le meilleur service
4. **Ajouter le support d'autres langues** si Google/Azure en ajoute

---

## Références

- [Azure Speech Service Documentation](https://learn.microsoft.com/en-us/azure/cognitive-services/speech-service/)
- [Google Cloud Text-to-Speech Documentation](https://cloud.google.com/text-to-speech/docs)
- [Comparaison TTS indépendante](https://en.wikipedia.org/wiki/Speech_synthesis#Neural_speech_synthesis)

---

**Dernière mise à jour:** 2 janvier 2026
