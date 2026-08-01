import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { chatApi } from '@/api/chatApi';
import { useChatStore } from '@/store/chatStore';
import { useSessionStore } from '@/store/sessionStore';
import type { Message } from '@/types';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

export function useChat(sessionId: string | undefined) {
  const {
    messagesBySession,
    isStreaming,
    streamingContent,
    setMessages,
    addMessage,
    setIsStreaming,
    setStreamingContent,
    finalizeStreamingMessage,
    setLastRetrievalResult,
  } = useChatStore();
  const { updateSession } = useSessionStore();
  const [error, setError] = useState<string | null>(null);

  const messages = sessionId ? (messagesBySession[sessionId] || []) : [];

  // Load messages for the session
  const query = useQuery({
    queryKey: ['messages', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const msgs = await chatApi.getMessages(sessionId);
      setMessages(sessionId, msgs);
      return msgs;
    },
    enabled: !!sessionId,
    staleTime: 10000,
  });

  // Simulate streaming word-by-word
  const simulateStreaming = useCallback(
    async (sessionId: string, fullContent: string, onDone: (content: string) => void) => {
      const words = fullContent.split(' ');
      let current = '';
      setIsStreaming(true, sessionId);

      // Add streaming placeholder message
      const streamingMsg: Message = {
        id: `streaming-${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        is_streaming: true,
      };
      addMessage(sessionId, streamingMsg);

      for (let i = 0; i < words.length; i++) {
        current += (i === 0 ? '' : ' ') + words[i];
        setStreamingContent(current);
        // Store in message
        useChatStore.getState().updateLastMessage(sessionId, current);
        // Vary the speed for realism
        const speed = words[i].endsWith('\n') || words[i].endsWith('.') ? 80 : 25;
        await delay(speed);
      }

      onDone(current);
    },
    [addMessage, setIsStreaming, setStreamingContent]
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId || !content.trim() || isStreaming) return;
      setError(null);

      // Optimistically add user message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        session_id: sessionId,
        role: 'user',
        content: content.trim(),
        created_at: new Date().toISOString(),
      };
      addMessage(sessionId, userMessage);

      try {
        // Call the API (mock or real)
        const response = await chatApi.sendMessage({
          session_id: sessionId,
          content: content.trim(),
        });

        // Update retrieval result
        if (response.metadata?.sources) {
          setLastRetrievalResult({
            chunks: [],
            sources: response.metadata.sources,
            retrieval_time_ms: response.metadata.retrieval_time_ms || 0,
            confidence_score: response.metadata.confidence_score || 0,
            model: response.metadata.model || '',
            provider: 'anthropic',
            tokens_used: response.metadata.tokens_used,
          });
        }

        // Simulate streaming of the assistant response
        await simulateStreaming(sessionId, response.response_message.content, () => {
          finalizeStreamingMessage(sessionId, response.response_message);
          setIsStreaming(false);
        });

        // Update session title on first message
        updateSession(sessionId, { last_message: content.trim() });

      } catch (err) {
        setIsStreaming(false);
        setError(err instanceof Error ? err.message : 'Failed to send message');
      }
    },
    [
      sessionId,
      isStreaming,
      addMessage,
      simulateStreaming,
      finalizeStreamingMessage,
      setIsStreaming,
      setLastRetrievalResult,
      updateSession,
    ]
  );

  const stopStreaming = useCallback(() => {
    setIsStreaming(false);
  }, [setIsStreaming]);

  return {
    messages,
    isLoading: query.isLoading,
    isStreaming,
    streamingContent,
    error,
    sendMessage,
    stopStreaming,
    refetch: query.refetch,
  };
}
