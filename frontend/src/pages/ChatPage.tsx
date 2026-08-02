import { useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain } from 'lucide-react';
import { Sidebar } from '@/components/sidebar/Sidebar';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ChatInput } from '@/components/chat/ChatInput';
import { WelcomeScreen } from '@/components/chat/WelcomeScreen';
import { ResearchInspector } from '@/components/inspector/ResearchInspector';
import { ArtifactViewer } from '@/components/artifact/ArtifactViewer';
import { useChat } from '@/hooks/useChat';
import { useChatStore } from '@/store/chatStore';
import { useUIStore } from '@/store/uiStore';
import { useSessionStore } from '@/store/sessionStore';
import { sessionApi } from '@/api/sessionApi';

export function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { messages, isLoading, isStreaming, sendMessage, stopStreaming, error } = useChat(sessionId);
  const { toggleInspector, inspectorOpen } = useUIStore();
  const { setActiveSessionId, addSession, pendingSessionId, setPendingSessionId, removeSession } = useSessionStore();

  // Keep a stable ref to sessionId for cleanup effects
  const sessionIdRef = useRef(sessionId);
  sessionIdRef.current = sessionId;

  // Sync active session inside useEffect to prevent render-phase state updates
  useEffect(() => {
    if (sessionId) {
      setActiveSessionId(sessionId);
    }
  }, [sessionId, setActiveSessionId]);

  // Auto-delete a pending (empty) session when the user navigates away without typing anything
  useEffect(() => {
    return () => {
      const leavingSessionId = sessionIdRef.current;
      const { pendingSessionId: pending, removeSession: removeSess, setPendingSessionId: clearPending } =
        useSessionStore.getState();

      if (pending && pending === leavingSessionId) {
        const msgs = useChatStore.getState().messagesBySession[pending] || [];
        if (msgs.length === 0) {
          // Silently delete the empty session from backend + store
          sessionApi.delete(pending).catch(() => {});
          removeSess(pending);
          clearPending(null);
        }
      }
    };
  // Only re-run when sessionId changes (mounting a new chat route)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const handleSend = async (msg: string) => {
    let activeId = sessionId;
    if (!activeId) {
      try {
        const title = msg.length > 30 ? msg.slice(0, 30) + '...' : msg;
        const newSession = await sessionApi.create({ title });
        addSession(newSession);
        activeId = newSession.id;
        setActiveSessionId(activeId);
        navigate(`/chat/${activeId}`);
      } catch (err) {
        console.error('Failed to create session:', err);
        return;
      }
    } else if (pendingSessionId === activeId) {
      // First message sent in this session — it's no longer pending/empty
      setPendingSessionId(null);
    }
    sendMessage(msg, activeId);
  };

  const showWelcome = messages.length === 0 && !isStreaming;

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      minWidth: 0,
    }}>
      {/* Top bar — minimal, just inspector toggle */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        padding: '6px 12px',
        borderBottom: '1px solid var(--color-border-subtle)',
        gap: 8,
        flexShrink: 0,
        minHeight: 40,
      }}>
        <button
          className="btn-icon"
          onClick={toggleInspector}
          title="Toggle Research Inspector (⌘I)"
          style={{ color: inspectorOpen ? 'var(--color-accent)' : undefined }}
        >
          <Brain size={16} />
        </button>
      </div>

      {/* Error bar */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            style={{
              background: 'rgba(239,68,68,0.08)',
              borderBottom: '1px solid rgba(239,68,68,0.2)',
              padding: '8px 20px',
              fontSize: '0.8125rem',
              color: 'var(--color-error)',
            }}
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat + Artifact area */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        {/* Chat column */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', minWidth: 0 }}>
          {showWelcome ? (
            <WelcomeScreen onPromptClick={handleSend} />
          ) : (
            <ChatWindow messages={messages} isStreaming={isStreaming} isLoading={isLoading} />
          )}

          {/* Input */}
          <div style={{
            flexShrink: 0,
            borderTop: '1px solid var(--color-border-subtle)',
            background: 'var(--color-background)',
            padding: '12px 0 0',
          }}>
            <div style={{ maxWidth: 800, margin: '0 auto' }}>
              <ChatInput
                onSend={handleSend}
                isStreaming={isStreaming}
                onStop={stopStreaming}
                disabled={isStreaming}
                placeholder="Ask Lenny anything about growth..."
              />
            </div>
          </div>
        </div>

        {/* Artifact Runtime Panel */}
        <ArtifactViewer
          onRegenerate={() => {
            if (messages.length > 0) {
              const lastUserMsg = [...messages].reverse().find((m) => m.role === 'user');
              if (lastUserMsg) {
                handleSend(lastUserMsg.content);
              }
            }
          }}
        />
      </div>
    </div>
  );
}
