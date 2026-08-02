import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { Artifact, ViewTab } from '@/types';

interface ArtifactState {
  currentArtifact: Artifact | null;
  artifacts: Record<string, Artifact[]>;
  activeTab: ViewTab;
  isFullscreen: boolean;
  isOpen: boolean;
  panelWidth: number;
  renderError: string | null;
  setCurrentArtifact: (artifact: Artifact | null) => void;
  setArtifacts: (sessionId: string, artifacts: Artifact[]) => void;
  setActiveTab: (tab: ViewTab) => void;
  setIsFullscreen: (v: boolean) => void;
  setIsOpen: (v: boolean) => void;
  setPanelWidth: (w: number) => void;
  setRenderError: (err: string | null) => void;
  toggleFullscreen: () => void;
}

export const useArtifactStore = create<ArtifactState>()(
  persist(
    (set) => ({
      currentArtifact: null,
      artifacts: {},
      activeTab: 'preview',
      isFullscreen: false,
      isOpen: false,
      panelWidth: 640,
      renderError: null,

      setCurrentArtifact: (artifact) =>
        set({ currentArtifact: artifact, isOpen: artifact !== null, renderError: null }),
      setArtifacts: (sessionId, artifacts) =>
        set((s) => ({ artifacts: { ...s.artifacts, [sessionId]: artifacts } })),
      setActiveTab: (tab) => set({ activeTab: tab }),
      setIsFullscreen: (v) => set({ isFullscreen: v }),
      setIsOpen: (v) => set({ isOpen: v }),
      setPanelWidth: (w) => set({ panelWidth: Math.max(360, Math.min(1200, w)) }),
      setRenderError: (err) => set({ renderError: err }),
      toggleFullscreen: () => set((s) => ({ isFullscreen: !s.isFullscreen })),
    }),
    {
      name: 'artifact-runtime-store',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        activeTab: state.activeTab,
        panelWidth: state.panelWidth,
        isFullscreen: state.isFullscreen,
        isOpen: state.isOpen,
        currentArtifact: state.currentArtifact,
      }),
    }
  )
);
