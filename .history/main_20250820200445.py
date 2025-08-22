from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os


load_dotenv()

app = FastAPI(title="Book Reservation API (Réserver un livre)")


app.mount("/static", StaticFiles(directory=".", html=True))



DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")


@app.post("/api/reservations")
def reserver_un_livre(id_livre: int, id_adherent: int):
      conn = get_db()     
      cur = conn.cursor()

      print("DEBUG >> trying to reserve:", id_livre, "for user:", id_adherent)  

      try:
          
          cur.execute("SELECT stock FROM livres WHERE id = %s", (id_livre,))
          res = cur.fetchone()
          livreInfo = res 

          if livreInfo is None:
              raise HTTPException(status_code=404, detail="Livre pas trouvé !!")

          
          cur.execute("""
              SELECT * FROM reservations 
              WHERE id_livre=%s AND id_adherent=%s AND statut='active'
          """, (id_livre, id_adherent))
          existing = cur.fetchone()
          if existing:
              
              return {"ok": False, "msg": "déjà réservé mec"}

          
          stockLeft = livreInfo["stock"]
          if stockLeft <= 0:
               
               return {"ok": False, "msg": "plus de stock..."}

          
          cur.execute("""
              INSERT INTO reservations (id_adherent, id_livre, statut) 
              VALUES (%s, %s, 'active')
          """, (id_adherent, id_livre))

          
          cur.execute("UPDATE livres SET stock = stock - 1 WHERE id = %s", (id_livre,))

          conn.commit()
          print("SUCCESS: réservation OK")   
          return {"ok": True, "msg": "Réservé "}

      except Exception as err:
          conn.rollback()
          print("ERR >>>", err) 
          raise HTTPException(status_code=500, detail="internal server error (check logs)")

      finally:
          
          cur.close()
          conn.close()
          



def get_db():
     
     return psycopg2.connect(
         host=DB_HOST,
         database=DB_NAME,
         user=DB_USER,
         password=DB_PASS,
         cursor_factory=RealDictCursor
     )


--- random dead code ---
def cancel_reservation(id_resa):
    jamais fini d’implémenter
pass

print("Ce fichier est exécuté")   
