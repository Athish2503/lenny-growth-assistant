import { motion } from 'framer-motion';
import { Zap, TrendingUp, BookOpen, BarChart3, PenLine, Sparkles } from 'lucide-react';

interface QuickPrompt {
  icon: React.ReactNode;
  label: string;
  prompt: string;
}

const quickPrompts: QuickPrompt[] = [
  {
    icon: <TrendingUp size={16} />,
    label: 'PLG Strategy',
    prompt: 'What is product-led growth and how should I implement it for my B2B SaaS?',
  },
  {
    icon: <BarChart3 size={16} />,
    label: 'Activation Metrics',
    prompt: 'What are the most important activation metrics I should track for my onboarding funnel?',
  },
  {
    icon: <PenLine size={16} />,
    label: 'Essay on Growth',
    prompt: '/essay Write an essay on the importance of retention in SaaS growth',
  },
  {
    icon: <BookOpen size={16} />,
    label: 'Retention Analysis',
    prompt: 'How do I analyze my retention curves and identify product-market fit?',
  },
];

interface WelcomeScreenProps {
  onPromptClick: (prompt: string) => void;
}

export function WelcomeScreen({ onPromptClick }: WelcomeScreenProps) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      flex: 1,
      padding: '40px 20px',
      gap: 32,
    }}>
      {/* Logo */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4, ease: 'easeOut' }}
        style={{ textAlign: 'center' }}
      >
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 6,
          padding: '4px 12px',
          borderRadius: 20,
          background: 'rgba(59, 130, 246, 0.12)',
          border: '1px solid rgba(59, 130, 246, 0.3)',
          color: '#60a5fa',
          fontSize: '0.78rem',
          fontWeight: 600,
          marginBottom: 16,
        }}>
          <Sparkles size={12} style={{ color: '#60a5fa' }} />
          <span>New Chat Session</span>
        </div>
        <div style={{
          width: 56,
          height: 56,
          borderRadius: 14,
          background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
          boxShadow: '0 0 40px rgba(59,130,246,0.3)',
        }}>
          <Zap size={26} color="#fff" fill="#fff" />
        </div>
        <h1 style={{
          fontSize: '1.75rem',
          fontWeight: 700,
          color: 'var(--color-text-primary)',
          letterSpacing: '-0.03em',
          marginBottom: 8,
        }}>
          Lenny Growth Assistant
        </h1>
        <p style={{ fontSize: '0.9375rem', color: 'var(--color-text-muted)', maxWidth: 420, lineHeight: 1.6 }}>
          Your AI-powered growth advisor. Ask anything about product growth, retention,
          metrics, or have an essay drafted in seconds.
        </p>
      </motion.div>

      {/* Quick prompts */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.15, ease: 'easeOut' }}
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(2, 1fr)',
          gap: 10,
          width: '100%',
          maxWidth: 560,
        }}
      >
        {quickPrompts.map((qp, i) => (
          <motion.button
            key={i}
            onClick={() => onPromptClick(qp.prompt)}
            whileHover={{ scale: 1.02, y: -1 }}
            whileTap={{ scale: 0.98 }}
            style={{
              background: 'var(--color-surface)',
              border: '1px solid var(--color-border)',
              borderRadius: 12,
              padding: '14px 16px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 10,
              textAlign: 'left',
              transition: 'border-color 0.15s',
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = 'var(--color-accent-border)';
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.borderColor = 'var(--color-border)';
            }}
          >
            <div style={{
              color: 'var(--color-accent)',
              background: 'var(--color-accent-subtle)',
              borderRadius: 7,
              padding: 6,
              flexShrink: 0,
            }}>
              {qp.icon}
            </div>
            <div>
              <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: 2 }}>
                {qp.label}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)', lineHeight: 1.4 }}>
                {qp.prompt.length > 60 ? qp.prompt.slice(0, 60) + '…' : qp.prompt}
              </div>
            </div>
          </motion.button>
        ))}
      </motion.div>

      {/* Keyboard shortcut hint */}
      <p style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
        Press <kbd style={{ background: 'var(--color-surface-elevated)', border: '1px solid var(--color-border)', borderRadius: 4, padding: '1px 5px', fontFamily: 'inherit' }}>⌘K</kbd> for a new chat
      </p>
    </div>
  );
}
