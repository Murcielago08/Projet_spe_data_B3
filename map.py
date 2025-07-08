from flask import Flask, render_template, request
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from folium.elements import MacroElement
from jinja2 import Template

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

    # # Nettoyage des colonnes (mise en minuscules et remplacement des espaces par des underscores)
    # df_logement.columns = df_logement.columns.str.strip().str.lower().str.replace(' ', '_')
    # df_finance.columns = df_finance.columns.str.strip().str.lower().str.replace(' ', '_')
    # df_educ.columns = df_educ.columns.str.strip().str.lower().str.replace(' ', '_')

    # Renommage spécifique des colonnes pour df_logement
    df_logement = df_logement.rename(columns={
        'Date de la mutation': 'date_de_la_mutation',
        'Valeur foncière': 'valeur_fonciere',
        'Numéro de voie': 'numero_de_voie',
        'Suffixe du numéro (bis/ter)': 'suffixe_du_numero',
        'Nom de la voie': 'nom_de_la_voie',
        'Code postal': 'code_postal',
        'Nombre de lots': 'nombre_de_lots',
        'Code du type de local': 'code_du_type_de_local',
        'Type de local': 'type_de_local',
        'Surface réelle du bâti': 'surface_reelle_du_bati',
        'Nombre de pièces principales': 'nombre_de_pieces_principales',
        'Surface du terrain': 'surface_du_terrain',
        'Longitude': 'longitude',
        'Latitude': 'latitude'
    })

    # Renommage spécifique des colonnes pour df_finance
    df_finance = df_finance.rename(columns={
        'Geo Point': 'geo_point',
        'Geo Shape': 'geo_shape',
        'gid': 'gid',
        'geom_o': 'geom_o',
        'geom_err': 'geom_err',
        'ident': 'ident',
        'adresse': 'adresse',
        'insee': 'insee',
        'raison_sociale': 'raison_sociale',
        'enseigne': 'enseigne',
        'sigle': 'sigle',
        'telephone': 'telephone',
        'date_etablissement': 'date_etablissement',
        'SECTION': 'section',
        'email': 'email',
        'url': 'url',
        'forme_juridique_agg': 'forme_juridique_agg',
        'forme_juridique': 'forme_juridique',
        'statut': 'statut',
        'date_entreprise': 'date_entreprise',
        'naf': 'naf',
        'annee_effectif': 'annee_effectif',
        'tranche_effectif': 'tranche_effectif',
        'cdate': 'cdate',
        'mdate': 'mdate',
        'CODESECTION': 'codesection',
        'nom': 'nom',
        'groupe_naf': 'groupe_naf',
        'section_naf': 'section_naf',
        'zonage_economique': 'zonage_economique',
        'acteur_economique': 'acteur_economique',
        'activite_commerce': 'activite_commerce',
        'origine': 'origine'
    })


    # Renommage spécifique des colonnes pour df_educ
    df_educ = df_educ.rename(columns={
        'Identifiant_de_l_etablissement': 'identifiant_de_l_etablissement',
        'Nom_etablissement': 'nom_etablissement',
        'Type_etablissement': 'type_etablissement',
        'Statut_public_prive': 'statut_public_prive',
        'Adresse_1': 'adresse_1',
        'Adresse_2': 'adresse_2',
        'Adresse_3': 'adresse_3',
        'Code_postal': 'code_postal',
        'Code_commune': 'code_commune',
        'Nom_commune': 'nom_commune',
        'Code_departement': 'code_departement',
        'Code_academie': 'code_academie',
        'Code_region': 'code_region',
        'Ecole_maternelle': 'ecole_maternelle',
        'Ecole_elementaire': 'ecole_elementaire',
        'Voie_generale': 'voie_generale',
        'Voie_technologique': 'voie_technologique',
        'Voie_professionnelle': 'voie_professionnelle',
        'Telephone': 'telephone',
        'Fax': 'fax',
        'Web': 'web',
        'Mail': 'mail',
        'Restauration': 'restauration',
        'Hebergement': 'hebergement',
        'ULIS': 'ulis',
        'Apprentissage': 'apprentissage',
        'Segpa': 'segpa',
        'Section_arts': 'section_arts',
        'Section_cinema': 'section_cinema',
        'Section_theatre': 'section_theatre',
        'Section_sport': 'section_sport',
        'Section_internationale': 'section_internationale',
        'Section_europeenne': 'section_europeenne',
        'Lycee_Agricole': 'lycee_agricole',
        'Lycee_militaire': 'lycee_militaire',
        'Lycee_des_metiers': 'lycee_des_metiers',
        'Post_BAC': 'post_bac',
        'Appartenance_Education_Prioritaire': 'appartenance_education_prioritaire',
        'GRETA': 'greta',
        'SIREN_SIRET': 'siren_siret',
        'Nombre_d_eleves': 'nombre_d_eleves',
        'Fiche_onisep': 'fiche_onisep',
        'position': 'position',
        'Type_contrat_prive': 'type_contrat_prive',
        'Libelle_departement': 'libelle_departement',
        'Libelle_academie': 'libelle_academie',
        'Libelle_region': 'libelle_region',
        'coordX_origine': 'coordx_origine',
        'coordY_origine': 'coordy_origine',
        'epsg_origine': 'epsg_origine',
        'nom_circonscription': 'nom_circonscription',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'precision_localisation': 'precision_localisation',
        'date_ouverture': 'date_ouverture',
        'date_maj_ligne': 'date_maj_ligne',
        'etat': 'etat',
        'ministere_tutelle': 'ministere_tutelle',
        'multi_uai': 'multi_uai',
        'rpi_concentre': 'rpi_concentre',
        'rpi_disperse': 'rpi_disperse',
        'code_nature': 'code_nature',
        'libelle_nature': 'libelle_nature',
        'Code_type_contrat_prive': 'code_type_contrat_prive',
        'PIAL': 'pial',
        'etablissement_mere': 'etablissement_mere',
        'type_rattachement_etablissement_mere': 'type_rattachement_etablissement_mere',
        'code_circonscription': 'code_circonscription',
        'code_zone_animation_pedagogique': 'code_zone_animation_pedagogique',
        'libelle_zone_animation_pedagogique': 'libelle_zone_animation_pedagogique',
        'code_bassin_formation': 'code_bassin_formation',
        'libelle_bassin_formation': 'libelle_bassin_formation'
    })


    df_logement = nettoyer_coordonnees(df_logement)
    df_finance = nettoyer_coordonnees(df_finance)
    df_educ = nettoyer_coordonnees(df_educ)

    # Ajout de la colonne 'annee' pour df_logement (utilise date_de_la_mutation)
    if df_logement['date_de_la_mutation'] is not None:
        df_logement['annee'] = pd.to_datetime(df_logement['date_de_la_mutation'], errors='coerce').dt.year
    else:
        df_logement['annee'] = None

    # Ajout de la colonne 'annee' pour df_finance (utilise date_etablissement en priorité)
    if 'annee' not in df_finance.columns:
        if 'cdate' in df_finance.columns:
            date_series = pd.to_datetime(df_finance['cdate'], errors='coerce', utc=True)
            df_finance['annee'] = date_series.dt.year
        else:
            df_finance['annee'] = None

    # Ajout de la colonne 'annee' pour df_educ (utilise date_maj_ligne)
    if df_educ['date_maj_ligne'] is not None:
        df_educ['annee'] = pd.to_datetime(df_educ['date_maj_ligne'], errors='coerce').dt.year
    else:
        df_educ['annee'] = None

    return df_logement, df_finance, df_educ


@app.route("/", methods=["GET", "POST"])
def index():
    try:
        df_logement, df_finance, df_educ = charger_donnees()

        # Valeurs uniques pour menus déroulants AVANT filtrage
        # Correction ici : vérifier la présence de la colonne avant d'accéder
        if "type_de_local" in df_logement.columns:
            type_biens = sorted(df_logement["type_de_local"].dropna().unique())
        else:
            type_biens = []
        if "type_etablissement" in df_educ.columns:
            types_etab = sorted(df_educ["type_etablissement"].dropna().unique())
        else:
            types_etab = []
        if "statut_public_prive" in df_educ.columns:
            statuts = sorted(df_educ["statut_public_prive"].dropna().unique())
        else:
            statuts = []
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
        # statut_etab = request.form.getlist("statut")
        # type_etab = request.form.getlist("type_etab")

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

        # vérifier la présence de la colonne avant de filtrer
        valeur_fonciere_col = None
        for possible in ["valeur_fonciere", "valeur_fonciere"]: # 'Valeur fonciere' est déjà converti en 'valeur_fonciere'
            if possible in df_logement.columns:
                valeur_fonciere_col = possible
                break

        if valeur_fonciere_col:
            if prix_min_val is not None and prix_max_val is not None:
                df_logement = df_logement[
                    (df_logement[valeur_fonciere_col].astype(float) >= prix_min_val) &
                    (df_logement[valeur_fonciere_col].astype(float) <= prix_max_val)
                ]
            elif prix_min_val is not None and prix_max_val is None:
                df_logement = df_logement[df_logement[valeur_fonciere_col].astype(float) >= prix_min_val]
            elif prix_max_val is not None and prix_min_val is None:
                df_logement = df_logement[df_logement[valeur_fonciere_col].astype(float) <= prix_max_val]
        # Filtrage multi-valeurs pour type_bien (si rien n'est coché, on ne filtre pas)
        if type_bien:
            df_logement = df_logement[df_logement["type_de_local"].isin(type_bien)]

        # Filtrage multi-valeurs pour statut_etab
        # if statut_etab:
        #     df_educ = df_educ[df_educ["statut_public_prive"].isin(statut_etab)]
        # Filtrage multi-valeurs pour type_etab
        # if type_etab:
        #     df_educ = df_educ[df_educ["type_etablissement"].isin(type_etab)]

        # Limite du nombre de points par couche
        MAX_POINTS = 10000

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
                # print(row.get("valeur_fonciere"))
                if pd.notnull(row.get("type_de_local")):
                    popup_infos.append(f"<b>Type</b>: {row.get('type_de_local')}")
                if pd.notnull(row.get("valeur_fonciere")):
                    popup_infos.append(f"<b>Prix</b>: {row.get('valeur_fonciere')} €")

                # Construction de l'adresse
                adresse_parts = []
                if pd.notnull(row.get("numero_de_voie")):
                    adresse_parts.append(str(row.get("numero_de_voie")).replace('.0', '').strip())
                if pd.notnull(row.get("suffixe_du_numero")):
                    adresse_parts.append(str(row.get("suffixe_du_numero")))
                if pd.notnull(row.get("nom_de_la_voie")):
                    adresse_parts.append(str(row.get("nom_de_la_voie")))

                if adresse_parts:
                    popup_infos.append(f"<b>Adresse</b>: {' '.join(adresse_parts)}")

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
