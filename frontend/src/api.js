import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  timeout: 30000,
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail
    let message = 'Something went wrong. Please try again.'
    if (typeof detail === 'string' && detail) {
      message = detail
    } else if (Array.isArray(detail) && detail.length) {
      message = detail.map((item) => item.msg).join(', ')
    } else if (error.code === 'ECONNABORTED') {
      message = 'The request took too long. Please try again.'
    } else if (!error.response) {
      message = 'Cannot reach the API. Is the backend running?'
    }
    return Promise.reject(new Error(message))
  },
)

const get = (url, config) => api.get(url, config).then((response) => response.data)
const post = (url, body) => api.post(url, body).then((response) => response.data)

export const searchMood = (query, topK = 12) =>
  post('/api/search', { query, top_k: topK })

export const getWatchParty = (movieIds, options = {}) =>
  post('/api/watch-party', { movie_ids: movieIds, ...options })

export const getTimeBudget = ({ minutes, startClock = null, calmOnly = false, topK = 12 }) =>
  post('/api/time-budget', {
    minutes,
    start_clock: startClock,
    calm_only: calmOnly,
    top_k: topK,
  })

export const getDoubleFeature = (movieId, mode = 'mirror') =>
  get(`/api/double-feature/${movieId}`, { params: { mode } })

export const getCulturalBridge = (movieId, topK = 10) =>
  get(`/api/cultural-bridge/${movieId}`, { params: { top_k: topK } })

export const getEraMachine = (movieId, decade, topK = 10) =>
  get(`/api/era-machine/${movieId}`, { params: { decade, top_k: topK } })

export const getHiddenGems = ({ genre = null, yearMin = null, yearMax = null, topK = 20 } = {}) =>
  get('/api/hidden-gems', {
    params: {
      genre: genre || undefined,
      year_min: yearMin ?? undefined,
      year_max: yearMax ?? undefined,
      top_k: topK,
    },
  })

export const searchTitles = (q, limit = 8) =>
  get('/api/titles', { params: { q, limit } })

export const getMovie = (movieId) => get(`/api/movies/${movieId}`)

export default api
