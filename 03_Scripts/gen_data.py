import os
import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import json

# =================================================================
# 1. GESTION DES CHEMINS (Script situé dans 03_Scripts)
# =================================================================
# On récupère le chemin absolu du dossier racine "Projet_PowerBI_ECommerce"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR) 

# Chemin cible pour les sources 
SOURCE_PATH = os.path.join(BASE_DIR, "02_Donnees", "Sources")

# Vérification de l'existence du dossier (sécurité)
if not os.path.exists(SOURCE_PATH):
    print(f"❌ Erreur : Le dossier {SOURCE_PATH} n'existe pas.")
    exit()

# =================================================================
# 2. INITIALISATION DES GÉNÉRATEURS 
# =================================================================
fake = Faker(['fr_FR'])
Faker.seed(42)
np.random.seed(42)

NB_CLIENTS = 5000   # 
NB_PRODUITS = 300   # 
NB_VENTES = 50000   # 
NB_SESSIONS = 100000 # 

# =================================================================
# 3. GÉNÉRATION DES SOURCES DE DONNÉES
# =================================================================

# --- A. DIM_PRODUIT (Source: XML) ---
categories = {'Électronique': 8000, 'Mode': 1200, 'Maison': 3000, 'Alimentaire': 500}
produits_list = []
root = ET.Element("catalogue_produits")

for i in range(1, NB_PRODUITS + 1):
    cat = random.choice(list(categories.keys()))
    prix_max = categories[cat]
    prix_u = round(random.uniform(50, prix_max), 2)
    
    prod_el = ET.SubElement(root, "produit")
    ET.SubElement(prod_el, "id").text = str(i)
    ET.SubElement(prod_el, "nom").text = f"{cat} {fake.word().capitalize()}"
    ET.SubElement(prod_el, "categorie").text = cat
    ET.SubElement(prod_el, "prix_unitaire").text = str(prix_u)
    ET.SubElement(prod_el, "cout_achat").text = str(round(prix_u * 0.7, 2))
    
    produits_list.append({'id': i, 'prix': prix_u, 'cat': cat})

tree = ET.ElementTree(root)
tree.write(os.path.join(SOURCE_PATH, "produits.xml"), encoding='utf-8', xml_declaration=True)

# --- B. DIM_CLIENT (Source: EXCEL)  ---
villes_maroc = ['Casablanca', 'Rabat', 'Tanger', 'Marrakech', 'Agadir', 'Fès']
clients_data = []
for i in range(1, NB_CLIENTS + 1):
    clients_data.append({
        'ID_Client': i,
        'Nom_Complet': fake.name(),
        'Email': fake.unique.email(),
        'Ville': random.choice(villes_maroc),
        'Age': random.randint(18, 75),
        'Genre': random.choice(['M', 'F']),
        'Date_Inscription': fake.date_between(start_date='-2y', end_date='today')
    })

df_clients = pd.DataFrame(clients_data)
# Doublons pour nettoyage ETL 
df_clients = pd.concat([df_clients, df_clients.head(50)], ignore_index=True)
df_clients.to_excel(os.path.join(SOURCE_PATH, "clients.xlsx"), index=False)

# --- C. FAIT_VENTES (Source: CSV)  ---
ventes_data = []
start_date = datetime(2023, 1, 1) # Période 2023-2024 

for i in range(NB_VENTES):
    date_v = start_date + timedelta(days=random.randint(0, 729))
    
    # Patterns saisonniers
    coeff = 1.0
    if date_v.month == 11: coeff = 2.5 # Black Friday
    if date_v.month == 4: coeff = 1.4  # Ramadan
    if date_v.month == 1: coeff = 0.7  # Post-fêtes
    
    if random.random() <= (coeff / 2.5):
        p = random.choice(produits_list)
        qte = random.randint(1, 4)
        ventes_data.append({
            'ID_Vente': i + 1,
            'ID_Client': random.randint(1, NB_CLIENTS),
            'ID_Produit': p['id'],
            'Date': date_v.strftime('%Y-%m-%d'),
            'ID_Canal': random.choice([1, 2, 3]), # 1:Web, 2:Mobile, 3:Magasin [cite: 295-298]
            'Quantite': qte,
            'Montant_TTC': round(p['prix'] * qte * 1.2, 2)
        })

pd.DataFrame(ventes_data).to_csv(os.path.join(SOURCE_PATH, "transactions.csv"), index=False)

# --- D. WEB_LOGS (Source: JSON) ---
sessions = []
for i in range(NB_SESSIONS):
    sessions.append({
        'session_id': f"SESS_{i}",
        'pages_vues': random.randint(1, 20),
        'duree_sec': random.randint(15, 1200),
        'a_achete': 1 if random.random() < 0.05 else 0,
        'panier_abandonne': 1 if random.random() < 0.15 else 0
    })

with open(os.path.join(SOURCE_PATH, "web_logs.json"), "w") as f:
    json.dump(sessions, f)

# --- E. OBJECTIFS (Source: Excel) ---
objectifs = []
for m in range(1, 13):
    objectifs.append({'Mois': m, 'Objectif_CA': random.randint(500000, 900000)})
pd.DataFrame(objectifs).to_excel(os.path.join(SOURCE_PATH, "objectifs_mensuels.xlsx"), index=False)

print(f"✅ Données générées avec succès dans : {SOURCE_PATH}")