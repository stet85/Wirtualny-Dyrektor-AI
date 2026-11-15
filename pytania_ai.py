"""Kontekst firmy + prompty analiz AI (model lokalny) + eksport CSV."""
from datetime import date
import pandas as pd
import symulator as sym

SYSTEM = ("Jesteś wirtualnym dyrektorem firmy właściciela. Odpowiadasz po polsku, konkretnie i profesjonalnie. "
          "Opierasz się wyłącznie na liczbach z kontekstu; jeśli czegoś brakuje, powiedz to wprost i oznacz jako założenie. "
          "Uzasadniaj rekomendacje i wskazuj ryzyka. Używaj krótkich nagłówków i punktów. Decyzję podejmuje człowiek.")

ANALIZY = {
    "Analiza kosztów i przychodów": "Przeanalizuj przychody i koszty: trendy, marże działów, najważniejsze wnioski i 3 działania.",
    "Niepotrzebne wydatki": "Wskaż niepotrzebne lub podejrzane wydatki oraz nieefektywnych pracowników. Podaj szacowane oszczędności i sposób weryfikacji.",
    "Analiza konkurencji": "Wykonaj analizę konkurencji dla tej firmy i jej branży: typowi konkurenci, ich mocne i słabe strony, "
                           "nasza pozycja, szanse i zagrożenia. Zaznacz, że to analiza ogólna do weryfikacji na rynku.",
    "Strategia marketingowa": "Przygotuj strategię marketingową na 6 miesięcy: grupy klientów, kanały, komunikat, budżet orientacyjny, KPI.",
    "Rekomendacje biznesowe": "Daj 5 priorytetowych rekomendacji biznesowych (co, dlaczego, efekt w zł, ryzyko, termin), od najważniejszej.",
}


def kontekst(df, prac, dzis=None):
    m, d = sym.podsumowanie_miesieczne(df), sym.zysk_po_dzialach(df)
    prog, _ = sym.prognoza(m)
    t = (f"DANE FIRMY (zł)\nZa {len(m)} mies.: przychody {m.przychody.sum():,.0f}, koszty {m.koszty.sum():,.0f}, "
         f"zysk {m.zysk.sum():,.0f}\nWg działów:\n{d.to_string()}\nOstatnie 3 miesiące:\n{m.tail(3).to_string()}\n"
         f"Prognoza zysku 3 mies.: {prog}\nPodejrzane wydatki: {sym.anomalie_kosztow(df) or 'brak'}\n")
    if len(prac):
        anon = prac.copy()  # RODO: do zewnetrznego API nie wysylamy imion (usun te 2 linie, by wysylac imiona)
        anon["pracownik"] = [f"P{i + 1:02d}" for i in range(len(anon))]
        t += f"Pracownicy (pseudonimy, koszt/mies., wydajność %):\n{anon.to_string(index=False)}\n"
    if dzis:
        t += "DANE Z DNIA " + str(dzis.get("data", date.today())) + ": " + ", ".join(
            f"{k} {v:,}" if isinstance(v, int) else f"{k} {v}" for k, v in dzis.items() if k != "data")
    return t


def _msgs(historia, df, prac, dzis):
    return [{"role": "system", "content": SYSTEM + "\n\n" + kontekst(df, prac, dzis)}] + historia


def wiad_analiza(nazwa, df, prac, dzis=None, uwagi=""):
    zadanie = ANALIZY[nazwa] + (f"\nDodatkowe informacje od właściciela: {uwagi}" if uwagi else "")
    return _msgs([{"role": "user", "content": zadanie}], df, prac, dzis)


def wiad_czat(historia, df, prac, dzis=None):
    """Kontekst odswiezany przy kazdej wiadomosci, wiec bot zna najnowsze dane."""
    return _msgs(historia, df, prac, dzis)


def raport_csv(nazwa, tekst):
    linie = [l for l in tekst.splitlines() if l.strip()]
    t = pd.DataFrame({"analiza": nazwa, "data": date.today().isoformat(), "nr": range(1, len(linie) + 1), "tresc": linie})
    return t.to_csv(index=False, sep=";").encode("utf-8-sig")


def historia_csv(historia):
    t = pd.DataFrame({"rola": ["Ty" if h["role"] == "user" else "Dyrektor" for h in historia],
                      "tresc": [h["content"] for h in historia]})
    return t.to_csv(index=False, sep=";").encode("utf-8-sig")
