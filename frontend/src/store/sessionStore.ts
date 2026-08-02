import { create } from 'zustand';
import type { Session } from '@/types';

interface SessionState {
  sessions: Session[];
  activeSessionId: string | null;
  pendingSessionId: string | null;
  searchQuery: string;
  setSessions: (sessions: Session[]) => void;
  addSession: (session: Session) => void;
  updateSession: (id: string, updates: Partial<Session>) => void;
  removeSession: (id: string) => void;
  setActiveSessionId: (id: string | null) => void;
  setPendingSessionId: (id: string | null) => void;
  setSearchQuery: (q: string) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  sessions: [],
  activeSessionId: null,
  pendingSessionId: null,
  searchQuery: '',

  setSessions: (sessions) => set({ sessions }),
  addSession: (session) =>
    set((s) => ({ sessions: [session, ...s.sessions] })),
  updateSession: (id, updates) =>
    set((s) => ({
      sessions: s.sessions.map((sess) =>
        sess.id === id ? { ...sess, ...updates } : sess
      ),
    })),
  removeSession: (id) =>
    set((s) => ({
      sessions: s.sessions.filter((sess) => sess.id !== id),
      activeSessionId: s.activeSessionId === id ? null : s.activeSessionId,
      pendingSessionId: s.pendingSessionId === id ? null : s.pendingSessionId,
    })),
  setActiveSessionId: (id) => set({ activeSessionId: id }),
  setPendingSessionId: (id) => set({ pendingSessionId: id }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),
}));
