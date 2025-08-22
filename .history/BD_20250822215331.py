# BD.py
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Boolean, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Base déclarative SQLAlchemy
Base = declarative_base()

# Définition du modèle Livre
class Livre(Base):
    __tablename__ = "livres"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(Text, nullable=False)
    description = Column(Text)
    prix = Column(Numeric(10, 2))
    disponibilite = Column(Boolean, default=True)
    image_url = Column(String)
    note = Column(Numeric(3, 1), default=0.0)
    lang = Column(String(2))
    stock = Column(Integer, default=1)

# Création du moteur et session
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Fonction pour créer toutes les tables
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("[INFO] Tables créées avec succès")
    except SQLAlchemyError as e:
        print(f"[ERREUR] Impossible de créer les tables: {e}")

# Dépendance FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

