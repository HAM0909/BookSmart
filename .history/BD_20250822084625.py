import pandas as pd
import psycopg2
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from stop_words import get_stop_words
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from db import get_db  # Shared function

load_dotenv()

# Database connection (already handled by get_db())

try:
    from urllib.parse import quote_plus
    password_encoded = quote_plus(os.getenv("DB_PASSWORD"))
    engine = create_engine(
        f"postgresql+psycopg2://{os.getenv('DB_USER')}:{password_encoded}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    with engine.connect() as test_conn:
        print("[OK] Connexion SQLAlchemy réussie !")

    # Load ALL columns (including 'stock')
    data = pd.read_sql("""
        SELECT id, titre, description, prix, disponibilite, image, note, lang, stock
        FROM livres;
    """, engine)
    print(f"[INFO] Nombre de livres chargés : {len(data)}")
    print("📋 Columns:", data.columns.tolist())  # Debug
    print("📊 Sample data:\n", data.head())     # Debug

    if len(data) == 0:
        print("[ERREUR] Aucune donnée trouvée dans 'livres'!")
        exit(1)

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