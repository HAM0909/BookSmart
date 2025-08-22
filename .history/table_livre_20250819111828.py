import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os


load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")


try:
    conn = psycopg2.connect(
        dbname="",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    
    cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [DB_NAME])
    exists = cur.fetchone()
    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"Base de données '{DB_NAME}' créée avec succès.")
    else:
        print(f"Base de données '{DB_NAME}' existe déjà.")

    cur.close()
    conn.close()

except Exception as e:
    print("Erreur lors de la création de la base :", e)
    exit()


try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    
    create_table_query = """
    CREATE TABLE IF NOT EXISTS livres (
        id SERIAL PRIMARY KEY,
        titre TEXT,
        description TEXT,
        prix NUMERIC,
        disponibilite BOOLEAN,
        image TEXT,
        note NUMERIC,
        lang TEXT
    );
    """
    cur.execute(create_table_query)
    conn.commit()
    print("Table 'livres' créée avec succès.")

    cur.close()
    conn.close()

except Exception as e:
    print("Erreur lors de la création de la table :", e)

