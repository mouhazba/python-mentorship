# Revue de code — générateurs

## Exercice 1 — `lire_erreurs_log`

### Ce qui fonctionne bien

- Générateur correctement écrit : lecture paresseuse, filtrage sur `"ERROR"`, aucune liste intermédiaire.
- La démonstration de l'épuisement est bien pensée : instancier `gen` séparément, appeler `list(gen)` deux fois de suite pour montrer que le second passage est vide. C'est exactement le comportement à mettre en évidence.

### À corriger

1. **Lignes non nettoyées** (ligne 6, `yield ligne`) : `ligne` contient encore le `\n` de fin de ligne du fichier. Résultat visible à l'exécution : une ligne vide entre chaque alerte affichée (`print(f"🚨 ALERTE : {ligne}")` ajoute son propre `\n` en plus de celui déjà présent dans `ligne`), et les entrées de `premieres_erreurs` contiennent toutes un `\n` final. Correction : `yield ligne.rstrip("\n")` (ou `.strip()`).
2. **Pas de garde `if __name__ == "__main__":`** : tout le code (ouverture de fichier, boucles, `print`) s'exécute au chargement du module. Sans conséquence ici, mais c'est une habitude à prendre tôt — un fichier réutilisé ou importé ailleurs (tests, notebook) déclencherait ces effets de bord silencieusement.
3. Chemin `"log_exemple.txt"` en dur, relatif au répertoire courant — fragile si le script est lancé d'ailleurs. Non bloquant pour un exercice.

## Exercice 2 — pipeline `compteur` → `filtrer_multiples` → `pagine_deleguee`

### Ce qui fonctionne bien

- `compteur` et `filtrer_multiples` : exactement le pattern attendu, génériques et réutilisables.
- Résultat vérifié à l'exécution : `[[0, 5, 10], [15, 20, 25], [30, 35, 40], [45, 50, 55]]` — correct.
- Bonne intuition de découpage : séparer "produire un lot" (`extraire_un_lot`) de "boucler et déléguer" (`pagine_deleguee` + `yield from`).

### Bug réel (le point important de cette revue)

`pagine_deleguee` (lignes 45-48) ne s'arrête jamais quand la séquence source est **finie**. Une fois `seq_iter` épuisé, `extraire_un_lot` ne construit aucun lot (`lot` reste `[]`), donc `if lot:` est faux et rien n'est `yield`é — mais `pagine_deleguee` repart quand même dans son `while True`, rappelle `extraire_un_lot` sur un itérateur déjà vide, ne produit toujours rien, et ainsi de suite : **boucle infinie silencieuse**, sans exception, 100 % CPU.

Testé directement avec une source finie (`range(7)` au lieu de `compteur`) : la boucle ne se termine jamais (confirmé avec un timeout). Le bug n'apparaît pas dans l'exercice tel qu'écrit uniquement parce que `compteur` est infini et que l'appelant limite volontairement la consommation avec `itertools.islice(lots, 4)`. Comme `pagine_deleguee` est une fonction générique (pas nommée ni documentée comme "pour source infinie uniquement"), c'est le genre de bug qui explose au premier réemploi sur une liste normale.

Correction minimale :

```python
def pagine_deleguee(sequence, taille):
    seq_iter = iter(sequence)
    while True:
        lot_produit = False
        for lot in extraire_un_lot(seq_iter, taille):
            lot_produit = True
            yield lot
        if not lot_produit:
            return
```

### Simplification possible

`extraire_un_lot` (lignes 36-43) est un générateur qui `yield` au plus **une seule** valeur (un lot, ou rien). Le `yield`/`yield from` n'apporte ici aucun bénéfice de paresse supplémentaire, puisque le lot est de toute façon entièrement construit avant d'être produit — c'est un signal qu'une fonction classique avec `return` suffit et serait plus directe à lire :

```python
def extraire_un_lot(sequence_iter, taille):
    return list(itertools.islice(sequence_iter, taille))  # [] si épuisé

def pagine_deleguee(sequence, taille):
    seq_iter = iter(sequence)
    while True:
        lot = extraire_un_lot(seq_iter, taille)
        if not lot:
            return
        yield lot
```

`itertools.islice(sequence_iter, taille)` remplace toute la boucle manuelle d'accumulation (`append` + `break` au bon compte) et gère nativement le cas où l'itérateur s'épuise avant d'atteindre `taille` éléments — ce qui corrige le bug ci-dessus en même temps que ça simplifie le code.

Le `yield from` reste un choix pédagogiquement valide (c'était la consigne), mais c'est un bon exemple concret de la limite du pattern : il est fait pour déléguer une **itération**, pas pour renvoyer un résultat déjà entièrement construit.

### PEP 8 / lisibilité

- Ligne 51 : `multiple =filtrer_multiples(source, 5)` — espace manquant après `=` (E225). Corriger en `multiple = filtrer_multiples(source, 5)`.
- Nommage : `multiple` contient une séquence de plusieurs valeurs → `multiples` (pluriel) serait plus juste.
- `import itertools` (ligne 54) est placé au milieu du fichier plutôt qu'en tête — à regrouper avec les autres imports en haut du module.
- Ligne 43, commentaire `# Produit le tableau [0, 5, 10]` : référence un cas d'usage particulier (multiples de 5, lot de 3) dans une fonction censée être générique. Trompeur/obsolète dès que la fonction est appelée avec d'autres paramètres — à généraliser ou supprimer.
- Ligne 24, espace de fin de ligne après `# exercice 2` (W291). Un linter (`ruff`, `flake8`) attraperait ce genre de détail automatiquement.

## Respect du concept

Les deux exercices montrent une bonne compréhension du concept : lazy evaluation, épuisement d'un générateur, délégation via `yield from`, composition en pipeline. Le point à retenir : un générateur qui ne `yield`e qu'une valeur unique de façon conditionnelle est souvent le signe qu'une fonction classique (`return`) ferait l'affaire — `yield`/`yield from` gagnent leur place quand il y a une vraie itération incrémentale à déléguer, pas pour retourner un résultat déjà entièrement calculé.

## Synthèse

| Sévérité | Constat | Emplacement |
|---|---|---|
| Élevée (bug) | `pagine_deleguee` boucle indéfiniment sur une source finie | `exercices_generateurs.py:45-48` |
| Moyenne | Lignes non nettoyées → ligne vide entre chaque alerte affichée | `exercices_generateurs.py:6` |
| Faible | `extraire_un_lot` sur-complexifié via `yield`/`yield from` | `exercices_generateurs.py:36-43` |
| Faible (PEP 8) | espace manquant autour de `=`, import hors du haut de fichier, commentaire obsolète, trailing whitespace | lignes 24, 43, 51, 54 |
| Style | Pas de garde `if __name__ == "__main__":` | tout le fichier |
