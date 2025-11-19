'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsAPI, Project } from '@/lib/api/projects'
import { Button } from '@/components/ui/button'
import { Plus, Archive, Trash2, FolderOpen } from 'lucide-react'

interface ProjectListProps {
  onSelectProject?: (project: Project) => void
  onCreateProject?: () => void
}

export function ProjectList({ onSelectProject, onCreateProject }: ProjectListProps) {
  const queryClient = useQueryClient()
  const [includeArchived, setIncludeArchived] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['projects', includeArchived],
    queryFn: () => projectsAPI.getAll({ include_archived: includeArchived })
  })

  const archiveMutation = useMutation({
    mutationFn: (id: string) => projectsAPI.archive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    }
  })

  const unarchiveMutation = useMutation({
    mutationFn: (id: string) => projectsAPI.unarchive(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    }
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => projectsAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    }
  })

  const getProgressColor = (percentage: number) => {
    if (percentage >= 75) return 'bg-green-500'
    if (percentage >= 50) return 'bg-blue-500'
    if (percentage >= 25) return 'bg-yellow-500'
    return 'bg-gray-300'
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading projects...</div>
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div className="flex gap-2">
          <Button
            variant={!includeArchived ? 'default' : 'outline'}
            onClick={() => setIncludeArchived(false)}
            size="sm"
          >
            Active
          </Button>
          <Button
            variant={includeArchived ? 'default' : 'outline'}
            onClick={() => setIncludeArchived(true)}
            size="sm"
          >
            Archived
          </Button>
        </div>
        
        {onCreateProject && (
          <Button onClick={onCreateProject} size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Project
          </Button>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {data?.items.length === 0 ? (
          <div className="col-span-full text-center py-12 text-muted-foreground">
            <FolderOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No projects found</p>
            {onCreateProject && (
              <Button onClick={onCreateProject} variant="outline" className="mt-4">
                Create your first project
              </Button>
            )}
          </div>
        ) : (
          data?.items.map((project) => (
            <div
              key={project.id}
              className="rounded-lg border p-4 hover:bg-accent/50 transition-colors cursor-pointer"
              onClick={() => onSelectProject?.(project)}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  {project.color && (
                    <div
                      className="w-4 h-4 rounded"
                      style={{ backgroundColor: project.color }}
                    />
                  )}
                  <h3 className="font-semibold">{project.name}</h3>
                </div>
                
                <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                  {project.is_archived ? (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => unarchiveMutation.mutate(project.id)}
                      title="Unarchive"
                    >
                      <Archive className="h-4 w-4" />
                    </Button>
                  ) : (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => archiveMutation.mutate(project.id)}
                      title="Archive"
                    >
                      <Archive className="h-4 w-4" />
                    </Button>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (confirm('Are you sure you want to delete this project?')) {
                        deleteMutation.mutate(project.id)
                      }
                    }}
                    className="text-destructive hover:text-destructive"
                    title="Delete"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {project.description && (
                <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                  {project.description}
                </p>
              )}

              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Progress</span>
                  <span className="font-medium">
                    {project.completed_task_count || 0} / {project.task_count || 0} tasks
                  </span>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getProgressColor(project.progress_percentage || 0)}`}
                    style={{ width: `${project.progress_percentage || 0}%` }}
                  />
                </div>
                
                <div className="text-xs text-muted-foreground">
                  {Math.round(project.progress_percentage || 0)}% complete
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
