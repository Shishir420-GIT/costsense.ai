import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Costs API
export const costsAPI = {
  getSummary: (days: number = 30, provider?: string) =>
    api.get(`/api/costs/summary`, { params: { days, provider } }),

  getByProvider: (days: number = 30) =>
    api.get(`/api/costs/by-provider`, { params: { days } }),

  getByResourceType: (days: number = 30, provider?: string, limit: number = 10) =>
    api.get(`/api/costs/by-resource-type`, { params: { days, provider, limit } }),

  getTrend: (days: number = 30, provider?: string) =>
    api.get(`/api/costs/trend`, { params: { days, provider } }),
}

// Investigations API
export const investigationsAPI = {
  list: (status?: string, limit: number = 50) =>
    api.get(`/api/investigations/`, { params: { status, limit } }),

  get: (id: number) =>
    api.get(`/api/investigations/${id}`),

  create: (data: any) =>
    api.post(`/api/investigations/`, data),

  updateStatus: (id: number, status: string) =>
    api.patch(`/api/investigations/${id}/status`, { new_status: status }),
}

// Tickets API
export const ticketsAPI = {
  list: (status?: string, limit: number = 50) =>
    api.get(`/api/tickets/`, { params: { status, limit } }),

  get: (id: number) =>
    api.get(`/api/tickets/${id}`),

  create: (data: any) =>
    api.post(`/api/tickets/`, data),

  approve: (id: number, approved: boolean, reason?: string) =>
    api.post(`/api/tickets/${id}/approve`, { approved, rejection_reason: reason }),
}

// Chat API
export const chatAPI = {
  send: (message: string, sessionId?: string, context?: any) =>
    api.post(`/api/chat/`, { message, session_id: sessionId, context }),

  getHistory: (sessionId: string) =>
    api.get(`/api/chat/history/${sessionId}`),

  clearHistory: (sessionId: string) =>
    api.delete(`/api/chat/history/${sessionId}`),
}

export default api
