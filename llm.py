"""Klient OpenRouter (https://openrouter.ai), API zgodne z OpenAI. Klucz podajesz w aplikacji, Secrets lub zmiennej OPENROUTER_API_KEY."""
import json
import os
import re
import requests

BAZA = "https://openrouter.ai/api/v1"
MODEL_DOMYSLNY = "nvidia/nemotron-3.5-super-vl:free"  # dowolny model z openrouter.ai/models
BRAK_KLUCZA = "⚠️ Brak klucza API OpenRouter. Wpisz go w panelu bocznym (Model AI) lub ustaw w Secrets jako OPENROUTER_API_KEY."
PUSTO = "⚠️ Model zwrócił pustą odpowiedź. Spróbuj ponownie lub wybierz inny model (najlepiej bez trybu rozumowania)."
OPISY = {401: "Nieprawidłowy klucz API OpenRouter.",
         402: "Brak środków na koncie OpenRouter. Doładuj kredyty albo wybierz model z końcówką :free.",
         404: "Nie znaleziono modelu. Sprawdź ID na openrouter.ai/models.",
         429: "Przekroczony limit zapytań. Spróbuj za chwilę."}


def klucz_ze_srodowiska():
    return os.environ.get("OPENROUTER_API_KEY", "")


def _naglowki(klucz):
    return {"Authorization": f"Bearer {klucz}", "Content-Type": "application/json", "X-Title": "Wirtualny Dyrektor AI"}


def sprawdz_klucz(klucz):
    """Dane klucza (limit, zuzycie) albo None, gdy klucz nie dziala."""
    if not klucz:
        return None
    try:
        r = requests.get(f"{BAZA}/auth/key", headers=_naglowki(klucz), timeout=8)
        return (r.json().get("data") or {"label": "ok"}) if r.status_code == 200 else None
    except Exception:
        return None


def _blad(status, tresc):
    try:
        szczegol = json.loads(tresc)["error"]["message"]
    except Exception:
        szczegol = tresc[:200]
    return f"⚠️ {OPISY.get(status, f'Błąd OpenRouter ({status}).')} ({szczegol})"


def _czysc(t):
    """Usuwa 'myslenie' modelu (<think>), tez gdy brak znacznika otwierajacego lub zamykajacego."""
    t = re.sub(r"<think>.*?</think>", "", t, flags=re.S)
    if "</think>" in t:
        t = t.split("</think>")[-1]
    return re.sub(r"<think>.*", "", t, flags=re.S).strip()


def _proba(messages, klucz, model, temperature, max_tokens, rozum):
    """Jedna proba zapytania. Generator tekstu; na koncu zwraca slownik z wynikiem (przez yield from)."""
    w = {"status": 200, "powod": None, "mysl": "", "surowy": "", "wyslano": False, "blad": None}
    cialo = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens, "stream": True}
    if rozum:
        cialo["reasoning"] = rozum
    mysli, bufor = False, ""
    try:
        with requests.post(f"{BAZA}/chat/completions", headers=_naglowki(klucz), stream=True, timeout=(10, 300),
                           json=cialo) as r:
            w["status"] = r.status_code
            if r.status_code != 200:
                w["blad"] = _blad(r.status_code, r.text)
                return w
            r.encoding = "utf-8"
            for linia in r.iter_lines(decode_unicode=True):
                if not linia or not linia.startswith("data:"):  # komentarze ": OPENROUTER PROCESSING" pomijamy
                    continue
                dane = linia[5:].strip()
                if dane == "[DONE]":
                    break
                try:
                    obj = json.loads(dane)
                except ValueError:
                    continue
                if "error" in obj:
                    w["status"], w["blad"] = 500, f"⚠️ Błąd w trakcie generowania: {obj['error'].get('message', obj['error'])}"
                    return w
                try:
                    wyb = obj["choices"][0]
                except (KeyError, IndexError):
                    continue
                delta = wyb.get("delta") or {}
                w["powod"] = wyb.get("finish_reason") or w["powod"]
                w["mysl"] += (delta.get("reasoning") or delta.get("reasoning_content") or "")
                kawalek = delta.get("content") or ""
                w["surowy"] += kawalek
                bufor += kawalek
                while True:
                    if mysli:
                        i = bufor.find("</think>")
                        if i < 0:
                            bufor = bufor[-8:]
                            break
                        bufor, mysli = bufor[i + 8:], False
                    else:
                        i = bufor.find("<think>")
                        if i < 0:
                            if len(bufor) > 7:
                                w["wyslano"] = True
                                yield bufor[:-7]
                                bufor = bufor[-7:]
                            break
                        if i:
                            w["wyslano"] = True
                            yield bufor[:i]
                        bufor, mysli = bufor[i + 7:], True
        if not mysli and bufor.strip():
            w["wyslano"] = True
            yield bufor
    except Exception as e:
        w["status"], w["blad"] = 0, f"⚠️ Brak połączenia z OpenRouter. Sprawdź internet. Szczegóły: {e}"
    return w


def strumien(messages, klucz, model=MODEL_DOMYSLNY, temperature=0.4, max_tokens=6000):
    """Generator kawalkow tekstu (dla st.write_stream). Zawsze zwraca cos widocznego, takze przy bledzie.
    Modele rozumujace (np. Nemotron) potrafia zuzyc caly limit na 'myslenie', wiec przy pustej odpowiedzi
    ponawiamy z wiekszym limitem i niskim wysilkiem rozumowania, a na koncu pokazujemy chociaz tok rozumowania."""
    if not klucz:
        yield BRAK_KLUCZA
        return
    w = {}
    for nr, (limit, rozum) in enumerate([(max_tokens, None), (max_tokens * 2, {"effort": "low"}), (max_tokens * 2, None)]):
        w = yield from _proba(messages, klucz, model, temperature, limit, rozum)
        if w["wyslano"]:
            return
        if w["blad"]:
            if nr == 1 and w["status"] in (400, 422):  # model nie przyjmuje parametru reasoning, probujemy bez
                continue
            yield w["blad"]
            return
    if _czysc(w["surowy"]):
        yield _czysc(w["surowy"])
    elif w["mysl"].strip():
        yield (f"⚠️ Model {model} zużył cały limit na „myślenie” i nie napisał końcowej odpowiedzi "
               f"(finish_reason: {w['powod']}). Wybierz model bez trybu rozumowania. Poniżej jego tok rozumowania:\n\n"
               + w["mysl"].strip())
    else:
        yield PUSTO + f" (finish_reason: {w['powod']})"


def zapytaj(messages, klucz, model=MODEL_DOMYSLNY, temperature=0.4, max_tokens=6000):
    return "".join(strumien(messages, klucz, model, temperature, max_tokens))
