# Exercices — décorateurs

## Exercice 1 — Décorateur de journalisation

Écris un décorateur `@log_appel` qui, à chaque appel de la fonction décorée, affiche :

1. le nom de la fonction appelée,
2. les arguments positionnels et nommés reçus,
3. la valeur retournée.

Utilise `*args`, `**kwargs` et `functools.wraps` pour que le décorateur reste générique et préserve les métadonnées de la fonction d'origine. Teste-le sur au moins deux fonctions différentes (signatures différentes).

## Exercice 2 — Décorateur paramétré de contrôle d'accès

Écris un décorateur `@requiert_role(role)` qui prend un paramètre (ex: `"admin"`) et vérifie, avant d'exécuter la fonction décorée, qu'un utilisateur passé en argument possède ce rôle.

- Si l'utilisateur n'a pas le rôle requis, lève une `PermissionError` (la fonction décorée ne doit pas s'exécuter).
- Sinon, exécute normalement la fonction et retourne son résultat.

Simule un utilisateur avec un dictionnaire (`{"nom": "Alice", "role": "admin"}`) ou une petite classe, et teste le décorateur avec un utilisateur autorisé et un utilisateur non autorisé.
