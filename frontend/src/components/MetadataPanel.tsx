import { useEffect, useState } from "react";
import { getMetadata, TaskMetadata } from "../api/taskApi";

interface MetadataPanelProps {
  metadataUrl: string | null;
}

export function MetadataPanel({ metadataUrl }: MetadataPanelProps) {
  const [metadata, setMetadata] = useState<TaskMetadata | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!metadataUrl) {
      setMetadata(null);
      setError(null);
      return;
    }

    let stopped = false;
    getMetadata(metadataUrl)
      .then((payload) => {
        if (!stopped) {
          setMetadata(payload);
          setError(null);
        }
      })
      .catch((err) => {
        if (!stopped) {
          setError(err instanceof Error ? err.message : "metadata 加载失败");
        }
      });

    return () => {
      stopped = true;
    };
  }, [metadataUrl]);

  if (!metadataUrl) {
    return null;
  }

  return (
    <section className="panel metadata-panel">
      <div className="section-kicker">Metadata</div>
      {error && <p className="error-text">{error}</p>}
      {!metadata && !error && <p className="muted">读取中</p>}
      {metadata && (
        <>
          <div className="metric-grid">
            <div>
              <span>钩子</span>
              <strong>{formatSeconds(metadata.hook.duration)}</strong>
            </div>
            <div>
              <span>高光</span>
              <strong>{metadata.highlights.length}</strong>
            </div>
            <div>
              <span>素材</span>
              <strong>{metadata.material_insertions.filter((item) => item.rendered).length}</strong>
            </div>
            <div>
              <span>转场</span>
              <strong>{metadata.transition_type}</strong>
            </div>
          </div>

          <div className="timeline-list">
            {metadata.timeline.map((item, index) => (
              <div className="timeline-row" key={`${item.label}-${index}`}>
                <span>{index + 1}</span>
                <div>
                  <strong>{labelForKind(item.kind)}</strong>
                  <p>{item.file}</p>
                </div>
                <em>{formatSeconds(item.duration)}</em>
              </div>
            ))}
          </div>
        </>
      )}
    </section>
  );
}

function formatSeconds(value: number) {
  return `${value.toFixed(1)}s`;
}

function labelForKind(kind: string) {
  if (kind === "source") {
    return "主视频";
  }
  if (kind === "material_image") {
    return "图片素材";
  }
  if (kind === "material_video") {
    return "视频素材";
  }
  return kind;
}
