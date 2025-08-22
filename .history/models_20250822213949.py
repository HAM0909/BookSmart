from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from BD import Base
from datetime import datetime

class Livre(Base):
    __tablename__ = "livres"
    id = Column(Integer, primary_key=True)
    titre = Column(String, nullable=False)
    description = Column(String)
    prix = Column(Numeric(10,2))
    disponibilite = Column(Boolean, default=True)
    image_url = Column(String)
    note = Column(Numeric(3,1), default=0.0)
    lang = Column(String(2))
    stock = Column(Integer, default=1)

class Emprunt(Base):
    __tablename__ = "emprunts"
    id = Column(Integer, primary_key=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id"))
    id_livre = Column(Integer, ForeignKey("livres.id"))
    date_emprunt = Column(DateTime, default=datetime.utcnow)
    date_retour_prevue = Column(DateTime, nullable=False)
    date_retour_effectif = Column(DateTime, nullable=True)
    
    livre = relationship("Livre")
