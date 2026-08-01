import { useParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { PanelRight, Brain } from 'lucide-react';
import { Sidebar } from '@/components/sidebar/Sidebar';
import { ChatWindow } from '@/components/chat/ChatWindow';
import { ChatInput } from '@/components/chat/ChatInput';
import { WelcomeScreen } from '@/components/chat/WelcomeScreen';
import { ResearchInspector } from '@/components/inspector/ResearchInspector';
import { ArtifactViewer } from '@/components/artifact/ArtifactViewer';
import { useChat } from '@/hooks/useChat';
import { useUIStore } from '@/store/uiStore';
import { useArtifactStore } from '@/store/artifactStore';
import { useSessionStore } from '@/store/sessionStore';

export function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const { messages, isLoading, isStreaming, sendMessage, stopStreaming, error } = useChat(sessionId);
  const { toggleInspector, inspectorOpen } = useUIStore();
  const { currentArtifact } = useArtifactStore();
  const { setActiveSessionId } = useSessionStore();

  // Sync active session
  if (sessionId) setActiveSessionId(sessionId);

  const handleSend = (msg: string) => {
    if (!sessionId) return;
    sendMessage(msg);
  };

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
      minWidth: 0,
    }}>
      {/* Top bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        padding: '8px 16px',
        borderBottom: '1px solid var(--color-border-subtle)',
        gap: 4,
        flexShrink: 0,
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
          {!sessionId || messages.length === 0 ? (
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
                disabled={!sessionId}
                placeholder={sessionId ? 'Ask Lenny anything about growth...' : 'Create a new chat to start'}
              />
            </div>
          </div>
        </div>

        {/* Artifact Viewer (if open and not using inspector) */}
        {currentArtifact && (
          <div style={{ width: 520, flexShrink: 0 }}>
            <ArtifactViewer />
          </div>
        )}
      </div>
    </div>
  );
}
