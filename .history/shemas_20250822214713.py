from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmpruntBase(BaseModel):
    id_adherent: int
    id_livre: int
    date_retour_prevue: datetime

class EmpruntCreate(EmpruntBase):
    pass

class EmpruntResponse(EmpruntBase):
    id: int
    date_emprunt: datetime
    date_retour_effectif: Optional[datetime] = None

    class Config:
        orm_mode = True

class RetourBase(BaseModel):
    id_emprunt: int
    date_retour_effectif: datetime
