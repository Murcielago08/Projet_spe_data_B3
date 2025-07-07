import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt
from sklearn.neighbors import BallTree
import networkx as nx
from geopy.distance import geodesic
from collections import defaultdict

# 🔧 Fonction utilitaire pour BallTree
def count_neighbors(tree, points, radius_m):
    radius = radius_m / 6371000
    counts = tree.query_radius(points, r=radius, count_only=True)
    return counts

# =====================================
# 📝 1. Charger les données immobilières
# =====================================
df = pd.read_csv("./db/Bordeaux.csv", sep=";", encoding="utf-8", skiprows=lambda i: i > 0 and np.random.rand() > 0.10)
print("DVF chargé")

# Nettoyer lat/lon
df = df.dropna(subset=["valeur_fonciere", "latitude", "longitude"]).reset_index(drop=True)
df['lat_rad'] = np.deg2rad(df['latitude'])
df['lon_rad'] = np.deg2rad(df['longitude'])
logements_coords = df[['lat_rad', 'lon_rad']].to_numpy()

# =====================================
# 📝 2. Charger commerces et écoles
# =====================================
commerces = pd.read_csv("./db/fi_etabl_p.csv", sep=";", encoding="utf-8", skiprows=lambda i: i > 0 and np.random.rand() > 0.1)
ecoles = pd.read_csv("./db/educ_bordeaux.csv", sep=";", encoding="utf-8", skiprows=lambda i: i > 0 and np.random.rand() > 0.1)

# Nettoyer Geo Point commerces
if 'Geo Point' in commerces.columns:
    geo_split = commerces['Geo Point'].str.extract(r'([0-9\.\-]+),\s*([0-9\.\-]+)')
    commerces['latitude'] = geo_split[0].astype(float)
    commerces['longitude'] = geo_split[1].astype(float)
else:
    raise KeyError("Geo Point manquant dans commerces")

# Convertir en radians
for df_tmp in [commerces, ecoles]:
    df_tmp['lat_rad'] = np.deg2rad(df_tmp['latitude'])
    df_tmp['lon_rad'] = np.deg2rad(df_tmp['longitude'])

commerces_coords = commerces[['lat_rad', 'lon_rad']].to_numpy()
ecoles_coords = ecoles[['lat_rad', 'lon_rad']].to_numpy()

# =====================================
# 📝 3. Charger et préparer les arrêts de bus (NetworkX)
# =====================================
stops = pd.read_csv('./db/stops.txt')
stops['lat_rad'] = np.deg2rad(stops['stop_lat'])
stops['lon_rad'] = np.deg2rad(stops['stop_lon'])
stops_coords = stops[['lat_rad', 'lon_rad']].to_numpy()

# Créer BallTree pour stops
tree_stops = BallTree(stops_coords, metric='haversine')

# =====================================
# 📝 4. Créer BallTrees commerces, écoles
# =====================================
tree_commerces = BallTree(commerces_coords, metric='haversine')
tree_ecoles = BallTree(ecoles_coords, metric='haversine')

# =====================================
# 🔥 5. Comptage des voisins pour chaque logement
# =====================================
print("Calcul des features spatiales...")
df['n_commerces_1000m'] = count_neighbors(tree_commerces, logements_coords, 1000)
df['n_ecoles_1000m'] = count_neighbors(tree_ecoles, logements_coords, 1000)
df['n_stops_1000m'] = count_neighbors(tree_stops, logements_coords, 1000)

# =====================================
# 📝 6. Encodage one-hot et préparation des features
# =====================================
df = pd.get_dummies(df, columns=["code_type_local", "type_local"], drop_first=True)

# Réduire la taille pour tests rapides
df = df.sample(frac=0.10, random_state=42).reset_index(drop=True)

X = df[["surface_reelle_bati", "nombre_pieces_principales", "surface_terrain",
        "code_postal", "n_commerces_1000m", "n_ecoles_1000m", "n_stops_1000m"] +
       [col for col in df.columns if col.startswith("code_type_local_") or col.startswith("type_local_")]].fillna(0)

y = df["valeur_fonciere"]

# =====================================
# 📝 7. Split train/test
# =====================================
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# =====================================
# 📝 8. Modèle LightGBM (alternative Random Forest)
# =====================================
model = RandomForestRegressor(n_estimators=2000)
model.fit(X_train, y_train)

# =====================================
# 📝 9. Prédictions et évaluation
# =====================================
y_pred = model.predict(X_test)
y_train_pred = model.predict(X_train)

mae_test = mean_absolute_error(y_test, y_pred)
mae_train = mean_absolute_error(y_train, y_train_pred)
r2 = r2_score(y_test, y_pred)

# 🔢 MAE en pourcentage du prix moyen (test set)
mae_test_pct = (mae_test / y_test.mean()) * 100

print(f"MAE (Mean Absolute Error) - Test : {mae_test:.2f}")
print(f"MAE (Mean Absolute Error) - Train : {mae_train:.2f}")
print(f"MAE Test as % of mean valeur_fonciere : {mae_test_pct:.2f}%")
print(f"R² score : {r2:.4f}")


# =====================================
# 📝 10. Importance des variables
# =====================================
importances = pd.Series(model.feature_importances_, index=X.columns)
importances.sort_values(ascending=False).plot(kind="bar", title="Importance des variables")
plt.tight_layout()
plt.show()
