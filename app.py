"""Wirtualny Dyrektor AI. Uruchom: streamlit run app.py"""
import streamlit as st
from dane import generuj_dane, generuj_pracownikow, dane_dzisiejsze
import symulator as sym
import llm
from pytania_ai import ANALIZY, analiza, czat

st.set_page_config(page_title="Wirtualny Dyrektor AI", page_icon="📊", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 1.2rem; max-width: 1250px; }
.hero { background: linear-gradient(120deg,#0B1F3A 0%,#12375F 60%,#0F766E 100%); color:#fff; padding:26px 32px;
        border-radius:16px; margin-bottom:18px; box-shadow:0 8px 24px rgba(11,31,58,.18); }
.hero h1 { margin:0; font-size:1.9rem; font-weight:700; color:#fff; }
.hero p { margin:4px 0 0; opacity:.8; font-size:.95rem; }
[data-testid="stMetric"] { background:#fff; border:1px solid #E5E9F0; border-radius:14px; padding:16px 18px;
        box-shadow:0 2px 8px rgba(15,23,42,.05); }
[data-testid="stMetricLabel"] { color:#64748B; font-weight:500; }
[data-testid="stMetricValue"] { color:#0B1F3A; font-weight:700; }
.stTabs [data-baseweb="tab-list"] { gap:6px; border-bottom:1px solid #E5E9F0; }
.stTabs [data-baseweb="tab"] { height:46px; padding:0 18px; border-radius:10px 10px 0 0; font-weight:600; color:#475569; }
.stTabs [aria-selected="true"] { color:#0F766E; }
h2, h3 { color:#0B1F3A; font-weight:700; }
.stButton > button { border-radius:10px; font-weight:600; border:1px solid #CBD5E1; }
.stButton > button[kind="primary"] { background:#0F766E; border:none; }
[data-testid="stSidebar"] { background:#0B1F3A; }
[data-testid="stSidebar"] * { color:#E2E8F0; }
.stChatMessage { background:#fff; border:1px solid #E5E9F0; border-radius:14px; }
</style>""", unsafe_allow_html=True)

df, prac = generuj_dane(), generuj_pracownikow()
m, d = sym.podsumowanie_miesieczne(df), sym.zysk_po_dzialach(df)
dzis = dane_dzisiejsze()
dziala = llm.czy_dziala()

with st.sidebar:
    st.markdown("### 📊 Wirtualny Dyrektor")
    st.markdown("**MetalPol Sp. z o.o.**  \n*dane fikcyjne*")
    st.divider()
    st.markdown("**Model AI (lokalny)**")
    st.markdown(f"`{llm.MODEL}`")
    st.markdown("🟢 Połączono z LM Studio" if dziala else "🔴 Brak połączenia z 127.0.0.1:1234")
    st.divider()
    st.markdown(f"**Dane z dnia {dzis['data']}**")
    st.metric("Przychody dziś", f"{dzis['przychody_dzis']:,} zł")
    st.metric("Stan konta", f"{dzis['stan_konta']:,} zł")
    st.caption(f"Zamówienia: {dzis['zamowienia']} · Reklamacje: {dzis['reklamacje']} · Nieobecni: {dzis['nieobecni_pracownicy']}")

st.markdown('<div class="hero"><h1>Wirtualny Dyrektor AI</h1>'
            '<p>Analizy finansowe, symulacje decyzji i doradca AI działający lokalnie na Twoich danych</p></div>',
            unsafe_allow_html=True)
t1, t2, t3, t4, t5 = st.tabs(["Dashboard", "Symulator decyzji", "Analizy AI", "Czat z dyrektorem", "O projekcie"])

with t1:
    c = st.columns(4)
    c[0].metric("Przychody (12 mies.)", f"{m.przychody.sum():,.0f} zł")
    c[1].metric("Koszty (12 mies.)", f"{m.koszty.sum():,.0f} zł")
    c[2].metric("Zysk (12 mies.)", f"{m.zysk.sum():,.0f} zł")
    c[3].metric("Marża", f"{m.zysk.sum() / m.przychody.sum():.1%}")
    st.write("")
    l, r = st.columns(2)
    l.subheader("Przychody, koszty i zysk"); l.line_chart(m)
    r.subheader("Zysk wg działów"); r.bar_chart(d.zysk)
    prog, trend = sym.prognoza(m)
    st.subheader("Prognoza zysku na 3 miesiące")
    pc = st.columns(3)
    for i, x in enumerate(prog):
        pc[i].metric(f"Miesiąc +{i + 1}", f"{x:,.0f} zł")
    if min(prog) < 0 or trend < 0:
        st.warning("Trend zysku jest spadkowy lub prognoza zakłada stratę.")
    else:
        st.success("Trend zysku jest rosnący, brak sygnałów zagrożenia płynności.")
    st.subheader("Podejrzane wydatki")
    an = sym.anomalie_kosztow(df)
    if an:
        st.dataframe(an, use_container_width=True, hide_index=True)
    else:
        st.info("Brak anomalii.")
    st.subheader("Wydajność pracowników")
    st.dataframe(prac.sort_values("wydajnosc_proc"), use_container_width=True, hide_index=True)

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
    st.subheader("Analizy generowane przez AI")
    nazwa = st.selectbox("Rodzaj analizy", list(ANALIZY))
    uwagi = st.text_area("Dodatkowe informacje (opcjonalnie)", placeholder="np. główni konkurenci, budżet, cele na kwartał")
    if st.button("Generuj analizę", type="primary"):
        with st.spinner("Model analizuje dane..."):
            st.session_state["wynik"] = (nazwa, analiza(nazwa, df, prac, uwagi))
    if "wynik" in st.session_state:
        n_, tekst = st.session_state["wynik"]
        with st.container(border=True):
            st.markdown(f"#### {n_}")
            st.markdown(tekst)
            st.download_button("Pobierz raport (.md)", tekst, file_name="raport.md")

with t4:
    st.subheader("Rozmowa z wirtualnym dyrektorem")
    st.caption("Bot zna dane firmy i dzisiejszy odczyt (odświeżane przy każdej wiadomości) i pamięta historię rozmowy.")
    if "historia" not in st.session_state:
        st.session_state.historia = []
    if st.button("Wyczyść historię"):
        st.session_state.historia = []
    if st.button("Poproś o poranną analizę dnia"):
        st.session_state.historia.append({"role": "user", "content": "Przygotuj krótką poranną analizę na podstawie dzisiejszych danych i wskaż 3 priorytety na dziś."})
        with st.spinner("Dyrektor analizuje..."):
            st.session_state.historia.append({"role": "assistant", "content": czat(st.session_state.historia, df, prac)})
    for msg in st.session_state.historia:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    if wiad := st.chat_input("Napisz do dyrektora..."):
        st.session_state.historia.append({"role": "user", "content": wiad})
        with st.chat_message("user"):
            st.markdown(wiad)
        with st.chat_message("assistant"):
            with st.spinner("Myślę..."):
                odp = czat(st.session_state.historia, df, prac)
            st.markdown(odp)
        st.session_state.historia.append({"role": "assistant", "content": odp})

with t5:
    st.markdown("""
**Architektura:** liczby liczy kod Pythona (`symulator.py`), a model językowy działa lokalnie w LM Studio
(`127.0.0.1:1234`) i interpretuje wyniki. Dane firmy nie opuszczają komputera.

**Ryzyka i etyka:** jakość danych decyduje o jakości rekomendacji, ocena pracowników wymaga nadzoru człowieka
(RODO, AI Act), a analiza konkurencji z modelu ogólnego wymaga weryfikacji na rynku. AI wspiera decyzje, nie zastępuje właściciela.

**Kierunki rozwoju:** import CSV/Excel, integracja z systemem księgowym, raporty PDF.
""")
