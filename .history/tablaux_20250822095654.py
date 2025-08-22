import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sys
import locale
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class EmpruntResponse(BaseModel):
    id: int
    titre: str
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effectif: Optional[datetime] = None
    statut: str

    class Config:
        from_attributes = True


print("[INFO] Lecture du fichier CSV brut...")
df = pd.read_csv('livres_bruts.csv')
print(f"[INFO] Nombre de livres avant nettoyage: {len(df)}")



load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")

try:
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"), [DB_NAME])
    if not cur.fetchone():
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print("Base créée.")
    else:
        print("Base existe déjà.")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Erreur base : {e}")
    exit()

try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    cur = conn.cursor()

    print("[INFO] Création de la table et insertion des données...")
    
    
    cur.execute("DROP TABLE IF EXISTS livres CASCADE;")
    
    
    cur.execute("""
        CREATE TABLE livres (
            id SERIAL PRIMARY KEY,
            titre TEXT NOT NULL,
            description TEXT,
            prix NUMERIC(10,2),
            disponibilite BOOLEAN DEFAULT true,
            image_url TEXT,
            note NUMERIC(3,1) DEFAULT 0.0,
            lang VARCHAR(2),
            stock INTEGER DEFAULT 1
        );
    """)

    # Insérer les données du DataFrame
    for index, row in df.iterrows():
        cur.execute("""
            INSERT INTO livres (titre, description, prix, disponibilite, image_url, note, lang)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['titre'],
            row['description'],
            float(row['prix']) if pd.notnull(row['prix']) else 0.0,
            bool(row['disponibilite']) if pd.notnull(row['disponibilite']) else True,
            row['image_url'] if 'image_url' in row else None,
            float(row['note']) if pd.notnull(row['note']) else 0.0,
            row['lang'] if 'lang' in row else None
        ))

    # Recréer les tables dépendantes si nécessaire
    cur.execute("""
        CREATE TABLE IF NOT EXISTS emprunts (
            id SERIAL PRIMARY KEY,
            id_adherent INTEGER REFERENCES adherents(id) ON DELETE CASCADE,
            id_livre INTEGER REFERENCES livres(id) ON DELETE CASCADE,
            date_emprunt TIMESTAMP DEFAULT NOW(),
            date_retour_prevue TIMESTAMP NOT NULL,
            date_retour_effectif TIMESTAMP
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            id_adherent INTEGER REFERENCES adherents(id) ON DELETE CASCADE,
            id_livre INTEGER REFERENCES livres(id) ON DELETE CASCADE,
            date_reservation TIMESTAMP DEFAULT NOW(),
            statut TEXT DEFAULT 'active' CHECK (statut IN ('active', 'completed', 'cancelled'))
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS historique_emprunts (
            id_adherent INTEGER REFERENCES adherents(id) ON DELETE CASCADE,
            id_livre INTEGER REFERENCES livres(id) ON DELETE CASCADE,
            note NUMERIC(3,2) CHECK (note >= 0 AND note <= 5),
            date_emprunt TIMESTAMP DEFAULT NOW(),
            PRIMARY KEY (id_adherent, id_livre)
        );
    """)

    conn.commit()
    print("Toutes les tables sont prêtes.")

    cur.close()
    conn.close()

except Exception as e:
    print(f"Erreur tables : {e}")
    exit()