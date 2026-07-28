# Observations — le besoin réel des `lambda` dans l'écosystème Python

## Pourquoi les lambdas existent vraiment

Une lambda n'est pas "une fonction en plus court". Son vrai rôle est de permettre de **passer un comportement en argument** à une fonction d'ordre supérieur (une fonction qui prend une fonction en paramètre), sans polluer le namespace avec une fonction nommée qui ne sert qu'une fois, à un seul endroit.

Le besoin réel apparaît chaque fois qu'une API attend un **callback** : "comment veux-tu trier ?", "comment veux-tu transformer chaque élément ?", "quelle condition veux-tu appliquer ?". Ce sont les fonctions d'ordre supérieur (`sorted`, `map`, `filter`, `key=`, `reduce`) qui créent ce besoin — la lambda est juste la syntaxe la plus légère pour y répondre.

**Règle pratique qui revient dans tout l'écosystème :** si le callback est court, immédiat et non réutilisé ailleurs → lambda. S'il doit être testé isolément, réutilisé, ou dépasse une expression → fonction nommée (`def`).

## Cadre par cadre

### 1. Python "vanille" (stdlib)

- `sorted(iterable, key=lambda x: ...)`, `list.sort(key=...)` : tri par un critère dérivé, sans créer une fonction nommée pour ça.
- `max()` / `min()` avec `key=` : ex. `max(employes, key=lambda e: e.salaire)`.
- `functools.reduce(lambda acc, x: acc + x, iterable)` : agrégation générique.
- `tkinter` (GUI) : `button = Button(root, command=lambda: action(param))` — indispensable ici car `command=` attend une fonction *sans argument*, et la lambda permet de "figer" un paramètre au moment de la création du bouton (utile typiquement dans une boucle qui crée plusieurs boutons).

### 2. Django / frameworks web

- **`urls.py`** : `path('', lambda request: redirect('accueil'))` pour une redirection triviale, sans créer une vue dédiée dans `views.py`.
- **Champs de modèle avec valeur par défaut dynamique** : `champ = models.DateTimeField(default=lambda: timezone.now() + timedelta(days=7))` — Django a besoin d'un *callable*, pas d'une valeur figée à l'import du module (sinon la date serait calculée une seule fois au démarrage du serveur).
- **Signaux et petits validateurs inline** dans les migrations ou settings.

Le point commun : Django exige souvent un *callable* (pas juste une valeur) pour retarder une évaluation — la lambda est le moyen le plus court de fournir "une valeur calculée plus tard".

### 3. Machine Learning / Data Science (pandas, numpy)

- `df['col'].apply(lambda x: x.strip().lower())` : transformation ligne par ligne quand aucune fonction vectorisée native n'existe pour ce cas précis.
- `df.apply(lambda row: row['a'] + row['b'], axis=1)` : logique multi-colonnes ad hoc.
- `df.groupby('categorie').agg(lambda x: x.max() - x.min())` : agrégation personnalisée par groupe.

**Attention (point pédagogique important)** : en pandas/numpy, une lambda dans `.apply()` est **souvent un anti-pattern de performance** — elle force une boucle Python élément par élément, alors qu'une opération vectorisée native (`df['col'] - df['col'].mean()`) s'exécute en C et est 10 à 100x plus rapide. La lambda ici est un outil de *dernier recours* quand la vectorisation n'est pas possible, pas le premier réflexe.

### 4. Deep Learning / IA (PyTorch, Keras/TensorFlow)

- **PyTorch** : `transforms.Lambda(lambda x: x / 255.0)` dans un pipeline `torchvision.transforms.Compose([...])` — pour insérer une transformation custom au milieu de transformations standards, sans écrire une classe entière.
- **Keras** : `tf.keras.layers.Lambda(lambda x: x * 2)` — permet d'insérer une opération arbitraire comme une couche dans un modèle séquentiel, quand cette opération n'a pas de couche dédiée.
- Callbacks d'entraînement légers, ex. `LearningRateScheduler(lambda epoch: lr * 0.95 ** epoch)`.

### 5. Spark (PySpark)

- Historiquement le cas d'usage le plus visible : `rdd.map(lambda x: x * 2)`, `rdd.filter(lambda x: x > 0)`, `rdd.reduceByKey(lambda a, b: a + b)`.
- Spark distribue la lambda comme fonction à appliquer sur chaque partition/nœud du cluster — c'est le modèle MapReduce lui-même qui repose sur "donne-moi une petite fonction à appliquer à chaque élément".
- Aujourd'hui, sur des DataFrames Spark (API moderne), on préfère les fonctions natives de `pyspark.sql.functions` (plus optimisées par le moteur Catalyst) — les lambdas restent surtout utilisées sur l'API RDD bas niveau ou pour des UDF (`udf(lambda x: ..., ReturnType())`) quand aucune fonction native n'existe.

### 6. Programmation fonctionnelle générale (`functools`, `itertools`)

- `functools.reduce`, `sorted`, `itertools.groupby(iterable, key=lambda x: ...)` : la lambda est le langage commun de tous les outils qui suivent le paradigme "prends une collection + une fonction".

## Synthèse

| Contexte | Rôle de la lambda |
|---|---|
| stdlib (`sorted`, `map`, `filter`) | callback de tri/transformation/filtre ponctuel |
| Tkinter | figer des arguments pour un callback sans-argument |
| Django | callable différé (valeur calculée à l'exécution, pas à l'import) |
| pandas/numpy | transformation ad hoc quand pas de vectorisation possible (à utiliser avec parcimonie) |
| PyTorch/Keras | insérer une opération custom dans un pipeline/modèle sans écrire une classe |
| Spark | fonction distribuée appliquée à chaque partition (modèle MapReduce) |

**Le fil conducteur partout** : la lambda n'est jamais la brique de logique métier centrale d'une application — c'est le connecteur léger entre une API générique (qui attend "une fonction") et un besoin très spécifique et local. Dès que ce besoin grandit (plusieurs lignes, réutilisation, besoin de tests unitaires), le bon réflexe est de remonter vers une fonction `def` nommée.
