# AI Content Writer

A full-stack AI Content Writer web app powered by **Qwen2.5-0.5B-Instruct**. Generate blog posts, articles, essays, social media posts, product descriptions, and marketing copy with customizable tone, length, and creativity.

## Tech Stack

- **Backend:** Python, FastAPI, Transformers, PyTorch
- **Frontend:** React, Vite, Tailwind CSS
- **Model:** Qwen/Qwen2.5-0.5B-Instruct
- **Deployment:** Render

## Prerequisites

- Python 3.11+
- Node.js 18+
- Git

## Local Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`. The model will download on first startup.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env   # Update VITE_API_URL to point to your backend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Deployment

### Render Backend (Web Service)

1. Push your repo to GitHub.
2. On Render, create a new **Web Service** from your repo.
3. Set the following:
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:** Add `PYTHONUNBUFFERED=1`
4. Render will auto-deploy on push.

### Render Frontend (Static Site)

1. On Render, create a new **Static Site** from your repo.
2. Set the following:
   - **Build Command:** `cd frontend && npm install && npm run build`
   - **Publish Directory:** `frontend/dist`
   - **Environment Variables:** Add `VITE_API_URL=https://your-backend-url.onrender.com`
3. Render will auto-deploy on push.

### One-Click Deploy with render.yaml

Push the repo to GitHub and use the `render.yaml` file to deploy both services at once.

## Project Structure

```
/backend   -> FastAPI app, requirements.txt, Dockerfile
/frontend  -> React app (Vite), package.json, .env.example
render.yaml  -> Infrastructure as Code for Render
README.md  -> Setup + deployment instructions
```

## API Endpoints

- `GET /health` — Check server status
- `POST /generate` — Generate content
  ```json
  {
    "topic": "machine learning",
    "content_type": "blog post",
    "tone": "Informative",
    "length": "Medium",
    "temperature": 0.7
  }
  ```
  Returns `{ "content": "..." }`.

## CI/CD (GitHub Actions)

Two workflows live in `.github/workflows/`:

| Workflow | File | Trigger |
|---|---|---|
| CI — lint & test | `ci.yml` | Every push and pull request |
| CD — deploy | `cd.yml` | Push to `main` only |

### CI workflow
- **Backend**: installs dependencies, runs `ruff` for linting, then `pytest` (20 tests, torch/transformers fully mocked — no model download needed).
- **Frontend**: runs `npm ci` then `npm run build` to catch build-time errors.

### CD workflow
The CD job calls Render [deploy hooks](https://render.com/docs/deploy-hooks) to trigger a redeploy whenever you push to `main`.

**Setup** — add two repository secrets in GitHub (Settings → Secrets and variables → Actions):

| Secret name | Where to get it |
|---|---|
| `RENDER_BACKEND_DEPLOY_HOOK` | Render dashboard → backend service → Settings → Deploy Hooks |
| `RENDER_FRONTEND_DEPLOY_HOOK` | Render dashboard → frontend static site → Settings → Deploy Hooks |

Once the secrets are set, every push to `main` will automatically redeploy both services.

## Notes

- The 0.5B model is CPU-friendly and can run on Render's free/starter instances.
- For faster generation, a GPU instance is recommended.
- Model downloads may take a few minutes on first startup.
