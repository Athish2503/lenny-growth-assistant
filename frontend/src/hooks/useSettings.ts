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

  const saveSettings = (partial: Partial<Settings>) => {
    updateSettings(partial);
    mutation.mutate(partial);
  };

  return {
    settings,
    isLoading: query.isLoading,
    isSaving: mutation.isPending,
    saveSettings,
  };
}
