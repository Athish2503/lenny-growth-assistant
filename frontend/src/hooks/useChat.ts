import { useState, useCallback, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { chatApi } from '@/api/chatApi';
import { USE_MOCK } from '@/api/client';
import { useChatStore } from '@/store/chatStore';
import { useSessionStore } from '@/store/sessionStore';
import { useArtifactStore } from '@/store/artifactStore';
import type { Message, Artifact } from '@/types';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
  const { setCurrentArtifact, setActiveTab } = useArtifactStore();
  const [error, setError] = useState<string | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const messages = sessionId ? messagesBySession[sessionId] || [] : [];

  // Load messages for the session
  const query = useQuery({
    queryKey: ['messages', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const msgs = await chatApi.getMessages(sessionId);
      const existing = useChatStore.getState().messagesBySession[sessionId] || [];
      if (existing.length > 0) {
        // Keep any unsaved or active streaming messages
        const unsaved = existing.filter(
          (m) => m.is_streaming || !msgs.some((dbM) => dbM.id === m.id)
        );
        const merged = [...msgs, ...unsaved];
        setMessages(sessionId, merged);
        return merged;
      }
      setMessages(sessionId, msgs);
      return msgs;
    },
    enabled: !!sessionId,
    staleTime: 10000,
  });

  // Simulate streaming word-by-word (for mock mode fallback)
  const simulateStreaming = useCallback(
    async (sessionId: string, fullContent: string, onDone: (content: string) => void) => {
      const words = fullContent.split(' ');
      let current = '';
      setIsStreaming(true, sessionId);

      for (let i = 0; i < words.length; i++) {
        if (abortControllerRef.current?.signal.aborted) break;
        current += (i === 0 ? '' : ' ') + words[i];
        setStreamingContent(current);
        useChatStore.getState().updateLastMessage(sessionId, current);
        const speed = words[i].endsWith('\n') || words[i].endsWith('.') ? 80 : 25;
        await delay(speed);
      }

      onDone(current);
    },
    [setIsStreaming, setStreamingContent]
  );

  const sendMessage = useCallback(
    async (content: string, targetSessionId?: string) => {
      const activeId = targetSessionId || sessionId;
      if (!activeId || !content.trim() || isStreaming) return;
      setError(null);

      // Optimistically add user message
      const userMessage: Message = {
        id: `user-${Date.now()}`,
        session_id: activeId,
        role: 'user',
        content: content.trim(),
        created_at: new Date().toISOString(),
      };
      addMessage(activeId, userMessage);

      // Add streaming placeholder assistant message
      const streamingMsg: Message = {
        id: `streaming-${Date.now()}`,
        session_id: activeId,
        role: 'assistant',
        content: '',
        created_at: new Date().toISOString(),
        is_streaming: true,
      };
      addMessage(activeId, streamingMsg);
      setIsStreaming(true, activeId);

      abortControllerRef.current = new AbortController();

      if (USE_MOCK) {
        try {
          const response = await chatApi.sendMessage({
            session_id: activeId,
            content: content.trim(),
          });

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

          await simulateStreaming(activeId, response.response_message.content, () => {
            finalizeStreamingMessage(activeId, response.response_message);
            setIsStreaming(false);
          });

          updateSession(activeId, { last_message: content.trim() });
        } catch (err) {
          setIsStreaming(false);
          setError(err instanceof Error ? err.message : 'Failed to send message');
        }
        return;
      }

      // Real SSE Streaming from Backend
      try {
        const response = await fetch(`${BASE_URL}/api/v1/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'text/event-stream',
          },
          body: JSON.stringify({
            session_id: activeId,
            content: content.trim(),
            stream: true,
          }),
          signal: abortControllerRef.current.signal,
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({ detail: 'Failed to process request' }));
          throw new Error(errData.detail || `HTTP Error ${response.status}`);
        }

        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        let accumulatedText = '';
        let finalAssistantMessage: Message | null = null;
        let artifactObj: Artifact | null = null;

        if (reader) {
          let buffer = '';
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
              const trimmed = line.trim();
              if (trimmed.startsWith('data: ')) {
                const dataStr = trimmed.slice(6);
                try {
                  const event = JSON.parse(dataStr);
                  if (event.type === 'metadata') {
                    if (event.sources || event.citations) {
                      setLastRetrievalResult({
                        chunks: [],
                        sources: event.citations || event.sources || [],
                        retrieval_time_ms: event.retrieval_time_ms || 0,
                        confidence_score: event.confidence_score || 0,
                        model: event.model || '',
                        provider: 'ollama',
                      });
                    }
                  } else if (event.type === 'token') {
                    accumulatedText += event.content;
                    setStreamingContent(accumulatedText);
                    useChatStore.getState().updateLastMessage(activeId, accumulatedText);
                  } else if (event.type === 'done') {
                    finalAssistantMessage = event.response_message;
                    if (event.artifact) {
                      artifactObj = event.artifact;
                    }
                  }
                } catch {
                  // Ignore JSON parse error on partial chunks
                }
              }
            }
          }
        }

        const finalMsg: Message = finalAssistantMessage || {
          id: `msg-${Date.now()}`,
          session_id: activeId,
          role: 'assistant',
          content: accumulatedText,
          created_at: new Date().toISOString(),
        };

        finalizeStreamingMessage(activeId, finalMsg);
        setIsStreaming(false);

        // Auto open artifact if created
        if (artifactObj || finalMsg.metadata?.artifact || finalMsg.metadata?.has_artifacts) {
          const art = artifactObj || (finalMsg.metadata?.artifact as Artifact);
          if (art) {
            setCurrentArtifact(art);
            setActiveTab('preview');
          }
        }

        updateSession(activeId, { last_message: content.trim() });
      } catch (err: unknown) {
        setIsStreaming(false);
        if (err instanceof Error && err.name === 'AbortError') {
          setError('Generation stopped by user');
        } else {
          setError(err instanceof Error ? err.message : 'Network failure or server error');
        }
      }
    },
    [
      sessionId,
      isStreaming,
      addMessage,
      setIsStreaming,
      setStreamingContent,
      finalizeStreamingMessage,
      setLastRetrievalResult,
      setCurrentArtifact,
      setActiveTab,
      simulateStreaming,
      updateSession,
    ]
  );

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
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
