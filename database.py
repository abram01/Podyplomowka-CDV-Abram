import sqlite3


def reset_baza():
    """
    Resetuje bazę danych, usuwając istniejące pliki.

    Returns:
        None
    """
    import os
    if os.path.exists("air_quality.db"):
        os.remove("air_quality.db")


def utworz_tabele():
    """
    Tworzy tabele w bazie danych.

    Returns:
        None
    """
    conn = sqlite3.connect("air_quality.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS czujniki (
        id_czujnika INTEGER PRIMARY KEY,
        nazwa TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS dane (
        id_czujnika INTEGER,
        data TEXT,
        wartosc REAL,
        FOREIGN KEY(id_czujnika) REFERENCES czujniki(id_czujnika)
    )
    """)

    conn.commit()
    conn.close()


def zapisz_czujnik(id_czujnika, nazwa):
    """
    Zapisuje czujnik do bazy danych.

    Args:
        id_czujnika (int): Unikalny identyfikator czujnika.
        nazwa (str): Nazwa czujnika.

    Returns:
        None
    """
    conn = sqlite3.connect("air_quality.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO czujniki (id_czujnika, nazwa) VALUES (?, ?)", (id_czujnika, nazwa))
    conn.commit()
    conn.close()


def zapisz_dane(dane):
    """
    Zapisuje dane pomiarowe do bazy danych.

    Args:
        dane (tuple): Dane pomiarowe w formie krotki (id_czujnika, data, wartosc).

    Returns:
        None
    """
    conn = sqlite3.connect("air_quality.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dane (id_czujnika, data, wartosc) VALUES (?, ?, ?)", dane)
    conn.commit()
    conn.close()


def pobierz_dane(id_czujnika, data_od, data_do):
    """
    Pobiera dane pomiarowe z bazy danych dla określonego czujnika w podanym przedziale czasowym.

    Args:
        id_czujnika (int): Unikalny identyfikator czujnika.
        data_od (str): Data początkowa w formacie yyyy-mm-dd.
        data_do (str): Data końcowa w formacie yyyy-mm-dd.

    Returns:
        list: Lista krotek zawierających datę i wartość pomiaru.
    """
    conn = sqlite3.connect("air_quality.db")
    cursor = conn.cursor()
    cursor.execute("SELECT data, wartosc FROM dane WHERE id_czujnika = ? AND data BETWEEN ? AND ?",
                   (id_czujnika, data_od, data_do))
    dane = cursor.fetchall()
    conn.close()
    return dane


def pobierz_wszystkie_dane(id_czujnika):
    """
    Pobiera wszystkie dane pomiarowe z bazy danych dla określonego czujnika.

    Args:
        id_czujnika (int): Unikalny identyfikator czujnika.

    Returns:
        list: Lista krotek zawierających datę i wartość pomiaru.
    """
    conn = sqlite3.connect("air_quality.db")
    cursor = conn.cursor()
    cursor.execute("SELECT data, wartosc FROM dane WHERE id_czujnika = ?", (id_czujnika,))
    dane = cursor.fetchall()
    conn.close()
    return dane
