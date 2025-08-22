from fastapi import APIRouter, Depends
from BD import get_db
from typing import List
from tablaux import EmpruntResponse  # si besoin pour les emprunts
import psycopg2

router = APIRouter(prefix="/api", tags=["livres"])

@router.get("/livres")
def get_livres(search: str = "", db=Depends(get_db)):
    """
    Retourne la liste des livres filtrés par titre si search est fourni.
    """
    cur = db.cursor()
    try:
        if search:
            cur.execute(
                "SELECT id, titre, image_url, stock FROM livres WHERE LOWER(titre) LIKE %s",
                (f"%{search.lower()}%",)
            )
        else:
            cur.execute("SELECT id, titre, image_url, stock FROM livres")
        livres = cur.fetchall()
        # Convertir le stock en disponibilité
        for livre in livres:
            livre["disponibilite"] = livre["stock"] > 0
        return livres
    finally:
        cur.close()
