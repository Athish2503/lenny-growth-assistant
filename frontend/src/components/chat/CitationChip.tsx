import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Play, Database, Mic } from 'lucide-react';
import type { Citation } from '@/types';

interface CitationChipProps {
  citation: Citation;
}

export function CitationChip({ citation }: CitationChipProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  const guestName = citation.guest || (citation.title ? citation.title.replace(/^Episode with /i, '') : 'Podcast Guest');
  const displayTitle = citation.episode_title || citation.title || 'Lenny\'s Podcast Episode';

  // Determine YouTube URL or fallback search URL
  let ytUrl = citation.youtube_url;
  if (!ytUrl && citation.source && citation.source.startsWith('http')) {
    ytUrl = citation.source;
  }
  if (!ytUrl) {
    ytUrl = `https://www.youtube.com/results?search_query=Lenny+Podcast+${encodeURIComponent(guestName)}`;
  }

  const scorePct = Math.round((citation.relevance_score > 1 ? citation.relevance_score / 100 : citation.relevance_score) * 100);

  return (
    <div style={{ position: 'relative', display: 'inline-flex', alignItems: 'center' }}>
      <div
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          background: 'var(--color-surface-elevated)',
          border: '1px solid var(--color-border)',
          borderRadius: 20,
          padding: '3px 10px 3px 8px',
          fontSize: '0.775rem',
          boxShadow: '0 2px 6px rgba(0,0,0,0.12)',
          transition: 'all 0.2s ease',
        }}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        {/* Source Icon / Guest */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontWeight: 600, color: 'var(--color-text-primary)' }}>
          <Mic size={12} style={{ color: 'var(--color-accent)' }} />
          <span>{guestName.length > 25 ? guestName.slice(0, 25) + '…' : guestName}</span>
        </div>

        {/* Relevance badge */}
        <span style={{
          background: 'rgba(59, 130, 246, 0.12)',
          color: '#60a5fa',
          border: '1px solid rgba(59, 130, 246, 0.25)',
          borderRadius: 10,
          padding: '1px 6px',
          fontSize: '0.675rem',
          fontWeight: 700,
        }}>
          {scorePct}% match
        </span>

        {/* YouTube Link Button Pill */}
        <a
          href={ytUrl}
          target="_blank"
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          title="Watch episode on YouTube"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 4,
            background: 'rgba(239, 68, 68, 0.15)',
            color: '#f87171',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: 12,
            padding: '2px 8px',
            fontSize: '0.7rem',
            fontWeight: 600,
            textDecoration: 'none',
            transition: 'all 0.15s ease',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.25)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.15)';
          }}
        >
          <Play size={10} fill="#f87171" color="#f87171" />
          <span>YouTube</span>
          <ExternalLink size={9} />
        </a>
      </div>

      {/* Tooltip */}
      <AnimatePresence>
        {showTooltip && (
          <motion.div
            initial={{ opacity: 0, y: 4, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.96 }}
            transition={{ duration: 0.15 }}
            style={{
              position: 'absolute',
              bottom: 'calc(100% + 8px)',
              left: '50%',
              transform: 'translateX(-50%)',
              background: '#121215',
              border: '1px solid var(--color-border)',
              borderRadius: 12,
              padding: '12px 14px',
              width: 320,
              boxShadow: '0 12px 30px rgba(0,0,0,0.5)',
              zIndex: 100,
              pointerEvents: 'none',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 4 }}>
              <Database size={13} style={{ color: 'var(--color-accent)' }} />
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--color-accent)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Knowledge Base Source
              </span>
            </div>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: '#f4f4f5', marginBottom: 4 }}>
              {displayTitle}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#a1a1aa', marginBottom: 8, display: 'flex', gap: 6, alignItems: 'center' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                <Mic size={11} /> Guest: {guestName}
              </span>
              <span>•</span>
              <span style={{ color: '#34d399' }}>{scorePct}% Relevance</span>
            </div>
            <div style={{
              fontSize: '0.78rem',
              color: '#d4d4d8',
              lineHeight: 1.5,
              background: 'rgba(255,255,255,0.03)',
              padding: '8px 10px',
              borderRadius: 8,
              borderLeft: '2px solid var(--color-accent)',
              fontStyle: 'italic',
            }}>
              "{citation.snippet}"
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
