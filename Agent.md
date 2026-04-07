# Agent.md

## 项目名称
AI Highlight Video Agent

## 项目目标
构建一个本地优先的视频高光剪辑系统，后端使用 Python，AI 工作流使用 ComfyUI，前端提供可视化操作页面。系统需要完成以下能力：

1. 上传长视频和辅助素材
2. 自动分析长视频内容
3. 自动截取 3 分钟左右的高光视频
4. 自动选择最吸引人的开头钩子片段
5. 自动插入辅助素材
6. 自动添加平滑转场
7. 支持本地部署，后续可迁移到云服务器

---

## 一、总体架构

系统采用前后端分离架构：

- 前端：React + Vite
- 后端：FastAPI
- AI 工作流：ComfyUI
- 视频处理：FFmpeg
- 任务调度：FastAPI BackgroundTasks / Celery（后续可扩展）
- 存储：
  - 本地阶段：本地磁盘
  - 云端阶段：对象存储 + 数据库

### 架构职责划分

#### 1. 前端
负责：
- 文件上传
- 参数配置
- 查看任务进度
- 预览和下载结果视频

#### 2. FastAPI 后端
负责：
- 接收上传文件
- 创建剪辑任务
- 调用视频分析模块
- 调用 ComfyUI workflow
- 调用 FFmpeg 完成剪辑、转场、合成
- 返回进度与结果

#### 3. ComfyUI
负责：
- AI 辅助分析
- 关键帧打分
- 钩子封面图生成
- 风格统一增强
- 可选的补帧、画面增强、封面生成

> 注意：ComfyUI 不是主剪辑器。
> 真正的视频剪切、拼接、转场建议由 Python + FFmpeg 完成。
> ComfyUI 主要承担 AI 能力增强。

#### 4. FFmpeg
负责：
- 视频切片
- 拼接
- 淡入淡出 / crossfade / 其他转场
- 混入 B-roll / 其他素材
- 输出最终 mp4

---

## 二、项目目录结构

建议让 Codex 按如下结构生成项目：

```bash
ai-highlight-video/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── routes_upload.py
│   │   │   ├── routes_tasks.py
│   │   │   └── routes_result.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logger.py
│   │   │   └── constants.py
│   │   ├── models/
│   │   │   ├── task.py
│   │   │   └── schemas.py
│   │   ├── services/
│   │   │   ├── video_analyzer.py
│   │   │   ├── highlight_selector.py
│   │   │   ├── hook_selector.py
│   │   │   ├── material_inserter.py
│   │   │   ├── transition_service.py
│   │   │   ├── ffmpeg_service.py
│   │   │   ├── comfyui_service.py
│   │   │   └── task_service.py
│   │   ├── utils/
│   │   │   ├── file_utils.py
│   │   │   ├── time_utils.py
│   │   │   └── ffmpeg_utils.py
│   │   └── workers/
│   │       └── video_pipeline.py
│   ├── uploads/
│   ├── outputs/
│   ├── temp/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── taskApi.ts
│   │   │   └── uploadApi.ts
│   │   ├── components/
│   │   │   ├── UploadForm.tsx
│   │   │   ├── ProgressPanel.tsx
│   │   │   ├── VideoPlayer.tsx
│   │   │   ├── MaterialList.tsx
│   │   │   └── ConfigPanel.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   └── ResultPage.tsx
│   │   ├── hooks/
│   │   │   └── useTaskProgress.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
│
├── comfyui-workflows/
│   ├── score_video_workflow.json
│   ├── hook_cover_workflow.json
│   └── enhance_frame_workflow.json
│
├── scripts/
│   ├── start_backend.sh
│   ├── start_frontend.sh
│   └── start_all.sh
│
└── Agent.md
```

---

## 三、核心功能设计

### 1. 上传视频
用户上传：
- 主视频（必传）
- 辅助素材（可选：视频、图片、音频）

后端保存到：
- `backend/uploads/{task_id}/source.mp4`
- `backend/uploads/{task_id}/materials/...`

---

### 2. 视频分析模块
目标：将长视频拆分为可评分片段。

建议实现步骤：

#### Step 1：镜头切分
使用以下方案之一：
- PySceneDetect
- OpenCV + 帧差
- ffmpeg scene detection

输出：
```json
[
  {"start": 0.0, "end": 5.2},
  {"start": 5.2, "end": 11.8},
  {"start": 11.8, "end": 18.4}
]
```

#### Step 2：音频特征分析
提取：
- 音量峰值
- 语速变化
- 音乐高潮
- 情绪波动

建议库：
- librosa
- pydub
- pyAudioAnalysis

#### Step 3：视觉特征分析
提取：
- 运动强度
- 人脸/人物出现频率
- 表情变化
- 画面复杂度
- 特定目标出现（可扩展）

#### Step 4：AI 打分
综合计算每个片段的高光分数：

```python
score = (
    visual_score * 0.4 +
    audio_score * 0.3 +
    emotion_score * 0.2 +
    semantic_score * 0.1
)
```

输出：
```json
[
  {"start": 0.0, "end": 5.2, "score": 0.71},
  {"start": 5.2, "end": 11.8, "score": 0.82}
]
```

---

### 3. 开头钩子选择
目标：从全片中挑选最抓人的 5~10 秒片段作为开头。

规则建议：
1. 从高分片段中选择分数最高的一段
2. 避免剧透过重，可配置
3. 优先有强烈情绪、冲突、高潮、夸张动作的片段
4. 钩子长度默认 6~10 秒

伪代码：
```python
def select_hook(scored_segments):
    sorted_segments = sorted(scored_segments, key=lambda x: x["score"], reverse=True)
    return sorted_segments[0]
```

---

### 4. 高光片段选择
目标：在扣除开头钩子后，选出剩余 170 秒左右的高光片段。

策略：
1. 按分数倒序排序
2. 保证片段之间尽量不重复、时间分布合理
3. 控制节奏，不要全部都是最高能量片段
4. 支持插入讲述片段，避免成片过于碎片化

伪代码：
```python
def select_highlights(segments, target_duration=180, hook_duration=10):
    remain = target_duration - hook_duration
    selected = []
    total = 0
    for seg in sorted(segments, key=lambda x: x["score"], reverse=True):
        duration = seg["end"] - seg["start"]
        if total + duration <= remain:
            selected.append(seg)
            total += duration
        if total >= remain:
            break
    return selected
```

---

### 5. 辅助素材插入
目标：将外部素材智能插入到主视频高光中。

素材包括：
- B-roll
- 表情包
- Logo
- 截图
- 氛围视频
- 补充镜头

插入方式：
1. 手动指定插入点
2. 规则插入
3. AI 推荐插入点

推荐策略：
- 当某高光片段节奏过快时插入缓冲素材
- 当语义需要补充说明时插入说明素材
- 在片段切换前后插入过渡素材

输出：
```json
[
  {
    "type": "material",
    "file": "broll1.mp4",
    "insert_at": 42.5,
    "duration": 2.5
  }
]
```

---

### 6. 平滑转场
转场方式建议支持：
- cut
- fade in / fade out
- crossfade
- blur transition
- zoom transition
- swipe transition

MVP 阶段优先实现：
- 普通硬切
- crossfade
- fade

FFmpeg 示例：
```bash
ffmpeg -i clip1.mp4 -i clip2.mp4 \
-filter_complex "xfade=transition=fade:duration=1:offset=4" \
output.mp4
```

后端统一封装：
```python
def apply_transition(clip_a, clip_b, transition_type="crossfade", duration=0.8):
    ...
```

---

## 四、ComfyUI 集成设计

### ComfyUI 的定位
ComfyUI 在此项目中承担 AI 辅助能力，而不是整条视频编辑流水线的唯一执行器。

可用方向：
1. 关键帧增强
2. 封面图生成
3. 风格统一
4. 特定帧修复
5. 生成转场素材
6. 对关键片段做 AI 视觉评分

### 调用方式
通过 Python 调用 ComfyUI HTTP API。

建议封装 `comfyui_service.py`

职责：
- 加载 workflow JSON
- 替换 workflow 输入参数
- 发送请求到 ComfyUI
- 查询执行状态
- 获取输出结果路径

伪代码：
```python
class ComfyUIService:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def run_workflow(self, workflow: dict) -> dict:
        # POST /prompt
        pass

    def wait_for_result(self, prompt_id: str) -> dict:
        # poll /history/{prompt_id}
        pass
```

### 推荐 workflow
1. `score_video_workflow.json`
   - 对关键帧进行评分或特征提取
2. `hook_cover_workflow.json`
   - 生成钩子封面 / 标题图
3. `enhance_frame_workflow.json`
   - 对关键帧进行增强

---

## 五、后端 API 设计

### 1. 上传并创建任务
**POST** `/api/tasks`

FormData:
- source_video: file
- materials: file[]
- config: json string

返回：
```json
{
  "task_id": "task_xxx",
  "status": "created"
}
```

---

### 2. 启动处理
也可以在创建任务时自动触发，或者拆成单独接口：

**POST** `/api/tasks/{task_id}/start`

返回：
```json
{
  "task_id": "task_xxx",
  "status": "queued"
}
```

---

### 3. 查询进度
**GET** `/api/tasks/{task_id}`

返回：
```json
{
  "task_id": "task_xxx",
  "status": "processing",
  "progress": 46,
  "stage": "selecting_highlights",
  "message": "正在选择高光片段"
}
```

---

### 4. 获取结果
**GET** `/api/tasks/{task_id}/result`

返回：
```json
{
  "task_id": "task_xxx",
  "status": "completed",
  "video_url": "/outputs/task_xxx/highlight.mp4",
  "metadata_url": "/outputs/task_xxx/metadata.json"
}
```

---

### 5. WebSocket 进度
**WS** `/ws/tasks/{task_id}`

推送消息：
```json
{
  "task_id": "task_xxx",
  "stage": "rendering_final_video",
  "progress": 87,
  "message": "正在合成最终视频"
}
```

---

## 六、任务状态机设计

任务状态建议：

- `created`
- `queued`
- `analyzing`
- `selecting_hook`
- `selecting_highlights`
- `inserting_materials`
- `applying_transitions`
- `enhancing_with_comfyui`
- `rendering_final_video`
- `completed`
- `failed`

建议维护统一 Task Model：

```python
class TaskStatus(str, Enum):
    CREATED = "created"
    QUEUED = "queued"
    ANALYZING = "analyzing"
    SELECTING_HOOK = "selecting_hook"
    SELECTING_HIGHLIGHTS = "selecting_highlights"
    INSERTING_MATERIALS = "inserting_materials"
    APPLYING_TRANSITIONS = "applying_transitions"
    ENHANCING_WITH_COMFYUI = "enhancing_with_comfyui"
    RENDERING_FINAL_VIDEO = "rendering_final_video"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 七、前端设计

### 页面
#### 1. 首页
功能：
- 上传主视频
- 上传辅助素材
- 设置参数
- 点击开始生成

参数面板：
- 目标时长（默认 180 秒）
- 钩子时长（默认 8 秒）
- 转场风格
- 是否启用 ComfyUI 增强
- 是否自动插入素材

#### 2. 任务页 / 结果页
功能：
- 显示当前状态
- 显示进度条
- 显示阶段说明
- 任务完成后可直接播放视频
- 下载结果和 metadata

### 核心组件
- `UploadForm.tsx`
- `ConfigPanel.tsx`
- `ProgressPanel.tsx`
- `VideoPlayer.tsx`
- `MaterialList.tsx`

### 状态管理
MVP 可直接使用：
- React hooks
- Zustand（可选）

---

## 八、本地部署要求

### 本地开发环境
- Python 3.11+
- Node.js 20+
- FFmpeg
- ComfyUI
- Git

### 后端依赖建议
```txt
fastapi
uvicorn
python-multipart
pydantic
httpx
opencv-python
numpy
librosa
pyscenedetect
ffmpeg-python
aiofiles
websockets
```

### 前端依赖建议
```bash
npm install react react-dom axios zustand
npm install -D vite typescript @types/react @types/react-dom
```

### 本地启动方式
#### 1. 启动 ComfyUI
默认地址：
```bash
http://127.0.0.1:8188
```

#### 2. 启动后端
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

#### 3. 启动前端
```bash
cd frontend
npm run dev
```

前端默认地址：
```bash
http://127.0.0.1:5173
```

---

## 九、云端迁移预留

后续迁移到云服务器时，代码要尽量避免和本地环境强绑定。

需要预留的点：

### 1. 文件存储抽象
本地阶段：
- 直接写磁盘

云端阶段：
- 切换为 OSS / S3 / MinIO

建议封装：
```python
class StorageService:
    def save_upload(self, file): ...
    def get_file_url(self, path): ...
```

### 2. 任务队列抽象
本地阶段：
- BackgroundTasks / asyncio

云端阶段：
- Celery + Redis
- 或者 Dramatiq / RQ

### 3. 数据库抽象
本地阶段：
- SQLite / JSON 文件

云端阶段：
- PostgreSQL / MySQL

### 4. 配置集中化
统一使用 `.env`

例如：
```env
APP_ENV=local
COMFYUI_BASE_URL=http://127.0.0.1:8188
UPLOAD_DIR=./uploads
OUTPUT_DIR=./outputs
TEMP_DIR=./temp
```

---

## 十、Codex 实现要求

请 Codex 按以下优先级实现：

### 第一阶段：MVP
必须完成：
1. 前后端项目初始化
2. 视频上传
3. 镜头切分
4. 高光评分
5. 开头钩子选择
6. 高光拼接
7. 简单转场
8. 结果输出
9. 前端进度展示

### 第二阶段：增强版
在 MVP 完成后继续实现：
1. 辅助素材自动插入
2. ComfyUI 接入
3. 关键帧增强
4. 封面生成
5. WebSocket 实时进度
6. metadata 可视化

### 第三阶段：云端准备
1. 存储抽象
2. 队列抽象
3. 数据库持久化
4. Docker 化
5. 部署脚本

---

## 十一、验收标准

MVP 完成标准：

1. 用户可以在前端上传一个长视频
2. 可以配置目标时长和转场类型
3. 后端能够自动生成一个约 3 分钟的视频
4. 结果视频前 5~10 秒是钩子片段
5. 成片包含多个高光片段
6. 片段之间至少支持 fade 或 crossfade
7. 前端可以查看进度并播放结果视频

增强版完成标准：

1. 可上传辅助素材并插入成片
2. 可启用 ComfyUI 增强
3. 可导出 metadata.json
4. 后续可直接迁移到云服务器

---

## 十二、建议补充功能

后续可以继续扩展：
1. 自动字幕
2. 自动标题生成
3. 自动封面生成
4. AI 配音
5. 节奏点卡点剪辑
6. 多模板输出
7. 适配抖音 / YouTube Shorts / Reels 的横竖屏版本
8. 人物追踪
9. 主体识别
10. 语义摘要剪辑

---

## 十三、给 Codex 的最终指令

请基于本 Agent.md 直接生成一个可运行的项目，要求：

1. 后端使用 FastAPI
2. 前端使用 React + Vite + TypeScript
3. 使用 FFmpeg 实现实际视频剪辑
4. 使用 Python 服务层封装视频分析、片段选择、转场、合成
5. 预留 ComfyUI HTTP API 集成点
6. 代码结构清晰，便于后续部署到云服务器
7. 先保证本地可运行，再考虑云端扩展
8. 所有核心步骤都要有日志
9. 所有 API 都要有基础错误处理
10. 输出 README，说明本地运行方式
