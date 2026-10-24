import { useState } from 'react'
import { getCulturalBridge } from '../api'
import Icon from '../components/Icon'
import MovieGrid from '../components/MovieGrid'
import MoviePicker from '../components/MoviePicker'
import PageHeader from '../components/PageHeader'

export default function CulturalBridge() {
  const [movie, setMovie] = useState(null)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)
  const [reference, setReference] = useState(null)

  const onSubmit = async (event) => {
    event.preventDefault()
    if (!movie) {
      setError('Pick a reference movie first.')
      return
    }
    setError('')
    setSearched(true)
    setResults([])
    setLoading(true)
    setReference(movie)
    try {
      const data = await getCulturalBridge(movie.id, 12)
      setResults(data.results)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <PageHeader
        icon="globe"
        title="Cultural Bridge"
        subtitle="Start with a Hollywood favorite. We'll surface the international films that share its soul — different language, same feeling."
      />

      <section className="tool-panel">
        <form onSubmit={onSubmit}>
          <div className="tool-grid tool-grid-narrow">
            <MoviePicker
              label="Your Hollywood favorite"
              selected={movie}
              onSelect={setMovie}
              placeholder="e.g. Inception, The Godfather…"
            />
          </div>

          <div className="tool-row">
            <button className="btn btn-primary" type="submit" disabled={loading || !movie}>
              {loading ? 'Crossing borders…' : 'Find its international soulmate'}
            </button>
            <span className="helper-text">Results are always non-English films.</span>
          </div>

          {error && !searched && <p className="form-error">{error}</p>}
        </form>
      </section>

      {searched && (
        <section className="section">
          <div className="section-head">
            <h2>
              International matches{reference ? ` for ${reference.title}` : ''}
            </h2>
            {!loading && !error && <span className="results-count">{results.length} films</span>}
          </div>
          <MovieGrid
            movies={results}
            loading={loading}
            error={error}
            skeletonCount={8}
            emptyTitle="No international matches found"
            emptyMessage="Try a different reference film."
          />
        </section>
      )}

      {!searched && (
        <section className="section intro-panel">
          <span className="empty-icon">
            <Icon name="globe" size={22} />
          </span>
          <h2>Same feeling, another language</h2>
          <p>
            Great stories travel. Pick a familiar English-language film and discover the
            films from around the world that live in the same emotional and thematic
            space.
          </p>
        </section>
      )}
    </>
  )
}
