from pydantic import BaseModel
from datetime import datetime

class EmpruntCreate(BaseModel):
    id_adherent: int
    id_livre: int
    date_retour_prevue: datetime

class EmpruntResponse(EmpruntCreate):
    id: int

    class Config:
        from_attributes = True 

class RetourBase(BaseModel):
    id_emprunt: int
    date_retour_effectif: datetime


