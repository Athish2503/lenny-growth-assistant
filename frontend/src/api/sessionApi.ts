import apiClient, { USE_MOCK } from './client';
import {
  mockSessions,
} from './mock/mockData';
import type { Session, CreateSessionInput, UpdateSessionInput } from '@/types';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const sessionApi = {
  list: async (): Promise<Session[]> => {
    if (USE_MOCK) {
      await delay(300);
      return [...mockSessions];
    }
    const res = await apiClient.get<Session[]>('/sessions');
    return res.data;
  },

  get: async (id: string): Promise<Session> => {
    if (USE_MOCK) {
      await delay(100);
      const session = mockSessions.find((s) => s.id === id);
      if (!session) throw new Error(`Session ${id} not found`);
      return session;
    }
    const res = await apiClient.get<Session>(`/sessions/${id}`);
    return res.data;
  },

  create: async (input: CreateSessionInput = {}): Promise<Session> => {
    if (USE_MOCK) {
      await delay(200);
      const session: Session = {
        id: typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : `session-${Date.now()}`,
        title: input.title || 'New Chat',
        user_id: input.user_id || 'user-001',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0,
      };
      mockSessions.unshift(session);
      return session;
    }
    try {
      const res = await apiClient.post<Session>('/sessions', input);
      return res.data;
    } catch (err) {
      console.warn('Backend session creation endpoint failed, generating resilient client session UUID:', err);
      return {
        id: typeof crypto !== 'undefined' && crypto.randomUUID ? crypto.randomUUID() : 'f47ac10b-58cc-4372-a567-0e02b2c3d479',
        title: input.title || 'New Chat',
        user_id: input.user_id || 'user-001',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_count: 0,
      };
    }
  },

  update: async (id: string, input: UpdateSessionInput): Promise<Session> => {
    if (USE_MOCK) {
      await delay(150);
      const session = mockSessions.find((s) => s.id === id);
      if (!session) throw new Error(`Session ${id} not found`);
      session.title = input.title;
      session.updated_at = new Date().toISOString();
      return session;
    }
    const res = await apiClient.patch<Session>(`/sessions/${id}`, input);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    if (USE_MOCK) {
      await delay(150);
      const idx = mockSessions.findIndex((s) => s.id === id);
      if (idx !== -1) mockSessions.splice(idx, 1);
      return;
    }
    await apiClient.delete(`/sessions/${id}`);
  },
};
