import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

data = pd.read_sql("SELECT id, titre, description, prix, disponibilite, image, note, lang FROM livres;", engine)




