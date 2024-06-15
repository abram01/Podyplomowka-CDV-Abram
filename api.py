import requests

BAZA_URL = "https://api.gios.gov.pl/pjp-api/rest/"

def pobierz_stacje():
    odpowiedz = requests.get(BAZA_URL + "station/findAll")
    odpowiedz.raise_for_status()
    return odpowiedz.json()

def pobierz_czujniki(id_stacji):
    odpowiedz = requests.get(BAZA_URL + f"station/sensors/{id_stacji}")
    odpowiedz.raise_for_status()
    return odpowiedz.json()

def pobierz_dane(id_czujnika):
    odpowiedz = requests.get(BAZA_URL + f"data/getData/{id_czujnika}")
    odpowiedz.raise_for_status()
    return odpowiedz.json()

def pobierz_indeks_jakosci_powietrza(id_stacji):
    odpowiedz = requests.get(BAZA_URL + f"aqindex/getIndex/{id_stacji}")
    odpowiedz.raise_for_status()
    return odpowiedz.json()
