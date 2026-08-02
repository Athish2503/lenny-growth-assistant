import apiClient, { USE_MOCK } from './client';
import { mockSettings } from './mock/mockData';
import type { Settings } from '@/types';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

// Use unknown to allow mutation
let localSettings: Record<string, unknown> = { ...mockSettings };

export const settingsApi = {
  get: async (): Promise<Settings> => {
    if (USE_MOCK) {
      await delay(100);
      return { ...localSettings } as unknown as Settings;
    }
    const res = await apiClient.get<Settings>('/settings');
    return res.data;
  },

  save: async (settings: Partial<Settings>): Promise<Settings> => {
    if (USE_MOCK) {
      await delay(200);
      localSettings = { ...localSettings, ...(settings as Record<string, unknown>) };
      return { ...localSettings } as unknown as Settings;
    }
    const res = await apiClient.put<Settings>('/settings', settings);
    return res.data;
  },

  getAvailableModels: async (): Promise<{
    ollama: string[];
    anthropic: string[];
    openai: string[];
    current_provider: string;
    current_model: string;
  }> => {
    if (USE_MOCK) {
      return {
        ollama: ['mistral:7b', 'gemma4:latest', 'qwen2.5-coder:7b'],
        anthropic: ['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229'],
        openai: ['gpt-4o', 'gpt-4o-mini'],
        current_provider: 'ollama',
        current_model: 'mistral:7b',
      };
    }
    const res = await apiClient.get('/settings/models');
    return res.data;
  },
};

