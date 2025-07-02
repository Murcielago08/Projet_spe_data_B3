# Projet Spé Data B3

## Sommaire
- [Projet Spé Data B3](#projet-spé-data-b3)
  - [Sommaire](#sommaire)
  - [Récupérer l'environnement](#récupérer-lenvironnement)
    - [1. Cloner le dépôt](#1-cloner-le-dépôt)
    - [2. Créer un environnement virtuel](#2-créer-un-environnement-virtuel)
    - [3. Activer l'environnement virtuel](#3-activer-lenvironnement-virtuel)
    - [4. Installer les dépendances](#4-installer-les-dépendances)
  - [Introduction](#introduction)
  - [Sources](#sources)

## Récupérer l'environnement

Pour récupérer et configurer l'environnement Python du projet, suivez ces étapes :

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

- **Sur Windows :**
  ```bash
  .\<env>\Scripts\activate
  ```
- **Sur macOS/Linux :**
  ```bash
  source <env>/bin/activate
  ```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

Votre environnement Python est maintenant prêt à l'emploi.

## Introduction

Dans le cadre de notre projet de spécialité en Data Science, nous avons choisi d'explorer les données de [explore.data.gouv.fr](https://explore.data.gouv.fr/fr/immobilier?onglet=carte&filtre=tous&lat=44.72832&lng=-0.54455&zoom=9.91&code=33&level=departement) pour analyser le marché immobillier à bordeaux et le comparé au autre ville. Notre objectif est proposer une analyse commercial ainsi que de développer des modèles prédictifs et des visualisations interactives pour mieux comprendre les dynamiques des données.

## Problematique

Comment les prix de l'immobilier à Bordeaux se comparent-ils à ceux d'autres villes françaises ?

### Objectifs
dashboard interactif pour visualiser les tendances du marché immobilier à Bordeaux et dans d'autres villes françaises.


## Sources

explore.data.gouv.fr