import { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Cpu, ChevronDown } from 'lucide-react';
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
import { useSettings } from '@/hooks/useSettings';
import { sessionApi } from '@/api/sessionApi';

function ModelSelectorHeader() {
  const { settings, saveSettings, availableModels } = useSettings();
  const providerModels = availableModels?.[settings.provider] || [];

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, position: 'relative' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 6,
        background: 'var(--color-surface-elevated)',
        border: '1px solid var(--color-border)',
        borderRadius: 8,
        padding: '3px 8px',
        fontSize: '0.8rem',
      }}>
        <Cpu size={13} style={{ color: 'var(--color-accent)' }} />
        <select
          value={settings.provider}
          onChange={(e) => {
            const p = e.target.value as 'ollama' | 'anthropic' | 'openai';
            const models = availableModels?.[p] || [];
            const defModel = models[0] || (p === 'ollama' ? 'mistral:7b' : 'claude-3-5-sonnet-20240620');
            saveSettings({ provider: p, model: defModel });
          }}
          style={{
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--color-text-primary)',
            fontSize: '0.8rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <option value="ollama">Ollama</option>
          <option value="anthropic">Anthropic</option>
          <option value="openai">OpenAI</option>
        </select>
        <span style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem' }}>/</span>
        <select
          value={settings.model}
          onChange={(e) => saveSettings({ model: e.target.value })}
          style={{
            background: 'transparent',
            border: 'none',
            outline: 'none',
            color: 'var(--color-text-muted)',
            fontSize: '0.8rem',
            cursor: 'pointer',
            maxWidth: 140,
            textOverflow: 'ellipsis',
          }}
        >
          {!providerModels.includes(settings.model) && settings.model && (
            <option value={settings.model}>{settings.model}</option>
          )}
          {providerModels.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

export function ChatPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const { messages, isLoading, isStreaming, sendMessage, stopStreaming, error } = useChat(sessionId);
  const { toggleInspector, inspectorOpen } = useUIStore();
  const { currentArtifact } = useArtifactStore();
  const { setActiveSessionId, addSession } = useSessionStore();

  // Sync active session inside useEffect to prevent render-phase state updates
  useEffect(() => {
    if (sessionId) {
      setActiveSessionId(sessionId);
    }
  }, [sessionId, setActiveSessionId]);

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
    }
    sendMessage(msg, activeId);
  };

  const showWelcome = !sessionId && messages.length === 0 && !isStreaming;

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
        justifyContent: 'space-between',
        padding: '8px 16px',
        borderBottom: '1px solid var(--color-border-subtle)',
        gap: 8,
        flexShrink: 0,
      }}>
        <ModelSelectorHeader />
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
