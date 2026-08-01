import { create } from 'zustand';
import type { Artifact, ViewTab } from '@/types';

interface ArtifactState {
  currentArtifact: Artifact | null;
  artifacts: Record<string, Artifact[]>;
  activeTab: ViewTab;
  isFullscreen: boolean;
  isOpen: boolean;
  setCurrentArtifact: (artifact: Artifact | null) => void;
  setArtifacts: (sessionId: string, artifacts: Artifact[]) => void;
  setActiveTab: (tab: ViewTab) => void;
  setIsFullscreen: (v: boolean) => void;
  setIsOpen: (v: boolean) => void;
  toggleFullscreen: () => void;
}

export const useArtifactStore = create<ArtifactState>((set) => ({
  currentArtifact: null,
  artifacts: {},
  activeTab: 'preview',
  isFullscreen: false,
  isOpen: false,

  setCurrentArtifact: (artifact) => set({ currentArtifact: artifact, isOpen: artifact !== null }),
  setArtifacts: (sessionId, artifacts) =>
    set((s) => ({ artifacts: { ...s.artifacts, [sessionId]: artifacts } })),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setIsFullscreen: (v) => set({ isFullscreen: v }),
  setIsOpen: (v) => set({ isOpen: v }),
  toggleFullscreen: () => set((s) => ({ isFullscreen: !s.isFullscreen })),
}));
