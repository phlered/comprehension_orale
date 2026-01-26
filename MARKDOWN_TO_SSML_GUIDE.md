# Guide Markdown → SSML

## Vue d'ensemble

Lors de la génération de textes pédagogiques (via `genmp3.py`), vous pouvez utiliser des marqueurs Markdown simples pour améliorer la qualité audio. Ces marqueurs sont convertis automatiquement en SSML (Speech Synthesis Markup Language) pour Azure Text-to-Speech.

## Syntaxe

### Emphasis (emphase vocale)

| Marqueur | Sémantique | SSML | Effet audio |
|----------|-----------|------|------------|
| `*mot*` | Italique léger | `<emphasis level="moderate">mot</emphasis>` | Prononciation plus expressive, légère |
| `**mot**` | Gras fort | `<emphasis level="strong">mot</emphasis>` | Prononciation très expressive, marquée |

**Exemple Markdown:**
```markdown
Je suis à l'école tous les jours. C'est très *important* pour ma **vie quotidienne**.
```

**Résultat audio:**
- "important" = prononcé avec légère emphase
- "vie quotidienne" = prononcé avec emphase marquée

### Pauses (breaks)

| Marqueur | Durée | SSML | Effet |
|----------|-------|------|-------|
| `[p]` | 250ms | `<break time="250ms"/>` | Pause courte, respiration naturelle |
| `[p:300]` | 300ms custom | `<break time="300ms"/>` | Pause courte personnalisée |
| `[p:400]` | 400ms custom | `<break time="400ms"/>` | Pause moyenne |
| `[p:600]` | 600ms custom | `<break time="600ms"/>` | Pause longue |

**Exemple Markdown:**
```markdown
Il y a trois concepts importants. [p:400] Concept un. [p] Concept deux. [p] Et concept trois.
```

**Résultat audio:**
- Pause de 400ms après la phrase d'introduction
- Pause de 250ms entre chaque concept pour laisser le temps de digérer

## Bonnes pratiques

### ✅ À faire

```markdown
**Vocabulaire clé** et *mots importants* sont marqués. [p:300]

Utilise [p] après une phrase complète pour une respiration naturelle.
Ajoute **emphase** sur les concepts à retenir.
```

- Max **3 emphasis** par paragraphe
- Max **3 pauses** par paragraphe
- Pauses après **ponctuation finale** (., !, ?)
- Emphasis sur **mots-clés pédagogiques**

### ❌ À éviter

```markdown
*Chaque* **mot** *est* **marqué** - trop d'emphasis!

Trop [p] de [p] pauses [p] tue [p] le [p] rythme.

[p] Pause en début de phrase - contre-intuitif.
```

- Surcharge d'emphasis (perte d'effet)
- Trop de pauses (lecture saccadée)
- Pauses en début de phrase

## Cas d'usage

### Texte A1 (simple)

```markdown
Je m'appelle **Marie**. [p:300] 

J'habite en France. C'est très *agréable*. [p]

Le matin, je vais à l'**école**. [p:250]
```

### Texte B1 (intermédiaire)

```markdown
Les **changements climatiques** sont importants. [p:400]

Il y a deux raisons principales. 
Première raison : *la température augmente*. [p]
Deuxième raison : *les événements extrêmes s'intensifient*. [p:300]
```

### Texte C2 (avancé)

```markdown
**D'un point de vue académique**, l'analyse révèle des corrélations significatives. [p:300]

Les données démontrent que **trois facteurs prépondérants** influencent le phénomène. [p:400]

Premièrement, *l'infrastructure institutionnelle*. [p] Deuxièmement, *les dynamiques socio-économiques*. [p] Troisièmement, *les paramètres environnementaux*. [p:300]
```

## Restriction: pas de nesting

Les marqueurs **ne se chevauchent pas**:

```markdown
❌ Incorrect: *Ce n'est **pas** bon*
✅ Correct: *Ce n'est pas* bon, **mais** utile.
```

## Affichage sur le site web

- Les pauses `[p]` disparaissent complètement (SSML seulement)
- Les emphasis `*` et `**` deviennent `<em>` et `<strong>` en HTML
- Aucun artefact visuel sur le site

## Prompt GPT recommandé

Si vous utilisez `genmp3.py` avec un prompt personnalisé, incluez:

```
Utilise *mot* pour une légère emphase et **mot** pour une emphase forte.
Ajoute [p] pour une pause de 250ms entre les phrases principales, [p:400] pour une pause plus longue.
Évite de surcharger : max 3 emphasis et 3 pauses par paragraphe.
```

## Troubleshooting

### "Les pauses n'apparaissent pas"
→ Vérifiez la syntaxe: `[p]` (pas d'espace), `[p:400]` (nombre uniquement).

### "Emphasis trop fort/faible"
→ Utilisez `*mot*` pour léger, `**mot**` pour fort. Azure n'offre que ces deux niveaux.

### "SSML invalide"
→ Si SSML est mal-formé, Azure génère sans emphasis (fallback automatique). Vérifiez la parenthèse des balises.

## Fichiers de référence

- **Implémentation**: [md2mp3.py#L487-L505](md2mp3.py) (fonction `markdown_to_ssml`)
- **Test d'exemple**: [test_ssml.md](test_ssml.md)
- **Résultats test**: [SSML_TEST_RESULTS.md](SSML_TEST_RESULTS.md)

---

**Version**: 1.0  
**Testé**: 7 janvier 2026  
**Status**: ✅ Production-ready (option)
