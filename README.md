# Projet Spé Data B3

## Sommaire
- [Projet Spé Data B3](#projet-spé-data-b3)
  - [Sommaire](#sommaire)
  - [Introduction](#introduction)
  - [Problematique](#problematique)
  - [Objectifs](#objectifs)
    - [Récupérer l'environnement](#récupérer-lenvironnement)
      - [1. Cloner le dépôt](#1-cloner-le-dépôt)
      - [2. Créer un environnement virtuel](#2-créer-un-environnement-virtuel)
      - [3. Activer l'environnement virtuel](#3-activer-lenvironnement-virtuel)
      - [4. Installer les dépendances](#4-installer-les-dépendances)
    - [Lancer la carte interactive](#lancer-la-carte-interactive)
  - [Sources](#sources)

## Introduction

Dans le cadre de notre projet de spécialité en Data Science, nous avons choisi d'explorer les données de **data.education.gouv.fr** et **datahub.bordeaux-metropole.fr** pour analyser le marché immobillier à bordeaux et le comparé au autre ville. Notre objectif est proposer une analyse commercial ainsi que de développer des modèles prédictifs et des visualisations interactives pour mieux comprendre les dynamiques des données.

## Problematique

Comment les prix de l'immobilier à Bordeaux se comparent-ils à ceux d'autres villes françaises ?

## Objectifs

L'objectif principal de la carte interactive est de permettre :

- **La visualisation géographique** des logements, établissements financiers et établissements scolaires sur Bordeaux et sa métropole.
- **L’exploration dynamique** grâce à des filtres : année, prix, type de bien, commune, type et statut d’établissement, etc.
- **L’analyse croisée** entre le marché immobilier, la présence d’entreprises et l’offre éducative, pour mieux comprendre les dynamiques territoriales.

La carte permet ainsi d’identifier des tendances, des zones attractives ou sous-dotées, et d’appuyer des analyses commerciales ou prédictives.


### Récupérer l'environnement

Pour récupérer et configurer l'environnement Python du projet, suivez ces étapes :

#### 1. Cloner le dépôt

```bash
git clone https://github.com/Murcielago08/Projet_python_B3
cd Projet_python_B3
```

#### 2. Créer un environnement virtuel

```bash
python -m venv <env>
```

#### 3. Activer l'environnement virtuel

- **Sur Windows :**
  ```bash
  .\<env>\Scripts\activate
  ```
- **Sur macOS/Linux :**
  ```bash
  source <env>/bin/activate
  ```

#### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

Votre environnement Python est maintenant prêt à l'emploi.


### Lancer la carte interactive

Pour lancer l’application web et accéder à la carte interactive :

1. **Assurez-vous d’avoir installé les dépendances** (voir section précédente).

2. **Démarrez le serveur Flask** depuis le dossier du projet :

   ```bash
   python map.py
   ```

3. **Ouvrez votre navigateur** et rendez-vous à l’adresse :
   [http://127.0.0.1:5000](http://127.0.0.1:5000)

Vous pourrez alors utiliser les filtres à gauche pour explorer les données sur la carte à droite.

## Sources

[Annuaire de l'éducation](https://data.education.gouv.fr/explore/dataset/fr-en-annuaire-education/export/?disjunctive.type_etablissement&disjunctive.libelle_academie&disjunctive.libelle_region&disjunctive.ministere_tutelle&disjunctive.appartenance_education_prioritaire&disjunctive.nom_commune&disjunctive.code_postal&disjunctive.code_departement)


[Demande de valeurs foncières géolocalisée sur Bordeaux Métropole](https://opendata.bordeaux-metropole.fr/explore/dataset/demande-de-valeurs-foncieres-geolocalisee-bordeaux-metropole/export/?location=19,44.85485,-0.5691&basemap=jawg.streets)


[Etablissement (d'une entreprise)](https://datahub.bordeaux-metropole.fr/explore/dataset/fi_etabl_p/export/)


[Arrêt transport bordeaux](https://datahub.bordeaux-metropole.fr/explore/dataset/offres-de-services-bus-tramway-gtfs/export/)