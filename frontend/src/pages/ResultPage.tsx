import { absoluteServerUrl, TaskState } from "../api/taskApi";
import { MetadataPanel } from "../components/MetadataPanel";
import { ProgressPanel } from "../components/ProgressPanel";
import { VideoPlayer } from "../components/VideoPlayer";

interface ResultPageProps {
  task: TaskState | null;
  error: string | null;
  submitting: boolean;
}

export function ResultPage({ task, error, submitting }: ResultPageProps) {
  const videoUrl = absoluteServerUrl(task?.result?.video_url);
  const metadataUrl = absoluteServerUrl(task?.result?.metadata_url);

  return (
    <div className="result-stack">
      <ProgressPanel task={task} error={error} submitting={submitting} />
      <VideoPlayer videoUrl={videoUrl} metadataUrl={metadataUrl} />
      <MetadataPanel metadataUrl={metadataUrl} />
    </div>
  );
}
