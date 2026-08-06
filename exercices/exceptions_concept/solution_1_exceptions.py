# Exercie 1 — raise / try-except

# Erreur Peronalisee
class AgeInvalideError(Exception):
    pass

def analyser_age(valeur: str) -> int:
    # 1. Essayer la conversion en entier
    try:
        age = int(valeur)
    except ValueError as e:
        # Chaînage de l'erreur d'origine avec 'from e'
        raise AgeInvalideError(f"'{valeur}' conversion impossible.") from e

    # 2. Vérification des bornes sur l'entier obtenu
    if age < 0 or age > 130:
        raise AgeInvalideError(f"valeur ({age}) hors bornes 0<age<130 .")

    return age

age_str = ["25", "-3", "abc", "200", "42"]
for age in age_str:
    try:
        res = analyser_age(age)
        print(f"Succès : '{age}' -> {res} ans")
    except AgeInvalideError as e:
        print(e)
        if e.__cause__ is not None:
            print(f"Cause originale : {e.__cause__!r}: ")
