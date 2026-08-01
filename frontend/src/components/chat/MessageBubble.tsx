import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { useState } from 'react';
import { Copy, Check, RotateCcw, ExternalLink } from 'lucide-react';
import type { Message } from '@/types';
import { CitationChip } from './CitationChip';

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

function AssistantMessage({ message, isLast }: { message: Message; isLast?: boolean }) {
  const hasRetrieval = message.metadata?.retrieval_performed;
  const citations = message.citations || message.metadata?.sources || [];

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
            <span className={`badge ${message.metadata.intent === 'essay' ? 'badge-blue' : 'badge-gray'}`}>
              {message.metadata.intent === 'qa' && '🔍 Researched'}
              {message.metadata.intent === 'essay' && '✍️ Essay'}
              {message.metadata.intent === 'artifact' && '📄 Artifact'}
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
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}

        {/* Citations */}
        {citations.length > 0 && !message.is_streaming && (
          <div style={{ marginTop: 12, display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {citations.map((cite) => (
              <CitationChip key={cite.id} citation={cite} />
            ))}
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
