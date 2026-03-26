/**
 * ProteinHub API Client
 * 封装后端API调用
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

class ApiClient {
  constructor() {
    this.baseUrl = API_BASE_URL
    this.userId = localStorage.getItem('user_id') || '1'
  }

  async request(url, options = {}) {
    const fullUrl = `${this.baseUrl}${url}`
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        'X-User-Id': this.userId,
        ...options.headers
      }
    }

    const response = await fetch(fullUrl, { ...defaultOptions, ...options })
    const data = await response.json()
    
    if (!data.success) {
      throw new Error(data.error || 'Request failed')
    }
    
    return data
  }

  // 笔记相关API
  async getFeed(params = {}) {
    const query = new URLSearchParams({
      page: params.page || 1,
      per_page: params.per_page || 10,
      sort: params.sort || 'popular'
    })
    return this.request(`/api/notes/feed?${query}`)
  }

  async getNoteDetail(noteId) {
    return this.request(`/api/notes/${noteId}`)
  }

  async likeNote(noteId) {
    return this.request(`/api/notes/${noteId}/like`, { method: 'POST' })
  }

  async favoriteNote(noteId) {
    return this.request(`/api/notes/${noteId}/favorite`, { method: 'POST' })
  }

  async getComments(noteId, params = {}) {
    const query = new URLSearchParams({
      page: params.page || 1,
      per_page: params.per_page || 20
    })
    return this.request(`/api/notes/${noteId}/comments?${query}`)
  }

  async createComment(noteId, content) {
    return this.request(`/api/notes/${noteId}/comments`, {
      method: 'POST',
      body: JSON.stringify({ content })
    })
  }
}

export const api = new ApiClient()
export default api
