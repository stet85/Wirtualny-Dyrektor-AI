"""Kontekst firmy + prompty analiz AI (model lokalny)."""
import symulator as sym
from dane import dane_dzisiejsze
from llm import zapytaj

SYSTEM = ("Jesteś wirtualnym dyrektorem firmy MetalPol Sp. z o.o. Odpowiadasz po polsku, konkretnie i profesjonalnie. "
          "Opierasz się wyłącznie na liczbach z kontekstu; jeśli czegoś brakuje, powiedz to wprost i oznacz jako założenie. "
          "Uzasadniaj rekomendacje i wskazuj ryzyka. Używaj krótkich nagłówków i punktów.")


def kontekst(df, prac):
    m, d = sym.podsumowanie_miesieczne(df), sym.zysk_po_dzialach(df)
    prog, _ = sym.prognoza(m)
    t = dane_dzisiejsze()
    return (f"DANE FIRMY (zł)\nZa 12 miesięcy: przychody {m.przychody.sum():,.0f}, koszty {m.koszty.sum():,.0f}, zysk {m.zysk.sum():,.0f}\n"
            f"Wg działów:\n{d.to_string()}\nOstatnie 3 miesiące:\n{m.tail(3).to_string()}\n"
            f"Prognoza zysku 3 mies.: {prog}\nPodejrzane wydatki: {sym.anomalie_kosztow(df) or 'brak'}\n"
            f"Pracownicy (koszt/mies., wydajność %):\n{prac.to_string(index=False)}\n"
            f"DANE Z DZISIAJ ({t['data']}): przychody {t['przychody_dzis']:,}, koszty {t['koszty_dzis']:,}, "
            f"zamówienia {t['zamowienia']}, reklamacje {t['reklamacje']}, stan konta {t['stan_konta']:,}, "
            f"nieobecni pracownicy {t['nieobecni_pracownicy']}")


ANALIZY = {
    "Analiza kosztów i przychodów": "Przeanalizuj przychody i koszty: trendy, marże działów, najważniejsze wnioski i 3 działania.",
    "Niepotrzebne wydatki": "Wskaż niepotrzebne lub podejrzane wydatki oraz nieefektywnych pracowników. Podaj szacowane oszczędności i sposób weryfikacji.",
    "Analiza konkurencji": "Wykonaj analizę konkurencji dla firmy z tej branży (produkcja metalowa + sprzedaż + serwis): typowi konkurenci, "
                           "ich mocne i słabe strony, nasza pozycja, szanse i zagrożenia. Zaznacz, że to analiza ogólna do weryfikacji na rynku.",
    "Strategia marketingowa": "Przygotuj strategię marketingową na 6 miesięcy: grupy klientów, kanały, komunikat, budżet orientacyjny, KPI.",
    "Rekomendacje biznesowe": "Daj 5 priorytetowych rekomendacji biznesowych (co, dlaczego, efekt w zł, ryzyko, termin), od najważniejszej.",
}


def analiza(nazwa, df, prac, uwagi=""):
    msgs = [{"role": "system", "content": SYSTEM + "\n\n" + kontekst(df, prac)},
            {"role": "user", "content": ANALIZY[nazwa] + (f"\nDodatkowe informacje od właściciela: {uwagi}" if uwagi else "")}]
    return zapytaj(msgs)


def czat(historia, df, prac):
    """Kontekst odswiezany przy kazdej wiadomosci, wiec bot zna najnowsze dane z dnia."""
    return zapytaj([{"role": "system", "content": SYSTEM + "\n\n" + kontekst(df, prac)}] + historia, temperature=0.5)
