"""Klient OpenRouter (https://openrouter.ai), API zgodne z OpenAI. Klucz podajesz w aplikacji, Secrets lub zmiennej OPENROUTER_API_KEY."""
import json
import os
import re
import requests

BAZA = "https://openrouter.ai/api/v1"
MODEL_DOMYSLNY = "openai/gpt-4o-mini"  # dowolny model z openrouter.ai/models
BRAK_KLUCZA = "⚠️ Brak klucza API OpenRouter. Wpisz go w panelu bocznym (Model AI) lub ustaw w Secrets jako OPENROUTER_API_KEY."
PUSTO = "⚠️ Model zwrócił pustą odpowiedź (mógł zużyć limit na 'myślenie'). Spróbuj ponownie lub wybierz inny model."
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


def strumien(messages, klucz, model=MODEL_DOMYSLNY, temperature=0.4, max_tokens=3000):
    """Generator kawalkow tekstu (dla st.write_stream). Zawsze zwraca cos widocznego, takze przy bledzie."""
    if not klucz:
        yield BRAK_KLUCZA
        return
    surowy, wyslano, mysli, bufor = "", False, False, ""
    try:
        with requests.post(f"{BAZA}/chat/completions", headers=_naglowki(klucz), stream=True, timeout=(10, 300), json={
                "model": model, "messages": messages, "temperature": temperature,
                "max_tokens": max_tokens, "stream": True}) as r:
            if r.status_code != 200:
                yield _blad(r.status_code, r.text)
                return
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
                    yield f"⚠️ Błąd w trakcie generowania: {obj['error'].get('message', obj['error'])}"
                    return
                try:
                    kawalek = obj["choices"][0]["delta"].get("content") or ""
                except (KeyError, IndexError):
                    continue
                surowy += kawalek
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
                                wyslano = True
                                yield bufor[:-7]
                                bufor = bufor[-7:]
                            break
                        if i:
                            wyslano = True
                            yield bufor[:i]
                        bufor, mysli = bufor[i + 7:], True
        if not mysli and bufor:
            wyslano = True
            yield bufor
    except Exception as e:
        yield f"⚠️ Brak połączenia z OpenRouter. Sprawdź internet. Szczegóły: {e}"
        return
    if not wyslano:
        yield _czysc(surowy) or PUSTO
