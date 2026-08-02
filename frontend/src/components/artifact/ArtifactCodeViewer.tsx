import React, { useState } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check, WrapText } from 'lucide-react';
import type { Artifact } from '@/types';

interface ArtifactCodeViewerProps {
  artifact: Artifact;
}

export const ArtifactCodeViewer = React.memo(function ArtifactCodeViewer({
  artifact,
}: ArtifactCodeViewerProps) {
  const [copied, setCopied] = useState(false);
  const [wrapLines, setWrapLines] = useState(true);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lineCount = artifact.content.split('\n').length;
  const langMap: Record<string, string> = {
    markdown: 'markdown',
    html: 'html',
    css: 'css',
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', background: '#09090b' }}>
      {/* Sub toolbar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '8px 16px',
        background: '#121215',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        fontSize: '0.75rem',
        color: '#a1a1aa',
        flexShrink: 0,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <span style={{ fontWeight: 600, color: '#e4e4e7', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            {artifact.artifact_type}
          </span>
          <span>{lineCount} lines</span>
          <span>{new Blob([artifact.content]).size} bytes</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <button
            className="btn-icon"
            onClick={() => setWrapLines(!wrapLines)}
            title={wrapLines ? 'Disable word wrap' : 'Enable word wrap'}
            style={{ color: wrapLines ? '#818cf8' : undefined }}
          >
            <WrapText size={14} />
          </button>
          <button className="btn-icon" onClick={handleCopy} title="Copy code">
            {copied ? <Check size={14} style={{ color: '#34d399' }} /> : <Copy size={14} />}
          </button>
        </div>
      </div>

      {/* Syntax Highlighter */}
      <div style={{ flex: 1, overflow: 'auto', position: 'relative' }}>
        <SyntaxHighlighter
          language={langMap[artifact.artifact_type] || 'text'}
          style={oneDark}
          customStyle={{
            margin: 0,
            padding: 20,
            background: '#09090b',
            minHeight: '100%',
            fontSize: '0.8125rem',
            lineHeight: 1.6,
            fontFamily: 'Fira Code, Consolas, Monaco, monospace',
          }}
          showLineNumbers
          wrapLines={wrapLines}
          lineProps={{ style: { wordBreak: wrapLines ? 'break-all' : 'normal', whiteSpace: wrapLines ? 'pre-wrap' : 'pre' } }}
          lineNumberStyle={{ color: '#52525b', fontSize: '0.75rem', minWidth: 40, paddingRight: 16 }}
        >
          {artifact.content}
        </SyntaxHighlighter>
      </div>
    </div>
  );
});
