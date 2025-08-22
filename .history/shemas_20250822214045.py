from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmpruntCreate(BaseModel):
    id_adherent: int
    id_livre: int

class RetourCreate(BaseModel):
    id_emprunt: int

class EmpruntResponse(BaseModel):
    id: int
    titre: str
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effectif: Optional[datetime] = None
    statut: str

    class Config:
        orm_mode = True
