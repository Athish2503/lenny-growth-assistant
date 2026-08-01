import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: 24,
      padding: 40,
    }}>
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.4 }}
        style={{ textAlign: 'center' }}
      >
        <div style={{
          fontSize: '5rem',
          fontWeight: 800,
          letterSpacing: '-0.05em',
          color: 'var(--color-text-disabled)',
          lineHeight: 1,
          marginBottom: 8,
        }}>
          404
        </div>
        <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: 8 }}>Page not found</h2>
        <p style={{ color: 'var(--color-text-muted)', marginBottom: 24, maxWidth: 320 }}>
          The page you're looking for doesn't exist or has been moved.
        </p>
        <button className="btn btn-primary" onClick={() => navigate('/chat')}>
          <Zap size={14} />
          Back to Chat
        </button>
      </motion.div>
    </div>
  );
}
