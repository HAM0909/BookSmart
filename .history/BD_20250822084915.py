import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine
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

print(f"[DEBUG] Connecting to DB: {DB_NAME} as {DB_USER}@{DB_HOST}:{DB_PORT}")

required_vars = [DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]
if not all(required_vars):
    print("[ERREUR] Variables d'environnement manquantes!")
    exit(1)

try:
    from urllib.parse import quote_plus
    password_encoded = quote_plus(DB_PASSWORD)
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    with engine.connect() as test_conn:
        print("[OK] Connexion SQLAlchemy réussie!")

    # Debug: List tables
    tables = pd.read_sql("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';", engine)
    print("[DEBUG] Tables in database:", tables['table_name'].tolist())

    # Debug: Check if 'livres' exists
    livres_exists = pd.read_sql("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'livres');", engine)
    print("[DEBUG] 'livres' table exists:", livres_exists.iloc[0, 0])

    # Load data with all columns (including stock)
    data = pd.read_sql("""
        SELECT id, titre, description, prix, disponibilite, image, note, lang, stock
        FROM livres;
    """, engine)

    print(f"[INFO] Nombre de livres chargés: {len(data)}")
    if len(data) == 0:
        print("[ERREUR] La table 'livres' est vide. Veuillez insérer des données.")
        exit(1)

    # Debug: Show columns and sample data
    print("[DEBUG] Columns in 'livres':", data.columns.tolist())
    print("[DEBUG] Sample data:\n", data.head())

    # Rest of your ML code...
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

except Exception as e:
    print(f"[ERREUR] {e}")
    exit(1)