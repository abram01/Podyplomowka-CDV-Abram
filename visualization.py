import matplotlib.pyplot as plt
from datetime import datetime

def wykres_danych(dane, data_od, data_do):
    """
    Wyświetla wykres danych pomiarowych w określonym przedziale czasowym.

    Args:
        dane (list): Lista krotek zawierających datę i wartość pomiaru.
        data_od (str): Data początkowa w formacie yyyy-mm-dd.
        data_do (str): Data końcowa w formacie yyyy-mm-dd.

    Returns:
        None
    """
    daty = [datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S") for entry in dane]
    wartosci = [entry[1] for entry in dane]

    plt.figure(figsize=(10, 5))
    plt.plot(daty, wartosci, marker='o', linestyle='-', color='b')
    plt.xlabel('Data')
    plt.ylabel('Wartość')
    plt.title(f'Dane pomiarowe od {data_od} do {data_do}')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.grid(True)
    plt.show()
