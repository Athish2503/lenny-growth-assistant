// ============================================================
// Core Domain Types — Lenny Growth Assistant
// ============================================================

export type MessageRole = 'user' | 'assistant' | 'system';
export type ArtifactType = 'markdown' | 'html' | 'css';
export type IntentType = 'qa' | 'essay' | 'artifact';
export type ProviderType = 'ollama' | 'anthropic' | 'openai';
export type ThemeType = 'dark' | 'light' | 'system';

// ============================================================
// Session
// ============================================================
export interface Session {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  message_count?: number;
  last_message?: string;
  last_message_at?: string;
}

export interface CreateSessionInput {
  title?: string;
  user_id?: string;
}

export interface UpdateSessionInput {
  title: string;
}

// ============================================================
// Message
// ============================================================
export interface Citation {
  id: string;
  title: string;
  source: string;
  snippet: string;
  relevance_score: number;
  chunk_index?: number;
  guest?: string;
  episode_title?: string;
  youtube_url?: string;
}

export interface MessageMetadata {
  service?: string;
  intent?: IntentType;
  retrieval_performed?: boolean;
  has_artifacts?: boolean;
  is_essay?: boolean;
  artifact_type?: ArtifactType;
  artifact_id?: string;
  artifact?: Artifact;
  sources?: Citation[];
  retrieval_time_ms?: number;
  confidence_score?: number;
  model?: string;
  tokens_used?: number;
}

export interface Message {
  id: string;
  session_id: string;
  role: MessageRole;
  content: string;
  created_at: string;
  metadata?: MessageMetadata;
  citations?: Citation[];
  is_streaming?: boolean;
}

export interface SendMessageInput {
  session_id: string;
  content: string;
  user_id?: string;
}

export interface SendMessageResponse {
  session_id: string;
  intent: IntentType;
  response_message: Message;
  history_count: number;
  metadata: MessageMetadata;
}

// ============================================================
// Artifact
// ============================================================
export interface Artifact {
  id: string;
  session_id: string;
  title: string;
  artifact_type: ArtifactType;
  content: string;
  version: number;
  created_at: string;
  metadata?: {
    service?: string;
    frontend_rendered?: boolean;
  };
}

// ============================================================
// Research Inspector
// ============================================================
export interface RetrievedChunk {
  id: string;
  content: string;
  source: string;
  score: number;
  metadata?: Record<string, unknown>;
}

export interface RetrievalResult {
  chunks: RetrievedChunk[];
  sources: Citation[];
  retrieval_time_ms: number;
  confidence_score: number;
  model: string;
  provider: ProviderType;
  tokens_used?: number;
}

// ============================================================
// Settings
// ============================================================
export interface ModelInfo {
  id: string;
  name: string;
  provider: ProviderType;
  context_window?: number;
  description?: string;
}

export interface Settings {
  theme: ThemeType;
  provider: ProviderType;
  model: string;
  embedding_model: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
  stream_responses: boolean;
}

// ============================================================
// API Responses
// ============================================================
export interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
}

// ============================================================
// UI State
// ============================================================
export interface StreamingState {
  isStreaming: boolean;
  sessionId: string | null;
  abortController?: AbortController;
}

export type ViewTab = 'preview' | 'code' | 'split';
