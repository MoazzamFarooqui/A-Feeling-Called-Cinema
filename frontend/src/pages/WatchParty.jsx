import { useState } from 'react'
import { getWatchParty } from '../api'
import Icon from '../components/Icon'
import MovieGrid from '../components/MovieGrid'
import MoviePicker from '../components/MoviePicker'
import PageHeader from '../components/PageHeader'

const MAX_PEOPLE = 5

export default function WatchParty() {
  const [slots, setSlots] = useState([null, null])
  const [maxRuntime, setMaxRuntime] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searched, setSearched] = useState(false)
  const [searchedPicks, setSearchedPicks] = useState([])

  const picks = slots.filter(Boolean)

  const setSlot = (index, movie) => {
    setSlots((current) => current.map((slot, slotIndex) => (slotIndex === index ? movie : slot)))
  }

  const addSlot = () => {
    setSlots((current) => (current.length < MAX_PEOPLE ? [...current, null] : current))
  }

  const removeSlot = (index) => {
    setSlots((current) => (current.length > 1 ? current.filter((_, i) => i !== index) : current))
  }

  const onSubmit = async (event) => {
    event.preventDefault()
    if (!picks.length) {
      setError('Add at least one favorite movie to get started.')
      return
    }
    setError('')
    setSearched(true)
    setResults([])
    setLoading(true)
    setSearchedPicks(picks)
    try {
      const data = await getWatchParty(picks.map((movie) => movie.id), {
        top_k: 12,
        max_runtime: maxRuntime ? Number(maxRuntime) : undefined,
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
        icon="users"
        title="Watch Party"
        subtitle="Add up to five favorites from everyone in the room. We blend them into one taste profile and surface the best compromise."
      />

      <section className="tool-panel">
        <form onSubmit={onSubmit}>
          <div className="party-grid">
            {slots.map((movie, index) => (
              <div className="party-slot" key={index}>
                <MoviePicker
                  label={`Person ${index + 1}`}
                  selected={movie}
                  onSelect={(selection) => setSlot(index, selection)}
                  excludeIds={picks.filter((pick) => pick.id !== movie?.id).map((pick) => pick.id)}
                  placeholder="Their favorite film…"
                />
                {slots.length > 1 && (
                  <button
                    type="button"
                    className="slot-remove"
                    onClick={() => removeSlot(index)}
                    aria-label={`Remove person ${index + 1}`}
                  >
                    <Icon name="close" size={13} />
                    Remove
                  </button>
                )}
              </div>
            ))}
          </div>

          <div className="tool-row">
            <div className="field field-inline">
              <label htmlFor="party-runtime">Max runtime</label>
              <select
                id="party-runtime"
                className="select"
                value={maxRuntime}
                onChange={(event) => setMaxRuntime(event.target.value)}
              >
                <option value="">Any length</option>
                <option value="90">Under 1h 30m</option>
                <option value="120">Under 2h</option>
                <option value="150">Under 2h 30m</option>
              </select>
            </div>

            <button
              type="button"
              className="btn btn-ghost"
              onClick={addSlot}
              disabled={slots.length >= MAX_PEOPLE}
            >
              <Icon name="plus" size={15} />
              Add person
            </button>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !picks.length}
            >
              {loading ? 'Finding…' : 'Find the compromise'}
            </button>
          </div>

          {error && !searched && <p className="form-error">{error}</p>}
        </form>
      </section>

      {searched && (
        <section className="section">
          <div className="section-head">
            <h2>Shared picks</h2>
            {!loading && !error && (
              <span className="results-count">{results.length} films</span>
            )}
          </div>
          {searchedPicks.length > 0 && (
            <p className="results-note">
              Blending {searchedPicks.map((movie) => movie.title).join(' · ')}
            </p>
          )}
          <MovieGrid
            movies={results}
            loading={loading}
            error={error}
            skeletonCount={8}
            emptyTitle="No common ground found"
            emptyMessage="Try removing the runtime filter or adding a different favorite."
          />
        </section>
      )}
    </>
  )
}
