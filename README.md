# Language Learning Assistant

本项目是一个本地可运行的 AI 翻译助手，当前阶段聚焦在基础翻译主流程：

- Backend: FastAPI
- Frontend: React + Vite
- LLM: OpenAI Chat Completions API

第一阶段不包含数据库、登录、历史记录、收藏、调用次数统计或 prompt 管理后台。

## Project Structure

```text
backend/
  app/
    core/          # settings and logger
    prompts/       # prompt txt files, used as translation styles
    routes/        # FastAPI routes
    schemas/       # request and response models
    services/      # LLM service
    utils/         # prompt manager
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
  "target_lang": "English"
}
```

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
