from fastapi import APIRouter, HTTPException, Depends
from typing import List
from BD import get_db 
from tablaux import EmpruntResponse

# Création du router pour les emprunts
router = APIRouter(prefix="/api", tags=["emprunts"])

@router.get("/mes-emprunts", response_model=List[EmpruntResponse])
def get_mes_emprunts(adherent_id: int, db = Depends(get_db)):
    """
    Récupère la liste des emprunts pour un adhérent donné
    Paramètres : adherent_id (query parameter)
    Retourne : liste des emprunts avec titre, dates et statut
    """
    cur = db.cursor()
    
    try:
        query = """
        SELECT 
            e.id,
            l.titre,
            e.date_emprunt,
            e.date_retour_prevue,
            e.date_retour_effectif,
            CASE 
                WHEN e.date_retour_effectif IS NOT NULL THEN 'rendu'
                WHEN e.date_retour_prevue < NOW() AND e.date_retour_effectif IS NULL THEN 'en_retard'
                ELSE 'en_cours'
            END as statut
        FROM emprunts e
        JOIN livres l ON e.id_livre = l.id
        WHERE e.id_adherent = %s
        ORDER BY e.date_emprunt DESC
        """
        
        cur.execute(query, (adherent_id,))
        emprunts = cur.fetchall()
        
        return emprunts
        
    except Exception as err:
        print(f"Erreur: {err}")
        raise HTTPException(status_code=500, detail="Erreur serveur")
    finally:
        cur.close()

@router.get("/adherents/{adherent_id}/emprunts", response_model=List[EmpruntResponse])
def get_emprunts_by_adherent_id(adherent_id: int, db = Depends(get_db)):
    """
    Version RESTful : GET /api/adherents/123/emprunts
    """
    return get_mes_emprunts(adherent_id, db)