import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  PenSquare, ChevronLeft, ChevronRight, Search, Settings, X, Zap,
} from 'lucide-react';
import { useSessions } from '@/hooks/useSessions';
import { useUIStore } from '@/store/uiStore';
import { useSessionStore } from '@/store/sessionStore';
import { useSettings } from '@/hooks/useSettings';
import { SessionList } from './SessionList';

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className = '' }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarCollapsed, toggleSidebar } = useUIStore();
  const { searchQuery, setSearchQuery } = useSessionStore();
  const { createSession, isCreating } = useSessions();
  const { settings } = useSettings();

  const isSettingsActive = location.pathname === '/settings';

  return (
    <motion.div
      className={`sidebar ${className}`}
      animate={{ width: sidebarCollapsed ? 64 : 260 }}
      transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
      style={{ overflow: 'hidden', flexShrink: 0 }}
    >
      {/* Header */}
      <div style={{
        padding: sidebarCollapsed ? '12px 8px' : '12px 12px 8px',
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        borderBottom: '1px solid var(--color-border-subtle)',
      }}>
        {!sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            style={{ flex: 1, display: 'flex', alignItems: 'center', gap: 8 }}
          >
            <div style={{
              width: 26,
              height: 26,
              borderRadius: 7,
              background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}>
              <Zap size={13} color="#fff" fill="#fff" />
            </div>
            <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--color-text-primary)', letterSpacing: '-0.02em' }}>
              Lenny
            </span>
          </motion.div>
        )}
        {sidebarCollapsed && (
          <div style={{
            width: 28,
            height: 28,
            borderRadius: 7,
            background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto',
          }}>
            <Zap size={14} color="#fff" fill="#fff" />
          </div>
        )}
        <div style={{ display: 'flex', gap: 4, alignItems: 'center' }}>
          {!sidebarCollapsed && (
            <button
              className="btn-icon"
              onClick={() => createSession()}
              disabled={isCreating}
              title="New chat (⌘K)"
              aria-label="New chat"
            >
              <PenSquare size={15} />
            </button>
          )}
          <button
            className="btn-icon"
            onClick={toggleSidebar}
            title={sidebarCollapsed ? 'Expand sidebar (⌘\\)' : 'Collapse sidebar (⌘\\)'}
            aria-label="Toggle sidebar"
          >
            {sidebarCollapsed ? <ChevronRight size={15} /> : <ChevronLeft size={15} />}
          </button>
        </div>
      </div>

      {/* Collapsed: just new chat icon */}
      {sidebarCollapsed && (
        <div style={{ padding: '8px 8px 4px', display: 'flex', justifyContent: 'center' }}>
          <button
            className="btn-icon"
            onClick={() => createSession()}
            disabled={isCreating}
            title="New chat (⌘K)"
          >
            <PenSquare size={15} />
          </button>
        </div>
      )}

      {/* Search */}
      {!sidebarCollapsed && (
        <div style={{ padding: '8px 12px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            background: 'var(--color-surface-elevated)',
            border: '1px solid var(--color-border)',
            borderRadius: 8,
            padding: '6px 10px',
          }}>
            <Search size={13} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
            <input
              type="text"
              placeholder="Search chats..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                flex: 1,
                background: 'transparent',
                border: 'none',
                outline: 'none',
                color: 'var(--color-text-primary)',
                fontSize: '0.8125rem',
                fontFamily: 'inherit',
              }}
            />
            {searchQuery && (
              <button
                className="btn-icon"
                onClick={() => setSearchQuery('')}
                style={{ width: 16, height: 16, padding: 0 }}
              >
                <X size={12} />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Session List */}
      <div style={{ flex: 1, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        <SessionList collapsed={sidebarCollapsed} />
      </div>

      {/* Footer */}
      <div style={{
        padding: sidebarCollapsed ? '8px' : '8px 12px',
        borderTop: '1px solid var(--color-border-subtle)',
        display: 'flex',
        flexDirection: 'column',
        gap: 4,
      }}>
        {!sidebarCollapsed && (
          <AnimatePresence>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: 8,
                padding: '6px 8px',
                borderRadius: 8,
                background: 'var(--color-surface-elevated)',
                marginBottom: 4,
              }}
            >
              <div style={{
                width: 28,
                height: 28,
                borderRadius: 6,
                background: 'linear-gradient(135deg, #22c55e, #06b6d4)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#fff' }}>GA</span>
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: '0.8rem', fontWeight: 500, color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {settings.provider === 'ollama' ? 'Ollama (Local)' : settings.provider === 'anthropic' ? 'Anthropic' : 'OpenAI'}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {settings.model || 'mistral:7b'}
                </div>
              </div>
              <div className="badge badge-green" style={{ fontSize: '0.65rem', padding: '1px 5px' }}>Active</div>
            </motion.div>
          </AnimatePresence>
        )}

        <button
          className={`sidebar-item ${isSettingsActive ? 'active' : ''}`}
          style={sidebarCollapsed ? { justifyContent: 'center', padding: 8 } : {}}
          onClick={() => navigate('/settings')}
          title="Settings (⌘,)"
        >
          <Settings size={15} />
          {!sidebarCollapsed && <span>Settings</span>}
        </button>
      </div>
    </motion.div>
  );
}
