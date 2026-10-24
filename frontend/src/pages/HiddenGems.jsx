import { useEffect, useState } from 'react'
import { getHiddenGems } from '../api'
import Icon from '../components/Icon'
import MovieGrid from '../components/MovieGrid'
import PageHeader from '../components/PageHeader'

const GENRES = [
  'Action',
  'Adventure',
  'Animation',
  'Comedy',
  'Crime',
  'Documentary',
  'Drama',
  'Family',
  'Fantasy',
  'History',
  'Horror',
  'Music',
  'Mystery',
  'Romance',
  'Science Fiction',
  'TV Movie',
  'Thriller',
  'War',
  'Western',
]

export default function HiddenGems() {
  const [genre, setGenre] = useState('')
  const [yearMin, setYearMin] = useState('')
  const [yearMax, setYearMax] = useState('')
  const [topK, setTopK] = useState('20')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [formError, setFormError] = useState('')

  useEffect(() => {
    let active = true
    getHiddenGems({ topK: 20 })
      .then((data) => {
        if (active) setResults(data.results)
      })
      .catch((err) => {
        if (active) setError(err.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })
    return () => {
      active = false
    }
  }, [])

  const onSubmit = async (event) => {
    event.preventDefault()
    if (yearMin && yearMax && Number(yearMin) > Number(yearMax)) {
      setFormError('Minimum year cannot be greater than maximum year.')
      return
    }
    setFormError('')
    setLoading(true)
    setError('')
    try {
      const data = await getHiddenGems({
        genre: genre || null,
        yearMin: yearMin ? Number(yearMin) : null,
        yearMax: yearMax ? Number(yearMax) : null,
        topK: Number(topK),
      })
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
        icon="gem"
        title="Hidden Gems"
        subtitle="A high rating with a low vote count usually means one thing: an audience found it, but the world hasn't yet."
      />

      <section className="tool-panel">
        <form onSubmit={onSubmit}>
          <div className="tool-grid tool-grid-4">
            <div className="field">
              <label htmlFor="gem-genre">Genre</label>
              <select
                id="gem-genre"
                className="select"
                value={genre}
                onChange={(event) => setGenre(event.target.value)}
              >
                <option value="">Any genre</option>
                {GENRES.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
            </div>

            <div className="field">
              <label htmlFor="year-min">From year</label>
              <input
                id="year-min"
                type="number"
                className="input"
                min="1920"
                max="2030"
                placeholder="1920"
                value={yearMin}
                onChange={(event) => setYearMin(event.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="year-max">To year</label>
              <input
                id="year-max"
                type="number"
                className="input"
                min="1920"
                max="2030"
                placeholder="2023"
                value={yearMax}
                onChange={(event) => setYearMax(event.target.value)}
              />
            </div>

            <div className="field">
              <label htmlFor="gem-count">Show</label>
              <select
                id="gem-count"
                className="select"
                value={topK}
                onChange={(event) => setTopK(event.target.value)}
              >
                <option value="12">12 gems</option>
                <option value="20">20 gems</option>
                <option value="30">30 gems</option>
                <option value="50">50 gems</option>
              </select>
            </div>
          </div>

          <div className="tool-row">
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? 'Digging…' : 'Apply filters'}
            </button>
            <span className="helper-text">
              Ranked by gem score — high rating, low popularity.
            </span>
          </div>

          {formError && <p className="form-error">{formError}</p>}
        </form>
      </section>

      <section className="section">
        <div className="section-head">
          <h2>Overlooked films worth your night</h2>
          {!loading && !error && <span className="results-count">{results.length} gems</span>}
        </div>
        <MovieGrid
          movies={results}
          loading={loading}
          error={error}
          skeletonCount={8}
          emptyTitle="No gems match those filters"
          emptyMessage="Try a wider year range or a different genre."
        />
      </section>

      <div className="stub-footnote">
        <Icon name="gem" size={14} />
        Gem score rewards strong ratings from audiences, not marketing budgets.
      </div>
    </>
  )
}
