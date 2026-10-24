import ast
import os
import sys
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'movies_clean_v2.csv')
EMBEDDINGS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'embeddings.npy')
IDS_PATH = os.path.join(BASE_DIR, 'data', 'processed', 'embedding_ids.npy')

MODEL_NAME = 'sentence-transformers/all-MiniLM-L6-v2'
OVERVIEW_LIMIT = 500
VALID_DECADES = [1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]


def parse_list(val):
    if isinstance(val, list):
        return val
    if pd.isna(val) or val == '':
        return []
    try:
        parsed = ast.literal_eval(val)
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []


def to_py(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


class MovieRecommender:
    def __init__(self, data_path=DATA_PATH, embeddings_path=EMBEDDINGS_PATH, ids_path=IDS_PATH):
        self.df = pd.read_csv(data_path, low_memory=False)
        self.embeddings = np.load(embeddings_path)
        emb_ids = np.load(ids_path)

        if not np.array_equal(self.df['id'].to_numpy(), emb_ids):
            pos = {int(mid): i for i, mid in enumerate(emb_ids)}
            self.df = self.df.set_index('id').loc[emb_ids].reset_index()

        self.df = self.df.reset_index(drop=True)
        self.genres = self.df['genres_list'].apply(parse_list).tolist()
        self.id_to_idx = {int(mid): i for i, mid in enumerate(self.df['id'].tolist())}
        self.genre_members = {}
        for idx, names in enumerate(self.genres):
            for name in names:
                self.genre_members.setdefault(str(name).strip().lower(), set()).add(idx)
        self.is_hidden_gem = self.df['is_hidden_gem'].fillna(False).to_numpy(dtype=bool)
        self.gem_scores = self.df['gem_score'].to_numpy(dtype=float)
        self.years = self.df['year'].to_numpy(dtype=int)
        self._model = None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(MODEL_NAME)
        return self._model

    def _format(self, idx, score=None, **extra):
        row = self.df.iloc[idx]
        overview = str(row['overview'])
        if len(overview) > OVERVIEW_LIMIT:
            overview = overview[:OVERVIEW_LIMIT].rsplit(' ', 1)[0] + '...'
        result = {
            'id': int(row['id']),
            'title': str(row['title']),
            'year': int(row['year']),
            'decade_label': str(row['decade_label']),
            'runtime': int(row['runtime']),
            'vote_average': round(float(row['vote_average']), 2),
            'vote_count': int(row['vote_count']),
            'weighted_rating': round(float(row['weighted_rating']), 3),
            'popularity': round(float(row['popularity']), 2),
            'gem_score': round(float(row['gem_score']), 3),
            'is_hidden_gem': bool(row['is_hidden_gem']),
            'genres': list(self.genres[idx]),
            'language': str(row['original_language']),
            'is_foreign': bool(row['is_foreign']),
            'intensity_label': str(row['intensity_label']),
            'main_studio': str(row['main_studio']),
            'tagline': '' if pd.isna(row['tagline']) else str(row['tagline']),
            'overview': overview,
        }
        if score is not None:
            result['score'] = round(float(score), 4)
        result.update(extra)
        if 'similarity' in result:
            result['similarity'] = round(float(result['similarity']), 4)
        return result

    def _movie_idx(self, movie_id):
        idx = self.id_to_idx.get(int(movie_id))
        if idx is None:
            raise ValueError(f'Movie id {movie_id} not found')
        return idx

    def get_movie(self, movie_id):
        idx = self.id_to_idx.get(int(movie_id))
        if idx is None:
            return None
        return self._format(idx)

    def search_titles(self, query, limit=10):
        q = str(query).strip().lower()
        if not q:
            return []
        mask = self.df['title'].str.lower().str.contains(q, regex=False, na=False)
        hits = self.df[mask].sort_values('popularity', ascending=False).head(limit)
        return [
            {'id': int(r['id']), 'title': str(r['title']), 'year': int(r['year'])}
            for _, r in hits.iterrows()
        ]

    def _passes(self, idx, max_runtime=None, genres=None, year_min=None, year_max=None):
        row = self.df.iloc[idx]
        if max_runtime is not None and int(row['runtime']) > max_runtime:
            return False
        if genres:
            wanted = {g.lower() for g in genres}
            if not wanted.intersection({g.lower() for g in self.genres[idx]}):
                return False
        if year_min is not None and int(row['year']) < year_min:
            return False
        if year_max is not None and int(row['year']) > year_max:
            return False
        return True

    # ------------------------------------------------------------------
    # Feature 1 — Mood-to-Scene Semantic Engine
    # ------------------------------------------------------------------
    def semantic_search(self, query, top_k=10):
        if not str(query).strip():
            raise ValueError('Query must not be empty')
        model = self._ensure_model()
        q_vec = model.encode([str(query)], convert_to_numpy=True, normalize_embeddings=True)[0]
        scores = self.embeddings @ q_vec
        order = np.argsort(-scores)[:top_k]
        return [self._format(int(i), score=scores[i]) for i in order]

    # ------------------------------------------------------------------
    # Feature 2 — Watch Party Multi-User Conflict Resolver
    # ------------------------------------------------------------------
    def watch_party(self, movie_ids, top_k=10, max_runtime=None, genres=None,
                    year_min=None, year_max=None):
        if not movie_ids:
            raise ValueError('At least one movie id is required')
        picks = [self._movie_idx(mid) for mid in movie_ids]
        if len(picks) > 5:
            raise ValueError('Watch party supports at most 5 movies')

        centroid = self.embeddings[picks].mean(axis=0)
        norm = np.linalg.norm(centroid)
        if norm > 0:
            centroid = centroid / norm
        scores = self.embeddings @ centroid

        exclude = set(picks)

        def collect(use_genres=True, use_years=True):
            out = []
            for i in np.argsort(-scores):
                i = int(i)
                if i in exclude:
                    continue
                if not self._passes(i, max_runtime=max_runtime,
                                    genres=genres if use_genres else None,
                                    year_min=year_min if use_years else None,
                                    year_max=year_max if use_years else None):
                    continue
                out.append(self._format(i, score=scores[i]))
                if len(out) >= top_k:
                    break
            return out

        results = collect()
        relaxed = False
        if not results and genres:
            results = collect(use_genres=False)
            relaxed = True
        if not results:
            results = collect(use_genres=False, use_years=False)
            relaxed = True
        if relaxed:
            for r in results:
                r['note'] = 'filters relaxed to find common ground'
        return results

    # ------------------------------------------------------------------
    # Feature 3 — Time-Budget & Evening Schedule Recommender
    # ------------------------------------------------------------------
    def time_budget(self, minutes, start_clock=None, calm_only=False, top_k=10):
        if minutes is None or int(minutes) <= 0:
            raise ValueError('minutes must be a positive number')
        minutes = int(minutes)

        start_dt = None
        if start_clock:
            try:
                start_dt = datetime.strptime(str(start_clock).strip(), '%H:%M')
            except ValueError:
                raise ValueError('start_clock must use HH:MM (24-hour) format')

        runtime_values = self.df['runtime'].to_numpy()
        mask = runtime_values <= minutes
        if calm_only:
            mask &= self.df['bedtime_safe'].fillna(False).to_numpy(dtype=bool)

        candidates = self.df.loc[mask].sort_values(
            ['weighted_rating', 'vote_count', 'runtime'],
            ascending=[False, False, True],
        ).head(top_k)

        results = []
        for movie_id, runtime in zip(candidates['id'], candidates['runtime']):
            extra = {}
            if start_dt is not None:
                finish = start_dt + timedelta(minutes=int(runtime))
                extra['finish_time'] = finish.strftime('%H:%M')
            results.append(self._format(self.id_to_idx[int(movie_id)], **extra))
        return results

    # ------------------------------------------------------------------
    # Feature 4 — Cinematic Companion Double Feature Pairing
    # ------------------------------------------------------------------
    def double_feature(self, movie_id, mode='mirror'):
        if mode not in ('mirror', 'contrast'):
            raise ValueError("mode must be 'mirror' or 'contrast'")
        idx = self._movie_idx(movie_id)
        base = self._format(idx)
        scores = self.embeddings @ self.embeddings[idx]
        scores[idx] = -1

        if mode == 'mirror':
            base_decade = self.df.iloc[idx]['decade']
            partner = None
            for threshold in (0.6, 0.5, 0.45, 0.4, 0.0):
                candidates = [
                    int(i) for i in np.argsort(-scores)
                    if int(i) != idx
                    and float(scores[i]) >= threshold
                    and self.df.iloc[int(i)]['decade'] != base_decade
                ]
                if candidates:
                    partner = candidates[0]
                    break
            if partner is None:
                raise ValueError('No suitable mirror partner found')
            partner_result = self._format(partner, similarity=float(scores[partner]))
        else:
            base_genres = {g.lower() for g in self.genres[idx]}
            base_intensity = float(self.df.iloc[idx]['intensity_score'])
            candidates = []
            for i in np.argsort(-scores):
                i = int(i)
                if i == idx:
                    continue
                overlap = base_genres.intersection({g.lower() for g in self.genres[i]})
                if not overlap:
                    continue
                diff = abs(float(self.df.iloc[i]['intensity_score']) - base_intensity)
                candidates.append((len(overlap), diff, float(self.df.iloc[i]['weighted_rating']), i))

            candidates.sort(key=lambda c: (-c[0], -c[1], -c[2]))
            strong = [c for c in candidates if c[1] >= 0.3]
            chosen = strong[0] if strong else (candidates[0] if candidates else None)
            if chosen is None:
                raise ValueError('No suitable contrast partner found')
            partner = chosen[3]
            partner_result = self._format(
                partner,
                intensity_shift=round(float(self.df.iloc[partner]['intensity_score']) - base_intensity, 3),
            )

        return {
            'mode': mode,
            'playlist': [base, partner_result],
        }

    # ------------------------------------------------------------------
    # Feature 5 — Cultural Bridge International Mirror
    # ------------------------------------------------------------------
    def cultural_bridge(self, movie_id, top_k=10):
        idx = self._movie_idx(movie_id)
        scores = self.embeddings @ self.embeddings[idx]
        scores[idx] = -1
        results = []
        for i in np.argsort(-scores):
            i = int(i)
            if i == idx:
                continue
            if not bool(self.df.iloc[i]['is_foreign']):
                continue
            results.append(self._format(i, similarity=float(scores[i])))
            if len(results) >= top_k:
                break
        return results

    # ------------------------------------------------------------------
    # Feature 6 — Era & Nostalgia Time Machine
    # ------------------------------------------------------------------
    def era_time_machine(self, movie_id, decade, top_k=10):
        decade = int(decade)
        if decade not in VALID_DECADES:
            raise ValueError(f'decade must be one of {VALID_DECADES}')
        idx = self._movie_idx(movie_id)
        scores = self.embeddings @ self.embeddings[idx]
        scores[idx] = -1

        results = []
        for i in np.argsort(-scores):
            i = int(i)
            if i == idx:
                continue
            if int(self.df.iloc[i]['decade']) != decade:
                continue
            results.append(self._format(i, similarity=float(scores[i])))
            if len(results) >= top_k:
                break
        return results

    # ------------------------------------------------------------------
    # Feature 7 — Hidden Gem Filter
    # ------------------------------------------------------------------
    def hidden_gems(self, genre=None, year_min=None, year_max=None, top_k=20):
        mask = self.is_hidden_gem.copy()
        if genre:
            members = self.genre_members.get(str(genre).strip().lower())
            if not members:
                return []
            genre_mask = np.zeros(len(self.df), dtype=bool)
            genre_mask[np.fromiter(members, dtype=np.int64)] = True
            mask &= genre_mask
        if year_min is not None:
            mask &= self.years >= int(year_min)
        if year_max is not None:
            mask &= self.years <= int(year_max)

        positions = np.flatnonzero(mask)
        if positions.size == 0:
            return []
        order = positions[np.argsort(-self.gem_scores[positions])][:top_k]
        return [self._format(int(i)) for i in order]

if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    rec = MovieRecommender()

    def first_id(title):
        for movie in rec.search_titles(title, limit=5):
            if movie['title'].lower() == title.lower():
                return movie['id']
        raise SystemExit(f'{title} not found')

    def show(label, rows, keys):
        print(f'\n--- {label} ---')
        for row in rows:
            print('  ' + ' | '.join(f'{k}: {row[k]}' for k in keys if k in row))

    inception = first_id('Inception')
    toy_story = first_id('Toy Story')
    godfather = first_id('The Godfather')

    show('Mood: claustrophobic submarine thriller',
         rec.semantic_search('claustrophobic submarine thriller', 5),
         ('title', 'year', 'score'))
    show('Watch Party: Inception + Toy Story',
         rec.watch_party([inception, toy_story], top_k=5),
         ('title', 'year', 'genres', 'score'))
    show('Time Budget: 95 min from 21:45, calm',
         rec.time_budget(95, '21:45', calm_only=True, top_k=5),
         ('title', 'runtime', 'weighted_rating', 'finish_time'))
    show('Double Feature (mirror): Inception',
         rec.double_feature(inception, 'mirror')['playlist'],
         ('title', 'year', 'similarity'))
    show('Double Feature (contrast): The Godfather',
         rec.double_feature(godfather, 'contrast')['playlist'],
         ('title', 'year', 'genres', 'intensity_label', 'intensity_shift'))
    show('Cultural Bridge: Inception',
         rec.cultural_bridge(inception, 5),
         ('title', 'year', 'language', 'similarity'))
    show('Era Time Machine: Inception -> 1980s',
         rec.era_time_machine(inception, 1980, 5),
         ('title', 'year', 'similarity'))
    show('Hidden Gems: Drama',
         rec.hidden_gems('Drama', top_k=5),
         ('title', 'year', 'gem_score'))
