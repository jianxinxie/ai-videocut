export type TransitionType = "cut" | "fade" | "crossfade";

export interface TaskConfig {
  target_duration: number;
  hook_duration: number;
  transition_type: TransitionType;
  transition_duration: number;
  enable_comfyui: boolean;
  auto_insert_materials: boolean;
}

export interface TaskResultLinks {
  video_url: string | null;
  metadata_url: string | null;
}

export interface TaskState {
  task_id: string;
  status: string;
  progress: number;
  stage: string;
  message: string;
  error: string | null;
  result: TaskResultLinks | null;
  created_at: number;
  updated_at: number;
}

export interface SegmentMetadata {
  start: number;
  end: number;
  score: number;
  duration: number;
  reasons?: Record<string, unknown>;
}

export interface MaterialInsertionMetadata {
  type: string;
  file: string;
  source_path: string | null;
  media_type: string;
  insert_at: number;
  duration: number;
  after_segment_index: number | null;
  rendered: boolean;
}

export interface TimelineMetadata {
  kind: string;
  file: string;
  start: number;
  end: number;
  duration: number;
  label: string;
}

export interface TaskMetadata {
  task_id: string;
  transition_type: string;
  hook: SegmentMetadata;
  highlights: SegmentMetadata[];
  material_insertions: MaterialInsertionMetadata[];
  timeline: TimelineMetadata[];
  result_video: string;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";
const SERVER_BASE = API_BASE.replace(/\/api\/?$/, "");

export function absoluteServerUrl(path: string | null | undefined): string | null {
  if (!path) {
    return null;
  }
  if (/^https?:\/\//.test(path)) {
    return path;
  }
  return `${SERVER_BASE}${path}`;
}

export async function createTask(
  sourceVideo: File,
  materials: File[],
  config: TaskConfig,
): Promise<{ task_id: string; status: string }> {
  const body = new FormData();
  body.append("source_video", sourceVideo);
  for (const material of materials) {
    body.append("materials", material);
  }
  body.append("config", JSON.stringify(config));

  const response = await fetch(`${API_BASE}/tasks`, {
    method: "POST",
    body,
  });
  return parseJsonResponse(response);
}

export async function getTask(taskId: string): Promise<TaskState> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}`);
  return parseJsonResponse(response);
}

export async function getMetadata(metadataUrl: string): Promise<TaskMetadata> {
  const response = await fetch(metadataUrl);
  return parseJsonResponse(response);
}

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `请求失败：${response.status}`;
    try {
      const payload = await response.json();
      message = payload.detail ?? message;
    } catch {
      // Keep the HTTP status fallback.
    }
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}
