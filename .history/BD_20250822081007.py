import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from stop_words import get_stop_words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """Your existing database connection function"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        cursor_factory=RealDictCursor
    )


try:
    from urllib.parse import quote_plus
    password_encoded = quote_plus("DB_PASSWORD")
    engine = create_engine(f"postgresql+psycopg2://{USER}:{password_encoded}@{HOST}:{PORT}/{DBNAME}")
    
    with engine.connect() as test_conn:
        print("Connexion SQLAlchemy réussie !")

    conn = psycopg2.connect(
        DB_NAME=livres_db,
        user=postgres,
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
        print(f"Base {DBNAME} créée avec succès")
    else:
        print(f"Base {DBNAME} existe déjà")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Erreur de connexion : {e}")
    print(f"USER: {USER}, HOST: {HOST}, PORT: {PORT}, DBNAME: {DBNAME}")
    print("Vérifiez vos paramètres de connexion dans le fichier .env")
    exit(1)


try:
    data = pd.read_sql("SELECT id, titre, description, prix, disponibilite, image, note, lang FROM livres;", engine)
    print("Nombre de livres chargés :", len(data))
    
    if len(data) == 0:
        print("Attention : Aucune donnée trouvée dans la table 'livres'")
        print("Assurez-vous d'avoir inséré des données dans la table")
        exit(1)
        
except Exception as e:
    print(f"Erreur lors du chargement des données : {e}")
    print("Vérifiez que la table 'livres' existe et contient des données")
    exit(1)

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

if len(data) > 0:
    exemple_titre = data['titre'].iloc[0]
    exemple = recommander(exemple_titre, 3)
    print(f"Exemple de recommandations pour '{exemple_titre}':")
    print(exemple)
else:
    print("Aucune donnée disponible pour tester les recommandations")