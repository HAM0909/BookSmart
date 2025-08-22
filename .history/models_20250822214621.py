from sqlalchemy import Column, Integer, String, Boolean, Numeric, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Adherent(Base):
    __tablename__ = "adherents"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="adherent")
    date_inscription = Column(DateTime, default=datetime.utcnow)

    emprunts = relationship("Emprunt", back_populates="adherent")
    reservations = relationship("Reservation", back_populates="adherent")

class Livre(Base):
    __tablename__ = "livres"
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String, nullable=False)
    description = Column(Text)
    prix = Column(Numeric(10,2))
    disponibilite = Column(Boolean, default=True)
    image_url = Column(String)
    note = Column(Numeric(3,1), default=0.0)
    lang = Column(String(2))
    stock = Column(Integer, default=1)

    emprunts = relationship("Emprunt", back_populates="livre")
    reservations = relationship("Reservation", back_populates="livre")

class Emprunt(Base):
    __tablename__ = "emprunts"
    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id"))
    id_livre = Column(Integer, ForeignKey("livres.id"))
    date_emprunt = Column(DateTime, default=datetime.utcnow)
    date_retour_prevue = Column(DateTime, nullable=False)
    date_retour_effectif = Column(DateTime, nullable=True)

    adherent = relationship("Adherent", back_populates="emprunts")
    livre = relationship("Livre", back_populates="emprunts")

class Reservation(Base):
    __tablename__ = "reservations"
    id = Column(Integer, primary_key=True, index=True)
    id_adherent = Column(Integer, ForeignKey("adherents.id"))
    id_livre = Column(Integer, ForeignKey("livres.id"))
    date_reservation = Column(DateTime, default=datetime.utcnow)
    statut = Column(String, default="active")

    adherent = relationship("Adherent", back_populates="reservations")
    livre = relationship("Livre", back_populates="reservations")
