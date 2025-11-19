import { apiClient } from './client'

export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  color?: string
  parent_project_id?: string
  is_archived: boolean
  created_at: string
  updated_at: string
  task_count?: number
  completed_task_count?: number
  progress_percentage?: number
}

export interface ProjectCreate {
  name: string
  description?: string
  color?: string
  parent_project_id?: string
}

export interface ProjectUpdate {
  name?: string
  description?: string
  color?: string
  parent_project_id?: string
  is_archived?: boolean
}

export interface ProjectProgress {
  project_id: string
  total_tasks: number
  completed_tasks: number
  in_progress_tasks: number
  pending_tasks: number
  progress_percentage: number
  overdue_tasks: number
}

export interface Collaborator {
  project_id: string
  user_id: string
  role: 'owner' | 'editor' | 'viewer'
  status: 'pending' | 'accepted' | 'declined'
  invited_by?: string
  created_at: string
  updated_at: string
  user_email?: string
  user_name?: string
}

export interface CollaboratorCreate {
  user_email: string
  role: 'owner' | 'editor' | 'viewer'
}

export interface CollaboratorUpdate {
  role: 'owner' | 'editor' | 'viewer'
}

export interface ProjectListResponse {
  items: Project[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ProjectWithCollaborators extends Project {
  collaborators: Collaborator[]
}

export const projectsAPI = {
  create: async (data: ProjectCreate): Promise<Project> => {
    return apiClient.post('/api/v1/projects', data)
  },

  getAll: async (params?: {
    include_archived?: boolean
    parent_project_id?: string
    page?: number
    page_size?: number
  }): Promise<ProjectListResponse> => {
    return apiClient.get('/api/v1/projects', params)
  },

  getById: async (id: string): Promise<ProjectWithCollaborators> => {
    return apiClient.get(`/api/v1/projects/${id}`)
  },

  update: async (id: string, data: ProjectUpdate): Promise<Project> => {
    return apiClient.patch(`/api/v1/projects/${id}`, data)
  },

  delete: async (id: string): Promise<void> => {
    return apiClient.delete(`/api/v1/projects/${id}`)
  },

  archive: async (id: string): Promise<Project> => {
    return apiClient.post(`/api/v1/projects/${id}/archive`)
  },

  unarchive: async (id: string): Promise<Project> => {
    return apiClient.post(`/api/v1/projects/${id}/unarchive`)
  },

  getProgress: async (id: string): Promise<ProjectProgress> => {
    return apiClient.get(`/api/v1/projects/${id}/progress`)
  },

  getTasks: async (id: string) => {
    return apiClient.get(`/api/v1/projects/${id}/tasks`)
  },

  getChildren: async (id: string): Promise<ProjectListResponse> => {
    return apiClient.get(`/api/v1/projects/${id}/children`)
  },

  // Collaborator methods
  addCollaborator: async (id: string, data: CollaboratorCreate): Promise<Collaborator> => {
    return apiClient.post(`/api/v1/projects/${id}/share`, data)
  },

  getCollaborators: async (id: string): Promise<Collaborator[]> => {
    return apiClient.get(`/api/v1/projects/${id}/collaborators`)
  },

  updateCollaborator: async (
    projectId: string,
    collaboratorId: string,
    data: CollaboratorUpdate
  ): Promise<Collaborator> => {
    return apiClient.patch(`/api/v1/projects/${projectId}/collaborators/${collaboratorId}`, data)
  },

  removeCollaborator: async (projectId: string, collaboratorId: string): Promise<void> => {
    return apiClient.delete(`/api/v1/projects/${projectId}/collaborators/${collaboratorId}`)
  },
}
