import { create } from 'zustand';

interface UIState {
  sidebarCollapsed: boolean;
  inspectorOpen: boolean;
  isMobileSidebarOpen: boolean;
  commandPaletteOpen: boolean;
  setSidebarCollapsed: (v: boolean) => void;
  toggleSidebar: () => void;
  setInspectorOpen: (v: boolean) => void;
  toggleInspector: () => void;
  setMobileSidebarOpen: (v: boolean) => void;
  setCommandPaletteOpen: (v: boolean) => void;
}

export const useUIStore = create<UIState>((set) => ({
  sidebarCollapsed: false,
  inspectorOpen: true,
  isMobileSidebarOpen: false,
  commandPaletteOpen: false,

  setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
  toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
  setInspectorOpen: (v) => set({ inspectorOpen: v }),
  toggleInspector: () => set((s) => ({ inspectorOpen: !s.inspectorOpen })),
  setMobileSidebarOpen: (v) => set({ isMobileSidebarOpen: v }),
  setCommandPaletteOpen: (v) => set({ commandPaletteOpen: v }),
}));
