from typing import List, Optional

from pydantic import BaseModel, Field


class Movie(BaseModel):
    id: int
    title: str
    year: int
    decade_label: str
    runtime: int
    vote_average: float
    vote_count: int
    weighted_rating: float
    popularity: float
    gem_score: float
    is_hidden_gem: bool
    genres: List[str]
    language: str
    is_foreign: bool
    intensity_label: str
    main_studio: str
    tagline: str
    overview: str
    score: Optional[float] = None
    similarity: Optional[float] = None
    note: Optional[str] = None
    finish_time: Optional[str] = None
    intensity_shift: Optional[float] = None


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500,
                       examples=['claustrophobic submarine thriller'])
    top_k: int = Field(10, ge=1, le=50)


class SearchResponse(BaseModel):
    query: str
    count: int
    results: List[Movie]


class WatchPartyRequest(BaseModel):
    movie_ids: List[int] = Field(..., min_length=1, max_length=5,
                                 examples=[[27205, 862]])
    top_k: int = Field(10, ge=1, le=50)
    max_runtime: Optional[int] = Field(None, ge=1, le=600)
    genres: Optional[List[str]] = None
    year_min: Optional[int] = Field(None, ge=1920, le=2030)
    year_max: Optional[int] = Field(None, ge=1920, le=2030)


class WatchPartyResponse(BaseModel):
    count: int
    results: List[Movie]


class TimeBudgetRequest(BaseModel):
    minutes: int = Field(..., gt=0, le=600, examples=[95])
    start_clock: Optional[str] = Field(
        None, pattern=r'^([01]\d|2[0-3]):[0-5]\d$', examples=['21:45'])
    calm_only: bool = False
    top_k: int = Field(10, ge=1, le=50)


class MovieListResponse(BaseModel):
    count: int
    results: List[Movie]


class DoubleFeatureResponse(BaseModel):
    mode: str
    playlist: List[Movie]


class TitleSuggestion(BaseModel):
    id: int
    title: str
    year: int


class TitlesResponse(BaseModel):
    count: int
    results: List[TitleSuggestion]
