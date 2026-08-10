# Arguments variadiques : `*args` et `**kwargs`

Python permet à une fonction d'accepter un **nombre arbitraire d'arguments** sans devoir déclarer chaque paramètre à l'avance. `*args` collecte les arguments positionnels excédentaires dans un `tuple`, et `**kwargs` collecte les arguments nommés excédentaires dans un `dict`. Ce ne sont pas des mots-clés réservés : c'est l'astérisque (`*`, `**`) qui déclenche le comportement — `args` et `kwargs` ne sont que des noms de variable conventionnels (on pourrait écrire `*valeurs, **options`).

**Syntaxe :**

```python
def fonction(a, b, *args, c=10, **kwargs):
    print(a, b)        # arguments positionnels classiques
    print(args)        # tuple des positionnels en trop
    print(c)           # keyword-only avec défaut
    print(kwargs)       # dict des nommés en trop

fonction(1, 2, 3, 4, c=99, x=1, y=2)
# 1 2
# (3, 4)
# 99
# {'x': 1, 'y': 2}
```

L'ordre des paramètres est fixe : `positionnels`, puis `*args`, puis `keyword-only`, puis `**kwargs`.

## Exemple 1 — `*args` : une fonction agrégatrice à arité variable

Une fonction comme `somme` ou `moyenne` n'a pas de raison d'imposer un nombre fixe d'arguments :

```python
def moyenne(*valeurs: float) -> float:
    if not valeurs:
        raise ValueError("Au moins une valeur est requise")
    return sum(valeurs) / len(valeurs)

print(moyenne(10, 20, 30))   # 20.0
print(moyenne(5))             # 5.0
```

Sans `*args`, il faudrait soit imposer une liste explicite (`moyenne([10, 20, 30])`, moins naturel à l'appel), soit multiplier les signatures (`moyenne2`, `moyenne3`...).

## Exemple 2 — `**kwargs` : transmission transparente d'options (wrapper)

Le cas d'usage le plus fréquent de `**kwargs` (souvent combiné à `*args`) est de **relayer** des arguments à une autre fonction sans connaître sa signature exacte, typique des décorateurs ou des wrappers de configuration :

```python
def appel_trace(fonction, *args, **kwargs):
    print(f"Appel de {fonction.__name__} avec args={args}, kwargs={kwargs}")
    return fonction(*args, **kwargs)

def creer_utilisateur(nom: str, age: int, actif: bool = True) -> dict:
    return {"nom": nom, "age": age, "actif": actif}

resultat = appel_trace(creer_utilisateur, "Alice", age=30, actif=False)
# Appel de creer_utilisateur avec args=('Alice',), kwargs={'age': 30, 'actif': False}
print(resultat)  # {'nom': 'Alice', 'age': 30, 'actif': False}
```

Ici, `appel_trace` n'a besoin d'aucune connaissance de la signature de `creer_utilisateur` : `*args` et `**kwargs` capturent tout à l'appel, puis `fonction(*args, **kwargs)` les **déballe** (unpacking) pour les retransmettre à l'identique.

## Points clés

- **`*` et `**` ont deux rôles opposés selon le contexte** : dans une signature de fonction (`def f(*args, **kwargs)`), ils *collectent* ; dans un appel de fonction (`f(*ma_liste, **mon_dict)`), ils *déballent*. C'est le même symbole pour l'opération inverse.
- **`*args` est un `tuple`, `**kwargs` est un `dict`** — pas des listes ou des objets spéciaux ; toutes les opérations habituelles sur ces types s'appliquent.
- **L'unpacking fonctionne aussi hors des fonctions** : `[*liste1, *liste2]`, `{**dict1, **dict2}` fusionnent des collections, ce qui est très utilisé pour combiner des configurations par défaut avec des overrides.
- **Les paramètres après `*args` sont "keyword-only"** : dans `def f(a, *args, c)`, `c` ne peut être passé que par `f(1, 2, c=3)`, jamais positionnellement — utile pour forcer la clarté d'un appel.

## Pièges à éviter

- **Abuser de `**kwargs` pour éviter de définir une vraie signature** rend la fonction opaque : ni l'IDE, ni la documentation, ni le lecteur ne savent quels arguments sont réellement acceptés. À réserver aux cas génériques (wrappers, décorateurs, relais) — pas à une fonction métier normale, qui doit lister ses paramètres explicitement.
- **Mutable par défaut combiné à `**kwargs`** : `def f(**kwargs): kwargs.setdefault("options", []).append(...)` peut sembler correct mais chaque appel recrée un nouveau `dict` pour `kwargs`, donc ce piège classique (argument par défaut mutable partagé) ne s'applique pas ici — à ne pas confondre avec `def f(options=[])`, qui lui reste dangereux.
- **Modifier `kwargs` en place puis le retransmettre** (`kwargs["x"] = 1; autre_fonction(**kwargs)`) fonctionne, mais masque la provenance de `x` pour le lecteur — préférer construire un nouveau dict (`{**kwargs, "x": 1}`) pour rendre l'ajout explicite.
- **Croire que `*args, **kwargs` documente une API** : à l'usage (bibliothèque, fonction publique), préférer des paramètres explicites avec valeurs par défaut quand l'ensemble des arguments est connu ; réserver `*args`/`**kwargs` aux cas où l'arité est réellement variable ou où la fonction relaie vers une autre.
- **Oublier l'ordre imposé** (`positionnels`, `*args`, `keyword-only`, `**kwargs`) : écrire `def f(**kwargs, *args)` est une `SyntaxError` — l'ordre n'est pas une convention mais une règle du langage.
