import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, clear_output

df_bordeaux = pd.read_csv("/db/Bordeaux.csv", sep=",", encoding="utf-8")

# Liste des colonnes numériques et catégorielles
colonnes_numeriques = df_bordeaux.select_dtypes(include=["float", "int"]).columns.tolist()
colonnes_categoriels = df_bordeaux.select_dtypes(include=["object"]).columns.tolist()

# Widgets de sélection
x_dropdown = widgets.Dropdown(
    options=df_bordeaux.columns,
    description="Axe X:"
)

y_dropdown = widgets.Dropdown(
    options=colonnes_numeriques,
    description="Axe Y:"
)

graph_type = widgets.RadioButtons(
    options=["Histogramme", "Boxplot", "Nuage de points"],
    description="Type:"
)

# Fonction de mise à jour du graphique
def update_plot(x_col, y_col, chart_type):
    clear_output(wait=True)
    display(open_menu_button)  # Affiche le bouton pour rouvrir le menu
    display(menu_output)       # Affiche la "fenêtre" du menu
    plt.figure(figsize=(10, 5))
    
    if chart_type == "Histogramme":
        sns.histplot(data=df_bordeaux, x=x_col, bins=30)
    elif chart_type == "Boxplot":
        sns.boxplot(data=df_bordeaux, x=x_col, y=y_col)
    elif chart_type == "Nuage de points":
        sns.scatterplot(data=df_bordeaux, x=x_col, y=y_col)
    
    plt.xticks(rotation=45)
    plt.title(f"{chart_type} de {y_col} selon {x_col}")
    plt.tight_layout()
    plt.show()

# Création d'une "fenêtre" pour le menu avec Output
menu_output = widgets.Output()

def show_menu(_=None):
    with menu_output:
        clear_output()
        display(x_dropdown, y_dropdown, graph_type)

# Bouton pour ouvrir le menu
open_menu_button = widgets.Button(description="Ouvrir le menu graphique")

open_menu_button.on_click(show_menu)

# Affichage initial : bouton + fenêtre vide
display(open_menu_button, menu_output)

# Liaison des widgets
widgets.interactive(update_plot, x_col=x_dropdown, y_col=y_dropdown, chart_type=graph_type)