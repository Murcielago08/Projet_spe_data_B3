# 📊 Projet Spé Data B3

## Sommaire

- [📊 Projet Spé Data B3](#-projet-spé-data-b3)
  - [Sommaire](#sommaire)
  - [🎓 Introduction](#-introduction)
  - [❓ Problématique](#-problématique)
  - [🌟 Objectifs](#-objectifs)
  - [🗂️ Organisation du projet](#️-organisation-du-projet)
  - [⚙️ Installation et configuration](#️-installation-et-configuration)
    - [1. Cloner le dépôt](#1-cloner-le-dépôt)
    - [2. Créer un environnement virtuel](#2-créer-un-environnement-virtuel)
    - [3. Activer l'environnement virtuel](#3-activer-lenvironnement-virtuel)
    - [4. Installer les dépendances](#4-installer-les-dépendances)
  - [🚀 Utilisation](#-utilisation)
    - [✅ Lancer le notebook](#-lancer-le-notebook)
    - [✅ Lancer la carte interactive](#-lancer-la-carte-interactive)
    - [✅ Exécuter les scripts d'analyse et de prédiction](#-exécuter-les-scripts-danalyse-et-de-prédiction)
  - [📈 Résultats obtenus](#-résultats-obtenus)
  - [🔮 Axes d'amélioration](#-axes-damélioration)
  - [📚 Sources](#-sources)

---

## 🎓 Introduction

Dans le cadre de notre projet de spécialité en Data Science (Bachelor 3 Ynov), nous avons choisi d'explorer les données de **data.education.gouv.fr** et **datahub.bordeaux-metropole.fr** afin d’analyser le marché immobilier de Bordeaux et de le comparer à d'autres villes. Notre objectif est de proposer une **analyse commerciale enrichie**, de développer des **modèles prédictifs** robustes et de créer des **visualisations interactives** pour mieux comprendre les dynamiques territoriales.

## ❓ Problématique

> **Comment les prix de l'immobilier à Bordeaux se comparent-ils à ceux d'autres villes françaises et quels facteurs géographiques ou socio-économiques influencent ces prix ?**

## 🌟 Objectifs
=======
- **La visualisation géographique** des logements, établissements financiers et établissements scolaires sur Bordeaux.
- **L’exploration dynamique** grâce à des filtres : année, prix, type de bien, commune, type et statut d’établissement.
- **L’analyse croisée** entre le marché immobilier, la présence d’entreprises et l’offre éducative, pour mieux comprendre les dynamiques territoriales.

La carte permet ainsi d’identifier des tendances, des zones attractives ou sous-dotées, et d’appuyer des analyses commerciales.

✅ Visualiser géographiquement :

- Les **logements**,
- Les **établissements financiers et commerciaux**,
- Les **établissements scolaires** sur Bordeaux Métropole.

✅ Explorer dynamiquement :

- Filtres sur **année, prix, type de bien, commune, type et statut d’établissement**, etc.

✅ Analyser :

- La **corrélation** entre marché immobilier, présence d’entreprises, offre éducative et accessibilité (transports).
- Identifier des **zones attractives ou sous-dotées**.

✅ Développer :

- Des **modèles prédictifs (LightGBM, TensorFlow MLP)** pour estimer les prix des biens selon leurs caractéristiques et leur localisation.

---

## 🗂️ Organisation du projet


```
Projet_python_B3/
│
├── db/                # Données sources : demande-de-valeurs-foncieres-geolocalisee-bordeaux-metropole.csv, fi_etabl_p.csv, fr-en-annuaire-education.csv, bordeaux.gtfs.zip
├── map.py             # Script Flask pour carte interactive
├── predi.py           # Script prédictif LightGBM et TensorFlow
├── graph_traj.py      # Analyse réseau GTFS des arrêts de bus/tramway
├── requirements.txt   # Dépendances Python
└── README.md          # Documentation du projet
```

---

## ⚙️ Installation et configuration

### 1. Cloner le dépôt

```bash
git clone https://github.com/Murcielago08/Projet_python_B3
cd Projet_python_B3
```

### 2. Créer un environnement virtuel

```bash
python -m venv <env>
```

### 3. Activer l'environnement virtuel

- **Windows :**

  ```bash
  .\<env>\Scripts\activate
  ```

- **macOS/Linux :**

  ```bash
  source <env>/bin/activate
  ```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### ✅ Lancer le notebook

Aller dans le fichier ```data_clean.ipynb``` et sélectionner votre environnement que vous avez créer juste au dessus 

### ✅ Lancer la carte interactive

```bash
python map.py
```

Puis ouvrez votre navigateur à [http://127.0.0.1:5000](http://127.0.0.1:5000).

### ✅ Exécuter les scripts d'analyse et de prédiction

1. **Prédiction RandomForest Regressor**


   ```bash
   python predi.py
   ```

2. **Prédiction TensorFlow MLP**

   ```bash
   python predi_proto.py 
   ```

3. **Analyse réseau transport (GTFS)**

   ```bash
   python graph_traj.py
   ```

   ➔ Identifie les arrêts atteignables et la connectivité du réseau.

---

## 📈 Résultats obtenus

- Visualisation interactive des logements et infrastructures sur Bordeaux.
- Identification des zones à forte accessibilité commerciale et éducative corrélées au prix foncier.
- une version RandomForest atteignant un **MAE moyen de 92 000 €** sur le jeu de test.
- Un prototype à continuer de modèle TensorFlow MLP atteignant un **MAE moyen de 520 000 €** sur le jeu de test.

*(Remplacer X par ton MAE final avant publication)*

---

## 🔮 Axes d'amélioration

- Intégrer plus de villes françaises pour comparaison complète.
- Ce servir de TensorFlow.

## 📚 Sources

- [Annuaire de l'éducation](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/export/?disjunctive.type_etablissement\&disjunctive.libelle_academie\&disjunctive.libelle_region\&disjunctive.ministere_tutelle\&disjunctive.appartenance_education_prioritaire\&disjunctive.nom_commune\&disjunctive.code_postal\&disjunctive.code_departement)
- [Demande de valeurs foncières géolocalisée sur Bordeaux Métropole](https://opendata.bordeaux-metropole.fr/explore/dataset/demande-de-valeurs-foncieres-geolocalisee-bordeaux-metropole/export/?location=19,44.85485,-0.5691\&basemap=jawg.streets)
- [Etablissement (entreprises)](https://datahub.bordeaux-metropole.fr/explore/dataset/fi_etabl_p/export/)
- [Arrêts transports Bordeaux (GTFS)](https://datahub.bordeaux-metropole.fr/explore/dataset/offres-de-services-bus-tramway-gtfs/export/) 
  
  il faut télécharger l'export GTFS 
  et le dézipper Pour récupérer les arrêts,
   il faut utiliser le fichier `stops.txt` et pour les temps d'arrès il faut récuperer `stop_times` dans le dossier GTFS dézippé.
  



