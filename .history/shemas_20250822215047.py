# schemas.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# -------- Adhérent --------
class AdherentBase(BaseModel):
    nom: str
    email: str

class AdherentCreate(AdherentBase):
    password: str

class AdherentResponse(AdherentBase):
    id: int
    role: str
    date_inscription: Optional[datetime]

    model_config = {"from_attributes": True}  # Pydantic v2

# -------- Livre --------
class LivreBase(BaseModel):
    titre: str
    description: Optional[str] = None
    prix: Optional[float] = 0.0
    disponibilite: Optional[bool] = True
    image_url: Optional[str] = None
    note: Optional[float] = 0.0
    lang: Optional[str] = None
    stock: Optional[int] = 1

class LivreCreate(LivreBase):
    pass

class LivreResponse(LivreBase):
    id: int

    model_config = {"from_attributes": True}  # Pydantic v2

# -------- Emprunt --------
class EmpruntBase(BaseModel):
    id_adherent: int
    id_livre: int
    date_retour_prevue: datetime

class EmpruntCreate(EmpruntBase):
    pass

class EmpruntResponse(BaseModel):
    id: int
    titre: str
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effectif: Optional[datetime] = None
    statut: str

    model_config = {"from_attributes": True}  


class ReservationBase(BaseModel):
    id_adherent: int
    id_livre: int

class ReservationCreate(ReservationBase):
    pass

class ReservationResponse(ReservationBase):
    id: int
    date_reservation: datetime
    statut: str

    model_config = {"from_attributes": True}
