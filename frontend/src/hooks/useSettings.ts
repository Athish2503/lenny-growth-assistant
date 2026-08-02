import { useQuery, useMutation } from '@tanstack/react-query';
import { settingsApi } from '@/api/settingsApi';
import { useSettingsStore } from '@/store/settingsStore';
import type { Settings } from '@/types';

export function useSettings() {
  const { settings, setSettings, updateSettings } = useSettingsStore();

  const query = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const s = await settingsApi.get();
      setSettings(s);
      return s;
    },
    staleTime: 60000,
  });

  const mutation = useMutation({
    mutationFn: settingsApi.save,
    onSuccess: (s: Settings) => {
      setSettings(s);
    },
  });

  const modelsQuery = useQuery({
    queryKey: ['availableModels'],
    queryFn: settingsApi.getAvailableModels,
    staleTime: 30000,
  });

  const saveSettings = (partial: Partial<Settings>) => {
    updateSettings(partial);
    mutation.mutate(partial);
  };

  return {
    settings,
    isLoading: query.isLoading,
    isSaving: mutation.isPending,
    saveSettings,
    availableModels: modelsQuery.data || {
      ollama: ['mistral:7b', 'gemma4:latest', 'qwen2.5-coder:7b'],
      anthropic: ['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229'],
      openai: ['gpt-4o', 'gpt-4o-mini'],
      current_provider: settings.provider,
      current_model: settings.model,
    },
  };
}
