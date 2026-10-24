import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import MovieRecommender


@pytest.fixture(scope='module')
def rec():
    return MovieRecommender()


def movie_id(rec, title):
    for movie in rec.search_titles(title, limit=20):
        if movie['title'].lower() == title.lower():
            return movie['id']
    raise AssertionError(f'Could not find movie titled {title!r}')


def test_single_person_watch_party(rec):
    results = rec.watch_party([movie_id(rec, 'Inception')], top_k=5)
    assert len(results) == 5
    assert all(result['id'] != movie_id(rec, 'Inception') for result in results)


def test_watch_party_impossible_runtime_cap_returns_empty(rec):
    assert rec.watch_party([movie_id(rec, 'Inception')], max_runtime=1) == []


def test_time_budget_too_small_returns_empty_list(rec):
    assert rec.time_budget(30) == []


def test_time_budget_minimum_realistic_window(rec):
    results = rec.time_budget(45, start_clock='23:30', top_k=10)
    assert results
    assert all(result['runtime'] <= 45 for result in results)
    assert all('finish_time' in result for result in results)


def test_gibberish_mood_query_still_returns_ranked_results(rec):
    results = rec.semantic_search('zxqv blorf 99', top_k=5)
    assert len(results) == 5
    scores = [result['score'] for result in results]
    assert scores == sorted(scores, reverse=True)


def test_gibberish_title_search_returns_empty(rec):
    assert rec.search_titles('zzzzqqqxxx') == []


def test_impossible_hidden_gem_filters_return_empty(rec):
    assert rec.hidden_gems(genre='TV Movie', year_min=1920, year_max=1920, top_k=10) == []


def test_hidden_gems_unknown_genre_returns_empty(rec):
    assert rec.hidden_gems(genre='Not A Genre', top_k=10) == []


def test_obscure_movie_can_still_bridge_cultures(rec):
    obscure_id = int(rec.df.iloc[-1]['id'])
    results = rec.cultural_bridge(obscure_id, top_k=5)
    assert len(results) == 5
    assert all(result['is_foreign'] for result in results)


def test_obscure_movie_works_in_every_movie_feature(rec):
    obscure_id = int(rec.df.iloc[-1]['id'])

    party = rec.watch_party([obscure_id], top_k=3)
    assert len(party) == 3

    pair = rec.double_feature(obscure_id, mode='contrast')
    assert len(pair['playlist']) == 2

    era = rec.era_time_machine(obscure_id, 1970, top_k=3)
    assert len(era) == 3
    assert all(result['year'] // 10 * 10 == 1970 for result in era)


def test_unknown_movie_ids_raise_friendly_value_errors(rec):
    with pytest.raises(ValueError):
        rec.double_feature(999999999, mode='mirror')
    with pytest.raises(ValueError):
        rec.era_time_machine(999999999, 1990)
    with pytest.raises(ValueError):
        rec.cultural_bridge(999999999)
