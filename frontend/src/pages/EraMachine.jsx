import { useState } from 'react'
import { getEraMachine } from '../api'
import Icon from '../components/Icon'
import MovieGrid from '../components/MovieGrid'
import MoviePicker from '../components/MoviePicker'
import PageHeader from '../components/PageHeader'

const DECADES = [1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]

export default function EraMachine() {
  const [movie, setMovie] = useState(null)
  const [decade, setDecade] = useState(1980)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)
  const [searchedDecade, setSearchedDecade] = useState(1980)

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
    setSearchedDecade(decade)
    try {
      const data = await getEraMachine(movie.id, decade, 12)
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
        icon="hourglass"
        title="Era Time Machine"
        subtitle="Choose a decade and a favorite film. We'll find the closest cinematic match from that era."
      />

      <section className="tool-panel">
        <form onSubmit={onSubmit}>
          <div className="tool-grid">
            <MoviePicker
              label="Reference film"
              selected={movie}
              onSelect={setMovie}
              placeholder="A film you love…"
            />

            <div className="field">
              <label htmlFor="decade">Travel to</label>
              <select
                id="decade"
                className="select"
                value={decade}
                onChange={(event) => setDecade(Number(event.target.value))}
              >
                {DECADES.map((value) => (
                  <option key={value} value={value}>
                    {value}s
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="tool-row">
            <button className="btn btn-primary" type="submit" disabled={loading || !movie}>
              {loading ? 'Travelling…' : 'Find the era match'}
            </button>
          </div>

          {error && !searched && <p className="form-error">{error}</p>}
        </form>
      </section>

      {searched && (
        <section className="section">
          <div className="section-head">
            <h2>Closest matches from the {searchedDecade}s</h2>
            {!loading && !error && <span className="results-count">{results.length} films</span>}
          </div>
          <MovieGrid
            movies={results}
            loading={loading}
            error={error}
            skeletonCount={8}
            emptyTitle="No matches in that decade"
            emptyMessage="Try another decade or a different reference film."
          />
        </section>
      )}

      {!searched && (
        <section className="section intro-panel">
          <span className="empty-icon">
            <Icon name="hourglass" size={22} />
          </span>
          <h2>Same taste, another time</h2>
          <p>
            Pick a film you love and a decade to visit. We'll find the films from that era
            that share its themes and atmosphere — a shortcut to the best of every decade.
          </p>
        </section>
      )}
    </>
  )
}
