'use client'

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack:react-query'
import { notesAPI, Note } from '@/lib/api/notes'
import { Button } from '@/components/ui/button'
import { Save, X } from 'lucide-react'

interface NoteEditorProps {
  note?: Note
  onClose: () => void
}

export function NoteEditor({ note, onClose }: NoteEditorProps) {
  const queryClient = useQueryClient()
  const [title, setTitle] = useState(note?.title || '')
  const [content, setContent] = useState(note?.content || '')
  const [tags, setTags] = useState(note?.tags.join(', ') || '')

  const saveMutation = useMutation({
    mutationFn: async () => {
      const data = {
        title,
        content,
        tags: tags.split(',').map(t => t.trim()).filter(Boolean)
      }
      
      if (note) {
        return notesAPI.update(note.id, data)
      } else {
        return notesAPI.create(data)
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] })
      onClose()
    }
  })

  return (
    <div className="fixed inset-0 z-50 bg-background">
      <div className="h-full flex flex-col">
        <div className="border-b p-4 flex justify-between items-center">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Note title"
            className="text-2xl font-bold bg-transparent border-none outline-none flex-1"
          />
          <div className="flex gap-2">
            <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}>
              <Save className="h-4 w-4 mr-2" />
              Save
            </Button>
            <Button variant="outline" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="p-4">
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="Tags (comma-separated)"
            className="w-full mb-4 px-3 py-2 border rounded"
          />
        </div>

        <div className="flex-1 p-4">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Write your note in markdown..."
            className="w-full h-full p-4 border rounded font-mono resize-none"
          />
        </div>
      </div>
    </div>
  )
}
