import marimo

__generated_with = "0.14.13"
app = marimo.App(width="medium")


@app.cell
def _():
    # Importation des librairies nécessaires à notre analyse
    import marimo as mo
    import pandas as pd
    import plotnine as plt
    import requests
    import tarfile
    from skimpy import skim
    return mo, pd, requests, skim, tarfile


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
    mo.md(r"""### Suppresion des lignes contenant une ou plusieurs valeurs manquantes""")
    return


@app.cell
def _(devices, skim):
    # Observation de la description des nos variables
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
def _(devices_without_na):
    # Filtrer pour n'avoir les lignes contenant des dates cohérentes
    devices_dates = devices_without_na[devices_without_na["startTime"] < devices_without_na["endTime"]]
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
    - la proportion des mesures prises pour chaque environnement de mesure
    - l'étude de la relation entre l'environnement et les mesures obtenues (calcul de la relation entre les deux variables)
    - la proportion des caractéristiques de l'appareil de mesure (apparatusVersion / apparatusSensorType)
    - la création d'un graphique temporel pour chaque environnement de mesure avec la moyenne de celles-ci (en 2024 ou 2025 ?)
    - la création d'un nuage de dispersion pour observer la durée des mesures et la mesure obtenue (ajout des deux histogrammes de densité)
    - l'étude de la relation entre la version de l'appareil et des mesures obtenues
    """
    )
    return


if __name__ == "__main__":
    app.run()
