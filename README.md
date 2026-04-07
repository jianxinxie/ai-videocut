# ai-videocut

本地优先的 AI 高光视频剪辑 MVP。后端使用 FastAPI，前端使用 React + Vite + TypeScript，实际视频切片、拼接和转场由 FFmpeg 执行，ComfyUI 作为后续 AI 增强入口预留。

## 当前能力

- 上传一个长视频和可选辅助素材
- 配置目标时长、钩子时长、转场类型和转场秒数
- 使用 FFmpeg 场景检测，失败时回退到均匀分段
- 使用音量和片段节奏启发式评分高光片段
- 自动选择开头钩子片段
- 开启自动插入素材后，支持把图片和视频素材插入最终时间线
- 输出 `highlight.mp4` 和 `metadata.json`
- 前端轮询任务进度并播放/下载结果
- 前端展示 metadata 摘要、时间线和 ComfyUI 连接状态
- 预留 ComfyUI HTTP API service、workflow JSON、WebSocket 进度端点

## 环境要求

- Python 3.11+
- Node.js 20+
- FFmpeg 和 FFprobe
- 可选：ComfyUI，默认地址 `http://127.0.0.1:8188`

检查 FFmpeg：

```bash
ffmpeg -version
ffprobe -version
```

## 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端地址：

```text
http://127.0.0.1:8000
```

## 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端地址：

```text
http://127.0.0.1:5173
```

## 一键本地启动

```bash
./scripts/start_all.sh
```

脚本会分别启动后端和前端。第一次运行会安装 Python 和 Node 依赖。

## Docker 启动

```bash
docker compose up --build
```

或者：

```bash
./scripts/deploy_local.sh
```

容器模式下前端地址：

```text
http://127.0.0.1:8080
```

后端地址：

```text
http://127.0.0.1:8000
```

容器内默认把上传、输出、临时文件和任务状态保存到 Docker volume `backend-data`。如果本机运行 ComfyUI，后端会通过 `http://host.docker.internal:8188` 访问。

## API

创建并自动启动任务：

```text
POST /api/tasks
```

FormData：

- `source_video`: 必传视频文件
- `materials`: 可选素材文件，可重复
- `config`: JSON 字符串

配置示例：

```json
{
  "target_duration": 180,
  "hook_duration": 8,
  "transition_type": "fade",
  "transition_duration": 0.6,
  "enable_comfyui": false,
  "auto_insert_materials": false
}
```

查询进度：

```text
GET /api/tasks/{task_id}
```

获取结果：

```text
GET /api/tasks/{task_id}/result
```

WebSocket 进度：

```text
WS /ws/tasks/{task_id}
```

ComfyUI 状态：

```text
GET /api/comfyui/health
```

## 输出目录

本地生成文件默认写入：

```text
backend/uploads/{task_id}/
backend/outputs/{task_id}/highlight.mp4
backend/outputs/{task_id}/metadata.json
backend/temp/
```

这些目录已在 `.gitignore` 中排除，避免提交上传素材和生成视频。

任务状态默认写入：

```text
backend/data/tasks.json
```

这个文件用于本地开发时跨后端重启恢复任务状态，同样已排除在 Git 外。

## 素材插入

`auto_insert_materials=true` 时，后端会把支持的视觉素材插到高光片段之间：

- 支持：`jpg`、`jpeg`、`png`、`webp`、`bmp`、`mp4`、`mov`、`mkv`、`webm`、`avi`、`m4v`
- 暂不直接混音：`mp3`、`wav`、`aac`、`m4a`、`flac`、`ogg`

音频素材会保留在 metadata 规划中，后续可以接入独立音轨混音策略。

## 实现边界

这是 MVP，不是完整 AI 剪辑系统。当前高光评分是 FFmpeg 场景检测 + 音量/片段长度/节奏启发式；ComfyUI workflow 是可替换占位模板，尚未绑定真实节点图。当前已预留本地存储、JSON 任务仓库、队列接口和 Docker 部署入口；后续可以替换为 OSS/S3、PostgreSQL、Celery/Redis，并接入真实 ComfyUI 节点图。
