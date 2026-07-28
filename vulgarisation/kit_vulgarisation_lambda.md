# Kit de Vulgarisation — `lambda` en Python

## Impact dans l'écosystème et en System Design

Une `lambda` n'est presque jamais une brique métier : c'est un **connecteur léger** entre une API générique qui attend "une fonction" et un besoin ponctuel et local. Ce rôle se retrouve partout, avec la même logique sous-jacente :

- **FastAPI** : les `Depends(...)`, `sorted()` sur des résultats de requête, ou un `key=` de tri dans un endpoint — la lambda évite de créer une fonction nommée pour une transformation utilisée une seule fois dans une route.
- **Django** : `default=lambda: timezone.now() + timedelta(days=7)` sur un champ de modèle — ici la lambda a un rôle architectural précis : fournir un *callable* pour retarder l'évaluation à l'exécution plutôt qu'à l'import du module.
- **Pandas/NumPy** : `.apply(lambda x: ...)` comble l'absence d'opération vectorisée — mais en System Design, c'est un signal d'alerte : une lambda dans une boucle `.apply()` casse la vectorisation et coûte 10 à 100x en performance.
- **PySpark** : `rdd.map(lambda x: ...)` — la lambda est ici la brique même du modèle MapReduce : "une petite fonction envoyée à chaque nœud du cluster".

**Le principe de System Design sous-jacent** : la lambda incarne une forme minimale d'**inversion de contrôle** — elle permet à une fonction d'ordre supérieur (`sorted`, `map`, un champ Django, un endpoint FastAPI) de rester générique et réutilisable, pendant que l'appelant injecte le comportement spécifique au dernier moment. C'est le même principe que le pattern *Strategy*, sans la cérémonie d'une classe.

La limite architecturale à retenir : dès que ce comportement injecté grandit (plusieurs lignes, besoin de tests unitaires, réutilisation à plusieurs endroits), la lambda cesse d'être un connecteur léger et devient de la dette technique cachée — il faut remonter vers une fonction `def` nommée.

---

## Post LinkedIn

**Accroche**
Une ligne de code qui semble anodine... et qui peut coûter 100x en performance si on l'utilise au mauvais endroit. Parlons des `lambda` en Python.

**Problème**
On apprend souvent la `lambda` comme "une fonction en plus court". Faux départ. Son vrai rôle : permettre d'injecter un comportement dans une fonction générique (`sorted`, `map`, un champ Django, un pipeline pandas) sans créer une fonction nommée qui ne sert qu'une fois.

**Code**
```python
# Trier une liste de produits par prix, puis par stock décroissant
produits_tries = sorted(produits, key=lambda p: (p["prix"], -p["stock"]))

# Anti-pattern fréquent en Data Science :
df["col"].apply(lambda x: x.strip().lower())   # boucle Python, lent
df["col"].str.strip().str.lower()               # vectorisé, 10-100x plus rapide
```

**Impact Architecture**
La `lambda` est une forme minimale d'inversion de contrôle : elle garde vos fonctions génériques génériques, et laisse l'appelant injecter le comportement spécifique au dernier moment (le même principe que le pattern Strategy, sans la classe). Mais dans un pipeline pandas ou PySpark, ce même outil peut devenir un goulot d'étranglement si on l'utilise là où une opération vectorisée existe.

Règle simple à appliquer en revue de code : callback court, immédiat, non réutilisé → `lambda`. Sinon → `def`.

#Python #SoftwareEngineering #DataEngineering #CleanCode

---

## Post Facebook

**Accroche**
Petit test : sais-tu vraiment à quoi sert une `lambda` en Python, au-delà de "une fonction sur une ligne" ?

**Problème**
Beaucoup de gens apprennent la lambda comme un raccourci d'écriture. En vrai, son intérêt n'est pas la brièveté — c'est de pouvoir "passer un comportement" à une fonction qui en a besoin, juste pour un instant, sans polluer son code avec une fonction qui ne sert qu'une seule fois.

**Code**
```python
nombres = [1, 2, 3, 4, 5, -1, -3]
positifs_au_cube = list(map(lambda x: x**3, filter(lambda x: x > 0, nombres)))
print(positifs_au_cube)  # [1, 8, 27, 64, 125]
```

**Impact Architecture**
On la retrouve partout dans l'écosystème Python : pour trier des données (`sorted`), pour donner une valeur par défaut calculée plus tard dans Django, pour transformer une colonne dans pandas, ou pour distribuer un calcul sur un cluster avec PySpark. Le point commun : c'est toujours un petit connecteur entre un outil générique et un besoin très précis — jamais la logique centrale d'une application.

À retenir : si ça dépasse une ligne ou que tu dois le réutiliser ailleurs, ce n'est plus le job d'une lambda — c'est le moment de passer à une vraie fonction `def`.

---

## Script TikTok (60 secondes)

**[0-8s] Hook visuel**
Plan serré sur un écran de code. On tape `sorted(produits, key=lambda p: ...)`. Voix off : *"Cette ligne cache le vrai pouvoir des lambdas — et 90% des tutos se trompent dessus."*

**[8-20s] Problème**
Cut vers un schéma simple : une boîte "fonction générique" (`sorted`, `map`, `filter`) avec un port vide marqué "?", et une boîte "ton besoin" (trier par prix). Voix off : *"Une lambda, ce n'est pas 'une fonction en plus court'. C'est l'adaptateur entre une fonction générique qui attend un comportement... et ton besoin précis, sur le moment."*

**[20-45s] Démo**
Écran partagé code + résultat, 2 exemples rapides :
```python
sorted(produits, key=lambda p: p["prix"])
df["col"].apply(lambda x: x.strip())   # ⚠️ lent en pandas
```
Voix off : *"Dans `sorted`, parfait, c'est jetable et local. Dans pandas par contre — attention, une lambda dans `.apply()` peut être 100x plus lente qu'une opération vectorisée native."*

**[45-55s] Call-to-action**
Texte à l'écran : *"Règle simple : court + jetable → lambda. Réutilisé ou testé → def."*
Voix off : *"Sauvegarde cette vidéo la prochaine fois que t'hésites entre les deux."*

**[55-60s]**
Logo / mention du compte + *"Suis-moi pour du Python niveau senior, sans blabla."*
