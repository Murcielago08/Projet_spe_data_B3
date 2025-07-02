import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# 1. Charger les données
df = pd.read_csv("dvf_clean.csv")

# ...existing code...
# Encodage one-hot pour code_type_local et type_local
df = pd.get_dummies(df, columns=["code_type_local", "type_local"], drop_first=True)
# 2. Exploration rapide
print(df.head())
print(df.info())
print(df.describe())
print("Types de bâtiments présents dans le dataset :")
print("Moyenne des prix (valeur_fonciere) :", df["valeur_fonciere"].mean())
# 3. Nettoyer les données
# Retirer les colonnes inutiles ou vides
df = df.dropna(subset=["valeur_fonciere"])  # retire les lignes sans prix
df = df.sample(frac=0.01, random_state=42).reset_index(drop=True)
cols_to_use = [
    "surface_reelle_bati", "nombre_pieces_principales",
    "surface_terrain", "code_postal", "code_type_local", "type_local"
]

# Préparation des features finales
X = df[["surface_reelle_bati", "nombre_pieces_principales", "surface_terrain", "code_postal"] + 
       [col for col in df.columns if col.startswith("code_type_local_") or col.startswith("type_local_")]].fillna(0)

y = df["valeur_fonciere"]
# ...existing code...
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 6. Création du modèle Random Forest
model = RandomForestRegressor(n_estimators=50)
model.fit(X_train, y_train)
# 6. Création du modèle Random Forest
model = RandomForestRegressor(n_estimators=20)
model.fit(X_train, y_train)

# 7. Prédictions
y_pred = model.predict(X_test)

# 8. Évaluation
mae_test = mean_absolute_error(y_test, y_pred)
y_train_pred = model.predict(X_train)
mae_train = mean_absolute_error(y_train, y_train_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE (Mean Absolute Error) - Test : {mae_test}")
print(f"MAE (Mean Absolute Error) - Train : {mae_train}")
print(f"R² score : {r2}")
# 9. Réduire la taille de la base pour les tests (prend 1% des données)
importances = pd.Series(model.feature_importances_, index=X.columns)
importances.sort_values(ascending=False).plot(kind="bar", title="Importance des variables")