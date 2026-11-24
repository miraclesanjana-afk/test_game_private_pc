# Word Scramble

An end-to-end word-scramble game. The word bank is built from the Oxford dictionary (via the Gemini API), with the Oxford Dictionaries API and an embedded fallback list as alternatives, so the game works even without any API key.

## Setup

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Keys are read from the environment or from the local `.env` file:

- `GEMINI_API_KEY` — fetches Oxford-style dictionary entries (primary source).
- `OXFORD_APP_ID` / `OXFORD_APP_KEY` — optional, alternative word source.

## Play

### Terminal (CLI)

```
.venv\Scripts\python cli.py
```

### Web (Streamlit)

```
.venv\Scripts\python -m streamlit run app.py
```

The web app is deployable on platforms like Streamlit Community Cloud, Render or Railway.

## Push to GitHub

```
git add -A
git commit -m "Initial commit"
git push
```
