# Les générateurs

Un générateur est une **fonction qui produit une séquence de valeurs paresseusement (lazy)**, une par une, via le mot-clé `yield`, au lieu de construire toute la séquence en mémoire d'un coup comme le ferait une fonction classique retournant une liste. Chaque appel à `next()` reprend l'exécution de la fonction juste après le dernier `yield`, en conservant tout son état local (variables, position dans les boucles) entre deux reprises.

**Syntaxe :**

```python
def mon_generateur():
    yield 1
    yield 2
    yield 3

gen = mon_generateur()   # ne s'exécute rien encore : retourne un objet générateur
next(gen)  # 1 -> exécute jusqu'au premier yield
next(gen)  # 2 -> reprend juste après, jusqu'au yield suivant
next(gen)  # 3
next(gen)  # StopIteration -> plus de valeur, la fonction est arrivée au bout
```

Un générateur est un **itérateur** : il fonctionne nativement avec `for`, `sum()`, `list()`, etc.

## Exemple 1 — lazy evaluation : lire un gros fichier ligne par ligne

L'intérêt principal d'un générateur est de ne **jamais garder toute la séquence en mémoire**. Comparaison avec une fonction classique :

```python
# Version "eager" : charge tout le fichier en mémoire avant de retourner
def lignes_majuscules_liste(chemin):
    resultat = []
    with open(chemin) as f:
        for ligne in f:
            resultat.append(ligne.upper())
    return resultat  # un fichier de 10 Go -> 10 Go en RAM

# Version "lazy" avec un générateur : une ligne à la fois
def lignes_majuscules_gen(chemin):
    with open(chemin) as f:
        for ligne in f:
            yield ligne.upper()  # suspend ici, attend le prochain next()

for ligne in lignes_majuscules_gen("gros_fichier.txt"):
    traiter(ligne)  # une seule ligne en mémoire à la fois
```

La fonction `lignes_majuscules_gen` ne lit rien tant qu'on ne consomme pas le générateur (avec `for`, `next()`, `list()`...). Chaque itération produit une ligne, la traite, puis l'oublie avant de passer à la suivante.

## Exemple 2 — pipeline de générateurs avec `yield from`

Les générateurs se chaînent facilement pour construire des pipelines de traitement, où chaque étage transforme le flux sans jamais matérialiser de liste intermédiaire :

```python
def entiers_naturels():
    n = 0
    while True:          # séquence infinie : impossible avec une liste !
        yield n
        n += 1

def filtrer_pairs(sequence):
    for x in sequence:
        if x % 2 == 0:
            yield x

def elever_au_carre(sequence):
    yield from (x ** 2 for x in sequence)  # yield from délègue à un sous-générateur

pipeline = elever_au_carre(filtrer_pairs(entiers_naturels()))

import itertools
print(list(itertools.islice(pipeline, 5)))  # [0, 4, 16, 36, 64]
```

Rien n'est calculé tant qu'on ne tire pas des valeurs du pipeline (ici via `itertools.islice`) — ce qui permet de représenter une séquence **infinie** (`entiers_naturels`) sans jamais exploser la mémoire.

## Points clés

- **Paresse (lazy evaluation)** : les valeurs sont calculées à la demande, pas à l'avance. C'est ce qui permet de représenter des séquences infinies ou trop grosses pour tenir en RAM.
- **État conservé** : entre deux `yield`, toutes les variables locales de la fonction restent intactes — c'est la machine à états qui rend le générateur possible.
- **`yield from sous_generateur`** délègue l'itération à un autre générateur/itérable ; plus lisible qu'une boucle `for x in sous_generateur: yield x`, et transmet aussi correctement `.send()`, `.throw()`, la valeur de retour.
- Une **expression génératrice** `(x for x in iterable)` est l'équivalent lazy d'une compréhension de liste `[x for x in iterable]` — mêmes bénéfices mémoire, en une ligne.

## Pièges à éviter

- **Un générateur ne se consomme qu'une seule fois.** Une fois épuisé (StopIteration levée), il reste vide pour toujours — impossible de le réitérer sans en recréer un nouveau (rappeler la fonction génératrice) :
  ```python
  gen = mon_generateur()
  list(gen)  # [1, 2, 3]
  list(gen)  # [] -> déjà épuisé
  ```
- **La présence d'un seul `yield` dans le corps suffit à transformer toute la fonction en générateur**, même si ce `yield` est dans une branche conditionnelle jamais atteinte à l'exécution. Un `return valeur` dans une fonction contenant `yield` ne retourne pas `valeur` à l'appelant : il termine juste le générateur, et `valeur` devient l'attribut de l'exception `StopIteration` levée (récupérable via `.value` en interceptant `StopIteration`, ou automatiquement propagée par `yield from`).
- **Pas de `len()`, pas d'indexation, pas de slicing** : un générateur n'est pas une séquence. Si le code a besoin de connaître la taille à l'avance, de revenir en arrière, ou d'accéder à un élément par index, un générateur n'est pas le bon outil — il faut soit `list(gen)`, soit repenser l'approche.
- **Lever `StopIteration` manuellement à l'intérieur d'un générateur est une erreur** (PEP 479) : depuis Python 3.7, cela est automatiquement transformé en `RuntimeError` pour éviter qu'une exception interne ne soit confondue avec la fin normale d'itération.
