import { useState } from "react";
import { createTask, TaskConfig } from "../api/taskApi";
import { UploadForm } from "../components/UploadForm";
import { useTaskProgress } from "../hooks/useTaskProgress";
import { ResultPage } from "./ResultPage";

const defaultConfig: TaskConfig = {
  target_duration: 180,
  hook_duration: 8,
  transition_type: "fade",
  transition_duration: 0.6,
  enable_comfyui: false,
  auto_insert_materials: false,
};

export function HomePage() {
  const [sourceVideo, setSourceVideo] = useState<File | null>(null);
  const [materials, setMaterials] = useState<File[]>([]);
  const [config, setConfig] = useState<TaskConfig>(defaultConfig);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { task, error: progressError } = useTaskProgress(taskId);

  const isBusy = submitting || Boolean(task && !["completed", "failed"].includes(task.status));

  const submit = async () => {
    if (!sourceVideo) {
      setSubmitError("请选择长视频");
      return;
    }
    try {
      setSubmitting(true);
      setSubmitError(null);
      const created = await createTask(sourceVideo, materials, config);
      setTaskId(created.task_id);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "任务创建失败");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="workbench-title">
        <p>AI Highlight Video Agent</p>
        <h1>本地高光剪辑</h1>
      </section>

      <div className="workspace-grid">
        <UploadForm
          sourceVideo={sourceVideo}
          materials={materials}
          config={config}
          disabled={isBusy}
          onSourceChange={setSourceVideo}
          onMaterialsChange={setMaterials}
          onConfigChange={setConfig}
          onSubmit={submit}
        />
        <ResultPage task={task} error={submitError ?? progressError} submitting={submitting} />
      </div>
    </main>
  );
}
