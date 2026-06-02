import type { AnswerEvidence } from '../types/api';

export interface Note {
  note_id: string;
  workspace_id: string;
  content: string;
  evidence_refs: AnswerEvidence[];
  created_at: string;
  updated_at: string;
}

export function getNotesKey(workspaceId: string): string {
  return `notes_${workspaceId}`;
}

export function loadNotes(workspaceId: string): Note[] {
  try {
    const raw = localStorage.getItem(getNotesKey(workspaceId));
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveNotes(workspaceId: string, notes: Note[]): void {
  localStorage.setItem(getNotesKey(workspaceId), JSON.stringify(notes));
}

export function createNote(workspaceId: string, content: string, evidenceRefs: AnswerEvidence[] = []): Note {
  const notes = loadNotes(workspaceId);
  const now = new Date().toISOString();
  const note: Note = {
    note_id: `note_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`,
    workspace_id: workspaceId,
    content,
    evidence_refs: evidenceRefs,
    created_at: now,
    updated_at: now
  };
  notes.unshift(note);
  saveNotes(workspaceId, notes);
  return note;
}

export function updateNote(workspaceId: string, noteId: string, content: string): Note | null {
  const notes = loadNotes(workspaceId);
  const index = notes.findIndex((n) => n.note_id === noteId);
  if (index < 0) return null;
  notes[index] = { ...notes[index], content, updated_at: new Date().toISOString() };
  saveNotes(workspaceId, notes);
  return notes[index];
}

export function deleteNote(workspaceId: string, noteId: string): boolean {
  const notes = loadNotes(workspaceId);
  const filtered = notes.filter((n) => n.note_id !== noteId);
  if (filtered.length === notes.length) return false;
  saveNotes(workspaceId, filtered);
  return true;
}