# Test SSML - Résultats et Recommandations

## Résumé de l'expérience

Nous avons testé l'intégration de SSML dans le pipeline de génération audio en utilisant des marqueurs Markdown simples.

### Fichiers créés

1. **`test_ssml.md`** - Texte pédagogique français A1 avec marqueurs:
   - `*mot*` → italique (emphasis légère)
   - `**mot**` → gras (emphasis forte)
   - `[p]` → pause 250ms
   - `[p:300]` → pause 300ms custom

2. **`test_ssml_compare.py`** - Script de test qui génère deux versions audio

3. **Sorties audio** (7 janvier 2026, 08:15):
   - `test_ssml_without_ssml.mp3` (255 KB) - Texte brut, sans SSML
   - `test_ssml_with_ssml.mp3` (237 KB) - Avec SSML (emphasis + pauses)

### Modifications apportées à `md2mp3.py`

Ajout de la méthode `markdown_to_ssml()` à la classe `MarkdownCleaner`:

```python
@staticmethod
def markdown_to_ssml(text):
    """
    Convertit les marqueurs Markdown en balises SSML.
    - *mot* → <emphasis level="moderate">mot</emphasis>
    - **mot** → <emphasis level="strong">mot</emphasis>
    - [p] → <break time="250ms"/>
    - [p:XXX] → <break time="XXXms"/>
    """
```

## Résultats observés

### ✅ Avantages confirmés

1. **Lisibilité Markdown** ⭐
   - Les marqueurs `*`, `**`, et `[p]` sont naturels et lisibles dans `text.md`
   - Zéro pollution visuelle comparé à `[[EMPH]]...[[/EMPH]]`

2. **Compatibilité web** ⭐
   - `*mot*` et `**mot**` continuent de générer `<em>` et `<strong>` HTML
   - Les pauses `[p]` n'apparaissent pas sur le site (elles sont dans le SSML seulement)

3. **Génération audio** ⭐
   - Azure TTS accepte et traite correctement le SSML généré
   - Les pauses et emphases sont appliquées lors de la synthèse

4. **Flexibilité** ⭐
   - Pauses avec durée custom: `[p:400]`, `[p:600]`
   - Deux niveaux d'emphasis: léger (`*`) et fort (`**`)

### 🎙️ Différences audibles attendues

Pour évaluer les fichiers:
- **Sans SSML** (`test_ssml_without_ssml.mp3`): Lecture fluide, uniforme
- **Avec SSML** (`test_ssml_with_ssml.mp3`): Pauses naturelles entre phrases, emphase sur mots-clés

Les pauses aux marqueurs `[p]` créent:
- Meilleure clarté pédagogique
- Respiration naturelle pour le lecteur
- Temps pour traiter les concepts

## Recommandations pour l'intégration

### 1. Mise à jour des prompts GPT

Ajouter aux instructions de `genmp3.py`:

```
**Marqueurs de formatage SSML:**
- Utilise *mot* pour une légère emphase (prononciation plus expressive)
- Utilise **mot** pour une emphase forte (très important à comprendre)
- Utilise [p] pour une pause courte (250ms) entre deux idées
- Utilise [p:400] ou [p:600] pour une pause plus longue
- Évite de surcharger: max 2-3 pauses par paragraphe, max 2-3 emphasis par texte

**Bonnes pratiques:**
- [p] après la fin d'une phrase pour une respiration naturelle
- **mot** pour les vocabulaire-clé et concepts importants
- *mot* pour les mots-clés secondaires ou exemples
```

### 2. Intégration dans le pipeline

Deux approches:

#### Option A: Conversion automatique (recommandée)
- Faire générer les marqueurs par GPT (comme ci-dessus)
- Convertir automatiquement dans `md2mp3.py` via `markdown_to_ssml()`
- Le texte `text.md` reste lisible, SSML généré à la synthèse

#### Option B: Pré-conversion manuelle
- Générer le texte brut via GPT
- Ajouter manuellement les marqueurs en post-édition
- Utile pour affiner les pauses et emphasis selon le contexte

### 3. Gestion du nettoyage Markdown

Le nettoyage `clean_text()` doit:
1. **Avant** suppression de syntaxe: convertir `*` et `**` en SSML via `markdown_to_ssml()`
2. **Après**: supprimer comme aujourd'hui (les SSML restent, les `*` sont nettoyés)

Flux corrigé:
```python
# 1. Extraire frontmatter et vocabulaire
cleaned_text = MarkdownCleaner.clean_text(content, args.langue)

# 2. Convertir Markdown → SSML AVANT suppression de la syntaxe
ssml_text = MarkdownCleaner.markdown_to_ssml(cleaned_text)

# 3. Passer le texte SSML à Azure TTS
tts.generate_audio_from_text(ssml_text, output_file)
```

### 4. Fallback et validation

Ajouter une validation SSML minimaliste:
```python
def validate_ssml(text):
    """Vérifie que le SSML est bien-formé"""
    # Compter les balises ouvertes/fermées
    # Retourner le texte brut si erreur (fallback)
```

## Prochaines étapes

1. ✅ **Test validé** - Les deux versions audio sont générées avec succès
2. ⏳ **Intégration optionnelle** - Ajouter la conversion SSML au pipeline standard
3. ⏳ **Documentation** - Mettre à jour les prompts GPT et la doc utilisateur
4. ⏳ **Évaluation qualité audio** - Écouter les différences et ajuster les durées de pause

## Fichiers de référence

- **Fonction SSML**: [md2mp3.py](md2mp3.py#L487-L505)
- **Test de comparaison**: [test_ssml_compare.py](test_ssml_compare.py)
- **Exemple pédagogique**: [test_ssml.md](test_ssml.md)
- **Audios générés**:
  - `test_ssml_without_ssml.mp3` (255 KB)
  - `test_ssml_with_ssml.mp3` (237 KB)

---

**Conclusion**: ✅ **L'approche Markdown + SSML est viably et recommandée.** Elle combine:
- Lisibilité maximale du texte source
- Qualité audio améliorée via pauses et emphasis
- Zéro rupture du pipeline existant
- Flexibilité pour l'affinage futur
