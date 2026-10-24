# A Feeling Called Cinema

A content-based film recommender built on 25,706 movies and 384-dimensional
semantic embeddings. Instead of scrolling through genres, you describe the
feeling, the time you have, the group you are watching with, or the film you
already love — and the engine finds what fits.

The project is a **Streamlit app** that exposes all seven recommendation tools.

## Table of Contents

- [Project Overview](#project-overview)
- [The Problem](#the-problem)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the App](#running-the-app)
- [Usage Guide](#usage-guide)
- [Screenshots](#screenshots)
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

- **Recommendation engine:** Python, pandas, NumPy, and
  `sentence-transformers/all-MiniLM-L6-v2`
- **Interface:** Streamlit with a custom black-and-white theme

## Project Structure

```text
.
├── app.py                      # Streamlit application
├── src/recommender.py          # Recommendation engine (all seven tools)
├── data/processed/             # Dataset, embeddings, and embedding ids
├── tests/                      # Engine, edge-case, and Streamlit tests
├── docs/screenshots/           # README screenshots
├── .streamlit/config.toml      # Streamlit theme
└── requirements.txt
```

## Installation

You need **Python 3.10 or newer**.

1. **Clone the repository**

   ```bash
   git clone https://github.com/MoazzamFarooqui/A-Feeling-Called-Cinema.git
   cd A-Feeling-Called-Cinema
   ```

2. **Install the Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

   If `pip` reports an "externally managed environment" error, create a virtual
   environment first:

   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS / Linux
   ```

3. **That's it.** The processed dataset and embeddings are already included, so
   there is no data prep step.

## Running the App

Start the Streamlit app:

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501). The sidebar lists the seven
tools; the landing page shows an overview and live hidden gems. An internet
connection is needed only on the first mood search, when the MiniLM model is
downloaded once and cached.

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

## Screenshots

### Home

<img width="1677" height="707" alt="image" src="https://github.com/user-attachments/assets/3e20b11c-d420-4622-9e5b-64b85cb1c584" />

<img width="1042" height="372" alt="image" src="https://github.com/user-attachments/assets/8a82eb07-c363-4cfe-91bb-9587ae87b4f9" />

---

### Mood to Scene

<img width="1662" height="802" alt="image" src="https://github.com/user-attachments/assets/6a49507e-dfbb-485f-88b9-8d451ac494c6" />

---

### Watch Party

<img width="1692" height="687" alt="image" src="https://github.com/user-attachments/assets/c5f4a3d5-9b09-4cda-9e90-e8d382e7480d" />

<img width="1010" height="352" alt="image" src="https://github.com/user-attachments/assets/0c2cc487-1f2d-422d-b3b4-422f74fe4082" />

---

### Time Budget

<img width="1617" height="842" alt="image" src="https://github.com/user-attachments/assets/0fc9a33d-1c23-48aa-be74-40cf861e03a8" />

---

### Double Feature

<img width="1788" height="837" alt="image" src="https://github.com/user-attachments/assets/bcd0ec4e-2a1b-4f6b-a8e9-e8b95b3b729e" />

---

### Cultural Bridge

<img width="1721" height="743" alt="image" src="https://github.com/user-attachments/assets/e6fcaf38-7057-4779-9ea8-a7124d360cbb" />

---

### Era Machine

<img width="1673" height="805" alt="image" src="https://github.com/user-attachments/assets/11176e00-01d2-4dea-b078-ee88789a299a" />

---

### Hidden Gems

<img width="1715" height="835" alt="image" src="https://github.com/user-attachments/assets/ec7d573a-458a-4b34-b6c9-9d93770b93ae" />

---

## Contributing

1. Fork the repository and create a feature branch:
   `git checkout -b feat/your-feature`.
2. Make your changes and check the app locally.
3. Open a pull request describing the problem and the change.

## Support

- Open an issue for bugs, ideas, or questions:
  [GitHub Issues](https://github.com/MoazzamFarooqui/A-Feeling-Called-Cinema/issues)
