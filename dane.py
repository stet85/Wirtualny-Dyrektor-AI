"""OSOBA 2: dane fikcyjnej firmy MetalPol Sp. z o.o. Mozna zmieniac liczby."""
import numpy as np
import pandas as pd

MIESIACE = ["Lis", "Gru", "Sty", "Lut", "Mar", "Kwi", "Maj", "Cze", "Lip", "Sie", "Wrz", "Paź"]

# dzial: (miesieczne przychody, miesieczne koszty)
DZIALY = {"Produkcja": (95000, 78000), "Sprzedaż": (70000, 48000), "Serwis": (25000, 34000)}


def generuj_dane(seed=42):
    rng = np.random.default_rng(seed)
    wiersze = []
    for i, m in enumerate(MIESIACE):
        sezon = 1 + 0.08 * np.sin(i / 12 * 2 * np.pi) + 0.01 * i
        for d, (p, k) in DZIALY.items():
            wiersze.append({"miesiac": m, "dzial": d,
                            "przychody": round(p * sezon * rng.normal(1, 0.04)),
                            "koszty": round(k * rng.normal(1, 0.03))})
    # celowy "niepotrzebny wydatek": skok kosztow w Serwisie w marcu
    df = pd.DataFrame(wiersze)
    df.loc[(df.miesiac == "Mar") & (df.dzial == "Serwis"), "koszty"] += 12000
    return df


def generuj_pracownikow():
    imiona = ["Anna", "Piotr", "Marek", "Ewa", "Jan", "Kasia", "Tomek", "Ola", "Adam", "Marta",
              "Paweł", "Iga", "Michał", "Zofia", "Krzysztof"]
    dzialy = ["Produkcja"] * 7 + ["Sprzedaż"] * 5 + ["Serwis"] * 3
    rng = np.random.default_rng(7)
    return pd.DataFrame({"pracownik": imiona, "dzial": dzialy,
                         "koszt_mies": rng.integers(6500, 9500, 15),
                         "wydajnosc_proc": rng.integers(60, 120, 15)})


import pandas as pd

KONKURENCI = pd.DataFrame([
    {"firma": "MetalPol (my)", "cena_wyrobu": 1200, "udzial_rynku_proc": 12, "wzrost_proc": 6, "mocna_strona": "jakość, terminowość", "slaba_strona": "słaby marketing"},
    {"firma": "StalTech", "cena_wyrobu": 1100, "udzial_rynku_proc": 25, "wzrost_proc": 3, "mocna_strona": "niska cena, skala", "slaba_strona": "obsługa klienta"},
    {"firma": "ProMetal", "cena_wyrobu": 1350, "udzial_rynku_proc": 18, "wzrost_proc": 8, "mocna_strona": "marka, e-commerce", "slaba_strona": "wysoka cena"},
    {"firma": "Kuźnia Południe", "cena_wyrobu": 1000, "udzial_rynku_proc": 9, "wzrost_proc": -2, "mocna_strona": "tradycja, lokalni klienci", "slaba_strona": "stare maszyny"},
])


def generuj_wydatki():
    """Pozycje kosztow miesiecznych; wykorzystanie_proc < 30 = podejrzane jako niepotrzebne."""
    dane = [("Materiały produkcyjne", 42000, 95), ("Energia", 9000, 90), ("Marketing online", 4000, 80),
            ("Ubezpieczenia", 2500, 85), ("Szkolenia", 1500, 60),
            ("Licencje CAD (5 stanowisk, używane 1)", 2400, 20),
            ("Drugi system CRM (duplikat)", 1800, 10), ("Wynajem magazynu B", 5500, 20),
            ("Reklama w prasie lokalnej", 3200, 25), ("Leasing auta (nieużywane)", 2100, 5)]
    return pd.DataFrame(dane, columns=["pozycja", "kwota_mies", "wykorzystanie_proc"])


from datetime import date, timedelta


def generuj_dzienne(dni=30):
    """Dane dzienne konczace sie DZISIAJ. Kazdy dzien ma wlasne ziarno, wiec 'dzisiejsze' dane sa nowe codziennie."""
    wiersze = []
    for i in range(dni):
        d = date.today() - timedelta(days=dni - 1 - i)
        rng = np.random.default_rng(d.toordinal())
        waga = 0.3 if d.weekday() >= 5 else 1.0
        p = round(6300 * waga * rng.normal(1, 0.08))
        k = round(5300 * (0.6 if d.weekday() >= 5 else 1.0) * rng.normal(1, 0.06))
        wiersze.append({"data": d, "przychody": p, "koszty": k, "zysk": p - k})
    return pd.DataFrame(wiersze)


KONKURENCI = pd.DataFrame([
    {"firma": "MetalPol (my)", "udzial_proc": 14, "indeks_cen": 100, "ocena_klientow": 4.1,
     "mocna": "jakość, serwis lokalny", "slaba": "słaby marketing online"},
    {"firma": "StalTech", "udzial_proc": 22, "indeks_cen": 92, "ocena_klientow": 3.8,
     "mocna": "niskie ceny, skala", "slaba": "długie terminy dostaw"},
    {"firma": "ProMet", "udzial_proc": 17, "indeks_cen": 108, "ocena_klientow": 4.5,
     "mocna": "marka premium, e-commerce", "slaba": "wysokie ceny"},
    {"firma": "BudMetal", "udzial_proc": 9, "indeks_cen": 95, "ocena_klientow": 3.5,
     "mocna": "elastyczność", "slaba": "niska jakość"},
])


def dane_dzisiejsze():
    """Dzisiejszy 'odczyt' firmy (symulacja danych z systemu). Zmienia sie kazdego dnia."""
    from datetime import date
    dzis = date.today()
    rng = np.random.default_rng(int(dzis.strftime("%Y%m%d")))
    przych = int(rng.normal(9500, 1500))
    koszty = int(rng.normal(8200, 900))
    return {"data": dzis.isoformat(), "przychody_dzis": przych, "koszty_dzis": koszty,
            "zamowienia": int(rng.integers(18, 45)), "reklamacje": int(rng.integers(0, 5)),
            "stan_konta": int(rng.normal(180000, 15000)), "nieobecni_pracownicy": int(rng.integers(0, 4))}
