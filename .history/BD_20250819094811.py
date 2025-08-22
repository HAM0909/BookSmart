import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

load_dotenv()


USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")


engine = create_engine(f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}")

data = pd.read_sql("SELECT id, titre, description, prix, disponibilite, image, note, lang FROM livres;", engine)

print("Nombre de livres chargés :", len(data))


stop_words_fr = ["le","la","les","de","des","un","une","et","en","du","au","aux","ce","ces","dans","pour","par","sur","avec","sans","ne","pas","que","qui"]
stop_words_en = ["the","and","of","in","to","a","an","for","on","with","without","is","are","it","this","that","by","from","as","at"]
stop_words = stop_words_fr + stop_words_en


vectoriseur = TfidfVectorizer(stop_words=stop_words)
X = vectoriseur.fit_transform(data['description'])

similarite = cosine_similarity(X, X)












