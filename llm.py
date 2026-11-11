"""Klient lokalnego modelu (LM Studio, API zgodne z OpenAI) pod http://127.0.0.1:1234"""
import re
import requests

BAZA = "http://127.0.0.1:1234"
MODEL = "qwen3.5-9b-uncensored-hauhaucs-aggressive"


def czy_dziala():
    try:
        return requests.get(f"{BAZA}/v1/models", timeout=2).status_code == 200
    except Exception:
        return False


def zapytaj(messages, temperature=0.4, max_tokens=1800):
    try:
        r = requests.post(f"{BAZA}/v1/chat/completions", timeout=600, json={
            "model": MODEL, "messages": messages, "temperature": temperature, "max_tokens": max_tokens})
        r.raise_for_status()
        tekst = r.json()["choices"][0]["message"]["content"]
        return re.sub(r"<think>.*?</think>", "", tekst, flags=re.S).strip()
    except Exception as e:
        return f"⚠️ Brak połączenia z lokalnym modelem ({BAZA}). Uruchom serwer w LM Studio i załaduj model {MODEL}. Szczegóły: {e}"
