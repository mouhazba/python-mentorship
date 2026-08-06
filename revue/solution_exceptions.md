# Revue de code — raise / try-except

## Exercice 1 — `analyser_age`

### Ce qui fonctionne bien

- Exception personnalisée `AgeInvalideError` bien définie, héritant de `Exception`.
- Chaînage correct avec `raise AgeInvalideError(...) from e` sur l'échec de conversion — `e.__cause__` est bien peuplé, vérifié à l'exécution :
  ```
  'abc' conversion impossible.
  Cause originale  : ValueError("invalid literal for int() with base 10: 'abc'"):
  ```
- Séparation claire des deux cas d'erreur (conversion impossible vs bornes), avec des messages distincts.
- Sortie testée conforme à l'attendu sur les 5 valeurs (`25` → succès, `-3` → hors bornes, `abc` → conversion impossible, `200` → hors bornes, `42` → succès).

### À corriger

- Aucun bug fonctionnel. Le seul point structurel : `except AgeInvalideError as e:` intercepte une exception potentiellement levée pour deux raisons différentes (conversion vs bornes), et distingue les deux uniquement via `e.__cause__ is not None`. Ça fonctionne, mais c'est un peu fragile — si `AgeInvalideError` est un jour levée ailleurs avec une cause, la logique d'affichage serait trompée. Une alternative plus robuste (non bloquante ici) serait deux sous-classes (`ConversionAgeError`, `BorneAgeError`) héritant de `AgeInvalideError`.

### PEP 8 / lisibilité

- ~~Nom de fichier avec espace~~ — le fichier a été renommé en `solution_1_exceptions.py` (plus d'espace).
- Ligne 3 : commentaire `# Erreur Peronalisee` — coquille (« Personnalisée »).
- Ligne 1 : `# Exercie 1` — coquille (« Exercice »).
- Ligne 29 : espace superflu avant `:` dans `f"Cause originale  : {e.__cause__!r}: "` (double espace après "originale", et `: ` final redondant en fin de f-string).
- Pas de garde `if __name__ == "__main__":` — le code de démonstration (boucle + `print`) s'exécute au chargement du module, comme relevé dans les revues précédentes.
- Lignes 30-31 : lignes vides superflues en fin de fichier.

## Exercice 2 — `traiter_transactions`

### Ce qui fonctionne bien

- Structure `try / except / else / finally` correctement articulée : la mise à jour du solde et l'incrément de `transaction_traitee` sont bien placés dans `else`, donc n'ont lieu que si la transaction n'a levé aucune exception.
- `except (ValueError, SoldeInsuffisantError) as e:` type précis, pas de capture générique.
- Résultat testé conforme sur le jeu de données fourni : `{'solde_final': 500, 'erreurs': [ValueError('Valeur incorrecte : -100'), SoldeInsuffisantError('Solde insuffisant : 500')]}`.
- Utilisation de `logging.info` plutôt que `print` pour le comptage — bon réflexe pour du code destiné à tourner en production.

### Bug réel — ✅ Corrigé

La consigne demandait explicitement : *« Toute transaction dont `montant` n'est pas un nombre positif doit lever `ValueError`. »* et de tester avec un **montant non numérique**. Ce cas n'avait pas été testé dans le jeu de données initial (seulement `-100`, `500`, `600`, tous des `int`), et il plantait :

```python
traiter_transactions([{'montant': 'abc', 'type': 'credit'}])
# TypeError: '<=' not supported between instances of 'str' and 'int'
```

La ligne `if montant <= 0:` supposait implicitement que `montant` était déjà numérique. Si ce n'était pas le cas, la comparaison levait un `TypeError`, absent du tuple `except (ValueError, SoldeInsuffisantError)` — l'exception remontait donc hors de la boucle et faisait planter toute la fonction sur une seule transaction corrompue, exactement le comportement que l'exercice demandait d'éviter.

**Correction appliquée** (`solution_2_exception.py:25`) :

```python
if not isinstance(montant, (int, float)) or isinstance(montant, bool) or montant <= 0:
    raise ValueError(f"Valeur incorrecte : {montant!r}")
```

(`isinstance(montant, bool)` exclu explicitement car `bool` est une sous-classe d'`int` en Python — `True <= 0` vaudrait `False` alors que `True` n'est pas un montant valide.)

Revérifié à l'exécution : `traiter_transactions([{'montant': 'abc', 'type': 'credit'}, {'montant': True, 'type': 'credit'}])` retourne désormais proprement `{'solde_final': 0, 'erreurs': [ValueError("Valeur incorrecte : 'abc'"), ValueError('Valeur incorrecte : True')]}` au lieu de planter. Le jeu de données original donne toujours le même résultat qu'avant (`solde_final: 500`).

### Code smell — `finally: pass` — ✅ Corrigé

Le bloc `finally: pass` ne faisait rien : du code mort, sans garantie supplémentaire. La consigne demandait d'utiliser `finally` pour logger le nombre de transactions traitées — c'était fait, mais **après la boucle**, via un simple appel `logging.info(...)`, pas dans un `finally`. Le `finally` per-itération n'avait donc aucun rôle réel.

**Correction appliquée** (`solution_2_exception.py:20-40`) : le `try/finally` a été remonté au niveau de la fonction entière, et le log déplacé dans ce `finally` :

```python
def traiter_transactions(transactions: list[dict]) -> dict:
    erreurs = []
    solde = 0
    transaction_traitee = 0
    try:
        for transaction in transactions:
            try:
                montant = transaction['montant']
                type_transaction = transaction['type']
                if not isinstance(montant, (int, float)) or isinstance(montant, bool) or montant <= 0:
                    raise ValueError(f"Valeur incorrecte : {montant!r}")
                if type_transaction == 'debit' and montant > solde:
                    raise SoldeInsuffisantError(f"Solde insuffisant : {solde}")
            except (ValueError, SoldeInsuffisantError) as e:
                erreurs.append(e)
            else:
                if type_transaction == 'credit':
                    solde += montant
                elif type_transaction == 'debit':
                    solde -= montant
                transaction_traitee += 1
    finally:
        logging.info(f"Nombre de transactions traitées : {transaction_traitee}")

    return {"solde_final": solde, "erreurs": erreurs}
```

Le `finally` de la fonction entière justifie maintenant sa présence : le log sort même si une exception non prévue casse la boucle avant la fin.

### PEP 8 / lisibilité

Ces points ont été réglés comme effet de bord des deux corrections ci-dessus (le bloc a été réécrit en entier) :

- ~~Double espace après `for`~~ — corrigé.
- ~~Espaces de fin de ligne (W291) sur 3 lignes~~ — corrigées.
- ~~Espace avant l'accolade fermante dans le dict retourné~~ — corrigé.
- ~~`list_erreur` (préfixe de type dans le nom)~~ — renommé en `erreurs`, cohérent avec la clé de retour.
- ~~Accent manquant « transactions traitee »~~ — corrigé (« traitées »).
- ~~Nom de fichier avec espace~~ — le fichier a été renommé en `solution_2_exception.py` (plus d'espace).

Restent à traiter (non touchés par cette correction, non bloquants) :

- Ligne 7 : `#filename='app_execution.log',` — ligne de code commentée sans justification ; à retirer ou à commenter pourquoi elle est désactivée.
- Incohérence de nommage entre les deux fichiers : `solution_1_exceptions.py` (pluriel) vs `solution_2_exception.py` (singulier).

## Respect du concept

Bonne maîtrise générale : `raise` avec message explicite, `raise ... from e` pour le chaînage, exceptions personnalisées, et structuration correcte de `try/except/else/finally` (le rôle de chaque bloc est respecté dans l'exercice 1 comme dans le squelette de l'exercice 2). Le point à retenir de cette revue : capturer un tuple d'exceptions précis (`except (ValueError, SoldeInsuffisantError)`) protège contre les erreurs *anticipées*, mais ne dispense pas de valider les données en amont si le type d'entrée n'est pas garanti — sinon une exception *non anticipée* (ici `TypeError`) s'échappe du `except` et casse exactement la garantie de résilience que l'exercice visait à démontrer.

## Synthèse

| Sévérité | Constat | Emplacement |
|---|---|---|
| Élevée (bug) | `TypeError` non catché sur un `montant` non numérique — fait planter toute la fonction | `exercice_2 _exception.py:24` |
| Moyenne (code smell) | `finally: pass` ne sert à rien ; le vrai `finally` (log garanti) n'est pas utilisé comme tel | `exercice_2 _exception.py:36-39` |
| Faible | `list_erreur` (préfixe de type dans le nom) | `exercice_2 _exception.py:17` |
| Faible (PEP 8) | double espace après `for`, trailing whitespace (x3), espace avant `}`, ligne commentée sans justification | `exercice_2 _exception.py:7,20,23,28,32,40` |
| Faible (PEP 8) | espaces dans les noms de fichiers (`exercice_1 _exceptions.py`, `exercice_2 _exception.py`), incohérence singulier/pluriel | noms de fichiers |
| Style | Pas de garde `if __name__ == "__main__":` | les deux fichiers |
