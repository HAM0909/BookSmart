from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- Pour créer un emprunt ---
class EmpruntCreate(BaseModel):
    id_adherent: int
    id_livre: int
    date_retour_prevue: datetime

# --- Pour afficher un emprunt ---
class EmpruntResponse(BaseModel):
    id: int
    id_adherent: int
    id_livre: int
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effectif: Optional[datetime] = None

    class Config:
        from_attributes = True  # Compatible SQLAlchemy

# --- Pour enregistrer un retour ---
class RetourBase(BaseModel):
    id_emprunt: int
    date_retour_effectif: datetime
