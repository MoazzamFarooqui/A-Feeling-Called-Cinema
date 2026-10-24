# A Feeling Called Cinema

A content-based film recommender built on 25,706 movies and 384-dimensional
semantic embeddings. Instead of scrolling through genres, you describe the
feeling, the time you have, the group you are watching with, or the film you
already love — and the engine finds what fits.

The project ships with two interfaces: a **Streamlit app** and a **React client
backed by FastAPI**. Both expose the same seven recommendation tools.

## Table of Contents

- [Project Overview](#project-overview)
- [The Problem](#the-problem)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Data Setup](#data-setup)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [API Reference](#api-reference)
- [Screenshots](#screenshots)
- [Testing](#testing)
- [Contributing](#contributing)
- [Support](#support)

## Project Overview

Streaming catalogues are enormous, but their filters are not. You can pick a
genre and a decade, yet not "something tense but warm, under two hours, that my
whole group will tolerate."

A Feeling Called Cinema treats a movie as a 384-dimensional vector built from
its plot summary, tagline, genres, tone, and production metadata. Recommendations
are produced with cosine similarity over those vectors, combined with practical
constraints such as runtime, language, decade, and group agreement.

Two signals keep the results grounded:

- **Weighted rating** balances a film's average score against how many people
  rated it, so a 9.0 from 50 voters does not outrank an 8.4 from 20,000.
- **Gem score** rewards strong ratings with low popularity, surfacing films most
  people never found.

No external recommendation API is called at runtime. The dataset, embeddings,
and ranking logic all live in this repository.

## The Problem

| Everyday problem | What this project does |
| --- | --- |
| Endless scrolling and decision fatigue | Returns a short, ranked list for a specific intent |
| Genre filters are too coarse | Understands free-text mood and tone through embeddings |
| Groups cannot agree | Blends up to five favourites into one shared vector |
| "We only have 95 minutes" | Filters by runtime and shows the exact finish time |
| Watchlists are US-centric | Surfaces international films with the same fingerprint |
| Nostalgia without repetition | Finds a film's closest companion from another decade |
| Great films stay invisible | Ranks overlooked, high-rated films by gem score |

## Features

| Tool | What it does | How it works |
| --- | --- | --- |
| **Mood to Scene** | Turns a feeling into a ranked film list | Encodes the query with MiniLM and ranks movies by embedding similarity |
| **Watch Party** | Finds one film a group can agree on | Averages the picks into a centroid, excludes the picks, relaxes filters only when needed |
| **Time Budget & Bedtime** | Fits a film into the minutes you have | Runtime filter, weighted-rating order, optional calm-only mode, and finish clocks |
| **Double Feature** | Pairs a film with its mirror or opposite | Mirror: high similarity from a different decade. Contrast: shared genre with an intensity shift |
| **Cultural Bridge** | Finds international counterparts | Similarity search restricted to non-domestic films, with language badges |
| **Era Machine** | Moves a film into another decade | Similarity search restricted to the chosen decade |
| **Hidden Gems** | Finds high-rated, low-buzz films | Filters hidden gems by genre and year, then ranks by gem score |

## Technologies Used

**Data and recommendation engine**

- Python 3, pandas, NumPy
- `sentence-transformers/all-MiniLM-L6-v2` (384-dimension embeddings)
- Precomputed, L2-normalized embeddings for 25,706 films

**Streamlit interface**

- Streamlit with a custom black-and-white editorial theme
- Session-state driven filters and typed inputs

**API and React client**

- FastAPI, Uvicorn, Pydantic
- React 19, React Router, Vite, Axios
- Responsive desktop and mobile layouts

**Testing**

- pytest, Streamlit AppTest, FastAPI TestClient
- Puppeteer end-to-end checks against the running API and client

## Project Structure

```text
.
├── app.py                      # Streamlit application
├── backend/
│   ├── main.py                 # FastAPI routes
│   └── schemas.py              # Request and response models
├── src/
│   └── recommender.py          # Recommendation engine (all seven tools)
├── data/
│   └── processed/
│       ├── movies_clean_v2.csv # 25,706 processed films
│       ├── embeddings.npy      # 25,706 × 384 normalized vectors
│       └── embedding_ids.npy   # Vector-to-movie alignment
├── frontend/
│   ├── src/                    # React pages and components
│   ├── e2e/verify.mjs          # End-to-end verification
│   └── public/favicon.svg
├── tests/                      # Engine, API, Streamlit, and edge-case tests
├── docs/screenshots/           # README screenshots
├── .streamlit/config.toml      # Streamlit theme
└── requirements.txt
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- ~500 MB of free disk space for Python and Node dependencies
- Internet access on the first mood search so the MiniLM model can be downloaded
  once and cached by Sentence Transformers
- No API keys or external accounts

## Installation

```bash
git clone https://github.com/MoazzamFarooqui/A-Feeling-Called-Cinema.git
cd A-Feeling-Called-Cinema
```

Create and activate a virtual environment:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Install the Python and frontend dependencies:

```bash
pip install -r requirements.txt

cd frontend
npm install
cd ..
```

## Data Setup

The processed dataset is committed, so no preprocessing or embedding build step
is required:

| File | Contents |
| --- | --- |
| `data/processed/movies_clean_v2.csv` | 25,706 films with ratings, runtime, genres, language, tone, and gem metrics |
| `data/processed/embeddings.npy` | 25,706 × 384 L2-normalized embeddings |
| `data/processed/embedding_ids.npy` | Movie ids aligned row-for-row with the embeddings |

The original raw IMDb dataset is not included. The engine loads the three files
above at startup, so the app works immediately after installation. Precomputed
vectors are used for every comparison; only a typed mood query needs to be
encoded at runtime.

## Running the Application

You can run either interface, or both at the same time.

### Streamlit App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501). The sidebar lists the seven
tools; the landing page shows an overview and live hidden gems.

### FastAPI + React Client

Terminal 1 — start the API:

```bash
uvicorn backend.main:app --reload --port 8000
```

Interactive API documentation is available at
[http://localhost:8000/docs](http://localhost:8000/docs).

Terminal 2 — start the React client:

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The client calls
`http://127.0.0.1:8000` by default; set `VITE_API_URL` to override it.

## Usage Guide

1. **Mood to Scene** — Describe a feeling, not a genre, e.g. "a quiet film about
   grief by the sea". Choose how many results you want, then search.
2. **Watch Party** — Pick one to five films your group loves, optionally set a
   maximum runtime and shared genre, then find the film everyone can agree on.
3. **Time Budget & Bedtime** — Enter the minutes available and your start time.
   Enable calm-only if it is close to bedtime. Every card shows when the film ends.
4. **Double Feature** — Choose a film and a mode: **mirror** finds a kindred film
   from another decade, while **contrast** finds a shared genre with the opposite
   intensity.
5. **Cultural Bridge** — Choose a film to see international films that share its
   emotional and narrative fingerprint, with language badges.
6. **Era Machine** — Choose a film and a decade to find its closest contemporaries
   from that era.
7. **Hidden Gems** — Filter by genre and year range, then browse films ranked by
   gem score: strong ratings, low popularity.

## API Reference

All endpoints are served by `backend/main.py`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/search` | Semantic mood search (`query`, `top_k`) |
| `POST` | `/api/watch-party` | Group consensus from 1–5 movie ids, with optional filters |
| `POST` | `/api/time-budget` | Runtime fit (`minutes`, optional `start_clock`, `calm_only`) |
| `GET` | `/api/double-feature/{movie_id}` | Pairing (`mode=mirror\|contrast`) |
| `GET` | `/api/cultural-bridge/{movie_id}` | International counterparts (`top_k`) |
| `GET` | `/api/era-machine/{movie_id}` | Films from `decade` with similar fingerprints |
| `GET` | `/api/hidden-gems` | Filter by `genre`, `year_min`, `year_max`, `top_k` |
| `GET` | `/api/titles` | Title search for pickers (`q`, `limit`) |
| `GET` | `/api/movies/{movie_id}` | Full movie details |

Responses share the same movie shape: title, year, runtime, rating, weighted
rating, genres, language, overview, badges, and tool-specific scores such as
similarity, match, finish time, or intensity shift.

## Screenshots

**Home — seven ways in**

![Streamlit home screen with seven recommendation tools](docs/screenshots/streamlit-home.png)

**Hidden Gems — filtered and ranked by gem score**

![Hidden Gems results grid](docs/screenshots/streamlit-hidden-gems.png)

## Testing

Run the Python suite (engine, API, Streamlit flows, and edge cases):

```bash
pytest
```

The suite covers recommendation behaviour, API validation, empty states, and the
Streamlit journeys for all seven tools.

For the React client, start the API on port 8000 and Vite on port 5173, then run:

```bash
cd frontend
npm run e2e
```

The end-to-end script exercises mood search, hidden gems, watch party, time
budget, double feature, cultural bridge, era machine, the movie modal, and the
home page. It uses Microsoft Edge by default; set `EDGE_PATH` if Edge is installed
elsewhere.

## Contributing

1. Fork the repository and create a feature branch:
   `git checkout -b feat/your-feature`.
2. Keep changes focused and follow conventional commit messages
   (`feat:`, `fix:`, `chore:`, `test:`, `docs:`).
3. Run `pytest` and, when the client changes, `npm run lint` and the end-to-end
   script.
4. Open a pull request describing the problem and the change.

## Support

- Open an issue for bugs, ideas, or questions:
  [GitHub Issues](https://github.com/MoazzamFarooqui/A-Feeling-Called-Cinema/issues)
- Browse the generated API documentation while the backend is running:
  [http://localhost:8000/docs](http://localhost:8000/docs)
