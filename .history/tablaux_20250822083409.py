import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import sys
import locale

# Définir l'encodage UTF-8 pour la sortie
sys.stdout.reconfigure(encoding='utf-8')
# Ou alternativement
# import codecs
# sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class EmpruntResponse(BaseModel):
    id: int
    titre: str
    date_emprunt: datetime
    date_retour_prevue: datetime
    date_retour_effectif: Optional[datetime] = None
    statut: str

    class Config:
        from_attributes = True

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


    cur.execute("""
        CREATE TABLE IF NOT EXISTS adherents (
            id SERIAL PRIMARY KEY,
            nom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'lecteur',
            date_inscription TIMESTAMP DEFAULT NOW()
        );
    """)

    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS livres (
            id SERIAL PRIMARY KEY,
            titre TEXT NOT NULL,
            description TEXT,
            image_url TEXT,
            stock INTEGER DEFAULT 0,
            rating NUMERIC(3,2) DEFAULT 0.00
        );
    """)

    
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

