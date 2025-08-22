import pandas as pd
import numpy as np
import re
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from unidecode import unidecode

def clean_description(text):
    if pd.isna(text):
        return ""
    # Supprimer les caractères spéciaux mais garder les accents
    text = re.sub(r'[^a-zA-ZÀ-ÿ\s]', ' ', str(text))
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def convert_price(price):
    if pd.isna(price):
        return 0.0
    if isinstance(price, str):
        # Supprimer tout sauf les chiffres et le point
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
    
    # Dictionnaire de conversion texte -> nombre
    rating_dict = {
        'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
        'un': 1, 'deux': 2, 'trois': 3, 'quatre': 4, 'cinq': 5
    }
    
    if isinstance(rating, str):
        # Convertir en minuscules et nettoyer
        rating = rating.lower().strip()
        # Vérifier si c'est un mot
        if rating in rating_dict:
            return float(rating_dict[rating])
        # Essayer de convertir en nombre
        try:
            return float(re.sub(r'[^0-9.]', '', rating))
        except:
            return 0.0
    try:
        return float(rating)
    except:
        return 0.0

try:
    # Charger le fichier CSV brut
    print("[INFO] Lecture du fichier CSV brut...")
    df = pd.read_csv('livres_bruts.csv')  # Correction ici
    print(f"[INFO] Nombre de livres avant nettoyage: {len(df)}")

    # Nettoyage des données
    print("[INFO] Nettoyage des données...")
    
    # Nettoyer les descriptions
    df['description'] = df['description'].apply(clean_description)
    
    # Remplir les descriptions manquantes avec le titre
    df['description'] = df.apply(lambda x: x['titre'] if pd.isna(x['description']) or len(x['description']) < 10 else x['description'], axis=1)
    
    # Convertir les prix
    df['prix'] = df['prix'].apply(convert_price)
    
    # Convertir la disponibilité
    df['disponibilite'] = df['disponibilite'].apply(convert_availability)
    
    # Convertir les notes
    df['note'] = df['note'].apply(convert_rating)
    
    # Sauvegarder en CSV temporaire (garder le même nom)
    df.to_csv('livres_bruts.csv', index=False)  # Correction ici aussi
    print("[OK] Données nettoyées sauvegardées dans livres_bruts.csv")

    # Connexion à la base de données
    load_dotenv()