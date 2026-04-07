export interface ComfyUIHealth {
  base_url: string;
  available: boolean;
  status: "available" | "unavailable";
}

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000/api";

export async function getComfyUIHealth(): Promise<ComfyUIHealth> {
  const response = await fetch(`${API_BASE}/comfyui/health`);
  if (!response.ok) {
    throw new Error(`请求失败：${response.status}`);
  }
  return response.json() as Promise<ComfyUIHealth>;
}
