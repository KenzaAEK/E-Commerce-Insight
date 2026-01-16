# OmniMarket 360 - Architecture BI Multi-Sources pour E-Commerce

Ce projet propose une solution complète de **Business Intelligence** pour analyser les performances d'une plateforme e-commerce multi-canaux (Web, Mobile et Magasins physiques). Inspirée des leaders du marché marocain comme Jumia ou Amazon, l'architecture traite l'intégralité de la chaîne décisionnelle, de la génération de données hétérogènes à la visualisation avancée dans Power BI.

## 🚀 Aperçu du Projet

L'objectif principal est de transformer des données brutes provenant de sources disparates en **insights stratégiques**. Le système permet notamment d'identifier des leviers de croissance, comme l'optimisation du tunnel de conversion (gain potentiel de 11,86M MAD) ou la réduction des retours clients.

### Points clés :

* 
**Intégration Multi-Sources :** Extraction de données depuis SQL, Excel, CSV, JSON et XML.


* 
**Modélisation Décisionnelle :** Conception d'un modèle en étoile avec 7 dimensions et 4 tables de faits.


* 
**Analyses Avancées :** Segmentation RFM, Analyse ABC (loi de Pareto), Time Intelligence et Funnel de conversion.



---

## 🛠️ Architecture Technique

L'architecture suit le paradigme classique des entrepôts de données:

1. 
**Génération (Python) :** Simulation de comportements clients réalistes avec patterns saisonniers (Ramadan, Black Friday).


2. 
**Stockage (MySQL) :** Base de données relationnelle hébergeant l'entrepôt.


3. 
**ETL (Power Query) :** Nettoyage, standardisation et gestion de la qualité des données (doublons, valeurs NULL).


4. 
**Visualisation (Power BI) :** Création de mesures DAX complexes et de dashboards interactifs.



---

## 📊 Dashboards Implémentés

Le projet comporte **5 tableaux de bord spécialisés**:

| Dashboard | Audience | Indicateurs Clés (KPIs) |
| --- | --- | --- |
| **Vue Exécutive** | Direction Générale | CA total, Marge, Évolution YoY, Panier Moyen.

 |
| **Analyse Clients** | Marketing & CRM | Segmentation RFM (Gold/Silver/Bronze), Lifetime Value, Performance par ville.

 |
| **Performance Produits** | Commercial | Analyse ABC, Top/Bottom ventes, Matrice CA vs Marge.

 |
| **Retours & Logistique** | Supply Chain | Taux de retour, Motifs de réclamation, Impact financier.

 |
| **Web & Conversion** | E-commerce Manager | Taux de conversion, Abandon de panier, Analyse du tunnel digital.

 |

---

## ⚙️ Installation et Utilisation

### Prérequis

* Python 3.x
* MySQL Server & Driver ODBC 9.5 ANSI 


* Power BI Desktop

### Étapes

1. **Cloner le dépôt :**
```bash
git clone https://github.com/KenzaAEK/E-Commerce-Insight.git

```


2. **Générer les données :**
Exécutez le script Python pour créer les fichiers sources (CSV, JSON, XML, etc.).


```bash
pip install -r requirements.txt
python generation_donnees.py

```


3. **Charger dans MySQL :**
Utilisez le script d'upload pour créer le schéma et injecter les données.


```bash
python upload_to_sql.py

```


4. **Ouvrir Power BI :**
Ouvrez le fichier `.pbix`, configurez le DSN ODBC et actualisez les données.



---

## 👥 Équipe de projet

* 
**Réalisé par :** ABOU-EL KASEM Kenza & EL BAKALI Malak.


* **Encadré par :** Pr. BADIR Hassan.


* 
**Institution :** ENSA Tanger, Université Abdelmalek Essaâdi.


* 
**Année Universitaire :** 2025-2026.



---
