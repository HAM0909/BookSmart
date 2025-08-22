
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
