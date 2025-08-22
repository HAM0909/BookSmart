import pandas as pd
import numpy as np
import re
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from urllib.parse import quote_plus

# ------------------------
# SQLAlchemy pour FastAPI
# ------------------------
load_dotenv()
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

password_encoded = quote_plus(DB_PASSWORD)
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# Fonctions de nettoyage CSV
# ------------------------
def clean_description(text):
    if pd.isna(text):
        return ""
    text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', str(text))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def convert_price(price):
    if pd.isna(price):
        return 0.0
    if isinstance(price, str):
        price = re.sub(r'[^0-9.]', '', price)
        try:
            return float(price)
        except:
            return 0.0
    return float(price)

def convert_availability(disponibilite):
    if pd.isna(disponibilite):
        return False
    if isinstance(disponibilite, bool):
        return disponibilite
    if isinstance(disponibilite, str):
        return disponibilite.lower() in ['true', 'yes',]()



