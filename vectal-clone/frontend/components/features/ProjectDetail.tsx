'use client'

import { useQuery } from '@tanstack/react-query'
import { projectsAPI, Project } from '@/lib/api/projects'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Users, BarChart3 } from 'lucide-react'
import { TaskList } from './TaskList'

interface ProjectDetailProps {
  projectId: string
  onBack: () => void
}

export function ProjectDetail({ projectId, onBack }: ProjectDetailProps) {
  const { data: project, isLoading } = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => projectsAPI.getById(projectId)
  })

  const { data: progress } = useQuery({
    queryKey: ['project-progress', projectId],
    queryFn: () => projectsAPI.getProgress(projectId)
  })

  const { data: tasks } = useQuery({
    queryKey: ['project-tasks', projectId],
    queryFn: () => projectsAPI.getTasks(projectId)
  })

  if (isLoading) {
    return <div className="text-center py-8">Loading project...</div>
  }

  if (!project) {
    return <div className="text-center py-8">Project not found</div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-4">
          <Button variant="ghost" size="sm" onClick={onBack}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          
          <div>
            <div className="flex items-center gap-2 mb-2">
              {project.color && (
                <div
                  className="w-6 h-6 rounded"
                  style={{ backgroundColor: project.color }}
                />
              )}
              <h1 className="text-3xl font-bold">{project.name}</h1>
            </div>
            
            {project.description && (
              <p className="text-muted-foreground">{project.description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Stats */}
      {progress && (
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-lg border p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Total Tasks</span>
            </div>
            <div className="text-2xl font-bold">{progress.total_tasks}</div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-4 w-4 text-green-500" />
              <span className="text-sm text-muted-foreground">Completed</span>
            </div>
            <div className="text-2xl font-bold text-green-500">{progress.completed_tasks}</div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-4 w-4 text-blue-500" />
              <span className="text-sm text-muted-foreground">In Progress</span>
            </div>
            <div className="text-2xl font-bold text-blue-500">{progress.in_progress_tasks}</div>
          </div>

          <div className="rounded-lg border p-4">
            <div className="flex items-center gap-2 mb-2">
              <BarChart3 className="h-4 w-4 text-red-500" />
              <span className="text-sm text-muted-foreground">Overdue</span>
            </div>
            <div className="text-2xl font-bold text-red-500">{progress.overdue_tasks}</div>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {progress && (
        <div className="rounded-lg border p-4">
          <div className="flex justify-between mb-2">
            <span className="text-sm font-medium">Project Progress</span>
            <span className="text-sm font-medium">{Math.round(progress.progress_percentage)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div
              className="bg-blue-500 h-3 rounded-full transition-all"
              style={{ width: `${progress.progress_percentage}%` }}
            />
          </div>
        </div>
      )}

      {/* Collaborators */}
      {project.collaborators && project.collaborators.length > 0 && (
        <div className="rounded-lg border p-4">
          <div className="flex items-center gap-2 mb-3">
            <Users className="h-4 w-4" />
            <h3 className="font-semibold">Collaborators</h3>
          </div>
          <div className="space-y-2">
            {project.collaborators.map((collaborator) => (
              <div key={collaborator.user_id} className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{collaborator.user_email || 'Unknown'}</div>
                  <div className="text-sm text-muted-foreground capitalize">{collaborator.role}</div>
                </div>
                <div className={`text-xs px-2 py-1 rounded ${
                  collaborator.status === 'accepted' ? 'bg-green-100 text-green-700' :
                  collaborator.status === 'pending' ? 'bg-yellow-100 text-yellow-700' :
                  'bg-gray-100 text-gray-700'
                }`}>
                  {collaborator.status}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tasks */}
      <div className="rounded-lg border p-4">
        <h3 className="font-semibold mb-4">Tasks</h3>
        {tasks && tasks.items.length > 0 ? (
          <div className="space-y-2">
            {tasks.items.map((task: any) => (
              <div key={task.id} className="flex items-center gap-3 p-3 rounded hover:bg-accent/50">
                <input
                  type="checkbox"
                  checked={task.status === 'completed'}
                  readOnly
                  className="h-4 w-4"
                />
                <div className="flex-1">
                  <div className={task.status === 'completed' ? 'line-through text-muted-foreground' : ''}>
                    {task.title}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No tasks in this project yet
          </div>
        )}
      </div>
    </div>
  )
}
