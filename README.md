# ✍️ AI Content Writer

A single-page AI Content Writer powered by **Qwen2.5-0.5B-Instruct**, built with **Streamlit**, and deployed on **Streamlit Community Cloud** (free).

## Tech Stack

| Layer | Tech |
|---|---|
| UI + Logic | Python, Streamlit |
| AI Model | Qwen/Qwen2.5-0.5B-Instruct |
| Libraries | Transformers, PyTorch, Accelerate |
| Hosting | Streamlit Community Cloud |

## Features

- 6 content types — Blog Post, Article, Essay, Social Media Post, Product Description, Marketing Copy
- 6 tones — Professional, Friendly, Informative, Persuasive, Creative, Casual
- 3 lengths — Short, Medium, Long
- Temperature slider for creativity control
- Download generated content as `.txt`
- Responsive two-column layout

## Local Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/ai-content-writer.git
cd ai-content-writer

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Opens at `http://localhost:8501`. Model downloads on first run (~1 GB).

## Deploy on Streamlit Community Cloud (Free)

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Fill in:

| Field | Value |
|---|---|
| **Repository** | `your-username/ai-content-writer` |
| **Branch** | `main` |
| **Main file path** | `app.py` |

4. Click **Deploy** — done! 🎉

> First deploy takes ~5 min (model download). After that it's fast.

## Project Structure

```
app.py              → Streamlit app (UI + model)
requirements.txt    → Python dependencies
.github/workflows/  → CI/CD (lint on push, auto-deploy on main)
backend/            → Old FastAPI backend (not used)
frontend/           → Old React frontend (not used)
```

## CI/CD

| Workflow | Trigger | Action |
|---|---|---|
| `ci.yml` | Every push / PR | Lint `app.py` with Ruff |
| `cd.yml` | Push to `main` | Streamlit Cloud auto-redeploys |

Streamlit Cloud watches your `main` branch — every push auto-redeploys. No secrets or webhooks needed.
