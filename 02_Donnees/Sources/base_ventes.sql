-- Script SQL auto-généré (projet E-Commerce Power BI)
-- Generated at 2026-01-14 15:31:36

CREATE TABLE IF NOT EXISTS Dim_Client (
  ID_Client INT,
  Code_Client TEXT,
  Prenom TEXT,
  Nom TEXT,
  Nom_Complet TEXT,
  Email TEXT,
  Telephone TEXT,
  Date_Inscription DATE,
  Ville TEXT,
  Pays TEXT,
  Age INT,
  Genre TEXT,
  Segment_RFM TEXT,
  Score_Fidelite INT,
  PRIMARY KEY (ID_Client)
);
CREATE TABLE IF NOT EXISTS Dim_Produit (
  ID_Produit INT,
  SKU TEXT,
  Nom_Produit TEXT,
  Categorie TEXT,
  Sous_Categorie TEXT,
  Marque TEXT,
  Prix_Unitaire NUMERIC(12,2),
  Cout_Achat NUMERIC(12,2),
  Poids_Kg NUMERIC(12,2),
  Actif INT,
  PRIMARY KEY (ID_Produit)
);
CREATE TABLE IF NOT EXISTS Dim_Temps (
  ID_Date INT,
  Date_Complete DATE,
  Annee INT,
  Trimestre INT,
  Mois INT,
  Mois_Nom TEXT,
  Semaine INT,
  Jour INT,
  Jour_Semaine TEXT,
  Est_Weekend INT,
  Est_Ferie INT,
  Saison_Commerciale TEXT,
  PRIMARY KEY (ID_Date)
);
CREATE TABLE IF NOT EXISTS Dim_Canal (
  ID_Canal INT,
  Nom_Canal TEXT,
  Type TEXT,
  PRIMARY KEY (ID_Canal)
);
CREATE TABLE IF NOT EXISTS Dim_Promotion (
  ID_Promotion INT,
  Code_Promo TEXT,
  Nom_Campagne TEXT,
  Type_Remise TEXT,
  Valeur_Remise INT,
  Date_Debut DATE,
  Date_Fin DATE,
  PRIMARY KEY (ID_Promotion)
);
CREATE TABLE IF NOT EXISTS Dim_Livraison (
  ID_Livraison INT,
  Transporteur TEXT,
  Type_Livraison TEXT,
  Delai_Prevu_Jours INT,
  PRIMARY KEY (ID_Livraison)
);
CREATE TABLE IF NOT EXISTS Dim_Motif_Retour (
  ID_Motif INT,
  Motif TEXT,
  Categorie TEXT,
  PRIMARY KEY (ID_Motif)
);
CREATE TABLE IF NOT EXISTS Fait_Ventes (
  ID_Vente INT,
  ID_Client INT,
  ID_Produit INT,
  ID_Date INT,
  Date_Vente DATE,
  Heure_Vente INT,
  DateTime_Vente TIMESTAMP,
  ID_Canal INT,
  ID_Promotion INT,
  ID_Livraison INT,
  Quantite INT,
  Montant_HT NUMERIC(12,2),
  Montant_TTC NUMERIC(12,2),
  Cout_Produit NUMERIC(12,2),
  Marge NUMERIC(12,2),
  Remise_Appliquee NUMERIC(12,2),
  PRIMARY KEY (ID_Vente)
);
CREATE TABLE IF NOT EXISTS Fait_Retours (
  ID_Retour INT,
  ID_Vente INT,
  ID_Date_Retour INT,
  Date_Retour DATE,
  ID_Motif INT,
  Montant_Rembourse NUMERIC(12,2),
  Delai_Retour_Jours INT,
  PRIMARY KEY (ID_Retour)
);
CREATE TABLE IF NOT EXISTS Fait_Trafic_Web (
  ID_Session INT,
  ID_Client INT,
  ID_Date INT,
  Pages_Vues INT,
  Duree_Session_Sec INT,
  A_Achete INT,
  Panier_Abandonne INT,
  PRIMARY KEY (ID_Session)
);
CREATE TABLE IF NOT EXISTS Fait_Stock (
  ID_Stock INT,
  ID_Produit INT,
  ID_Date INT,
  Date_Snapshot DATE,
  Quantite_Disponible INT,
  Quantite_Reservee INT,
  Valeur_Stock NUMERIC(12,2),
  PRIMARY KEY (ID_Stock)
);

-- NOTE: Inserts non inclus (volumes élevés). Charge via Power Query (Excel/CSV/JSON/XML).
