# 🔄 Migration vers OpenAI - Guide Rapide

L'application a été mise à jour pour utiliser **OpenAI (GPT-4o)** au lieu d'Anthropic Claude.

## ✅ Changements effectués

1. **API** : Anthropic → OpenAI
2. **Modèle** : Claude 3.5 Sonnet → GPT-4o
3. **Variable d'environnement** : `ANTHROPIC_API_KEY` → `OPENAI_API_KEY`

## 🚀 Configuration rapide

### 1. Installer OpenAI (déjà fait)
```bash
pip3 install --user openai
```

### 2. Obtenir votre clé API OpenAI

1. Allez sur https://platform.openai.com/
2. Connectez-vous avec votre compte (celui avec 10$ de crédits)
3. Allez dans **API Keys** : https://platform.openai.com/api-keys
4. Cliquez sur **"Create new secret key"**
5. Copiez la clé (elle commence par `sk-proj-` ou `sk-`)

### 3. Configurer le fichier .env

Éditez le fichier `.env` qui a déjà été créé :

```bash
nano .env
```

Remplacez cette ligne :
```
OPENAI_API_KEY=sk-votre_clé_openai_ici
```

Par votre vraie clé :
```
OPENAI_API_KEY=sk-proj-ABC123votre_vraie_clé_ici
```

Sauvegardez (Ctrl+O, Enter, Ctrl+X)

### 4. Lancer l'application

```bash
python3 app_comprehension_orale.py
```

## 💰 Avantages d'OpenAI

✅ **Vous avez déjà 10$ de crédits** (vs 5$ chez Anthropic)  
✅ **Moins cher** : ~0,002$ par exercice (vs 0,003-0,005$)  
✅ **Plus d'exercices** : ~2500-3000 avec vos 10$ (vs ~1000-1500)  
✅ **GPT-4o** : Excellent pour l'allemand, très naturel  
✅ **API stable** : Très fiable et rapide  

## 🎯 Coûts détaillés GPT-4o

- **Génération vocabulaire** (15 mots) : ~0,0003$
- **Génération texte** (300 mots) : ~0,0015-0,002$
- **Total par exercice** : ~0,002-0,0025$ (moins de 1 centime !)

Avec **10$**, vous pouvez créer environ **2500-3000 exercices complets** ! 🎉

## ✅ Test rapide

Pour vérifier que tout fonctionne :

```bash
python3 app_comprehension_orale.py
```

1. Entrez un thème (ex: "la météo")
2. Cliquez sur "🤖 Générer le vocabulaire (IA)"
3. Si ça fonctionne → tout est OK ! 🎉
4. Si erreur → vérifiez votre clé API dans `.env`

## 🔍 Vérifier votre compte OpenAI

- Allez sur https://platform.openai.com/usage
- Vous verrez vos crédits restants (devrait afficher ~10$)
- Après quelques générations, vous verrez la consommation

## 📝 Notes importantes

- La clé API **ne doit jamais être partagée** publiquement
- Le fichier `.env` est **ignoré par git** (sécurité)
- Gardez votre clé secrète et sécurisée

## 🆘 Problèmes ?

### "Clé API non trouvée"
→ Vérifiez que `.env` contient `OPENAI_API_KEY=sk-...`

### "Invalid API Key"
→ La clé est incorrecte, regénérez-en une sur OpenAI

### "Insufficient credits"
→ Vos crédits sont épuisés, ajoutez un moyen de paiement

---

**C'est tout ! Votre application est prête à utiliser OpenAI ! 🚀**
