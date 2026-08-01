import apiClient, { USE_MOCK } from './client';
import { mockMessages, mockCitations, mockChunks, mockArtifacts, mockResponses } from './mock/mockData';
import type { Message, SendMessageInput, SendMessageResponse, RetrievalResult } from '@/types';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const chatApi = {
  getMessages: async (sessionId: string): Promise<Message[]> => {
    if (USE_MOCK) {
      await delay(200);
      return mockMessages[sessionId] || [];
    }
    const res = await apiClient.get<Message[]>(`/sessions/${sessionId}/messages`);
    return res.data;
  },

  sendMessage: async (input: SendMessageInput): Promise<SendMessageResponse> => {
    if (USE_MOCK) {
      await delay(800);
      const responseContent = mockResponses[Math.floor(Math.random() * mockResponses.length)];
      const isEssay = input.content.toLowerCase().includes('essay') || input.content.toLowerCase().includes('write');
      const hasArtifact = input.content.toLowerCase().includes('generate') || input.content.toLowerCase().includes('create') || input.content.toLowerCase().includes('artifact');

      // Add user message to mock store
      const userMsg: Message = {
        id: `msg-${Date.now()}-user`,
        session_id: input.session_id,
        role: 'user',
        content: input.content,
        created_at: new Date().toISOString(),
      };

      const assistantMsg: Message = {
        id: `msg-${Date.now()}-assistant`,
        session_id: input.session_id,
        role: 'assistant',
        content: responseContent,
        created_at: new Date().toISOString(),
        citations: isEssay ? undefined : mockCitations.slice(0, 2),
        metadata: {
          service: isEssay ? 'EssayService' : hasArtifact ? 'ArtifactService' : 'QAService',
          intent: isEssay ? 'essay' : hasArtifact ? 'artifact' : 'qa',
          retrieval_performed: !isEssay,
          confidence_score: isEssay ? undefined : 0.87 + Math.random() * 0.1,
          retrieval_time_ms: isEssay ? undefined : 200 + Math.floor(Math.random() * 300),
          model: 'claude-3-5-sonnet-20241022',
          sources: isEssay ? undefined : mockCitations.slice(0, 2),
          artifact_id: hasArtifact ? mockArtifacts[0].id : undefined,
        },
      };

      if (!mockMessages[input.session_id]) {
        mockMessages[input.session_id] = [];
      }
      mockMessages[input.session_id].push(userMsg, assistantMsg);

      return {
        session_id: input.session_id,
        intent: isEssay ? 'essay' : hasArtifact ? 'artifact' : 'qa',
        response_message: assistantMsg,
        history_count: mockMessages[input.session_id].length,
        metadata: assistantMsg.metadata!,
      };
    }
    const res = await apiClient.post<SendMessageResponse>('/chat', input);
    return res.data;
  },

  getRetrieval: async (sessionId: string, messageId: string): Promise<RetrievalResult> => {
    if (USE_MOCK) {
      await delay(100);
      return {
        chunks: mockChunks,
        sources: mockCitations,
        retrieval_time_ms: 287,
        confidence_score: 0.88,
        model: 'claude-3-5-sonnet-20241022',
        provider: 'anthropic',
        tokens_used: 1847,
      };
    }
    const res = await apiClient.get<RetrievalResult>(`/sessions/${sessionId}/messages/${messageId}/retrieval`);
    return res.data;
  },
};
