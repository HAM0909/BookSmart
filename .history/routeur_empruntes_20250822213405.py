from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from DB import get_db
from models import Emprunt, Livre
from schemas import EmpruntCreate, RetourCreate

router = APIRouter(prefix="/api", tags=["emprunts"])

@router.post("/emprunts")
def create_emprunt(data: EmpruntCreate, db: Session = Depends(get_db)):
    """
    Enregistrer un nouvel emprunt pour un adhérent
    """
    livre = db.query(Livre).filter(Livre.id == data.id_livre).first()
    if not livre or livre.stock <= 0:
        raise HTTPException(status_code=400, detail="Livre indisponible")
    
    emprunt = Emprunt(id_adherent=data.id_adherent, id_livre=data.id_livre)
    db.add(emprunt)
    livre.stock -= 1
    db.commit()
    return {"ok": True, "msg": "Emprunt enregistré"}

@router.post("/retours")
def create_retour(data: RetourCreate, db: Session = Depends(get_db)):
    """
    Enregistrer le retour d'un emprunt
    """
    emprunt = db.query(Emprunt).filter(Emprunt.id == data.id_emprunt, Emprunt.date_retour_effectif == None).first()
    if not emprunt:
        raise HTTPException(status_code=400, detail="Emprunt introuvable ou déjà retourné")
    
    emprunt.date_retour_effectif = datetime.utcnow()
    livre = db.query(Livre).filter(Livre.id == emprunt.id_livre).first()
    livre.stock += 1
    db.commit()
    return {"ok": True, "msg": "Retour enregistré"}
