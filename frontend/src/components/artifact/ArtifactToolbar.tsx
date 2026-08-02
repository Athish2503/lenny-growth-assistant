import React, { useState } from 'react';
import {
  Copy,
  Download,
  Maximize2,
  Minimize2,
  ExternalLink,
  RotateCw,
  Eye,
  Code2,
  Columns,
  Check,
  X,
  FileCode,
  FileText,
  Globe,
} from 'lucide-react';
import { useArtifactStore } from '@/store/artifactStore';
import type { Artifact, ViewTab } from '@/types';

interface ArtifactToolbarProps {
  artifact: Artifact;
  onRegenerate?: () => void;
}

export const ArtifactToolbar = React.memo(function ArtifactToolbar({
  artifact,
  onRegenerate,
}: ArtifactToolbarProps) {
  const {
    activeTab,
    isFullscreen,
    setActiveTab,
    setCurrentArtifact,
    toggleFullscreen,
  } = useArtifactStore();

  const [copied, setCopied] = useState(false);
  const [downloadMenuOpen, setDownloadMenuOpen] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(artifact.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (format: 'html' | 'md' | 'txt') => {
    const titleClean = artifact.title.replace(/[^a-zA-Z0-9_-]/g, '_');
    let fileContent = artifact.content;
    let fileName = `${titleClean}.${format}`;
    let mimeType = 'text/plain';

    if (format === 'html') {
      mimeType = 'text/html';
      if (!fileContent.toLowerCase().includes('<html')) {
        fileContent = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${artifact.title}</title></head><body>${fileContent}</body></html>`;
      }
    } else if (format === 'md') {
      mimeType = 'text/markdown';
    }

    const blob = new Blob([fileContent], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
    setDownloadMenuOpen(false);
  };

  const handleOpenNewWindow = () => {
    let content = artifact.content;
    let mime = 'text/html';
    if (artifact.artifact_type === 'markdown') {
      mime = 'text/plain';
    } else if (!content.toLowerCase().includes('<html')) {
      content = `<!DOCTYPE html><html><head><meta charset="utf-8"><title>${artifact.title}</title><script src="https://cdn.tailwindcss.com"></script></head><body>${content}</body></html>`;
    }

    const blob = new Blob([content], { type: mime });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '10px 16px',
      borderBottom: '1px solid var(--color-border)',
      background: 'var(--color-surface)',
      flexShrink: 0,
      gap: 12,
    }}>
      {/* Left: Title & Type Badge */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, minWidth: 0, flex: 1 }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 6,
          padding: '3px 8px',
          borderRadius: 6,
          background: 'var(--color-surface-elevated)',
          border: '1px solid var(--color-border)',
          fontSize: '0.725rem',
          fontWeight: 600,
          color: 'var(--color-accent)',
          textTransform: 'uppercase',
        }}>
          {artifact.artifact_type === 'html' ? <Globe size={12} /> : <FileText size={12} />}
          <span>{artifact.artifact_type}</span>
        </div>

        <span style={{
          fontSize: '0.875rem',
          fontWeight: 600,
          color: 'var(--color-text-primary)',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          whiteSpace: 'nowrap',
        }}>
          {artifact.title}
        </span>
      </div>

      {/* Middle: View Mode Tabs */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        background: 'var(--color-surface-elevated)',
        border: '1px solid var(--color-border)',
        borderRadius: 8,
        padding: 3,
        gap: 2,
      }}>
        <button
          onClick={() => setActiveTab('preview')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            borderRadius: 6,
            fontSize: '0.75rem',
            fontWeight: 500,
            border: 'none',
            cursor: 'pointer',
            background: activeTab === 'preview' ? 'var(--color-accent)' : 'transparent',
            color: activeTab === 'preview' ? '#ffffff' : 'var(--color-text-muted)',
            transition: 'all 0.15s ease',
          }}
          title="Preview Mode"
        >
          <Eye size={13} /> Preview
        </button>

        <button
          onClick={() => setActiveTab('code')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            borderRadius: 6,
            fontSize: '0.75rem',
            fontWeight: 500,
            border: 'none',
            cursor: 'pointer',
            background: activeTab === 'code' ? 'var(--color-accent)' : 'transparent',
            color: activeTab === 'code' ? '#ffffff' : 'var(--color-text-muted)',
            transition: 'all 0.15s ease',
          }}
          title="Code Mode"
        >
          <Code2 size={13} /> Code
        </button>

        <button
          onClick={() => setActiveTab('split')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            padding: '4px 10px',
            borderRadius: 6,
            fontSize: '0.75rem',
            fontWeight: 500,
            border: 'none',
            cursor: 'pointer',
            background: activeTab === 'split' ? 'var(--color-accent)' : 'transparent',
            color: activeTab === 'split' ? '#ffffff' : 'var(--color-text-muted)',
            transition: 'all 0.15s ease',
          }}
          title="Split View Mode"
        >
          <Columns size={13} /> Split
        </button>
      </div>

      {/* Right: Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, position: 'relative' }}>
        <button className="btn-icon" onClick={handleCopy} title="Copy Code (Ctrl+C)">
          {copied ? <Check size={14} style={{ color: 'var(--color-success)' }} /> : <Copy size={14} />}
        </button>

        {/* Download Menu */}
        <div style={{ position: 'relative' }}>
          <button
            className="btn-icon"
            onClick={() => setDownloadMenuOpen(!downloadMenuOpen)}
            title="Download (Ctrl+S)"
          >
            <Download size={14} />
          </button>

          {downloadMenuOpen && (
            <div style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: 6,
              background: 'var(--color-surface-elevated)',
              border: '1px solid var(--color-border)',
              borderRadius: 8,
              boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)',
              padding: 4,
              zIndex: 100,
              display: 'flex',
              flexDirection: 'column',
              minWidth: 140,
            }}>
              <button
                onClick={() => handleDownload('html')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '6px 10px',
                  border: 'none',
                  background: 'transparent',
                  color: 'var(--color-text-primary)',
                  fontSize: '0.775rem',
                  borderRadius: 4,
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <Globe size={13} /> HTML (.html)
              </button>
              <button
                onClick={() => handleDownload('md')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '6px 10px',
                  border: 'none',
                  background: 'transparent',
                  color: 'var(--color-text-primary)',
                  fontSize: '0.775rem',
                  borderRadius: 4,
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <FileText size={13} /> Markdown (.md)
              </button>
              <button
                onClick={() => handleDownload('txt')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 8,
                  padding: '6px 10px',
                  border: 'none',
                  background: 'transparent',
                  color: 'var(--color-text-primary)',
                  fontSize: '0.775rem',
                  borderRadius: 4,
                  cursor: 'pointer',
                  textAlign: 'left',
                }}
              >
                <FileCode size={13} /> Text (.txt)
              </button>
            </div>
          )}
        </div>

        {onRegenerate && (
          <button className="btn-icon" onClick={onRegenerate} title="Regenerate Artifact">
            <RotateCw size={14} />
          </button>
        )}

        <button className="btn-icon" onClick={handleOpenNewWindow} title="Open in New Window">
          <ExternalLink size={14} />
        </button>

        <button
          className="btn-icon"
          onClick={toggleFullscreen}
          title={isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}
        >
          {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
        </button>

        <button className="btn-icon" onClick={() => setCurrentArtifact(null)} title="Close Panel (Esc)">
          <X size={14} />
        </button>
      </div>
    </div>
  );
});
