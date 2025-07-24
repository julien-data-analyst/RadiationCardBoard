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
    return mo, pd, requests, tarfile


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


if __name__ == "__main__":
    app.run()
