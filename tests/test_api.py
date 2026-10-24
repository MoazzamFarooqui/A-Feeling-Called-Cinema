import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main import app


@pytest.fixture(scope='module')
def client():
    with TestClient(app) as c:
        yield c


def test_root_lists_endpoints(client):
    r = client.get('/')
    assert r.status_code == 200
    body = r.json()
    assert len(body['endpoints']) == 9


def test_openapi_docs_available(client):
    r = client.get('/openapi.json')
    assert r.status_code == 200
    paths = r.json()['paths']
    api_paths = [p for p in paths if p.startswith('/api/')]
    assert '/api/search' in paths
    assert '/api/hidden-gems' in paths
    assert len(api_paths) == 9


def test_titles_autocomplete(client):
    r = client.get('/api/titles', params={'q': 'incept'})
    assert r.status_code == 200
    titles = [m['title'] for m in r.json()['results']]
    assert 'Inception' in titles


def test_titles_requires_query(client):
    assert client.get('/api/titles').status_code == 422


def test_movie_details_and_404(client):
    r = client.get('/api/movies/27205')
    assert r.status_code == 200
    assert r.json()['title'] == 'Inception'
    assert r.json()['genres']
    assert client.get('/api/movies/999999999').status_code == 404


def test_semantic_search(client):
    r = client.post('/api/search', json={'query': 'submarine thriller', 'top_k': 5})
    assert r.status_code == 200
    body = r.json()
    assert body['count'] == 5
    assert len(body['results']) == 5
    assert all('score' in m for m in body['results'])


def test_semantic_search_validation(client):
    assert client.post('/api/search', json={'query': '', 'top_k': 5}).status_code == 422
    assert client.post('/api/search', json={'query': 'x', 'top_k': 51}).status_code == 422


def test_watch_party(client):
    r = client.post('/api/watch-party', json={'movie_ids': [27205, 862], 'top_k': 5})
    assert r.status_code == 200
    body = r.json()
    assert body['count'] == 5
    ids = {m['id'] for m in body['results']}
    assert not ids.intersection({27205, 862})


def test_watch_party_unknown_movie(client):
    r = client.post('/api/watch-party', json={'movie_ids': [999999999], 'top_k': 5})
    assert r.status_code == 404


def test_watch_party_empty_list_rejected(client):
    assert client.post('/api/watch-party', json={'movie_ids': [], 'top_k': 5}).status_code == 422


def test_time_budget(client):
    r = client.post('/api/time-budget',
                    json={'minutes': 90, 'start_clock': '21:30', 'calm_only': True, 'top_k': 5})
    assert r.status_code == 200
    body = r.json()
    assert body['count'] == 5
    assert all(m['runtime'] <= 90 for m in body['results'])
    assert all(m['finish_time'] for m in body['results'])


def test_time_budget_invalid_clock(client):
    r = client.post('/api/time-budget', json={'minutes': 90, 'start_clock': '25:99'})
    assert r.status_code == 422


def test_double_feature_modes(client):
    r = client.get('/api/double-feature/27205', params={'mode': 'mirror'})
    assert r.status_code == 200
    body = r.json()
    assert body['mode'] == 'mirror'
    assert len(body['playlist']) == 2
    assert body['playlist'][0]['decade_label'] != body['playlist'][1]['decade_label']

    r = client.get('/api/double-feature/238', params={'mode': 'contrast'})
    assert r.status_code == 200
    assert len(r.json()['playlist']) == 2


def test_double_feature_invalid(client):
    assert client.get('/api/double-feature/27205', params={'mode': 'sequel'}).status_code == 422
    assert client.get('/api/double-feature/999999999').status_code == 404


def test_cultural_bridge(client):
    r = client.get('/api/cultural-bridge/27205', params={'top_k': 5})
    assert r.status_code == 200
    results = r.json()['results']
    assert len(results) == 5
    assert all(m['is_foreign'] for m in results)


def test_era_machine(client):
    r = client.get('/api/era-machine/27205', params={'decade': 1980, 'top_k': 5})
    assert r.status_code == 200
    results = r.json()['results']
    assert len(results) == 5
    assert all(m['year'] // 10 * 10 == 1980 for m in results)


def test_era_machine_invalid_decade(client):
    assert client.get('/api/era-machine/27205', params={'decade': 1985}).status_code == 400
    assert client.get('/api/era-machine/27205', params={'decade': 1800}).status_code == 422


def test_hidden_gems(client):
    r = client.get('/api/hidden-gems')
    assert r.status_code == 200
    results = r.json()['results']
    assert len(results) == 20
    assert all(m['is_hidden_gem'] for m in results)

    r = client.get('/api/hidden-gems',
                   params={'genre': 'Drama', 'year_min': 1970, 'year_max': 2010, 'top_k': 10})
    assert r.status_code == 200
    results = r.json()['results']
    assert results
    assert all('Drama' in m['genres'] for m in results)
    assert all(1970 <= m['year'] <= 2010 for m in results)


def test_hidden_gems_bad_year_range(client):
    r = client.get('/api/hidden-gems', params={'year_min': 2000, 'year_max': 1990})
    assert r.status_code == 400
