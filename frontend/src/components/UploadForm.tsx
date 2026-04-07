import { FormEvent } from "react";
import { TaskConfig } from "../api/taskApi";
import { ComfyUIStatus } from "./ComfyUIStatus";
import { ConfigPanel } from "./ConfigPanel";
import { MaterialList } from "./MaterialList";

interface UploadFormProps {
  sourceVideo: File | null;
  materials: File[];
  config: TaskConfig;
  disabled?: boolean;
  onSourceChange: (file: File | null) => void;
  onMaterialsChange: (files: File[]) => void;
  onConfigChange: (config: TaskConfig) => void;
  onSubmit: () => void;
}

export function UploadForm({
  sourceVideo,
  materials,
  config,
  disabled,
  onSourceChange,
  onMaterialsChange,
  onConfigChange,
  onSubmit,
}: UploadFormProps) {
  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form className="upload-stack" onSubmit={submit}>
      <section className="panel primary-panel">
        <div className="section-kicker">视频</div>
        <label className="drop-zone">
          <input
            type="file"
            accept="video/*"
            disabled={disabled}
            onChange={(event) => onSourceChange(event.target.files?.[0] ?? null)}
          />
          <strong>{sourceVideo ? sourceVideo.name : "选择长视频"}</strong>
          <span>MP4、MOV、MKV</span>
        </label>
      </section>

      <section className="panel">
        <div className="section-kicker">素材</div>
        <label className="file-row">
          <span>添加 B-roll、图片或音频</span>
          <input
            type="file"
            multiple
            accept="video/*,image/*,audio/*"
            disabled={disabled}
            onChange={(event) => onMaterialsChange(Array.from(event.target.files ?? []))}
          />
        </label>
        <MaterialList files={materials} onRemove={(index) => onMaterialsChange(materials.filter((_, i) => i !== index))} />
      </section>

      <ConfigPanel value={config} onChange={onConfigChange} disabled={disabled} />
      <ComfyUIStatus />

      <button className="submit-button" type="submit" disabled={!sourceVideo || disabled}>
        开始生成
      </button>
    </form>
  );
}
