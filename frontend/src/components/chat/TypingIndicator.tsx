export function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: 12, padding: '4px 0 8px', alignItems: 'flex-start' }}>
      <div style={{
        width: 28,
        height: 28,
        borderRadius: 7,
        background: 'linear-gradient(135deg, #3b82f6, #6366f1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        marginTop: 4,
      }}>
        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: '#fff' }}>L</span>
      </div>
      <div style={{
        background: 'var(--color-surface)',
        border: '1px solid var(--color-border)',
        borderRadius: '4px 16px 16px 16px',
        padding: '12px 16px',
        display: 'flex',
        gap: 5,
        alignItems: 'center',
      }}>
        <span className="typing-dot" />
        <span className="typing-dot" />
        <span className="typing-dot" />
      </div>
    </div>
  );
}
