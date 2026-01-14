-- Création de la base de données
CREATE DATABASE ecommerce_db;

-- Utilisation de la base (pour MySQL)
-- USE ecommerce_db;

-- Table Clients (Source SQL) [cite: 305]
CREATE TABLE clients (
    ID_Client INT PRIMARY KEY,
    Nom_Complet VARCHAR(255),
    Email VARCHAR(255),
    Ville VARCHAR(100),
    Age INT,
    Genre CHAR(1),
    Date_Inscription DATE
);

-- Table Ventes (Source SQL) [cite: 304]
CREATE TABLE ventes (
    ID_Vente INT PRIMARY KEY,
    ID_Client INT,
    ID_Produit INT,
    Date_Vente DATE,
    ID_Canal INT,
    Quantite INT,
    Montant_TTC DECIMAL(10, 2)
);