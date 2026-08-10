# Exercices — *args / **kwargs

## Exercice 1 — Agrégateur générique avec `*args`

Écris une fonction `statistiques(*valeurs: float) -> dict` qui accepte un nombre arbitraire de nombres et retourne un dictionnaire `{"min": ..., "max": ..., "moyenne": ..., "somme": ...}`.

- Si aucune valeur n'est passée, lève une `ValueError` avec un message clair (pas de `min`/`max` sur une séquence vide).
- Écris ensuite une fonction `statistiques_ponderees(poids: list[float], *valeurs: float) -> float` qui calcule une moyenne pondérée (`sum(v * p for v, p in zip(valeurs, poids)) / sum(poids)`), et lève une `ValueError` si `len(poids) != len(valeurs)`.

Teste `statistiques` avec plusieurs appels (`statistiques(1, 2, 3)`, `statistiques(42)`, `statistiques()` pour vérifier l'exception), et `statistiques_ponderees` avec un cas valide et un cas où les longueurs ne correspondent pas.

## Exercice 2 — Wrapper de journalisation avec `*args` et `**kwargs`

Écris une fonction `avec_journalisation(fonction, *args, **kwargs)` qui :

- Affiche un message avant l'appel indiquant le nom de la fonction (`fonction.__name__`) et les arguments reçus (`args` et `kwargs`).
- Appelle `fonction(*args, **kwargs)` et capture le résultat.
- Si l'appel lève une exception, affiche un message d'erreur incluant le type de l'exception et la relève (`raise`), sans l'avaler.
- Si l'appel réussit, affiche le résultat obtenu puis le retourne.

Utilise `avec_journalisation` pour appeler au moins deux fonctions différentes que tu définiras toi-même :
- une fonction avec seulement des arguments positionnels,
- une fonction avec un mélange d'arguments positionnels et nommés, dont un qui lève volontairement une exception sur certaines entrées (pour vérifier que l'erreur est bien journalisée puis relevée).

- Vérifie avec `try/except` autour de l'appel à `avec_journalisation` que l'exception d'origine remonte bien jusqu'à l'appelant.
