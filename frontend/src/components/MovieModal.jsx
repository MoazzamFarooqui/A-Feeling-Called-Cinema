import { useEffect } from 'react'
import Icon from './Icon'

export default function MovieModal({ movie, onClose }) {
  useEffect(() => {
    const onKey = (event) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKey)
      document.body.style.overflow = previousOverflow
    }
  }, [onClose])

  if (!movie) return null

  const hue = Math.round((movie.id * 137.508) % 360)

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-panel"
        role="dialog"
        aria-modal="true"
        aria-label={movie.title}
        onClick={(event) => event.stopPropagation()}
      >
        <button type="button" className="modal-close" onClick={onClose} aria-label="Close details">
          <Icon name="close" size={18} />
        </button>

        <div className="modal-poster" style={{ '--hue': hue }}>
          <span className="modal-poster-initial" aria-hidden="true">
            {(movie.title || '?').trim().charAt(0).toUpperCase()}
          </span>
          <div className="modal-poster-bottom">
            <span className="poster-rating">
              <Icon name="star" size={12} />
              {Number(movie.vote_average).toFixed(1)}
            </span>
          </div>
        </div>

        <div className="modal-body">
          <h2>{movie.title}</h2>
          <p className="modal-sub">
            {movie.year} · {movie.decade_label} ·{' '}
            {Math.floor(movie.runtime / 60)}h {String(movie.runtime % 60).padStart(2, '0')}m ·{' '}
            {movie.intensity_label}
          </p>

          {movie.tagline && <p className="modal-tagline">“{movie.tagline}”</p>}

          <div className="genre-row">
            {movie.genres.map((genre) => (
              <span key={genre} className="chip">
                {genre}
              </span>
            ))}
          </div>

          <p className="modal-overview">{movie.overview}</p>

          <dl className="modal-facts">
            <div className="fact">
              <dt>Weighted rating</dt>
              <dd>{Number(movie.weighted_rating).toFixed(2)}</dd>
            </div>
            <div className="fact">
              <dt>Votes</dt>
              <dd>{Number(movie.vote_count).toLocaleString()}</dd>
            </div>
            <div className="fact">
              <dt>Language</dt>
              <dd>{movie.language.toUpperCase()}</dd>
            </div>
            <div className="fact">
              <dt>Studio</dt>
              <dd>{movie.main_studio || '—'}</dd>
            </div>
            <div className="fact">
              <dt>Gem score</dt>
              <dd>{Number(movie.gem_score).toFixed(2)}</dd>
            </div>
            <div className="fact">
              <dt>Popularity</dt>
              <dd>{Number(movie.popularity).toFixed(1)}</dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  )
}
