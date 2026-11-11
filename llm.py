"""Klient lokalnego modelu (LM Studio, API zgodne z OpenAI) pod http://127.0.0.1:1234"""
import json
import re
import requests

BAZA = "http://127.0.0.1:1234"
MODEL = "qwen3.5-9b-uncensored-hauhaucs-aggressive"
BRAK = (f"⚠️ Brak połączenia z lokalnym modelem. Uruchom serwer w LM Studio (port 1234) i załaduj model {MODEL}.")
PUSTO = ("⚠️ Model zwrócił pustą odpowiedź (prawdopodobnie zużył limit na 'myślenie'). "
         "W LM Studio wyłącz Thinking i ustaw Context Length co najmniej 8192.")


def czy_dziala():
    try:
        return requests.get(f"{BAZA}/v1/models", timeout=2).status_code == 200
    except Exception:
        return False


def _czysc(t):
    """Usuwa 'myslenie' modelu (<think>), tez gdy brak znacznika otwierajacego lub zamykajacego."""
    t = re.sub(r"<think>.*?</think>", "", t, flags=re.S)
    if "</think>" in t:
        t = t.split("</think>")[-1]
    return re.sub(r"<think>.*", "", t, flags=re.S).strip()


def strumien(messages, temperature=0.4, max_tokens=4096):
    """Generator kawalkow tekstu (dla st.write_stream). Zawsze zwraca cos widocznego, takze przy bledzie."""
    surowy, wyslano, mysli, bufor = "", False, False, ""
    try:
        with requests.post(f"{BAZA}/v1/chat/completions", stream=True, timeout=(5, 900), json={
                "model": MODEL, "messages": messages, "temperature": temperature,
                "max_tokens": max_tokens, "stream": True}) as r:
            r.raise_for_status()
            r.encoding = "utf-8"
            for linia in r.iter_lines(decode_unicode=True):
                if not linia or not linia.startswith("data:"):
                    continue
                dane = linia[5:].strip()
                if dane == "[DONE]":
                    break
                try:
                    kawalek = json.loads(dane)["choices"][0]["delta"].get("content") or ""
                except (ValueError, KeyError, IndexError):
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
        yield f"{BRAK} Szczegóły: {e}"
        return
    if not wyslano:
        yield _czysc(surowy) or PUSTO


def zapytaj(messages, temperature=0.4, max_tokens=4096):
    return "".join(strumien(messages, temperature, max_tokens))
