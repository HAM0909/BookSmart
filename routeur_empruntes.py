from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from BD import get_db
from models import Emprunt, Livre
from schemas import EmpruntCreate, EmpruntResponse, RetourBase
from datetime import datetime

router = APIRouter(prefix="/api", tags=["emprunts"])

@router.post("/emprunts", response_model=EmpruntResponse)
def create_emprunt(emprunt: EmpruntCreate, db: Session = Depends(get_db)):
    livre = db.query(Livre).filter(Livre.id == emprunt.id_livre).first()
    if not livre:
        raise HTTPException(status_code=404, detail="Livre introuvable")
    if livre.stock <= 0:
        raise HTTPException(status_code=400, detail="Stock insuffisant")

    livre.stock -= 1
    db_emprunt = Emprunt(
        id_adherent=emprunt.id_adherent,
        id_livre=emprunt.id_livre,
        date_retour_prevue=emprunt.date_retour_prevue
    )
    db.add(db_emprunt)
    db.commit()
    db.refresh(db_emprunt)
    return db_emprunt

@router.post("/retours")
def enregistrer_retour(retour: RetourBase, db: Session = Depends(get_db)):
    emprunt = db.query(Emprunt).filter(Emprunt.id == retour.id_emprunt).first()
    if not emprunt:
        raise HTTPException(status_code=404, detail="Emprunt introuvable")
    if emprunt.date_retour_effectif:
        raise HTTPException(status_code=400, detail="Retour déjà enregistré")

    emprunt.date_retour_effectif = retour.date_retour_effectif
    livre = db.query(Livre).filter(Livre.id == emprunt.id_livre).first()
    if livre:
        livre.stock += 1

    db.commit()
    return {"message": "Retour enregistré avec succès"}
