# exercice 1
import itertools
from pathlib import Path

FICHIER_LOGS = "log_exemple.txt"
def lire_erreurs_log(chemin):
    path = Path(chemin)
    if not path.exists():
        raise FileNotFoundError("Fichier introuvalbe")
    with open(chemin) as f:
        for ligne in f:
            if "ERROR" in ligne:
                yield ligne.strip()
    

# exercice 2 
def compteur(depart=0):
    valeur = depart
    while True:
        yield valeur
        valeur += 1

def filtrer_multiples(sequence, n):
    for x in sequence:
        if x % n == 0:
            yield x

def extraire_un_lot(sequence_iter, taille):
    lot = []
    for elem in sequence_iter:
        lot.append(elem)
        if len(lot) == taille:
            break
    if lot:
        yield lot

def pagine_deleguee(sequence, taille):
    seq_iter = iter(sequence)
    while True:
        yield from extraire_un_lot(seq_iter, taille)


def main():
    try:
        logs = lire_erreurs_log(FICHIER_LOGS)
        for ligne in logs:
            print(f"🚨 ALERTE : {ligne}")
        # instantiation du gen
        gen = lire_erreurs_log("log_exemple.txt")

        # premiere execution
        premieres_erreurs = list(gen)
        print(f"Premier passage : {premieres_erreurs}")

        # seconde execution
        secondes_erreurs = list(gen)
        print(f"Second passage : {secondes_erreurs}")
    except Exception as e:
        print(e)
        
    source = compteur(0)
    multiple =filtrer_multiples(source, 5)
    lots = pagine_deleguee(multiple, 3)
    quatre_premiers_lot = list(itertools.islice(lots, 4))
    print(quatre_premiers_lot)

if __name__ == "__main__":
    main()

