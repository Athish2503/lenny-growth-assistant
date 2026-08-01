import { motion, AnimatePresence } from 'framer-motion';
import { X, ChevronRight, Brain, Clock, Database, TrendingUp, Cpu } from 'lucide-react';
import { useUIStore } from '@/store/uiStore';
import { useChatStore } from '@/store/chatStore';
import { useArtifactStore } from '@/store/artifactStore';
import { useSessionStore } from '@/store/sessionStore';
import { mockArtifacts } from '@/api/mock/mockData';

function ConfidenceBar({ score }: { score: number }) {
  const pct = Math.round(score * 100);
  const color = pct >= 85 ? '#22c55e' : pct >= 65 ? '#f59e0b' : '#ef4444';
  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)' }}>Confidence</span>
        <span style={{ fontSize: '0.875rem', fontWeight: 700, color }}>{pct}%</span>
      </div>
      <div className="confidence-bar">
        <motion.div
          className="confidence-fill"
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
          style={{ background: `linear-gradient(90deg, ${color}, #3b82f6)` }}
        />
      </div>
    </div>
  );
}

export function ResearchInspector() {
  const { inspectorOpen, toggleInspector } = useUIStore();
  const { lastRetrievalResult } = useChatStore();
  const { setCurrentArtifact, setActiveTab } = useArtifactStore();
  const { activeSessionId } = useSessionStore();

  const result = lastRetrievalResult;
  const sessionArtifacts = activeSessionId
    ? mockArtifacts.filter((a) => a.session_id === activeSessionId)
    : [];

  return (
    <AnimatePresence mode="wait">
      {inspectorOpen && (
        <motion.div
          initial={{ width: 0, opacity: 0 }}
          animate={{ width: 340, opacity: 1 }}
          exit={{ width: 0, opacity: 0 }}
          transition={{ duration: 0.22, ease: [0.4, 0, 0.2, 1] }}
          style={{
            flexShrink: 0,
            display: 'flex',
            flexDirection: 'column',
            background: 'var(--color-surface)',
            borderLeft: '1px solid var(--color-border)',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--color-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexShrink: 0,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <Brain size={15} style={{ color: 'var(--color-accent)' }} />
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                Research Inspector
              </span>
            </div>
            <button className="btn-icon" onClick={toggleInspector} title="Close inspector (⌘I)">
              <X size={14} />
            </button>
          </div>

          {/* Scrollable content */}
          <div style={{ flex: 1, overflowY: 'auto' }}>
            {!result ? (
              <div style={{ padding: 20, textAlign: 'center' }}>
                <div style={{
                  width: 48,
                  height: 48,
                  borderRadius: 12,
                  background: 'var(--color-surface-elevated)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 12px',
                }}>
                  <Brain size={22} style={{ color: 'var(--color-text-muted)' }} />
                </div>
                <p style={{ fontSize: '0.8125rem', color: 'var(--color-text-muted)', lineHeight: 1.6 }}>
                  Ask a question to see research details, sources, and retrieved chunks here.
                </p>
              </div>
            ) : (
              <>
                {/* Model Info */}
                <div className="inspector-section">
                  <div className="inspector-label">Active Model</div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div style={{
                      width: 32,
                      height: 32,
                      borderRadius: 7,
                      background: 'linear-gradient(135deg, #f97316, #ec4899)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}>
                      <Cpu size={15} color="#fff" />
                    </div>
                    <div>
                      <div style={{ fontSize: '0.8125rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                        {result.model}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>
                        {result.provider}
                        {result.tokens_used && ` · ${result.tokens_used.toLocaleString()} tokens`}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Retrieval Stats */}
                <div className="inspector-section">
                  <div className="inspector-label">Retrieval Stats</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    <ConfidenceBar score={result.confidence_score} />
                    <div style={{ display: 'flex', gap: 8 }}>
                      <div style={{
                        flex: 1,
                        background: 'var(--color-surface-elevated)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 8,
                        padding: '8px 10px',
                        display: 'flex',
                        gap: 8,
                        alignItems: 'center',
                      }}>
                        <Clock size={13} style={{ color: 'var(--color-text-muted)' }} />
                        <div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Time</div>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                            {result.retrieval_time_ms}ms
                          </div>
                        </div>
                      </div>
                      <div style={{
                        flex: 1,
                        background: 'var(--color-surface-elevated)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 8,
                        padding: '8px 10px',
                        display: 'flex',
                        gap: 8,
                        alignItems: 'center',
                      }}>
                        <Database size={13} style={{ color: 'var(--color-text-muted)' }} />
                        <div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Chunks</div>
                          <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                            {result.chunks.length || result.sources.length}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Sources */}
                {result.sources.length > 0 && (
                  <div className="inspector-section">
                    <div className="inspector-label">Sources Used</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {result.sources.map((source, i) => (
                        <div
                          key={source.id}
                          style={{
                            background: 'var(--color-surface-elevated)',
                            border: '1px solid var(--color-border)',
                            borderRadius: 8,
                            padding: '10px 12px',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 4 }}>
                            <div style={{
                              fontSize: '0.8rem',
                              fontWeight: 600,
                              color: 'var(--color-text-primary)',
                              lineHeight: 1.3,
                              flex: 1,
                              marginRight: 8,
                            }}>
                              {i + 1}. {source.title}
                            </div>
                            <span style={{
                              fontSize: '0.7rem',
                              fontWeight: 700,
                              color: 'var(--color-success)',
                              flexShrink: 0,
                            }}>
                              {Math.round(source.relevance_score * 100)}%
                            </span>
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 6 }}>
                            {source.source}
                          </div>
                          <div style={{
                            fontSize: '0.78rem',
                            color: 'var(--color-text-secondary)',
                            lineHeight: 1.5,
                            fontStyle: 'italic',
                            borderLeft: '2px solid var(--color-accent)',
                            paddingLeft: 8,
                          }}>
                            "{source.snippet.slice(0, 100)}…"
                          </div>
                          <div style={{ marginTop: 6 }}>
                            <div
                              style={{
                                height: 3,
                                background: 'var(--color-surface)',
                                borderRadius: 9999,
                                overflow: 'hidden',
                              }}
                            >
                              <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${source.relevance_score * 100}%` }}
                                transition={{ duration: 0.6, delay: i * 0.1 }}
                                style={{ height: '100%', background: 'var(--color-accent)', borderRadius: 9999 }}
                              />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Retrieved Chunks */}
                {result.chunks.length > 0 && (
                  <div className="inspector-section">
                    <div className="inspector-label">Retrieved Chunks</div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {result.chunks.map((chunk) => (
                        <div
                          key={chunk.id}
                          style={{
                            background: 'var(--color-surface-elevated)',
                            border: '1px solid var(--color-border)',
                            borderRadius: 8,
                            padding: '10px 12px',
                          }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                              {chunk.source.split('—').pop()?.trim() || chunk.source}
                            </span>
                            <span style={{ fontSize: '0.7rem', color: 'var(--color-accent)', fontWeight: 600 }}>
                              {Math.round(chunk.score * 100)}%
                            </span>
                          </div>
                          <p style={{ fontSize: '0.78rem', color: 'var(--color-text-secondary)', lineHeight: 1.5, margin: 0 }}>
                            {chunk.content}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Artifacts Section */}
            {sessionArtifacts.length > 0 && (
              <div className="inspector-section">
                <div className="inspector-label">Artifacts</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {sessionArtifacts.map((artifact) => (
                    <button
                      key={artifact.id}
                      onClick={() => {
                        setCurrentArtifact(artifact);
                        setActiveTab('preview');
                      }}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 10,
                        background: 'var(--color-surface-elevated)',
                        border: '1px solid var(--color-border)',
                        borderRadius: 8,
                        padding: '10px 12px',
                        cursor: 'pointer',
                        textAlign: 'left',
                        transition: 'border-color 0.15s',
                        width: '100%',
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.borderColor = 'var(--color-accent-border)')}
                      onMouseLeave={(e) => (e.currentTarget.style.borderColor = 'var(--color-border)')}
                    >
                      <div style={{
                        fontSize: '1rem',
                        flexShrink: 0,
                      }}>
                        {artifact.artifact_type === 'markdown' ? '📄' : artifact.artifact_type === 'html' ? '🌐' : '🎨'}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {artifact.title}
                        </div>
                        <div style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                          {artifact.artifact_type.toUpperCase()} · v{artifact.version}
                        </div>
                      </div>
                      <ChevronRight size={13} style={{ color: 'var(--color-text-muted)', flexShrink: 0 }} />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
