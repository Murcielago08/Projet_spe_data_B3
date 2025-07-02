import pandas as pd
import folium
from folium.plugins import MarkerCluster
import webbrowser
import os

# === 🔹 1. CHARGEMENT DES DONNÉES IMMOBILIÈRES ===
df_bordeaux = pd.read_csv("Bordeaux.csv", sep=",", encoding="utf-8", low_memory=False)
df_map = df_bordeaux.rename(columns={"latitude": "lat", "longitude": "long"}).copy()
df_map = df_map.dropna(subset=["lat", "long"])

# Convertir les coordonnées en float
df_map["lat"] = df_map["lat"].astype(str).str.replace(",", ".").astype(float)
df_map["long"] = df_map["long"].astype(str).str.replace(",", ".").astype(float)

# Garder les points en France métropolitaine
df_map = df_map[(df_map["lat"] >= 41) & (df_map["lat"] <= 51) &
                (df_map["long"] >= -5) & (df_map["long"] <= 10)]

# === 🔹 2. CRÉATION DE LA CARTE ===
m = folium.Map(location=[44.84, -0.58], zoom_start=11)
marker_cluster = MarkerCluster().add_to(m)

# Ajouter les points de mutation immobilière
for _, row in df_map.iterrows():
    popup = f"""
    <b>Mutation immobilière</b><br>
    <b>Commune:</b> {row.get('nom_commune', '')}<br>
    <b>Adresse:</b> {row.get('adresse_numero', '')} {row.get('adresse_nom_voie', '')}<br>
    <b>Valeur foncière:</b> {row.get('valeur_fonciere', 'N/A')} €<br>
    <b>Surface:</b> {row.get('surface_reelle_bati', 'N/A')} m²<br>
    <b>Type:</b> {row.get('type_local', 'N/A')}<br>
    <b>Date:</b> {row.get('date_mutation', '')}
    """
    folium.Marker(
        location=[row["lat"], row["long"]],
        popup=popup,
        icon=folium.Icon(color="black", icon="home", prefix="fa")
    ).add_to(marker_cluster)

# === 🔹 3. CHARGEMENT DES COMMERCES ===
df_etabl = pd.read_csv("fi_etabl_p.csv", sep=";", encoding="utf-8", low_memory=False)

if "Geo Point" in df_etabl.columns:
    df_etabl[["lat", "long"]] = df_etabl["Geo Point"].str.split(",", expand=True)
    df_etabl["lat"] = df_etabl["lat"].astype(str).str.replace(",", ".").astype(float)
    df_etabl["long"] = df_etabl["long"].astype(str).str.replace(",", ".").astype(float)
else:
    raise Exception("Colonne 'Geo Point' non trouvée dans fi_etabl_p.csv")

df_etabl = df_etabl.dropna(subset=["lat", "long"])
df_etabl = df_etabl[(df_etabl["lat"] >= 41) & (df_etabl["lat"] <= 51) &
                    (df_etabl["long"] >= -5) & (df_etabl["long"] <= 10)]

# === 🔹 4. CHARGEMENT DES ÉTABLISSEMENTS SCOLAIRES ===
df_educ = pd.read_csv("educ_bordeaux.csv", sep=",", encoding="utf-8", low_memory=False)
df_educ.columns = [col.strip().lower().replace(" ", "_") for col in df_educ.columns]

# Maintenant la détection des colonnes latitude/longitude doit fonctionner :
if "latitude" in df_educ.columns and "longitude" in df_educ.columns:
    df_educ["lat"] = df_educ["latitude"].astype(str).str.replace(",", ".").astype(float)
    df_educ["long"] = df_educ["longitude"].astype(str).str.replace(",", ".").astype(float)
elif "coordonnees" in df_educ.columns:
    df_educ[["lat", "long"]] = df_educ["coordonnees"].str.split(",", expand=True)
    df_educ["lat"] = df_educ["lat"].astype(str).str.replace(",", ".").astype(float)
    df_educ["long"] = df_educ["long"].astype(str).str.replace(",", ".").astype(float)
else:
    raise Exception("Colonne 'latitude/longitude' ou 'geo_point' introuvable dans educ_bordeaux.csv")

df_educ = df_educ.dropna(subset=["lat", "long"])
df_educ = df_educ[(df_educ["lat"] >= 41) & (df_educ["lat"] <= 51) &
                  (df_educ["long"] >= -5) & (df_educ["long"] <= 10)]

# === 🔹 5. AJOUT DES COMMERCES ===
for _, row in df_etabl.iterrows():
    popup = f"""
    <b>Commerce</b><br>
    <b>Nom:</b> {row.get('nom', '')}<br>
    <b>Adresse:</b> {row.get('adresse', '')}
    """
    folium.CircleMarker(
        location=[row["lat"], row["long"]],
        radius=6,
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.8,
        popup=popup
    ).add_to(m)

# === 🔹 6. AJOUT DES ÉTABLISSEMENTS SCOLAIRES ===
for _, row in df_educ.iterrows():
    nom = row.get('nom', '').lower()
    popup = f"""
    <b>Établissement scolaire</b><br>
    <b>Nom:</b> {row.get('nom', '')}<br>
    <b>Adresse:</b> {row.get('adresse', '')}
    """

    # Couleur selon le type d'établissement
    if "lycée" in nom:
        color = "green"
    elif "collège" in nom:
        color = "orange"
    else:
        color = "blue"  # école par défaut

    folium.CircleMarker(
        location=[row["lat"], row["long"]],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        popup=popup
    ).add_to(m)

# === 🔹 7. AJOUT D'UNE LÉGENDE ===
legend_html = """
<div style="position: fixed; 
     bottom: 50px; left: 50px; width: 200px; height: 160px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:white; opacity: 0.9; padding: 10px;">
<b>Légende</b><br>
<span style="color:red;">●</span> Commerce<br>
<span style="color:blue;">●</span> École<br>
<span style="color:orange;">●</span> Collège<br>
<span style="color:green;">●</span> Lycée<br>
<span style="color:black;">📍</span> Transaction immobilière<br>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# === 🔹 8. EXPORT & AFFICHAGE ===
output_path = "map_bordeaux.html"
m.save(output_path)
webbrowser.open('file://' + os.path.realpath(output_path))
