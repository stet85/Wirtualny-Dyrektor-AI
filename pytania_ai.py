"""OSOBA 2: odpowiedzi na pytania. Tryb 1: reguly + obliczenia. Tryb 2: Claude API (jesli jest klucz)."""
import symulator as sym


def fakty(df, prac):
    m = sym.podsumowanie_miesieczne(df)
    d = sym.zysk_po_dzialach(df)
    prog, trend = sym.prognoza(m)
    return {"m": m, "d": d, "prog": prog, "trend": trend,
            "anom": sym.anomalie_kosztow(df), "slaby": prac.sort_values("wydajnosc_proc").head(3)}


def odpowiedz(pytanie, df, prac, klucz=None):
    f = fakty(df, prac)
    baza = _reguly(pytanie.lower(), f)
    if klucz:
        try:
            import anthropic
            k = anthropic.Anthropic(api_key=klucz)
            kontekst = (f"Zysk wg dzialow (zl, 12 mies.):\n{f['d'].to_string()}\n"
                        f"Prognoza zysku na 3 mies.: {f['prog']}\nAnomalie kosztow: {f['anom']}\n"
                        f"Wstepna analiza: {baza}")
            r = k.messages.create(model="claude-sonnet-5-5", max_tokens=600,
                system="Jestes wirtualnym dyrektorem firmy. Odpowiadaj po polsku, konkretnie, "
                       "uzywaj tylko podanych liczb, wyjasnij rekomendacje i zaznacz ryzyka.",
                messages=[{"role": "user", "content": f"{kontekst}\n\nPytanie wlasciciela: {pytanie}"}])
            return r.content[0].text
        except Exception as e:
            return baza + f"\n\n(Tryb AI niedostępny: {e})"
    return baza


def _reguly(p, f):
    d, m = f["d"], f["m"]
    najgorszy = d.index[0]
    if "strat" in p or "dział" in p or "dzial" in p:
        if d.zysk.iloc[0] < 0:
            return (f"Największe straty generuje dział **{najgorszy}**: {d.zysk.iloc[0]:,.0f} zł w 12 miesięcy "
                    f"(przychody {d.przychody.iloc[0]:,.0f} zł, koszty {d.koszty.iloc[0]:,.0f} zł). "
                    f"Rekomendacja: przegląd kosztów tego działu lub podniesienie cen usług.")
        return f"Żaden dział nie jest stratny. Najsłabszy to {najgorszy} ({d.zysk.iloc[0]:,.0f} zł zysku)."
    if "zatrudn" in p:
        w = sym.zatrudnienie(m, 2, 7500, 6000)
        return (f"Przy założeniu kosztu 7 500 zł i dodatkowych przychodów 6 000 zł na osobę miesięczny zysk zmieni się "
                f"o {w['zmiana']:,.0f} zł ({w['zysk_teraz']:,.0f} → {w['zysk_po']:,.0f} zł). "
                f"Zatrudnienie jest opłacalne tylko, jeśli nowa osoba przyniesie więcej niż kosztuje. Sprawdź w zakładce Symulator.")
    if "leasing" in p or "maszyn" in p or "kup" in p:
        w = sym.kup_czy_leasing(200000, 4200, 60, 40000)
        return (f"Dla maszyny za 200 000 zł (60 mies., wartość końcowa 40 000 zł): kupno kosztuje realnie {w['kupno']:,.0f} zł, "
                f"leasing {w['leasing']:,.0f} zł. Lepszy wariant: **{w['wybor']}** (różnica {w['roznica']:,.0f} zł).")
    if "zwiększ" in p or "zysk" in p or "wydat" in p or "oszczęd" in p:
        t = [f"{a['dzial']} w m-cu {a['miesiac']} (+{a['ponad_srednia']:,} zł ponad średnią)" for a in f["anom"]]
        return ("Gdzie zwiększyć zysk: 1) skorygować dział " + najgorszy + "; 2) sprawdzić podejrzane wydatki: "
                + (", ".join(t) if t else "brak") + "; 3) utrzymać trend sprzedaży.")
    return (f"Średni miesięczny zysk to {m.zysk.mean():,.0f} zł, prognoza na 3 miesiące: {f['prog']}. "
            f"Zapytaj o straty, zatrudnienie, leasing maszyny lub zwiększenie zysku.")
