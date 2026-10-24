import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getHiddenGems } from '../api'
import { FEATURES } from '../features'
import EmptyState from '../components/EmptyState'
import Icon from '../components/Icon'
import MovieCard from '../components/MovieCard'
import SkeletonCard from '../components/SkeletonCard'

export default function Home() {
  const [gems, setGems] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getHiddenGems({ topK: 6 })
      .then((data) => {
        if (active) setGems(data.results)
      })
      .catch((err) => {
        if (active) setError(err.message)
      })
    return () => {
      active = false
    }
  }, [])

  return (
    <>
      <section className="hero">
        <p className="hero-eyebrow">Seven ways to find your next film</p>
        <h1>
          Stop scrolling. Start <em>watching</em>.
        </h1>
        <p className="hero-sub">
          A Feeling Called Cinema reads the mood, the clock, the group chat, and the decade — then
          finds the film that fits. 25,706 titles, ranked by what actually matters
          to you.
        </p>
        <div className="hero-actions">
          <Link className="btn btn-primary" to="/hidden-gems">
            <Icon name="gem" size={17} />
            Find a hidden gem
          </Link>
          <Link className="btn btn-ghost" to="/mood">
            <Icon name="search" size={17} />
            Search by mood
          </Link>
        </div>
        <div className="hero-stats">
          <div className="hero-stat">
            <strong>25,706</strong>
            <span>Films indexed</span>
          </div>
          <div className="hero-stat">
            <strong>7</strong>
            <span>Discovery tools</span>
          </div>
          <div className="hero-stat">
            <strong>384</strong>
            <span>Dimensions of taste</span>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <h2>Explore the tools</h2>
          <Link className="section-link" to="/mood">
            Start with a mood
            <Icon name="arrow" size={15} />
          </Link>
        </div>
        <div className="feature-grid">
          {FEATURES.map((feature) => (
            <Link key={feature.path} to={feature.path} className="feature-card">
              <span className="feature-icon">
                <Icon name={feature.icon} size={21} />
              </span>
              <h3>{feature.title}</h3>
              <p>{feature.blurb}</p>
              <span className="feature-open">
                Open tool
                <Icon name="arrow" size={14} />
              </span>
            </Link>
          ))}
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <h2>Tonight&apos;s hidden gems</h2>
          <Link className="section-link" to="/hidden-gems">
            See all
            <Icon name="arrow" size={15} />
          </Link>
        </div>

        {error ? (
          <EmptyState
            icon="film"
            title="Backend not reachable"
            message={error}
            hint=".\\venv\\Scripts\\python.exe -m uvicorn backend.main:app --reload"
          />
        ) : (
          <div className="movie-grid">
            {gems
              ? gems.map((movie) => <MovieCard key={movie.id} movie={movie} />)
              : Array.from({ length: 6 }, (_, index) => <SkeletonCard key={index} />)}
          </div>
        )}
      </section>
    </>
  )
}
