# A Feeling Called Cinema

A data-driven film recommender built on 25,706 titles and 384-dimensional
semantic embeddings. Seven tools meet you where you are: a mood, a clock, a
group chat, a decade, or a favourite film.

## Recommendation tools

- **Mood to Scene** — semantic search over a free-text feeling.
- **Watch Party** — one film the whole group can agree on.
- **Time Budget & Bedtime** — films that fit the minutes you have, with finish times.
- **Double Feature** — a mirror or a deliberate contrast for a film you love.
- **Cultural Bridge** — international films that rhyme with a Hollywood favourite.
- **Era Machine** — a film's closest companion from another decade.
- **Hidden Gems** — high ratings, low popularity, ranked by gem score.

## Stack

- **Streamlit** interface (`app.py`)
- **FastAPI** service (`backend/`)
- **React + Vite** client (`frontend/`)
- **pandas / NumPy** recommendation engine (`src/recommender.py`)

## Project layout

```text
app.py                 Streamlit application
backend/               FastAPI routes and schemas
src/recommender.py     Recommendation engine
data/processed/        Processed dataset, embeddings, and embedding ids
frontend/              React client
tests/                 Engine, API, Streamlit, and edge-case tests
```

## Run the Streamlit app

```bash
pip install -r requirements.txt
streamlit run app.py
```

The processed dataset and precomputed embeddings are included, so no model
download or embedding build step is required.

## Run the API and React client

```bash
uvicorn backend.main:app --reload --port 8000
```

```bash
cd frontend
npm install
npm run dev
```

The client reads `VITE_API_URL` when set and defaults to `http://127.0.0.1:8000`.

## Tests

```bash
pytest
```

With the API on port 8000 and the Vite client on port 5173:

```bash
cd frontend
node e2e/verify.mjs
```
