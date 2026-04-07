STAGE_MESSAGES: dict[str, str] = {
    "created": "任务已创建",
    "queued": "任务已进入处理队列",
    "analyzing": "正在分析视频片段",
    "selecting_hook": "正在选择开头钩子片段",
    "selecting_highlights": "正在选择高光片段",
    "inserting_materials": "正在规划辅助素材插入点",
    "applying_transitions": "正在准备转场与片段",
    "enhancing_with_comfyui": "正在调用 ComfyUI 增强流程",
    "rendering_final_video": "正在合成最终视频",
    "completed": "处理完成",
    "failed": "处理失败",
}

SUPPORTED_TRANSITIONS = {"cut", "fade", "crossfade"}
