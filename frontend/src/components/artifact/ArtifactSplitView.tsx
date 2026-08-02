import React from 'react';
import { ArtifactCodeViewer } from './ArtifactCodeViewer';
import { ArtifactRuntimeIframe } from './ArtifactRuntimeIframe';
import { ArtifactMarkdownViewer } from './ArtifactMarkdownViewer';
import type { Artifact } from '@/types';

interface ArtifactSplitViewProps {
  artifact: Artifact;
}

export const ArtifactSplitView = React.memo(function ArtifactSplitView({
  artifact,
}: ArtifactSplitViewProps) {
  return (
    <div style={{ display: 'flex', width: '100%', height: '100%', overflow: 'hidden' }}>
      {/* Code half */}
      <div style={{ flex: 1, borderRight: '1px solid var(--color-border)', overflow: 'hidden', height: '100%' }}>
        <ArtifactCodeViewer artifact={artifact} />
      </div>

      {/* Preview half */}
      <div style={{ flex: 1, overflow: 'hidden', height: '100%' }}>
        {artifact.artifact_type === 'markdown' ? (
          <div style={{ height: '100%', overflow: 'auto' }}>
            <ArtifactMarkdownViewer artifact={artifact} />
          </div>
        ) : (
          <ArtifactRuntimeIframe artifact={artifact} />
        )}
      </div>
    </div>
  );
});
