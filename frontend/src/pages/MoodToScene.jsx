import { useState } from 'react'
import { searchMood } from '../api'
import Icon from '../components/Icon'
import MovieGrid from '../components/MovieGrid'
import PageHeader from '../components/PageHeader'

const EXAMPLES = [
  'claustrophobic submarine thriller',
  'feel-good road trip comedy',
  'slow emotional family drama',
  'rainy night in Tokyo',
  'heist gone wrong',
  'summer camp nostalgia',
]

export default function MoodToScene() {
  const [query, setQuery] = useState('')
  const [submitted, setSubmitted] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const runSearch = (text) => {
    const value = (text ?? query).trim()
    if (!value) return
    setSubmitted(value)
    setSearched(true)
    setResults([])
    setError('')
    setLoading(true)
    searchMood(value, 18)
      .then((data) => setResults(data.results))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  const onSubmit = (event) => {
    event.preventDefault()
    runSearch()
  }

  return (
    <>
      <PageHeader
        icon="sparkles"
        title="Mood to Scene"
        subtitle="Describe a feeling, a scene, or a film you love — we translate it into a vector and find the closest matches in the catalog."
      />

      <section className="tool-panel">
        <form onSubmit={onSubmit}>
          <div className="mood-search">
            <Icon name="search" size={19} />
            <input
              className="mood-input"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder='Try "lonely neon-lit city at night"…'
              aria-label="Describe the mood"
            />
            <button className="btn btn-primary" type="submit" disabled={loading || !query.trim()}>
              {loading ? 'Searching…' : 'Find films'}
            </button>
          </div>
          <div className="example-row">
            <span className="example-label">Try:</span>
            {EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                className="chip-button"
                onClick={() => {
                  setQuery(example)
                  runSearch(example)
                }}
              >
                {example}
              </button>
            ))}
          </div>
        </form>
      </section>

      {searched ? (
        <section className="section">
          <div className="section-head">
            <h2>Results for “{submitted}”</h2>
            {!loading && !error && <span className="results-count">{results.length} films</span>}
          </div>
          <MovieGrid
            movies={results}
            loading={loading}
            error={error}
            skeletonCount={9}
            emptyTitle="No films match that mood"
            emptyMessage="Try describing it with different words — a setting, a feeling, or a film you already love."
          />
        </section>
      ) : (
        <section className="section intro-panel">
          <span className="empty-icon">
            <Icon name="sparkles" size={22} />
          </span>
          <h2>Not sure what to type?</h2>
          <p>
            The search understands atmosphere, setting, and emotion — not just titles.
            Try a scene (“a heist that goes wrong”), a feeling (“quiet grief by the sea”),
            or a reference (“like Blade Runner, but warmer”).
          </p>
        </section>
      )}
    </>
  )
}
