import axios from 'axios'

const isProduction = !window.location.hostname.includes('localhost')

const api = axios.create({
  baseURL: isProduction ? '/api' : '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

const credentials = btoa('Snehith:Gnanvi01')
api.defaults.headers.common['Authorization'] = `Basic ${credentials}`

export default api