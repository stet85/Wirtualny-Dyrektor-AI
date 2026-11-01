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
