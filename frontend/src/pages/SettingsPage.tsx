import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ChevronLeft, Palette, Brain, Cpu, Terminal, Info, Thermometer } from 'lucide-react';
import { useSettings } from '@/hooks/useSettings';

function SectionHeader({ icon, title }: { icon: React.ReactNode; title: string }) {
  return (
    <div className="settings-section-header">
      <div style={{ color: 'var(--color-accent)' }}>{icon}</div>
      <span className="settings-section-title">{title}</span>
    </div>
  );
}

export function SettingsPage() {
  const navigate = useNavigate();
  const { settings, saveSettings, isSaving } = useSettings();

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{
        padding: '14px 24px',
        borderBottom: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        flexShrink: 0,
      }}>
        <button
          className="btn-ghost"
          onClick={() => navigate(-1)}
          style={{ padding: '6px 8px', display: 'flex', alignItems: 'center', gap: 6 }}
        >
          <ChevronLeft size={16} />
          Back
        </button>
        <div style={{ width: 1, height: 20, background: 'var(--color-border)' }} />
        <h1 style={{ fontSize: '1.0625rem', fontWeight: 600, margin: 0 }}>Settings</h1>
        {isSaving && (
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Saving…</span>
        )}
      </div>

      <div style={{ flex: 1, overflow: 'auto', padding: '24px' }}>
        <div style={{ maxWidth: 680, margin: '0 auto', display: 'flex', flexDirection: 'column', gap: 0 }}>

          {/* Appearance */}
          <motion.div
            className="settings-section"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0 }}
          >
            <SectionHeader icon={<Palette size={16} />} title="Appearance" />
            <div className="settings-row">
              <div>
                <div className="settings-row-label">Theme</div>
                <div className="settings-row-description">Choose your preferred color theme</div>
              </div>
              <select
                className="form-select"
                value={settings.theme}
                onChange={(e) => saveSettings({ theme: e.target.value as 'dark' | 'light' | 'system' })}
              >
                <option value="dark">Dark</option>
                <option value="light">Light</option>
                <option value="system">System</option>
              </select>
            </div>
            <div className="settings-row">
              <div>
                <div className="settings-row-label">Stream Responses</div>
                <div className="settings-row-description">Show AI responses as they are generated</div>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={settings.stream_responses}
                  onChange={(e) => saveSettings({ stream_responses: e.target.checked })}
                />
                <span className="toggle-slider" />
              </label>
            </div>
          </motion.div>

          {/* Model Provider */}
          <motion.div
            className="settings-section"
            style={{ marginTop: 16 }}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.05 }}
          >
            <SectionHeader icon={<Brain size={16} />} title="Model Provider" />
            <div className="settings-row">
              <div>
                <div className="settings-row-label">Provider</div>
                <div className="settings-row-description">LLM provider for generating responses</div>
              </div>
              <select
                className="form-select"
                value={settings.provider}
                onChange={(e) => saveSettings({ provider: e.target.value as 'anthropic' | 'ollama' | 'openai' })}
              >
                <option value="anthropic">Anthropic (Claude)</option>
                <option value="ollama">Ollama (Local)</option>
                <option value="openai">OpenAI</option>
              </select>
            </div>
            <div className="settings-row">
              <div>
                <div className="settings-row-label">Model</div>
                <div className="settings-row-description">Specific model to use for generation</div>
              </div>
              <select
                className="form-select"
                value={settings.model}
                onChange={(e) => saveSettings({ model: e.target.value })}
              >
                {settings.provider === 'anthropic' && (
                  <>
                    <option value="claude-3-5-sonnet-20241022">claude-3-5-sonnet</option>
                    <option value="claude-3-opus-20240229">claude-3-opus</option>
                    <option value="claude-3-haiku-20240307">claude-3-haiku</option>
                  </>
                )}
                {settings.provider === 'ollama' && (
                  <>
                    <option value="llama3.2">llama3.2</option>
                    <option value="mistral">mistral</option>
                    <option value="gemma2">gemma2</option>
                    <option value="qwen2.5">qwen2.5</option>
                  </>
                )}
                {settings.provider === 'openai' && (
                  <>
                    <option value="gpt-4o">gpt-4o</option>
                    <option value="gpt-4o-mini">gpt-4o-mini</option>
                    <option value="gpt-4-turbo">gpt-4-turbo</option>
                  </>
                )}
              </select>
            </div>
          </motion.div>

          {/* Embedding Model */}
          <motion.div
            className="settings-section"
            style={{ marginTop: 16 }}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <SectionHeader icon={<Cpu size={16} />} title="Embedding Model" />
            <div className="settings-row">
              <div>
                <div className="settings-row-label">Embedding Model</div>
                <div className="settings-row-description">Used for semantic search over transcripts</div>
              </div>
              <select
                className="form-select"
                value={settings.embedding_model}
                onChange={(e) => saveSettings({ embedding_model: e.target.value })}
              >
                <option value="text-embedding-3-small">text-embedding-3-small</option>
                <option value="text-embedding-3-large">text-embedding-3-large</option>
                <option value="nomic-embed-text">nomic-embed-text (Ollama)</option>
              </select>
            </div>
          </motion.div>

          {/* Generation */}
          <motion.div
            className="settings-section"
            style={{ marginTop: 16 }}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
          >
            <SectionHeader icon={<Thermometer size={16} />} title="Generation" />
            <div className="settings-row">
              <div>
                <div className="settings-row-label">Temperature</div>
                <div className="settings-row-description">Higher = more creative, lower = more precise</div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={settings.temperature}
                  onChange={(e) => saveSettings({ temperature: parseFloat(e.target.value) })}
                  style={{ width: 100, accentColor: 'var(--color-accent)' }}
                />
                <span style={{
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  color: 'var(--color-text-primary)',
                  minWidth: 30,
                  textAlign: 'right',
                }}>
                  {settings.temperature.toFixed(2)}
                </span>
              </div>
            </div>
            <div className="settings-row">
              <div>
                <div className="settings-row-label">Max Tokens</div>
                <div className="settings-row-description">Maximum length of generated responses</div>
              </div>
              <select
                className="form-select"
                value={settings.max_tokens}
                onChange={(e) => saveSettings({ max_tokens: parseInt(e.target.value) })}
              >
                <option value={1024}>1,024</option>
                <option value={2048}>2,048</option>
                <option value={4096}>4,096</option>
                <option value={8192}>8,192</option>
              </select>
            </div>
          </motion.div>

          {/* System Prompt */}
          <motion.div
            className="settings-section"
            style={{ marginTop: 16 }}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <SectionHeader icon={<Terminal size={16} />} title="System Prompt" />
            <div style={{ padding: '16px 20px' }}>
              <div className="settings-row-description" style={{ marginBottom: 10 }}>
                Customize the assistant's persona and instructions
              </div>
              <textarea
                className="form-input"
                value={settings.system_prompt}
                onChange={(e) => saveSettings({ system_prompt: e.target.value })}
                rows={5}
                style={{ width: '100%', resize: 'vertical', lineHeight: 1.6 }}
              />
            </div>
          </motion.div>

          {/* About */}
          <motion.div
            className="settings-section"
            style={{ marginTop: 16 }}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.25 }}
          >
            <SectionHeader icon={<Info size={16} />} title="About" />
            <div className="settings-row">
              <div className="settings-row-label">Application</div>
              <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Lenny Growth Assistant</span>
            </div>
            <div className="settings-row">
              <div className="settings-row-label">Version</div>
              <span className="badge badge-gray">v0.1.0 — Beta</span>
            </div>
            <div className="settings-row">
              <div className="settings-row-label">Backend</div>
              <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>FastAPI · SQLAlchemy · ChromaDB</span>
            </div>
            <div className="settings-row" style={{ borderBottom: 'none' }}>
              <div className="settings-row-label">Mode</div>
              <span className="badge badge-green">Mock Data Active</span>
            </div>
          </motion.div>

        </div>
      </div>
    </div>
  );
}
