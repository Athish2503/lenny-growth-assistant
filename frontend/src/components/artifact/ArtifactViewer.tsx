import { useState } from 'react';
import { motion } from 'framer-motion';
import { X, Maximize2, Minimize2, Copy, Download, Check } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { useArtifactStore } from '@/store/artifactStore';
import type { Artifact, ViewTab } from '@/types';

function ArtifactPreview({ artifact }: { artifact: Artifact }) {
  if (artifact.artifact_type === 'html') {
    const srcDoc = `
      <style>
        body { margin: 0; background: transparent; }
      </style>
      ${artifact.content}
    `;
    return (
      <iframe
        srcDoc={srcDoc}
        title={artifact.title}
        sandbox="allow-scripts"
        style={{ width: '100%', height: '100%', border: 'none', background: '#fff' }}
      />
    );
  }

  if (artifact.artifact_type === 'css') {
    return (
      <div style={{ padding: 20 }}>
        <div style={{
          background: 'var(--color-surface-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 8,
          padding: '10px 14px',
          marginBottom: 12,
          display: 'flex',
          alignItems: 'center',
          gap: 8,
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
            CSS Preview — styles are applied below
          </span>
        </div>
        <style>{artifact.content}</style>
        <div className="prose" style={{ fontSize: '0.875rem' }}>
          <p>CSS stylesheet loaded. Preview shows raw styles applied to this container.</p>
        </div>
      </div>
    );
  }

  // Markdown
  return (
    <div className="prose" style={{ padding: 20, maxWidth: '100%' }}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeHighlight]}>
        {artifact.content}
      </ReactMarkdown>
    </div>
  );
}

function ArtifactCode({ artifact }: { artifact: Artifact }) {
  const langMap: Record<string, string> = {
    markdown: 'markdown',
    html: 'html',
    css: 'css',
  };

  return (
    <div style={{ height: '100%', overflow: 'auto' }}>
      <SyntaxHighlighter
        language={langMap[artifact.artifact_type] || 'text'}
        style={oneDark}
        customStyle={{
          margin: 0,
          padding: 20,
          background: '#0d0d0f',
          height: '100%',
          fontSize: '0.875rem',
          lineHeight: 1.6,
        }}
        showLineNumbers
        lineNumberStyle={{ color: '#4b5563', fontSize: '0.75rem', minWidth: 36 }}
      >
        {artifact.content}
      </SyntaxHighlighter>
    </div>
  );
}

function TypeBadge({ type }: { type: string }) {
  const colors: Record<string, string> = {
    markdown: 'badge-gray',
    html: 'badge-blue',
    css: 'badge-green',
  };
  const labels: Record<string, string> = {
    markdown: '📄 Markdown',
    html: '🌐 HTML',
    css: '🎨 CSS',
  };
  return (
    <span className={`badge ${colors[type] || 'badge-gray'}`}>
      {labels[type] || type.toUpperCase()}
    </span>
  );
}

export function ArtifactViewer() {
  const { currentArtifact, activeTab, isFullscreen, setActiveTab, setCurrentArtifact, toggleFullscreen } = useArtifactStore();
  const [copied, setCopied] = useState(false);

  if (!currentArtifact) return null;
  const artifact = currentArtifact;

  const handleCopy = async () => {
    await navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const ext = { markdown: 'md', html: 'html', css: 'css' }[artifact.artifact_type] || 'txt';
    const blob = new Blob([artifact.content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${artifact.title.replace(/\s+/g, '_')}.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      transition={{ duration: 0.2 }}
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: 'var(--color-surface)',
        borderLeft: '1px solid var(--color-border)',
        ...(isFullscreen ? {
          position: 'fixed',
          inset: 0,
          zIndex: 200,
          borderLeft: 'none',
        } : {}),
      }}
    >
      {/* Header */}
      <div style={{
        padding: '12px 16px',
        borderBottom: '1px solid var(--color-border)',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        flexShrink: 0,
      }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: '0.875rem',
            fontWeight: 600,
            color: 'var(--color-text-primary)',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
            marginBottom: 4,
          }}>
            {artifact.title}
          </div>
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <TypeBadge type={artifact.artifact_type} />
            <span style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>v{artifact.version}</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <button className="btn-icon" onClick={handleCopy} title="Copy">
            {copied ? <Check size={14} style={{ color: 'var(--color-success)' }} /> : <Copy size={14} />}
          </button>
          <button className="btn-icon" onClick={handleDownload} title="Download">
            <Download size={14} />
          </button>
          <button className="btn-icon" onClick={toggleFullscreen} title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}>
            {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          </button>
          {!isFullscreen && (
            <button className="btn-icon" onClick={() => setCurrentArtifact(null)} title="Close artifact">
              <X size={14} />
            </button>
          )}
          {isFullscreen && (
            <button className="btn-icon" onClick={toggleFullscreen} title="Close fullscreen">
              <X size={14} />
            </button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="artifact-tabs" style={{ flexShrink: 0 }}>
        {(['preview', 'code'] as ViewTab[]).map((tab) => (
          <button
            key={tab}
            className={`artifact-tab ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={{ flex: 1, overflow: 'auto' }}>
        {activeTab === 'preview' ? (
          <ArtifactPreview artifact={artifact} />
        ) : (
          <ArtifactCode artifact={artifact} />
        )}
      </div>
    </motion.div>
  );
}
