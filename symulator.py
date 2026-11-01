"""OSOBA 2: symulator decyzji i prognoza. Liczy kod, nie AI, wiec wyniki sa wiarygodne."""
import numpy as np


def podsumowanie_miesieczne(df):
    m = df.groupby("miesiac", sort=False)[["przychody", "koszty"]].sum()
    m["zysk"] = m.przychody - m.koszty
    return m


def zysk_po_dzialach(df):
    d = df.groupby("dzial")[["przychody", "koszty"]].sum()
    d["zysk"] = d.przychody - d.koszty
    return d.sort_values("zysk")


def anomalie_kosztow(df):
    """Koszty wyzsze o >1.5 odchylenia std od sredniej danego dzialu = podejrzane wydatki."""
    wyniki = []
    for d, g in df.groupby("dzial"):
        prog = g.koszty.mean() + 1.5 * g.koszty.std()
        for _, r in g[g.koszty > prog].iterrows():
            wyniki.append({"dzial": d, "miesiac": r.miesiac, "koszty": r.koszty,
                           "ponad_srednia": round(r.koszty - g.koszty.mean())})
    return wyniki


def prognoza(m, n=3):
    """Trend liniowy zysku na kolejne n miesiecy."""
    y = m.zysk.values
    a, b = np.polyfit(range(len(y)), y, 1)
    return [round(a * (len(y) + i) + b) for i in range(n)], a


def zatrudnienie(m, ile, koszt_osoby, przychod_osoby):
    zysk_teraz = m.zysk.mean()
    zmiana = ile * (przychod_osoby - koszt_osoby)
    zwrot = None if przychod_osoby <= koszt_osoby else 0
    return {"zysk_teraz": zysk_teraz, "zysk_po": zysk_teraz + zmiana, "zmiana": zmiana,
            "rentowne": przychod_osoby > koszt_osoby}


def kup_czy_leasing(cena, rata, miesiecy, wartosc_koncowa, koszt_kapitalu=0.08):
    lata = miesiecy / 12
    kupno = cena + cena * koszt_kapitalu * lata - wartosc_koncowa
    leasing = rata * miesiecy
    return {"kupno": kupno, "leasing": leasing,
            "wybor": "leasing" if leasing < kupno else "kupno", "roznica": abs(kupno - leasing)}
