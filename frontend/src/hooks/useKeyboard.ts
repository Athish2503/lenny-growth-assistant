import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSessions } from './useSessions';
import { useUIStore } from '@/store/uiStore';

export function useKeyboard() {
  const navigate = useNavigate();
  const { createSession } = useSessions();
  const { toggleSidebar, toggleInspector } = useUIStore();

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const ctrl = e.ctrlKey || e.metaKey;

      // Ctrl/Cmd + K — New chat
      if (ctrl && e.key === 'k') {
        e.preventDefault();
        createSession();
      }
      // Ctrl/Cmd + \ — Toggle sidebar
      if (ctrl && e.key === '\\') {
        e.preventDefault();
        toggleSidebar();
      }
      // Ctrl/Cmd + I — Toggle inspector
      if (ctrl && e.key === 'i') {
        e.preventDefault();
        toggleInspector();
      }
      // Ctrl/Cmd + , — Settings
      if (ctrl && e.key === ',') {
        e.preventDefault();
        navigate('/settings');
      }
      // Escape — close modals handled per-component
    };

    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [navigate, createSession, toggleSidebar, toggleInspector]);
}
