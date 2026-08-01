import apiClient, { USE_MOCK } from './client';
import { mockArtifacts } from './mock/mockData';
import type { Artifact } from '@/types';

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

export const artifactApi = {
  getBySession: async (sessionId: string): Promise<Artifact[]> => {
    if (USE_MOCK) {
      await delay(150);
      return mockArtifacts.filter((a) => a.session_id === sessionId);
    }
    const res = await apiClient.get<Artifact[]>(`/sessions/${sessionId}/artifacts`);
    return res.data;
  },

  getById: async (id: string): Promise<Artifact> => {
    if (USE_MOCK) {
      await delay(100);
      const artifact = mockArtifacts.find((a) => a.id === id);
      if (!artifact) throw new Error(`Artifact ${id} not found`);
      return artifact;
    }
    const res = await apiClient.get<Artifact>(`/artifacts/${id}`);
    return res.data;
  },
};
