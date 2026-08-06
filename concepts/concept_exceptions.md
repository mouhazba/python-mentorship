# Gestion des exceptions : `raise` / `try-except`

Python gère les erreurs via un mécanisme d'**exceptions** : plutôt que de faire remonter des codes d'erreur (comme en C), une fonction qui rencontre une situation anormale **lève** (`raise`) un objet exception, qui interrompt immédiatement le flot normal d'exécution et remonte la pile d'appels jusqu'à ce qu'un bloc `try/except` la **capture**, ou jusqu'à ce que le programme plante si personne ne la capture. C'est le principe **EAFP** (*Easier to Ask Forgiveness than Permission*), idiomatique en Python : on tente l'opération et on gère l'échec, plutôt que de tout vérifier au préalable (LBYL, *Look Before You Leap*).

**Syntaxe :**

```python
try:
    resultat = 10 / 0
except ZeroDivisionError as e:
    print(f"Erreur : {e}")
else:
    print("Aucune exception -> exécuté seulement si le try réussit")
finally:
    print("Toujours exécuté, exception ou pas")
```

## Exemple 1 — `raise` : signaler une erreur explicitement

Une fonction doit lever une exception dès qu'elle ne peut pas garantir son contrat, plutôt que de retourner une valeur ambiguë (`None`, `-1`...) que l'appelant pourrait oublier de vérifier :

```python
class SoldeInsuffisantError(Exception):
    """Levée quand un retrait dépasse le solde disponible."""
    pass

def retirer(solde: float, montant: float) -> float:
    if montant <= 0:
        raise ValueError(f"Le montant doit être positif, reçu : {montant}")
    if montant > solde:
        raise SoldeInsuffisantError(
            f"Retrait de {montant} refusé, solde disponible : {solde}"
        )
    return solde - montant

try:
    retirer(100, 150)
except SoldeInsuffisantError as e:
    print(f"Opération refusée : {e}")
except ValueError as e:
    print(f"Entrée invalide : {e}")
```

Définir sa propre classe d'exception (héritant de `Exception`) permet à l'appelant de distinguer précisément le type d'erreur, au lieu de parser un message texte.

## Exemple 2 — chaînage d'exceptions avec `raise ... from`

Quand une exception bas niveau est attrapée puis re-levée sous une forme plus parlante pour l'appelant, `raise ... from` conserve la cause originale dans la trace, au lieu de la masquer :

```python
def charger_config(chemin: str) -> dict:
    try:
        with open(chemin) as f:
            import json
            return json.load(f)
    except FileNotFoundError as e:
        raise RuntimeError(f"Configuration introuvable : {chemin}") from e
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Configuration invalide : {chemin}") from e

try:
    charger_config("config.json")
except RuntimeError as e:
    print(e)
    print(f"Cause originale : {e.__cause__!r}")
```

La trace affichée contiendra à la fois la `FileNotFoundError` d'origine ("*The above exception was the direct cause of the following exception*") et la `RuntimeError` levée — un débogage bien plus riche qu'un simple `raise RuntimeError(...)` qui perdrait le contexte.

## Points clés

- **`except` doit être le plus spécifique possible.** Capturer une classe d'exception précise (`ZeroDivisionError`) plutôt que sa base générique (`Exception`) évite de masquer des bugs qui n'ont rien à voir avec le cas géré.
- **`else`** s'exécute uniquement si le bloc `try` n'a levé aucune exception ; utile pour séparer le code "risqué" du code qui dépend de sa réussite.
- **`finally`** s'exécute toujours (exception levée, capturée, ou non), typiquement pour libérer une ressource (fichier, connexion, verrou) — mais un `with` (context manager) est presque toujours préférable pour ça.
- **Une exception personnalisée hérite de `Exception`**, jamais de `BaseException` directement (réservée à `SystemExit`, `KeyboardInterrupt`, etc., qu'on ne veut presque jamais intercepter).

## Pièges à éviter

- **`except:` nu (sans type)** attrape absolument tout, y compris `KeyboardInterrupt` et `SystemExit` — il devient impossible d'interrompre le programme avec Ctrl+C proprement. Toujours préciser au moins `except Exception:`.
- **Avaler une exception silencieusement** (`except Exception: pass`) fait disparaître l'erreur sans laisser de trace, rendant le débogage quasi impossible. Logger au minimum le message, ou ne pas capturer du tout.
- **`raise NouvelleErreur(...)` sans `from e`** à l'intérieur d'un `except` masque la cause originale dans la trace (Python affiche quand même "*During handling of the above exception*", mais `from e` est plus explicite et lie `__cause__`). Utiliser `raise ... from None` uniquement si l'on veut délibérément cacher la cause.
- **Confondre `raise` et `raise e`** dans un bloc `except` : `raise` seul relève l'exception courante avec sa trace d'origine intacte ; `raise e` reconstruit une nouvelle trace à partir de ce point, ce qui perd l'information de la ligne où l'erreur a réellement eu lieu.
- **Utiliser les exceptions pour du contrôle de flux normal** (ex: lever une exception à chaque itération de boucle pour tester une condition fréquente) est coûteux en performance et nuit à la lisibilité — les exceptions doivent rester réservées aux cas réellement exceptionnels.
