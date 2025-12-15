# 🎤 Guide Audio - edge-tts vs gTTS

## 📊 État actuel

Le script utilise maintenant un **système hybride** :
1. **Tentative edge-tts** (meilleure qualité)
2. **Fallback gTTS** si edge-tts échoue

---

## 🔍 Résultats des tests

### edge-tts (Microsoft)
- **Status actuel** : ❌ Ne fonctionne pas
- **Erreur** : "No audio was received"
- **Qualité** : Excellente (quand ça marche)
- **Voix** : Multiples (homme/femme)
- **Pauses** : Aucune, lecture fluide

### gTTS (Google)
- **Status actuel** : ✅ Fonctionne
- **Qualité** : Bonne
- **Voix** : Une seule par langue
- **Pauses** : ⚠️ Parfois présentes dans les phrases longues

---

## ⚠️ Problème des pauses avec gTTS

### Cause
gTTS découpe le texte en segments pour la génération audio. Parfois, ce découpage crée des pauses artificielles au milieu des phrases, surtout en allemand.

### Exemple
```
"Die Jahreszeiten spielen [PAUSE] eine wichtige Rolle in unserem Leben."
```

---

## 🔧 Solutions possibles

### Option 1: Pré-traitement du texte ✅ (Recommandé)

Découper le texte en phrases courtes avant de le passer à gTTS :

```python
def split_into_sentences(text):
    """Découpe le texte en phrases"""
    # Pour l'allemand, découper sur . ! ?
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

def generate_audio_smooth(text, lang_code, output_file):
    """Génère l'audio phrase par phrase"""
    sentences = split_into_sentences(text)
    
    # Créer un fichier audio pour chaque phrase
    temp_files = []
    for i, sentence in enumerate(sentences):
        temp_file = f"temp_{i}.mp3"
        tts = gTTS(text=sentence, lang=lang_code, slow=False)
        tts.save(temp_file)
        temp_files.append(temp_file)
    
    # Concaténer les fichiers (nécessite pydub)
    from pydub import AudioSegment
    combined = AudioSegment.empty()
    for temp_file in temp_files:
        combined += AudioSegment.from_mp3(temp_file)
        os.remove(temp_file)
    
    combined.export(output_file, format="mp3")
```

### Option 2: Utiliser pyttsx3 (Local) 🔊

Synthèse vocale locale, pas de connexion internet requise :

```bash
pip install pyttsx3
```

**Avantages** :
- ✅ Pas de pauses artificielles
- ✅ Fonctionne hors ligne
- ✅ Rapide

**Inconvénients** :
- ❌ Voix robotiques
- ❌ Qualité inférieure à gTTS/edge-tts
- ❌ Nécessite des dépendances système (espeak)

### Option 3: Réessayer edge-tts plus tard 🔄

Le problème edge-tts peut être temporaire :
- Problème de connexion réseau
- Service Microsoft temporairement indisponible
- Limitation de taux (rate limiting)

**À tester** :
1. Vérifier votre connexion internet
2. Réessayer dans quelques heures
3. Vérifier si un VPN interfère

### Option 4: API premium payante 💰

Services TTS professionnels sans pauses :
- **Google Cloud TTS** (payant, meilleure qualité que gTTS)
- **Amazon Polly** (payant, excellente qualité)
- **Microsoft Azure Speech** (payant, même voix qu'edge-tts)

---

## 🎯 Recommandations

### Court terme (maintenant)
✅ **Utiliser le système hybride actuel**
- edge-tts essayé automatiquement
- gTTS en fallback
- Accepter les pauses occasionnelles de gTTS

### Moyen terme (si pauses gênantes)
✅ **Implémenter le pré-traitement du texte** (Option 1)
- Découper en phrases
- Générer phrase par phrase
- Concaténer (nécessite pydub)

### Long terme (si qualité critique)
💰 **Passer à une API premium**
- Google Cloud TTS
- Amazon Polly
- Azure Speech

---

## 📝 Configuration actuelle

Le script `app.py` utilise maintenant :

```python
class AudioGenerator:
    """Génère l'audio avec edge-tts (priorité) ou gTTS (fallback)"""
    
    @staticmethod
    def generate(text, langue_code, voix, fichier_sortie):
        # 1. Essayer edge-tts
        # 2. Si échec → gTTS
        # 3. Si échec → fichier vide
```

**Avantages** :
- ✅ Automatique
- ✅ Robuste (plusieurs fallbacks)
- ✅ Meilleure qualité quand edge-tts fonctionne
- ✅ Toujours un fichier audio généré

---

## 🧪 Tester edge-tts manuellement

Pour vérifier si edge-tts fonctionne sur votre système :

```bash
cd /Users/ph/Dropbox/Philippe/Projets/comprehension_orale
./.venv312/bin/python test_comparison.py
```

Résultat attendu :
- ❌ edge-tts échoue → Continuer avec gTTS
- ✅ edge-tts fonctionne → Activer uniquement edge-tts

---

## 💡 Pourquoi edge-tts ne fonctionne pas ?

Causes possibles :
1. **Connexion réseau** : Vérifiez votre internet
2. **Firewall/VPN** : Peut bloquer l'accès au service Microsoft
3. **Rate limiting** : Trop de requêtes en peu de temps
4. **Service indisponible** : Microsoft a des problèmes temporaires
5. **Version incompatible** : Mise à jour edge-tts nécessaire

**À tester** :
```bash
# Mettre à jour edge-tts
pip install --upgrade edge-tts

# Vérifier la connexion
curl -I https://speech.platform.bing.com
```

---

## ✅ Conclusion

**Situation actuelle** :
- edge-tts ne fonctionne pas sur votre système
- gTTS fonctionne mais avec des pauses occasionnelles
- Le système hybride garantit toujours un fichier audio

**Options** :
1. ✅ **Accepter les pauses** (le plus simple)
2. ✅ **Implémenter le pré-traitement** (améliore gTTS)
3. 🔄 **Réessayer edge-tts** (peut marcher plus tard)
4. 💰 **API premium** (si budget disponible)

---

**Date** : 2025-12-10  
**Status** : Système hybride fonctionnel avec gTTS en fallback
