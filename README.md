# Wirtualny Dyrektor AI
Python + Streamlit + lokalny model AI (Ollama). Dashboard, analizy AI, chatbot z danymi z dzisiaj, symulator decyzji.

## Uruchomienie
1. Zainstaluj Ollama (ollama.com), potem: `ollama pull llama3.1` i `ollama serve`
2. `pip install -r requirements.txt`
3. `streamlit run app.py`

Inny model: zmienna `OLLAMA_MODEL` lub wybór w panelu bocznym.
Uwaga: na Streamlit Cloud nie ma dostępu do Twojego localhosta. Demo pokazuj lokalnie albo przez tunel (ngrok).

## Podział pracy
| Plik | Kto |
|---|---|
| app.py, llm.py, .streamlit/, README.md | Osoba 1 |
| dane.py, symulator.py, pytania_ai.py, asystent.py | Osoba 2 |
| prezentacja | Osoba 3 |
