
except Exception as e:
    print("Erreur de connexion au serveur :", e)
    exit()


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
