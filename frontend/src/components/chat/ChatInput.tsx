import { useCallback, useRef, useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Square, Paperclip } from 'lucide-react';

interface ChatInputProps {
  onSend: (message: string) => void;
  isStreaming: boolean;
  onStop: () => void;
  disabled?: boolean;
  placeholder?: string;
}

export function ChatInput({ onSend, isStreaming, onStop, disabled, placeholder }: ChatInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current;
    if (!ta) return;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 200) + 'px';
  }, [value]);

  const handleSend = useCallback(() => {
    if (!value.trim() || isStreaming || disabled) return;
    onSend(value);
    setValue('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  }, [value, isStreaming, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const canSend = value.trim().length > 0 && !isStreaming && !disabled;

  return (
    <div style={{ padding: '0 20px 20px' }}>
      <div className="chat-input-container">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || 'Ask Lenny anything about growth...'}
          className="chat-textarea"
          rows={1}
          disabled={disabled}
          aria-label="Chat message input"
        />

        {/* Bottom row: attach + char count + send */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '0 10px 10px',
        }}>
          <div style={{ display: 'flex', gap: 4 }}>
            <button
              className="btn-icon"
              disabled
              title="Attach file (coming soon)"
              style={{ opacity: 0.4 }}
            >
              <Paperclip size={15} />
            </button>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {value.length > 100 && (
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                {value.length}
              </span>
            )}
            <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
              Shift+Enter for newline
            </span>
            {isStreaming ? (
              <motion.button
                className="btn-send"
                onClick={onStop}
                style={{ background: 'var(--color-surface-elevated)', border: '1px solid var(--color-border)' }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                title="Stop generation"
                aria-label="Stop generation"
              >
                <Square size={14} style={{ color: 'var(--color-text-primary)' }} fill="currentColor" />
              </motion.button>
            ) : (
              <motion.button
                className="btn-send"
                onClick={handleSend}
                disabled={!canSend}
                whileHover={canSend ? { scale: 1.05 } : {}}
                whileTap={canSend ? { scale: 0.95 } : {}}
                title="Send message (Enter)"
                aria-label="Send message"
              >
                <Send size={14} />
              </motion.button>
            )}
          </div>
        </div>
      </div>

      <div style={{ textAlign: 'center', marginTop: 8 }}>
        <span style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
          Lenny may make mistakes. Verify important information.
        </span>
      </div>
    </div>
  );
}
