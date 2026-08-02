import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sun, Moon, Sunset, Trees, ChevronDown, Monitor } from 'lucide-react';
import { useThemeStore, type Theme } from '@/store/themeStore';

const themes: { id: Theme; label: string; icon: React.ReactNode; dot: string }[] = [
  { id: 'dark',     label: 'Dark',     icon: <Moon size={14} />,    dot: '#3b82f6' },
  { id: 'light',    label: 'Light',    icon: <Sun size={14} />,     dot: '#f59e0b' },
  { id: 'midnight', label: 'Midnight', icon: <Monitor size={14} />, dot: '#6097ff' },
  { id: 'forest',   label: 'Forest',   icon: <Trees size={14} />,   dot: '#4ade80' },
];

export function ThemeToggle() {
  const { theme, setTheme } = useThemeStore();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const current = themes.find((t) => t.id === theme) ?? themes[0];

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      <button
        onClick={() => setOpen((o) => !o)}
        title="Switch theme"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 5,
          background: 'var(--color-surface-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 8,
          padding: '5px 9px',
          cursor: 'pointer',
          color: 'var(--color-text-secondary)',
          fontSize: '0.775rem',
          fontWeight: 500,
          transition: 'all 0.15s ease',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-accent-border)'; e.currentTarget.style.color = 'var(--color-text-primary)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
      >
        {/* Color dot */}
        <span style={{
          display: 'inline-block',
          width: 8,
          height: 8,
          borderRadius: '50%',
          background: current.dot,
          flexShrink: 0,
        }} />
        <span style={{ color: 'var(--color-text-primary)' }}>{current.icon}</span>
        <span>{current.label}</span>
        <ChevronDown size={11} style={{ opacity: 0.6, transition: 'transform 0.2s', transform: open ? 'rotate(180deg)' : 'rotate(0deg)' }} />
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 6, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 6, scale: 0.96 }}
            transition={{ duration: 0.14 }}
            style={{
              position: 'absolute',
              bottom: 'calc(100% + 8px)',
              left: 0,
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 12,
              padding: 6,
              minWidth: 160,
              boxShadow: 'var(--shadow-lg)',
              zIndex: 200,
            }}
          >
            <div style={{ padding: '4px 8px 6px', fontSize: '0.7rem', fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              Theme
            </div>
            {themes.map((t) => {
              const isActive = t.id === theme;
              return (
                <button
                  key={t.id}
                  onClick={() => { setTheme(t.id); setOpen(false); }}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    width: '100%',
                    background: isActive ? 'var(--color-accent-subtle)' : 'transparent',
                    border: 'none',
                    borderRadius: 8,
                    padding: '8px 10px',
                    cursor: 'pointer',
                    color: isActive ? 'var(--color-accent)' : 'var(--color-text-secondary)',
                    fontSize: '0.825rem',
                    fontWeight: isActive ? 600 : 400,
                    textAlign: 'left',
                    transition: 'all 0.12s ease',
                  }}
                  onMouseEnter={(e) => { if (!isActive) { e.currentTarget.style.background = 'var(--color-surface-hover)'; e.currentTarget.style.color = 'var(--color-text-primary)'; }}}
                  onMouseLeave={(e) => { if (!isActive) { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}}
                >
                  <span style={{
                    display: 'inline-block',
                    width: 10,
                    height: 10,
                    borderRadius: '50%',
                    background: t.dot,
                    flexShrink: 0,
                    boxShadow: isActive ? `0 0 6px ${t.dot}99` : 'none',
                  }} />
                  <span style={{ color: 'var(--color-text-primary)', opacity: isActive ? 1 : 0.7 }}>{t.icon}</span>
                  <span>{t.label}</span>
                  {isActive && (
                    <span style={{ marginLeft: 'auto', width: 6, height: 6, borderRadius: '50%', background: 'var(--color-accent)' }} />
                  )}
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
