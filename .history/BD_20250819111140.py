import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from stop_words import get_stop_words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

load_dotenv()


USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")


try:
    # Pour les mots de passe avec caractères spéciaux, il faut les encoder dans l'URL
    from urllib.parse import quote_plus
    
    # Encoder le mot de passe pour l'URL SQLAlchemy
    password_encoded = quote_plus(PASSWORD)
    
    # Créer l'engine SQLAlchemy avec le mot de passe encodé
    engine = create_engine(f"postgresql+psycopg2://{USER}:{password_encoded}@{HOST}:{PORT}/{DBNAME}")
conn = psycopg2.connect(
    dbname="livres_db",
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)
conn.autocommit = True
cur = conn.cursor()

cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DBNAME}';")
exists = cur.fetchone()

if not exists:
    cur.execute(f"CREATE DATABASE {DBNAME};")
    print(f" Base {DBNAME} créée avec succès")
else:
    print(f" Base {DBNAME} existe déjà")

cur.close()
conn.close()





data = pd.read_sql("SELECT id, titre, description, prix, disponibilite, image, note, lang FROM livres;", engine)

print("Nombre de livres chargés :", len(data))

stop_fr = set(get_stop_words("french"))
stop_en = set(get_stop_words("english"))

stop_all = list(set(stop_en).union(set(stop_fr)))


vectoriseur = TfidfVectorizer(stop_words=stop_all)
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










