# Observations — le besoin réel de raise / try-except dans l'écosystème Python

## Pourquoi les exceptions existent vraiment

Le mécanisme d'exceptions répond à un problème que le retour de valeur seul ne résout pas proprement : **séparer le chemin nominal du code de la gestion des cas anormaux**, sans polluer chaque appel de fonction avec des vérifications de codes d'erreur (`if result == -1: ...`). Une exception interrompt immédiatement l'exécution et remonte la pile jusqu'au premier `except` compatible, en transportant avec elle un message et une trace complète — impossible à ignorer silencieusement comme un code de retour non vérifié.

**Règle pratique qui revient dans tout l'écosystème** : une fonction lève une exception dès qu'elle ne peut pas honorer son contrat (entrée invalide, ressource indisponible, état incohérent) ; elle ne retourne `None` ou une valeur "sentinelle" que lorsque l'absence de résultat est un cas **normal et attendu** par l'appelant (ex: `dict.get()`). Confondre les deux — retourner `None` pour une vraie erreur — est la source la plus fréquente de bugs silencieux en Python.

Le second usage, moins visible, est la **hiérarchie d'exceptions comme documentation vivante de l'API** : la structure des classes d'exception d'une bibliothèque (`requests.exceptions.*`, `django.core.exceptions.*`) indique à l'appelant exactement quels cas il peut distinguer et gérer séparément.

## Cadre par cadre

### 1. Python "vanille" (stdlib)

- **La hiérarchie `BaseException` → `Exception` → ...** est la colonne vertébrale de tout le langage : `KeyError`, `IndexError`, `AttributeError`, `TypeError` sont levées en permanence par les structures de données natives (`dict[clé]`, `liste[index]`) — comprendre `try/except` est un prérequis pour lire n'importe quel code Python, pas seulement pour en écrire.
- **`contextlib.suppress(Exception)`** encapsule le pattern "ignorer une exception précise" plus proprement qu'un `try/except: pass` nu.
- **`warnings.warn()`** est le cousin non-fatal de `raise` : signale une situation anormale sans interrompre l'exécution, utilisé massivement pour les dépréciations d'API.
- **`sys.excepthook`** et le module `traceback` permettent de personnaliser l'affichage ou la capture des exceptions non gérées, base de tout système de logging d'erreurs en production.

### 2. Tests (pytest, unittest)

- **`pytest.raises(ExceptionType)`** est le mécanisme central pour tester qu'une fonction échoue correctement — un test qui vérifie *qu'une exception est bien levée* est aussi important qu'un test du chemin nominal, et c'est souvent l'endroit où l'on découvre qu'une fonction avale silencieusement une erreur qu'elle aurait dû propager.
- Les hiérarchies d'exceptions personnalisées (comme `SoldeInsuffisantError` de l'exercice) permettent des assertions précises (`pytest.raises(SoldeInsuffisantError)`) plutôt que de tester un message texte fragile.

### 3. Frameworks web (FastAPI, Django, Flask)

- **FastAPI `HTTPException`** est directement levée dans une route pour produire une réponse HTTP avec un code de statut précis (404, 400, 403...) — le framework capture l'exception au niveau global et la transforme en réponse JSON, exactement le pattern `raise` + gestionnaire centralisé.
- **Les "exception handlers" (`@app.exception_handler(MonException)`)** en FastAPI/Starlette généralisent le `try/except` local à l'échelle de toute l'application : au lieu de capturer partout, on lève des exceptions métier spécifiques et on centralise leur traduction en réponse HTTP à un seul endroit.
- **Django** utilise une hiérarchie similaire (`Http404`, `PermissionDenied`, `ValidationError`) — lever `ValidationError` dans un `clean()` de formulaire est le mécanisme standard de validation de données.
- **Les clients HTTP (`requests`, `httpx`)** exposent `response.raise_for_status()` qui lève une exception si le code HTTP indique une erreur (4xx/5xx) — pattern EAFP typique : on tente l'appel réseau, on gère l'échec après coup plutôt que de tout vérifier avant.

### 4. Data Science / IA & Machine Learning

- **pandas** lève des exceptions précises (`KeyError` sur colonne absente, `ValueError` sur incompatibilité de shape/dtype) qui sont couramment capturées dans des pipelines de nettoyage de données pour isoler les lignes/fichiers problématiques sans interrompre tout le traitement — exactement le pattern "traiter transaction par transaction, continuer malgré les erreurs" de l'exercice 2.
- **PyTorch / TensorFlow** lèvent des exceptions dédiées (`RuntimeError` pour incompatibilité de dimensions de tenseurs, `torch.cuda.OutOfMemoryError`) qu'un pipeline d'entraînement robuste doit anticiper — par exemple pour réduire dynamiquement la taille de batch en cas d'OOM (`except torch.cuda.OutOfMemoryError: ...`).
- **Appels à des API de LLM (OpenAI, Anthropic)** exposent des hiérarchies d'exceptions typées (`RateLimitError`, `APITimeoutError`, `AuthenticationError`) qu'un code de production doit distinguer pour décider s'il faut réessayer (rate limit, timeout) ou échouer immédiatement (erreur d'authentification) — un `except Exception:` générique masquerait cette distinction critique pour une stratégie de retry.

### 5. Ingénierie de données et systèmes distribués

- **Retry avec backoff (`tenacity`, `backoff`)** : ces bibliothèques s'appuient entièrement sur `try/except` pour intercepter des exceptions transitoires (timeout réseau, erreur 503) et relancer automatiquement l'opération — un pattern impossible sans une hiérarchie d'exceptions permettant de distinguer "erreur temporaire, à réessayer" de "erreur définitive, à propager".
- **SQLAlchemy / connecteurs de base de données** lèvent des exceptions typées (`IntegrityError`, `OperationalError`) essentielles pour distinguer une violation de contrainte métier (à gérer applicativement) d'une perte de connexion (à réessayer).
- **Traitement de fichiers/ETL en masse** : le pattern "capturer l'erreur par enregistrement, logger, continuer le lot" (comme dans l'exercice 2) est la norme dans tout pipeline batch — un seul enregistrement corrompu ne doit jamais faire échouer tout le job.

## Synthèse

| Contexte | Rôle de raise / try-except |
|---|---|
| stdlib | base de la gestion d'erreur du langage (`KeyError`, `IndexError`...) |
| pytest | `pytest.raises` pour valider le comportement d'échec d'une fonction |
| FastAPI/Django | `HTTPException`/`ValidationError` + gestionnaires centralisés pour traduire erreurs métier en réponses HTTP |
| requests/httpx | `raise_for_status()`, pattern EAFP pour les appels réseau |
| pandas/PyTorch | isoler les erreurs de données/calcul sans interrompre tout le pipeline |
| APIs LLM (OpenAI, Anthropic) | distinguer erreurs transitoires (retry) et définitives (échec immédiat) |
| tenacity/backoff, SQLAlchemy | retry automatique sur exceptions transitoires vs propagation des erreurs définitives |

## Le fil conducteur

Partout dans l'écosystème, `raise`/`try-except` est le mécanisme qui permet de **rendre les erreurs explicites, typées et impossibles à ignorer silencieusement**, tout en gardant le code du chemin nominal lisible. La compétence clé n'est pas de savoir écrire un `try/except` — c'est de savoir **quand** lever, **quoi** capturer (jamais plus large que nécessaire), et **comment** structurer une hiérarchie d'exceptions qui documente les cas d'erreur d'une API. C'est un prérequis direct pour tout code de production interagissant avec un réseau, une base de données, un modèle ML, ou tout système externe intrinsèquement faillible.
