# Test de la fonctionnalité de traduction à la demande

## Fonctionnalité implémentée

✅ **Traduction instantanée de tous les mots au clic/touch**

### Comment ça fonctionne

1. **Wrapping automatique** : Tous les mots du texte sont automatiquement enveloppés dans des `<span class="clickable-word">` au chargement
2. **Traduction à la demande** : Au clic sur un mot, l'API MyMemory traduit le mot vers le français
3. **Cache localStorage** : Les traductions sont mises en cache pour éviter les requêtes répétées
4. **Tooltip au-dessus** : La traduction apparaît dans une bulle au-dessus du mot (même style que le vocabulaire)

### API utilisée

**MyMemory Translation API**
- URL : `https://api.mymemory.translated.net/get`
- Gratuit, sans clé API requise
- Limite : ~1000 requêtes/jour par IP
- Support de 50+ langues

### Comportements

1. **Mots du vocabulaire** (surlignés en jaune) :
   - Traduction instantanée (déjà dans les métadonnées)
   - Priorité sur les mots cliquables

2. **Tous les autres mots** :
   - Affichage d'un loader "⏳ Traduction..."
   - Appel API MyMemory
   - Affichage de la traduction
   - Cache pour 2ème clic instantané

3. **Détection automatique langue source** :
   - Néerlandais → `nl`
   - Allemand → `de`
   - Anglais → `en`
   - Espagnol → `es`
   - Italien → `it`
   - Coréen → `ko`

### Tests à effectuer

1. Ouvrir une ressource : http://localhost:8000/player.html?id=XXX
2. Afficher le texte
3. Cliquer sur un mot du vocabulaire → Traduction instantanée
4. Cliquer sur un mot normal → Loader puis traduction
5. Recliquer sur le même mot → Traduction instantanée (cache)

### Limitations

- **API gratuite** : Si trop de requêtes, peut devenir lente
- **Traduction mot à mot** : Pas de contexte (peut être imprécis)
- **Requiert connexion internet** : Pas de traduction hors ligne

### Alternatives possibles

Si l'API MyMemory devient problématique :

1. **LibreTranslate** (auto-hébergé)
2. **Google Translate API** (payant)
3. **DeepL API** (meilleure qualité, 500k chars/mois gratuit)
4. **Pré-traduction** : Générer toutes les traductions lors de la création (coûteux)

### Fichiers modifiés

- [site_langues/player.html](site_langues/player.html) :
  - Styles pour `.clickable-word`
  - Fonction `makeWordsClickable()` (wrapping)
  - Fonction `translateWord()` (API call + cache)
  - Fonction `getSourceLanguage()` (mapping)
  - Handler de clic étendu

## Tests réalisés

- [ ] Clic sur mot vocabulaire → OK
- [ ] Clic sur mot normal → Traduction via API
- [ ] Reclic sur mot → Cache OK
- [ ] Mobile/tactile → Tooltip correct
- [ ] Plusieurs langues → Détection OK

## Date d'implémentation

27 décembre 2025
