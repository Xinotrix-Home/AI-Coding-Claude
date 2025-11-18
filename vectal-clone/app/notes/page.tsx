'use client'

import { useState, useEffect } from 'react'
import { Plus, Search, FileText, Trash2, Save, X } from 'lucide-react'

interface Note {
  id: string
  title: string
  content: string
  tags: string | null
  createdAt: string
  updatedAt: string
}

export default function NotesPage() {
  const [notes, setNotes] = useState<Note[]>([])
  const [filteredNotes, setFilteredNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedNote, setSelectedNote] = useState<Note | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [editTitle, setEditTitle] = useState('')
  const [editContent, setEditContent] = useState('')
  const [editTags, setEditTags] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    fetchNotes()
  }, [])

  useEffect(() => {
    filterNotes()
  }, [notes, searchQuery])

  const fetchNotes = async () => {
    try {
      const response = await fetch('/api/notes')
      if (response.ok) {
        const data = await response.json()
        setNotes(data)
      }
    } catch (error) {
      console.error('Error fetching notes:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterNotes = () => {
    if (!searchQuery) {
      setFilteredNotes(notes)
      return
    }

    const filtered = notes.filter(note =>
      note.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
      note.tags?.toLowerCase().includes(searchQuery.toLowerCase())
    )

    setFilteredNotes(filtered)
  }

  const handleCreateNote = () => {
    setIsCreating(true)
    setSelectedNote(null)
    setEditTitle('')
    setEditContent('')
    setEditTags('')
  }

  const handleSelectNote = (note: Note) => {
    setSelectedNote(note)
    setIsCreating(false)
    setEditTitle(note.title)
    setEditContent(note.content)
    setEditTags(note.tags || '')
  }

  const handleSave = async () => {
    if (!editTitle.trim()) {
      alert('Title is required')
      return
    }

    setSaving(true)
    try {
      if (isCreating) {
        const response = await fetch('/api/notes', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: editTitle,
            content: editContent,
            tags: editTags || null,
          }),
        })

        if (response.ok) {
          const newNote = await response.json()
          setNotes([newNote, ...notes])
          setSelectedNote(newNote)
          setIsCreating(false)
        }
      } else if (selectedNote) {
        const response = await fetch(`/api/notes/${selectedNote.id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: editTitle,
            content: editContent,
            tags: editTags || null,
          }),
        })

        if (response.ok) {
          const updatedNote = await response.json()
          setNotes(notes.map(n => n.id === updatedNote.id ? updatedNote : n))
          setSelectedNote(updatedNote)
        }
      }
    } catch (error) {
      console.error('Error saving note:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (noteId: string) => {
    if (!confirm('Are you sure you want to delete this note?')) {
      return
    }

    try {
      const response = await fetch(`/api/notes/${noteId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setNotes(notes.filter(n => n.id !== noteId))
        if (selectedNote?.id === noteId) {
          setSelectedNote(null)
          setIsCreating(false)
        }
      }
    } catch (error) {
      console.error('Error deleting note:', error)
    }
  }

  return (
    <div className="flex h-screen">
      {/* Sidebar - Notes List */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900">Notes</h2>
            <button
              onClick={handleCreateNote}
              className="bg-blue-600 text-white p-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-5 h-5" />
            </button>
          </div>

          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search notes..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            </div>
          ) : filteredNotes.length === 0 ? (
            <div className="p-8 text-center">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-600">
                {searchQuery ? 'No notes found' : 'No notes yet'}
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredNotes.map((note) => (
                <button
                  key={note.id}
                  onClick={() => handleSelectNote(note)}
                  className={`w-full p-4 text-left hover:bg-gray-50 transition-colors ${
                    selectedNote?.id === note.id ? 'bg-blue-50 border-l-4 border-blue-600' : ''
                  }`}
                >
                  <h3 className="font-semibold text-gray-900 mb-1 truncate">
                    {note.title}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {note.content || 'No content'}
                  </p>
                  {note.tags && (
                    <p className="text-xs text-gray-500 mt-2">
                      {note.tags}
                    </p>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Main Content - Note Editor */}
      <div className="flex-1 flex flex-col">
        {selectedNote || isCreating ? (
          <>
            <div className="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center">
              <input
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                placeholder="Note title..."
                className="text-2xl font-bold text-gray-900 border-none focus:outline-none flex-1"
              />
              <div className="flex gap-2">
                <button
                  onClick={handleSave}
                  disabled={saving || !editTitle.trim()}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition-colors flex items-center"
                >
                  <Save className="w-4 h-4 mr-2" />
                  {saving ? 'Saving...' : 'Save'}
                </button>
                {selectedNote && (
                  <button
                    onClick={() => handleDelete(selectedNote.id)}
                    className="text-red-600 hover:bg-red-50 px-4 py-2 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => {
                    setSelectedNote(null)
                    setIsCreating(false)
                  }}
                  className="text-gray-600 hover:bg-gray-100 px-4 py-2 rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div className="p-6 flex-1 overflow-y-auto">
              <div className="max-w-4xl mx-auto space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tags
                  </label>
                  <input
                    type="text"
                    value={editTags}
                    onChange={(e) => setEditTags(e.target.value)}
                    placeholder="work, personal, ideas..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Content
                  </label>
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    placeholder="Start writing..."
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[400px]"
                  />
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gray-50">
            <div className="text-center">
              <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No note selected
              </h3>
              <p className="text-gray-600 mb-6">
                Select a note from the list or create a new one
              </p>
              <button
                onClick={handleCreateNote}
                className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Note
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
