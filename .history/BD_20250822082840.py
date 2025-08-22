import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from stop_words import get_stop_words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

required_vars = [DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]
if not all(required_vars):
    print("[ERREUR] Variables d'environnement manquantes!")
    print("Vérifiez votre fichier .env")
    exit(1)

def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

try:
    from urllib.parse import quote_plus
    password_encoded = quote_plus(DB_PASSWORD)
    engine = create_engine(f"postgresql+psycopg2://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

    with engine.connect() as test_conn:
        print("[OK] Connexion SQLAlchemy réussie !")

except Exception as e:
    print(f"[ERREUR] Erreur de connexion : {e}")
    print(f"USER: {DB_USER}, HOST: {DB_HOST}, PORT: {DB_PORT}, DBNAME: {DB_NAME}")
    print("Vérifiez vos paramètres de connexion dans le fichier .env")
    exit(1)

try:
    data = pd.read_sql("SELECT id, titre, description, prix, disponibilite, image, note, lang FROM livres;", engine)
    print(f"[INFO] Nombre de livres chargés : {len(data)}")

    if len(data) == 0:
        print("[ATTENTION] Aucune donnée trouvée dans la table 'livres'")
        print("Assurez-vous d'avoir inséré des données dans la table")
        exit(1)

except Exception as e:
    print(f"[ERREUR] Erreur lors du chargement des données : {e}")
    print("Vérifiez que la table 'livres' existe et contient des données")
    exit(1)

print("[INFO] Préparation du modèle ML...")
stop_fr = set(get_stop_words("french"))
stop_en = set(get_stop_words("english"))
stop_all = list(set(stop_en).union(set(stop_fr)))

vectoriseur = TfidfVectorizer(stop_words=stop_all)
X = vectoriseur.fit_transform(data['description'].fillna(''))

similarite = cosine_similarity(X, X)

joblib.dump(similarite, "similarite_livres.pkl")
joblib.dump(vectoriseur, "vectoriseur.pkl")
joblib.dump(data, "data_livres.pkl")
print("[OK] Modèles sauvegardés!")

def recommander(titre, n=5):
    if titre not in data['titre'].values:
        return {"titre": titre, "recommandations": [], "msg": "Livre non trouvé"}

    idx = data[data['titre'] == titre].index[0]
    scores = list(enumerate(similarite[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    scores = scores[1:n+1]

    suggestions = data.iloc[[s[0] for s in scores]]
    recommandations = suggestions[['titre', 'prix', 'note', 'disponibilite']].to_dict(orient='records')

    return {"titre": titre, "recommandations": recommandations}

if len(data) > 0:
    exemple_titre = data['titre'].iloc[0]
    exemple = recommander(exemple_titre, 3)
    print(f"[INFO] Exemple de recommandations pour '{exemple_titre}':")
    print(exemple)
else:
    print("[ERREUR] Aucune donnée disponible pour tester les recommandations")