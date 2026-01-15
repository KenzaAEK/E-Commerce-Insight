"""
Script de génération de données pour projet E-Commerce Power BI
Auteur : ABOU EL KASEM KENZA ET EL BAKALI MALAK
Date : Janvier 2026

Version corrigée (alignée cahier des charges + tes exigences de formats) :
- Ajout DateTime_Vente + Heure_Vente (Heatmap Jour x Heure)
- Dim_Promotion : ajout Date_Debut / Date_Fin
- Garantie NB_PRODUITS exact (complétion si catalogue insuffisant)
- Nommage DW : Dim_* / Fait_*
- Clients + Ventes en EXCEL (comme tu veux)
- Le reste réparti sur différents formats (CSV / XML / JSON / SQL)
- CSV séparateur ';' (Excel FR)
- JSON : NaN -> null
- Objectifs Excel : feuilles 2023 et 2024
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
import xml.etree.ElementTree as ET

# ============================================
# CONFIGURATION GLOBALE
# ============================================

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUTPUT_PATH = "../02_Donnees/Sources/"
os.makedirs(OUTPUT_PATH, exist_ok=True)

NB_CLIENTS = 5000
NB_PRODUITS = 300
NB_TRANSACTIONS = 50000
NB_SESSIONS_WEB = 100000

DATE_DEBUT = datetime(2023, 1, 1)
DATE_FIN = datetime(2024, 12, 31)

print("🚀 Démarrage génération des données E-Commerce (version multi-formats)...")

# ============================================
# 1) DIM_TEMPS
# ============================================

print("\n📅 Génération Dim_Temps...")

def generer_dim_temps():
    dates = pd.date_range(start=DATE_DEBUT, end=DATE_FIN, freq='D')

    dim_temps = pd.DataFrame({
        'ID_Date': range(1, len(dates) + 1),
        'Date_Complete': dates,
        'Annee': dates.year,
        'Trimestre': dates.quarter,
        'Mois': dates.month,
        'Mois_Nom': dates.strftime('%B'),
        'Semaine': dates.isocalendar().week.astype(int),
        'Jour': dates.day,
        'Jour_Semaine': dates.strftime('%A'),
        'Est_Weekend': dates.dayofweek.isin([5, 6]).astype(int),
        'Est_Ferie': 0
    })

    def get_saison(dt):
        mois = dt.month
        if mois == 11:
            return "Black Friday"
        elif mois in [1, 2]:
            return "Soldes Hiver"
        elif mois in [7, 8]:
            return "Soldes Été"
        elif mois in [3, 4]:
            return "Ramadan"
        else:
            return "Normal"

    dim_temps['Saison_Commerciale'] = dim_temps['Date_Complete'].apply(get_saison)
    return dim_temps

dim_temps = generer_dim_temps()
print(f"✅ {len(dim_temps)} jours générés (2023-2024)")

# ============================================
# 2) DIM_CLIENT
# ============================================

print("\n👥 Génération Dim_Client...")

prenoms_maroc = ['Ahmed', 'Mohamed', 'Fatima', 'Khadija', 'Hassan', 'Youssef',
                 'Aicha', 'Zineb', 'Omar', 'Salma', 'Karim', 'Laila',
                 'Mehdi', 'Sara', 'Rachid', 'Samira', 'Bilal', 'Nadia']

noms_maroc = ['Alami', 'Benjelloun', 'El Fassi', 'Tazi', 'Berrada',
              'Filali', 'Idrissi', 'Kettani', 'Lahlou', 'Mekouar',
              'Sefrioui', 'Tounsi', 'Yacoubi', 'Zniber']

villes_maroc = ['Casablanca', 'Rabat', 'Marrakech', 'Fès', 'Tanger',
                'Agadir', 'Meknès', 'Oujda', 'Kenitra', 'Tétouan',
                'Salé', 'El Jadida', 'Nador', 'Mohammedia']

def generer_dim_clients():
    clients = []

    for i in range(1, NB_CLIENTS + 1):
        prenom = random.choice(prenoms_maroc)
        nom = random.choice(noms_maroc)
        genre = random.choice(['M', 'F'])

        age = int(np.random.normal(35, 12))
        age = max(18, min(70, age))

        jours_depuis_debut = int(np.random.exponential(200))
        jours_depuis_debut = min(jours_depuis_debut, (DATE_FIN - DATE_DEBUT).days)
        date_inscription = DATE_DEBUT + timedelta(days=jours_depuis_debut)

        email = f"{prenom.lower()}.{nom.lower()}{random.randint(1,999)}@email.ma"
        telephone = f"+212{random.choice([6,7])}{random.randint(10000000,99999999)}"

        ville_weights = [0.3, 0.15, 0.1, 0.08, 0.07] + [0.03] * 9
        ville = random.choices(villes_maroc, weights=ville_weights)[0]

        clients.append({
            'ID_Client': i,
            'Code_Client': f'CLI{i:05d}',
            'Prenom': prenom,
            'Nom': nom,
            'Nom_Complet': f'{prenom} {nom}',
            'Email': email,
            'Telephone': telephone,
            'Date_Inscription': date_inscription.strftime('%Y-%m-%d'),
            'Ville': ville,
            'Pays': 'Maroc',
            'Age': age,
            'Genre': genre,
            'Segment_RFM': None,
            'Score_Fidelite': 0
        })

    df_clients = pd.DataFrame(clients)

    # Doublons volontaires (50) pour ETL
    doublons = df_clients.sample(50, random_state=SEED).copy()
    doublons['ID_Client'] = range(NB_CLIENTS + 1, NB_CLIENTS + 51)
    df_clients = pd.concat([df_clients, doublons], ignore_index=True)

    # NULL volontaires
    null_indices = random.sample(range(len(df_clients)), 200)
    df_clients.loc[null_indices[:100], 'Telephone'] = None
    df_clients.loc[null_indices[100:], 'Ville'] = None

    return df_clients

dim_clients = generer_dim_clients()
print(f"✅ {len(dim_clients)} clients générés (dont 50 doublons à nettoyer)")

# ============================================
# 3) DIM_PRODUIT
# ============================================

print("\n📦 Génération Dim_Produit...")

catalogue_produits = {
    'Électronique': {
        'Smartphones': ['iPhone 14', 'Samsung Galaxy S23', 'Xiaomi Redmi Note 12', 'Huawei P60'],
        'Ordinateurs': ['MacBook Pro', 'Dell XPS 13', 'HP Pavilion', 'Lenovo ThinkPad'],
        'Accessoires': ['AirPods Pro', 'Souris Logitech', 'Clavier Gaming', 'Webcam HD']
    },
    'Mode': {
        'Vêtements Homme': ['Chemise', 'Pantalon', 'Veste', 'T-shirt'],
        'Vêtements Femme': ['Robe', 'Jupe', 'Blouse', 'Pantalon'],
        'Chaussures': ['Baskets Nike', 'Escarpins', 'Sandales', 'Bottes']
    },
    'Maison': {
        'Cuisine': ['Cafetière', 'Mixeur', 'Poêle', 'Set Couteaux'],
        'Décoration': ['Lampe', 'Cadre Photo', 'Vase', 'Coussin'],
        'Électroménager': ['Aspirateur', 'Fer à repasser', 'Ventilateur']
    },
    'Beauté': {
        'Parfums': ['Eau de Toilette', 'Eau de Parfum', 'Déodorant'],
        'Soins': ['Crème visage', 'Sérum', 'Masque', 'Gommage'],
        'Maquillage': ['Rouge à lèvres', 'Mascara', 'Fond de teint']
    },
    'Sport': {
        'Fitness': ['Tapis de yoga', 'Haltères', 'Élastiques'],
        'Vêtements Sport': ['Legging', 'Brassière', 'Short'],
        'Équipements': ['Ballon', 'Raquette', 'Gourde']
    },
    'Livres': {
        'Romans': ['Thriller', 'Romance', 'Science-Fiction'],
        'Éducatif': ['Livre développement personnel', 'Manuel scolaire'],
        'BD': ['Manga', 'Comics', 'BD Franco-Belge']
    }
}

marques = ['Apple', 'Samsung', 'Sony', 'Nike', 'Adidas', 'Zara', 'H&M',
           'Philips', 'Bosch', "L'Oréal", 'Dior', 'Generic']

def _prix_par_categorie(categorie: str) -> float:
    if categorie == 'Électronique':
        return round(random.uniform(500, 15000), 2)
    if categorie == 'Mode':
        return round(random.uniform(100, 2000), 2)
    if categorie == 'Maison':
        return round(random.uniform(50, 3000), 2)
    if categorie == 'Beauté':
        return round(random.uniform(50, 800), 2)
    if categorie == 'Sport':
        return round(random.uniform(80, 1500), 2)
    return round(random.uniform(50, 300), 2)

def generer_dim_produits():
    produits = []
    id_prod = 1

    for categorie, sous_cats in catalogue_produits.items():
        for sous_cat, items in sous_cats.items():
            for item in items:
                nb_variantes = random.randint(1, 3)
                for v in range(nb_variantes):
                    marque = random.choice(marques)
                    nom_complet = f"{item} {marque}" if v == 0 else f"{item} {marque} v{v+1}"

                    prix = _prix_par_categorie(categorie)
                    cout = round(prix * random.uniform(0.6, 0.8), 2)

                    produits.append({
                        'ID_Produit': id_prod,
                        'SKU': f'SKU{id_prod:05d}',
                        'Nom_Produit': nom_complet,
                        'Categorie': categorie,
                        'Sous_Categorie': sous_cat,
                        'Marque': marque,
                        'Prix_Unitaire': prix,
                        'Cout_Achat': cout,
                        'Poids_Kg': round(random.uniform(0.1, 5.0), 2),
                        'Actif': 1
                    })

                    id_prod += 1
                    if id_prod > NB_PRODUITS:
                        break
                if id_prod > NB_PRODUITS:
                    break
            if id_prod > NB_PRODUITS:
                break
        if id_prod > NB_PRODUITS:
            break

    df = pd.DataFrame(produits)

    # Complétion si < NB_PRODUITS
    if len(df) < NB_PRODUITS:
        manque = NB_PRODUITS - len(df)
        for k in range(manque):
            pid = len(df) + 1
            categorie = random.choice(list(catalogue_produits.keys()))
            sous_cat = random.choice(list(catalogue_produits[categorie].keys()))
            marque = random.choice(marques)

            prix = _prix_par_categorie(categorie)
            cout = round(prix * random.uniform(0.6, 0.8), 2)

            df = pd.concat([df, pd.DataFrame([{
                'ID_Produit': pid,
                'SKU': f'SKU{pid:05d}',
                'Nom_Produit': f"Produit Generic {categorie} {marque} #{k+1}",
                'Categorie': categorie,
                'Sous_Categorie': sous_cat,
                'Marque': marque,
                'Prix_Unitaire': prix,
                'Cout_Achat': cout,
                'Poids_Kg': round(random.uniform(0.1, 5.0), 2),
                'Actif': 1
            }])], ignore_index=True)

    if len(df) > NB_PRODUITS:
        df = df.iloc[:NB_PRODUITS].copy()

    return df

dim_produits = generer_dim_produits()
print(f"✅ {len(dim_produits)} produits générés dans {dim_produits['Categorie'].nunique()} catégories")

# ============================================
# 4) AUTRES DIMENSIONS
# ============================================

print("\n🏪 Génération Dim_Canal, Dim_Promotion, Dim_Livraison, Dim_Motif_Retour...")

dim_canal = pd.DataFrame({
    'ID_Canal': [1, 2, 3],
    'Nom_Canal': ['Web', 'Mobile', 'Magasin'],
    'Type': ['Online', 'Online', 'Offline']
})

promotions = [
    {'ID_Promotion': 1, 'Code_Promo': 'BIENVENUE10', 'Nom_Campagne': 'Bienvenue nouveaux clients',
     'Type_Remise': 'Pourcentage', 'Valeur_Remise': 10, 'Date_Debut': '2023-01-01', 'Date_Fin': '2024-12-31'},
    {'ID_Promotion': 2, 'Code_Promo': 'BLACKFRIDAY', 'Nom_Campagne': 'Black Friday 2024',
     'Type_Remise': 'Pourcentage', 'Valeur_Remise': 30, 'Date_Debut': '2024-11-01', 'Date_Fin': '2024-11-30'},
    {'ID_Promotion': 3, 'Code_Promo': 'SOLDES50', 'Nom_Campagne': 'Soldes Été',
     'Type_Remise': 'Pourcentage', 'Valeur_Remise': 50, 'Date_Debut': '2024-07-01', 'Date_Fin': '2024-08-31'},
    {'ID_Promotion': 4, 'Code_Promo': 'RAMADAN20', 'Nom_Campagne': 'Promo Ramadan',
     'Type_Remise': 'Pourcentage', 'Valeur_Remise': 20, 'Date_Debut': '2024-03-01', 'Date_Fin': '2024-04-30'},
    {'ID_Promotion': 5, 'Code_Promo': None, 'Nom_Campagne': 'Sans promotion',
     'Type_Remise': None, 'Valeur_Remise': 0, 'Date_Debut': None, 'Date_Fin': None}
]
dim_promotion = pd.DataFrame(promotions)

dim_livraison = pd.DataFrame({
    'ID_Livraison': [1, 2, 3],
    'Transporteur': ['Amana', 'CTM', 'Chrono Express'],
    'Type_Livraison': ['Standard', 'Express', 'Standard'],
    'Delai_Prevu_Jours': [3, 1, 2]
})

dim_motif_retour = pd.DataFrame({
    'ID_Motif': range(1, 8),
    'Motif': ['Produit défectueux', 'Taille incorrecte', 'Couleur différente',
              "Changement d'avis", 'Livraison tardive', 'Produit endommagé', 'Autre'],
    'Categorie': ['Qualité', 'Erreur', 'Erreur', 'Client', 'Logistique', 'Logistique', 'Autre']
})

print("✅ Dimensions simples créées")

# ============================================
# 5) FAIT_VENTES
# ============================================

print("\n💰 Génération Fait_Ventes...")
print("⏳ Cela peut prendre 1-2 minutes...")

# Poids horaires (normalisés une seule fois)
hour_weights = np.array([
    0.02, 0.01, 0.01, 0.01, 0.01, 0.02,  # 00–05
    0.03, 0.04, 0.05, 0.06, 0.06, 0.06,  # 06–11
    0.06, 0.06, 0.06, 0.06, 0.06, 0.06,  # 12–17
    0.07, 0.07, 0.06, 0.05, 0.04, 0.03   # 18–23
])
hour_weights = hour_weights / hour_weights.sum()

def generer_fait_ventes():
    ventes = []

    saison_weights = {
        'Normal': 1.0,
        'Soldes Hiver': 1.3,
        'Soldes Été': 1.2,
        'Ramadan': 1.4,
        'Black Friday': 2.5
    }

    canal_proba = [0.6, 0.3, 0.1]

    for i in range(1, NB_TRANSACTIONS + 1):
        date_row = dim_temps.sample(1, weights=dim_temps['Saison_Commerciale'].map(saison_weights))
        id_date = int(date_row['ID_Date'].values[0])
        d = pd.to_datetime(date_row['Date_Complete'].values[0]).to_pydatetime()

        heure = int(np.random.choice(range(24), p=hour_weights))
        minute = random.randint(0, 59)
        seconde = random.randint(0, 59)
        datetime_vente = datetime(d.year, d.month, d.day, heure, minute, seconde)

        # Client 80/20
        if random.random() < 0.8:
            id_client = random.randint(1, int(NB_CLIENTS * 0.2))
        else:
            id_client = random.randint(1, NB_CLIENTS)

        id_produit = random.randint(1, len(dim_produits))
        produit = dim_produits.iloc[id_produit - 1]

        id_canal = random.choices([1, 2, 3], weights=canal_proba)[0]

        if id_canal == 1:
            quantite = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        elif id_canal == 2:
            quantite = 1
        else:
            quantite = random.choices([1, 2, 3, 4], weights=[0.5, 0.3, 0.15, 0.05])[0]

        saison = date_row['Saison_Commerciale'].values[0]
        if saison == 'Black Friday':
            id_promo = 2
        elif saison in ['Soldes Hiver', 'Soldes Été']:
            id_promo = 3
        elif saison == 'Ramadan':
            id_promo = 4
        elif random.random() < 0.1:
            id_promo = 1
        else:
            id_promo = 5

        promo = dim_promotion[dim_promotion['ID_Promotion'] == id_promo].iloc[0]
        remise_pct = float(promo['Valeur_Remise']) if pd.notna(promo['Valeur_Remise']) else 0.0

        prix_unitaire = float(produit['Prix_Unitaire'])
        cout_unitaire = float(produit['Cout_Achat'])

        montant_ht = prix_unitaire * quantite
        remise_appliquee = montant_ht * (remise_pct / 100.0)
        montant_ht_final = montant_ht - remise_appliquee
        montant_ttc = montant_ht_final * 1.20

        cout_total = cout_unitaire * quantite
        marge = montant_ht_final - cout_total

        if id_canal in [1, 2]:
            id_livraison = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
        else:
            id_livraison = None

        ventes.append({
            'ID_Vente': i,
            'ID_Client': id_client,
            'ID_Produit': id_produit,
            'ID_Date': id_date,
            'Date_Vente': datetime_vente.strftime('%Y-%m-%d'),
            'Heure_Vente': heure,
            'DateTime_Vente': datetime_vente.strftime('%Y-%m-%d %H:%M:%S'),
            'ID_Canal': id_canal,
            'ID_Promotion': id_promo,
            'ID_Livraison': id_livraison,
            'Quantite': quantite,
            'Montant_HT': round(montant_ht, 2),
            'Montant_TTC': round(montant_ttc, 2),
            'Cout_Produit': round(cout_total, 2),
            'Marge': round(marge, 2),
            'Remise_Appliquee': round(remise_appliquee, 2)
        })

        if i % 10000 == 0:
            print(f"   ⏳ {i}/{NB_TRANSACTIONS} ventes générées...")

    return pd.DataFrame(ventes)

fait_ventes = generer_fait_ventes()
print(f"✅ {len(fait_ventes)} ventes générées")

# Segmentation RFM
print("\n📊 Calcul segmentation RFM...")
ventes_client = fait_ventes.groupby('ID_Client').agg({
    'ID_Vente': 'count',
    'Montant_TTC': 'sum',
    'DateTime_Vente': 'max'
}).reset_index()
ventes_client.columns = ['ID_Client', 'Nb_Achats', 'CA_Total', 'Derniere_Vente']

def calculer_rfm(row):
    if row['Nb_Achats'] >= 8 and row['CA_Total'] >= 5000:
        return 'Gold'
    elif row['Nb_Achats'] >= 4:
        return 'Silver'
    elif row['Nb_Achats'] >= 1:
        return 'Bronze'
    else:
        return 'Nouveau'

ventes_client['Segment_RFM'] = ventes_client.apply(calculer_rfm, axis=1)

dim_clients = dim_clients.merge(
    ventes_client[['ID_Client', 'Segment_RFM']],
    on='ID_Client',
    how='left',
    suffixes=('', '_new')
)
dim_clients['Segment_RFM'] = dim_clients['Segment_RFM_new'].fillna('Nouveau')
dim_clients = dim_clients.drop('Segment_RFM_new', axis=1)

print(f"   Distribution RFM: {dim_clients['Segment_RFM'].value_counts().to_dict()}")

# ============================================
# 6) FAIT_RETOURS
# ============================================

print("\n↩️ Génération Fait_Retours...")

def generer_fait_retours():
    nb_retours = int(NB_TRANSACTIONS * 0.05)
    ventes_retournees = fait_ventes.sample(nb_retours, random_state=SEED)

    retours = []
    for i, (_, vente) in enumerate(ventes_retournees.iterrows(), 1):
        date_vente = pd.to_datetime(vente['Date_Vente'])
        delai_retour = random.randint(1, 14)
        date_retour = date_vente + timedelta(days=delai_retour)

        id_date_retour = dim_temps.loc[dim_temps['Date_Complete'] == date_retour, 'ID_Date'].values
        if len(id_date_retour) == 0:
            continue

        retours.append({
            'ID_Retour': i,
            'ID_Vente': int(vente['ID_Vente']),
            'ID_Date_Retour': int(id_date_retour[0]),
            'Date_Retour': date_retour.strftime('%Y-%m-%d'),
            'ID_Motif': random.randint(1, 7),
            'Montant_Rembourse': float(vente['Montant_TTC']),
            'Delai_Retour_Jours': delai_retour
        })

    return pd.DataFrame(retours)

fait_retours = generer_fait_retours()
print(f"✅ {len(fait_retours)} retours générés")

# ============================================
# 7) FAIT_TRAFIC_WEB
# ============================================

print("\n🌐 Génération Fait_Trafic_Web...")

def generer_fait_trafic():
    sessions = []

    for i in range(1, NB_SESSIONS_WEB + 1):
        date_row = dim_temps.sample(1)
        id_date = int(date_row['ID_Date'].values[0])

        id_client = random.randint(1, NB_CLIENTS) if random.random() < 0.5 else None

        pages_vues = int(np.random.poisson(3)) + 1
        duree_session = int(np.random.exponential(180))

        a_achete = 1 if random.random() < 0.5 else 0
        panier_abandonne = (1 if random.random() < 0.3 else 0) if a_achete == 0 else 0

        sessions.append({
            'ID_Session': i,
            'ID_Client': id_client,
            'ID_Date': id_date,
            'Pages_Vues': pages_vues,
            'Duree_Session_Sec': duree_session,
            'A_Achete': a_achete,
            'Panier_Abandonne': panier_abandonne
        })

        if i % 20000 == 0:
            print(f"   ⏳ {i}/{NB_SESSIONS_WEB} sessions générées...")

    return pd.DataFrame(sessions)

fait_trafic = generer_fait_trafic()
print(f"✅ {len(fait_trafic)} sessions web générées")

# ============================================
# 8) FAIT_STOCK
# ============================================

print("\n📦 Génération Fait_Stock...")

def generer_fait_stock():
    stocks = []
    id_stock = 1

    dates_snapshot = pd.date_range(start=DATE_DEBUT, end=DATE_FIN, freq='W')

    for dt in dates_snapshot:
        id_date = dim_temps.loc[dim_temps['Date_Complete'] == dt, 'ID_Date'].values
        if len(id_date) == 0:
            continue
        id_date = int(id_date[0])

        for id_produit in range(1, len(dim_produits) + 1):
            produit = dim_produits.iloc[id_produit - 1]
            qte_dispo = random.randint(0, 500)
            qte_reservee = random.randint(0, min(50, qte_dispo))
            valeur_stock = qte_dispo * float(produit['Prix_Unitaire'])

            stocks.append({
                'ID_Stock': id_stock,
                'ID_Produit': id_produit,
                'ID_Date': id_date,
                'Date_Snapshot': dt.strftime('%Y-%m-%d'),
                'Quantite_Disponible': qte_dispo,
                'Quantite_Reservee': qte_reservee,
                'Valeur_Stock': round(valeur_stock, 2)
            })
            id_stock += 1

    return pd.DataFrame(stocks)

fait_stock = generer_fait_stock()
print(f"✅ {len(fait_stock)} enregistrements stock générés")

# ============================================
# 9) EXPORT MULTI-SOURCES (TES EXIGENCES)
# ============================================

print("\n💾 Export multi-sources...")

# ---- EXCEL : Clients + Ventes (comme tu veux)
print("   📗 Export Excel : Dim_Client.xlsx + Fait_Ventes.xlsx + Objectifs_Mensuels.xlsx")

with pd.ExcelWriter(os.path.join(OUTPUT_PATH, 'Dim_Client.xlsx'), engine='openpyxl') as writer:
    dim_clients.to_excel(writer, sheet_name='Dim_Client', index=False)
    ventes_client.to_excel(writer, sheet_name='Stats_RFM', index=False)

with pd.ExcelWriter(os.path.join(OUTPUT_PATH, 'Fait_Ventes.xlsx'), engine='openpyxl') as writer:
    fait_ventes.to_excel(writer, sheet_name='Fait_Ventes', index=False)

objectifs_2023 = pd.DataFrame({
    'Mois': range(1, 13),
    'Objectif_CA': [random.randint(800000, 1500000) for _ in range(12)],
    'Budget_Marketing': [random.randint(50000, 100000) for _ in range(12)]
})
objectifs_2024 = objectifs_2023.copy()
objectifs_2024['Objectif_CA'] = (objectifs_2024['Objectif_CA'] * 1.15).astype(int)

with pd.ExcelWriter(os.path.join(OUTPUT_PATH, 'Objectifs_Mensuels.xlsx'), engine='openpyxl') as writer:
    objectifs_2023.to_excel(writer, sheet_name='2023', index=False)
    objectifs_2024.to_excel(writer, sheet_name='2024', index=False)

# ---- CSV : seulement certains (séparateur ; pour Excel FR)
print("   📄 Export CSV : Dim_Temps, Dim_Promotion, Fait_Stock, Fait_Retours")

dim_temps.to_csv(os.path.join(OUTPUT_PATH, 'Dim_Temps.csv'), index=False, encoding='utf-8-sig', sep=';')
dim_promotion.to_csv(os.path.join(OUTPUT_PATH, 'Dim_Promotion.csv'), index=False, encoding='utf-8-sig', sep=';')
fait_stock.to_csv(os.path.join(OUTPUT_PATH, 'Fait_Stock.csv'), index=False, encoding='utf-8-sig', sep=';')
fait_retours.to_csv(os.path.join(OUTPUT_PATH, 'Fait_Retours.csv'), index=False, encoding='utf-8-sig', sep=';')

# ---- JSON : Dim_Canal + Dim_Livraison + Fait_Trafic_Web (NaN -> null)
print("   🧾 Export JSON : Dim_Canal, Dim_Livraison, Fait_Trafic_Web")

with open(os.path.join(OUTPUT_PATH, 'Dim_Canal.json'), 'w', encoding='utf-8') as f:
    json.dump(dim_canal.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

with open(os.path.join(OUTPUT_PATH, 'Dim_Livraison.json'), 'w', encoding='utf-8') as f:
    json.dump(dim_livraison.to_dict(orient="records"), f, ensure_ascii=False, indent=2)

fait_trafic_json = fait_trafic.replace({np.nan: None})
payload_trafic = {
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "sessions": fait_trafic_json.to_dict(orient="records")
}
with open(os.path.join(OUTPUT_PATH, 'Fait_Trafic_Web.json'), 'w', encoding='utf-8') as f:
    json.dump(payload_trafic, f, ensure_ascii=False, indent=2)

# ---- XML : Dim_Produit + Referentiel_Geo + Dim_Motif_Retour
print("   🧩 Export XML : Dim_Produit, Referentiel_Geo, Dim_Motif_Retour")

# Dim_Produit.xml
root_prod = ET.Element('Dim_Produit')
for _, row in dim_produits.iterrows():
    p = ET.SubElement(root_prod, 'Produit')
    for col in ['ID_Produit', 'SKU', 'Nom_Produit', 'Categorie', 'Sous_Categorie', 'Marque',
                'Prix_Unitaire', 'Cout_Achat', 'Poids_Kg', 'Actif']:
        child = ET.SubElement(p, col)
        child.text = "" if pd.isna(row[col]) else str(row[col])
ET.ElementTree(root_prod).write(os.path.join(OUTPUT_PATH, 'Dim_Produit.xml'),
                                encoding='utf-8', xml_declaration=True)

# Referentiel_Geo.xml
root_geo = ET.Element('Referentiel_Geo')
regions = ET.SubElement(root_geo, 'regions')

region_map = {
    'Casablanca': 'Casablanca-Settat',
    'Mohammedia': 'Casablanca-Settat',
    'Rabat': 'Rabat-Salé-Kénitra',
    'Salé': 'Rabat-Salé-Kénitra',
    'Kenitra': 'Rabat-Salé-Kénitra',
    'Marrakech': 'Marrakech-Safi',
    'Agadir': 'Souss-Massa',
    'Tanger': 'Tanger-Tétouan-Al Hoceïma',
    'Tétouan': 'Tanger-Tétouan-Al Hoceïma',
    'Fès': 'Fès-Meknès',
    'Meknès': 'Fès-Meknès',
    'Oujda': "L'Oriental",
    'Nador': "L'Oriental",
    'El Jadida': 'Casablanca-Settat'
}

for r in sorted(set(region_map.values())):
    ET.SubElement(regions, 'region').text = r

villes_node = ET.SubElement(root_geo, 'villes')
for v in villes_maroc:
    ville_node = ET.SubElement(villes_node, 'ville')
    ET.SubElement(ville_node, 'nom').text = v
    ET.SubElement(ville_node, 'region').text = region_map.get(v, 'Autre')

ET.ElementTree(root_geo).write(os.path.join(OUTPUT_PATH, 'Referentiel_Geo.xml'),
                               encoding='utf-8', xml_declaration=True)

# Dim_Motif_Retour.xml
root_motif = ET.Element('Dim_Motif_Retour')
for _, row in dim_motif_retour.iterrows():
    m = ET.SubElement(root_motif, 'Motif')
    for col in ['ID_Motif', 'Motif', 'Categorie']:
        child = ET.SubElement(m, col)
        child.text = "" if pd.isna(row[col]) else str(row[col])

ET.ElementTree(root_motif).write(os.path.join(OUTPUT_PATH, 'Dim_Motif_Retour.xml'),
                                 encoding='utf-8', xml_declaration=True)

# ---- SQL : script CREATE TABLE (optionnel mais utile)
print("   🗃️ Export SQL : base_ventes.sql")

def _sql_type(col: str, dtype) -> str:
    if col.startswith('ID_'):
        return "INT"
    if "DateTime" in col:
        return "TIMESTAMP"
    if "Date_" in col or col.startswith("Date"):
        return "DATE"
    if "Heure" in col:
        return "INT"
    if pd.api.types.is_integer_dtype(dtype):
        return "INT"
    if pd.api.types.is_float_dtype(dtype):
        return "NUMERIC(12,2)"
    return "TEXT"

def _create_table_sql(table_name: str, df: pd.DataFrame, pk: str | None):
    cols = [f"  {c} {_sql_type(c, df[c].dtype)}" for c in df.columns]
    if pk and pk in df.columns:
        cols.append(f"  PRIMARY KEY ({pk})")
    return f"CREATE TABLE IF NOT EXISTS {table_name} (\n" + ",\n".join(cols) + "\n);\n"

sql_path = os.path.join(OUTPUT_PATH, 'base_ventes.sql')
with open(sql_path, 'w', encoding='utf-8') as f:
    f.write("-- Script SQL auto-généré (projet E-Commerce Power BI)\n")
    f.write(f"-- Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    # Dimensions (structure)
    f.write(_create_table_sql("Dim_Client", dim_clients.head(0), "ID_Client"))
    f.write(_create_table_sql("Dim_Produit", dim_produits.head(0), "ID_Produit"))
    f.write(_create_table_sql("Dim_Temps", dim_temps.head(0), "ID_Date"))
    f.write(_create_table_sql("Dim_Canal", dim_canal.head(0), "ID_Canal"))
    f.write(_create_table_sql("Dim_Promotion", dim_promotion.head(0), "ID_Promotion"))
    f.write(_create_table_sql("Dim_Livraison", dim_livraison.head(0), "ID_Livraison"))
    f.write(_create_table_sql("Dim_Motif_Retour", dim_motif_retour.head(0), "ID_Motif"))

    # Faits (structure)
    f.write(_create_table_sql("Fait_Ventes", fait_ventes.head(0), "ID_Vente"))
    f.write(_create_table_sql("Fait_Retours", fait_retours.head(0), "ID_Retour"))
    f.write(_create_table_sql("Fait_Trafic_Web", fait_trafic.head(0), "ID_Session"))
    f.write(_create_table_sql("Fait_Stock", fait_stock.head(0), "ID_Stock"))

    f.write("\n-- NOTE: Inserts non inclus (volumes élevés). Charge via Power Query (Excel/CSV/JSON/XML).\n")

print("\n✅ Export terminé !")
print("📁 Dossier :", OUTPUT_PATH)
print("📗 Excel : Dim_Client.xlsx, Fait_Ventes.xlsx, Objectifs_Mensuels.xlsx")
print("📄 CSV   : Dim_Temps.csv, Dim_Promotion.csv, Fait_Stock.csv, Fait_Retours.csv")
print("🧾 JSON  : Dim_Canal.json, Dim_Livraison.json, Fait_Trafic_Web.json")
print("🧩 XML   : Dim_Produit.xml, Referentiel_Geo.xml, Dim_Motif_Retour.xml")
print("🗃️ SQL   : base_ventes.sql")
print("\n🎉 Fin du script.")