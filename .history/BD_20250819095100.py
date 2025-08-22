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



vectoriseur = TfidfVectorizer(stop_words=stop_words)
X = vectoriseur.fit_transform(data['description'])

similarite = cosine_similarity(X, X)


joblib.dump(similarite, "similarite_livres.pkl")
joblib.dump(vectoriseur, "vectoriseur.pkl")
joblib.dump(data, "data_livres.pkl")



def recommander(titre, n=5):
    if titre not in data['titre'].values:
        return []
    
    idx = data.index[data['titre'] == titre][0]
    scores = list(enumerate(similarite[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = [s for s in scores if s[0] != idx][:n]
    
    suggestions = data.iloc[[s[0] for s in scores]]
    return suggestions[['titre', 'prix', 'note', 'disponibilite']].to_dict(orient='records')


exemple = recommander("Titre d'exemple", 3)
print(exemple)










