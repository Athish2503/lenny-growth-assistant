import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink } from 'lucide-react';
import type { Citation } from '@/types';

interface CitationChipProps {
  citation: Citation;
}

export function CitationChip({ citation }: CitationChipProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <button
        className="citation-chip"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        aria-label={`Source: ${citation.title}`}
      >
        <ExternalLink size={10} />
        {citation.title.length > 30 ? citation.title.slice(0, 30) + '…' : citation.title}
        <span style={{
          background: 'rgba(59,130,246,0.2)',
          borderRadius: 4,
          padding: '1px 4px',
          fontSize: '0.65rem',
          fontWeight: 700,
        }}>
          {Math.round(citation.relevance_score * 100)}%
        </span>
      </button>

      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 4 }}
            transition={{ duration: 0.1 }}
            style={{
              position: 'absolute',
              bottom: 'calc(100% + 8px)',
              left: '50%',
              transform: 'translateX(-50%)',
              background: 'var(--color-surface-elevated)',
              border: '1px solid var(--color-border)',
              borderRadius: 10,
              padding: 12,
              maxWidth: 300,
              boxShadow: 'var(--shadow-lg)',
              zIndex: 100,
              pointerEvents: 'none',
            }}
          >
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 4 }}>
              {citation.title}
            </div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: 6 }}>
              {citation.source}
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-secondary)', lineHeight: 1.5, fontStyle: 'italic' }}>
              "{citation.snippet}"
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
