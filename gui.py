import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from datetime import datetime
import requests
import certifi
import database
import visualization
import analysis
import folium
import webbrowser
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Testowanie połączenia z API
response = requests.get('https://api.gios.gov.pl', verify=certifi.where())
print(response.text)

class WejscieZPlaceholder(ttk.Entry):
    """
    Klasa rozszerzająca ttk.Entry, dodająca obsługę placeholdera.

    Attributes:
        placeholder (str): Tekst placeholdera.
        placeholder_color (str): Kolor placeholdera.
        default_fg_color (str): Domyślny kolor tekstu.
    """

    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey', *args, **kwargs):
        """
        Inicjalizuje obiekt klasy WejscieZPlaceholder.

        Args:
            master: Rodzic widgetu.
            placeholder (str): Tekst placeholdera.
            color (str): Kolor placeholdera.
        """
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['foreground']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        """
        Ustawia placeholder w polu tekstowym.

        Returns:
            None
        """
        self.insert(0, self.placeholder)
        self['foreground'] = self.placeholder_color

    def foc_in(self, *args):
        """
        Obsługuje zdarzenie FocusIn, usuwając placeholder.

        Args:
            *args: Argumenty zdarzenia.

        Returns:
            None
        """
        if self.get() == self.placeholder:
            self.delete(0, 'end')
            self['foreground'] = self.default_fg_color

    def foc_out(self, *args):
        """
        Obsługuje zdarzenie FocusOut, przywracając placeholder.

        Args:
            *args: Argumenty zdarzenia.

        Returns:
            None
        """
        if not self.get():
            self.put_placeholder()

class AplikacjaJakosciPowietrza:
    """
    Główna klasa aplikacji monitorującej jakość powietrza.

    Attributes:
        root (tk.Tk): Główne okno aplikacji.
        stacja_id (str): Identyfikator wybranej stacji pomiarowej.
        czujnik_id (str): Identyfikator wybranego czujnika pomiarowego.
    """

    def __init__(self, root):
        """
        Inicjalizuje obiekt klasy AplikacjaJakosciPowietrza.

        Args:
            root (tk.Tk): Główne okno aplikacji.

        Returns:
            None
        """
        self.root = root
        self.root.title("Monitorowanie Jakości Powietrza")
        self.utworz_widzety()
        database.reset_baza()
        database.utworz_tabele()
        self.stacja_id = None
        self.czujnik_id = None
        self.geolocator = Nominatim(user_agent="geoapiExercises")

    def utworz_widzety(self):
        """
        Tworzy widżety interfejsu użytkownika.

        Returns:
            None
        """
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        stacja_frame = ttk.Frame(main_frame, padding="5")
        stacja_frame.pack(fill=tk.X)

        self.etkieta_stacji = ttk.Label(stacja_frame, text="Stacja Pomiarowa:")
        self.etkieta_stacji.pack(side=tk.LEFT, padx=5, pady=5)

        self.kombobox_stacji = ttk.Combobox(stacja_frame)
        self.kombobox_stacji.pack(fill=tk.X, padx=5, pady=5, expand=True)
        self.kombobox_stacji.bind("<<ComboboxSelected>>", self.wybor_stacji)

        czujnik_frame = ttk.Frame(main_frame, padding="5")
        czujnik_frame.pack(fill=tk.X)

        self.etkieta_czujnika = ttk.Label(czujnik_frame, text="Stanowisko Pomiarowe:")
        self.etkieta_czujnika.pack(side=tk.LEFT, padx=5, pady=5)

        self.kombobox_czujnika = ttk.Combobox(czujnik_frame)
        self.kombobox_czujnika.pack(fill=tk.X, padx=5, pady=5, expand=True)
        self.kombobox_czujnika.bind("<<ComboboxSelected>>", self.wybor_czujnika)

        data_frame = ttk.Frame(main_frame, padding="5")
        data_frame.pack(fill=tk.X)

        self.etkieta_od = ttk.Label(data_frame, text="Data początkowa (yyyy-mm-dd):")
        self.etkieta_od.pack(side=tk.LEFT, padx=5, pady=5)

        self.wejscie_od = ttk.Entry(data_frame)
        self.wejscie_od.insert(0, "2020-01-01")
        self.wejscie_od.pack(fill=tk.X, padx=5, pady=5, expand=True)

        self.etkieta_do = ttk.Label(data_frame, text="Data końcowa (yyyy-mm-dd):")
        self.etkieta_do.pack(side=tk.LEFT, padx=5, pady=5)

        self.wejscie_do = ttk.Entry(data_frame)
        self.wejscie_do.insert(0, "2025-01-01")
        self.wejscie_do.pack(fill=tk.X, padx=5, pady=5, expand=True)

        przyciski_frame = ttk.Frame(main_frame, padding="5")
        przyciski_frame.pack(fill=tk.X)

        self.przycisk_wykres = ttk.Button(przyciski_frame, text="Pokaż Wykres", command=self.pokaz_wykres)
        self.przycisk_wykres.pack(side=tk.LEFT, padx=5, pady=5)

        self.przycisk_analityka = ttk.Button(przyciski_frame, text="Analizuj Dane", command=self.analizuj_dane)
        self.przycisk_analityka.pack(side=tk.LEFT, padx=5, pady=5)

        self.przycisk_mapa = ttk.Button(przyciski_frame, text="Pokaż Mapę", command=self.pokaz_mape)
        self.przycisk_mapa.pack(side=tk.LEFT, padx=5, pady=5)

        self.laduj_stacje()
        self.utworz_filtrowanie()

    def utworz_filtrowanie(self):
        """
        Tworzy widżety do filtrowania stacji pomiarowych.

        Returns:
            None
        """
        filtr_frame = ttk.Frame(self.root, padding="10")
        filtr_frame.pack(fill=tk.X)

        self.etkieta_filtr = ttk.Label(filtr_frame, text="Filtruj stacje:")
        self.etkieta_filtr.pack(side=tk.LEFT, padx=5, pady=5)

        self.wejscie_miasto = WejscieZPlaceholder(filtr_frame, placeholder="Nazwa miasta")
        self.wejscie_miasto.pack(fill=tk.X, padx=5, pady=5, expand=True)

        self.przycisk_filtr_miasto = ttk.Button(filtr_frame, text="Filtruj po mieście", command=self.filtruj_po_miescie)
        self.przycisk_filtr_miasto.pack(side=tk.LEFT, padx=5, pady=5)

        promien_frame = ttk.Frame(self.root, padding="10")
        promien_frame.pack(fill=tk.X)

        self.etkieta_promien = ttk.Label(promien_frame, text="Promień wyszukiwania (km):")
        self.etkieta_promien.pack(side=tk.LEFT, padx=5, pady=5)

        self.wejscie_promien = WejscieZPlaceholder(promien_frame, placeholder="Promień (km)")
        self.wejscie_promien.pack(fill=tk.X, padx=5, pady=5, expand=True)

        self.wejscie_lokalizacja = WejscieZPlaceholder(promien_frame, placeholder="Lokalizacja (np. Collegium Da Vinci)")
        self.wejscie_lokalizacja.pack(fill=tk.X, padx=5, pady=5, expand=True)

        self.wejscie_lat = WejscieZPlaceholder(promien_frame, placeholder="Szerokość geograficzna (opcjonalnie)")
        self.wejscie_lat.pack(fill=tk.X, padx=5, pady=5, expand=True)

        self.wejscie_lon = WejscieZPlaceholder(promien_frame, placeholder="Długość geograficzna (opcjonalnie)")
        self.wejscie_lon.pack(fill=tk.X, padx=5, pady=5, expand=True)

        self.przycisk_filtr_promien = ttk.Button(promien_frame, text="Filtruj po promieniu", command=self.filtruj_po_promieniu)
        self.przycisk_filtr_promien.pack(side=tk.LEFT, padx=5, pady=5)

    def laduj_stacje(self):
        """
        Ładuje listę stacji pomiarowych z API GIOŚ.

        Returns:
            None
        """
        try:
            response = requests.get("https://api.gios.gov.pl/pjp-api/rest/station/findAll", verify=certifi.where())
            response.raise_for_status()
            self.stacje = {str(stacja['id']): stacja for stacja in response.json()}
            self.kombobox_stacji['values'] = [stacja['stationName'] for stacja in self.stacje.values()]
        except requests.RequestException as e:
            messagebox.showerror("Błąd", f"Nie udało się załadować stacji: {e}")

    def wybor_stacji(self, event):
        """
        Obsługuje wybór stacji pomiarowej przez użytkownika.

        Args:
            event: Zdarzenie wyboru z Combobox.

        Returns:
            None
        """
        stacja_nazwa = self.kombobox_stacji.get()
        self.stacja_id = next((id for id, stacja in self.stacje.items() if stacja['stationName'] == stacja_nazwa), None)
        if self.stacja_id:
            try:
                response = requests.get(f"https://api.gios.gov.pl/pjp-api/rest/station/sensors/{self.stacja_id}", verify=certifi.where())
                response.raise_for_status()
                self.czujniki = response.json()
                self.kombobox_czujnika['values'] = [czujnik['param']['paramName'] for czujnik in self.czujniki]
            except requests.RequestException as e:
                messagebox.showerror("Błąd", f"Nie udało się załadować czujników: {e}")

    def wybor_czujnika(self, event):
        """
        Obsługuje wybór stanowiska pomiarowego przez użytkownika.

        Args:
            event: Zdarzenie wyboru z Combobox.

        Returns:
            None
        """
        czujnik_nazwa = self.kombobox_czujnika.get()
        czujnik = next((czujnik for czujnik in self.czujniki if czujnik['param']['paramName'] == czujnik_nazwa), None)
        if czujnik:
            self.czujnik_id = czujnik['id']
            try:
                response = requests.get(f"https://api.gios.gov.pl/pjp-api/rest/data/getData/{self.czujnik_id}", verify=certifi.where())
                response.raise_for_status()
                dane = response.json()
                self.dane = [(entry['date'], entry['value']) for entry in dane['values']]
                messagebox.showinfo("Informacja", "Dane zostały załadowane.")
                self.zapisz_dane_do_bazy(self.czujnik_id, czujnik['param']['paramName'], dane)
            except requests.RequestException as e:
                messagebox.showerror("Błąd", f"Nie udało się załadować danych: {e}")

    def zapisz_dane_do_bazy(self, id_czujnika, nazwa, dane):
        """
        Zapisuje dane pomiarowe do bazy danych.

        Args:
            id_czujnika (int): Unikalny identyfikator czujnika.
            nazwa (str): Nazwa czujnika.
            dane (dict): Dane pomiarowe w formacie JSON.

        Returns:
            None
        """
        try:
            database.zapisz_czujnik(id_czujnika, nazwa)
            for entry in dane['values']:
                database.zapisz_dane((id_czujnika, entry['date'], entry['value']))
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się zapisać danych do bazy: {e}")

    def pokaz_wykres(self):
        """
        Wyświetla wykres danych pomiarowych dla wybranego czujnika.

        Returns:
            None
        """
        try:
            if self.czujnik_id is not None:
                data_od = self.wejscie_od.get()
                data_do = self.wejscie_do.get()
                dane = database.pobierz_dane(self.czujnik_id, data_od, data_do)
                visualization.wykres_danych(dane, data_od, data_do)
            else:
                messagebox.showerror("Błąd", "Nie wybrano stanowiska pomiarowego.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyświetlić wykresu: {e}")

    def analizuj_dane(self):
        """
        Przeprowadza analizę danych pomiarowych i wyświetla wyniki.

        Returns:
            None
        """
        try:
            if self.czujnik_id is not None:
                wyniki = analysis.analizuj_dane(self.dane)
                if wyniki:
                    messagebox.showinfo("Analiza danych",
                                        f"Min: {wyniki['min']} ({wyniki['min_data']})\n"
                                        f"Max: {wyniki['max']} ({wyniki['max_data']})\n"
                                        f"Średnia: {wyniki['srednia']}\n"
                                        f"Trend: {wyniki['trend']}")
                else:
                    messagebox.showwarning("Brak danych", "Brak wystarczających danych do analizy.")
            else:
                messagebox.showerror("Błąd", "Nie wybrano stanowiska pomiarowego.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się przeanalizować danych: {e}")

    def pokaz_mape(self):
        """
        Wyświetla mapę z zaznaczonymi stacjami pomiarowymi. Wybrana stacja jest zaznaczona na czerwono.

        Returns:
            None
        """
        try:
            mapa = folium.Map(location=[52.2296756, 21.0122287], zoom_start=6)
            lokalizacja_centralna = None
            for stacja in self.stacje.values():
                if str(stacja['id']) == self.stacja_id:
                    marker_color = "red"
                    lokalizacja_centralna = (stacja['gegrLat'], stacja['gegrLon'])
                else:
                    marker_color = "blue"
                folium.Marker(
                    location=[stacja['gegrLat'], stacja['gegrLon']],
                    popup=stacja['stationName'],
                    icon=folium.Icon(color=marker_color, icon="info-sign"),
                ).add_to(mapa)
            if lokalizacja_centralna:
                promien = self.wejscie_promien.get()
                try:
                    if promien:
                        promien = float(promien)
                        folium.Circle(
                            location=lokalizacja_centralna,
                            radius=promien * 1000,
                            color='green',
                            fill=True,
                            fill_color='green'
                        ).add_to(mapa)
                except ValueError:
                    messagebox.showerror("Błąd", "Wartość promienia nie jest poprawną liczbą.")
            mapa_file = "mapa.html"
            mapa.save(mapa_file)
            absolute_path = os.path.abspath(mapa_file)
            webbrowser.open(f"file://{absolute_path}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się wyświetlić mapy: {e}")

    def filtruj_po_miescie(self):
        """
        Filtruje stacje pomiarowe na podstawie nazwy miasta.

        Returns:
            None
        """
        miasto = self.wejscie_miasto.get()
        stacje_filtr = [stacja['stationName'] for stacja in self.stacje.values() if stacja['city']['name'].lower() == miasto.lower()]
        self.kombobox_stacji['values'] = stacje_filtr

    def filtruj_po_promieniu(self):
        """
        Filtruje stacje pomiarowe na podstawie promienia od określonej lokalizacji.

        Returns:
            None
        """
        try:
            lokalizacja_nazwa = self.wejscie_lokalizacja.get()
            lokalizacja = self.geolocator.geocode(lokalizacja_nazwa)
            if lokalizacja:
                lokalizacja_koordynaty = (lokalizacja.latitude, lokalizacja.longitude)
            else:
                lat = self.wejscie_lat.get()
                lon = self.wejscie_lon.get()
                if lat and lon:
                    lokalizacja_koordynaty = (float(lat), float(lon))
                else:
                    messagebox.showerror("Błąd", "Nie udało się znaleźć lokalizacji ani współrzędnych.")
                    return

            promien = self.wejscie_promien.get()
            if promien:
                promien = float(promien)
                stacje_filtr = [stacja['stationName'] for stacja in self.stacje.values()
                                if geodesic(lokalizacja_koordynaty, (stacja['gegrLat'], stacja['gegrLon'])).km <= promien]
            else:
                stacje_filtr = [stacja['stationName'] for stacja in self.stacje.values()
                                if geodesic(lokalizacja_koordynaty, (stacja['gegrLat'], stacja['gegrLon'])).km]

            self.kombobox_stacji['values'] = stacje_filtr
        except ValueError:
            messagebox.showerror("Błąd", "Proszę wprowadzić poprawne dane dla promienia i lokalizacji.")
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie udało się przetworzyć lokalizacji: {e}")

if __name__ == "__main__":
    root = ThemedTk(theme="radiance")
    app = AplikacjaJakosciPowietrza(root)
    root.mainloop()
