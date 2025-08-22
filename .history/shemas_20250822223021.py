# schemas.py
from pydantic import BaseModel
from datetime import datetime

# Schéma pour créer un emprunt
class EmpruntCreate(BaseModel):
    id_adherent: int
    id_livre: int
    date_retour_prevue: datetime

# Schéma pour la réponse d'un emprunt
class EmpruntResponse(EmpruntCreate):
    id: int

    class Config:
        orm_mode = True  # permet à SQLAlchemy de mapper l'objet automatiquement

# Schéma pour enregistrer un retour
class RetourBase(BaseModel):
    id_emprunt: int
    date_retour_effectif: datetime

