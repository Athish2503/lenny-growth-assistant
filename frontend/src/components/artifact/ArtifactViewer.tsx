import React, { useEffect, useCallback, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useArtifactStore } from '@/store/artifactStore';
import { ArtifactToolbar } from './ArtifactToolbar';
import { ArtifactRuntimeIframe } from './ArtifactRuntimeIframe';
import { ArtifactMarkdownViewer } from './ArtifactMarkdownViewer';
import { ArtifactCodeViewer } from './ArtifactCodeViewer';
import { ArtifactSplitView } from './ArtifactSplitView';

interface ArtifactViewerProps {
  onRegenerate?: () => void;
}

export function ArtifactViewer({ onRegenerate }: ArtifactViewerProps) {
  const {
    currentArtifact,
    activeTab,
    isFullscreen,
    isOpen,
    panelWidth,
    setCurrentArtifact,
    setPanelWidth,
    setIsFullscreen,
  } = useArtifactStore();

  const isResizingRef = useRef(false);
  const [isResizing, setIsResizing] = useState(false);

  // Keyboard shortcut listener (Esc to close, Cmd/Ctrl+C to copy, Cmd/Ctrl+S to download)
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!currentArtifact) return;

      if (e.key === 'Escape') {
        if (isFullscreen) {
          setIsFullscreen(false);
        } else {
          setCurrentArtifact(null);
        }
      } else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'c' && !window.getSelection()?.toString()) {
        e.preventDefault();
        navigator.clipboard.writeText(currentArtifact.content);
      } else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        const ext = currentArtifact.artifact_type === 'html' ? 'html' : 'md';
        const blob = new Blob([currentArtifact.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentArtifact.title.replace(/\s+/g, '_')}.${ext}`;
        a.click();
        URL.revokeObjectURL(url);
      }
    },
    [currentArtifact, isFullscreen, setCurrentArtifact, setIsFullscreen]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  // Handle panel mouse drag resizing
  const startResizing = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    isResizingRef.current = true;
    setIsResizing(true);

    const handleMouseMove = (moveEvent: MouseEvent) => {
      if (!isResizingRef.current) return;
      const newWidth = window.innerWidth - moveEvent.clientX;
      setPanelWidth(newWidth);
    };

    const handleMouseUp = () => {
      isResizingRef.current = false;
      setIsResizing(false);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };

    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);
  }, [setPanelWidth]);

  if (!currentArtifact || !isOpen) return null;
  const artifact = currentArtifact;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 40 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 40 }}
        transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
        style={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%',
          width: isFullscreen ? '100vw' : panelWidth,
          background: 'var(--color-surface)',
          borderLeft: isFullscreen ? 'none' : '1px solid var(--color-border)',
          position: isFullscreen ? 'fixed' : 'relative',
          inset: isFullscreen ? 0 : undefined,
          zIndex: isFullscreen ? 300 : 10,
          boxShadow: isFullscreen
            ? 'none'
            : '-10px 0 30px -5px rgba(0, 0, 0, 0.3)',
          transition: isResizing ? 'none' : 'width 0.1s ease',
          userSelect: isResizing ? 'none' : 'auto',
        }}
      >
        {/* Resize Handle (Left edge) */}
        {!isFullscreen && (
          <div
            onMouseDown={startResizing}
            style={{
              position: 'absolute',
              top: 0,
              bottom: 0,
              left: -4,
              width: 8,
              cursor: 'col-resize',
              zIndex: 20,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
            title="Drag to resize panel"
          >
            <div style={{
              width: 2,
              height: 32,
              borderRadius: 1,
              background: isResizing ? 'var(--color-accent)' : 'var(--color-border)',
              transition: 'background 0.15s ease',
            }} />
          </div>
        )}

        {/* Toolbar */}
        <ArtifactToolbar artifact={artifact} onRegenerate={onRegenerate} />

        {/* View Mode Content */}
        <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
          {activeTab === 'preview' && (
            artifact.artifact_type === 'markdown' ? (
              <div style={{ height: '100%', overflow: 'auto' }}>
                <ArtifactMarkdownViewer artifact={artifact} />
              </div>
            ) : (
              <ArtifactRuntimeIframe artifact={artifact} />
            )
          )}

          {activeTab === 'code' && (
            <ArtifactCodeViewer artifact={artifact} />
          )}

          {activeTab === 'split' && (
            <ArtifactSplitView artifact={artifact} />
          )}
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
