# Findings & Decisions

## Requirements
- Build a local-first AI highlight video editor from `Agent.md`.
- Backend: FastAPI, Python service layers, FFmpeg for real clipping/composition, ComfyUI HTTP API integration point, logs and basic API error handling.
- Frontend: React + Vite + TypeScript, upload source video and optional materials, configure target duration/hook duration/transition/ComfyUI/material insertion, show task progress, play/download final output.
- MVP: initialize frontend/backend projects, upload video, segment video, score highlights, select hook, concatenate high-scoring clips with simple transitions, output final video and show progress.
- Enhanced phase: material insertion, ComfyUI, keyframe enhancement, cover generation, WebSocket progress, metadata visualization.
- Cloud phase: storage abstraction, task queue abstraction, database persistence, Docker/deployment scripts.

## Research Findings
- Repository started with only `README.md`, staged `Agent.md`, and newly created `.gitignore`.
- `Agent.md` specifies the target structure: `backend/app/...`, `frontend/src/...`, `comfyui-workflows/`, and `scripts/`.
- `rg` is unavailable in this environment, so file discovery uses `find`.
- Node v24.5.0, npm 11.5.1, and FFmpeg 4.4.2 are available.
- Python compile, frontend build, backend import, and a direct FFmpeg pipeline smoke test completed successfully.
- Material insertion now renders supported visual materials into the final timeline when `auto_insert_materials` is enabled.
- Frontend now visualizes metadata summary and timeline in addition to linking `metadata.json`.
- ComfyUI health endpoint returns `available`/`unavailable`; with no local ComfyUI running it correctly returned `unavailable`.
- Cloud-prep phase should avoid introducing required external services before Docker/local workflow is stable.
- Docker Compose now builds both backend and frontend images; backend image installs FFmpeg.
- Frontend Docker build reported `npm audit` with 2 moderate severity vulnerabilities from the current dependency tree.
- No required implementation phase remains; optimization work should target reliability and maintainability.
- Upload route currently creates and persists a task before upload files are saved; upload failures should mark the task as failed.
- FFmpeg render methods duplicate final transition/concat logic across `render_clips` and `render_items`.
- Upload failures now mark tasks failed before returning a 500 response.
- JSON task repository now moves invalid JSON stores to `.bad` and skips invalid individual records.
- FFmpeg fade/crossfade/concat finalization now shares one method.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Start with a complete local MVP scaffold | User asked to analyze requirements and begin implementation immediately. |
| Use FFmpeg CLI helpers | Gives the backend real video processing while keeping dependencies simple. |
| Use fallback uniform segmentation | Scene detection can fail on some videos; the MVP should still produce output. |
| Poll task progress from React | Simpler than WebSocket for MVP; WebSocket can be added later without changing core task state. |
| Use a dark industrial/editorial frontend | Fits a video cutting console and avoids generic landing-page UI. |
| Use placeholder ComfyUI workflow JSON | Real node graphs depend on installed ComfyUI nodes/models; placeholders document the contract for replacement. |
| Render only supported visual materials into the timeline | Videos and images can be normalized to video clips via FFmpeg; arbitrary audio insertion is a separate mixing problem and should remain metadata-only for now. |
| Use JSON task repository before a real database | It gives restart persistence and a clean repository boundary while keeping local setup simple. |
| Use Nginx to proxy frontend container requests | Browser clients cannot call Docker service names directly; proxying `/api`, `/outputs`, and `/ws` keeps the public base URL simple. |
| Preserve API behavior during optimization | The current frontend and smoke tests rely on existing task/result URLs; hardening should avoid changing public API shapes. |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| No existing app skeleton | Create backend/frontend/scripts/workflow directories from scratch. |
| Frontend palette initially used warm near-white tones | Adjusted to cool gray/charcoal/red to follow project UI constraints. |
| Docker backend build is slow because FFmpeg pulls many Debian packages | Build still succeeds; future optimization can use a smaller FFmpeg base image or a pinned runtime layer. |

## Resources
- `Agent.md`
- `/home/jim/.agents/skills/planning-with-files/SKILL.md`
- `/home/jim/.agents/skills/frontend-design/SKILL.md`
- `backend/app/main.py`
- `frontend/src/pages/HomePage.tsx`
- `README.md`

## Visual/Browser Findings
- No browser or image research used.
