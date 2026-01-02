# Persistance du niveau de langue

## Fonctionnalité

Le niveau de langue (A1, A2, B1, B2, C1, C2) est maintenant **automatiquement mémorisé** lors de la navigation entre les pages du site.

## Comportement

### Sauvegarde automatique

Le niveau est sauvegardé dans `localStorage` du navigateur dans les situations suivantes :

1. **Dans [search.html](site_langues/search.html)** : Quand vous sélectionnez un niveau dans le filtre
2. **Dans [player.html](site_langues/player.html)** : Quand vous consultez une ressource (le niveau de cette ressource est mémorisé)
3. **Dans [global_quiz.html](site_langues/global_quiz.html)** : Quand vous changez de niveau
4. **Dans [random_player.html](site_langues/random_player.html)** : Quand vous changez le filtre de niveau

### Restauration automatique

Le niveau est restauré automatiquement dans les situations suivantes :

1. **Dans [search.html](site_langues/search.html)** : Au chargement de la page, si aucun niveau n'est spécifié
2. **Dans [vocab.html](site_langues/vocab.html)** : Au chargement, si pas de paramètre `niveau` dans l'URL
3. **Dans [global_quiz.html](site_langues/global_quiz.html)** : Au chargement, si pas de paramètre `niveau` dans l'URL
4. **Dans [random_player.html](site_langues/random_player.html)** : Au chargement de la page

## Exemple d'utilisation

1. **Scénario typique** :
   - Vous allez sur [search.html](site_langues/search.html?lang=eng)
   - Vous sélectionnez "B1" dans le filtre
   - Le niveau B1 est sauvegardé
   - Vous cliquez sur "Quiz vocabulaire" → [global_quiz.html](site_langues/global_quiz.html) s'ouvre avec B1 pré-sélectionné
   - Vous revenez et cliquez sur "Vocabulaire" → [vocab.html](site_langues/vocab.html) affiche le vocabulaire B1
   - Vous consultez une ressource dans [player.html](site_langues/player.html) → Le niveau de cette ressource devient le nouveau niveau mémorisé

2. **Changement de niveau** :
   - Vous pouvez toujours changer le niveau à tout moment
   - Le nouveau choix écrase l'ancien et devient le niveau mémorisé

3. **Suppression** :
   - Si vous sélectionnez "Tous les niveaux" dans [search.html](site_langues/search.html), la mémorisation est effacée
   - Pour réinitialiser manuellement, ouvrez la console du navigateur et tapez : `localStorage.removeItem('selectedNiveau')`

## Implémentation technique

### Clé localStorage

```javascript
'selectedNiveau' // Stocke la valeur : 'A1', 'A2', 'B1', 'B2', 'C1', ou 'C2'
```

### Code JavaScript ajouté

Dans chaque fichier HTML, le code suivant a été ajouté :

**Sauvegarde** :
```javascript
// Lors du changement de niveau
if (niveau) {
    localStorage.setItem('selectedNiveau', niveau);
} else {
    localStorage.removeItem('selectedNiveau');
}
```

**Restauration** :
```javascript
// Au chargement de la page
const savedNiveau = localStorage.getItem('selectedNiveau');
if (savedNiveau) {
    // Appliquer le niveau sauvegardé
    document.getElementById('filter-niveau').value = savedNiveau;
}
```

## Fichiers modifiés

- [site_langues/search.html](site_langues/search.html) : Sauvegarde et restauration du niveau
- [site_langues/player.html](site_langues/player.html) : Sauvegarde du niveau de la ressource consultée
- [site_langues/vocab.html](site_langues/vocab.html) : Restauration du niveau si absent de l'URL
- [site_langues/global_quiz.html](site_langues/global_quiz.html) : Sauvegarde et restauration du niveau
- [site_langues/random_player.html](site_langues/random_player.html) : Sauvegarde et restauration du niveau

## Compatibilité

- ✅ Tous les navigateurs modernes (Chrome, Firefox, Safari, Edge)
- ✅ Fonctionne en mode privé/incognito (mais données effacées à la fermeture)
- ✅ Compatible mobile (iOS/Android)
- ✅ Pas de dépendance externe (utilise l'API localStorage native)

## Limitations

- Les données localStorage sont liées au domaine
- Si vous changez de navigateur, le niveau n'est pas synchronisé
- En mode navigation privée, les données sont effacées à la fermeture de la session
- Limite de stockage : ~5-10MB (largement suffisant pour une simple valeur de niveau)
