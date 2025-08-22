
    print("Table 'livres' créée avec succès !")
except Exception as e:
    print("Erreur lors de la création de la table :", e)

cursor.close()
conn.close()
