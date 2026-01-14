import os
import re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# ============================================
# CONFIG (à adapter)
# ============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Chemins vers tes fichiers générés
SQL_SCHEMA_PATH = os.path.join(BASE_DIR, "..", "02_Donnees", "Sources", "base_ventes.sql")
DIM_CLIENT_XLSX = os.path.join(BASE_DIR, "..", "02_Donnees", "Sources", "Dim_Client.xlsx")
FAIT_VENTES_XLSX = os.path.join(BASE_DIR, "..", "02_Donnees", "Sources", "Fait_Ventes.xlsx")

# Connexion MySQL (recommandé: variables d'environnement)
# PowerShell (exemple) :
# $env:DB_HOST="localhost"; $env:DB_PORT="3306"; $env:DB_NAME="ecommerce_dw"; $env:DB_USER="root"; $env:DB_PASS="password"
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "ecommerce_dw")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")

# Driver PyMySQL
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Tables cibles (doivent correspondre aux noms dans base_ventes.sql)
T_DIM_CLIENT = "Dim_Client"
T_FAIT_VENTES = "Fait_Ventes"


# ============================================
# UTILITAIRES
# ============================================

def make_engine() -> Engine:
    return create_engine(DATABASE_URL, future=True)

def read_text(path: str) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def split_sql_statements(sql: str) -> list[str]:
    """
    Découpe simple par ';' en évitant ceux dans les strings.
    Suffisant pour un DDL auto-généré.
    """
    statements = []
    buff = []
    in_string = False
    quote = None

    for ch in sql:
        if ch in ("'", '"'):
            if not in_string:
                in_string = True
                quote = ch
            elif quote == ch:
                in_string = False
                quote = None

        if ch == ";" and not in_string:
            stmt = "".join(buff).strip()
            if stmt:
                statements.append(stmt)
            buff = []
        else:
            buff.append(ch)

    last = "".join(buff).strip()
    if last:
        statements.append(last)

    return statements

def normalize_schema_for_mysql(sql: str) -> str:
    """
    Rend le SQL plus compatible MySQL.
    - supprime commentaires
    - remplace NUMERIC(x,y) -> DECIMAL(x,y)
    - TEXT ok, INT ok, DATE ok, TIMESTAMP ok
    """
    # remove -- comments
    sql = re.sub(r"--.*", "", sql)

    # numeric -> decimal
    sql = re.sub(r"\bNUMERIC\(", "DECIMAL(", sql, flags=re.IGNORECASE)

    # optionnel : IF NOT EXISTS ok, PRIMARY KEY ok
    return sql

def create_database_if_not_exists() -> None:
    """
    Création de la base si elle n'existe pas.
    On se connecte au serveur sans DB, puis CREATE DATABASE.
    """
    server_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/?charset=utf8mb4"
    engine_server = create_engine(server_url, future=True)

    with engine_server.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"))

def execute_schema(engine: Engine, schema_path: str) -> None:
    raw_sql = read_text(schema_path)
    sql = normalize_schema_for_mysql(raw_sql)
    statements = split_sql_statements(sql)

    with engine.begin() as conn:
        for stmt in statements:
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))

def read_excel(path: str, sheet: str) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, engine="openpyxl")
    # NaN -> None pour MySQL (sinon pandas envoie NaN comme float)
    df = df.replace({np.nan: None})
    return df

def truncate_table(engine: Engine, table: str) -> None:
    with engine.begin() as conn:
        # MySQL: TRUNCATE fonctionne, mais attention FK : si FK plus tard, il faudra désactiver FK checks
        conn.execute(text(f"TRUNCATE TABLE {table};"))

def upload_df(df: pd.DataFrame, table: str, engine: Engine) -> None:
    """
    Charge les données dans MySQL.
    if_exists='append' : insertion
    chunksize: batch
    """
    df.to_sql(
        name=table,
        con=engine,
        if_exists="append",
        index=False,
        chunksize=5000,
        method="multi",
    )

def count_rows(engine: Engine, table: str) -> int:
    with engine.connect() as conn:
        return int(conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar_one())


# ============================================
# MAIN
# ============================================

def main():
    print("🔧 (1) Création base si nécessaire...")
    create_database_if_not_exists()

    print("🔌 (2) Connexion MySQL...")
    engine = make_engine()

    print("🏗️ (3) Exécution du schéma base_ventes.sql...")
    execute_schema(engine, SQL_SCHEMA_PATH)

    print("📥 (4) Lecture Excel : Dim_Client + Fait_Ventes...")
    df_clients = read_excel(DIM_CLIENT_XLSX, "Dim_Client")
    df_ventes = read_excel(FAIT_VENTES_XLSX, "Fait_Ventes")

    # Optionnel mais conseillé : forcer certains types
    # df_clients["ID_Client"] = df_clients["ID_Client"].astype("Int64")
    # df_ventes["ID_Vente"] = df_ventes["ID_Vente"].astype("Int64")

    print("🧹 (5) Nettoyage/chargement : TRUNCATE puis INSERT...")
    truncate_table(engine, T_FAIT_VENTES)
    truncate_table(engine, T_DIM_CLIENT)

    # Charger dimensions d'abord, puis faits
    upload_df(df_clients, T_DIM_CLIENT, engine)
    upload_df(df_ventes, T_FAIT_VENTES, engine)

    print("✅ (6) Vérification volumes...")
    print(f"   - {T_DIM_CLIENT}: {count_rows(engine, T_DIM_CLIENT)} lignes")
    print(f"   - {T_FAIT_VENTES}: {count_rows(engine, T_FAIT_VENTES)} lignes")

    # Vérif FK logique (même si pas encore FK en DB)
    with engine.connect() as conn:
        missing = conn.execute(text(f"""
            SELECT COUNT(*)
            FROM {T_FAIT_VENTES} v
            LEFT JOIN {T_DIM_CLIENT} c ON v.ID_Client = c.ID_Client
            WHERE c.ID_Client IS NULL;
        """)).scalar_one()
    print(f"🔎 Ventes avec ID_Client absent dans Dim_Client : {int(missing)} (attendu: 0)")

    print("\n🎉 Terminé : schéma créé + Dim_Client & Fait_Ventes chargées dans MySQL.")

if __name__ == "__main__":
    main()
