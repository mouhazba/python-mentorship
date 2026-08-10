 #solution 1 Exercice 1 — Agrégateur générique avec `*args`
def statistiques(*valeurs: float) -> dict:
    if not valeurs:
        raise ValueError("pas de `min`/`max` sur une séquence vide")
    min_v = min(valeurs)
    max_v = max(valeurs)
    sum_v = sum(valeurs)
    moy_v = sum_v/len(valeurs)
    return {"min": min_v, "max": max_v, "moyenne": moy_v, "somme": sum_v}

try:
    print(statistiques(1, 2, 3))
except ValueError as e:
    print(e)

try:
    print(statistiques(42))
except ValueError as e:
    print(e)

try:
    print(statistiques())
except ValueError as e:
    print(e)
    

def statistiques_ponderees(poids: list[float], *valeurs: float) -> float:
    if not poids or not valeurs:
        raise ValueError("pas de poids pondures sur une sequence vide")
    if len(poids) != len(valeurs):
        raise ValueError("La taille de `poids` doit correspondre au nombre de valeurs")
    sum_poids = sum(poids)
    if sum_poids == 0:
        raise ZeroDivisionError("Division par zero impossible")
    cal = sum(v * p for v, p in zip(valeurs, poids)) / sum_poids
    return cal

poids = [2.3, 4.5, 5.9]

try:
    pp = statistiques_ponderees(poids, 1, 2, 3)
    print(f"Poids pondere de {poids} = {pp}")
except (ValueError, ZeroDivisionError) as e:
    print(e)

try:
    pp = statistiques_ponderees(poids, 1, 2, 3, 4)
    print(f"Poids pondere de {poids} = {pp}")
except (ValueError, ZeroDivisionError) as e:
    print(e)

# resultat des deux fonctions:
'''
{'min': 1, 'max': 3, 'moyenne': 2.0, 'somme': 6}
{'min': 42, 'max': 42, 'moyenne': 42.0, 'somme': 42}
pas de `min`/`max` sur une séquence vide
Poids pondere de [2.3, 4.5, 5.9] = 2.2834645669291342
Taille de poid doit etre different de nombre valeurs
'''