import Icon from './Icon'

function formatRuntime(minutes) {
  if (minutes == null) return ''
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return hours > 0 ? `${hours}h ${String(rest).padStart(2, '0')}m` : `${rest}m`
}

export default function MovieCard({ movie, onOpen }) {
  const hue = Math.round((movie.id * 137.508) % 360)
  const match = movie.score ?? movie.similarity
  const genres = (movie.genres || []).slice(0, 3)
  const initial = (movie.title || '?').trim().charAt(0).toUpperCase()
  const interactive = Boolean(onOpen)

  return (
    <article
      className={`movie-card${interactive ? ' movie-card-clickable' : ''}`}
      style={{ '--hue': hue }}
      onClick={interactive ? onOpen : undefined}
      onKeyDown={
        interactive
          ? (event) => {
              if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault()
                onOpen()
              }
            }
          : undefined
      }
      role={interactive ? 'button' : undefined}
      tabIndex={interactive ? 0 : undefined}
    >
      <div className="movie-poster">
        <span className="poster-initial" aria-hidden="true">
          {initial}
        </span>

        <div className="poster-top">
          <div className="badge-row">
            {movie.is_hidden_gem && <span className="badge badge-gem">Hidden gem</span>}
            {movie.is_foreign && (
              <span className="badge badge-lang">{String(movie.language).toUpperCase()}</span>
            )}
          </div>
          <span className="poster-rating">
            <Icon name="star" size={12} />
            {Number(movie.vote_average).toFixed(1)}
          </span>
        </div>

        <div className="poster-bottom">
          <h3 className="poster-title">{movie.title}</h3>
          <p className="poster-sub">
            {movie.year} · {formatRuntime(movie.runtime)}
          </p>
        </div>
      </div>

      <div className="movie-body">
        {genres.length > 0 && (
          <div className="genre-row">
            {genres.map((genre) => (
              <span key={genre} className="chip">
                {genre}
              </span>
            ))}
          </div>
        )}

        <div className="meta-row">
          {match != null && (
            <span className="meta-pill meta-match">
              <Icon name="target" size={12} />
              {Math.round(match * 100)}% match
            </span>
          )}
          {movie.finish_time && (
            <span className="meta-pill">
              <Icon name="clock" size={12} />
              Ends {movie.finish_time}
            </span>
          )}
          {movie.intensity_label && (
            <span className={`meta-pill intensity-${movie.intensity_label}`}>
              {movie.intensity_label}
            </span>
          )}
          {movie.is_hidden_gem && movie.gem_score != null && (
            <span className="meta-pill meta-gem">Gem {Number(movie.gem_score).toFixed(1)}</span>
          )}
        </div>

        {movie.note && <p className="card-note">{movie.note}</p>}
      </div>
    </article>
  )
}
