# Les fonctions `lambda`

Une `lambda` est une **fonction anonyme** (sans nom), définie en une seule ligne, sans `def`. Elle est limitée à une seule expression, qui est automatiquement retournée — pas besoin de `return`.

**Syntaxe :**

```python
lambda arguments: expression
```

## Exemple 1 — usage simple, équivalent à une fonction classique

```python
carre = lambda x: x ** 2
print(carre(5))  # 25

# équivalent avec def :
def carre(x):
    return x ** 2
```

## Exemple 2 — usage idiomatique, comme argument d'une autre fonction (`sorted`, `map`, `filter`)

```python
personnes = [{"nom": "Alice", "age": 30}, {"nom": "Bob", "age": 25}]

# tri par age, sans définir une fonction nommée juste pour ça
tri_par_age = sorted(personnes, key=lambda p: p["age"])
print(tri_par_age)
# [{'nom': 'Bob', 'age': 25}, {'nom': 'Alice', 'age': 30}]

# filtrer les nombres pairs
nombres = [1, 2, 3, 4, 5, 6]
pairs = list(filter(lambda n: n % 2 == 0, nombres))
print(pairs)  # [2, 4, 6]
```

## Point clé (PEP 8)

PEP 8 déconseille d'assigner une lambda à une variable comme dans l'exemple 1 (`carre = lambda x: ...`) — dans ce cas, autant utiliser `def`.

Le vrai cas d'usage d'une lambda, c'est quand une fonction est **jetable**, passée directement en argument (`key=`, `map`, `filter`), sans jamais être réutilisée ailleurs.
