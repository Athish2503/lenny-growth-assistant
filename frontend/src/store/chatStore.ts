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
      const streamingIdx = updated.findLastIndex((m) => m.is_streaming || m.role === 'assistant');
      if (streamingIdx !== -1) {
        updated[streamingIdx] = { ...updated[streamingIdx], content };
      } else {
        updated[updated.length - 1] = { ...updated[updated.length - 1], content };
      }
      return {
        messagesBySession: { ...s.messagesBySession, [sessionId]: updated },
      };
    }),

  finalizeStreamingMessage: (sessionId, message) =>
    set((s) => {
      const msgs = s.messagesBySession[sessionId] || [];
      const updated = [...msgs];
      const streamingIdx = updated.findIndex((m) => m.is_streaming);
      if (streamingIdx !== -1) {
        updated[streamingIdx] = { ...message, is_streaming: false };
      } else {
        updated.push({ ...message, is_streaming: false });
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
