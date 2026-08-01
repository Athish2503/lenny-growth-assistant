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
};

