'use client'

import { useState } from 'react'
import { ProjectList } from '@/components/features/ProjectList'
import { CreateProjectModal } from '@/components/features/CreateProjectModal'
import { ProjectDetail } from '@/components/features/ProjectDetail'
import { Project } from '@/lib/api/projects'

export default function ProjectsPage() {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)

  if (selectedProject) {
    return (
      <div className="container mx-auto py-8">
        <ProjectDetail
          projectId={selectedProject.id}
          onBack={() => setSelectedProject(null)}
        />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Projects</h1>
        <p className="text-muted-foreground">Organize your tasks into projects</p>
      </div>

      <ProjectList
        onSelectProject={setSelectedProject}
        onCreateProject={() => setIsCreateModalOpen(true)}
      />

      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  )
}
