# Les décorateurs

Un décorateur est une **fonction qui prend une fonction en argument et retourne une nouvelle fonction**, généralement pour lui ajouter un comportement (logging, timing, validation, cache...) sans modifier son code source. C'est une application directe des fonctions d'ordre supérieur, combinée à la syntaxe `@`.

**Syntaxe :**

```python
@mon_decorateur
def ma_fonction():
    ...

# équivalent à :
def ma_fonction():
    ...
ma_fonction = mon_decorateur(ma_fonction)
```

## Exemple 1 — décorateur simple, chronométrer une fonction

```python
import time
from functools import wraps

def chronometre(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        debut = time.perf_counter()
        resultat = func(*args, **kwargs)
        duree = time.perf_counter() - debut
        print(f"{func.__name__} a pris {duree:.4f}s")
        return resultat
    return wrapper

@chronometre
def calcul_lourd(n):
    return sum(i ** 2 for i in range(n))

calcul_lourd(1_000_000)
# calcul_lourd a pris 0.0821s
```

## Exemple 2 — décorateur paramétré, retry configurable

Un décorateur qui prend lui-même des arguments a besoin d'un niveau d'imbrication supplémentaire : une fonction qui retourne le décorateur, qui retourne le wrapper.

```python
from functools import wraps

def retry(tentatives=3):
    def decorateur(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for essai in range(1, tentatives + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Tentative {essai}/{tentatives} échouée : {e}")
                    if essai == tentatives:
                        raise
        return wrapper
    return decorateur

@retry(tentatives=3)
def appel_api_instable():
    import random
    if random.random() < 0.7:
        raise ConnectionError("timeout")
    return "OK"
```

## Points clés

- **`*args, **kwargs`** dans le `wrapper` sont indispensables pour que le décorateur reste générique et fonctionne avec n'importe quelle fonction, quelle que soit sa signature.
- **`@functools.wraps(func)`** copie `__name__`, `__doc__` et d'autres métadonnées du `func` original sur le `wrapper`. Sans lui, `calcul_lourd.__name__` vaudrait `"wrapper"` — ce qui casse le debugging, la doc, et tout framework qui inspecte la signature/le nom de la fonction (FastAPI, Click, pytest...).
- Un décorateur **sans** paramètres a 2 niveaux (`decorateur(func) -> wrapper`) ; un décorateur **avec** paramètres a 3 niveaux (`retry(tentatives) -> decorateur(func) -> wrapper`).

**NB — `inspect.signature(func).bind(...)`**

Dans un `wrapper(*args, **kwargs)`, on perd le nom des paramètres : on ne sait plus si un argument précis (ex. `user`) a été passé en positionnel (dans `args`) ou en keyword (dans `kwargs`). Aller chercher `args[0]` en dur suppose que l'appelant respecte toujours le même style d'appel — ce qui casse dès qu'une fonction est appelée autrement (`ma_fonction(user=...)` au lieu de `ma_fonction(...)`).

`inspect.signature(func).bind(*args, **kwargs)` reconstruit le mapping *nom de paramètre → valeur*, exactement comme Python le ferait pour exécuter `func`, peu importe comment les arguments ont été passés à l'appel :

```python
import inspect
from functools import wraps

def requiert_role(role):
    def decorateur(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            user = bound_args.arguments.get("user")
            if user is None or user.get("role") != role:
                raise PermissionError("Permission Denied")
            return func(*args, **kwargs)
        return wrapper
    return decorateur
```

**NB - Que l'appel soit `suppression_bdd(utilisateur_courant)` ou `suppression_bdd(user=utilisateur_courant)`, `bound_args.arguments["user"]` retrouve la bonne valeur. C'est le même principe qui permet à des frameworks comme FastAPI d'associer une requête HTTP aux bons paramètres d'une fonction, quel que soit l'ordre ou le style de l'appel.**

```python
# 1. Si ton décorateur N'A PAS d'argument -> 2 niveaux de fonctions
def mon_decorateur(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # --- Avant la fonction ---
        res = func(*args, **kwargs)
        # --- Après la fonction ---
        return res
    return wrapper

# 2. Si ton décorateur A des arguments -> 3 niveaux de fonctions
def mon_decorateur_avec_arg(option="valeur"):
    def decorateur(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Utilise 'option' et 'func' ici
            return func(*args, **kwargs)
        return wrapper
    return decorateur
``` 
