import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { useState } from 'react';
import { Copy, Check, ExternalLink, FileText, Database, Search, PenTool, FileCode } from 'lucide-react';
import type { Message } from '@/types';
import { CitationChip } from './CitationChip';
import { useArtifactStore } from '@/store/artifactStore';

interface MessageBubbleProps {
  message: Message;
  isLast?: boolean;
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  const handleCopy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button className="btn-icon" onClick={handleCopy} title="Copy" aria-label="Copy message">
      {copied ? <Check size={14} style={{ color: 'var(--color-success)' }} /> : <Copy size={14} />}
    </button>
  );
}

function UserMessage({ message }: { message: Message }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'flex-end', padding: '0 0 4px' }}>
      <div
        style={{
          maxWidth: '70%',
          background: 'var(--color-accent)',
          color: '#fff',
          borderRadius: '16px 16px 4px 16px',
          padding: '10px 16px',
          fontSize: '0.9375rem',
          lineHeight: 1.6,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}
      >
        {message.content}
      </div>
    </div>
  );
}

// ============================================================
// Compact Inline Citation Chip Component
// ============================================================
interface CitationChipInlineProps {
  citation: any;
  index: number;
}

function CitationChipInline({ citation, index }: CitationChipInlineProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const guestName = citation.guest || (citation.title ? citation.title.replace(/^Episode with /i, '') : `Source ${index}`);
  const displayTitle = citation.episode_title || citation.title || "Lenny's Growth Podcast";
  const scorePct = Math.round((citation.relevance_score > 1 ? citation.relevance_score / 100 : citation.relevance_score) * 100);

  let ytUrl = citation.youtube_url;
  if (!ytUrl && citation.source && citation.source.startsWith('http')) {
    ytUrl = citation.source;
  }
  if (!ytUrl) {
    ytUrl = `https://www.youtube.com/results?search_query=Lenny+Podcast+${encodeURIComponent(guestName)}`;
  }

  return (
    <span
      style={{
        position: 'relative',
        display: 'inline-flex',
        alignItems: 'center',
        margin: '0 3px',
        verticalAlign: 'middle',
      }}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <a
        href={ytUrl}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 4,
          background: 'rgba(59, 130, 246, 0.08)',
          color: 'var(--color-accent)',
          border: '1px solid rgba(59, 130, 246, 0.22)',
          borderRadius: 6,
          padding: '1px 6px',
          fontSize: '0.725rem',
          fontWeight: 600,
          textDecoration: 'none',
          cursor: 'pointer',
          transition: 'all 0.15s ease',
        }}
      >
        <span style={{ fontSize: '0.62rem', opacity: 0.8 }}>⚡</span>
        <span>{guestName.length > 20 ? guestName.slice(0, 20) + '…' : guestName}</span>
      </a>

      {/* Mini Tooltip */}
      <AnimatePresence>
        {showTooltip && (
          <motion.span
            initial={{ opacity: 0, y: 4, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.95 }}
            transition={{ duration: 0.1 }}
            style={{
              position: 'absolute',
              bottom: 'calc(100% + 6px)',
              left: '50%',
              transform: 'translateX(-50%)',
              background: '#121215',
              border: '1px solid var(--color-border)',
              borderRadius: 8,
              padding: '8px 10px',
              width: 250,
              boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
              zIndex: 100,
              pointerEvents: 'none',
              display: 'block',
              textAlign: 'left',
              lineHeight: 1.4,
              fontSize: '0.75rem',
            }}
          >
            <strong style={{ display: 'block', color: '#fff', marginBottom: 2 }}>{displayTitle}</strong>
            <span style={{ display: 'block', color: 'var(--color-accent)', fontSize: '0.7rem', fontWeight: 600, marginBottom: 4 }}>
              Guest: {guestName} · {scorePct}% match
            </span>
            <span style={{ display: 'block', color: '#a1a1aa', fontStyle: 'italic', fontSize: '0.7rem' }}>
              "{citation.snippet || (citation.content ? citation.content.slice(0, 80) + '...' : '')}"
            </span>
          </motion.span>
        )}
      </AnimatePresence>
    </span>
  );
}

function AssistantMessage({ message, isLast }: { message: Message; isLast?: boolean }) {
  const hasRetrieval = message.metadata?.retrieval_performed;
  const citations = message.citations || message.metadata?.sources || [];

  // Parse inline reference formats like [Source 1], [Source 2], etc. to use custom markup links
  const processContent = (content: string) => {
    let result = content;
    
    // Replace standard citation markers with special custom markdown link hash to be captured by link renderer
    result = result.replace(/\[Source\s*(\d+)\]/gi, (match, num) => {
      return `[${match}](#citation-${num})`;
    });

    return result;
  };

  const processedContent = processContent(message.content);

  return (
    <div style={{ display: 'flex', gap: 12, padding: '0 0 8px', alignItems: 'flex-start' }}>
      {/* Avatar */}
      <div style={{
        width: 28,
        height: 28,
        borderRadius: 7,
        background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        marginTop: 4,
      }}>
        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: '#fff' }}>L</span>
      </div>

      <div style={{ flex: 1, minWidth: 0 }}>
        {/* Intent badge */}
        {message.metadata?.intent && (
          <div style={{ marginBottom: 8 }}>
            <span className={`badge ${message.metadata.intent === 'essay' ? 'badge-blue' : 'badge-gray'}`} style={{ display: 'inline-flex', alignItems: 'center', gap: 5 }}>
              {message.metadata.intent === 'qa' && <><Search size={11} /> Researched</>}
              {message.metadata.intent === 'essay' && <><PenTool size={11} /> Essay</>}
              {message.metadata.intent === 'artifact' && <><FileCode size={11} /> Artifact</>}
            </span>
          </div>
        )}

        {/* Message content */}
        {message.is_streaming ? (
          <div className="prose" style={{ fontSize: '0.9375rem' }}>
            <span style={{ whiteSpace: 'pre-wrap' }}>{message.content}</span>
            <span className="cursor-blink" />
          </div>
        ) : (
          <div className="prose">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
              components={{
                code({ className, children, ...props }) {
                  const match = /language-(\w+)/.exec(className || '');
                  const isBlock = className?.includes('language-');
                  if (isBlock) {
                    return (
                      <div className="code-block-wrapper">
                        <div className="code-block-header">
                          <span className="code-block-lang">{match?.[1] || 'code'}</span>
                          <CopyButton text={String(children)} />
                        </div>
                        <pre style={{
                          background: '#0d0d0f',
                          border: '1px solid var(--color-border)',
                          borderTop: 'none',
                          borderRadius: '0 0 var(--radius-md) var(--radius-md)',
                          padding: '14px 16px',
                          overflow: 'auto',
                          margin: 0,
                        }}>
                          <code className={className} {...props}>{children}</code>
                        </pre>
                      </div>
                    );
                  }
                  return <code className={className} {...props}>{children}</code>;
                },
                // Intercept custom citation links and render inline guest pills instead
                a({ href, children, ...props }) {
                  if (href && href.startsWith('#citation-')) {
                    const num = parseInt(href.replace('#citation-', ''), 10);
                    const citation = citations[num - 1];
                    if (citation) {
                      return <CitationChipInline citation={citation} index={num} />;
                    }
                  }
                  return <a href={href} target="_blank" rel="noopener noreferrer" {...props}>{children}</a>;
                }
              }}
            >
              {processedContent}
            </ReactMarkdown>
          </div>
        )}

        {/* Artifact Card */}
        {message.metadata?.artifact && !message.is_streaming && (
          <div
            onClick={() => {
              const art = message.metadata?.artifact;
              if (art) {
                useArtifactStore.getState().setCurrentArtifact(art);
                useArtifactStore.getState().setActiveTab('preview');
              }
            }}
            style={{
              marginTop: 12,
              padding: '10px 14px',
              borderRadius: 8,
              background: 'var(--color-surface-elevated)',
              border: '1px solid var(--color-border)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
            className="artifact-card-hover"
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
              <div style={{
                width: 32,
                height: 32,
                borderRadius: 6,
                background: 'rgba(59, 130, 246, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--color-accent)',
              }}>
                <FileText size={18} />
              </div>
              <div>
                <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--color-text-primary)' }}>
                  {message.metadata.artifact.title || 'Generated Artifact'}
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                  Click to open side-by-side artifact viewer
                </div>
              </div>
            </div>
            <ExternalLink size={16} style={{ color: 'var(--color-accent)' }} />
          </div>
        )}

        {/* Knowledge Base Citations Footer */}
        {citations.length > 0 && !message.is_streaming && (
          <div style={{
            marginTop: 14,
            padding: '10px 14px',
            borderRadius: 12,
            background: 'rgba(59, 130, 246, 0.04)',
            border: '1px solid rgba(59, 130, 246, 0.15)',
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-accent)' }}>
              <Database size={13} />
              <span>✨ Verified Growth Insights from Lenny's Guests ({citations.length})</span>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {citations.map((cite) => (
                <CitationChip key={cite.id} citation={cite} />
              ))}
            </div>
          </div>
        )}

        {/* Actions row */}
        {!message.is_streaming && isLast && (
          <div style={{ marginTop: 10, display: 'flex', gap: 4, alignItems: 'center' }}>
            <CopyButton text={message.content} />
            {hasRetrieval && (
              <div style={{ marginLeft: 8, fontSize: '0.75rem', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: 4 }}>
                <span>
                  {message.metadata?.retrieval_time_ms}ms
                </span>
                {message.metadata?.confidence_score && (
                  <span>· {Math.round(message.metadata.confidence_score * 100)}% confidence</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export function MessageBubble({ message, isLast }: MessageBubbleProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: 'easeOut' }}
    >
      {message.role === 'user' ? (
        <UserMessage message={message} />
      ) : (
        <AssistantMessage message={message} isLast={isLast} />
      )}
    </motion.div>
  );
}
