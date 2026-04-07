export interface UploadLimits {
  source_video: string;
  materials: string;
  note: string;
  max_materials_recommended: number;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export async function getUploadLimits(): Promise<UploadLimits> {
  const response = await fetch(`${API_BASE}/uploads/limits`);
  if (!response.ok) {
    throw new Error(`请求失败：${response.status}`);
  }
  return response.json() as Promise<UploadLimits>;
}
