import { TaskConfig, TransitionType } from "../api/taskApi";

interface ConfigPanelProps {
  value: TaskConfig;
  onChange: (value: TaskConfig) => void;
  disabled?: boolean;
}

const transitions: Array<{ value: TransitionType; label: string }> = [
  { value: "fade", label: "Fade" },
  { value: "crossfade", label: "Crossfade" },
  { value: "cut", label: "Cut" },
];

export function ConfigPanel({ value, onChange, disabled }: ConfigPanelProps) {
  const update = <Key extends keyof TaskConfig>(key: Key, nextValue: TaskConfig[Key]) => {
    onChange({ ...value, [key]: nextValue });
  };

  return (
    <section className="panel">
      <div className="section-kicker">参数</div>
      <div className="field-grid">
        <label className="field">
          <span>目标时长</span>
          <input
            type="number"
            min={15}
            max={900}
            value={value.target_duration}
            disabled={disabled}
            onChange={(event) => update("target_duration", Number(event.target.value))}
          />
        </label>

        <label className="field">
          <span>钩子时长</span>
          <input
            type="number"
            min={3}
            max={20}
            value={value.hook_duration}
            disabled={disabled}
            onChange={(event) => update("hook_duration", Number(event.target.value))}
          />
        </label>

        <label className="field">
          <span>转场</span>
          <select
            value={value.transition_type}
            disabled={disabled}
            onChange={(event) => update("transition_type", event.target.value as TransitionType)}
          >
            {transitions.map((transition) => (
              <option key={transition.value} value={transition.value}>
                {transition.label}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>转场秒数</span>
          <input
            type="number"
            min={0.1}
            max={2}
            step={0.1}
            value={value.transition_duration}
            disabled={disabled}
            onChange={(event) => update("transition_duration", Number(event.target.value))}
          />
        </label>
      </div>

      <div className="switch-row">
        <label className="switch">
          <input
            type="checkbox"
            checked={value.enable_comfyui}
            disabled={disabled}
            onChange={(event) => update("enable_comfyui", event.target.checked)}
          />
          <span>ComfyUI 增强</span>
        </label>
        <label className="switch">
          <input
            type="checkbox"
            checked={value.auto_insert_materials}
            disabled={disabled}
            onChange={(event) => update("auto_insert_materials", event.target.checked)}
          />
          <span>自动插入素材</span>
        </label>
      </div>
    </section>
  );
}
