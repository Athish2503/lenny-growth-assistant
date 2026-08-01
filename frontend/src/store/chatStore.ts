import { create } from 'zustand';
import type { Message, RetrievalResult } from '@/types';

interface ChatState {
  messagesBySession: Record<string, Message[]>;
  isStreaming: boolean;
  streamingSessionId: string | null;
  streamingContent: string;
  lastRetrievalResult: RetrievalResult | null;
  setMessages: (sessionId: string, messages: Message[]) => void;
  addMessage: (sessionId: string, message: Message) => void;
  updateLastMessage: (sessionId: string, content: string) => void;
  finalizeStreamingMessage: (sessionId: string, message: Message) => void;
  setIsStreaming: (v: boolean, sessionId?: string | null) => void;
  setStreamingContent: (content: string) => void;
  setLastRetrievalResult: (result: RetrievalResult | null) => void;
  clearMessages: (sessionId: string) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messagesBySession: {},
  isStreaming: false,
  streamingSessionId: null,
  streamingContent: '',
  lastRetrievalResult: null,

  setMessages: (sessionId, messages) =>
    set((s) => ({
      messagesBySession: { ...s.messagesBySession, [sessionId]: messages },
    })),

  addMessage: (sessionId, message) =>
    set((s) => ({
      messagesBySession: {
        ...s.messagesBySession,
        [sessionId]: [...(s.messagesBySession[sessionId] || []), message],
      },
    })),

  updateLastMessage: (sessionId, content) =>
    set((s) => {
      const msgs = s.messagesBySession[sessionId] || [];
      if (msgs.length === 0) return s;
      const updated = [...msgs];
      updated[updated.length - 1] = { ...updated[updated.length - 1], content };
      return {
        messagesBySession: { ...s.messagesBySession, [sessionId]: updated },
      };
    }),

  finalizeStreamingMessage: (sessionId, message) =>
    set((s) => {
      const msgs = s.messagesBySession[sessionId] || [];
      const updated = [...msgs];
      if (updated.length > 0 && updated[updated.length - 1].is_streaming) {
        updated[updated.length - 1] = message;
      } else {
        updated.push(message);
      }
      return {
        messagesBySession: { ...s.messagesBySession, [sessionId]: updated },
        isStreaming: false,
        streamingSessionId: null,
        streamingContent: '',
      };
    }),

  setIsStreaming: (v, sessionId = null) =>
    set({ isStreaming: v, streamingSessionId: sessionId ?? null }),

  setStreamingContent: (content) => set({ streamingContent: content }),

  setLastRetrievalResult: (result) => set({ lastRetrievalResult: result }),

  clearMessages: (sessionId) =>
    set((s) => {
      const updated = { ...s.messagesBySession };
      delete updated[sessionId];
      return { messagesBySession: updated };
    }),
}));
