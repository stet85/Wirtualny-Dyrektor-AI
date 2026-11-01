"""TY: aplikacja glowna (Streamlit). Uruchom: streamlit run app.py"""
import streamlit as st
from dane import generuj_dane, generuj_pracownikow
import symulator as sym
from pytania_ai import odpowiedz

st.set_page_config(page_title="Wirtualny Dyrektor AI", page_icon="📊", layout="wide")
df, prac = generuj_dane(), generuj_pracownikow()
m, d = sym.podsumowanie_miesieczne(df), sym.zysk_po_dzialach(df)

st.title("📊 Wirtualny Dyrektor AI")
st.caption("Firma przykładowa: MetalPol Sp. z o.o. (dane fikcyjne). AI wspiera decyzje, ale nie zastępuje właściciela.")
t1, t2, t3, t4 = st.tabs(["📈 Dashboard", "🧮 Symulator decyzji", "💬 Zapytaj dyrektora", "ℹ️ O projekcie"])

with t1:
    c = st.columns(4)
    c[0].metric("Przychody (12 mies.)", f"{m.przychody.sum():,.0f} zł")
    c[1].metric("Koszty (12 mies.)", f"{m.koszty.sum():,.0f} zł")
    c[2].metric("Zysk (12 mies.)", f"{m.zysk.sum():,.0f} zł")
    c[3].metric("Marża", f"{m.zysk.sum() / m.przychody.sum():.1%}")
    l, r = st.columns(2)
    l.subheader("Przychody, koszty i zysk"); l.line_chart(m)
    r.subheader("Zysk wg działów"); r.bar_chart(d.zysk)
    prog, trend = sym.prognoza(m)
    st.subheader("🔮 Prognoza zysku na 3 miesiące")
    st.write(" → ".join(f"{x:,.0f} zł" for x in prog))
    if min(prog) < 0 or trend < 0:
        st.warning("Uwaga: trend zysku jest spadkowy lub prognoza zakłada stratę.")
    else:
        st.success("Trend zysku jest rosnący, brak sygnałów zagrożenia płynności.")
    st.subheader("🔎 Podejrzane wydatki")
    an = sym.anomalie_kosztow(df)
    st.dataframe(an) if an else st.write("Brak anomalii.")
    st.subheader("👥 Wydajność pracowników")
    st.dataframe(prac.sort_values("wydajnosc_proc"), use_container_width=True)

with t2:
    a, b = st.columns(2)
    with a:
        st.subheader("Zatrudnienie nowych osób")
        n = st.slider("Liczba nowych pracowników", 0, 10, 2)
        koszt = st.slider("Koszt pracodawcy / osoba (zł)", 5000, 12000, 7500, 100)
        przych = st.slider("Dodatkowy przychód / osoba (zł)", 0, 15000, 6000, 100)
        w = sym.zatrudnienie(m, n, koszt, przych)
        st.metric("Miesięczny zysk po decyzji", f"{w['zysk_po']:,.0f} zł", f"{w['zmiana']:,.0f} zł")
        st.info("Decyzja opłacalna." if w["rentowne"] or n == 0 else "Decyzja obniży zysk firmy.")
    with b:
        st.subheader("Kupić maszynę czy leasingować?")
        cena = st.number_input("Cena maszyny (zł)", 10000, 2000000, 200000, 10000)
        rata = st.number_input("Rata leasingu (zł/mies.)", 500, 50000, 4200, 100)
        mies = st.slider("Okres (mies.)", 12, 96, 60, 12)
        wk = st.number_input("Wartość końcowa maszyny (zł)", 0, 1000000, 40000, 5000)
        k = sym.kup_czy_leasing(cena, rata, mies, wk)
        st.metric("Koszt kupna (z kosztem kapitału 8%)", f"{k['kupno']:,.0f} zł")
        st.metric("Koszt leasingu", f"{k['leasing']:,.0f} zł")
        st.success(f"Korzystniejszy wariant: {k['wybor']} (o {k['roznica']:,.0f} zł)")

with t3:
    try:
        klucz = st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        klucz = None
    st.caption("Tryb: " + ("Claude API" if klucz else "analiza regułowa (dodaj ANTHROPIC_API_KEY w Secrets, by włączyć Claude)"))
    przyklady = ["Który dział generuje największe straty?", "Co się stanie, jeśli zatrudnię dwóch pracowników?",
                 "Czy kupić maszynę, czy leasingować?", "Gdzie mogę zwiększyć zysk?"]
    wybor = st.radio("Przykładowe pytania", przyklady, horizontal=True)
    pytanie = st.text_input("Własne pytanie (opcjonalnie)")
    if st.button("Zapytaj", type="primary"):
        with st.spinner("Analizuję..."):
            st.markdown(odpowiedz(pytanie or wybor, df, prac, klucz))

with t4:
    st.markdown("""
**Dane:** fikcyjne, generowane w `dane.py`. **Liczby** liczy kod Pythona, a AI jedynie interpretuje wyniki.

**Ryzyka i etyka:** jakość danych decyduje o jakości rekomendacji, dane firmy są poufne,
AI nie zastępuje decyzji właściciela, a ocena pracowników wymaga nadzoru człowieka (RODO, AI Act).

**Kierunki rozwoju:** import danych z Excela/CSV, integracja z systemem księgowym, raporty PDF.
""")
