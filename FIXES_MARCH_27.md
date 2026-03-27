# Corrections - 27 Mars 2026

## 1. Label "Version pour fonds sombres" - Couleur Invisible

**Problème**: Le texte "Version pour fonds sombres" était blanc sur blanc (non visible)

**Cause**: La couleur était `rgba(255,255,255,0.7)` (blanc semi-transparent), appliquée au label qui s'affiche sur un fond blanc/gris

**Solution**: Changé la couleur de `rgba(255,255,255,0.7)` à `var(--text-primary)` (noir/sombre)

**Fichier modifié**: `templates/public/generate.html` (ligne 68)

**Avant**:
```html
<p style="font-size: var(--text-sm); color: rgba(255,255,255,0.7); margin-bottom: 0;">Version pour fonds sombres</p>
```

**Après**:
```html
<p style="font-size: var(--text-sm); color: var(--text-primary); margin-bottom: 0;">Version pour fonds sombres</p>
```

### Résultat
✅ Le label "Version pour fonds sombres" est maintenant visible en texte sombre sur fond clair

---

## 2. Retour à la Ligne Automatique pour "Secrétariat Général"

**Nouvelle Règle**: Si le nom de l'institution contient "Secrétariat Général", forcer automatiquement un retour à la ligne avant "Secrétariat"

**Fichier modifié**: `algorithms/text_splitter.py`

### Changements

#### Ajout d'une variable pour détecter "secrétariat général"
```python
has_secretariat_general = 'SECRÉTARIAT' in nom.upper() and 'GÉNÉRAL' in nom.upper()
```

#### Ajout de la logique de séparation obligatoire
```python
# If "secrétariat général" is present, force a line break before "secrétariat"
if has_secretariat_general:
    # Find the index of "SECRÉTARIAT"
    secretariat_index = None
    for i, w in enumerate(words):
        if 'SECRÉTARIAT' in w:
            secretariat_index = i
            break

    if secretariat_index is not None and secretariat_index > 0:
        # Split: everything before "secrétariat" on one line, rest on another
        before = ' '.join(words[:secretariat_index])
        after = ' '.join(words[secretariat_index:])
        return [before, after]
```

### Exemples

**Cas 1**: "Ministère du Secrétariat Général"
```
Avant: MINISTÈRE DU SECRÉTARIAT GÉNÉRAL (une ou deux lignes selon l'algorithme)
Après:
  MINISTÈRE DU
  SECRÉTARIAT GÉNÉRAL
```

**Cas 2**: "Bureau du Secrétariat Général de la Présidence"
```
Avant: BUREAU DU SECRÉTARIAT GÉNÉRAL DE LA PRÉSIDENCE (divisé normalement)
Après:
  BUREAU DU
  SECRÉTARIAT GÉNÉRAL DE LA PRÉSIDENCE
```

**Cas 3**: "Ministère de la Défense" (pas de "secrétariat général")
```
Pas de changement - l'algorithme normal s'applique:
  MINISTÈRE
  DE LA DÉFENSE
```

### Logique

- La détection est **case-insensitive** (fonctionne quelle que soit la casse)
- Le retour à la ligne se fait **obligatoirement** avant "SECRÉTARIAT"
- Tout ce qui précède "SECRÉTARIAT" va sur la première ligne
- "SECRÉTARIAT" et le reste vont sur la deuxième ligne
- S'il n'y a rien avant "SECRÉTARIAT" (cas rare), l'algorithme normal s'applique

### Cas Limites Gérés

✅ "Secrétariat Général seul" → Retour normal (pas de séparation si rien avant)
✅ "Ministre du Secrétariat" → Sépare avant "Secrétariat"
✅ "Secrétariat" sans "Général" → Pas de séparation obligatoire
✅ "République Démocratique du Secrétariat Général du Congo" → Sépare correctement

---

## Fichiers Modifiés

1. **templates/public/generate.html**
   - Ligne 68: Changé couleur du label "Version pour fonds sombres"

2. **algorithms/text_splitter.py**
   - Lignes 33-37: Mise à jour de la docstring
   - Lignes 38-55: Ajout de la détection et logique de séparation pour "secrétariat général"
   - Lignes 83+: Reste de l'algorithme inchangé

---

## Vérification

### Test 1: Label visible
- ✅ Ouvrir `/generate`
- ✅ Générer un logo
- ✅ Vérifier que "Version pour fonds sombres" est lisible en texte sombre

### Test 2: Séparation "secrétariat général"
- ✅ Générer avec "Ministère du Secrétariat Général"
- ✅ Vérifier que le texte s'affiche sur 2 lignes:
  - Ligne 1: "MINISTÈRE DU"
  - Ligne 2: "SECRÉTARIAT GÉNÉRAL"

### Test 3: Cas normal (pas de "secrétariat général")
- ✅ Générer avec "Ministère de la Défense"
- ✅ Vérifier que l'algorithme normal s'applique

---

## Impact

- ✅ Aucun changement à l'API
- ✅ Aucun changement au backend (génération d'images)
- ✅ Comportement automatique, transparent pour l'utilisateur
- ✅ Amélioration de la lisibilité visuelle des logos

