import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useNavigate, useParams } from 'react-router-dom';
import {
  MessageSquare, MoreHorizontal, Pencil, Trash2, Check, X,
} from 'lucide-react';
import { useSessions } from '@/hooks/useSessions';
import { useUIStore } from '@/store/uiStore';
import { useSessionStore } from '@/store/sessionStore';
import type { Session } from '@/types';

interface SessionItemProps {
  session: Session;
  isActive: boolean;
  collapsed: boolean;
}

export function SessionItem({ session, isActive, collapsed }: SessionItemProps) {
  const navigate = useNavigate();
  const { renameSession, deleteSession } = useSessions();
  const { setMobileSidebarOpen } = useUIStore();
  const [showMenu, setShowMenu] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [renameValue, setRenameValue] = useState(session.title);
  const menuRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isRenaming && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [isRenaming]);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowMenu(false);
      }
    };
    if (showMenu) document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [showMenu]);

  const handleClick = () => {
    if (isRenaming) return;
    navigate(`/chat/${session.id}`);
    setMobileSidebarOpen(false);
  };

  const handleRenameSubmit = () => {
    if (renameValue.trim() && renameValue !== session.title) {
      renameSession({ id: session.id, title: renameValue.trim() });
    }
    setIsRenaming(false);
  };

  const handleRenameKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleRenameSubmit();
    if (e.key === 'Escape') {
      setRenameValue(session.title);
      setIsRenaming(false);
    }
  };

  if (collapsed) {
    return (
      <button
        onClick={handleClick}
        title={session.title}
        className={`sidebar-item w-full justify-center ${isActive ? 'active' : ''}`}
        style={{ padding: '8px' }}
      >
        <MessageSquare size={16} />
      </button>
    );
  }

  return (
    <div
      className={`group relative sidebar-item ${isActive ? 'active' : ''}`}
      onClick={handleClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
    >
      {isRenaming ? (
        <div className="flex items-center gap-1 flex-1 min-w-0" onClick={(e) => e.stopPropagation()}>
          <input
            ref={inputRef}
            value={renameValue}
            onChange={(e) => setRenameValue(e.target.value)}
            onKeyDown={handleRenameKeyDown}
            className="form-input flex-1 min-w-0 text-xs py-1 px-2"
            style={{ fontSize: '0.8rem', padding: '3px 6px' }}
          />
          <button className="btn-icon" style={{ width: 22, height: 22, padding: 2 }} onClick={handleRenameSubmit}>
            <Check size={12} />
          </button>
          <button className="btn-icon" style={{ width: 22, height: 22, padding: 2 }} onClick={() => { setRenameValue(session.title); setIsRenaming(false); }}>
            <X size={12} />
          </button>
        </div>
      ) : (
        <>
          <MessageSquare size={14} style={{ flexShrink: 0 }} />
          <span style={{ flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '0.8125rem' }}>
            {session.title}
          </span>
          <div
            ref={menuRef}
            className="relative"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="btn-icon opacity-0 group-hover:opacity-100 transition-opacity"
              style={{ width: 22, height: 22, padding: 2 }}
              onClick={() => setShowMenu(!showMenu)}
            >
              <MoreHorizontal size={13} />
            </button>
            <AnimatePresence>
              {showMenu && (
                <motion.div
                  className="context-menu absolute right-0 top-full mt-1 z-50"
                  initial={{ opacity: 0, scale: 0.95, y: -4 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.95, y: -4 }}
                  transition={{ duration: 0.12 }}
                >
                  <button
                    className="context-menu-item w-full"
                    onClick={() => { setIsRenaming(true); setShowMenu(false); }}
                  >
                    <Pencil size={12} /> Rename
                  </button>
                  <button
                    className="context-menu-item danger w-full"
                    onClick={() => { deleteSession(session.id); setShowMenu(false); }}
                  >
                    <Trash2 size={12} /> Delete
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </>
      )}
    </div>
  );
}

// ============================================================
// Session Group
// ============================================================
interface SessionGroupProps {
  label: string;
  sessions: Session[];
  activeId: string | undefined;
  collapsed: boolean;
}

export function SessionGroup({ label, sessions, activeId, collapsed }: SessionGroupProps) {
  if (sessions.length === 0) return null;
  return (
    <div style={{ marginBottom: '4px' }}>
      {!collapsed && (
        <div style={{
          fontSize: '0.6875rem',
          fontWeight: 600,
          color: 'var(--color-text-disabled)',
          textTransform: 'uppercase',
          letterSpacing: '0.07em',
          padding: '6px 10px 3px',
        }}>
          {label}
        </div>
      )}
      {sessions.map((s) => (
        <SessionItem key={s.id} session={s} isActive={s.id === activeId} collapsed={collapsed} />
      ))}
    </div>
  );
}

// ============================================================
// Session List
// ============================================================
export function SessionList({ collapsed }: { collapsed: boolean }) {
  const { sessions, isLoading } = useSessions();
  const { sessionId: activeId } = useParams();
  const { searchQuery } = useSessionStore();


  const filtered = searchQuery
    ? sessions.filter((s) => s.title.toLowerCase().includes(searchQuery.toLowerCase()))
    : sessions;

  const now = new Date();
  const todaySessions = filtered.filter((s) => {
    const d = new Date(s.updated_at);
    return now.getTime() - d.getTime() < 86400000;
  });
  const yesterdaySessions = filtered.filter((s) => {
    const d = new Date(s.updated_at);
    const diff = now.getTime() - d.getTime();
    return diff >= 86400000 && diff < 172800000;
  });
  const olderSessions = filtered.filter((s) => {
    const d = new Date(s.updated_at);
    return now.getTime() - d.getTime() >= 172800000;
  });

  if (isLoading) {
    return (
      <div style={{ padding: '8px 10px', display: 'flex', flexDirection: 'column', gap: 6 }}>
        {[...Array(5)].map((_, i) => (
          <div key={i} className="skeleton" style={{ height: 32, borderRadius: 8 }} />
        ))}
      </div>
    );
  }

  return (
    <div style={{ padding: '4px 8px', overflowY: 'auto', flex: 1 }}>
      {filtered.length === 0 ? (
        <div style={{ padding: '20px 8px', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: '0.8125rem' }}>
          {searchQuery ? 'No chats found' : 'No chats yet'}
        </div>
      ) : (
        <>
          <SessionGroup label="Today" sessions={todaySessions} activeId={activeId} collapsed={collapsed} />
          <SessionGroup label="Yesterday" sessions={yesterdaySessions} activeId={activeId} collapsed={collapsed} />
          <SessionGroup label="Older" sessions={olderSessions} activeId={activeId} collapsed={collapsed} />
        </>
      )}
    </div>
  );
}
