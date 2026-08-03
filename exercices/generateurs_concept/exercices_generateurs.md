# Exercices — générateurs

## Exercice 1 — Générateur paresseux : filtrer un gros fichier log

Écris une fonction génératrice `lire_erreurs_log(chemin)` qui lit un fichier ligne par ligne et ne `yield` que les lignes contenant le mot `"ERROR"`, sans jamais charger tout le fichier en mémoire.

- Crée un petit fichier `log_exemple.txt` de test avec un mélange de lignes `INFO`, `WARNING`, `ERROR`.
- Consomme le générateur avec une boucle `for` et affiche chaque ligne d'erreur trouvée.
- Vérifie explicitement (par exemple avec `list(gen)` appelé deux fois de suite) qu'un générateur déjà épuisé ne renvoie plus rien, contrairement à une fonction qui retournerait une liste.

## Exercice 2 — Pipeline de générateurs avec `yield from`

Construis un petit pipeline de traitement de flux, entièrement paresseux :

1. `compteur(depart=0)` : générateur **infini** qui yield `depart`, `depart + 1`, `depart + 2`, ...
2. `filtrer_multiples(sequence, n)` : générateur qui ne laisse passer que les valeurs de `sequence` multiples de `n`.
3. `pagine(sequence, taille)` : générateur qui regroupe les valeurs de `sequence` par lots (listes) de longueur `taille`, en utilisant `yield from` pour déléguer si besoin.

- Combine les trois pour produire les 4 premiers lots de 3 multiples de 5 à partir de 0 (résultat attendu : `[0, 5, 10]`, `[15, 20, 25]`, `[30, 35, 40]`, `[45, 50, 55]`), en te limitant avec `itertools.islice` puisque `compteur` est infini.
