# Task Plan: AI Highlight Video Agent MVP

## Goal
Build a locally runnable MVP for the AI Highlight Video Agent described in `Agent.md`, with FastAPI backend, React/Vite frontend, FFmpeg-based video clipping pipeline, progress reporting, and ComfyUI extension points.

## Current Phase
Phase 11

## Phases

### Phase 1: Requirements & Discovery
- [x] Read `Agent.md`
- [x] Identify MVP requirements and enhancement/deployment requirements
- [x] Check existing repository structure and Git state
- **Status:** complete

### Phase 2: Project Skeleton & Planning
- [x] Create backend, frontend, workflow, and script directories
- [x] Add project-level README and environment examples
- [x] Document architecture decisions
- **Status:** complete

### Phase 3: Backend MVP
- [x] Implement FastAPI app, task APIs, result APIs, and static output serving
- [x] Implement task model/state management and background video pipeline
- [x] Implement FFmpeg/FFprobe helpers, segment analysis, hook/highlight selection, transitions, and metadata output
- [x] Add ComfyUI service placeholder
- **Status:** complete

### Phase 4: Frontend MVP
- [x] Implement React + Vite + TypeScript project
- [x] Add upload/config form, material list, progress panel, and result player
- [x] Poll task progress and show result/download links
- **Status:** complete

### Phase 5: Scripts & Verification
- [x] Add local startup scripts and placeholder ComfyUI workflows
- [x] Run syntax/type-adjacent checks that do not require unavailable dependencies
- [x] Update documentation with local run instructions and constraints
- **Status:** complete

### Phase 6: Delivery
- [x] Review Git status and summarize created files
- [x] Call out remaining limits and next steps
- **Status:** complete

### Phase 7: Enhanced Workflow
- [x] Render supported auxiliary image/video materials into the final timeline when auto insertion is enabled
- [x] Add frontend metadata visualization instead of only linking raw JSON
- [x] Add ComfyUI health/status surface
- [x] Re-run backend/frontend verification and smoke tests
- **Status:** complete

### Phase 8: Cloud Preparation
- [x] Add local storage abstraction for uploads, outputs, temp files, and future object storage replacement
- [x] Add JSON task repository so local task state survives backend restarts
- [x] Add queue abstraction around FastAPI BackgroundTasks for later Celery/RQ migration
- [x] Add Dockerfiles, docker-compose, and deployment-oriented environment docs
- [x] Re-run compile/build/import checks
- **Status:** complete

### Phase 9: Optimization & Hardening
- [x] Harden task creation and upload failure handling
- [x] Make JSON task repository resilient to corrupt state files
- [x] Remove duplicated FFmpeg render finalization logic
- [x] Reduce Docker build noise and improve noninteractive behavior
- [x] Re-run backend/frontend verification and targeted smoke tests
- **Status:** complete

### Phase 10: Commit & Push
- [x] Stage project files
- [x] Create Git commit
- [x] Push to GitHub `origin/main`
- **Status:** complete

### Phase 11: Poetry & IDE Import Fix
- [x] Move Poetry `package-mode = false` under `[tool.poetry]`
- [x] Sync `requirements.txt` dependencies into `pyproject.toml`
- [x] Regenerate `poetry.lock`
- [x] Convert backend internal `app.*` imports to package-relative imports
- [x] Verify Poetry check, Python compile, and app import
- **Status:** complete

### Phase 12: Light UI Polish
- [x] Convert the frontend from dark workbench styling to a light cool-toned interface
- [x] Improve panels, upload controls, buttons, form focus states, progress display, status cards, and timeline readability
- [x] Keep existing React component structure and avoid changing backend behavior
- [x] Verify the frontend production build
- **Status:** complete

## Key Questions
1. How much of `Agent.md` should be implemented now? Answer: implement the MVP path end to end; reserve ComfyUI, advanced material insertion, WebSocket, database/queue/storage abstractions as extension points.
2. How should video analysis work without requiring heavyweight AI models? Answer: use FFmpeg/FFprobe first, with scene detection fallback to uniform segments and audio-volume scoring as the MVP heuristic.
3. How should task state persist? Answer: keep an in-memory registry for local MVP and write output `metadata.json`; leave database abstraction for later cloud phase.

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| Build a runnable MVP instead of a full AI system | The requested system is large; `Agent.md` prioritizes local runnable MVP first. |
| Use FFmpeg CLI through Python subprocess | Keeps real video cutting/composition in FFmpeg and avoids hard dependency on Python FFmpeg wrappers for the first runnable version. |
| Use in-memory task state plus output metadata | Simple for local development; avoids premature database/queue complexity. |
| Keep uploaded/generated media ignored by Git | Prevents large local videos and transient outputs from entering the repository. |
| Keep ComfyUI workflows as placeholders | Real ComfyUI node graphs are environment-specific; the MVP exposes service and workflow files without pretending they are runnable node graphs. |
| Implement enhancement work incrementally | Material insertion and metadata visualization directly improve the current runnable MVP without forcing real ComfyUI node graphs. |
| Add cloud-prep abstractions without external services | The project still needs to run locally; JSON persistence and interface boundaries provide migration points without requiring Redis/Postgres/S3 now. |
| Optimize reliability before adding optional features | Existing phases are complete; hardening failure paths and duplicated render logic improves maintainability without expanding scope. |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `rg` not installed | 1 | Used `find`/`sed` for repository inspection. |

## Notes
- Existing `Agent.md` is already staged by the user; do not modify or unstage it.
- Existing `.gitignore` was created in the previous turn and should be preserved.
