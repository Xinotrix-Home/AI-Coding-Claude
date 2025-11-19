'use client'

import { useState } from 'react'
import { NoteList } from '@/components/features/NoteList'
import { NoteEditor } from '@/components/features/NoteEditor'
import { Note } from '@/lib/api/notes'

export default function NotesPage() {
  const [isEditorOpen, setIsEditorOpen] = useState(false)
  const [selectedNote, setSelectedNote] = useState<Note | undefined>()

  const handleSelectNote = (note: Note) => {
    setSelectedNote(note)
    setIsEditorOpen(true)
  }

  const handleCloseEditor = () => {
    setIsEditorOpen(false)
    setSelectedNote(undefined)
  }

  if (isEditorOpen) {
    return <NoteEditor note={selectedNote} onClose={handleCloseEditor} />
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Notes</h1>
        <p className="text-muted-foreground">Capture your thoughts and ideas</p>
      </div>

      <NoteList
        onSelectNote={handleSelectNote}
        onCreateNote={() => setIsEditorOpen(true)}
      />
    </div>
  )
}
