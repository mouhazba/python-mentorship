# Exercices — raise / try-except

## Exercice 1 — Validation d'entrées avec exceptions personnalisées

Écris une fonction `analyser_age(valeur: str) -> int` qui convertit une chaîne en âge valide :

- Si `valeur` n'est pas convertible en entier (`int(valeur)` échoue), lève une exception personnalisée `AgeInvalideError` avec un message clair, en chaînant la cause d'origine (`raise ... from e`).
- Si l'entier obtenu est négatif ou supérieur à 130, lève également `AgeInvalideError` (message différent selon le cas).
- Sinon, retourne l'entier.

Écris ensuite une boucle qui teste `analyser_age` sur une liste de valeurs (`["25", "-3", "abc", "200", "42"]`), capture `AgeInvalideError` pour chaque cas invalide et affiche un message distinct selon la cause (conversion impossible vs valeur hors bornes) — sans utiliser `except Exception:` générique.

- Vérifie que `e.__cause__` est bien peuplé dans le cas "abc" (conversion impossible).

## Exercice 2 — Traitement résilient d'une liste avec `try/except/else/finally`

Écris une fonction `traiter_transactions(transactions: list[dict]) -> dict` qui parcourt une liste de transactions de la forme `{"montant": ..., "type": "credit"|"debit"}` et met à jour un solde en partant de 0 :

- `type == "credit"` : ajoute `montant` au solde.
- `type == "debit"` : retire `montant` du solde ; si `montant` dépasse le solde courant, lève `SoldeInsuffisantError` (à définir).
- Toute transaction dont `montant` n'est pas un nombre positif doit lever `ValueError`.

La fonction ne doit **pas** s'arrêter à la première transaction invalide : elle doit capturer chaque erreur transaction par transaction, l'ajouter à une liste `erreurs`, et continuer avec les suivantes. Utilise `else` pour ne compter une transaction comme "traitée" que si elle n'a levé aucune exception, et `finally` (au niveau de la boucle ou de la fonction, à toi de choisir judicieusement) pour logger le nombre de transactions traitées.

La fonction retourne `{"solde_final": ..., "erreurs": [...]}`.

- Teste avec un mélange de transactions valides et invalides (montant négatif, débit trop élevé, montant non numérique).
- Vérifie que le solde final ne reflète que les transactions réellement appliquées.
