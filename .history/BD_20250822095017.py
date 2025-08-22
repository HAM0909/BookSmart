import pandas as pd
import numpy as np
import re
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from unidecode import unidecode

def clean_description(text):
    if pd.isna(text):
        return ""
    text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', str(text))
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def convert_price(price):
    if pd.isna(price):
        return 0.0
    if isinstance(price, str):
        price = re.sub(r'[^0-9.]', '', price)
        try:
            return float(price)
        except:
            return 0.0
    return float(price)

def convert_availability(disponibilite):
    if pd.isna(disponibilite):
        return 0
    if isinstance(disponibilite, bool):
        return 1 if disponibilite else 0
    if isinstance(disponibilite, str):
        return 1 if disponibilite.lower() in ['true', 'yes', '1', 'disponible'] else 0
    return 1 if disponibilite else 0

def convert_rating(rating):
    if pd.isna(rating):
        return 0.0
    
    rating_dict = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'un': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5
    }
    
    if isinstance(rating, str):
        rating = rating.lower().strip()
        if rating in rating_dict:
            return float(rating_dict[rating])
        try:
            return float(re.sub(r'[^0-9.]', '', rating))
        except:
            return 0.0
    try:
        return float(rating)
    except:
        return 0.0

def main():
    try:
        # Charger le fichier CSV brut
        print("[INFO] Lecture du fichier CSV brut...")
        df = pd.read_csv('livres_bruts.csv')
        print(f"[INFO] Nombre de livres avant nettoyage: {len(df)}")

        # Nettoyage des données
        print( Nettoyage des données...")
        
        
        df['description'] = df['description'].apply(clean_description)
        
        
        df['description'] = df.apply(
            lambda x: x['titre'] if pd.isna(x['description']) or len(x['description']) < 10 else x['description'],
            axis=1
        )
        
        
        df['prix'] = df['prix'].apply(convert_price)
        
        
        df['disponibilite'] = df['disponibilite'].apply(convert_availability)
        
        
        df['note'] = df['note'].apply(convert_rating)
        
        
        df.to_csv('livres_bruts.csv', index=False)
        print(" Données nettoyées sauvegardées dans livres_bruts.csv")

        
        load_dotenv()
        DB_USER = os.getenv("DB_USER")
        DB_PASSWORD = os.getenv("DB_PASSWORD")
        DB_HOST = os.getenv("DB_HOST")
        DB_PORT = os.getenv("DB_PORT")
        DB_NAME = os.getenv("DB_NAME")

        
        print("[INFO] Connexion à PostgreSQL...")
        from urllib.parse import quote_plus
        password_encoded = quote_plus(DB_PASSWORD)
        engine = create_engine(
            f"postgresql+psycopg2://{DB_USER}:{password_encoded}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )

        
        print("[INFO] Création de la table et insertion des données...")
        with engine.connect() as conn:
            
            conn.execute(text("DROP TABLE IF EXISTS livres;"))
            
            
            conn.execute(text("""
                CREATE TABLE livres (
                    id SERIAL PRIMARY KEY,
                    titre TEXT NOT NULL,
                    description TEXT,
                    prix NUMERIC(10,2),
                    disponibilite BOOLEAN,
                    image TEXT,
                    note NUMERIC(3,1),
                    lang VARCHAR(2)
                );
            """))
            
            
            conn.commit()
            
        
        df.to_sql('livres', engine, if_exists='append', index=False)
        
        
        print("[INFO] Préparation du modèle de recommandation...")
        
        
        descriptions = pd.read_sql(text("SELECT description FROM livres"), engine)
        
        
        vectorizer = TfidfVectorizer(
            stop_words=['french', 'english'],
            max_features=5000,
            ngram_range=(1, 2)
        )
        
        tfidf_matrix = vectorizer.fit_transform(descriptions['description'])
        
        
        similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
        
        
        print("[INFO] Sauvegarde des modèles...")
        joblib.dump(vectorizer, 'vectorizer.joblib')
        joblib.dump(similarity_matrix, 'similarity_matrix.joblib')
        joblib.dump(df, 'data_livres.pkl')
        
        
        print("\n=== Résumé du traitement ===")
        print(f"Nombre de livres traités: {len(df)}")
        print("Statistiques des données nettoyées:")
        print(df.describe())
        print("\nExemple de données nettoyées:")
        print(df.head())
        
        print("Traitement terminé avec succès!")

    except Exception as e:
        print(f"[ERREUR] Une erreur est survenue: {str(e)}")
        raise e

if __name__ == "__main__":
    main()