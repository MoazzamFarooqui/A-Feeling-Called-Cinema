import { useEffect, useRef, useState } from 'react'
import { searchTitles } from '../api'
import Icon from './Icon'

const NO_EXCLUDES = []

export default function MoviePicker({
  label,
  placeholder = 'Search movie titles…',
  selected,
  onSelect,
  excludeIds = NO_EXCLUDES,
  disabled = false,
}) {
  const [query, setQuery] = useState('')
  const [options, setOptions] = useState([])
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [highlight, setHighlight] = useState(0)
  const [error, setError] = useState('')
  const containerRef = useRef(null)
  const results = options.filter((movie) => !excludeIds.includes(movie.id))
  const activeIndex = Math.min(highlight, Math.max(results.length - 1, 0))

  useEffect(() => {
    if (selected) return undefined

    const q = query.trim()
    if (q.length < 2) return undefined

    let active = true
    const timer = setTimeout(() => {
      searchTitles(q, 8)
        .then((data) => {
          if (!active) return
          setOptions(data.results)
          setHighlight(0)
          setError('')
        })
        .catch((err) => {
          if (!active) return
          setOptions([])
          setError(err.message)
        })
        .finally(() => {
          if (active) setLoading(false)
        })
    }, 250)

    return () => {
      active = false
      clearTimeout(timer)
    }
  }, [query, selected])

  useEffect(() => {
    const onMouseDown = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', onMouseDown)
    return () => document.removeEventListener('mousedown', onMouseDown)
  }, [])

  const choose = (movie) => {
    onSelect(movie)
    setQuery('')
    setOptions([])
    setError('')
    setOpen(false)
  }

  const handleQueryChange = (event) => {
    const value = event.target.value
    setQuery(value)
    if (value.trim().length < 2) {
      setOptions([])
      setLoading(false)
      setError('')
      setOpen(false)
    } else {
      setLoading(true)
      setOpen(true)
    }
  }

  const onKeyDown = (event) => {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setHighlight((current) => Math.min(current + 1, Math.max(results.length - 1, 0)))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setHighlight((current) => Math.max(current - 1, 0))
    } else if (event.key === 'Enter') {
      if (open && results[activeIndex]) {
        event.preventDefault()
        choose(results[activeIndex])
      }
    } else if (event.key === 'Escape') {
      setOpen(false)
    }
  }

  return (
    <div className="movie-picker" ref={containerRef}>
      {label && <span className="picker-label">{label}</span>}

      {selected ? (
        <div className="picker-selected">
          <span className="picker-value">
            <Icon name="film" size={15} />
            {selected.title}
            <em>({selected.year})</em>
          </span>
          <button
            type="button"
            className="icon-btn"
            onClick={() => onSelect(null)}
            aria-label={`Remove ${selected.title}`}
            disabled={disabled}
          >
            <Icon name="close" size={15} />
          </button>
        </div>
      ) : (
        <div className="picker-input-wrap">
          <Icon name="search" size={16} className="picker-search-icon" />
          <input
            className="input picker-input"
            value={query}
            onChange={handleQueryChange}
            onFocus={() => {
              if (results.length || query.trim().length >= 2) setOpen(true)
            }}
            onKeyDown={onKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            aria-label={label || placeholder}
            autoComplete="off"
          />
          {open && (
            <ul className="picker-options" role="listbox">
              {loading && <li className="picker-empty">Searching…</li>}
              {!loading && error && <li className="picker-empty">{error}</li>}
              {!loading && !error && results.length === 0 && (
                <li className="picker-empty">No titles found</li>
              )}
              {!loading &&
                results.map((movie, index) => (
                  <li key={movie.id}>
                    <button
                      type="button"
                      className={`picker-option${index === activeIndex ? ' active' : ''}`}
                      onClick={() => choose(movie)}
                      onMouseEnter={() => setHighlight(index)}
                    >
                      <span>{movie.title}</span>
                      <span className="picker-year">{movie.year}</span>
                    </button>
                  </li>
                ))}
            </ul>
          )}
        </div>
      )}
    </div>
  )
}
