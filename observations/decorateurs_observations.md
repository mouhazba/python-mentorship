# Observations — le besoin réel des décorateurs dans l'écosystème Python

## Pourquoi les décorateurs existent vraiment

Le décorateur répond à un problème précis : comment ajouter un comportement **transversal** (cross-cutting concern) — logging, authentification, cache, retry, validation, mesure de performance — à une fonction, sans dupliquer ce code dans chaque fonction concernée et sans polluer la logique métier de la fonction elle-même.

C'est une forme de séparation des responsabilités : la fonction décorée reste focalisée sur "que faire", le décorateur gère "comment on l'entoure" (avant/après l'appel, condition d'exécution, gestion d'erreur, enregistrement).

**Règle pratique qui revient dans tout l'écosystème** : dès qu'un comportement doit s'appliquer identiquement à plusieurs fonctions/méthodes, indépendamment de leur logique interne → décorateur. Si le comportement est spécifique à une seule fonction et non réutilisable → code inline dans la fonction.

## Cadre par cadre

### 1. Python "vanille" (stdlib)

- `@property`, `@staticmethod`, `@classmethod` : contrôlent la façon dont une méthode est accédée/liée sur une classe — piliers de la POO Python.
- `@functools.lru_cache` / `@functools.cache` : mémoïsation transparente, sans toucher au corps de la fonction.
- `@functools.wraps` : décorateur "méta" utilisé pour écrire proprement d'autres décorateurs (cf. concept).
- `@contextlib.contextmanager` : transforme une fonction génératrice en context manager utilisable avec `with`.
- `@dataclasses.dataclass` : génère automatiquement `__init__`, `__repr__`, `__eq__` à partir des annotations de classe.

### 2. Frameworks web (Flask, FastAPI, Django)

- **Flask/FastAPI** : `@app.route("/users")` ou `@app.get("/users")` — le décorateur EST le mécanisme d'enregistrement de routes. Sans lui, il faudrait un registre manuel (`routes = {"/users": ma_fonction}`) construit et maintenu à la main.
- **FastAPI** s'appuie fortement sur la signature réelle des fonctions (type hints) pour générer la validation Pydantic et la doc OpenAPI automatiques. C'est pour ça qu'un décorateur custom mal écrit (sans `functools.wraps`) peut casser silencieusement cette validation : FastAPI voit la signature du `wrapper` (`*args, **kwargs`), pas celle de la fonction d'origine.
- **Django** : `@login_required`, `@permission_required`, `@csrf_exempt` sur les vues — contrôle d'accès transversal appliqué en une ligne, réutilisé sur des dizaines de vues.
- **Flask** : `@app.before_request`, `@app.errorhandler(404)` — hooks de cycle de vie déclarés par décoration.

### 3. Tests (pytest)

- `@pytest.fixture` : injection de dépendances pour les tests (setup/teardown réutilisable).
- `@pytest.mark.parametrize` : exécute le même test avec plusieurs jeux de données, évite d'écrire N fois quasiment le même test.
- `@pytest.mark.skip` / `@pytest.mark.xfail` : contrôle conditionnel d'exécution des tests.

### 4. CLI (Click, Typer)

- `@click.command()`, `@click.option("--verbose")` : construisent une interface en ligne de commande de façon déclarative — chaque décorateur ajoute un argument/option à la fonction sans toucher à son corps.

### 5. Tâches asynchrones / distribuées (Celery)

- `@app.task` : transforme une fonction Python normale en tâche exécutable de façon asynchrone par un worker distant. Le décorateur ajoute des méthodes (`.delay()`, `.apply_async()`) à la fonction décorée.

### 6. ORM / Validation de données (SQLAlchemy, Pydantic)

- `@field_validator` (Pydantic v2) : validation custom d'un champ de modèle.
- `@hybrid_property` (SQLAlchemy) : propriété utilisable à la fois côté Python et traduite en SQL côté requête.

### 7. Résilience réseau (tenacity, backoff)

- `@retry(...)` de la librairie `tenacity` est l'extension industrielle exacte de l'exercice 2 de retry proposé dans ce module : stratégies de nouvelle tentative, backoff exponentiel, conditions d'arrêt — toutes injectées via un décorateur paramétré.

## Synthèse

| Contexte | Rôle du décorateur |
|---|---|
| stdlib | contrôle d'accès méthode (property/static/classmethod), cache, context manager |
| Flask/FastAPI | enregistrement de route, hook de cycle de vie |
| Django | contrôle d'accès transversal sur les vues |
| pytest | injection de fixtures, paramétrisation de tests |
| Click/Typer | construction déclarative de CLI |
| Celery | transformation fonction → tâche asynchrone |
| Pydantic/SQLAlchemy | validation de champ, propriété hybride |
| tenacity | retry / résilience réseau |

## Le fil conducteur

Partout dans l'écosystème, le décorateur est le mécanisme standard pour transformer une fonction "métier" en un objet **enregistré ou géré par un framework** (route, tâche, fixture, commande CLI) — c'est la frontière entre le code utilisateur et l'infrastructure du framework. Maîtriser les décorateurs (et en particulier `*args/**kwargs` + `functools.wraps`) est donc un prérequis pour comprendre en profondeur la quasi-totalité des frameworks Python modernes.
