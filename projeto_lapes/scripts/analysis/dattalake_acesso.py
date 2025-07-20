import duckdb
import functools


user_roles = {
    "carlos": "scientist",
    "ana": "analyst",
    "joao": "engineer",
}


con = duckdb.connect(database="/mnt/data/meu_datalake.duckdb", read_only=False)



def require_role(*allowed_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(usuario, *args, **kwargs):
            role = user_roles.get(usuario)
            if role not in allowed_roles:
                raise PermissionError(f" acesso negado para {usuario} com papel '{role}'.")
            print(f"acesso concedido para {usuario} ({role})")
            return func(usuario, *args, **kwargs)
        return wrapper
    return decorator



@require_role("engineer", "scientist")
def acessar_bronze(usuario):
    print("lendo camada Bronze...")
    return con.execute("SELECT * FROM read_parquet('/mnt/data/bronze_pacientes.parquet') LIMIT 5").df()



@require_role("scientist")
def acessar_silver(usuario):
    print(" lendo camada Silver...")
    return con.execute("SELECT * FROM read_parquet('/mnt/data/silver_pacientes.parquet') LIMIT 5").df()



@require_role("analyst", "scientist")
def acessar_gold(usuario):
    role = user_roles[usuario]

    if role == "analyst":
        print("modo restrito: ocultando colunas sensiveis...")
        return con.execute("""
            SELECT "Finding Labels", "Faixa Etária"
            FROM read_parquet('/mnt/data/gold_pacientes.parquet')
            LIMIT 5
        """).df()
    else:
        print("modo completo: acesso total a camada gold.")
        return con.execute("SELECT * FROM read_parquet('/mnt/data/gold_pacientes.parquet') LIMIT 5").df()