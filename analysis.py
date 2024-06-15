def analizuj_dane(dane):
    """
    Przeprowadza prostą analizę danych pomiarowych.

    Args:
        dane (list): Lista krotek zawierających datę i wartość pomiaru.

    Returns:
        dict: Słownik zawierający wyniki analizy.
    """
    if not dane:
        return None

    wartosci = [entry[1] for entry in dane if entry[1] is not None]
    daty = [entry[0] for entry in dane if entry[1] is not None]

    if not wartosci:
        return None

    min_wartosc = min(wartosci)
    max_wartosc = max(wartosci)
    srednia_wartosc = sum(wartosci) / len(wartosci)
    trend = "wzrostowy" if wartosci[-1] > wartosci[0] else "spadkowy"

    wyniki = {
        "min": min_wartosc,
        "min_data": daty[wartosci.index(min_wartosc)],
        "max": max_wartosc,
        "max_data": daty[wartosci.index(max_wartosc)],
        "srednia": srednia_wartosc,
        "trend": trend
    }

    return wyniki
