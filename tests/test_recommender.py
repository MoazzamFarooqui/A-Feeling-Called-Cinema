import os
import sys
from datetime import datetime, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import MovieRecommender


@pytest.fixture(scope='module')
def rec():
    return MovieRecommender()


def movie_id(rec, title):
    for m in rec.search_titles(title, limit=20):
        if m['title'].lower() == title.lower():
            return m['id']
    raise AssertionError(f'Could not find movie titled {title!r}')


INCEPTION = 'Inception'
TOY_STORY = 'Toy Story'
GODFATHER = 'The Godfather'


# ---------------------------------------------------------------- Feature 1
def test_semantic_search_returns_ranked_results(rec):
    results = rec.semantic_search('astronaut space mission survival', top_k=5)
    assert len(results) == 5
    scores = [r['score'] for r in results]
    assert scores == sorted(scores, reverse=True)
    space_titles = {
        'Interstellar', 'The Martian', 'Gravity', 'Apollo 13', 'Sunshine', 'Moon',
        '2001: A Space Odyssey', 'First Man', 'Contact', 'Armageddon', 'The Right Stuff',
        'Europa Report', 'Stowaway', 'Ad Astra',
    }
    scifi_or_space = sum(
        1 for r in results
        if 'Science Fiction' in r['genres'] or r['title'] in space_titles
    )
    assert scifi_or_space >= 3


def test_semantic_search_empty_query_raises(rec):
    with pytest.raises(ValueError):
        rec.semantic_search('   ')


# ---------------------------------------------------------------- Feature 2
def test_watch_party_returns_shared_taste_picks(rec):
    picks = [movie_id(rec, INCEPTION), movie_id(rec, TOY_STORY)]
    results = rec.watch_party(picks, top_k=8)
    assert len(results) == 8
    ids = {r['id'] for r in results}
    assert not ids.intersection(picks)
    scores = [r['score'] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_watch_party_respects_runtime_filter(rec):
    picks = [movie_id(rec, INCEPTION)]
    results = rec.watch_party(picks, top_k=10, max_runtime=100)
    assert results
    assert all(r['runtime'] <= 100 for r in results)


def test_watch_party_unknown_id_raises(rec):
    with pytest.raises(ValueError):
        rec.watch_party([999999999])


# ---------------------------------------------------------------- Feature 3
def test_time_budget_filters_and_computes_finish_time(rec):
    results = rec.time_budget(95, start_clock='21:45', top_k=10)
    assert results
    assert all(r['runtime'] <= 95 for r in results)
    ratings = [r['weighted_rating'] for r in results]
    assert ratings == sorted(ratings, reverse=True)
    first = results[0]
    expected = datetime.strptime('21:45', '%H:%M') + timedelta(minutes=first['runtime'])
    assert first['finish_time'] == expected.strftime('%H:%M')


def test_time_budget_calm_only(rec):
    results = rec.time_budget(120, calm_only=True, top_k=10)
    assert results
    assert all(r['runtime'] <= 120 for r in results)
    assert all(r['intensity_label'].lower() in ('calm', 'mild') for r in results)


def test_time_budget_invalid_clock_raises(rec):
    with pytest.raises(ValueError):
        rec.time_budget(90, start_clock='25:99')


# ---------------------------------------------------------------- Feature 4
def test_double_feature_mirror(rec):
    base_id = movie_id(rec, INCEPTION)
    pair = rec.double_feature(base_id, mode='mirror')
    assert pair['mode'] == 'mirror'
    assert len(pair['playlist']) == 2
    base, partner = pair['playlist']
    assert base['id'] == base_id
    assert partner['id'] != base_id
    assert partner['decade_label'] != base['decade_label']
    assert partner['similarity'] > 0


def test_double_feature_contrast(rec):
    base_id = movie_id(rec, GODFATHER)
    pair = rec.double_feature(base_id, mode='contrast')
    base, partner = pair['playlist']
    assert set(base['genres']).intersection(partner['genres'])
    assert abs(partner['intensity_shift']) >= 0.3


def test_double_feature_invalid_mode_raises(rec):
    with pytest.raises(ValueError):
        rec.double_feature(movie_id(rec, INCEPTION), mode='sequel')


# ---------------------------------------------------------------- Feature 5
def test_cultural_bridge_returns_foreign_only(rec):
    results = rec.cultural_bridge(movie_id(rec, INCEPTION), top_k=10)
    assert len(results) == 10
    assert all(r['is_foreign'] for r in results)
    scores = [r['similarity'] for r in results]
    assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------- Feature 6
def test_era_time_machine_returns_target_decade(rec):
    results = rec.era_time_machine(movie_id(rec, INCEPTION), 1980, top_k=10)
    assert len(results) == 10
    assert all(r['year'] // 10 * 10 == 1980 for r in results)
    scores = [r['similarity'] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_era_time_machine_invalid_decade_raises(rec):
    with pytest.raises(ValueError):
        rec.era_time_machine(movie_id(rec, INCEPTION), 1985)


# ---------------------------------------------------------------- Feature 7
def test_hidden_gems_sorted_and_flagged(rec):
    results = rec.hidden_gems(top_k=20)
    assert len(results) == 20
    assert all(r['is_hidden_gem'] for r in results)
    scores = [r['gem_score'] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_hidden_gems_genre_and_year_filters(rec):
    results = rec.hidden_gems(genre='Drama', year_min=1970, year_max=2010, top_k=15)
    assert results
    assert all('Drama' in r['genres'] for r in results)
    assert all(1970 <= r['year'] <= 2010 for r in results)


# ---------------------------------------------------------------- Helpers
def test_get_movie_and_unknown(rec):
    movie = rec.get_movie(movie_id(rec, INCEPTION))
    assert movie['title'] == INCEPTION
    assert movie['genres']
    assert rec.get_movie(999999999) is None


def test_search_titles_finds_prefix(rec):
    hits = rec.search_titles('inception')
    assert any(h['title'] == INCEPTION for h in hits)


def test_csv_and_embeddings_alignment(rec):
    assert len(rec.df) == 25706
    assert rec.embeddings.shape == (25706, 384)
    assert len(rec.id_to_idx) == 25706
