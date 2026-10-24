import { useState } from 'react'
import { getTimeBudget } from '../api'
import MovieGrid from '../components/MovieGrid'
import PageHeader from '../components/PageHeader'

function formatMinutes(minutes) {
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  return hours > 0 ? `${hours}h ${String(rest).padStart(2, '0')}m` : `${rest}m`
}

function addMinutes(clock, minutes) {
  const [hours, mins] = clock.split(':').map(Number)
  const total = hours * 60 + mins + Number(minutes)
  const hh = Math.floor((total % 1440) / 60)
  const mm = total % 60
  return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`
}

function nowClock() {
  const now = new Date()
  return `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
}

export default function TimeBudget() {
  const [minutes, setMinutes] = useState(120)
  const [startClock, setStartClock] = useState(nowClock())
  const [calmOnly, setCalmOnly] = useState(false)
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)

  const endsBy = addMinutes(startClock, minutes)

  const onSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSearched(true)
    setResults([])
    setLoading(true)
    try {
      const data = await getTimeBudget({
        minutes,
        startClock,
        calmOnly,
        topK: 12,
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
        icon="clock"
        title="Time-Budget & Bedtime"
        subtitle="Enter the minutes you have and when you're starting. We'll only suggest films that fit — and tell you exactly when they end."
      />

      <section className="tool-panel">
        <form onSubmit={onSubmit}>
          <div className="tool-grid">
            <div className="field">
              <label htmlFor="minutes">
                Time available — <strong>{formatMinutes(minutes)}</strong>
              </label>
              <input
                id="minutes"
                type="range"
                className="range"
                min="30"
                max="240"
                step="5"
                value={minutes}
                onChange={(event) => setMinutes(Number(event.target.value))}
              />
              <div className="range-scale">
                <span>30m</span>
                <span>2h</span>
                <span>4h</span>
              </div>
            </div>

            <div className="field">
              <label htmlFor="start-time">Start time</label>
              <input
                id="start-time"
                type="time"
                className="input"
                value={startClock}
                onChange={(event) => setStartClock(event.target.value)}
              />
            </div>
          </div>

          <label className="switch">
            <input
              type="checkbox"
              checked={calmOnly}
              onChange={(event) => setCalmOnly(event.target.checked)}
            />
            <span className="switch-track">
              <span className="switch-thumb" />
            </span>
            <span className="switch-text">Calm only — gentle films for late-night viewing</span>
          </label>

          <div className="tool-row">
            <button className="btn btn-primary" type="submit" disabled={loading || !startClock}>
              {loading ? 'Checking the clock…' : 'Find films that fit'}
            </button>
            <span className="helper-text">
              Starting at {startClock} · {formatMinutes(minutes)} available
            </span>
          </div>
        </form>
      </section>

      {searched && (
        <section className="section">
          <div className="section-head">
            <h2>Films that finish before {endsBy}</h2>
            {!loading && !error && <span className="results-count">{results.length} films</span>}
          </div>
          <MovieGrid
            movies={results}
            loading={loading}
            error={error}
            skeletonCount={8}
            emptyTitle="No films fit that window"
            emptyMessage="Try adding more time or switching off calm mode."
          />
        </section>
      )}
    </>
  )
}
