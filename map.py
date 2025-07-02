from flask import Flask, render_template, request
import pandas as pd
import folium
import os
from folium.plugins import MarkerCluster

app = Flask(__name__)

# Charger les données une seule fois
df_raw = pd.read_csv("Bordeaux.csv", sep=",", encoding="utf-8", low_memory=False)

# Nettoyage
df_raw = df_raw.rename(columns={"latitude": "lat", "longitude": "long"}).copy()
df_raw = df_raw.dropna(subset=["lat", "long"])
df_raw["lat"] = df_raw["lat"].astype(str).str.replace(",", ".").astype(float)
df_raw["long"] = df_raw["long"].astype(str).str.replace(",", ".").astype(float)
df_raw = df_raw[(df_raw["lat"] >= 41) & (df_raw["lat"] <= 51) &
                (df_raw["long"] >= -5) & (df_raw["long"] <= 10)]

# Menus déroulants
types_biens = sorted(df_raw["type_local"].dropna().unique().tolist())
communes = sorted(df_raw["nom_commune"].dropna().unique().tolist())

@app.route('/', methods=['GET', 'POST'])
def index():
    df = df_raw.copy()
    year = request.form.get("year", "")
    min_price = request.form.get("min_price", "")
    max_price = request.form.get("max_price", "")
    selected_type = request.form.get("type_local", "")
    selected_commune = request.form.get("nom_commune", "")

    # Filtres
    if year:
        df = df[df["date_mutation"].str.startswith(year)]
    if min_price:
        df = df[df["valeur_fonciere"] >= float(min_price)]
    if max_price:
        df = df[df["valeur_fonciere"] <= float(max_price)]
    if selected_type:
        df = df[df["type_local"] == selected_type]
    if selected_commune:
        df = df[df["nom_commune"] == selected_commune]

    # Carte
    m = folium.Map(location=[44.8378, -0.5792], zoom_start=11)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup = f"""
        <b>Commune:</b> {row['nom_commune']}<br>
        <b>Adresse:</b> {row['adresse_numero']} {row['adresse_nom_voie']}<br>
        <b>Valeur foncière:</b> {row['valeur_fonciere']} €<br>
        <b>Type:</b> {row.get('type_local', 'Non défini')}<br>
        <b>Date:</b> {row['date_mutation']}
        """
        folium.CircleMarker(
            location=[row["lat"], row["long"]],
            radius=3,
            color='blue',
            fill=True,
            fill_opacity=0.6,
            popup=popup
        ).add_to(marker_cluster)

    map_html = m._repr_html_()

    return render_template("map.html",
                           map_html=map_html,
                           year=year,
                           min_price=min_price,
                           max_price=max_price,
                           selected_type=selected_type,
                           selected_commune=selected_commune,
                           types_biens=types_biens,
                           communes=communes)

if __name__ == "__main__":
    app.run(debug=True)
