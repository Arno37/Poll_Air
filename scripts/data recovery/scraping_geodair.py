from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import glob
import csv
import json
from selenium.webdriver.common.action_chains import ActionChains

# Dossier où les fichiers seront téléchargés
download_dir = os.path.abspath("downloads")
os.makedirs(download_dir, exist_ok=True)

options = webdriver.ChromeOptions()
options.add_experimental_option("prefs", {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Liste des polluants à traiter (texte exact affiché dans le menu)
polluants = ["NO₂", "O₃", "PM₁₀", "PM₂.₅", "SO₂"]

# Lancer le navigateur
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get("https://www.geodair.fr/donnees/consultation")
time.sleep(5)

for polluant in polluants:
    # Sélectionner le polluant
    try:
        select_polluant = driver.find_element(By.ID, "mat-select-value-1")
        select_polluant.click()
        time.sleep(1)
    except Exception as e:
        print(f"Impossible d'ouvrir le menu du polluant pour {polluant} :", e)
        continue

    try:
        option = driver.find_element(By.XPATH, f"//span[contains(text(), '{polluant}')]")
        ActionChains(driver).move_to_element(option).click().perform()
        print(f"Polluant {polluant} sélectionné.")
        time.sleep(2)
    except Exception as e:
        print(f"Impossible de sélectionner {polluant} :", e)
        continue

    # Cliquer sur le bouton "Exporter en CSV"
    try:
        bouton_csv = driver.find_element(By.XPATH, "//button[contains(., 'Exporter en CSV')]")
        bouton_csv.click()
        print("Bouton 'Exporter en CSV' cliqué.")
    except Exception as e:
        print("Impossible de trouver ou de cliquer sur le bouton CSV :", e)
        continue

    # Attendre le téléchargement (adapter selon la taille du fichier)
    time.sleep(10)

    # Conversion automatique du dernier CSV téléchargé en JSON
    list_csv = glob.glob(os.path.join(download_dir, '*.csv'))
    if list_csv:
        latest_csv = max(list_csv, key=os.path.getctime)
        # Nom du fichier JSON basé sur le polluant
        json_file = os.path.join(download_dir, f"{polluant.replace('₁','1').replace('₂','2').replace('₅','5').replace('₀','0').replace('.','').replace(',','')}.json")
        # Conversion CSV -> JSON
        with open(latest_csv, encoding='utf-8') as f_csv:
            reader = csv.DictReader(f_csv)
            data = list(reader)
        with open(json_file, 'w', encoding='utf-8') as f_json:
            json.dump(data, f_json, ensure_ascii=False, indent=2)
        print(f"Fichier JSON créé : {json_file}")
        os.remove(latest_csv)
        print(f"Fichier CSV supprimé : {latest_csv}")
    else:
        print("Aucun fichier CSV trouvé dans le dossier de téléchargement.")

# Fermer le navigateur
driver.quit()
print("Traitement terminé pour tous les polluants.")