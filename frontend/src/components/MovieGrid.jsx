import { useState } from 'react'
import EmptyState from './EmptyState'
import MovieCard from './MovieCard'
import MovieModal from './MovieModal'
import SkeletonCard from './SkeletonCard'

export default function MovieGrid({
  movies = [],
  loading = false,
  error = '',
  skeletonCount = 6,
  emptyTitle = 'No movies found',
  emptyMessage = 'Try relaxing your filters.',
  pair = false,
}) {
  const [selected, setSelected] = useState(null)
  const gridClass = pair ? 'movie-grid movie-grid-pair' : 'movie-grid'

  if (error) {
    return <EmptyState icon="film" title="Something went wrong" message={error} />
  }

  if (loading) {
    return (
      <div className={gridClass}>
        {Array.from({ length: skeletonCount }, (_, index) => (
          <SkeletonCard key={index} />
        ))}
      </div>
    )
  }

  if (movies.length === 0) {
    return <EmptyState icon="search" title={emptyTitle} message={emptyMessage} />
  }

  return (
    <>
      <div className={gridClass}>
        {movies.map((movie) => (
          <MovieCard key={movie.id} movie={movie} onOpen={() => setSelected(movie)} />
        ))}
      </div>
      {selected && <MovieModal movie={selected} onClose={() => setSelected(null)} />}
    </>
  )
}
