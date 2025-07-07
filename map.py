from flask import Flask, render_template, request
import pandas as pd
import folium
import branca
from folium.plugins import MarkerCluster

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
    df_logement = pd.read_csv("./db/Bordeaux.csv", sep=";")
    df_finance = pd.read_csv("./db/entreprise_bordeaux.csv", sep=";", low_memory=False)
    df_educ = pd.read_csv("./db/educ_bordeaux.csv", sep=";")

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
        for possible in ['date', 'date_maj', 'date_maj_ligne', 'cdate']:
            if possible in df_finance.columns:
                date_col = possible
                break
        if date_col:
            # Conversion robuste de la colonne date avec gestion des timezones
            date_series = pd.to_datetime(df_finance[date_col], errors='coerce', utc=True)
            if pd.api.types.is_datetime64_any_dtype(date_series):
                df_finance['annee'] = date_series.dt.year
            else:
                print(f"Impossible de convertir {date_col} en datetime. Exemple de valeur : {df_finance[date_col].iloc[0]}")
                df_finance['annee'] = None
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
    try:
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
        # Remplacer get par getlist pour année
        annee = request.form.getlist("annee")
        prix_min = request.form.get("prix_min")
        prix_max = request.form.get("prix_max")
        type_bien = request.form.getlist("type_bien")
        commune = request.form.getlist("commune")
        statut_etab = request.form.getlist("statut")
        type_etab = request.form.getlist("type_etab")

        # Application des filtres APRÈS avoir extrait les valeurs uniques
        # Filtrage multi-valeurs pour année (si rien n'est coché, on ne filtre pas)
        if annee:
            try:
                annees_int = [int(a) for a in annee]
                df_logement = df_logement[df_logement["annee"].isin(annees_int)]
                df_finance = df_finance[df_finance["annee"].isin(annees_int)]
                df_educ = df_educ[df_educ["annee"].isin(annees_int)]
            except Exception as e:
                print("Erreur filtre année :", e)

        # filtrage prix_min/prix_max
        prix_min_val = None
        prix_max_val = None
        try:
            prix_min_val = float(prix_min) if prix_min not in (None, "", "None") else None
        except Exception:
            prix_min_val = None
        try:
            prix_max_val = float(prix_max) if prix_max not in (None, "", "None") else None
        except Exception:
            prix_max_val = None

        if prix_min_val is not None and prix_max_val is not None:
            df_logement = df_logement[
                (df_logement["valeur_fonciere"].astype(float) >= prix_min_val) &
                (df_logement["valeur_fonciere"].astype(float) <= prix_max_val)
            ]
        elif prix_min_val is not None and prix_max_val is None:
            df_logement = df_logement[df_logement["valeur_fonciere"].astype(float) >= prix_min_val]
        elif prix_max_val is not None and prix_min_val is None:
            df_logement = df_logement[df_logement["valeur_fonciere"].astype(float) <= prix_max_val]
        # Filtrage multi-valeurs pour type_bien (si rien n'est coché, on ne filtre pas)
        if type_bien:
            df_logement = df_logement[df_logement["type_local"].isin(type_bien)]
        # Filtrage multi-valeurs pour commune
        if commune:
            df_logement = df_logement[df_logement["commune"].isin(commune)]

        # Filtrage multi-valeurs pour statut_etab
        if statut_etab:
            df_educ = df_educ[df_educ["statut_public_prive"].isin(statut_etab)]
        # Filtrage multi-valeurs pour type_etab
        if type_etab:
            df_educ = df_educ[df_educ["type_etablissement"].isin(type_etab)]

        # Limite du nombre de points par couche
        MAX_POINTS = 1000

        # Création de la carte
        m = folium.Map(location=[44.8378, -0.5792], zoom_start=12)

        # Ajout d'un script JS pour ajuster la taille des points selon le zoom (compatible Folium)
        map_var = m.get_name()
        custom_js = f"""
        function resizeCircles(e) {{
            var zoom = e.target.getZoom();
            var scale = Math.max(2, Math.min(zoom, 16));
            e.target.eachLayer(function(layer) {{
                if(layer instanceof L.CircleMarker){{
                    layer.setRadius(scale);
                }}
            }});
        }}
        {map_var}.on('zoomend', resizeCircles);
        resizeCircles({{target: {map_var}}});
        """
        from folium.elements import MacroElement
        from jinja2 import Template
        class CustomJs(MacroElement):
            def __init__(self, script):
                super().__init__()
                self._template = Template(f"""
                <script>
                {script}
                </script>
                """)
        m.get_root().add_child(CustomJs(custom_js))

        # MarkerCluster pour chaque couche
        logement_cluster = MarkerCluster(name="Logement").add_to(m)
        finance_cluster = MarkerCluster(name="Finance").add_to(m)
        educ_cluster = MarkerCluster(name="Éducation").add_to(m)

        # Affichage des points logement (limite à MAX_POINTS)
        if "latitude" in df_logement.columns and "longitude" in df_logement.columns and not df_logement.empty:
            print("Nb points logement à afficher :", len(df_logement))
            for _, row in df_logement.head(MAX_POINTS).iterrows():
                popup_infos = []
                if pd.notnull(row.get("type_local")):
                    popup_infos.append(f"<b>Type</b>: {row.get('type_local')}")
                if pd.notnull(row.get("valeur_fonciere")):
                    popup_infos.append(f"<b>Prix</b>: {row.get('valeur_fonciere')}")
                if pd.notnull(row.get("commune")):
                    popup_infos.append(f"<b>Commune</b>: {row.get('commune')}")
                popup_text = "<br>".join(popup_infos) if popup_infos else "Logement"
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    icon=folium.Icon(color="blue", icon="home", prefix='fa'),
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(logement_cluster)
        else:
            print("Aucun point logement à afficher (colonnes manquantes ou DataFrame vide)")

        # Affichage des points finance (limite à MAX_POINTS)
        if "latitude" in df_finance.columns and "longitude" in df_finance.columns and not df_finance.empty:
            print("Nb points finance à afficher :", len(df_finance))
            for _, row in df_finance.head(MAX_POINTS).iterrows():
                popup_infos = []
                if pd.notnull(row.get("raison_sociale")):
                    popup_infos.append(f"<b>Nom</b>: {row.get('raison_sociale')}")
                if pd.notnull(row.get("statut")):
                    popup_infos.append(f"<b>Statut</b>: {row.get('statut')}")
                if pd.notnull(row.get("section")):
                    popup_infos.append(f"<b>Section</b>: {row.get('section')}")
                popup_text = "<br>".join(popup_infos) if popup_infos else "Établissement financier"
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    icon=folium.Icon(color="green", icon="shopping-cart", prefix='fa'),
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(finance_cluster)
        else:
            print("Aucun point finance à afficher (colonnes manquantes ou DataFrame vide)")

        # Affichage des points éducation (limite à MAX_POINTS)
        if "latitude" in df_educ.columns and "longitude" in df_educ.columns and not df_educ.empty:
            print("Nb points educ à afficher :", len(df_educ))
            for _, row in df_educ.head(MAX_POINTS).iterrows():
                popup_infos = []
                if pd.notnull(row.get("type_etablissement")):
                    popup_infos.append(f"<b>Type</b>: {row.get('type_etablissement')}")
                if pd.notnull(row.get("statut_public_prive")):
                    popup_infos.append(f"<b>Statut</b>: {row.get('statut_public_prive')}")
                if pd.notnull(row.get("nom_etablissement")):
                    popup_infos.append(f"<b>Nom</b>: {row.get('nom_etablissement')}")
                popup_text = "<br>".join(popup_infos) if popup_infos else "Établissement"
                folium.Marker(
                    location=[row["latitude"], row["longitude"]],
                    icon=folium.Icon(color="red", icon="graduation-cap", prefix='fa'),
                    popup=folium.Popup(popup_text, max_width=300)
                ).add_to(educ_cluster)
        else:
            print("Aucun point éducation à afficher (colonnes manquantes ou DataFrame vide)")

        map_html = m._repr_html_()
        print("map_html length:", len(map_html))  # Debug: should be > 0

        return render_template(
            "map.html",
            map_html=map_html,
            type_biens=type_biens if type_biens is not None else [],
            communes=communes if communes is not None else [],
            types_etab=types_etab if types_etab is not None else [],
            statuts=statuts if statuts is not None else [],
            annees=annees if annees is not None else [],
            form_data=request.form
        )
    except Exception as e:
        print("Erreur lors du rendu de la page :", e)
        return "<h2>Erreur lors du rendu de la page : {}</h2>".format(e)

if __name__ == "__main__":
    app.run(debug=True)
