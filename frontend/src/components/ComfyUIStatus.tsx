import { useEffect, useState } from "react";
import { ComfyUIHealth, getComfyUIHealth } from "../api/comfyuiApi";

export function ComfyUIStatus() {
  const [health, setHealth] = useState<ComfyUIHealth | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let stopped = false;

    const load = async () => {
      try {
        const nextHealth = await getComfyUIHealth();
        if (!stopped) {
          setHealth(nextHealth);
          setError(null);
        }
      } catch (err) {
        if (!stopped) {
          setError(err instanceof Error ? err.message : "ComfyUI 状态不可用");
        }
      }
    };

    load();
    const timer = window.setInterval(load, 10000);

    return () => {
      stopped = true;
      window.clearInterval(timer);
    };
  }, []);

  const available = health?.available ?? false;

  return (
    <section className="panel status-panel">
      <div className="section-kicker">ComfyUI</div>
      <div className="service-status">
        <span className={available ? "status-dot online" : "status-dot"} />
        <strong>{available ? "可用" : "未连接"}</strong>
      </div>
      <p className="muted">{health?.base_url ?? error ?? "检测中"}</p>
    </section>
  );
}
