import React, { useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeHighlight from 'rehype-highlight';
import mermaid from 'mermaid';
import { Info, Lightbulb, Key, AlertTriangle, AlertOctagon } from 'lucide-react';
import 'katex/dist/katex.min.css';
import type { Artifact } from '@/types';

interface ArtifactMarkdownViewerProps {
  artifact: Artifact;
}

// Inline Mermaid Diagram Component
function MermaidDiagram({ code }: { code: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const idRef = useRef(`mermaid-${Math.random().toString(36).substr(2, 9)}`);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      securityLevel: 'loose',
      fontFamily: 'Inter, sans-serif',
    });

    if (containerRef.current) {
      containerRef.current.innerHTML = '';
      mermaid.render(idRef.current, code.trim()).then(({ svg }) => {
        if (containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      }).catch((err) => {
        if (containerRef.current) {
          containerRef.current.innerHTML = `<pre class="text-xs text-red-400 p-3 bg-red-950/40 rounded">Mermaid Render Error: ${err.message || String(err)}</pre>`;
        }
      });
    }
  }, [code]);

  return (
    <div
      ref={containerRef}
      className="my-6 p-4 bg-zinc-900/60 border border-zinc-800 rounded-xl overflow-x-auto flex justify-center items-center shadow-lg"
    />
  );
}

// Custom Callout Box Component
function CalloutBlock({ type, children }: { type: string; children: React.ReactNode }) {
  const styles: Record<string, { bg: string; border: string; text: string; icon: React.ReactNode; title: string }> = {
    NOTE: { bg: 'rgba(59, 130, 246, 0.08)', border: 'rgba(59, 130, 246, 0.3)', text: '#60a5fa', icon: <Info size={14} />, title: 'Note' },
    TIP: { bg: 'rgba(16, 185, 129, 0.08)', border: 'rgba(16, 185, 129, 0.3)', text: '#34d399', icon: <Lightbulb size={14} />, title: 'Tip' },
    IMPORTANT: { bg: 'rgba(168, 85, 247, 0.08)', border: 'rgba(168, 85, 247, 0.3)', text: '#c084fc', icon: <Key size={14} />, title: 'Important' },
    WARNING: { bg: 'rgba(245, 158, 11, 0.08)', border: 'rgba(245, 158, 11, 0.3)', text: '#fbbf24', icon: <AlertTriangle size={14} />, title: 'Warning' },
    CAUTION: { bg: 'rgba(239, 68, 68, 0.08)', border: 'rgba(239, 68, 68, 0.3)', text: '#f87171', icon: <AlertOctagon size={14} />, title: 'Caution' },
  };

  const cfg = styles[type.toUpperCase()] || styles.NOTE;

  return (
    <div style={{
      background: cfg.bg,
      borderLeft: `4px solid ${cfg.border}`,
      borderRadius: '0 8px 8px 0',
      padding: '12px 16px',
      margin: '16px 0',
      color: 'var(--color-text-primary)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontWeight: 600, fontSize: '0.85rem', color: cfg.text, marginBottom: 4 }}>
        <span>{cfg.icon}</span>
        <span>{cfg.title}</span>
      </div>
      <div className="text-sm leading-relaxed">{children}</div>
    </div>
  );
}

export const ArtifactMarkdownViewer = React.memo(function ArtifactMarkdownViewer({
  artifact,
}: ArtifactMarkdownViewerProps) {
  return (
    <div
      className="prose prose-invert max-w-none"
      style={{
        padding: '24px 32px',
        color: 'var(--color-text-primary)',
        lineHeight: 1.7,
        fontSize: '0.9375rem',
      }}
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex, rehypeHighlight]}
        components={{
          code({ className, children, ...props }) {
            const match = /language-(\w+)/.exec(className || '');
            const language = match ? match[1] : '';
            const codeString = String(children).replace(/\n$/, '');

            if (language === 'mermaid') {
              return <MermaidDiagram code={codeString} />;
            }

            return (
              <code className={className} {...props}>
                {children}
              </code>
            );
          },
          blockquote({ children }) {
            // Check for GFM alert callout pattern > [!NOTE]
            const childArray = React.Children.toArray(children);
            const firstChild = childArray[0];

            if (React.isValidElement<{ children?: React.ReactNode }>(firstChild) && firstChild.props.children) {
              const inner = firstChild.props.children;
              const textContent = String(Array.isArray(inner) ? inner[0] : inner);

              const alertMatch = textContent.match(/^\[\!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]/i);
              if (alertMatch) {
                const calloutType = alertMatch[1];
                const cleanText = textContent.replace(/^\[\!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]/i, '').trim();
                const cleanFirstChild = React.cloneElement(firstChild, {}, cleanText);
                const remainingChildren = childArray.slice(1);
                return (
                  <CalloutBlock type={calloutType}>
                    {cleanFirstChild}
                    {remainingChildren}
                  </CalloutBlock>
                );
              }
            }

            return (
              <blockquote style={{
                borderLeft: '3px solid var(--color-accent)',
                paddingLeft: 16,
                margin: '16px 0',
                color: 'var(--color-text-muted)',
                fontStyle: 'italic',
              }}>
                {children}
              </blockquote>
            );
          },
          table({ children }) {
            return (
              <div style={{ overflowX: 'auto', margin: '20px 0' }}>
                <table style={{
                  width: '100%',
                  borderCollapse: 'collapse',
                  fontSize: '0.875rem',
                  border: '1px solid var(--color-border)',
                  borderRadius: 8,
                  overflow: 'hidden',
                }}>
                  {children}
                </table>
              </div>
            );
          },
          th({ children }) {
            return (
              <th style={{
                background: 'var(--color-surface-elevated)',
                borderBottom: '2px solid var(--color-border)',
                padding: '10px 14px',
                textAlign: 'left',
                fontWeight: 600,
                color: 'var(--color-text-primary)',
              }}>
                {children}
              </th>
            );
          },
          td({ children }) {
            return (
              <td style={{
                borderBottom: '1px solid var(--color-border-subtle)',
                padding: '10px 14px',
                color: 'var(--color-text-primary)',
              }}>
                {children}
              </td>
            );
          },
        }}
      >
        {artifact.content}
      </ReactMarkdown>
    </div>
  );
});
