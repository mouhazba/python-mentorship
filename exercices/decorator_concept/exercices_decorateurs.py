import inspect
from functools import wraps

def log_appel(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"--- Appel de : {func.__name__}  ---")
        print(f"Arguments positionnels: {args}")
        print(f"Arguments nommes: {kwargs}")
        valeur_retournee = func(*args, **kwargs)
        print(f"Valeur retournee: {valeur_retournee} \n")

        return valeur_retournee
    return wrapper


@log_appel
def carre_nombre(n):
    return n**2

carre_nombre(4)


@log_appel
def calcul_tax(n, imposition=0.18):
    return f"Montant {n} est imposable a {n*imposition}"

calcul_tax(500, imposition=0.15)

'''
--- Appel de : calcul_tax  ---
Arguments positionnels: (500,)
Arguments nommes: {'imposition': 0.15}
Valeur retournee: Montant 500 est imposable a 75.0 

'''

def requiert_role(role):
    def decorateur_login(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = inspect.signature(func).bind(*args, **kwargs)
            user = bound_args.arguments.get('user')
            user_role = user.get('role') if user else None
            if role != user_role:
                raise PermissionError("Permission Denied")
            return func(*args, **kwargs)
        return wrapper

    return decorateur_login


@requiert_role('admin')
def suppression_bdd(user):
    return "suppression de base de donnees"

print(suppression_bdd({"nom": "Alice", "role": "admin"}))

