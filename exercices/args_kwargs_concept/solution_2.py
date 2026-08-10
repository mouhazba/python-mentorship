#Exercice 2 — Wrapper de journalisation avec `*args` et `**kwargs
def avec_journalisation(fonction, *args, **kwargs):
    #avant execution
    print(f"Appel de {fonction.__name__} avec args={args}, kwargs={kwargs}")
    try:
        #Execution
        rslt = fonction(*args, **kwargs)
    except Exception as e:
        print(e)
        raise e
    else:
        #Apres Execution
        print(rslt)
        return rslt

def statistiques(*valeurs: float) -> dict:
    if not valeurs:
        raise ValueError("pas de `min`/`max` sur une séquence vide")
    min_v = min(valeurs)
    max_v = max(valeurs)
    sum_v = sum(valeurs)
    moy_v = sum_v/len(valeurs)
    return {"min": min_v, "max": max_v, "moyenne": moy_v, "somme": sum_v}

try:
    rp = avec_journalisation(statistiques, 1, 3, 4)
except Exception as e:
    if e.__cause__ is not None:
        print(f"Cause originale : {e.__cause__!r}: ")

try:
    rp = avec_journalisation(statistiques, )
except Exception as e:
    if e.__cause__ is not None:
        print(f"Cause originale : {e.__cause__!r}: ")


def diviser(numerateur, denominateur, precision=2):
    """Effectue une division avec arrondi et lève une exception si le dénominateur vaut 0."""
    if denominateur == 0:
        raise ValueError("Le dénominateur ne peut pas être égal à zéro.")
    return round(numerateur / denominateur, precision)

try:
    rp = avec_journalisation(diviser, 10, 3, precision=3)
except Exception as e:
    if e.__cause__ is not None:
        print(f"Cause originale : {e.__cause__!r}: ")


try:
    rp = avec_journalisation(diviser, 10, 0, precision=3)
except Exception as e:
    if e.__cause__ is not None:
        print(f"Cause originale : {e.__cause__!r}: ")


