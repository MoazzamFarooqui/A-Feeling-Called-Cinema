import { useState } from 'react'
import { getDoubleFeature } from '../api'
import Icon from '../components/Icon'
import MovieGrid from '../components/MovieGrid'
import MoviePicker from '../components/MoviePicker'
import PageHeader from '../components/PageHeader'
import Segmented from '../components/Segmented'

const MODES = [
  { value: 'mirror', label: 'Mirror' },
  { value: 'contrast', label: 'Contrast' },
]

const MODE_COPY = {
  mirror: 'A film with the same energy — but from a different decade.',
  contrast: 'A film that shares a genre yet flips the intensity.',
}

export default function DoubleFeature() {
  const [movie, setMovie] = useState(null)
  const [mode, setMode] = useState('mirror')
  const [playlist, setPlaylist] = useState([])
  const [resultMode, setResultMode] = useState('mirror')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const onSubmit = async (event) => {
    event.preventDefault()
    if (!movie) {
      setError('Pick a reference movie first.')
      return
    }
    setError('')
    setSearched(true)
    setPlaylist([])
    setLoading(true)
    try {
      const data = await getDoubleFeature(movie.id, mode)
      setPlaylist(data.playlist)
      setResultMode(data.mode)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <PageHeader
        icon="layers"
        title="Double Feature"
        subtitle="Pick a film. We'll find its perfect companion — either a mirror from another decade or a deliberate contrast."
      />

      <section className="tool-panel">
        <form onSubmit={onSubmit}>
          <div className="tool-grid tool-grid-narrow">
            <MoviePicker
              label="Reference film"
              selected={movie}
              onSelect={setMovie}
              placeholder="Start with a film you love…"
            />

            <div className="field">
              <label>Pairing mode</label>
              <Segmented
                options={MODES}
                value={mode}
                onChange={setMode}
                ariaLabel="Pairing mode"
              />
              <span className="helper-text">{MODE_COPY[mode]}</span>
            </div>
          </div>

          <div className="tool-row">
            <button className="btn btn-primary" type="submit" disabled={loading || !movie}>
              {loading ? 'Pairing…' : 'Build the double feature'}
            </button>
          </div>

          {error && !searched && <p className="form-error">{error}</p>}
        </form>
      </section>

      {searched && (
        <section className="section">
          <div className="section-head">
            <h2>Your double feature</h2>
            {!loading && !error && (
              <span className="results-count">
                {resultMode === 'mirror' ? 'Mirror mode' : 'Contrast mode'}
              </span>
            )}
          </div>
          {!loading && !error && playlist.length === 2 && (
            <p className="results-note">
              Watch <strong>{playlist[0].title}</strong> first, then{' '}
              <strong>{playlist[1].title}</strong>.
            </p>
          )}
          <MovieGrid
            movies={playlist}
            loading={loading}
            error={error}
            pair
            skeletonCount={2}
            emptyTitle="No companion found"
            emptyMessage="Try another reference film or switch the pairing mode."
          />
        </section>
      )}

      {!searched && (
        <section className="section intro-panel">
          <span className="empty-icon">
            <Icon name="layers" size={22} />
          </span>
          <h2>Two films, one night</h2>
          <p>
            Mirror mode finds a kindred spirit from another era. Contrast mode finds a
            film that shares DNA but flips the mood — perfect for a double bill with a
            twist.
          </p>
        </section>
      )}
    </>
  )
}
