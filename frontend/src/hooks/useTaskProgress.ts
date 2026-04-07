import { useEffect, useState } from "react";
import { getTask, TaskState } from "../api/taskApi";

export function useTaskProgress(taskId: string | null) {
  const [task, setTask] = useState<TaskState | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!taskId) {
      setTask(null);
      setError(null);
      return;
    }

    let stopped = false;
    let timer: number | undefined;

    const poll = async () => {
      try {
        const nextTask = await getTask(taskId);
        if (stopped) {
          return;
        }
        setTask(nextTask);
        setError(null);
        if (!["completed", "failed"].includes(nextTask.status)) {
          timer = window.setTimeout(poll, 1200);
        }
      } catch (err) {
        if (!stopped) {
          setError(err instanceof Error ? err.message : "进度查询失败");
          timer = window.setTimeout(poll, 2200);
        }
      }
    };

    poll();

    return () => {
      stopped = true;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [taskId]);

  return { task, error };
}
