import marimo

__generated_with = "0.16.5"
app = marimo.App(width="medium")


@app.cell
def _():
    # Importation des librairies nécessaires à notre analyse
    import marimo as mo
    import pandas as pd
    import requests
    import tarfile
    from skimpy import skim
    import plotnine as plt
    import patchworklib as pw
    return mo, pd, plt, pw, requests, skim, tarfile


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # **Analyse des appareils de mesures de radioactivité**

    Dans cette partie, nous allons analyser les mesures prises par les appareils utilisés en tenant compte du type d'appareil, de mesure et de l'identifiant de l'appareil. L'objectif étant d'analyser par des courbes de données fonctionnelles ces mesures.
    """
    )
    return


@app.cell
def _():
    # Indication de la requête HTML et du chemin pour enregistrer temporairement le fichier compressé
    url = "https://request.openradiation.net/openradiation_dataset.tar.gz"
    tar_gz_path = "temp/openradiation_dataset.tar.gz"
    return tar_gz_path, url


@app.cell
def _(requests, tar_gz_path, url):
    # Téléchargement du fichier compressé
    print("Téléchargement...")
    response = requests.get(url, stream=True)
    with open(tar_gz_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Téléchargement finie")
    return


@app.cell
def _(tar_gz_path, tarfile):
    # Extraction du contenu du fichier compressé dans le dossier temporaire
    print("Extraction du .tar.gz...")
    with tarfile.open(tar_gz_path, "r:gz") as tar:
        tar.extractall(path="Data")
    print("Extraction du fichier compressé terminé")
    return


@app.cell
def _(pd):
    # Les fichiers sont extraites, maintenant lisons les mesures dans un DataFrame Pandas (23 secondes de lectures)
    dataset = pd.read_csv("Data/out/measurements.csv", 
                sep=";", # séparateur des colonnes
                decimal=".", # séparateur décimal
                header=0) # première ligne en en-tête
    return (dataset,)


@app.cell
def _(dataset):
    # Vérification du succès de l'opération
    print(dataset.head(2))
    return


@app.cell
def _(dataset):
    dataset.shape
    return


@app.cell
def _(mo):
    mo.md(r"""## Consulter les différentes colonnes du DataFrame importé""")
    return


@app.cell
def _(dataset):
    dataset.dtypes
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Commentaire :

    Pour pouvoir analyser les mesures de chaque appareil, nous devons sélectionner ces différentes colonnes :

    - apparatusId
    - apparatusVersion
    - apparatusSensorType
    - apparatusTubeType
    - value
    - startTime
    - endTime
    - measurementEnvironment
    - dateAndTimeOfCreation
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Sélection des colonnes d'intérêts

    Maintenant, qu'on a trouvé les colonnes qui nous intéressent, on va pouvoir les sélectionner.
    """
    )
    return


@app.cell
def _(dataset):
    # Sélection des colonnes
    devices = dataset[["apparatusId", "apparatusVersion", "apparatusSensorType", "apparatusTubeType", 
                      "value", "startTime", "endTime", "measurementEnvironment", "dateAndTimeOfCreation"]]
    return (devices,)


@app.cell
def _(devices):
    # Vérification du succès de l'opération
    devices.head(5)
    return


@app.cell
def _(devices):
    devices.dtypes
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Conversion des types pour les colonnes

    Avant d'aller plus loin, nous devons absolument préciser à notre DataFrame que les colonnes "startTime", "endTime" et "dateAndTimeOfCreation" sont des colonnes de type Datetime. Cela vaut aussi pour les colonnes "measurementEnvironment", "apparatusSensorType" et "apparatusTubeType" où on doit le convertir en catégorie.
    """
    )
    return


@app.cell
def _(devices, pd):
    # Conversion en Datetime pour startTime, endTime et dateAndTimeOfCreation
    for col in ["startTime", "endTime", "dateAndTimeOfCreation"]:
        devices[col] = pd.to_datetime(devices[col], # la colonne concernée
                    format="%Y-%m-%dT%H:%M:%S.%fZ", # format du datetime
                    errors="coerce") # convertir en NaT si erreur dans la conversion

    # Conversion en variable catégorique pour apparatusSensorType, apparatusTubeType et measurementEnvironment
    for col in ["apparatusSensorType", "apparatusTubeType", "measurementEnvironment", "apparatusVersion"] :
        devices[col] = devices[col].astype("category")
    return


@app.cell
def _(devices):
    # Vérification du succès de l'opération
    devices.dtypes
    return


@app.cell
def _(devices):
    # Regardons le résultat sur les 10 premières lignes et sur les 10 dernières lignes
    devices.head(10)
    return


@app.cell
def _(devices):
    devices.tail(10) # Apparition de lignes ne contenant pas d'identifiant pour l'appareil
    return


@app.cell
def _(mo):
    mo.md(r"""### Nettoyage de la colonne concernant l'identifiant""")
    return


@app.cell
def _(devices):
    # Nettoyage de texte
    devices["apparatusId"] = devices["apparatusId"].str.lower() # Tout mettre en minuscule
    devices["apparatusId"] = devices["apparatusId"].str.replace('"', '', regex=False) # Remplacer le caractère '"' par rien
    devices["apparatusId"] = devices["apparatusId"].str.strip() # Enlever toute espace avant ou après la fin de la chaîne 
    return


@app.cell
def _(mo):
    mo.md(r"""### Suppresion des lignes contenant une ou plusieurs valeurs manquantes""")
    return


@app.cell
def _(devices, skim):
    # Observation de la description de nos variables
    skim(devices)
    return


@app.cell
def _(devices):
    # Suppresion des lignes contenant une ou plusieurs valeurs manquantes
    devices_without_na = devices.dropna(axis=0, 
                                       subset = ["apparatusId", 
                                                 "endTime"])
    return (devices_without_na,)


@app.cell
def _(devices, devices_without_na):
    # Taux de suppresion
    lignes_supprimees = devices.shape[0] - devices_without_na.shape[0]
    taux = lignes_supprimees / devices.shape[0]
    print(f"Suppresion des mesures est de : {round(taux * 100, 2)} %")
    print(f"Les dimensions du nouveau DataFrame / ancien DataFrame : {devices_without_na.shape} / {devices.shape} ")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Supprimer les lignes incohérentes 

    Supprimer les lignes incohérentes sont ceux qui possèdent : 

    - une date de début (startTime) supérieure à la date de fin de la mesure (endTime)
    - une valeur de mesure négative (<=0)
    """
    )
    return


@app.cell
def _():
    import datetime as dt
    return (dt,)


@app.cell
def _(dt):
    dt.datetime.now().year
    return


@app.cell
def _(devices_without_na, dt):
    # Filtrer pour n'avoir les lignes contenant des dates cohérentes
    devices_dates = devices_without_na[(devices_without_na["startTime"] < devices_without_na["endTime"]) &     
                                      (devices_without_na["startTime"] <= dt.datetime.now()) & 
                                      (devices_without_na["endTime"] <= dt.datetime.now())]
    return (devices_dates,)


@app.cell
def _(devices_dates):
    devices_dates.head(10)
    return


@app.cell
def _(devices_dates):
    # Vérifier s'il n'y a plus de lignes incohérentes
    devices_dates[devices_dates["startTime"] >= devices_dates["endTime"]]
    return


@app.cell
def _(devices_dates):
    # Filtrer pour n'avoir que des mesures positives
    devices_positive_measures = devices_dates[devices_dates["value"] > 0]
    return (devices_positive_measures,)


@app.cell
def _(devices_positive_measures):
    # Observer s'il n'y a plus de valeurs négatives
    devices_positive_measures["value"].describe()
    return


@app.cell
def _(devices, devices_positive_measures):
    # Taux de suppresion
    lignes_supprimees_measures = devices.shape[0] - devices_positive_measures.shape[0]
    taux_measures = lignes_supprimees_measures / devices.shape[0]
    print(f"Suppresion des mesures est de : {round(taux_measures * 100, 2)} %")
    print(f"Les dimensions du nouveau DataFrame / ancien DataFrame : {devices_positive_measures.shape} / {devices.shape} ")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Analyse exploratoire sur les différentes variables

    Maintenant que nous avons préparé les données, on va analyser ces mesures notamment : 

    - la proportion des mesures prises pour chaque appareil
    - la proportion des caractéristiques de l'appareil de mesure (apparatusVersion / apparatusSensorType)
    - la proportion des mesures prises pour chaque environnement de mesure
    - la création d'un graphique temporel pour chaque environnement de mesure avec la moyenne de celles-ci (l'année dernière et actuelle)
    - la création d'un nuage de dispersion pour observer la durée des mesures et la mesure obtenue (ajout des deux histogrammes de densité)
    - l'étude de la relation entre la version de l'appareil et des mesures obtenues
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Appareils de mesure (toutes année, l'année dernière et cette année)

    Comme on vient de le dire, nous allons calculer la proportion des mesures prises de chaque appareil en utilisant la colonne de l'identifiant. L'objectif est ici de savoir quels sont les appareils qui font le plus de mesure.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ### Tableau des appareils de mesure et des indicateurs
    Dans cette sous partie, nous allons créer un tableau PDF présentant chaque appareil de mesure avec l'effectif total, pour cette année et l'année dernière. La moyenne, médiane et l'écart-type vont être ajoutées pour observer facilement les doses obtenues pour chaque appareil.
    """
    )
    return


@app.cell
def _(devices_positive_measures):
    devices_positive_measures.dtypes
    return


@app.cell
def _(devices_positive_measures):
    # Calculer la porportion pour chaque appareil
    devices_positive_measures["apparatusId"].value_counts(normalize=True)
    return


@app.cell
def _(devices_positive_measures):
    # Calculer l'effectif pour chaque appareil
    devices_positive_measures["apparatusId"].value_counts()
    return


@app.cell
def _(devices_positive_measures):
    # Calculer le tableau contenant l'effectif, la moyenne, la médiane, l'écart-type des doses par appareil
    result = (
        devices_positive_measures.groupby("apparatusId")["value"]
          .agg(
              effectif="count",
              moyenne_dose="mean",
              median_dose="median",
              std_dose="std"
          )
          .reset_index()
    )

    # Ajout de la proportion
    total = result["effectif"].sum()
    result["pourcentage"] = (result["effectif"] / total * 100)

    # Réorganisation des colonnes (mettre pourcentage en 2e position)
    cols = ["apparatusId", "pourcentage", "effectif", "moyenne_dose", "median_dose", "std_dose"]
    result = result[cols]

    # Tri par ordre décroissant selon effectif
    result = result.sort_values(by="effectif", ascending=False).reset_index(drop=True)
    return (result,)


@app.cell
def _(result):
    # Vérificaton du succès de l'opération
    result
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    #### Commentaire : 
    On peut observer que l'appareil "b183cbc2-e56f-4308-862a-3fd17716e5b1" est celui qui a fait le plus de mesure avec 18,30 % pour celles-ci. Cela concerne pour toutes les mesures de toutes les années. Observons maintenant ceux de cette année et de l'année dernière.
    """
    )
    return


@app.cell
def _(devices_positive_measures):
    # Extraire l'année
    devices_positive_measures["annee_endTime"] = devices_positive_measures["endTime"].dt.year

    # Déterminer l'année actuelle et l'année dernière
    annee_actuelle = devices_positive_measures["annee_endTime"].max()
    annee_derniere = annee_actuelle - 1
    return annee_actuelle, annee_derniere


@app.cell
def _(devices_positive_measures):
    devices_positive_measures.head(10)
    return


@app.cell
def _(annee_actuelle, annee_derniere, devices_positive_measures):
    # Filtrage pour pouvoir calculer le nombre de mesures cette année et l'année dernière
    devices_filtre_annee = devices_positive_measures[
            devices_positive_measures["annee_endTime"].isin(
                            [annee_derniere, annee_actuelle]
                                                            )
                ]
    return (devices_filtre_annee,)


@app.cell
def _(devices_filtre_annee):
    # Effectifs par appareil et par année
    effectifs = (
        devices_filtre_annee.groupby(["apparatusId", "annee_endTime"])["value"]
          .agg(effectif="count", 
              moyenne = "mean",
              mediane = "median",
              std = "std")
          .reset_index()
    )
    return (effectifs,)


@app.cell
def _(effectifs):
    # Vérification dus succès de l'opération
    effectifs
    return


@app.cell
def _(effectifs):
    # Pivot pour avoir colonnes séparées année actuelle / année dernière
    pivot = effectifs.pivot(index="apparatusId", 
                            columns="annee_endTime", 
                            values=["effectif", "moyenne", "mediane", "std"]).fillna(0)
    return (pivot,)


@app.cell
def _(pivot):
    # Reset les index de lignes
    pivot.reset_index(inplace=True)
    return


@app.cell
def _(pivot):
    pivot
    return


@app.cell
def _(pd):
    pivot_rename = pd.DataFrame()
    return (pivot_rename,)


@app.cell
def _(pivot, pivot_rename):
    liste_col = pivot.columns

    for col_old in liste_col :
        if col_old[0] == "apparatusId":
            new_name = col_old[0]
        else:
            new_name = f"{col_old[0]}_{col_old[1]}"
        pivot_rename[new_name] = pivot[col_old]
    return


@app.cell
def _(pivot_rename):
    # Vérification de l'ajout des colonnes
    pivot_rename.dtypes
    return


@app.cell
def _(pivot_rename):
    # Vérification des données de calculs 
    pivot_rename
    return


@app.cell
def _(annee_actuelle, annee_derniere, pivot_rename):
    # Calcul des proportions (par rapport au total de l’année)
    total_actuelle = pivot_rename[f"effectif_{annee_actuelle}"].sum()
    total_derniere = pivot_rename[f"effectif_{annee_derniere}"].sum()

    pivot_rename[f"proportion_{annee_actuelle}"] = (pivot_rename[f"effectif_{annee_actuelle}"] / total_actuelle * 100)
    pivot_rename[f"proportion_{annee_derniere}"] = (pivot_rename[f"effectif_{annee_derniere}"] / total_derniere * 100)
    return


@app.cell
def _(pivot_rename):
    # vérification du succès de l'opération
    pivot_rename
    return


@app.cell
def _(pivot_rename, result):
    # Fusionner avec les colonnes annuelles
    tableau_appareil = result.merge(pivot_rename, on="apparatusId", how="left")
    return (tableau_appareil,)


@app.cell
def _(tableau_appareil):
    tableau_appareil
    return


@app.cell
def _(tableau_appareil):
    # Export vers un tableau excel pour l'analyse sur excel
    tableau_appareil.to_excel("Data/out/appareil_mesure.xlsx", 
                              index=False, 
                              sheet_name="appareil_mesure")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ### Top 10 des appareils de mesures et de leurs moyennes de doses observées pour 2024 / 2025

    Maintenant que le tableau a été créé, on va pouvoir facilement l'utiliser dans la suite de notre programme.
    L'objectif est donc d'observer par différents graphiques les mesures obervées par ces appareils.
    Commençons d'abord par le top 10 des appareils qui ont pris le plus de mesures et la moyenne de dose qui ont observé pour 2024 / 2025.
    """
    )
    return


@app.cell
def _(annee_actuelle, annee_derniere, tableau_appareil):
    # ne garder que les dix premiers
    top_10_appareil_annee_derniere = tableau_appareil.sort_values(by=f"effectif_{annee_derniere}", ascending=False).reset_index(drop=True).head(10)[
        ["apparatusId", f"effectif_{annee_derniere}", f"moyenne_{annee_derniere}", f"std_{annee_derniere}", f"proportion_{annee_derniere}"]
        ]

    top_10_appareil_actuel = tableau_appareil.sort_values(by=f"effectif_{annee_actuelle}", ascending=False).reset_index(drop=True).head(10)[["apparatusId", f"effectif_{annee_actuelle}", f"moyenne_{annee_actuelle}", f"std_{annee_actuelle}", f"proportion_{annee_actuelle}"]]

    #print(top_10_appareil_actuel)
    #print(top_10_appareil_annee_derniere)
    return top_10_appareil_actuel, top_10_appareil_annee_derniere


@app.cell
def _(top_10_appareil_annee_derniere):
    # vérification du succès de l'opération
    top_10_appareil_annee_derniere
    return


@app.cell
def _(top_10_appareil_actuel):
    # vérification du succès de l'opération
    top_10_appareil_actuel
    return


@app.cell
def _(mo):
    mo.md(r"""#### Faire deux graphiques à barres (l'un représentant le nombre de mesures prises pour l'année 2025 et de l'autre la moyenne de dose)""")
    return


@app.cell
def _(annee_actuelle, plt, top_10_appareil_actuel):

    p1 = ( 
        plt.ggplot(top_10_appareil_actuel, plt.aes(x=f'reorder(apparatusId, proportion_{annee_actuelle}, ascending=False)', 
                                                   y=f'proportion_{annee_actuelle}')) # Jeu de données 
        + plt.geom_bar(stat = "identity", color="black", fill="blue") # Ajout du type de graphique avec couleur des bordures + barres 

        + plt.labs(title=f"Les dix appareils qui ont fait le plus de mesure ({annee_actuelle})", 
                       x = "Identifiant de l'appareil", y = "Pourcentage") # Ajout des titres 

        + plt.geom_text( plt.aes(label = f"proportion_{annee_actuelle}"), 
                         size = 12, 
                         nudge_y=0.8, 
                         format_string="{:.1f}%") # Ajout des pourcentages (labels), format_string=format de la chaîne de caractère 
        + plt.theme_bw() # Thème utilisé 
        + plt.theme(figure_size=(14, 7), # Taille de la figure 
                            axis_text_x = plt.element_text(angle = 45, hjust = 1), 
                            plot_title=plt.element_text(ha='center'), 
                            panel_grid= plt.element_blank()) # Enlever les carreaux gris 
                    )
    return (p1,)


@app.cell
def _(p1):
    # Afficher
    p1.draw()
    return


@app.cell
def _(annee_actuelle, plt, top_10_appareil_actuel):
    # Premier graphique à barre sur la proportion des mesures
    p2 = (
        plt.ggplot(top_10_appareil_actuel, plt.aes(x=f'reorder(apparatusId, proportion_{annee_actuelle}, ascending=False)', y=f'moyenne_{annee_actuelle}'))
        # Jeu de données
        + plt.geom_bar(stat = "identity",
                       color="black",
                       fill="blue") # Ajout du type de graphique avec couleur des bordures + barres
        + plt.labs(title=f"La moyenne de dose pour chaque appareil ({annee_actuelle})",
                   x = "Identifiant de l'appareil",
                   y = "Moyenne de dose (µSv/h)") # Ajout des titres
        + plt.geom_text(
            plt.aes(label = f"moyenne_{annee_actuelle}"),
            size = 12,
            nudge_y=0.2,
            format_string="{:.2f}") # Ajout des pourcentages (labels), format_string=format de la chaîne de caractère
        + plt.theme_bw() # Thème utilisé
        + plt.theme(figure_size=(14, 7), # Taille de la figure
                    axis_text_x = plt.element_text(angle = 45, hjust = 1),
                    plot_title=plt.element_text(ha='center'),
                    panel_grid= plt.element_blank()) # Enlever les carreaux gris
    )

    return (p2,)


@app.cell
def _(p2):
    p2.draw()
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    Pour créer plusieurs graphiques, il faut avoir deux packages avec une version précise pour que ça fonctionne : 
    - plotnine (0.12.3) : pour la création de graphiques avec la syntaxe ggplot
    - pathworklib (0.6.3) : pour superposer plusieurs graphiques dans la même image
    """
    )
    return


@app.cell
def _(p1, pw):
    g1 = pw.load_ggplot(p1, figsize=(4,4))
    return (g1,)


@app.cell
def _(p2, pw):
    g2 = pw.load_ggplot(p2, figsize=(4,4))
    return (g2,)


@app.cell
def _(g1, g2):
    g12 = (g1|g2)
    return (g12,)


@app.cell
def _(g12):
    g12.savefig()
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""On peut observer que les appareils qui ont pris le plus de mesures sont ceux qui ont des doses très faibles en moyenne entre 0,10 (safecast_id 3220) et 0,37 (safecast_id 1223) µSv/h et entre 6 et 17,2% de mesures prises. Cependant, les appareils dans les quatres dernières positions ont des doses beaucoup plus élevées en moyenne avec notamment 5,50 µSv/h pour l'appareil "88:6b:0f:09:7c:a4".""")
    return


@app.cell
def _(annee_derniere, plt, top_10_appareil_annee_derniere):
    # Pour l'année dernière
    p1_ann_dern = ( 
        plt.ggplot(top_10_appareil_annee_derniere, plt.aes(x=f'reorder(apparatusId, proportion_{annee_derniere}, ascending=False)', 
                                                   y=f'proportion_{annee_derniere}')) # Jeu de données 
        + plt.geom_bar(stat = "identity", color="black", fill="blue") # Ajout du type de graphique avec couleur des bordures + barres 

        + plt.labs(title=f"Les dix appareils qui ont fait le plus de mesure ({annee_derniere})", 
                       x = "Identifiant de l'appareil", y = "Pourcentage") # Ajout des titres 

        + plt.geom_text( plt.aes(label = f"proportion_{annee_derniere}"), 
                         size = 12, 
                         nudge_y=0.8, 
                         format_string="{:.1f}%") # Ajout des pourcentages (labels), format_string=format de la chaîne de caractère 
        + plt.theme_bw() # Thème utilisé 
        + plt.theme(figure_size=(14, 7), # Taille de la figure 
                            axis_text_x = plt.element_text(angle = 45, hjust = 1), 
                            plot_title=plt.element_text(ha='center'), 
                            panel_grid= plt.element_blank()) # Enlever les carreaux gris 
                    )
    return (p1_ann_dern,)


@app.cell
def _(p1_ann_dern):
    p1_ann_dern.draw()
    return


@app.cell
def _(annee_derniere, plt, top_10_appareil_annee_derniere):
    # Premier graphique à barre sur la proportion des mesures
    p2_ann_dern = (
        plt.ggplot(top_10_appareil_annee_derniere, plt.aes(x=f'reorder(apparatusId, proportion_{annee_derniere}, ascending=False)', y=f'moyenne_{annee_derniere}'))
        # Jeu de données
        + plt.geom_bar(stat = "identity",
                       color="black",
                       fill="blue") # Ajout du type de graphique avec couleur des bordures + barres
        + plt.labs(title=f"La moyenne de dose pour chaque appareil ({annee_derniere})",
                   x = "Identifiant de l'appareil",
                   y = "Moyenne de dose (µSv/h)") # Ajout des titres
        + plt.geom_text(
            plt.aes(label = f"moyenne_{annee_derniere}"),
            size = 12,
            nudge_y=0.2,
            format_string="{:.2f}") # Ajout des pourcentages (labels), format_string=format de la chaîne de caractère
        + plt.theme_bw() # Thème utilisé
        + plt.theme(figure_size=(14, 7), # Taille de la figure
                    axis_text_x = plt.element_text(angle = 45, hjust = 1),
                    plot_title=plt.element_text(ha='center'),
                    panel_grid= plt.element_blank()) # Enlever les carreaux gris
    )
    return (p2_ann_dern,)


@app.cell
def _(p2_ann_dern):
    p2_ann_dern.draw()
    return


@app.cell
def _(p1_ann_dern, p2_ann_dern, pw):
    g1_ann_dern = pw.load_ggplot(p1_ann_dern, figsize=(4,4))
    g2_ann_dern = pw.load_ggplot(p2_ann_dern, figsize=(4,4))

    g12_ann_derniere = (g1_ann_dern|g2_ann_dern)
    g12_ann_derniere.savefig()
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Caractéristiques des appareils de mesures

    Ici, nous allons observer les caractéristiques de mesures de toutes les appareils pour savoir quelles sont les types d'appareils les plus utilisées.
    """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""### Pour la version de l'appareil""")
    return


@app.cell
def _(devices_positive_measures):
    # Vérifier si on a des duplications
    devices_positive_measures.duplicated(subset="apparatusId").any()
    return


@app.cell
def _(devices_positive_measures):
    devices_unique = devices_positive_measures[["apparatusId","apparatusVersion", "apparatusSensorType"]]. \
        drop_duplicates(subset="apparatusId")
    return (devices_unique,)


@app.cell
def _(devices_unique):
    # Vérifier si on n'a pas de duplicat
    devices_unique.duplicated(subset="apparatusId").any()
    return


@app.cell
def _(devices_unique):
    print("Le nombre d'appareils uniques dans notre analyse : " +str(devices_unique["apparatusId"].count()))
    return


@app.cell
def _(devices_unique, pd):
    devices_version = pd.DataFrame(devices_unique["apparatusVersion"].value_counts(normalize=True).\
        mul(100).\
        reset_index()
        )
    return (devices_version,)


@app.cell
def _(devices_version):
    devices_version
    return


@app.cell
def _(devices_version):
    devices_version.dtypes
    return


@app.cell
def _():
    return


@app.cell
def _(devices_version, plt):
    graph_version = ( 
        plt.ggplot(devices_version.head(10), plt.aes(x='reorder(apparatusVersion, proportion, ascending=False)', 
                                                   y='proportion')) # Jeu de données 
        + plt.geom_bar(stat = "identity", color="black", fill="purple") # Ajout du type de graphique avec couleur des bordures + barres 

        + plt.labs(title=f"Top 10 des versions des appareils", 
                       x = "Version de l'appareil", y = "Pourcentage") # Ajout des titres 

        + plt.geom_text( plt.aes(label = f"proportion"), 
                         size = 12, 
                         nudge_y=0.8, 
                         format_string="{:.1f}%") # Ajout des pourcentages (labels), format_string=format de la chaîne de caractère 
        + plt.theme_bw() # Thème utilisé 
        + plt.theme(figure_size=(14, 7), # Taille de la figure 
                            axis_text_x = plt.element_text(angle = 45, hjust = 1), 
                            plot_title=plt.element_text(ha='center'), 
                            panel_grid= plt.element_blank()) # Enlever les carreaux gris 
                    )
    return (graph_version,)


@app.cell
def _(graph_version):
    graph_version
    return


@app.cell
def _(mo):
    mo.md(r"""### Le type de senseur de l'appareil""")
    return


@app.cell
def _(devices_unique, pd):
    devices_sensor = pd.DataFrame(devices_unique["apparatusSensorType"].value_counts(normalize=True).\
        mul(100).\
        reset_index()
        )
    return (devices_sensor,)


@app.cell
def _(devices_sensor):
    devices_sensor
    return


@app.cell
def _(mo):
    mo.md(r"""On observe que tous les appareils de mesures entre 2024 et 2025 ont des senseurs de type **geiger**.""")
    return


@app.cell
def _(mo):
    mo.md(r"""## Observation des mesures prises selon l'environnement de mesure""")
    return


@app.cell
def _(devices_positive_measures, pd):
    devices_environment = (
        pd.DataFrame(
            devices_positive_measures["measurementEnvironment"]
            .value_counts(normalize=True)
            .mul(100)
            .reset_index()
        )
    )
    return (devices_environment,)


@app.cell
def _(devices_environment):
    devices_environment
    return


@app.cell
def _(devices_positive_measures):
    devices_positive_measures.isna()["measurementEnvironment"].value_counts(normalize=True) * 100
    return


@app.cell
def _(devices_environment, plt):
    # Création du graphique 
    graph_environ = ( 
        plt.ggplot(devices_environment, plt.aes(x='reorder(measurementEnvironment, proportion, ascending=False)', 
                                                   y='proportion')) # Jeu de données 
        + plt.geom_bar(stat = "identity", color="black", fill="red") # Ajout du type de graphique avec couleur des bordures + barres 

        + plt.labs(title="Environnement de mesure des appareils", 
                       x = "Version de l'appareil", y = "Pourcentage") # Ajout des titres 

        + plt.geom_text( plt.aes(label = f"proportion"), 
                         size = 12, 
                         nudge_y=0.8, 
                         format_string="{:.1f}%") # Ajout des pourcentages (labels), format_string=format de la chaîne de caractère 
        + plt.theme_bw() # Thème utilisé 
        + plt.theme(figure_size=(14, 7), # Taille de la figure 
                            axis_text_x = plt.element_text(hjust = 0.5, size=12), 
                            plot_title=plt.element_text(ha='center'), 
                            panel_grid= plt.element_blank()) # Enlever les carreaux gris 
                    )
    return (graph_environ,)


@app.cell
def _(graph_environ):
    # Visualisation graphique
    graph_environ
    return


@app.cell
def _(devices_positive_measures, plt):
    # Création du boxplot pour chaque environnement de mesure
    (
        plt.ggplot(devices_positive_measures)
        + plt.geom_boxplot(
            plt.aes(x="factor(measurementEnvironment)", y="value"), fill="lightblue"
        )
    )
    return


@app.cell
def _(devices_positive_measures, plt):
    # Création du boxplot pour chaque environnement de mesure filtrant sur les mesures inférieures à 50
    (
        plt.ggplot(devices_positive_measures.dropna(subset="measurementEnvironment")[(devices_positive_measures["value"] < 10)])
        + plt.geom_boxplot(
            plt.aes(x="factor(measurementEnvironment)", y="value"), fill="lightblue"
        )
    )
    return


@app.cell
def _(mo):
    mo.md(r"""Cela rends très illisibles et nous devrions peut-être observer les indicateurs numériques que le boxplot pour faciliter l'analyse quantitative.""")
    return


@app.cell
def _(devices_positive_measures):
    # Calcul de la moyenne, médiane et écart-type de ces mesures 
    indicateurs_environment_dose = (
        devices_positive_measures.groupby("measurementEnvironment")["value"]
          .agg(effectif="count", 
              moyenne = "mean",
              mediane = "median",
              std = "std",
              Q1=lambda x: x.quantile(0.25),
              Q3=lambda x: x.quantile(0.75),
              P99 = lambda x: x.quantile(0.99))
          .reset_index()
    )
    return (indicateurs_environment_dose,)


@app.cell
def _(indicateurs_environment_dose):
    # Vérification du succès de l'opération
    indicateurs_environment_dose
    return


@app.cell
def _(mo):
    mo.md(r"""## Observation des durées de mesures""")
    return


@app.cell
def _(devices_positive_measures):
    # Ajout de la durée de mesure
    # Calcul de la différence en minutes
    devices_positive_measures["duree_minutes"] = (devices_positive_measures["endTime"] - devices_positive_measures["startTime"]).dt.total_seconds() / 60
    return


@app.cell
def _(devices_positive_measures):
    # Vérification du succès de l'opération
    devices_positive_measures.head(5)[["apparatusId", "duree_minutes"]]
    return


@app.cell
def _(devices_positive_measures):
    # Calcul de la moyenne, médiane et écart-type de ces mesures 
    indicateurs_environment_duree = (
        devices_positive_measures.groupby("measurementEnvironment")["duree_minutes"]
          .agg(effectif="count", 
              moyenne = "mean",
              mediane = "median",
              std = "std",
              Q1=lambda x: x.quantile(0.25),
              Q3=lambda x: x.quantile(0.75),
              P99 = lambda x: x.quantile(0.99))
          .reset_index()
    )
    return (indicateurs_environment_duree,)


@app.cell
def _(indicateurs_environment_duree):
    indicateurs_environment_duree
    return


@app.cell
def _(devices_positive_measures):
    # Calcul de la moyenne, médiane et écart-type de ces mesures 
    indicateurs_duree = (
        devices_positive_measures["duree_minutes"]
          .agg(effectif="count", 
              moyenne = "mean",
              mediane = "median",
              std = "std",
              Q1=lambda x: x.quantile(0.25),
              Q3=lambda x: x.quantile(0.75),
              P99 = lambda x: x.quantile(0.99))
          .reset_index()
    )
    return (indicateurs_duree,)


@app.cell
def _(indicateurs_duree):
    indicateurs_duree
    return


@app.cell
def _(mo):
    mo.md(r"""## Observation des doses des mesures prises""")
    return


@app.cell
def _(devices_positive_measures):
    # Calcul de la moyenne, médiane et écart-type de ces mesures 
    indicateurs_dose = (
        devices_positive_measures["value"]
          .agg(effectif="count", 
              moyenne = "mean",
              mediane = "median",
              std = "std",
              Q1=lambda x: x.quantile(0.25),
              Q3=lambda x: x.quantile(0.75),
              P99 = lambda x: x.quantile(0.99))
          .reset_index()
    )
    return (indicateurs_dose,)


@app.cell
def _(indicateurs_dose):
    indicateurs_dose
    return


@app.cell
def _(mo):
    mo.md(r"""## Analyse des doses obtenues sur l'année 2024/2025 pour chaque environnement de mesure""")
    return


@app.cell
def _(devices_filtre_annee, devices_positive_measures):
    # Extraire l'année et le mois
    devices_filtre_annee["mois_endTime"] = devices_positive_measures["endTime"].dt.month
    return


@app.cell
def _(devices_filtre_annee):
    # Moyenne par environnement, année et mois
    moyenne_doses_2024_2025 = (
        devices_filtre_annee
            .groupby(["measurementEnvironment", "annee_endTime", "mois_endTime"], as_index=False)["value"]
            .mean()
    )
    return (moyenne_doses_2024_2025,)


@app.cell
def _(moyenne_doses_2024_2025):
    # Vérification du succès de l'opération
    moyenne_doses_2024_2025
    return


@app.cell
def _(moyenne_doses_2024_2025, plt):
    graph_dose_temporelle_1 = (
        plt.ggplot(moyenne_doses_2024_2025, plt.aes(x="mois_endTime", y="value", color="factor(annee_endTime)", group="annee_endTime"))
        + plt.geom_line(size=1)
        + plt.geom_point(size=2)
        + plt.facet_wrap("~measurementEnvironment", scales="free_y")
        + plt.labs(
            x="Date (mois)",
            y="Moyenne mensuelle de value",
            color="Année",
            title="Évolution mensuelle de la dose par environnement"
        )
        + plt.scale_x_datetime(date_labels="%b %Y", date_breaks="2 months")
        + plt.theme_bw()
        + plt.theme(
            figure_size=(10, 5),
            axis_text_x=plt.element_text(rotation=45, ha="right"),
            subplots_adjust={"wspace": 0.25}
        )
    )
    return (graph_dose_temporelle_1,)


@app.cell
def _(graph_dose_temporelle_1):
    graph_dose_temporelle_1
    return


@app.cell
def _(moyenne_doses_2024_2025, plt):
    # Utilisation de facet_grid
    graph_dose_temporelle_2 = (
        plt.ggplot(moyenne_doses_2024_2025, plt.aes(x="mois_endTime", y="value"))
        + plt.geom_line(size=1, color="blue")
        + plt.geom_point(size=2, color="blue")
        + plt.facet_grid("measurementEnvironment~annee_endTime", scales="free_y")
        + plt.labs(
            x="Date (mois)",
            y="Moyenne mensuelle de value",
            color="Année",
            title="Évolution mensuelle de la dose par environnement"
        )
        + plt.scale_x_datetime(date_labels="%b %Y", date_breaks="2 months")
        + plt.theme_bw()
        + plt.theme(
            figure_size=(10, 5),
            axis_text_x=plt.element_text(rotation=45, ha="right"),
            subplots_adjust={"wspace": 0.25}
        )
    )
    return (graph_dose_temporelle_2,)


@app.cell
def _(graph_dose_temporelle_2):
    graph_dose_temporelle_2
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Observation des courbes des appareils selon l'environnement de mesure""")
    return


@app.cell
def _(devices_positive_measures):
    devices_positive_measures.dtypes
    return


if __name__ == "__main__":
    app.run()
