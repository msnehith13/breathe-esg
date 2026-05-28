import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Attach Basic Auth for dev — in production this would be token-based
const credentials = btoa('Snehith:Gnanvi01')
api.defaults.headers.common['Authorization'] = `Basic ${credentials}`

export default api