import { useQuery } from '@tanstack/react-query';
import { artifactApi } from '@/api/artifactApi';
import { useArtifactStore } from '@/store/artifactStore';
import type { Artifact } from '@/types';

export function useArtifacts(sessionId: string | undefined) {
  const { setArtifacts, setCurrentArtifact, setActiveTab } = useArtifactStore();

  const query = useQuery({
    queryKey: ['artifacts', sessionId],
    queryFn: async () => {
      if (!sessionId) return [];
      const artifacts = await artifactApi.getBySession(sessionId);
      setArtifacts(sessionId, artifacts);
      return artifacts;
    },
    enabled: !!sessionId,
    staleTime: 30000,
  });

  const openArtifact = (artifact: Artifact) => {
    setCurrentArtifact(artifact);
    setActiveTab('preview');
  };

  const closeArtifact = () => {
    setCurrentArtifact(null);
  };

  return {
    artifacts: query.data || [],
    isLoading: query.isLoading,
    openArtifact,
    closeArtifact,
  };
}
