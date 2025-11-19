'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { notesAPI, Note } from '@/lib/api/notes'
import { Button } from '@/components/ui/button'
import { Plus, Pin, Archive, Trash2, FileText, Grid, List } from 'lucide-react'

interface NoteListProps {
  onSelectNote?: (note: Note) => void
  onCreateNote?: () => void
}

export function NoteList({ onSelectNote, onCreateNote }: NoteListProps) {
  const queryClient = useQueryClient()
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid')
  const [includeArchived, setIncludeArchived] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['notes', includeArchived],
    queryFn: () => notesAPI.getAll({ is_archived: includeArchived })
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => notesAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] })
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: any }) => notesAPI.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] })
    }
  })

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading notes...</div>
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

        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setViewMode('grid')}
          >
            <Grid className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4" />
          </Button>
          
          {onCreateNote && (
            <Button onClick={onCreateNote} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              New Note
            </Button>
          )}
        </div>
      </div>

      {data?.items.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">
          <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
          <p>No notes found</p>
          {onCreateNote && (
            <Button onClick={onCreateNote} variant="outline" className="mt-4">
              Create your first note
            </Button>
          )}
        </div>
      ) : (
        <div className={viewMode === 'grid' ? 'grid gap-4 md:grid-cols-2 lg:grid-cols-3' : 'space-y-2'}>
          {data?.items.map((note) => (
            <div
              key={note.id}
              className={`rounded-lg border p-4 hover:bg-accent/50 transition-colors cursor-pointer ${
                viewMode === 'list' ? 'flex items-start gap-4' : ''
              }`}
              onClick={() => onSelectNote?.(note)}
            >
              <div className="flex-1">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {note.is_pinned && <Pin className="h-4 w-4 text-yellow-500" />}
                    <h3 className="font-semibold line-clamp-1">{note.title}</h3>
                  </div>
                  
                  <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => updateMutation.mutate({
                        id: note.id,
                        data: { is_pinned: !note.is_pinned }
                      })}
                      title={note.is_pinned ? 'Unpin' : 'Pin'}
                    >
                      <Pin className={`h-4 w-4 ${note.is_pinned ? 'fill-current' : ''}`} />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => updateMutation.mutate({
                        id: note.id,
                        data: { is_archived: !note.is_archived }
                      })}
                      title={note.is_archived ? 'Unarchive' : 'Archive'}
                    >
                      <Archive className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        if (confirm('Are you sure you want to delete this note?')) {
                          deleteMutation.mutate(note.id)
                        }
                      }}
                      className="text-destructive hover:text-destructive"
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                {note.preview && (
                  <p className="text-sm text-muted-foreground mb-3 line-clamp-3">
                    {note.preview}
                  </p>
                )}

                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <div className="flex gap-2">
                    {note.tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="px-2 py-0.5 bg-secondary rounded-full">
                        {tag}
                      </span>
                    ))}
                    {note.tags.length > 3 && (
                      <span className="px-2 py-0.5 bg-secondary rounded-full">
                        +{note.tags.length - 3}
                      </span>
                    )}
                  </div>
                  <span>{formatDate(note.updated_at)}</span>
                </div>

                {note.word_count && (
                  <div className="text-xs text-muted-foreground mt-2">
                    {note.word_count} words
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
