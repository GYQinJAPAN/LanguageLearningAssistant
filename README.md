# Language Learning Assistant

本项目是一个本地可运行的 AI 翻译助手，当前阶段聚焦在基础翻译主流程、学习模式多结果生成和本地历史记录持久化：

- Backend: FastAPI
- Frontend: React + Vite
- LLM: OpenAI Chat Completions API

当前已支持 SQLite 本地历史记录和学习模式三版本翻译；暂不包含登录、收藏、用户设置、口语提示、复杂统计或 prompt 管理后台。

## Project Structure

```text
backend/
  app/
    core/          # settings and logger
    models/        # SQLAlchemy models
    prompts/       # style prompts and task templates
    routes/        # FastAPI routes
    schemas/       # request and response models
    services/      # LLM service
    utils/         # prompt manager
  data/            # local SQLite database, ignored by Git
frontend/
  src/
    config/        # frontend API config
    services/      # frontend API client
```

## Backend Setup

Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install backend dependencies:

```powershell
pip install -r backend\requirements.txt
```

Create `backend\.env`:

```env
OPENAI_API_KEY=your_api_key_here

APP_HOST=127.0.0.1
APP_PORT=8000
API_PREFIX=/api/v1
ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
LOG_LEVEL=INFO

OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=300
# OPENAI_BASE_URL=https://api.openai.com/v1

# Optional. Defaults to backend/data/app.db.
# DATABASE_URL=sqlite+aiosqlite:///C:/absolute/path/to/app.db
```

Start the backend:

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Backend health check:

```text
http://127.0.0.1:8000/health
```

`GET /health` only checks that the FastAPI app is running. It does not call OpenAI.

API docs:

```text
http://127.0.0.1:8000/docs
```

## Local Database

This stage uses SQLite through SQLAlchemy async APIs.

Default database file:

```text
backend/data/app.db
```

You can override it in `backend\.env`:

```env
DATABASE_URL=sqlite+aiosqlite:///C:/absolute/path/to/app.db
```

Initialization happens automatically on backend startup. The app runs `create_all` only, so it creates missing tables and does not delete old records.

Tables:

- `translation_history`: main source text, translated text, style, language, and timestamp.
- `translation_variants`: learning-mode versions linked by `history_id`; fields include `variant_type`, `translated_text`, `short_note`, `sort_order`, and `created_at`.

The SQLite file is ignored by Git via `backend/data/`, `*.db`, `*.sqlite`, and `*.sqlite3`.

To clear local history data, stop the backend and delete:

```powershell
Remove-Item backend\data\app.db
```

Then start the backend again. The table will be recreated automatically.

History endpoints:

```text
GET http://127.0.0.1:8000/api/v1/history?page=1&page_size=20
GET http://127.0.0.1:8000/api/v1/history?q=hello
GET http://127.0.0.1:8000/api/v1/history/{id}
DELETE http://127.0.0.1:8000/api/v1/history/{id}
DELETE http://127.0.0.1:8000/api/v1/history
```

The delete endpoints remove one history record by ID or clear all local history records. The frontend asks for confirmation before either destructive action.

Core translation endpoint:

```text
POST http://127.0.0.1:8000/api/v1/translate
```

The compatible request fields are:

```json
{
  "text": "你好",
  "style": "base_prompt",
  "source_lang": "auto",
  "target_lang": "English",
  "result_mode": "single"
}
```

`result_mode` is optional and defaults to `single`. In single mode, the response keeps the original success fields.

The compatible success response fields are:

```json
{
  "original_text": "你好",
  "translated_text": "Hello.",
  "style_requested": "base_prompt",
  "style_applied": "base_prompt",
  "source_lang": "auto",
  "target_lang": "English"
}
```

Learning mode uses the same endpoint:

```json
{
  "text": "我今天有点累，但是还是想和你聊天。",
  "style": "casual",
  "source_lang": "auto",
  "target_lang": "English",
  "result_mode": "learning"
}
```

The learning-mode response keeps `translated_text` as the natural version and adds `variants`:

```json
{
  "original_text": "我今天有点累，但是还是想和你聊天。",
  "translated_text": "I'm a bit tired today, but I still want to chat with you.",
  "style_requested": "casual",
  "style_applied": "casual",
  "source_lang": "auto",
  "target_lang": "English",
  "result_mode": "learning",
  "variants": [
    {
      "variant_type": "written",
      "label": "书面版",
      "translated_text": "I'm feeling a little tired today, but I would still like to talk with you.",
      "short_note": "More complete and slightly more polished."
    },
    {
      "variant_type": "natural",
      "label": "自然版",
      "translated_text": "I'm a bit tired today, but I still want to chat with you.",
      "short_note": "Closest to everyday natural expression."
    },
    {
      "variant_type": "spoken",
      "label": "口语版",
      "translated_text": "I'm kinda tired today, but I still wanna talk to you.",
      "short_note": "More relaxed and easy to say out loud."
    }
  ]
}
```

## Frontend Setup

Install frontend dependencies:

```powershell
cd frontend
npm install
```

The development environment file is `frontend\.env.development`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Keep `/api/v1` in `VITE_API_BASE_URL` for the current frontend contract. The frontend API client will trim trailing slashes, so both of these are valid:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1/
```

Start the frontend:

```powershell
cd frontend
npm run dev
```

Open the Vite URL shown in the terminal, usually:

```text
http://127.0.0.1:5173
```

## One-Command Local Start

From the project root, you can start backend and frontend in two PowerShell windows:

```powershell
.\start_dev.ps1
```

This script starts:

- Backend: `http://127.0.0.1:8000`
- Frontend: Vite dev server, usually `http://127.0.0.1:5173`
- Health check: `http://127.0.0.1:8000/health`

## Prompt Styles

Translation styles are read dynamically from:

```text
backend/app/prompts/*.txt
```

Examples:

- `base_prompt.txt`
- `casual.txt`
- `polite.txt`
- `professional.txt`

Style keys must contain only letters, numbers, underscores, or short hyphens. Invalid style keys return a 422 response. If a valid style key is requested but the prompt file is missing, the backend falls back to `base_prompt` and records a warning log.

Task templates are stored separately from style prompts:

```text
backend/app/prompts/tasks/translate_single.txt
backend/app/prompts/tasks/translate_learning_mode.txt
```

The backend combines one style prompt with one task template for each translation request. Style controls tone; `result_mode` controls whether the task returns one result or written/natural/spoken variants.

Learning-mode prompt files describe the translation task and expression-level differences only. The JSON output shape, allowed `variant_type` values, ordering, and display labels are controlled in backend Python code and response schemas.

## Environment Files

Do not commit real secrets. Use these templates as references:

- Backend: `backend/.env.example`
- Frontend: `frontend/.env.example`

Local backend environment:

```env
OPENAI_API_KEY=your_api_key_here
ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173
LOG_LEVEL=INFO
```

Local frontend environment, preferably `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

Keep `/api/v1` in `VITE_API_BASE_URL`. The frontend reads this value at build time through Vite, so production values should be configured in the hosting platform, not hard-coded in source code.

## Demo Deployment

This project is ready for a demo-level split deployment with the frontend on Vercel and the backend on Render. This is not a production hardening guide.

Backend on Render:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Required environment variables:
  - `OPENAI_API_KEY=...`
  - `ALLOWED_ORIGINS=https://<frontend-domain>`
  - `LOG_LEVEL=INFO`
- Optional environment variables:
  - `OPENAI_MODEL=gpt-4o-mini`
  - `OPENAI_BASE_URL=...`
  - `DATABASE_URL=...`

Frontend on Vercel:

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Required environment variables:
  - `VITE_API_BASE_URL=https://<backend-domain>/api/v1`

For local Windows development, keep using the existing PowerShell commands and `start_dev.ps1`. The Render start command is Linux-oriented and should not replace the local development script.
