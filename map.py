import pandas as pd
import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

df_bordeaux = pd.read_csv("Bordeaux.csv", sep=",", encoding="utf-8", low_memory=False)

# Renommer pour homogénéiser (optionnel)
df_map = df_bordeaux.rename(columns={"latitude": "lat", "longitude": "long"}).copy()

# Filtrer les coordonnées non nulles
df_map = df_map.dropna(subset=["lat", "long"])

# Si les coordonnées sont avec des virgules au lieu de points (cas rare)
df_map["lat"] = df_map["lat"].astype(str).str.replace(",", ".").astype(float)
df_map["long"] = df_map["long"].astype(str).str.replace(",", ".").astype(float)

# Garder uniquement les points en France métropolitaine
df_map = df_map[(df_map["lat"] >= 41) & (df_map["lat"] <= 51) &
                (df_map["long"] >= -5) & (df_map["long"] <= 10)]

# Créer la carte centrée sur la France
m = folium.Map(location=[46.6, 2.2], zoom_start=6)

# Ajouter un cluster de marqueurs
marker_cluster = MarkerCluster().add_to(m)

# Ajouter chaque point au cluster
for _, row in df_map.iterrows():
    popup = f"""
    <b>Commune:</b> {row['nom_commune']}<br>
    <b>Adresse:</b> {row['adresse_numero']} {row['adresse_nom_voie']}<br>
    <b>Valeur foncière:</b> {row['valeur_fonciere']} €<br>
    <b>Date:</b> {row['date_mutation']}
    """
    folium.Marker(
        location=[row["lat"], row["long"]],
        popup=popup
    ).add_to(marker_cluster)

# Afficher la carte dans une fenêtre du navigateur
output_path = "map_bordeaux.html"
m.save(output_path)
webbrowser.open('file://' + os.path.realpath(output_path))
