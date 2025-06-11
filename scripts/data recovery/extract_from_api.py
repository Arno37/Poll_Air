import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

DATE_DEBUT = "2025-06-01"
DATE_FIN = "2024-06-01"

URL_PM10 = f"https://admindata.atmo-france.org/api/v2/data/episodes/historique?format=geojson&polluant=PM10&date={DATE_DEBUT}&date_historique={DATE_FIN}"
URL_PM25 = f"https://admindata.atmo-france.org/api/v2/data/episodes/historique?format=geojson&polluant=PM2.5&date={DATE_DEBUT}&date_historique={DATE_FIN}"
URL_NO2 = f"https://admindata.atmo-france.org/api/v2/data/episodes/historique?format=geojson&polluant=NO2&date={DATE_DEBUT}&date_historique={DATE_FIN}"
URL_SO2 = f"https://admindata.atmo-france.org/api/v2/data/episodes/historique?format=geojson&polluant=SO2&date={DATE_DEBUT}&date_historique={DATE_FIN}"
URL_O3 = f"https://admindata.atmo-france.org/api/v2/data/episodes/historique?format=geojson&polluant=O3&date={DATE_DEBUT}&date_historique={DATE_FIN}"
TOKEN = os.getenv("ATMO_SECRET_KEY")

headers = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

try:
    response = requests.get(URL_PM10, headers=headers)
    response.raise_for_status()
    data = response.json()
    with open("data_pm10.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Les données PM10 ont été sauvegardées dans data_pm10.json.")
except requests.RequestException as e:
    print(f"Erreur lors de la récupération des données PM10 : {e}")

try:
    response = requests.get(URL_PM25, headers=headers)
    response.raise_for_status()
    data = response.json()
    with open("data_pm25.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Les données PM2.5 ont été sauvegardées dans data_pm25.json.")
except requests.RequestException as e:
    print(f"Erreur lors de la récupération des données PM2.5 : {e}")

# NO2
try:
    response = requests.get(URL_NO2, headers=headers)
    response.raise_for_status()
    data = response.json()
    with open("data_no2.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Les données NO2 ont été sauvegardées dans data_no2.json.")
except requests.RequestException as e:
    print(f"Erreur lors de la récupération des données NO2 : {e}")

# SO2
try:
    response = requests.get(URL_SO2, headers=headers)
    response.raise_for_status()
    data = response.json()
    with open("data_so2.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Les données SO2 ont été sauvegardées dans data_so2.json.")
except requests.RequestException as e:
    print(f"Erreur lors de la récupération des données SO2 : {e}")

# O3
try:
    response = requests.get(URL_O3, headers=headers)
    response.raise_for_status()
    data = response.json()
    with open("data_o3.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Les données O3 ont été sauvegardées dans data_o3.json.")
except requests.RequestException as e:
    print(f"Erreur lors de la récupération des données O3 : {e}") 