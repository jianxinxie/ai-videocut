import { TaskState } from "../api/taskApi";

interface ProgressPanelProps {
  task: TaskState | null;
  error: string | null;
  submitting: boolean;
}

export function ProgressPanel({ task, error, submitting }: ProgressPanelProps) {
  const progress = task?.progress ?? (submitting ? 3 : 0);
  const statusText = task?.message ?? (submitting ? "正在上传" : "等待任务");

  return (
    <section className="panel progress-panel">
      <div className="section-kicker">进度</div>
      <div className="progress-head">
        <strong>{statusText}</strong>
        <span>{progress}%</span>
      </div>
      <div className="progress-track" aria-label="处理进度">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
      <dl className="status-grid">
        <div>
          <dt>任务</dt>
          <dd>{task?.task_id ?? "-"}</dd>
        </div>
        <div>
          <dt>阶段</dt>
          <dd>{task?.stage ?? "-"}</dd>
        </div>
        <div>
          <dt>状态</dt>
          <dd>{task?.status ?? "-"}</dd>
        </div>
      </dl>
      {(error || task?.error) && <p className="error-text">{error ?? task?.error}</p>}
    </section>
  );
}
