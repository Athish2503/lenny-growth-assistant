import React, { useMemo, useEffect, useRef } from 'react';
import { AlertCircle, Code2, RefreshCw } from 'lucide-react';
import { useArtifactStore } from '@/store/artifactStore';
import type { Artifact } from '@/types';

interface ArtifactRuntimeIframeProps {
  artifact: Artifact;
}

export const ArtifactRuntimeIframe = React.memo(function ArtifactRuntimeIframe({
  artifact,
}: ArtifactRuntimeIframeProps) {
  const { renderError, setRenderError, setActiveTab } = useArtifactStore();
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Clear previous error on artifact change
  useEffect(() => {
    setRenderError(null);
  }, [artifact.id, setRenderError]);

  const srcDoc = useMemo(() => {
    const rawContent = artifact.content || '';
    const hasHead = rawContent.toLowerCase().includes('<html') || rawContent.toLowerCase().includes('<head');

    if (hasHead) {
      // Inject CDN dependencies and error listeners into existing HTML head
      let documentHtml = rawContent;
      const headInject = `
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
          window.onerror = function(msg, url, lineNo, columnNo, error) {
            window.parent.postMessage({ type: 'IFRAME_ERROR', message: msg, line: lineNo }, '*');
            return false;
          };
          window.addEventListener('unhandledrejection', function(e) {
            window.parent.postMessage({ type: 'IFRAME_ERROR', message: e.reason ? (e.reason.message || String(e.reason)) : 'Unhandled promise rejection' }, '*');
          });
          document.addEventListener('DOMContentLoaded', function() {
            if (window.mermaid) {
              window.mermaid.initialize({ startOnLoad: true, theme: 'dark' });
            }
          });
        </script>
        <style>
          * { box-sizing: border-box; }
          body { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
          ::-webkit-scrollbar { width: 6px; height: 6px; }
          ::-webkit-scrollbar-track { background: transparent; }
          ::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.4); border-radius: 3px; }
        </style>
      `;

      if (documentHtml.toLowerCase().includes('<head>')) {
        documentHtml = documentHtml.replace(/<head>/i, `<head>${headInject}`);
      } else if (documentHtml.toLowerCase().includes('<html>')) {
        documentHtml = documentHtml.replace(/<html>/i, `<html><head>${headInject}</head>`);
      }
      return documentHtml;
    }

    // Wrap snippet into modern HTML document
    return `
      <!DOCTYPE html>
      <html lang="en" class="dark">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
        <script>
          window.onerror = function(msg, url, lineNo, columnNo, error) {
            window.parent.postMessage({ type: 'IFRAME_ERROR', message: msg, line: lineNo }, '*');
            return false;
          };
          window.addEventListener('unhandledrejection', function(e) {
            window.parent.postMessage({ type: 'IFRAME_ERROR', message: e.reason ? (e.reason.message || String(e.reason)) : 'Unhandled promise rejection' }, '*');
          });
          document.addEventListener('DOMContentLoaded', function() {
            if (window.mermaid) {
              window.mermaid.initialize({ startOnLoad: true, theme: 'dark' });
            }
          });
        </script>
        <style>
          * { box-sizing: border-box; }
          body {
            margin: 0;
            padding: 24px;
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
            background: #09090b;
            color: #f4f4f5;
            min-height: 100vh;
          }
          ::-webkit-scrollbar { width: 6px; height: 6px; }
          ::-webkit-scrollbar-track { background: transparent; }
          ::-webkit-scrollbar-thumb { background: rgba(156, 163, 175, 0.4); border-radius: 3px; }
        </style>
      </head>
      <body>
        ${artifact.artifact_type === 'css' ? `<style>${artifact.content}</style><div class="artifact-container"><h1 class="text-2xl font-bold">${artifact.title}</h1><p class="mt-2 text-gray-400">Live preview with injected stylesheet.</p></div>` : artifact.content}
      </body>
      </html>
    `;
  }, [artifact.content, artifact.artifact_type, artifact.title]);

  // Listen for postMessage iframe errors
  useEffect(() => {
    const handleMessage = (e: MessageEvent) => {
      if (e.data && e.data.type === 'IFRAME_ERROR') {
        const errorMsg = e.data.message || 'Error occurred while rendering HTML runtime';
        setRenderError(errorMsg);
      }
    };
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [setRenderError]);

  if (renderError) {
    return (
      <div style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 32,
        background: 'var(--color-surface-elevated)',
        color: 'var(--color-text-primary)',
        textAlign: 'center',
      }}>
        <AlertCircle size={40} style={{ color: 'var(--color-error)', marginBottom: 16 }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 8 }}>Rendering Failed</h3>
        <p style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', maxWidth: 460, marginBottom: 20 }}>
          {renderError}
        </p>
        <div style={{ display: 'flex', gap: 12 }}>
          <button
            onClick={() => setActiveTab('code')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '8px 16px',
              background: 'var(--color-accent)',
              color: '#ffffff',
              border: 'none',
              borderRadius: 8,
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            <Code2 size={16} /> Switch to Code Mode
          </button>
          <button
            onClick={() => setRenderError(null)}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              padding: '8px 16px',
              background: 'transparent',
              color: 'var(--color-text-primary)',
              border: '1px solid var(--color-border)',
              borderRadius: 8,
              fontSize: '0.875rem',
              fontWeight: 500,
              cursor: 'pointer',
            }}
          >
            <RefreshCw size={15} /> Retry Render
          </button>
        </div>
      </div>
    );
  }

  return (
    <iframe
      ref={iframeRef}
      srcDoc={srcDoc}
      title={artifact.title}
      sandbox="allow-scripts allow-modals allow-same-origin"
      style={{
        width: '100%',
        height: '100%',
        border: 'none',
        background: '#09090b',
        display: 'block',
      }}
    />
  );
});
