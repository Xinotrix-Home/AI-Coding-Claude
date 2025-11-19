import { apiClient } from './client'

export interface Note {
  id: string
  user_id: string
  project_id?: string
  title: string
  content: string
  tags: string[]
  linked_tasks: string[]
  linked_notes: string[]
  current_version: number
  is_pinned: boolean
  is_archived: boolean
  created_at: string
  updated_at: string
  preview?: string
  word_count?: number
}

export interface NoteCreate {
  title: string
  content: string
  project_id?: string
  tags?: string[]
  linked_tasks?: string[]
  linked_notes?: string[]
}

export interface NoteUpdate {
  title?: string
  content?: string
  project_id?: string
  tags?: string[]
  linked_tasks?: string[]
  linked_notes?: string[]
  is_pinned?: boolean
  is_archived?: boolean
}

export interface NoteVersion {
  version: number
  content: string
  updated_at: string
  updated_by: string
}

export interface NoteSearchResult {
  id: string
  title: string
  content: string
  preview: string
  score: number
  highlights: string[]
  tags: string[]
  created_at: string
  updated_at: string
}

export interface NoteListResponse {
  items: Note[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface NoteSearchListResponse {
  items: NoteSearchResult[]
  total: number
  query: string
}

export const notesAPI = {
  create: async (data: NoteCreate): Promise<Note> => {
    return apiClient.post('/api/v1/notes', data)
  },

  getAll: async (params?: {
    project_id?: string
    tags?: string
    is_pinned?: boolean
    is_archived?: boolean
    page?: number
    page_size?: number
  }): Promise<NoteListResponse> => {
    return apiClient.get('/api/v1/notes', params)
  },

  search: async (query: string, page?: number, page_size?: number): Promise<NoteSearchListResponse> => {
    return apiClient.get('/api/v1/notes/search', { q: query, page, page_size })
  },

  getById: async (id: string): Promise<Note> => {
    return apiClient.get(`/api/v1/notes/${id}`)
  },

  update: async (id: string, data: NoteUpdate): Promise<Note> => {
    return apiClient.patch(`/api/v1/notes/${id}`, data)
  },

  delete: async (id: string): Promise<void> => {
    return apiClient.delete(`/api/v1/notes/${id}`)
  },

  getVersions: async (id: string): Promise<NoteVersion[]> => {
    return apiClient.get(`/api/v1/notes/${id}/versions`)
  },

  getLinks: async (id: string) => {
    return apiClient.get(`/api/v1/notes/${id}/links`)
  },

  renderMarkdown: async (id: string): Promise<{ html: string }> => {
    return apiClient.post(`/api/v1/notes/${id}/render`)
  },
}
