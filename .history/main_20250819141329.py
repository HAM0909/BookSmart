from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="Réserver un livre")

# Connexion à la base (déjà créée)
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=RealDictCursor
    )

@app.post("/api/reservations")
def reserver_livre(id_livre: int, id_adherent: int):
    conn = get_db()
    cur = conn.cursor()

    try:
        # Vérifier si le livre existe
        cur.execute("SELECT stock FROM livres WHERE id = %s", (id_livre,))
        livre = cur.fetchone()
        if not livre:
            raise HTTPException(status_code=404, detail="Livre non trouvé")

    
        cur.execute("""
            SELECT * FROM reservations 
            WHERE id_livre = %s AND id_adherent = %s AND statut = 'active'
        """, (id_livre, id_adherent))
        existe = cur.fetchone()
        if existe:
            return {"success": False, "message": "Déjà réservé"}

        
        if livre["stock"] <= 0:
            return {"success": False, "message": "Pas disponible"}

        
        cur.execute("""
            INSERT INTO reservations (id_adherent, id_livre, statut)
            VALUES (%s, %s, 'active')
        """, (id_adherent, id_livre))

        
        cur.execute("UPDATE livres SET stock = stock - 1 WHERE id = %s", (id_livre,))

        conn.commit()
        return {"success": True, "message": "Réservation réussie !"}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")

    finally:
        cur.close()
        conn.close()