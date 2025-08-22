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

# Correction de la connexion PostgreSQL avec gestion du mot de passe spécial
try:
    # Pour les mots de passe avec caractères spéciaux, il faut les encoder dans l'URL
    from urllib.parse import quote_plus
    
    # Encoder le mot de passe pour l'URL SQLAlchemy
    password_encoded = quote_plus(PASSWORD)
    
    # Créer l'engine SQLAlchemy avec le mot de passe encodé
    engine = create_engine(f"postgresql+psycopg2://{USER}:{password_encoded}@{HOST}:{PORT}/{DBNAME}")
    
    # Test de connexion
    with engine.connect() as test_conn:
        print("Connexion SQLAlchemy réussie !")
    
    # Connexion psycopg2 pour la gestion de base (pas besoin d'encoder ici)
    conn = psycopg2.connect(
        dbname="postgres",  # Se connecter à la base par défaut d'abord
        user=USER,
        password=PASSWORD,  # Mot de passe original pour psycopg2
        host=HOST,
        port=PORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Vérifier si la base cible existe
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DBNAME}';")
    exists = cur.fetchone()

    if not exists:
        cur.execute(f"CREATE DATABASE {DBNAME};")
        print(f" Base {DBNAME} créée avec succès")
    else:
        print(f" Base {DBNAME} existe déjà")

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