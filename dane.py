"""OSOBA 2: dane przykładowe fikcyjnej firmy MetalPol + wczytywanie własnych plików CSV."""
import io
import numpy as np
import pandas as pd

KOL_FIN = ["miesiac", "dzial", "przychody", "koszty"]
KOL_PRAC = ["pracownik", "dzial", "koszt_mies", "wydajnosc_proc"]
KOL_DZIS = ["data", "przychody_dzis", "koszty_dzis", "zamowienia", "reklamacje", "stan_konta", "nieobecni_pracownicy"]
TEKSTOWE = ("miesiac", "dzial", "pracownik", "data")

# dzial: (miesieczne przychody, miesieczne koszty)
DZIALY = {"Produkcja": (95000, 78000), "Sprzedaż": (70000, 48000), "Serwis": (25000, 34000),
          "Logistyka": (22000, 26000), "Marketing": (36000, 27000)}
LICZBA_PRACOWNIKOW = {"Produkcja": 10, "Sprzedaż": 6, "Serwis": 4, "Logistyka": 3, "Marketing": 2}
IMIONA = ["Anna", "Piotr", "Marek", "Ewa", "Jan", "Kasia", "Tomek", "Ola", "Adam", "Marta", "Paweł", "Iga",
          "Michał", "Zofia", "Krzysztof", "Agnieszka", "Łukasz", "Natalia", "Rafał", "Dorota", "Bartek",
          "Magda", "Kamil", "Julia", "Robert"]


def _miesiace(n=24):
    koniec = pd.Timestamp.today().to_period("M") - 1
    return [str(p) for p in pd.period_range(end=koniec, periods=n, freq="M")]


def generuj_dane(seed=42):
    rng = np.random.default_rng(seed)
    mies = _miesiace()
    wiersze = []
    for i, m in enumerate(mies):
        sezon = 1 + 0.08 * np.sin(i / 12 * 2 * np.pi) + 0.008 * i
        for d, (p, k) in DZIALY.items():
            wiersze.append({"miesiac": m, "dzial": d, "przychody": int(round(p * sezon * rng.normal(1, 0.04))),
                            "koszty": int(round(k * rng.normal(1, 0.03)))})
    df = pd.DataFrame(wiersze)
    # celowe "niepotrzebne wydatki" do wykrycia
    df.loc[(df.miesiac == mies[18]) & (df.dzial == "Serwis"), "koszty"] += 12000
    df.loc[(df.miesiac == mies[9]) & (df.dzial == "Marketing"), "koszty"] += 9000
    return df


def generuj_pracownikow():
    rng = np.random.default_rng(7)
    dzialy = [d for d, n in LICZBA_PRACOWNIKOW.items() for _ in range(n)]
    return pd.DataFrame({"pracownik": IMIONA, "dzial": dzialy,
                         "koszt_mies": rng.integers(6500, 9500, len(IMIONA)),
                         "wydajnosc_proc": rng.integers(60, 120, len(IMIONA))})


def dane_dzisiejsze():
    """Dzisiejszy 'odczyt' firmy (symulacja danych z systemu). Zmienia sie kazdego dnia."""
    from datetime import date
    dzis = date.today()
    rng = np.random.default_rng(int(dzis.strftime("%Y%m%d")))
    return {"data": dzis.isoformat(), "przychody_dzis": int(rng.normal(9500, 1500)),
            "koszty_dzis": int(rng.normal(8200, 900)), "zamowienia": int(rng.integers(18, 45)),
            "reklamacje": int(rng.integers(0, 5)), "stan_konta": int(rng.normal(180000, 15000)),
            "nieobecni_pracownicy": int(rng.integers(0, 4)), "zapytania_ofertowe": int(rng.integers(2, 15)),
            "faktury_po_terminie": int(rng.integers(0, 6))}


# ---------- CSV ----------
def _czytaj(plik, kolumny, nazwa):
    surowe = plik.getvalue()
    try:
        tekst = surowe.decode("utf-8-sig")
    except UnicodeDecodeError:
        tekst = surowe.decode("cp1250")
    t = pd.read_csv(io.StringIO(tekst), sep=None, engine="python")
    t.columns = [str(c).strip().lower() for c in t.columns]
    brak = [c for c in kolumny if c not in t.columns]
    if brak:
        raise ValueError(f"Plik {nazwa}: brakuje kolumn {', '.join(brak)}. Wymagane: {', '.join(kolumny)}.")
    t = t[kolumny].copy()
    for c in kolumny:
        if c in TEKSTOWE:
            t[c] = t[c].astype(str).str.strip()
        else:
            t[c] = pd.to_numeric(t[c].astype(str).str.replace(" ", "").str.replace(",", "."), errors="coerce")
    t = t.dropna()
    if t.empty:
        raise ValueError(f"Plik {nazwa} nie zawiera poprawnych wierszy.")
    return t.reset_index(drop=True)


def wczytaj(f1=None, f2=None, f3=None):
    """Zwraca (finanse, pracownicy, dzis, bledy). Bez plikow: dane przykladowe z tego pliku.
    dzis = dict z dziennym odczytem albo None (gdy wlasne finanse bez pliku z danymi dnia)."""
    bledy, df, prac, dzis = [], None, None, None
    if f1:
        try:
            df = _czytaj(f1, KOL_FIN, "finansowy")
            if df.miesiac.nunique() < 3:
                raise ValueError("Plik finansowy: potrzebne dane z co najmniej 3 miesięcy.")
        except Exception as e:
            bledy.append(f"{e} Używam danych przykładowych.")
            df = None
    wlasne = df is not None
    if df is None:
        df = generuj_dane()
    if f2:
        try:
            prac = _czytaj(f2, KOL_PRAC, "pracowników")
        except Exception as e:
            bledy.append(str(e))
    if prac is None:
        prac = pd.DataFrame(columns=KOL_PRAC) if wlasne else generuj_pracownikow()
    if f3:
        try:
            w = _czytaj(f3, KOL_DZIS, "danych z dnia").iloc[-1]
            dzis = {k: (str(w[k]) if k in TEKSTOWE else int(w[k])) for k in KOL_DZIS}
        except Exception as e:
            bledy.append(str(e))
    if dzis is None and not wlasne:
        dzis = dane_dzisiejsze()
    return df, prac, dzis, bledy
