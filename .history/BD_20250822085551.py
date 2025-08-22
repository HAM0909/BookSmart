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

# Load environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Verify all required environment variables are set
required_vars = [DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]
if not all(required_vars):
    print("[ERREUR] Variables d'environnement manquantes!")
    print("Vérifiez votre fichier .env")
    exit(1)

print(f"[INFO] Connexion à la base de données: {DB_NAME}@{DB_HOST}:{DB_PORT}")

try:
    # Create SQLAlchemy engine
    from urllib.parse import quote_plus
    password_encoded = quote_plus(DB_PASSWORD)
    engine = create_engine(
        f"postgresql+psycopg2://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Test the connection
    with engine.connect() as test_conn:
        print("[OK] Connexion SQLAlchemy réussie!")

    # Debug: List all tables in the database
    tables = pd.read_sql("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public';
    """, engine)
    print("[DEBUG] Tables dans la base de données:", tables['table_name'].tolist())

    # Debug: Verify 'livres' table exists
    livres_exists = pd.read_sql("""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_name = 'livres'
        );
    """, engine)
    print("[DEBUG] La table 'livres' existe:", livres_exists.iloc[0, 0])

    # Debug: Show columns in 'livres' table
    columns = pd.read_sql("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'livres';
    """, engine)
    print("[DEBUG] Colonnes dans 'livres':")
    print(columns)

    # Load data from 'livres' table (without 'stock' column)
    data = pd.read_sql("""
        SELECT id, titre, description, prix, disponibilite, image, note, lang
        FROM livres;
    """, engine)

    print(f"[INFO] Nombre de livres chargés: {len(data)}")

    if len(data) == 0:
        print("[ERREUR] La table 'livres' est vide. Veuillez insérer des données.")
        print("Exemple de commande SQL pour insérer des données:")
        print("INSERT INTO livres (titre, description, prix, disponibilite, image, note, lang) VALUES")
        print("('Le Petit Prince', 'Un livre sur un prince...', 9.99, TRUE, 'petitprince.jpg', 4.8, 'fr');")
        exit(1)

    # Show sample data for verification
    print("[DEBUG] Échantillon de données:")
    print(data.head())

    # Prepare ML model
    print("[INFO] Préparation du modèle ML...")
    stop_fr = set(get_stop_words("french"))
    stop_en = set(get_stop_words("english"))
    stop_all = list(set(stop_en).union(set(stop_fr)))

    # Use 'description' for TF-IDF vectorization
    vectoriseur = TfidfVectorizer(stop_words=stop_all)
    X = vectoriseur.fit_transform(data['description'].fillna(''))

    # Calculate cosine similarity
    similarite = cosine_similarity(X, X)

    # Save models to disk
    joblib.dump(similarite, "similarite_livres.pkl")
    joblib.dump(vectoriseur, "vectoriseur.pkl")
    joblib.dump(data, "data_livres.pkl")
    print("[OK] Modèles sauvegardés!")

    # Test recommendation with first book
    if len(data) > 0:
        exemple_titre = data['titre'].iloc[0]
        print(f"[INFO] Exemple de recommandation pour: '{exemple_titre}'")

        # Simple recommendation function (for testing)
        def recommander(titre, n=3):
            if titre not in data['titre'].values:
                return {"error": "Livre non trouvé"}

            idx = data[data['titre'] == titre].index[0]
            scores = list(enumerate(similarite[idx]))
            scores = sorted(scores, key=lambda x: x[1], reverse=True)
            scores = scores[1:n+1]  # Exclude the book itself

            recommandations = []
            for i, score in scores:
                book = data.iloc[i]
                recommandations.append({
                    "titre": book['titre'],
                    "note": book['note'],
                    "similarity": score
                })

            return {
                "livre": titre,
                "recommandations": recommandations