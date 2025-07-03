from flask import Flask, render_template, request
import pandas as pd
import folium

app = Flask(__name__)

# Nettoyage générique avec vérification
def nettoyer_coordonnees(df):
    # Si latitude/longitude n'existent pas, tente de les extraire depuis geo_point ou geo point
    if 'latitude' not in df.columns or 'longitude' not in df.columns:
        geo_col = None
        for possible in ['geo_point', 'geo point', 'geopoint']:
            if possible in df.columns:
                geo_col = possible
                break
        if geo_col:
            # Extraction des coordonnées depuis geo_point ou geo point
            def extract_lat(row):
                try:
                    return float(str(row).split(',')[0].strip())
                except:
                    return None
            def extract_lon(row):
                try:
                    return float(str(row).split(',')[1].strip())
                except:
                    return None
            df['latitude'] = df[geo_col].apply(extract_lat)
            df['longitude'] = df[geo_col].apply(extract_lon)
    if 'latitude' in df.columns and 'longitude' in df.columns:
        df = df.dropna(subset=['latitude', 'longitude'])
        df = df[(df['latitude'].apply(lambda x: str(x).replace('.', '', 1).replace('-', '', 1).isdigit())) &
                (df['longitude'].apply(lambda x: str(x).replace('.', '', 1).replace('-', '', 1).isdigit()))]
        df['latitude'] = df['latitude'].astype(float)
        df['longitude'] = df['longitude'].astype(float)
    else:
        print("Colonnes latitude/longitude manquantes :", df.columns)
    return df

# Chargement + nettoyage des fichiers CSV
def charger_donnees():
    df_logement = pd.read_csv("Bordeaux.csv", sep=",")
    df_finance = pd.read_csv("fi_etabl_p.csv", sep=";", low_memory=False)
    df_educ = pd.read_csv("educ_bordeaux.csv", sep=",")

    # Nettoyage des colonnes
    df_logement.columns = df_logement.columns.str.strip().str.lower()
    df_finance.columns = df_finance.columns.str.strip().str.lower()
    df_educ.columns = df_educ.columns.str.strip().str.lower()

    df_logement = nettoyer_coordonnees(df_logement)
    df_finance = nettoyer_coordonnees(df_finance)
    df_educ = nettoyer_coordonnees(df_educ)

    # Harmonisation du nom de la colonne 'commune'
    commune_col = None
    for possible in ['commune', 'nom_commune', 'commune_actuelle']:
        if possible in df_logement.columns:
            commune_col = possible
            break
    if commune_col and commune_col != 'commune':
        df_logement = df_logement.rename(columns={commune_col: 'commune'})
    elif not commune_col:
        print("Aucune colonne 'commune' trouvée dans df_logement. Colonnes disponibles :", df_logement.columns)

    # Harmonisation/ajout de la colonne 'annee' pour df_logement
    if 'annee' not in df_logement.columns:
        # Essayer de l'extraire depuis une colonne de date
        date_col = None
        for possible in ['date_mutation', 'date_vente', 'date_transaction']:
            if possible in df_logement.columns:
                date_col = possible
                break
        if date_col:
            df_logement['annee'] = pd.to_datetime(df_logement[date_col], errors='coerce').dt.year
        else:
            print("Aucune colonne de date trouvée pour extraire l'année dans df_logement. Colonnes disponibles :", df_logement.columns)
            df_logement['annee'] = None

    # Harmonisation/ajout de la colonne 'annee' pour df_finance
    if 'annee' not in df_finance.columns:
        date_col = None
        for possible in ['date', 'date_maj', 'date_maj_ligne']:
            if possible in df_finance.columns:
                date_col = possible
                break
        if date_col:
            df_finance['annee'] = pd.to_datetime(df_finance[date_col], errors='coerce').dt.year
        else:
            print("Aucune colonne de date trouvée pour extraire l'année dans df_finance. Colonnes disponibles :", df_finance.columns)
            df_finance['annee'] = None

    # Harmonisation/ajout de la colonne 'annee' pour df_educ
    if 'annee' not in df_educ.columns:
        date_col = None
        for possible in ['date_maj_ligne', 'date_maj', 'date']:
            if possible in df_educ.columns:
                date_col = possible
                break
        if date_col:
            df_educ['annee'] = pd.to_datetime(df_educ[date_col], errors='coerce').dt.year
        else:
            print("Aucune colonne de date trouvée pour extraire l'année dans df_educ. Colonnes disponibles :", df_educ.columns)
            df_educ['annee'] = None

    return df_logement, df_finance, df_educ

@app.route("/", methods=["GET", "POST"])
def index():
    df_logement, df_finance, df_educ = charger_donnees()

    # Valeurs uniques pour menus déroulants AVANT filtrage
    type_biens = sorted(df_logement["type_local"].dropna().unique())
    if "commune" in df_logement.columns:
        communes = sorted(df_logement["commune"].dropna().unique())
    else:
        communes = []
    types_etab = sorted(df_educ["type_etablissement"].dropna().unique())
    statuts = sorted(df_educ["statut_public_prive"].dropna().unique())
    if "annee" in df_logement.columns:
        annees_logement = set(df_logement["annee"].dropna().unique())
    else:
        annees_logement = set()
    if "annee" in df_finance.columns:
        annees_finance = set(df_finance["annee"].dropna().unique())
    else:
        annees_finance = set()
    if "annee" in df_educ.columns:
        annees_educ = set(df_educ["annee"].dropna().unique())
    else:
        annees_educ = set()
    annees = sorted(annees_logement | annees_finance | annees_educ)

    # Récupération des filtres utilisateur
    annee = request.form.get("annee")
    prix_min = request.form.get("prix_min")
    prix_max = request.form.get("prix_max")
    type_bien = request.form.get("type_bien")
    commune = request.form.get("commune")
    statut_etab = request.form.get("statut")
    type_etab = request.form.get("type_etab")

    df_educ["annee"] = pd.to_datetime(df_educ["date_maj_ligne"], errors="coerce").dt.year

    # Application des filtres APRÈS avoir extrait les valeurs uniques
    if annee:
        annee = int(annee)
        df_logement = df_logement[df_logement["annee"] == annee]
        df_finance = df_finance[df_finance["annee"] == annee]
        df_educ = df_educ[df_educ["annee"] == annee]

    if prix_min:
        df_logement = df_logement[df_logement["valeur_fonciere"] >= float(prix_min)]
    if prix_max:
        df_logement = df_logement[df_logement["valeur_fonciere"] <= float(prix_max)]
    if type_bien:
        df_logement = df_logement[df_logement["type_local"].str.contains(type_bien, case=False, na=False)]
    if commune:
        df_logement = df_logement[df_logement["commune"].str.contains(commune, case=False, na=False)]

    if statut_etab:
        df_educ = df_educ[df_educ["statut_public_prive"].str.contains(statut_etab, case=False, na=False)]
    if type_etab:
        df_educ = df_educ[df_educ["type_etablissement"].str.contains(type_etab, case=False, na=False)]

    # Création de la carte
    m = folium.Map(location=[44.8378, -0.5792], zoom_start=12)

    # Affichage des points logement
    if "latitude" in df_logement.columns and "longitude" in df_logement.columns and not df_logement.empty:
        for _, row in df_logement.iterrows():
            popup_infos = []
            if "type_local" in row and pd.notnull(row["type_local"]):
                popup_infos.append(f"Type: {row['type_local']}")
            if "valeur_fonciere" in row and pd.notnull(row["valeur_fonciere"]):
                popup_infos.append(f"Prix: {row['valeur_fonciere']}")
            if "commune" in row and pd.notnull(row["commune"]):
                popup_infos.append(f"Commune: {row['commune']}")
            popup_text = "<br>".join(popup_infos) if popup_infos else "Logement"
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4,
                color="blue",
                fill=True,
                fill_opacity=0.6,
                popup=popup_text
            ).add_to(m)
    else:
        print("Aucun point logement à afficher (colonnes manquantes ou DataFrame vide)")

    # Affichage des points finance
    if "latitude" in df_finance.columns and "longitude" in df_finance.columns and not df_finance.empty:
        for _, row in df_finance.iterrows():
            popup_infos = []
            if "raison_sociale" in row and pd.notnull(row["raison_sociale"]):
                popup_infos.append(f"Nom: {row['raison_sociale']}")
            if "statut" in row and pd.notnull(row["statut"]):
                popup_infos.append(f"Statut: {row['statut']}")
            popup_text = "<br>".join(popup_infos) if popup_infos else "Établissement financier"
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4,
                color="green",
                fill=True,
                fill_opacity=0.6,
                popup=popup_text
            ).add_to(m)
    else:
        print("Aucun point finance à afficher (colonnes manquantes ou DataFrame vide)")

    # Affichage des points éducation
    if "latitude" in df_educ.columns and "longitude" in df_educ.columns and not df_educ.empty:
        for _, row in df_educ.iterrows():
            popup_infos = []
            if "type_etablissement" in row and pd.notnull(row["type_etablissement"]):
                popup_infos.append(f"Type: {row['type_etablissement']}")
            if "statut_public_prive" in row and pd.notnull(row["statut_public_prive"]):
                popup_infos.append(f"Statut: {row['statut_public_prive']}")
            if "nom_etablissement" in row and pd.notnull(row["nom_etablissement"]):
                popup_infos.append(f"Nom: {row['nom_etablissement']}")
            popup_text = "<br>".join(popup_infos) if popup_infos else "Établissement"
            folium.CircleMarker(
                location=[row["latitude"], row["longitude"]],
                radius=4,
                color="red",
                fill=True,
                fill_opacity=0.6,
                popup=popup_text
            ).add_to(m)
    else:
        print("Aucun point éducation à afficher (colonnes manquantes ou DataFrame vide)")

    map_html = m._repr_html_()

    return render_template("map.html",
                           map_html=map_html,
                           type_biens=type_biens,
                           communes=communes,
                           types_etab=types_etab,
                           statuts=statuts,
                           annees=annees,
                           form_data=request.form)

if __name__ == "__main__":
    app.run(debug=True)
