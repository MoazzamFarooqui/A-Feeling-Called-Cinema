import os
import sys
import threading
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.schemas import (  # noqa: E402
    DoubleFeatureResponse,
    Movie,
    MovieListResponse,
    SearchRequest,
    SearchResponse,
    TimeBudgetRequest,
    TitlesResponse,
    WatchPartyRequest,
    WatchPartyResponse,
)
from src.recommender import VALID_DECADES, MovieRecommender  # noqa: E402

_rec_instance = None
_rec_lock = threading.Lock()


def get_recommender() -> MovieRecommender:
    global _rec_instance
    if _rec_instance is None:
        with _rec_lock:
            if _rec_instance is None:
                _rec_instance = MovieRecommender()
    return _rec_instance


app = FastAPI(
    title='Movie Recommendation API',
    version='1.0.0',
    description='Seven data-driven recommendation features over 25,706 movies.',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:3000',
        'http://127.0.0.1:3000',
        'http://localhost:4173',
        'http://127.0.0.1:4173',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
def root():
    return {
        'name': 'Movie Recommendation API',
        'version': '1.0.0',
        'docs': '/docs',
        'movies_loaded': 25706,
        'endpoints': [
            'POST /api/search',
            'POST /api/watch-party',
            'POST /api/time-budget',
            'GET /api/double-feature/{movie_id}',
            'GET /api/cultural-bridge/{movie_id}',
            'GET /api/era-machine/{movie_id}',
            'GET /api/hidden-gems',
            'GET /api/titles',
            'GET /api/movies/{movie_id}',
        ],
    }


def require_movie(rec: MovieRecommender, movie_id: int):
    if movie_id not in rec.id_to_idx:
        raise HTTPException(status_code=404, detail=f'Movie id {movie_id} not found')


@app.post('/api/search', response_model=SearchResponse)
def search(payload: SearchRequest, rec: MovieRecommender = Depends(get_recommender)):
    results = rec.semantic_search(payload.query, top_k=payload.top_k)
    return {'query': payload.query, 'count': len(results), 'results': results}


@app.post('/api/watch-party', response_model=WatchPartyResponse)
def watch_party(payload: WatchPartyRequest, rec: MovieRecommender = Depends(get_recommender)):
    if payload.year_min is not None and payload.year_max is not None \
            and payload.year_min > payload.year_max:
        raise HTTPException(status_code=400, detail='year_min must be <= year_max')
    unknown = [mid for mid in payload.movie_ids if mid not in rec.id_to_idx]
    if unknown:
        raise HTTPException(status_code=404, detail=f'Movie id(s) not found: {unknown}')
    results = rec.watch_party(
        payload.movie_ids,
        top_k=payload.top_k,
        max_runtime=payload.max_runtime,
        genres=payload.genres,
        year_min=payload.year_min,
        year_max=payload.year_max,
    )
    return {'count': len(results), 'results': results}


@app.post('/api/time-budget', response_model=MovieListResponse)
def time_budget(payload: TimeBudgetRequest, rec: MovieRecommender = Depends(get_recommender)):
    try:
        results = rec.time_budget(
            payload.minutes,
            start_clock=payload.start_clock,
            calm_only=payload.calm_only,
            top_k=payload.top_k,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {'count': len(results), 'results': results}


@app.get('/api/double-feature/{movie_id}', response_model=DoubleFeatureResponse)
def double_feature(
    movie_id: int,
    mode: str = Query('mirror', pattern='^(mirror|contrast)$'),
    rec: MovieRecommender = Depends(get_recommender),
):
    require_movie(rec, movie_id)
    try:
        return rec.double_feature(movie_id, mode=mode)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get('/api/cultural-bridge/{movie_id}', response_model=MovieListResponse)
def cultural_bridge(
    movie_id: int,
    top_k: int = Query(10, ge=1, le=50),
    rec: MovieRecommender = Depends(get_recommender),
):
    require_movie(rec, movie_id)
    results = rec.cultural_bridge(movie_id, top_k=top_k)
    return {'count': len(results), 'results': results}


@app.get('/api/era-machine/{movie_id}', response_model=MovieListResponse)
def era_machine(
    movie_id: int,
    decade: int = Query(..., ge=1920, le=2020),
    top_k: int = Query(10, ge=1, le=50),
    rec: MovieRecommender = Depends(get_recommender),
):
    require_movie(rec, movie_id)
    if decade not in VALID_DECADES:
        raise HTTPException(status_code=400, detail=f'decade must be one of {VALID_DECADES}')
    results = rec.era_time_machine(movie_id, decade, top_k=top_k)
    return {'count': len(results), 'results': results}


@app.get('/api/hidden-gems', response_model=MovieListResponse)
def hidden_gems(
    genre: Optional[str] = Query(None, max_length=50),
    year_min: Optional[int] = Query(None, ge=1920, le=2030),
    year_max: Optional[int] = Query(None, ge=1920, le=2030),
    top_k: int = Query(20, ge=1, le=50),
    rec: MovieRecommender = Depends(get_recommender),
):
    if year_min is not None and year_max is not None and year_min > year_max:
        raise HTTPException(status_code=400, detail='year_min must be <= year_max')
    results = rec.hidden_gems(genre=genre, year_min=year_min, year_max=year_max, top_k=top_k)
    return {'count': len(results), 'results': results}


@app.get('/api/titles', response_model=TitlesResponse)
def titles(
    q: str = Query(..., min_length=1, max_length=100),
    limit: int = Query(10, ge=1, le=20),
    rec: MovieRecommender = Depends(get_recommender),
):
    results = rec.search_titles(q, limit=limit)
    return {'count': len(results), 'results': results}


@app.get('/api/movies/{movie_id}', response_model=Movie)
def movie_details(movie_id: int, rec: MovieRecommender = Depends(get_recommender)):
    movie = rec.get_movie(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail=f'Movie id {movie_id} not found')
    return movie
