# Revue de code — *args / **kwargs

## Exercice 1 — `statistiques` / `statistiques_ponderees`

### Ce qui fonctionne bien

- `statistiques(*valeurs: float)` capture correctement un nombre arbitraire de positionnels via `*args`, garde vide bien gérée (`if not valeurs: raise ValueError(...)`).
- `statistiques_ponderees(poids: list[float], *valeurs: float)` mélange proprement un paramètre fixe et un `*args` — exactement l'usage visé par l'exercice.
- Résultats vérifiés à l'exécution conformes à l'attendu :
  ```
  {'min': 1, 'max': 3, 'moyenne': 2.0, 'somme': 6}
  {'min': 42, 'max': 42, 'moyenne': 42.0, 'somme': 42}
  pas de `min`/`max` sur une séquence vide
  Poids pondere de [2.3, 4.5, 5.9] = 2.2834645669291342
  Taille de poid doit etre different de nombre valeurs
  ```
- Bon réflexe de tester le cas nominal, le cas à une seule valeur, le cas vide, et le cas de désaccord de tailles.

### Bug — message d'erreur trompeur — ✅ Corrigé

`statistiques_ponderees` lève l'exception quand `len(poids) != len(valeurs)`, mais le message disait *« Taille de poid doit etre different de nombre valeurs »* — soit l'inverse de la condition réelle (l'erreur survient précisément quand les tailles **diffèrent**, pas quand elles doivent différer). Un message trompeur est pire qu'absent : il envoie le lecteur dans la mauvaise direction au moment du débogage.

**Correction appliquée** (`solution_1_args_kwargs.py:20`) :

```python
raise ValueError("La taille de `poids` doit correspondre au nombre de valeurs")
```

### Edge case — ✅ Corrigé

Le cas `sum(poids) == 0` (ou `poids`/`valeurs` vides) est maintenant géré explicitement :

```python
if not poids or not valeurs:
    raise ValueError("pas de poids pondures sur une sequence vide")
...
sum_poids = sum(poids)
if sum_poids == 0:
    raise ZeroDivisionError("Division par zero impossible")
```

Bon réflexe d'avoir séparé les deux cas (séquence vide vs somme nulle) en deux exceptions distinctes plutôt qu'un seul `except` fourre-tout côté appelant — remarque au passage sur le message ligne 29 : « pas de poids pondures » contient une coquille (« pondurés » → à retirer, le mot n'apporte rien) et il manque l'accent sur « séquence ».

### Structure des tests — ✅ Corrigé

Les trois cas de `statistiques` sont maintenant isolés chacun dans leur propre `try/except` (lignes 11-24), ce qui règle exactement la fragilité relevée précédemment : un échec inattendu sur un cas n'empêche plus les suivants de s'exécuter.

### PEP 8 / lisibilité (à corriger, non bloquant)

- Ligne 1 : espace superflu avant `#`, et espace manquant après `#` (E265) → `# solution 1 ...`.
- Ligne 8 : `sum_v/len(valeurs)` — espaces manquants autour de `/` (E226) → `sum_v / len(valeurs)`.
- Ligne 15 : un seul saut de ligne entre la fin du bloc de tests et `def statistiques_ponderees` (E302 attend 2 lignes vides avant un `def` top-level).
- Pas de garde `if __name__ == "__main__":` — le code de test s'exécute au chargement du module (déjà relevé lors de revues précédentes sur ce projet).

## Exercice 2 — `avec_journalisation`

### Ce qui fonctionne bien

- `avec_journalisation(fonction, *args, **kwargs)` capture bien n'importe quelle fonction et ses arguments, journalise avant/après l'appel, et utilise correctement `try/except/else` (le `print(rslt)` + `return` ne s'exécutent que si l'appel a réussi, exactement le rôle du `else`).
- Testé avec deux fonctions de signatures différentes comme demandé : `statistiques` (positionnels uniquement, via `*args`) et `diviser` (mélange positionnel + nommé `precision=...`, avec un cas qui échoue volontairement sur `denominateur=0`).
- Les quatre appels sont chacun protégés par leur propre `try/except` côté appelant, ce qui vérifie bien que l'exception d'origine remonte jusqu'à l'appelant sans être avalée par le wrapper.

### Bug — `raise e` reconstruit la trace — ✅ Corrigé

C'est précisément le piège documenté dans `concepts/concept_exceptions.md` : à l'intérieur d'un `except Exception as e:`, `raise e` relève l'exception mais **reconstruit une nouvelle trace** à partir de ce point, en perdant l'information de la ligne où l'erreur a réellement eu lieu à l'intérieur de `fonction(*args, **kwargs)`. `raise` seul (sans argument) relève l'exception courante avec sa trace d'origine intacte.

**Correction appliquée** (`solution_2_args_kwargs.py:10`) : `raise e` → `raise`.

### Bug — message d'erreur sans le type de l'exception — ✅ Corrigé

La consigne demandait explicitement d'« afficher un message d'erreur incluant **le type** de l'exception ». `print(e)` (ligne 9 avant correction) n'affiche que le message (`str(e)`), sans indiquer s'il s'agit d'un `ValueError`, `TypeError`, etc.

**Correction appliquée** (`solution_2_args_kwargs.py:9`) :

```python
print(f"Erreur ({type(e).__name__}) : {e}")
```

### Bug — vérification `__cause__` toujours fausse (code mort) — ✅ Corrigé

Les quatre blocs `except` côté appelant testaient `if e.__cause__ is not None:` avant d'afficher la cause. Or `raise e` (et même `raise` seul) **ne peuplent jamais `__cause__`** : `__cause__` n'est défini que par un `raise ... from ...` explicite. Vérifié à l'exécution avant correction — aucune des quatre lignes « Cause originale » ne s'affichait jamais, y compris pour les deux appels qui lèvent bel et bien une exception (`statistiques()` et `diviser(10, 0, ...)`) : la condition était systématiquement fausse, rendant ce diagnostic silencieusement inopérant.

**Correction appliquée** (`solution_2_args_kwargs.py:28,33,45,51`), remplacée par une confirmation inconditionnelle de la remontée :

```python
except Exception as e:
    print(f"Exception remontée jusqu'à l'appelant : {type(e).__name__} ({e})")
```

Revérifié à l'exécution : les deux cas d'erreur affichent maintenant bien `Exception remontée jusqu'à l'appelant : ValueError (...)`, confirmant que l'exception d'origine (type et message) traverse intacte le wrapper jusqu'à l'appelant — exactement ce que l'exercice demandait de vérifier.

### PEP 8 / lisibilité — ✅ Corrigé (effet de bord des corrections ci-dessus)

- Ligne 1 : backtick fermant manquant après `**kwargs`, espace manquant après `#`.
- Lignes 3, 6, 12 : commentaires sans espace après `#` (E265) et sans accents (« avant execution », « Apres Execution ») — reformulés en « avant exécution », « exécution », « après exécution ».

Reste non traité (mineur, non bloquant) :

- Ligne 15 : un seul saut de ligne entre `avec_journalisation` et `def statistiques` (E302, attend 2).
- Ligne 42 (et similaires) : un seul saut de ligne entre `def diviser` et le `try` suivant (incohérent avec les 2 lignes vides utilisées ailleurs dans le fichier).
- `rp` (résultat de `avec_journalisation`) est assigné à chaque appel mais jamais utilisé ensuite — sans gravité ici puisque l'affichage a lieu à l'intérieur du wrapper, mais une variable non lue est un signal à surveiller.
- Pas de garde `if __name__ == "__main__":`.

## Respect du concept

Bonne maîtrise de `*args`/`**kwargs` sur les deux exercices : capture positionnelle pure (`statistiques`), mélange positionnel/nommé transmis tel quel via `fonction(*args, **kwargs)` (`avec_journalisation`), et signatures différentes correctement relayées sans connaître leur détail. Le point à retenir de cette revue rejoint directement le concept précédent (raise/try-except) : un wrapper générique qui relaie `*args, **kwargs` doit aussi relayer l'exception **sans la déformer** — `raise` seul (jamais `raise e`) est ce qui garantit que la trace d'origine reste exploitable une fois l'erreur remontée à travers plusieurs couches d'abstraction, un scénario très fréquent dès qu'on empile des décorateurs ou des wrappers.

## Synthèse

| Sévérité | Constat | Emplacement |
|---|---|---|
| Moyenne (bug) | Ex.1 — Message d'erreur inversé par rapport à la condition réelle — ✅ corrigé | `solution_1_args_kwargs.py:20` |
| Moyenne (bug) | Ex.2 — `raise e` reconstruit la trace au lieu de la préserver — ✅ corrigé | `solution_2_args_kwargs.py:10` |
| Moyenne (bug) | Ex.2 — Message d'erreur sans le type de l'exception (exigé par la consigne) — ✅ corrigé | `solution_2_args_kwargs.py:9` |
| Moyenne (code mort) | Ex.2 — `if e.__cause__ is not None` toujours faux, diagnostic jamais affiché — ✅ corrigé | `solution_2_args_kwargs.py:28,33,45,51` |
| Faible (PEP 8) | E226, E265, E302, backtick manquant, coquilles d'accents | `solution_1_args_kwargs.py:1,8,15` · `solution_2_args_kwargs.py:15,42` |
| Faible | `rp` assigné mais jamais lu | `solution_2_args_kwargs.py:26,31,43,49` |
| Style | Pas de garde `if __name__ == "__main__":` | les deux fichiers |
