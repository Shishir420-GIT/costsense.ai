export type Provider = 'openai' | 'gemini';

export interface Message {
  from: 'user' | 'ai';
  text: string;
  dsl?: string;
  timestamp?: string;
  error?: boolean;
}

export interface AIResponse {
  reply: string;
  dsl?: string;
  provider: Provider;
  generationTime?: number;
  error?: string;
  code?: string;
  fallbackMessage?: string;
}

export interface ProviderStatus {
  available: boolean;
  configured: boolean;
  error?: string;
}

export interface AIStatus {
  providers: Record<Provider, ProviderStatus>;
  available: Provider[];
  conversationCount?: number;
}

export interface ConversationHistory {
  conversationId: string;
  history: Message[];
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  resetTime: string;
  retryAfter?: number;
}

export interface AIError {
  error: string;
  code: string;
  provider?: Provider;
  fallbackMessage?: string;
  timestamp?: string;
}