# Exercice 2 — Traitement résilient d'une liste avec `try/except/else/finally`
# Erreur personnalisee

import logging

logging.basicConfig(
    #filename='app_execution.log',
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class SoldeInsuffisantError(Exception):
    pass

def traiter_transactions(transactions: list[dict]) -> dict:
    erreurs = []
    solde = 0
    transaction_traitee = 0
    try:
        for transaction in transactions:
            try:
                montant = transaction['montant']
                type_transaction = transaction['type']
                if not isinstance(montant, (int, float)) or isinstance(montant, bool) or montant <= 0: # exclu True equivalent a 1
                    raise ValueError(f"Valeur incorrecte : {montant!r}")
                if type_transaction == 'debit' and montant > solde:
                    raise SoldeInsuffisantError(f"Solde insuffisant : {solde}")
            except (ValueError, SoldeInsuffisantError) as e:
                erreurs.append(e)
            else:
                if type_transaction == 'credit':
                    solde += montant
                elif type_transaction == 'debit':
                    solde -= montant
                transaction_traitee += 1
    finally:
        logging.info(f"Nombre de transactions traitées : {transaction_traitee}")

    return {"solde_final": solde, "erreurs": erreurs}


transactions = [
    {'montant': 1000, 'type': 'credit'},
    {'montant': -100, 'type': 'debit'},
    {'montant': "abc", 'type': 'credit'},
    {'montant': 500, 'type': 'debit'},
    {'montant': 600, 'type': 'debit'},
]

tran = traiter_transactions(transactions)
print(tran)