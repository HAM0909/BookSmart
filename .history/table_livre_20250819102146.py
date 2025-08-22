import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Charger les variables d'environnement depuis .env
load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# 1️⃣ Connexion au serveur PostgreSQL (sans sélectionner de DB)
try:
    conn = psycopg2.connect(
        dbname="postgres",  # DB par défaut pour créer une nouvelle DB
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    print("Connexion au serveur réussie !")
except Exception as e:
    print("Erreur de connexion au serveur :", e)
    exit()

# 2️⃣ Création de la base de données si elle n'existe pas
try:
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(
        sql.Identifier(DB_NAME)
    ))
    print(f"Base de données '{DB_NAME}' créée avec succès !")
except psycopg2.errors.DuplicateDatabase:
    print(f"La base de données '{DB_NAME}' existe déjà.")
except Exception as e:
    print("Erreur lors de la création de la DB :", e)

cursor.close()
conn.close()

# 3️⃣ Connexion à la base de données nouvellement créée
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print(f"Connexion à la base '{DB_NAME}' réussie !")
except Exception as e:
    print("Erreur de connexion à la DB :", e)
    exit()

# 4️⃣ Création de la table 'livres'
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

try:
    cursor.execute(create_table_query)
    conn.commit()
    print("Table 'livres' créée avec succès !")
except Exception as e:
    print("Erreur lors de la création de la table :", e)

cursor.close()
conn.close()
