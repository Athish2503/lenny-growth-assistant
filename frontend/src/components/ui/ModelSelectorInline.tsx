import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Cpu, ChevronDown, Check, Zap, Bot } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

const providerMeta: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  ollama:    { label: 'Ollama',    color: '#f97316', icon: <Bot size={11} /> },
  anthropic: { label: 'Anthropic', color: '#d97706', icon: <Zap size={11} /> },
  openai:    { label: 'OpenAI',    color: '#22c55e', icon: <Cpu size={11} /> },
};

function shortModelName(model: string) {
  // claude-3-5-sonnet-20240620 → Claude 3.5 Sonnet
  // gpt-4o-mini → GPT-4o Mini
  if (!model) return model;
  return model
    .replace(/-\d{8}$/, '')
    .split(/[-_]/)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

export function ModelSelectorInline() {
  const { settings, saveSettings, availableModels } = useSettings();
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const providers = Object.keys(providerMeta);
  const providerModels = availableModels?.[settings.provider] || [];
  const currentMeta = providerMeta[settings.provider] ?? { label: settings.provider, color: '#3b82f6', icon: <Cpu size={11} /> };

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      {/* Trigger pill */}
      <button
        id="model-selector-btn"
        onClick={() => setOpen((o) => !o)}
        title="Switch model"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 5,
          background: 'var(--color-surface-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 20,
          padding: '4px 10px 4px 8px',
          cursor: 'pointer',
          fontSize: '0.78rem',
          fontWeight: 500,
          color: 'var(--color-text-secondary)',
          transition: 'all 0.15s ease',
          whiteSpace: 'nowrap',
        }}
        onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-accent-border)'; e.currentTarget.style.color = 'var(--color-text-primary)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
      >
        {/* Provider dot */}
        <span style={{
          display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
          width: 16, height: 16, borderRadius: '50%',
          background: currentMeta.color + '22',
          color: currentMeta.color,
          flexShrink: 0,
        }}>
          {currentMeta.icon}
        </span>
        <span style={{ color: currentMeta.color, fontWeight: 600, fontSize: '0.74rem' }}>{currentMeta.label}</span>
        <span style={{ color: 'var(--color-border)', fontSize: '0.75rem' }}>·</span>
        <span style={{ color: 'var(--color-text-primary)', maxWidth: 120, overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {shortModelName(settings.model)}
        </span>
        <ChevronDown
          size={11}
          style={{
            opacity: 0.5,
            transition: 'transform 0.2s',
            transform: open ? 'rotate(180deg)' : 'rotate(0)',
          }}
        />
      </button>

      {/* Dropdown */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.97 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.97 }}
            transition={{ duration: 0.15 }}
            style={{
              position: 'absolute',
              bottom: 'calc(100% + 10px)',
              left: 0,
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 14,
              padding: 8,
              minWidth: 260,
              boxShadow: 'var(--shadow-lg)',
              zIndex: 300,
            }}
          >
            {providers.map((prov) => {
              const meta = providerMeta[prov];
              const models: string[] = availableModels?.[prov as keyof typeof availableModels] as string[] || [];
              const isCurrentProvider = prov === settings.provider;

              return (
                <div key={prov} style={{ marginBottom: 4 }}>
                  {/* Provider header */}
                  <div style={{
                    display: 'flex', alignItems: 'center', gap: 6,
                    padding: '5px 8px 3px',
                    fontSize: '0.7rem', fontWeight: 700,
                    color: meta.color,
                    textTransform: 'uppercase', letterSpacing: '0.08em',
                  }}>
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, color: meta.color }}>
                      {meta.icon}
                    </span>
                    {meta.label}
                  </div>

                  {/* Models */}
                  {models.map((model: string) => {
                    const isActive = isCurrentProvider && model === settings.model;
                    return (
                      <button
                        key={model}
                        onClick={() => {
                          saveSettings({ provider: prov as 'ollama' | 'anthropic' | 'openai', model: model });
                          setOpen(false);
                        }}
                        style={{
                          display: 'flex', alignItems: 'center', gap: 10,
                          width: '100%',
                          background: isActive ? 'var(--color-accent-subtle)' : 'transparent',
                          border: `1px solid ${isActive ? 'var(--color-accent-border)' : 'transparent'}`,
                          borderRadius: 8,
                          padding: '7px 10px',
                          cursor: 'pointer',
                          textAlign: 'left',
                          transition: 'all 0.12s ease',
                        }}
                        onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.background = 'var(--color-surface-hover)'; }}
                        onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.background = 'transparent'; }}
                      >
                        <span style={{
                          fontSize: '0.82rem',
                          fontWeight: isActive ? 600 : 400,
                          color: isActive ? 'var(--color-accent)' : 'var(--color-text-primary)',
                          flex: 1,
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}>
                          {shortModelName(model)}
                        </span>
                        <span style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', flexShrink: 0 }}>
                          {model.includes('mini') || model.includes('7b') ? 'Fast' : 'Capable'}
                        </span>
                        {isActive && <Check size={12} style={{ color: 'var(--color-accent)', flexShrink: 0 }} />}
                      </button>
                    );
                  })}
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
