import { create } from 'zustand';
import type { Settings } from '@/types';
import { mockSettings } from '@/api/mock/mockData';

interface SettingsState {
  settings: Settings;
  isLoaded: boolean;
  setSettings: (settings: Settings) => void;
  updateSettings: (partial: Partial<Settings>) => void;
  setIsLoaded: (v: boolean) => void;
}

export const useSettingsStore = create<SettingsState>((set) => ({
  settings: { ...mockSettings },
  isLoaded: false,

  setSettings: (settings) => set({ settings, isLoaded: true }),
  updateSettings: (partial) =>
    set((s) => ({ settings: { ...s.settings, ...partial } })),
  setIsLoaded: (v) => set({ isLoaded: v }),
}));
